#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
千问大模型工具类 - 配置示例

本文件展示了如何使用自定义配置、自定义记忆存储和日志存储

作者: AI Assistant
创建时间: 2025-01-25
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# 导入配置系统
from config import (
    QianwenConfig, APIConfig, ModelConfig, MemoryConfig, LogConfig,
    MemoryStorage, LogStorage
)
from qianwen_client_enhanced import QianwenClient


# ============= 自定义记忆存储示例 =============

class RedisMemoryStorage(MemoryStorage):
    """Redis记忆存储实现示例"""
    
    def __init__(self, config: MemoryConfig):
        self.config = config
        self.redis_client = None
        # 这里应该初始化Redis客户端
        # import redis
        # self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
    
    async def initialize(self) -> bool:
        """初始化存储"""
        print("初始化Redis记忆存储...")
        # 这里应该测试Redis连接
        return True
    
    async def save_message(self, user_id: str, session_id: str, role: str, content: str, metadata: Dict[str, Any] = None):
        """保存消息"""
        key = f"memory:{user_id}:{session_id}"
        message_data = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        # 模拟Redis操作
        print(f"保存消息到Redis: {key} -> {message_data}")
        # self.redis_client.lpush(key, json.dumps(message_data))
        # self.redis_client.expire(key, self.config.ttl_seconds)
    
    async def get_history(self, user_id: str, session_id: str, limit: int = None) -> List[Dict[str, Any]]:
        """获取历史记录"""
        key = f"memory:{user_id}:{session_id}"
        print(f"从Redis获取历史记录: {key}")
        
        # 模拟返回数据
        return [
            {
                "role": "user",
                "content": "你好",
                "timestamp": datetime.now(),
                "metadata": {}
            },
            {
                "role": "assistant",
                "content": "你好！有什么可以帮助你的吗？",
                "timestamp": datetime.now(),
                "metadata": {}
            }
        ]
    
    async def clear_history(self, user_id: str, session_id: str):
        """清除历史记录"""
        key = f"memory:{user_id}:{session_id}"
        print(f"清除Redis历史记录: {key}")
        # self.redis_client.delete(key)
    
    async def close(self):
        """关闭存储"""
        print("关闭Redis记忆存储")
        # if self.redis_client:
        #     self.redis_client.close()


class FileMemoryStorage(MemoryStorage):
    """文件记忆存储实现示例"""
    
    def __init__(self, config: MemoryConfig):
        self.config = config
        self.storage_dir = getattr(config, 'storage_dir', './memory_data')
        import os
        os.makedirs(self.storage_dir, exist_ok=True)
    
    async def initialize(self) -> bool:
        """初始化存储"""
        print(f"初始化文件记忆存储: {self.storage_dir}")
        return True
    
    def _get_file_path(self, user_id: str, session_id: str) -> str:
        """获取文件路径"""
        import os
        return os.path.join(self.storage_dir, f"{user_id}_{session_id}.json")
    
    async def save_message(self, user_id: str, session_id: str, role: str, content: str, metadata: Dict[str, Any] = None):
        """保存消息"""
        file_path = self._get_file_path(user_id, session_id)
        
        # 读取现有数据
        messages = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                messages = json.load(f)
        except FileNotFoundError:
            pass
        
        # 添加新消息
        message_data = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        messages.append(message_data)
        
        # 保存到文件
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)
        
        print(f"保存消息到文件: {file_path}")
    
    async def get_history(self, user_id: str, session_id: str, limit: int = None) -> List[Dict[str, Any]]:
        """获取历史记录"""
        file_path = self._get_file_path(user_id, session_id)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                messages = json.load(f)
            
            # 转换时间戳
            for msg in messages:
                if isinstance(msg.get('timestamp'), str):
                    msg['timestamp'] = datetime.fromisoformat(msg['timestamp'])
            
            if limit:
                messages = messages[-limit:]
            
            print(f"从文件获取历史记录: {file_path}, 共{len(messages)}条")
            return messages
            
        except FileNotFoundError:
            print(f"历史记录文件不存在: {file_path}")
            return []
    
    async def clear_history(self, user_id: str, session_id: str):
        """清除历史记录"""
        file_path = self._get_file_path(user_id, session_id)
        try:
            import os
            os.remove(file_path)
            print(f"清除文件历史记录: {file_path}")
        except FileNotFoundError:
            pass
    
    async def close(self):
        """关闭存储"""
        print("关闭文件记忆存储")


# ============= 自定义日志存储示例 =============

