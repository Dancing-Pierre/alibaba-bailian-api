#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
千问大模型工具类配置系统

提供灵活的配置选项，支持：
- 自定义记忆存储
- 自定义日志记录
- 灵活的参数配置
"""

import os
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime
import json


# ============= 抽象接口定义 =============

class MemoryStorage(ABC):
    """记忆存储抽象接口"""
    
    @abstractmethod
    async def save_message(self, user_id: str, session_id: str, role: str, content: str, metadata: Dict[str, Any] = None) -> bool:
        """保存消息到存储"""
        pass
    
    @abstractmethod
    async def get_history(self, user_id: str, session_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """获取历史记录"""
        pass
    
    @abstractmethod
    async def clear_history(self, user_id: str, session_id: str) -> bool:
        """清除历史记录"""
        pass
    
    @abstractmethod
    async def initialize(self) -> bool:
        """初始化存储"""
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """关闭存储连接"""
        pass


class LogStorage(ABC):
    """日志存储抽象接口"""
    
    @abstractmethod
    async def log_request(self, user_id: str, session_id: str, request_data: Dict[str, Any]) -> bool:
        """记录请求日志"""
        pass
    
    @abstractmethod
    async def log_response(self, user_id: str, session_id: str, response_data: Dict[str, Any], request_id: str = None) -> bool:
        """记录响应日志"""
        pass
    
    @abstractmethod
    async def log_error(self, user_id: str, session_id: str, error_data: Dict[str, Any]) -> bool:
        """记录错误日志"""
        pass
    
    @abstractmethod
    async def get_logs(self, user_id: str = None, session_id: str = None, start_time: datetime = None, end_time: datetime = None, limit: int = 100) -> List[Dict[str, Any]]:
        """获取日志记录"""
        pass
    
    @abstractmethod
    async def initialize(self) -> bool:
        """初始化日志存储"""
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """关闭日志存储连接"""
        pass


# ============= 配置数据类 =============

@dataclass
class APIConfig:
    """API配置"""
    api_key: str = None
    base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    timeout: int = 60
    max_retries: int = 3
    retry_delay: float = 1.0


@dataclass
class ModelConfig:
    """模型配置"""
    default_model: str = "qwen-plus"
    default_temperature: float = 0.7
    default_max_tokens: int = 2000
    default_system_message: str = None
    available_models: List[str] = field(default_factory=lambda: [
        "qwen-plus", "qwen-max", "qwen-vl-plus", "qwen-vl-max"
    ])


@dataclass
class MemoryConfig:
    """记忆配置"""
    enabled: bool = True
    storage_type: str = "mongodb"  # mongodb, redis, file, custom
    max_history_length: int = 10
    ttl_hours: int = 24 * 7  # 7天
    # MongoDB配置
    mongo_uri: str = "mongodb://localhost:27017"
    mongo_database: str = "qianwen_memory"
    mongo_collection: str = "conversations"
    # Redis配置
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str = None
    # 文件存储配置
    file_storage_path: str = "./memory_data"
    # 自定义存储实例
    custom_storage: MemoryStorage = None


@dataclass
class LogConfig:
    """日志配置"""
    enabled: bool = True
    storage_type: str = "mongodb"  # mongodb, file, custom
    log_level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR
    log_requests: bool = True
    log_responses: bool = True
    log_errors: bool = True
    # MongoDB配置
    mongo_uri: str = "mongodb://localhost:27017"
    mongo_database: str = "qianwen_logs"
    mongo_collection: str = "api_logs"
    # 文件存储配置
    file_storage_path: str = "./logs"
    file_rotation: str = "daily"  # daily, weekly, monthly
    max_file_size: str = "100MB"
    # 自定义存储实例
    custom_storage: LogStorage = None


@dataclass
class QianwenConfig:
    """千问工具类主配置"""
    api: APIConfig = field(default_factory=APIConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    memory: MemoryConfig = field(default_factory=MemoryConfig)
    log: LogConfig = field(default_factory=LogConfig)
    
    @classmethod
    def from_env(cls) -> 'QianwenConfig':
        """从环境变量创建配置"""
        config = cls()
        
        # API配置
        config.api.api_key = os.getenv('QIANWEN_API_KEY') or os.getenv('DASHSCOPE_API_KEY')
        config.api.base_url = os.getenv('QIANWEN_BASE_URL', config.api.base_url)
        config.api.timeout = int(os.getenv('QIANWEN_TIMEOUT', config.api.timeout))
        
        # 模型配置
        config.model.default_model = os.getenv('QIANWEN_DEFAULT_MODEL', config.model.default_model)
        config.model.default_temperature = float(os.getenv('QIANWEN_DEFAULT_TEMPERATURE', config.model.default_temperature))
        config.model.default_max_tokens = int(os.getenv('QIANWEN_DEFAULT_MAX_TOKENS', config.model.default_max_tokens))
        config.model.default_system_message = os.getenv('QIANWEN_DEFAULT_SYSTEM_MESSAGE')
        
        # 记忆配置
        config.memory.enabled = os.getenv('QIANWEN_MEMORY_ENABLED', 'true').lower() == 'true'
        config.memory.storage_type = os.getenv('QIANWEN_MEMORY_STORAGE', config.memory.storage_type)
        config.memory.mongo_uri = os.getenv('MONGO_URI', config.memory.mongo_uri)
        config.memory.mongo_database = os.getenv('MONGO_DATABASE', config.memory.mongo_database)
        config.memory.max_history_length = int(os.getenv('QIANWEN_MAX_HISTORY', config.memory.max_history_length))
        
        # 日志配置
        config.log.enabled = os.getenv('QIANWEN_LOG_ENABLED', 'true').lower() == 'true'
        config.log.storage_type = os.getenv('QIANWEN_LOG_STORAGE', config.log.storage_type)
        config.log.log_level = os.getenv('QIANWEN_LOG_LEVEL', config.log.log_level)
        config.log.mongo_uri = os.getenv('LOG_MONGO_URI', config.log.mongo_uri)
        config.log.mongo_database = os.getenv('LOG_MONGO_DATABASE', config.log.mongo_database)
        
        return config
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'QianwenConfig':
        """从字典创建配置"""
        config = cls()
        
        if 'api' in config_dict:
            api_config = config_dict['api']
            config.api = APIConfig(**api_config)
        
        if 'model' in config_dict:
            model_config = config_dict['model']
            config.model = ModelConfig(**model_config)
        
        if 'memory' in config_dict:
            memory_config = config_dict['memory']
            config.memory = MemoryConfig(**memory_config)
        
        if 'log' in config_dict:
            log_config = config_dict['log']
            config.log = LogConfig(**log_config)
        
        return config
    
    @classmethod
    def from_file(cls, config_file: str) -> 'QianwenConfig':
        """从配置文件创建配置"""
        with open(config_file, 'r', encoding='utf-8') as f:
            if config_file.endswith('.json'):
                config_dict = json.load(f)
            else:
                # 支持其他格式，如YAML
                raise ValueError(f"不支持的配置文件格式: {config_file}")
        
        return cls.from_dict(config_dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'api': {
                'api_key': self.api.api_key,
                'base_url': self.api.base_url,
                'timeout': self.api.timeout,
                'max_retries': self.api.max_retries,
                'retry_delay': self.api.retry_delay
            },
            'model': {
                'default_model': self.model.default_model,
                'default_temperature': self.model.default_temperature,
                'default_max_tokens': self.model.default_max_tokens,
                'default_system_message': self.model.default_system_message,
                'available_models': self.model.available_models
            },
            'memory': {
                'enabled': self.memory.enabled,
                'storage_type': self.memory.storage_type,
                'max_history_length': self.memory.max_history_length,
                'ttl_hours': self.memory.ttl_hours,
                'mongo_uri': self.memory.mongo_uri,
                'mongo_database': self.memory.mongo_database,
                'mongo_collection': self.memory.mongo_collection,
                'redis_host': self.memory.redis_host,
                'redis_port': self.memory.redis_port,
                'redis_db': self.memory.redis_db,
                'file_storage_path': self.memory.file_storage_path
            },
            'log': {
                'enabled': self.log.enabled,
                'storage_type': self.log.storage_type,
                'log_level': self.log.log_level,
                'log_requests': self.log.log_requests,
                'log_responses': self.log.log_responses,
                'log_errors': self.log.log_errors,
                'mongo_uri': self.log.mongo_uri,
                'mongo_database': self.log.mongo_database,
                'mongo_collection': self.log.mongo_collection,
                'file_storage_path': self.log.file_storage_path,
                'file_rotation': self.log.file_rotation,
                'max_file_size': self.log.max_file_size
            }
        }
    
    def save_to_file(self, config_file: str) -> None:
        """保存配置到文件"""
        config_dict = self.to_dict()
        
        with open(config_file, 'w', encoding='utf-8') as f:
            if config_file.endswith('.json'):
                json.dump(config_dict, f, indent=2, ensure_ascii=False)
            else:
                raise ValueError(f"不支持的配置文件格式: {config_file}")


# ============= 默认实现 =============

class MongoMemoryStorage(MemoryStorage):
    """MongoDB记忆存储实现"""
    
    def __init__(self, config: MemoryConfig):
        self.config = config
        self._client = None
        self._collection = None
    
    async def initialize(self) -> bool:
        """初始化MongoDB连接"""
        try:
            from motor.motor_asyncio import AsyncIOMotorClient
            self._client = AsyncIOMotorClient(self.config.mongo_uri)
            db = self._client[self.config.mongo_database]
            self._collection = db[self.config.mongo_collection]
            
            # 创建索引
            await self._collection.create_index([("user_id", 1), ("session_id", 1), ("timestamp", -1)])
            
            # 设置TTL索引
            if self.config.ttl_hours > 0:
                await self._collection.create_index(
                    "timestamp", 
                    expireAfterSeconds=self.config.ttl_hours * 3600
                )
            
            return True
        except Exception as e:
            print(f"MongoDB记忆存储初始化失败: {e}")
            return False
    
    async def save_message(self, user_id: str, session_id: str, role: str, content: str, metadata: Dict[str, Any] = None) -> bool:
        """保存消息"""
        if self._collection is None:
            return False
        
        try:
            document = {
                "user_id": user_id,
                "session_id": session_id,
                "role": role,
                "content": content,
                "metadata": metadata or {},
                "timestamp": datetime.utcnow()
            }
            
            await self._collection.insert_one(document)
            return True
        except Exception as e:
            print(f"保存消息失败: {e}")
            return False
    
    async def get_history(self, user_id: str, session_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """获取历史记录"""
        if self._collection is None:
            return []
        
        try:
            query = {"user_id": user_id, "session_id": session_id}
            cursor = self._collection.find(query).sort("timestamp", 1)
            
            if limit:
                cursor = cursor.limit(limit)
            elif self.config.max_history_length > 0:
                cursor = cursor.limit(self.config.max_history_length)
            
            messages = []
            async for doc in cursor:
                messages.append({
                    "role": doc["role"],
                    "content": doc["content"],
                    "metadata": doc.get("metadata", {}),
                    "timestamp": doc["timestamp"]
                })
            
            return messages
        except Exception as e:
            print(f"获取历史记录失败: {e}")
            return []
    
    async def clear_history(self, user_id: str, session_id: str) -> bool:
        """清除历史记录"""
        if self._collection is None:
            return False
        
        try:
            query = {"user_id": user_id, "session_id": session_id}
            await self._collection.delete_many(query)
            return True
        except Exception as e:
            print(f"清除历史记录失败: {e}")
            return False
    
    async def close(self) -> None:
        """关闭连接"""
        if self._client:
            self._client.close()


class MongoLogStorage(LogStorage):
    """MongoDB日志存储实现"""
    
    def __init__(self, config: LogConfig):
        self.config = config
        self._client = None
        self._collection = None
    
    async def initialize(self) -> bool:
        """初始化MongoDB连接"""
        try:
            from motor.motor_asyncio import AsyncIOMotorClient
            self._client = AsyncIOMotorClient(self.config.mongo_uri)
            db = self._client[self.config.mongo_database]
            self._collection = db[self.config.mongo_collection]
            
            # 创建索引
            await self._collection.create_index([("user_id", 1), ("timestamp", -1)])
            await self._collection.create_index([("session_id", 1), ("timestamp", -1)])
            await self._collection.create_index("log_type")
            
            return True
        except Exception as e:
            print(f"MongoDB日志存储初始化失败: {e}")
            return False
    
    async def log_request(self, user_id: str, session_id: str, request_data: Dict[str, Any]) -> bool:
        """记录请求日志"""
        if not self.config.log_requests or self._collection is None:
            return False
        
        try:
            document = {
                "user_id": user_id,
                "session_id": session_id,
                "log_type": "request",
                "data": request_data,
                "timestamp": datetime.utcnow()
            }
            
            await self._collection.insert_one(document)
            return True
        except Exception as e:
            print(f"记录请求日志失败: {e}")
            return False
    
    async def log_response(self, user_id: str, session_id: str, response_data: Dict[str, Any], request_id: str = None) -> bool:
        """记录响应日志"""
        if not self.config.log_responses or self._collection is None:
            return False
        
        try:
            document = {
                "user_id": user_id,
                "session_id": session_id,
                "log_type": "response",
                "data": response_data,
                "request_id": request_id,
                "timestamp": datetime.utcnow()
            }
            
            await self._collection.insert_one(document)
            return True
        except Exception as e:
            print(f"记录响应日志失败: {e}")
            return False
    
    async def log_error(self, user_id: str, session_id: str, error_data: Dict[str, Any]) -> bool:
        """记录错误日志"""
        if not self.config.log_errors or self._collection is None:
            return False
        
        try:
            document = {
                "user_id": user_id,
                "session_id": session_id,
                "log_type": "error",
                "data": error_data,
                "timestamp": datetime.utcnow()
            }
            
            await self._collection.insert_one(document)
            return True
        except Exception as e:
            print(f"记录错误日志失败: {e}")
            return False
    
    async def get_logs(self, user_id: str = None, session_id: str = None, start_time: datetime = None, end_time: datetime = None, limit: int = 100) -> List[Dict[str, Any]]:
        """获取日志记录"""
        if self._collection is None:
            return []
        
        try:
            query = {}
            if user_id:
                query["user_id"] = user_id
            if session_id:
                query["session_id"] = session_id
            if start_time or end_time:
                time_query = {}
                if start_time:
                    time_query["$gte"] = start_time
                if end_time:
                    time_query["$lte"] = end_time
                query["timestamp"] = time_query
            
            cursor = self._collection.find(query).sort("timestamp", -1).limit(limit)
            
            logs = []
            async for doc in cursor:
                logs.append({
                    "user_id": doc["user_id"],
                    "session_id": doc["session_id"],
                    "log_type": doc["log_type"],
                    "data": doc["data"],
                    "timestamp": doc["timestamp"],
                    "request_id": doc.get("request_id")
                })
            
            return logs
        except Exception as e:
            print(f"获取日志记录失败: {e}")
            return []
    
    async def close(self) -> None:
        """关闭连接"""
        if self._client:
            self._client.close()