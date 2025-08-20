# 千问大模型工具类 - 增强版

一个功能强大、高度可配置的千问大模型API工具类，支持自定义配置系统、多种存储后端和完整的日志记录功能。
## 📞 联系方式

如果您发现可以进行更好的拓展或遇到问题，欢迎提交 Issue 或联系我们：

- **作者**: @Lapper
- **📧 邮箱**: shibaizhelianmeng@163.com
- **💬 微信**: EonNetWork
- **📝 博客**: [胖虎爱Java-CSDN博客](https://blog.csdn.net/m0_68711597?spm=1010.2135.3001.5343)

---


## ✨ 特性

### 核心功能
- 🔗 **链式调用**: 支持流畅的链式API调用
- 🧠 **记忆缓存**: 基于MongoDB的上下文记忆系统
- 👥 **用户隔离**: 完善的多用户记忆隔离机制
- 🌊 **流式输出**: 支持实时流式对话
- 🔍 **联网搜索**: 内置联网搜索功能
- 🖼️ **多模态**: 支持图像、视频理解
- 📄 **文档处理**: 支持文档理解和文字提取
- ⚡ **异步支持**: 完整的异步API支持
- 🛡️ **错误处理**: 完善的错误处理机制

### 增强特性
- ⚙️ **自定义配置**: 灵活的配置系统，支持多种配置方式
- 🗄️ **自定义存储**: 可插拔的记忆存储接口，支持MongoDB、Redis、文件等
- 📊 **日志记录**: 完整的请求/响应日志记录系统
- 🔌 **接口扩展**: 易于扩展的存储和日志接口

## 📁 项目文件结构

```
d:\AI2025\AI组件/
├── qianwen_client_enhanced.py    # 🔧 核心工具类 - 千问大模型API封装
├── config.py                     # ⚙️ 配置系统 - 核心配置类和接口定义
├── config_examples.py            # 📋 配置示例 - 自定义存储和配置实现示例
├── examples.py                   # 📚 使用示例 - 完整功能演示代码
├── README.md                     # 📖 项目文档 - 使用指南和API文档
├── requirements.txt              # 📦 依赖管理 - Python包依赖列表
├── .env.example                  # 🔑 环境变量模板 - 配置示例文件
├── .env                          # 🔐 环境变量配置 - 实际配置文件（需自行创建）
└── __pycache__/                  # 🗂️ Python缓存目录 - 编译后的字节码文件
```

### 📄 文件详细说明

#### 🔧 核心功能文件

**`qianwen_client_enhanced.py`** - 主要工具类
- 千问大模型的核心API封装
- 支持基础对话、流式输出、多模态输入
- 集成记忆功能、用户隔离、MongoDB缓存
- 提供联网搜索、文档理解、文字提取等高级功能
- 支持链式调用和异步操作

**调用示例：**
```python
# 基础使用
from qianwen_client_enhanced import QianwenClient
from config import QianwenConfig

async def main():
    config = QianwenConfig.from_env()
    async with QianwenClient(config) as client:
        chat = client.chat(user_id="user123")
        response = await chat.ask("你好！")
        print(response['choices'][0]['message']['content'])

# 链式调用
response = await client.chat(user_id="user123") \
    .model("qwen-plus") \
    .temperature(0.8) \
    .ask("写一首诗")
```

#### ⚙️ 配置系统

**`config.py`** - 核心配置文件
- 定义所有配置类：`APIConfig`、`ModelConfig`、`MemoryConfig`、`LogConfig`
- 实现存储接口：`MemoryStorage`、`LogStorage`
- 提供MongoDB记忆存储和日志存储实现
- 支持环境变量和文件配置加载
- 默认启用MongoDB作为记忆和日志存储

**调用示例：**
```python
from config import QianwenConfig, APIConfig, MemoryConfig

# 使用环境变量配置
config = QianwenConfig.from_env()

# 自定义配置
config = QianwenConfig(
    api=APIConfig(api_key="your_key"),
    memory=MemoryConfig(max_history_length=20)
)

# 从文件加载配置
config = QianwenConfig.from_file("config.json")

# 保存配置到文件
config.save_to_file("my_config.json")
```

**`config_examples.py`** - 配置示例文件
- 提供Redis记忆存储实现示例
- 展示文件存储实现方法
- 包含自定义日志存储示例
- 提供完整的配置使用案例和最佳实践

**调用示例：**
```python
from config_examples import RedisMemoryStorage, FileMemoryStorage
from config import QianwenConfig, MemoryConfig

# 使用Redis作为记忆存储
redis_storage = RedisMemoryStorage(
    host="localhost",
    port=6379,
    db=0
)

config = QianwenConfig(
    memory=MemoryConfig(
        enabled=True,
        custom_storage=redis_storage
    )
)

# 使用文件存储
file_storage = FileMemoryStorage("memory.json")
config = QianwenConfig(
    memory=MemoryConfig(
        enabled=True,
        custom_storage=file_storage
    )
)
```

#### 📚 使用示例和文档

**`examples.py`** - 使用示例集合
- 基础对话和流式输出示例
- 记忆功能和用户隔离演示
- 多模态输入（图像、视频）示例
- 联网搜索和文档处理示例
- 自定义配置和高级功能使用方法
- 完整的错误处理和最佳实践

**调用示例：**
```bash
# 运行所有示例
python examples.py

# 或者在Python中导入使用
python -c "from examples import basic_chat_demo; import asyncio; asyncio.run(basic_chat_demo())"
```

**`README.md`** - 项目文档
- 完整的安装和配置指南
- 详细的功能特性介绍
- 丰富的代码示例和API文档
- 故障排除和常见问题解答
- 自定义接口扩展指南

#### 🔧 环境和依赖

**`requirements.txt`** - 依赖管理
- 千问SDK：`dashscope>=1.14.1`
- MongoDB驱动：`pymongo>=4.6.0`
- 异步HTTP客户端：`aiohttp>=3.9.1`
- 其他必需的Python包和版本要求

**使用方法：**
```bash
# 安装所有依赖
pip install -r requirements.txt

# 或使用虚拟环境（推荐）
python -m venv venv
venv\Scripts\activate  # Windows
# 或
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

**`.env.example`** - 环境变量模板
```env
# API配置
QIANWEN_API_KEY=your_api_key_here
QIANWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1

# MongoDB配置
MONGO_URI=mongodb://localhost:27017
MONGO_DATABASE=qianwen_memory
MONGO_LOG_DATABASE=qianwen_logs

# 功能开关
QIANWEN_MEMORY_ENABLED=true
QIANWEN_LOG_ENABLED=true
```

**使用方法：**
```bash
# 复制模板文件
cp .env.example .env

# 编辑配置文件
notepad .env  # Windows
# 或
vim .env     # Linux/Mac

# 设置必要的环境变量
set DASHSCOPE_API_KEY=your_api_key_here  # Windows
# 或
export DASHSCOPE_API_KEY=your_api_key_here  # Linux/Mac
```

**`.env`** - 实际环境变量配置
- 复制`.env.example`并修改为实际配置
- 包含真实的API密钥和数据库连接信息
- 此文件不会被版本控制系统跟踪

#### 🗂️ 缓存文件

**`__pycache__/`** - Python缓存目录
- 存放编译后的Python字节码文件（`.pyc`）
- 提高模块加载速度，可安全删除
- 包含项目中所有Python模块的缓存版本

## 🚀 快速开始

### 1. 克隆项目
```bash
git clone <repository-url>
cd AI组件
```

### 2. 安装依赖
```bash
# 创建虚拟环境（推荐）
python -m venv venv
venv\Scripts\activate  # Windows
# 或 source venv/bin/activate  # Linux/Mac

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置环境
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑.env文件，设置API密钥
# DASHSCOPE_API_KEY=your_api_key_here
```

### 4. 运行示例
```bash
# 运行所有功能示例
python examples.py

# 或者运行单个示例
python -c "from examples import basic_chat_demo; import asyncio; asyncio.run(basic_chat_demo())"
```

### 5. 在代码中使用
```python
from qianwen_client_enhanced import QianwenClient
from config import QianwenConfig
import asyncio

async def main():
    # 使用默认配置（从环境变量加载）
    config = QianwenConfig.from_env()
    
    async with QianwenClient(config) as client:
        # 创建聊天会话（自动启用记忆功能）
        chat = client.chat(user_id="user123")
        
        # 发送消息
        response = await chat.ask("你好，请介绍一下你自己")
        print(response['choices'][0]['message']['content'])
        
        # 继续对话（会记住上下文）
        response = await chat.ask("你刚才说了什么？")
        print(response['choices'][0]['message']['content'])

if __name__ == "__main__":
    asyncio.run(main())
```

## 📦 详细安装指南

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置API密钥

创建`.env`文件并配置千问API密钥：

```env
QIANWEN_API_KEY=your_api_key_here
```

**获取API密钥：**
1. 访问 [阿里云百炼平台](https://bailian.console.aliyun.com/)
2. 注册/登录账号
3. 创建应用并获取API Key

### 3. 安装MongoDB（推荐）

**默认配置使用MongoDB作为记忆和日志存储**，建议安装MongoDB以获得完整功能：

```bash
# Windows (使用Chocolatey)
choco install mongodb

# macOS (使用Homebrew)
brew install mongodb-community

# Ubuntu/Debian
sudo apt-get install mongodb
```

启动MongoDB服务：
```bash
# Windows
net start MongoDB

# macOS/Linux
sudo systemctl start mongod
```

**注意**: 如果不安装MongoDB，工具类会自动降级到文件存储模式。

## 💡 详细使用指南

### 基础对话

```python
import asyncio
from qianwen_client_enhanced import QianwenClient
from config import QianwenConfig

async def main():
    # 使用默认配置创建客户端（默认启用MongoDB记忆和日志）
    config = QianwenConfig()
    client = QianwenClient(config)
    await client.initialize()
    
    # 创建对话
    chat = client.chat(user_id="user123", session_id="session456")
    
    # 发送消息
    response = await chat.ask("你好！")
    print(response['choices'][0]['message']['content'])
    
    # 关闭客户端
    await client.close()

asyncio.run(main())
```

### 自定义配置

```python
from config import QianwenConfig, APIConfig, ModelConfig, MemoryConfig, LogConfig

# 创建自定义配置
config = QianwenConfig(
    api=APIConfig(
        api_key="your_api_key",
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
        connection_string="mongodb://localhost:27017",
        database_name="qianwen_memory"
    ),
    log=LogConfig(
        enabled=True,
        storage_type="mongodb",
        connection_string="mongodb://localhost:27017",
        database_name="qianwen_logs"
    )
)

client = QianwenClient(config)
```

### 自定义记忆存储

```python
from config import MemoryStorage
import json

class FileMemoryStorage(MemoryStorage):
    """文件存储示例"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.data = {}
    
    async def initialize(self) -> bool:
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        except FileNotFoundError:
            self.data = {}
        return True
    
    async def save_message(self, user_id: str, session_id: str, role: str, content: str, metadata: dict = None):
        key = f"{user_id}:{session_id}"
        if key not in self.data:
            self.data[key] = []
        
        self.data[key].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        })
        
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    # ... 其他方法实现

# 使用自定义存储
from config import MemoryConfig

custom_storage = FileMemoryStorage("memory.json")
memory_config = MemoryConfig(
    enabled=True,
    custom_storage=custom_storage
)

config = QianwenConfig(memory=memory_config)
client = QianwenClient(config)
```

### 链式调用

```python
async def chain_demo():
    config = QianwenConfig()
    client = QianwenClient(config)
    await client.initialize()
    
    # 链式设置参数并发送消息
    response = await client.chat(user_id="user123") \
        .model("qwen-plus") \
        .temperature(0.8) \
        .max_tokens(1000) \
        .system("你是一个专业的AI助手") \
        .ask("请介绍一下人工智能")
    
    print(response['choices'][0]['message']['content'])
    await client.close()
```

### 日志记录功能

```python
async def log_demo():
    # 启用日志记录
    config = QianwenConfig(
        log=LogConfig(
            enabled=True,
            storage_type="mongodb"
        )
    )
    
    client = QianwenClient(config)
    await client.initialize()
    
    chat = client.chat(user_id="user123", session_id="session456")
    
    # 发送消息（自动记录日志）
    response = await chat.ask("你好！")
    
    # 查看日志记录
    if client.log_manager:
        logs = await client.log_manager.get_logs(
            user_id="user123",
            session_id="session456",
            limit=10
        )
        print(f"找到 {len(logs)} 条日志记录")
    
    await client.close()
```

### 流式对话

```python
async def stream_demo():
    config = QianwenConfig()
    client = QianwenClient(config)
    await client.initialize()
    
    chat = client.chat(user_id="user123")
    
    print("AI: ", end="", flush=True)
    async for chunk in chat.stream("请写一首关于春天的诗"):
        if chunk.choices and chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="", flush=True)
    print()
    
    await client.close()
```

### 图像理解

```python
async def image_demo():
    client = create_async_client()
    await client.initialize()
    
    chat = client.chat(user_id="user123")
    
    # 分析图像
    response = await chat.model("qwen-vl-plus").image(
        "请描述这张图片的内容", 
        "path/to/your/image.jpg"
    )
    
    print(response['choices'][0]['message']['content'])
    await client.close()
```

### 联网搜索

```python
async def search_demo():
    client = create_async_client()
    await client.initialize()
    
    chat = client.chat(user_id="user123")
    
    # 启用搜索功能
    response = await chat.search(True).ask("今天的天气如何？")
    
    print(response['choices'][0]['message']['content'])
    await client.close()
```

### 记忆功能

千问工具类支持上下文记忆功能，可以在对话中保持上下文连续性。**默认最多保存10条历史记录**，防止记忆数据无限增长：

```python
async def memory_demo():
    client = create_async_client()
    await client.initialize()
    
    chat = client.chat(user_id="user123", session_id="session456")
    
    # 第一轮对话
    await chat.ask("我的名字是张三")
    
    # 第二轮对话（会记住之前的内容）
    response = await chat.ask("你还记得我的名字吗？")
    print(response['choices'][0]['message']['content'])
    
    # 查看历史记录
    history = await chat.get_history()
    print(f"历史记录数量: {len(history)}")
    
    # 清除记忆
    await chat.clear_memory()
    
    await client.close()
```

**记忆限制说明：**
- 默认最多保存10条历史记录（用户消息+助手回复各算1条）
- 当超过限制时，会自动删除最旧的记录
- 可通过MemoryConfig的max_history_length参数调整限制

### 用户隔离

```python
async def user_isolation_demo():
    client = create_async_client()
    await client.initialize()
    
    # 用户A的对话
    chat_a = client.chat(user_id="user_a", session_id="session_a")
    await chat_a.ask("我喜欢蓝色")
    
    # 用户B的对话
    chat_b = client.chat(user_id="user_b", session_id="session_b")
    await chat_b.ask("我喜欢红色")
    
    # 测试隔离效果
    result_a = await chat_a.ask("我喜欢什么颜色？")
    result_b = await chat_b.ask("我喜欢什么颜色？")
    
    print(f"用户A: {result_a['choices'][0]['message']['content']}")
    print(f"用户B: {result_b['choices'][0]['message']['content']}")
    
    await client.close()
```

### 文档处理

```python
async def document_demo():
    client = create_async_client()
    await client.initialize()
    
    chat = client.chat(user_id="user123")
    
    # 分析文档
    response = await chat.document(
        "请总结这个文档的主要内容", 
        "path/to/your/document.pdf"
    )
    
    print(response['choices'][0]['message']['content'])
    await client.close()
```

## 📚 API 参考

### 创建客户端

```python
from qianwen_client_enhanced import QianwenClient
from config import QianwenConfig, APIConfig

# 使用默认配置
config = QianwenConfig()
client = QianwenClient(config)

# 使用自定义API密钥
config = QianwenConfig(
    api=APIConfig(api_key="your_api_key")
)
client = QianwenClient(config)

# 完全自定义配置
config = QianwenConfig(
    api=APIConfig(
        api_key="your_api_key",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        timeout=60
    ),
    model=ModelConfig(
        default_model="qwen-plus",
        default_temperature=0.7
    ),
    memory=MemoryConfig(
        enabled=True,
        storage_type="mongodb"
    ),
    log=LogConfig(
        enabled=True,
        storage_type="mongodb"
    )
)
client = QianwenClient(config)
```

### 对话方法

#### 链式配置方法
- `model(model_name: str)`: 设置模型（如 "qwen-plus", "qwen-max", "qwen-vl-plus"）
- `temperature(temp: float)`: 设置温度参数 (0.0-1.0)
- `max_tokens(tokens: int)`: 设置最大输出长度
- `system(message: str)`: 设置系统提示
- `search(enabled: bool)`: 启用/禁用联网搜索
- `memory(enabled: bool)`: 启用/禁用记忆功能
- `user(user_id: str)`: 设置用户ID
- `session(session_id: str)`: 设置会话ID

#### 对话方法
- `ask(message: str)`: 发送文本消息
- `stream(message: str)`: 流式对话
- `image(message: str, image_path: str)`: 图像理解
- `video(message: str, video_frames: List[str])`: 视频理解
- `document(message: str, doc_path: str)`: 文档理解

#### 记忆方法
- `get_history(limit: int = None)`: 获取历史记录
- `clear_memory()`: 清除当前会话记忆

## 🔧 配置说明

### 配置类说明

#### APIConfig - API配置
```python
api_config = APIConfig(
    api_key="your_api_key",           # API密钥
    base_url="https://...",           # API基础URL
    timeout=60,                       # 请求超时时间
    max_retries=3,                    # 最大重试次数
    proxies=None                      # 代理设置
)
```

#### ModelConfig - 模型配置
```python
model_config = ModelConfig(
    default_model="qwen-plus",        # 默认模型
    default_temperature=0.7,          # 默认温度
    default_max_tokens=2000,          # 默认最大token数
    default_system_message="你是AI助手" # 默认系统消息
)
```

#### MemoryConfig - 记忆配置
```python
memory_config = MemoryConfig(
    enabled=True,                     # 是否启用记忆
    storage_type="mongodb",           # 存储类型
    connection_string="mongodb://...", # 连接字符串
    database_name="qianwen_memory",   # 数据库名
    collection_name="messages",       # 集合名
    max_history_length=10,            # 最大历史记录数量
    custom_storage=None               # 自定义存储实现
)
```

#### LogConfig - 日志配置
```python
log_config = LogConfig(
    enabled=True,                     # 是否启用日志
    storage_type="mongodb",           # 存储类型
    connection_string="mongodb://...", # 连接字符串
    database_name="qianwen_logs",     # 数据库名
    collection_name="api_logs",       # 集合名
    custom_storage=None               # 自定义日志存储实现
)
```

### 环境变量

```env
# 必需配置
QIANWEN_API_KEY=your_api_key_here

# 可选配置
QIANWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
MONGO_URI=mongodb://localhost:27017
MONGO_DATABASE=qianwen_memory
MONGO_LOG_DATABASE=qianwen_logs
```

### 支持的模型

- `qwen-plus`: 通用对话模型
- `qwen-max`: 高级对话模型
- `qwen-vl-plus`: 视觉理解模型
- `qwen-vl-max`: 高级视觉理解模型

## 🔍 故障排除

### 常见问题

**Q: API密钥错误**
```
A: 请确保QIANWEN_API_KEY环境变量设置正确
```

**Q: MongoDB连接失败**
```
A: 请确保MongoDB服务正在运行，或禁用记忆功能
```

**Q: 图像处理失败**
```
A: 请确保使用支持视觉的模型（如qwen-vl-plus）
```

## 🔌 自定义接口

### 自定义记忆存储接口

```python
from config import MemoryStorage
from typing import List, Dict, Any, Optional
from datetime import datetime

class CustomMemoryStorage(MemoryStorage):
    """自定义记忆存储实现"""
    
    async def initialize(self) -> bool:
        """初始化存储"""
        # 实现初始化逻辑
        return True
    
    async def save_message(self, user_id: str, session_id: str, role: str, content: str, metadata: dict = None):
        """保存消息"""
        # 实现消息保存逻辑
        pass
    
    async def get_history(self, user_id: str, session_id: str, limit: int = None) -> List[Dict[str, Any]]:
        """获取历史记录"""
        # 实现历史记录获取逻辑
        return []
    
    async def clear_history(self, user_id: str, session_id: str):
        """清除历史记录"""
        # 实现历史记录清除逻辑
        pass
    
    async def close(self):
        """关闭存储连接"""
        # 实现连接关闭逻辑
        pass
```

### 自定义日志存储接口

```python
from config import LogStorage

class CustomLogStorage(LogStorage):
    """自定义日志存储实现"""
    
    async def initialize(self) -> bool:
        """初始化日志存储"""
        return True
    
    async def log_request(self, user_id: str, session_id: str, request_data: Dict[str, Any]):
        """记录请求日志"""
        pass
    
    async def log_response(self, user_id: str, session_id: str, response_data: Dict[str, Any], request_id: str = None):
        """记录响应日志"""
        pass
    
    async def log_error(self, user_id: str, session_id: str, error_data: Dict[str, Any]):
        """记录错误日志"""
        pass
    
    async def get_logs(self, user_id: str = None, session_id: str = None, start_time: datetime = None, end_time: datetime = None, limit: int = 100) -> List[Dict[str, Any]]:
        """获取日志记录"""
        return []
    
    async def close(self):
        """关闭日志存储连接"""
        pass
```

## 📝 更新日志

### v3.0.0 (2025-01-25) - 增强版
- ⚙️ 自定义配置系统
- 🗄️ 可插拔存储接口
- 📊 完整日志记录功能
- 🔌 易于扩展的接口设计

### v2.0.0 (2025-01-25)
- ✨ 支持链式调用
- 🧠 MongoDB记忆缓存
- 👥 用户隔离功能
- 🖼️ 多模态支持
- 🔍 联网搜索
- 📄 文档处理

## ⚠️ 注意事项

1. **API密钥安全**: 请妥善保管您的千问API密钥，不要将其提交到版本控制系统
2. **MongoDB连接**: 确保MongoDB服务正在运行，否则会降级到文件存储
3. **记忆限制**: 默认最多保存10条历史记录，可通过配置调整
4. **异步操作**: 所有API调用都是异步的，请使用`await`关键字
5. **错误处理**: 建议在生产环境中添加适当的错误处理和重试机制

## 📝 总结

这个千问工具类项目提供了完整的千问大模型集成解决方案，具有以下特点：

- **🎯 功能完整**: 支持基础对话、多模态输入、联网搜索、文档处理等全部功能
- **💾 智能存储**: 默认使用MongoDB进行记忆和日志存储，支持用户隔离
- **🔧 灵活配置**: 支持环境变量、文件配置和自定义存储接口
- **⚡ 高性能**: 异步操作和链式调用，支持流式输出
- **📚 易于使用**: 详细的文档和示例，快速上手

无论是简单的聊天机器人还是复杂的AI应用，这个工具类都能满足您的需求。开始使用吧！

## 📄 许可证

MIT License