class FileLogStorage(LogStorage):
    """文件日志存储实现示例"""
    
    def __init__(self, config: LogConfig):
        self.config = config
        self.log_dir = getattr(config, 'log_dir', './log_data')
        import os
        os.makedirs(self.log_dir, exist_ok=True)
    
    async def initialize(self) -> bool:
        """初始化存储"""
        print(f"初始化文件日志存储: {self.log_dir}")
        return True
    
    def _get_log_file(self, log_type: str) -> str:
        """获取日志文件路径"""
        import os
        date_str = datetime.now().strftime('%Y%m%d')
        return os.path.join(self.log_dir, f"{log_type}_{date_str}.json")
    
    async def log_request(self, user_id: str, session_id: str, request_data: Dict[str, Any]):
        """记录请求日志"""
        log_file = self._get_log_file('request')
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "session_id": session_id,
            "request_data": request_data
        }
        
        # 追加到文件
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        
        print(f"记录请求日志到文件: {log_file}")
    
    async def log_response(self, user_id: str, session_id: str, response_data: Dict[str, Any], request_id: str = None):
        """记录响应日志"""
        log_file = self._get_log_file('response')
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "session_id": session_id,
            "request_id": request_id,
            "response_data": response_data
        }
        
        # 追加到文件
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        
        print(f"记录响应日志到文件: {log_file}")
    
    async def log_error(self, user_id: str, session_id: str, error_data: Dict[str, Any]):
        """记录错误日志"""
        log_file = self._get_log_file('error')
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "session_id": session_id,
            "error_data": error_data
        }
        
        # 追加到文件
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        
        print(f"记录错误日志到文件: {log_file}")
    
    async def get_logs(self, user_id: str = None, session_id: str = None, start_time: datetime = None, end_time: datetime = None, limit: int = 100) -> List[Dict[str, Any]]:
        """获取日志记录"""
        # 这里简化实现，实际应该解析所有日志文件并过滤
        print(f"获取日志记录: user_id={user_id}, session_id={session_id}, limit={limit}")
        return []
    
    async def close(self):
        """关闭存储"""
        print("关闭文件日志存储")


# ============= 配置示例 =============

def example_basic_config():
    """基础配置示例"""
    config = QianwenConfig(
        api=APIConfig(
            api_key="your-api-key-here",
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        ),
        model=ModelConfig(
            default_model="qwen-plus",
            default_temperature=0.7,
            default_max_tokens=2000
        ),
        memory=MemoryConfig(
            enabled=True,
            storage_type="mongodb",
            max_history_length=20
        ),
        log=LogConfig(
            enabled=True,
            storage_type="mongodb"
        )
    )
    return config


def example_custom_memory_config():
    """自定义记忆存储配置示例"""
    # 创建自定义记忆存储
    memory_config = MemoryConfig(
        enabled=True,
        storage_type="custom",
        max_history_length=50
    )
    
    # 设置自定义存储实现
    memory_config.custom_storage = FileMemoryStorage(memory_config)
    # 或者使用Redis存储
    # memory_config.custom_storage = RedisMemoryStorage(memory_config)
    
    config = QianwenConfig(
        api=APIConfig(
            api_key="your-api-key-here",
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        ),
        model=ModelConfig(
            default_model="qwen-plus"
        ),
        memory=memory_config,
        log=LogConfig(enabled=False)  # 禁用日志
    )
    return config


def example_custom_log_config():
    """自定义日志存储配置示例"""
    # 创建自定义日志存储
    log_config = LogConfig(
        enabled=True,
        storage_type="custom"
    )
    
    # 设置自定义存储实现
    log_config.custom_storage = FileLogStorage(log_config)
    
    config = QianwenConfig(
        api=APIConfig(
            api_key="your-api-key-here",
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        ),
        model=ModelConfig(
            default_model="qwen-plus"
        ),
        memory=MemoryConfig(enabled=False),  # 禁用记忆
        log=log_config
    )
    return config


def example_full_custom_config():
    """完全自定义配置示例"""
    # 自定义记忆存储
    memory_config = MemoryConfig(
        enabled=True,
        storage_type="custom",
        max_history_length=30
    )
    memory_config.custom_storage = FileMemoryStorage(memory_config)
    
    # 自定义日志存储
    log_config = LogConfig(
        enabled=True,
        storage_type="custom"
    )
    log_config.custom_storage = FileLogStorage(log_config)
    
    config = QianwenConfig(
        api=APIConfig(
            api_key="your-api-key-here",
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            timeout=60
        ),
        model=ModelConfig(
            default_model="qwen-plus",
            default_temperature=0.8,
            default_max_tokens=3000,
            default_system_message="你是一个有用的AI助手。"
        ),
        memory=memory_config,
        log=log_config
    )
    return config


