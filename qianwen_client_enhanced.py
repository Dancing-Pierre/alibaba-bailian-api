#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
千问大模型API工具类 - 增强版

新增特性：
- 自定义配置系统
- 自定义记忆存储接口
- 日志记录功能
- 更灵活的配置选项

基础特性：
- 链式调用支持
- MongoDB上下文记忆缓存
- 用户记忆隔离
- 多模态输入（文本、图像、视频、文档）
- 流式输出
- 联网搜索
- 参数自由控制
- 简单易用的API设计

作者: AI Assistant
创建时间: 2025-01-25
"""

import os
import base64
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, AsyncGenerator, Callable
from pathlib import Path
import asyncio
from dataclasses import dataclass, field
from contextlib import asynccontextmanager

# 导入配置系统
from config import (
    QianwenConfig, APIConfig, ModelConfig, MemoryConfig, LogConfig,
    MemoryStorage, LogStorage, MongoMemoryStorage, MongoLogStorage
)

# 第三方库
try:
    from openai import OpenAI, AsyncOpenAI
except ImportError:
    raise ImportError("请安装openai库: pip install openai")

try:
    import pymongo
    from motor.motor_asyncio import AsyncIOMotorClient
except ImportError:
    print("警告: 未安装MongoDB库，记忆功能将不可用")
    pymongo = None
    AsyncIOMotorClient = None

try:
    from loguru import logger
except ImportError:
    import logging as logger

try:
    from PIL import Image
except ImportError:
    Image = None

try:
    import orjson
except ImportError:
    import json as orjson

try:
    from cachetools import TTLCache
except ImportError:
    TTLCache = None

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


# ============= 异常定义 =============

class QianwenAPIError(Exception):
    """千问API异常"""
    def __init__(self, message: str, error_code: str = None):
        super().__init__(message)
        self.error_code = error_code
        self.message = message


# ============= 数据类定义 =============

@dataclass
class ChatMessage:
    """聊天消息数据类"""
    role: str
    content: Union[str, List[Dict[str, Any]]]
    timestamp: datetime = field(default_factory=datetime.now)
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


# ============= 存储工厂 =============

class StorageFactory:
    """存储工厂类"""
    
    @staticmethod
    def create_memory_storage(config: MemoryConfig) -> Optional[MemoryStorage]:
        """创建记忆存储实例"""
        if not config.enabled:
            return None
        
        if config.custom_storage:
            return config.custom_storage
        
        if config.storage_type == "mongodb":
            return MongoMemoryStorage(config)
        elif config.storage_type == "redis":
            # 这里可以实现Redis存储
            raise NotImplementedError("Redis存储尚未实现，请使用自定义存储")
        elif config.storage_type == "file":
            # 这里可以实现文件存储
            raise NotImplementedError("文件存储尚未实现，请使用自定义存储")
        else:
            raise ValueError(f"不支持的存储类型: {config.storage_type}")
    
    @staticmethod
    def create_log_storage(config: LogConfig) -> Optional[LogStorage]:
        """创建日志存储实例"""
        if not config.enabled:
            return None
        
        if config.custom_storage:
            return config.custom_storage
        
        if config.storage_type == "mongodb":
            return MongoLogStorage(config)
        elif config.storage_type == "file":
            # 这里可以实现文件日志存储
            raise NotImplementedError("文件日志存储尚未实现，请使用自定义存储")
        else:
            raise ValueError(f"不支持的日志存储类型: {config.storage_type}")


# ============= 记忆管理器 =============

class MemoryManager:
    """记忆管理器 - 使用可配置的存储后端"""
    
    def __init__(self, config: MemoryConfig):
        self.config = config
        self.storage = StorageFactory.create_memory_storage(config)
        self._local_cache = None
        
        # 本地缓存
        if TTLCache and config.enabled:
            self._local_cache = TTLCache(
                maxsize=getattr(config, 'local_cache_size', 1000),
                ttl=3600  # 1小时本地缓存
            )
    
    async def initialize(self):
        """初始化记忆管理器"""
        if self.storage:
            return await self.storage.initialize()
        return True
    
    async def save_message(self, message: ChatMessage):
        """保存消息到记忆"""
        if not self.storage:
            return
        
        try:
            # 保存到存储
            await self.storage.save_message(
                user_id=message.user_id,
                session_id=message.session_id,
                role=message.role,
                content=message.content if isinstance(message.content, str) else json.dumps(message.content),
                metadata=message.metadata
            )
            
            # 更新本地缓存
            if self._local_cache:
                cache_key = f"{message.user_id}:{message.session_id}"
                if cache_key in self._local_cache:
                    self._local_cache[cache_key].append(message)
                
        except Exception as e:
            print(f"保存消息到记忆失败: {e}")
    
    async def get_history(self, user_id: str, session_id: str, limit: int = None) -> List[ChatMessage]:
        """获取历史记录"""
        if not self.storage:
            return []
        
        try:
            # 检查本地缓存
            cache_key = f"{user_id}:{session_id}"
            if self._local_cache and cache_key in self._local_cache:
                cached_messages = self._local_cache[cache_key]
                if limit:
                    return cached_messages[-limit:]
                return cached_messages
            
            # 从存储获取
            messages_data = await self.storage.get_history(user_id, session_id, limit)
            
            messages = []
            for msg_data in messages_data:
                content = msg_data['content']
                try:
                    # 尝试解析JSON内容
                    content = json.loads(content)
                except (json.JSONDecodeError, TypeError):
                    # 如果不是JSON，保持原样
                    pass
                
                message = ChatMessage(
                    role=msg_data['role'],
                    content=content,
                    timestamp=msg_data.get('timestamp', datetime.now()),
                    user_id=user_id,
                    session_id=session_id,
                    metadata=msg_data.get('metadata', {})
                )
                messages.append(message)
            
            # 更新本地缓存
            if self._local_cache:
                self._local_cache[cache_key] = messages
            
            return messages
            
        except Exception as e:
            print(f"获取历史记录失败: {e}")
            return []
    
    async def clear_history(self, user_id: str, session_id: str):
        """清除历史记录"""
        if not self.storage:
            return
        
        try:
            await self.storage.clear_history(user_id, session_id)
            
            # 清除本地缓存
            if self._local_cache:
                cache_key = f"{user_id}:{session_id}"
                if cache_key in self._local_cache:
                    del self._local_cache[cache_key]
                    
        except Exception as e:
            print(f"清除历史记录失败: {e}")
    
    async def close(self):
        """关闭记忆管理器"""
        if self.storage:
            await self.storage.close()


# ============= 日志管理器 =============

class LogManager:
    """日志管理器 - 使用可配置的存储后端"""
    
    def __init__(self, config: LogConfig):
        self.config = config
        self.storage = StorageFactory.create_log_storage(config)
    
    async def initialize(self):
        """初始化日志管理器"""
        if self.storage:
            return await self.storage.initialize()
        return True
    
    async def log_request(self, user_id: str, session_id: str, request_data: Dict[str, Any], request_id: str = None) -> str:
        """记录请求日志"""
        if not self.storage:
            return request_id or str(uuid.uuid4())
        
        request_id = request_id or str(uuid.uuid4())
        
        try:
            log_data = {
                "request_id": request_id,
                "model": request_data.get("model"),
                "messages": request_data.get("messages"),
                "temperature": request_data.get("temperature"),
                "max_tokens": request_data.get("max_tokens"),
                "stream": request_data.get("stream", False)
            }
            
            await self.storage.log_request(user_id, session_id, log_data)
            
        except Exception as e:
            print(f"记录请求日志失败: {e}")
        
        return request_id
    
    async def log_response(self, user_id: str, session_id: str, response_data: Dict[str, Any], request_id: str = None):
        """记录响应日志"""
        if not self.storage:
            return
        
        try:
            log_data = {
                "choices": response_data.get("choices"),
                "usage": response_data.get("usage"),
                "model": response_data.get("model"),
                "created": response_data.get("created")
            }
            
            await self.storage.log_response(user_id, session_id, log_data, request_id)
            
        except Exception as e:
            print(f"记录响应日志失败: {e}")
    
    async def log_error(self, user_id: str, session_id: str, error_data: Dict[str, Any]):
        """记录错误日志"""
        if not self.storage:
            return
        
        try:
            await self.storage.log_error(user_id, session_id, error_data)
            
        except Exception as e:
            print(f"记录错误日志失败: {e}")
    
    async def get_logs(self, user_id: str = None, session_id: str = None, start_time: datetime = None, end_time: datetime = None, limit: int = 100) -> List[Dict[str, Any]]:
        """获取日志记录"""
        if not self.storage:
            return []
        
        try:
            return await self.storage.get_logs(user_id, session_id, start_time, end_time, limit)
        except Exception as e:
            print(f"获取日志记录失败: {e}")
            return []
    
    async def close(self):
        """关闭日志管理器"""
        if self.storage:
            await self.storage.close()


# ============= 对话会话类 =============

class QianwenChat:
    """千问对话会话类 - 支持链式调用"""
    
    def __init__(self, client: 'QianwenClient', user_id: str = None, session_id: str = None):
        self.client = client
        self._user_id = user_id or "default_user"
        self._session_id = session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 链式调用参数
        self._model = client.config.model.default_model
        self._temperature = client.config.model.default_temperature
        self._max_tokens = client.config.model.default_max_tokens
        self._system_message = client.config.model.default_system_message
        self._search_enabled = False
        self._memory_enabled = client.config.memory.enabled
    
    # ============= 链式调用方法 =============
    
    def model(self, model_name: str) -> 'QianwenChat':
        """设置模型"""
        self._model = model_name
        return self
    
    def temperature(self, temp: float) -> 'QianwenChat':
        """设置温度参数"""
        self._temperature = max(0.0, min(1.0, temp))
        return self
    
    def max_tokens(self, tokens: int) -> 'QianwenChat':
        """设置最大输出长度"""
        self._max_tokens = max(1, tokens)
        return self
    
    def system(self, message: str) -> 'QianwenChat':
        """设置系统提示"""
        self._system_message = message
        return self
    
    def search(self, enabled: bool = True) -> 'QianwenChat':
        """启用/禁用搜索"""
        self._search_enabled = enabled
        return self
    
    def memory(self, enabled: bool = True) -> 'QianwenChat':
        """启用/禁用记忆功能"""
        self._memory_enabled = enabled
        return self
    
    def user(self, user_id: str) -> 'QianwenChat':
        """设置用户ID"""
        self._user_id = user_id
        return self
    
    def session(self, session_id: str) -> 'QianwenChat':
        """设置会话ID"""
        self._session_id = session_id
        return self
    
    # ============= 对话方法 =============
    
    async def ask(self, message: str, **kwargs) -> Dict[str, Any]:
        """发送消息并获取回复"""
        try:
            # 构建消息列表
            messages = await self._build_messages(message)
            
            # 构建请求参数
            request_params = {
                "model": self._model,
                "messages": messages,
                "temperature": self._temperature,
                "max_tokens": self._max_tokens,
                **kwargs
            }
            
            # 添加搜索工具
            if self._search_enabled:
                request_params["tools"] = [{
                    "type": "web_search",
                    "web_search": {"enable": True}
                }]
            
            # 记录请求日志
            request_id = None
            if self.client.log_manager:
                request_id = await self.client.log_manager.log_request(
                    self._user_id, self._session_id, request_params
                )
            
            # 发送请求
            response = await self.client.async_client.chat.completions.create(**request_params)
            response_dict = response.model_dump()
            
            # 记录响应日志
            if self.client.log_manager:
                await self.client.log_manager.log_response(
                    self._user_id, self._session_id, response_dict, request_id
                )
            
            # 保存对话到记忆
            if self._memory_enabled and self.client.memory_manager:
                # 保存用户消息
                user_message = ChatMessage(
                    role="user",
                    content=message,
                    user_id=self._user_id,
                    session_id=self._session_id
                )
                await self.client.memory_manager.save_message(user_message)
                
                # 保存助手回复
                if response_dict.get('choices'):
                    assistant_content = response_dict['choices'][0]['message']['content']
                    assistant_message = ChatMessage(
                        role="assistant",
                        content=assistant_content,
                        user_id=self._user_id,
                        session_id=self._session_id
                    )
                    await self.client.memory_manager.save_message(assistant_message)
            
            return response_dict
            
        except Exception as e:
            # 记录错误日志
            if self.client.log_manager:
                await self.client.log_manager.log_error(
                    self._user_id, self._session_id, {
                        "error_type": type(e).__name__,
                        "error_message": str(e),
                        "request_params": locals().get('request_params', {})
                    }
                )
            raise QianwenAPIError(f"API调用失败: {e}")
    
    async def stream(self, message: str, **kwargs) -> AsyncGenerator[Any, None]:
        """流式对话"""
        try:
            # 构建消息列表
            messages = await self._build_messages(message)
            
            # 构建请求参数
            request_params = {
                "model": self._model,
                "messages": messages,
                "temperature": self._temperature,
                "max_tokens": self._max_tokens,
                "stream": True,
                **kwargs
            }
            
            # 添加搜索工具
            if self._search_enabled:
                request_params["tools"] = [{
                    "type": "web_search",
                    "web_search": {"enable": True}
                }]
            
            # 记录请求日志
            request_id = None
            if self.client.log_manager:
                request_id = await self.client.log_manager.log_request(
                    self._user_id, self._session_id, request_params
                )
            
            # 流式响应
            full_content = ""
            
            try:
                # 尝试使用stream_options参数
                request_params["stream_options"] = {"include_usage": True}
                stream = await self.client.async_client.chat.completions.create(**request_params)
            except TypeError:
                # 如果不支持stream_options，则移除该参数
                request_params.pop("stream_options", None)
                stream = await self.client.async_client.chat.completions.create(**request_params)
            
            async for chunk in stream:
                yield chunk
                
                # 收集完整内容用于记忆保存
                if chunk.choices and chunk.choices[0].delta.content:
                    full_content += chunk.choices[0].delta.content
            
            # 保存对话到记忆
            if self._memory_enabled and self.client.memory_manager and full_content:
                # 保存用户消息
                user_message = ChatMessage(
                    role="user",
                    content=message,
                    user_id=self._user_id,
                    session_id=self._session_id
                )
                await self.client.memory_manager.save_message(user_message)
                
                # 保存助手回复
                assistant_message = ChatMessage(
                    role="assistant",
                    content=full_content,
                    user_id=self._user_id,
                    session_id=self._session_id
                )
                await self.client.memory_manager.save_message(assistant_message)
            
            # 记录响应日志
            if self.client.log_manager:
                await self.client.log_manager.log_response(
                    self._user_id, self._session_id, 
                    {"content": full_content, "stream": True}, 
                    request_id
                )
            
        except Exception as e:
            # 记录错误日志
            if self.client.log_manager:
                await self.client.log_manager.log_error(
                    self._user_id, self._session_id, {
                        "error_type": type(e).__name__,
                        "error_message": str(e),
                        "request_params": locals().get('request_params', {})
                    }
                )
            raise QianwenAPIError(f"流式API调用失败: {e}")
    
    async def image(self, message: str, image_path: str, **kwargs) -> Dict[str, Any]:
        """图像理解"""
        if not os.path.exists(image_path):
            raise QianwenAPIError(f"图片文件不存在: {image_path}")
        
        # 编码图片
        image_base64 = self.client._encode_image(image_path)
        
        # 构建多模态消息
        multimodal_message = [
            {"type": "text", "text": message},
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{image_base64}"
                }
            }
        ]
        
        return await self._multimodal_request(multimodal_message, **kwargs)
    
    async def video(self, message: str, video_frames: List[str], **kwargs) -> Dict[str, Any]:
        """视频理解"""
        # 构建多模态消息
        multimodal_message = [{"type": "text", "text": message}]
        
        for frame_path in video_frames:
            if not os.path.exists(frame_path):
                raise QianwenAPIError(f"视频帧文件不存在: {frame_path}")
            
            frame_base64 = self.client._encode_image(frame_path)
            multimodal_message.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{frame_base64}"
                }
            })
        
        return await self._multimodal_request(multimodal_message, **kwargs)
    
    async def document(self, message: str, document_path: str, **kwargs) -> Dict[str, Any]:
        """文档理解"""
        if not os.path.exists(document_path):
            raise QianwenAPIError(f"文档文件不存在: {document_path}")
        
        # 读取文档内容（这里简化处理，实际可能需要更复杂的文档解析）
        try:
            with open(document_path, 'r', encoding='utf-8') as f:
                doc_content = f.read()
        except UnicodeDecodeError:
            # 如果是二进制文档，可能需要特殊处理
            raise QianwenAPIError(f"无法读取文档内容: {document_path}")
        
        # 构建包含文档内容的消息
        full_message = f"{message}\n\n文档内容：\n{doc_content}"
        
        return await self.ask(full_message, **kwargs)
    
    async def _multimodal_request(self, content: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        """多模态请求的通用方法"""
        try:
            # 获取历史记录
            messages = []
            if self._memory_enabled and self.client.memory_manager:
                history = await self.client.memory_manager.get_history(
                    self._user_id, self._session_id, 
                    limit=self.client.config.memory.max_history_length
                )
                
                for msg in history:
                    messages.append({
                        "role": msg.role,
                        "content": msg.content
                    })
            
            # 添加系统消息
            if self._system_message:
                messages.insert(0, {
                    "role": "system",
                    "content": self._system_message
                })
            
            # 添加当前多模态消息
            messages.append({
                "role": "user",
                "content": content
            })
            
            # 构建请求参数
            request_params = {
                "model": self._model,
                "messages": messages,
                "temperature": self._temperature,
                "max_tokens": self._max_tokens,
                **kwargs
            }
            
            # 记录请求日志
            request_id = None
            if self.client.log_manager:
                request_id = await self.client.log_manager.log_request(
                    self._user_id, self._session_id, request_params
                )
            
            # 发送请求
            response = await self.client.async_client.chat.completions.create(**request_params)
            response_dict = response.model_dump()
            
            # 记录响应日志
            if self.client.log_manager:
                await self.client.log_manager.log_response(
                    self._user_id, self._session_id, response_dict, request_id
                )
            
            # 保存对话到记忆
            if self._memory_enabled and self.client.memory_manager:
                # 保存用户消息
                user_message = ChatMessage(
                    role="user",
                    content=content,
                    user_id=self._user_id,
                    session_id=self._session_id
                )
                await self.client.memory_manager.save_message(user_message)
                
                # 保存助手回复
                if response_dict.get('choices'):
                    assistant_content = response_dict['choices'][0]['message']['content']
                    assistant_message = ChatMessage(
                        role="assistant",
                        content=assistant_content,
                        user_id=self._user_id,
                        session_id=self._session_id
                    )
                    await self.client.memory_manager.save_message(assistant_message)
            
            return response_dict
            
        except Exception as e:
            # 记录错误日志
            if self.client.log_manager:
                await self.client.log_manager.log_error(
                    self._user_id, self._session_id, {
                        "error_type": type(e).__name__,
                        "error_message": str(e),
                        "request_params": locals().get('request_params', {})
                    }
                )
            raise QianwenAPIError(f"多模态API调用失败: {e}")
    
    async def _build_messages(self, message: str) -> List[Dict[str, Any]]:
        """构建消息列表"""
        messages = []
        
        # 添加系统消息
        if self._system_message:
            messages.append({
                "role": "system",
                "content": self._system_message
            })
        
        # 获取历史记录
        if self._memory_enabled and self.client.memory_manager:
            history = await self.client.memory_manager.get_history(
                self._user_id, self._session_id, 
                limit=self.client.config.memory.max_history_length
            )
            
            for msg in history:
                messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
        
        # 添加当前消息
        messages.append({
            "role": "user",
            "content": message
        })
        
        return messages
    
    # ============= 记忆管理方法 =============
    
    async def clear_memory(self):
        """清除当前会话的记忆"""
        if self.client.memory_manager:
            await self.client.memory_manager.clear_history(self._user_id, self._session_id)
    
    async def get_history(self, limit: int = None) -> List[ChatMessage]:
        """获取历史记录"""
        if self.client.memory_manager:
            return await self.client.memory_manager.get_history(self._user_id, self._session_id, limit)
        return []


# ============= 主客户端类 =============

class QianwenClient:
    """千问客户端 - 增强版"""
    
    def __init__(self, config: Union[QianwenConfig, Dict[str, Any], str] = None, **kwargs):
        # 处理配置
        if config is None:
            self.config = QianwenConfig.from_env()
        elif isinstance(config, str):
            self.config = QianwenConfig.from_file(config)
        elif isinstance(config, dict):
            self.config = QianwenConfig.from_dict(config)
        elif isinstance(config, QianwenConfig):
            self.config = config
        else:
            raise ValueError("配置参数类型错误")
        
        # 应用kwargs覆盖配置
        if 'api_key' in kwargs:
            self.config.api.api_key = kwargs['api_key']
        if 'base_url' in kwargs:
            self.config.api.base_url = kwargs['base_url']
        
        # 检查API密钥
        if not self.config.api.api_key:
            raise QianwenAPIError("未设置API密钥，请设置QIANWEN_API_KEY环境变量或在配置中指定")
        
        # 初始化OpenAI客户端
        self.async_client = AsyncOpenAI(
            api_key=self.config.api.api_key,
            base_url=self.config.api.base_url,
            timeout=self.config.api.timeout
        )
        
        # 初始化管理器
        self.memory_manager = None
        self.log_manager = None
    
    async def initialize(self):
        """初始化客户端"""
        # 初始化记忆管理器
        if self.config.memory.enabled:
            self.memory_manager = MemoryManager(self.config.memory)
            await self.memory_manager.initialize()
        
        # 初始化日志管理器
        if self.config.log.enabled:
            self.log_manager = LogManager(self.config.log)
            await self.log_manager.initialize()
    
    def chat(self, user_id: str = None, session_id: str = None) -> QianwenChat:
        """创建对话会话"""
        return QianwenChat(self, user_id, session_id)
    
    def _encode_image(self, image_path: str) -> str:
        """编码图片为base64"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def get_models(self) -> Dict[str, Any]:
        """获取可用模型列表"""
        return {
            "available_models": self.config.model.available_models,
            "default_model": self.config.model.default_model,
            "text_models": ["qwen-plus", "qwen-max"],
            "vision_models": ["qwen-vl-plus", "qwen-vl-max"]
        }
    
    async def get_logs(self, user_id: str = None, session_id: str = None, start_time: datetime = None, end_time: datetime = None, limit: int = 100) -> List[Dict[str, Any]]:
        """获取日志记录"""
        if self.log_manager:
            return await self.log_manager.get_logs(user_id, session_id, start_time, end_time, limit)
        return []
    
    async def close(self):
        """关闭客户端"""
        if self.memory_manager:
            await self.memory_manager.close()
        if self.log_manager:
            await self.log_manager.close()
        await self.async_client.close()
    
    async def __aenter__(self):
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


# ============= 便捷函数 =============

def create_client(config: Union[QianwenConfig, Dict[str, Any], str] = None, **kwargs) -> QianwenClient:
    """创建千问客户端"""
    return QianwenClient(config, **kwargs)


def create_async_client(config: Union[QianwenConfig, Dict[str, Any], str] = None, **kwargs) -> QianwenClient:
    """创建异步千问客户端"""
    return QianwenClient(config, **kwargs)


# ============= 测试代码 =============

if __name__ == "__main__":
    import asyncio
    
    async def test():
        # 测试基础功能
        client = create_async_client()
        await client.initialize()
        
        chat = client.chat(user_id="test_user", session_id="test_session")
        response = await chat.ask("你好！")
        print(response['choices'][0]['message']['content'])
        
        await client.close()
    
    asyncio.run(test())