def example_dict_config():
    """字典配置示例"""
    config_dict = {
        "api": {
            "api_key": "your-api-key-here",
            "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
            "timeout": 30
        },
        "model": {
            "default_model": "qwen-plus",
            "default_temperature": 0.7,
            "default_max_tokens": 2000
        },
        "memory": {
            "enabled": True,
            "storage_type": "mongodb",
            "max_history_length": 20,
            "mongodb_url": "mongodb://localhost:27017",
            "database_name": "qianwen_memory"
        },
        "log": {
            "enabled": True,
            "storage_type": "mongodb",
            "mongodb_url": "mongodb://localhost:27017",
            "database_name": "qianwen_logs"
        }
    }
    return config_dict


# ============= 使用示例 =============

async def example_basic_usage():
    """基础使用示例"""
    print("=== 基础使用示例 ===")
    
    # 使用基础配置
    config = example_basic_config()
    
    async with QianwenClient(config) as client:
        chat = client.chat(user_id="user1", session_id="session1")
        
        # 基础对话
        response = await chat.ask("你好！")
        print(f"回复: {response['choices'][0]['message']['content']}")
        
        # 链式调用
        response = await chat.temperature(0.9).max_tokens(1000).ask("讲个笑话")
        print(f"笑话: {response['choices'][0]['message']['content']}")


async def example_custom_memory_usage():
    """自定义记忆存储使用示例"""
    print("\n=== 自定义记忆存储使用示例 ===")
    
    # 使用自定义记忆存储配置
    config = example_custom_memory_config()
    
    async with QianwenClient(config) as client:
        chat = client.chat(user_id="user2", session_id="session2")
        
        # 对话1
        await chat.ask("我叫张三")
        print("已告诉AI我的名字")
        
        # 对话2 - 测试记忆功能
        response = await chat.ask("我叫什么名字？")
        print(f"AI回忆: {response['choices'][0]['message']['content']}")
        
        # 查看历史记录
        history = await chat.get_history()
        print(f"历史记录数量: {len(history)}")


async def example_custom_log_usage():
    """自定义日志存储使用示例"""
    print("\n=== 自定义日志存储使用示例 ===")
    
    # 使用自定义日志存储配置
    config = example_custom_log_config()
    
    async with QianwenClient(config) as client:
        chat = client.chat(user_id="user3", session_id="session3")
        
        # 进行一些对话，观察日志记录
        await chat.ask("今天天气怎么样？")
        await chat.ask("推荐一本好书")
        
        # 获取日志记录
        logs = await client.get_logs(user_id="user3", limit=10)
        print(f"日志记录数量: {len(logs)}")


async def example_full_custom_usage():
    """完全自定义配置使用示例"""
    print("\n=== 完全自定义配置使用示例 ===")
    
    # 使用完全自定义配置
    config = example_full_custom_config()
    
    async with QianwenClient(config) as client:
        chat = client.chat(user_id="user4", session_id="session4")
        
        # 测试各种功能
        await chat.system("你是一个专业的编程助手").ask("如何学习Python？")
        await chat.search(True).ask("最新的Python版本是什么？")
        
        print("完全自定义配置测试完成")


async def example_dict_config_usage():
    """字典配置使用示例"""
    print("\n=== 字典配置使用示例 ===")
    
    # 使用字典配置
    config_dict = example_dict_config()
    
    async with QianwenClient(config_dict) as client:
        chat = client.chat(user_id="user5", session_id="session5")
        
        response = await chat.ask("用字典配置创建的客户端工作正常吗？")
        print(f"回复: {response['choices'][0]['message']['content']}")


# ============= 主函数 =============

async def main():
    """主函数 - 运行所有示例"""
    print("千问大模型工具类 - 配置示例")
    print("=" * 50)
    
    try:
        # 注意：这些示例需要有效的API密钥才能运行
        # 请在配置中设置正确的API密钥
        
        # await example_basic_usage()
        # await example_custom_memory_usage()
        # await example_custom_log_usage()
        # await example_full_custom_usage()
        # await example_dict_config_usage()
        
        print("\n所有示例配置已展示完成！")
        print("请根据需要选择合适的配置方式。")
        
    except Exception as e:
        print(f"示例运行出错: {e}")
        print("请检查API密钥配置是否正确")


if __name__ == "__main__":
    # 运行示例
    asyncio.run(main())
    
    # 也可以单独测试某个配置
    print("\n=== 配置对象示例 ===")
    
    # 基础配置
    basic_config = example_basic_config()
    print(f"基础配置: {basic_config}")
    
    # 自定义记忆配置
    custom_memory_config = example_custom_memory_config()
    print(f"自定义记忆配置: {custom_memory_config}")
    
    # 字典配置
    dict_config = example_dict_config()
    print(f"字典配置: {dict_config}")