#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
千问大模型工具类使用示例

本文件展示了千问工具类的各种使用方法，包括：
- 基础对话
- 链式调用
- 流式输出
- 图像理解
- 联网搜索
- 记忆功能
- 用户隔离
- 文档处理
"""

import asyncio
import os
from qianwen_client import create_async_client


async def basic_chat_example():
    """基础对话示例"""
    print("\n=== 基础对话示例 ===")
    
    client = create_async_client()
    await client.initialize()
    
    try:
        # 创建对话
        chat = client.chat(user_id="user123", session_id="session456")
        
        # 发送消息
        response = await chat.ask("你好！请介绍一下你自己。")
        print(f"AI: {response['choices'][0]['message']['content']}")
        
    finally:
        await client.close()


async def chain_call_example():
    """链式调用示例"""
    print("\n=== 链式调用示例 ===")
    
    client = create_async_client()
    await client.initialize()
    
    try:
        # 链式设置参数并发送消息
        response = await client.chat(user_id="user123") \
            .model("qwen-plus") \
            .temperature(0.8) \
            .max_tokens(500) \
            .system("你是一个专业的AI助手，请用简洁的语言回答问题") \
            .ask("请用3句话介绍人工智能的发展历程")
        
        print(f"AI: {response['choices'][0]['message']['content']}")
        
    finally:
        await client.close()


async def stream_chat_example():
    """流式对话示例"""
    print("\n=== 流式对话示例 ===")
    
    client = create_async_client()
    await client.initialize()
    
    try:
        chat = client.chat(user_id="user123")
        
        print("AI: ", end="", flush=True)
        async for chunk in chat.stream("请写一首关于春天的短诗"):
            if chunk.choices and chunk.choices[0].delta.content:
                print(chunk.choices[0].delta.content, end="", flush=True)
        print()  # 换行
        
    finally:
        await client.close()


async def image_understanding_example():
    """图像理解示例"""
    print("\n=== 图像理解示例 ===")
    
    client = create_async_client()
    await client.initialize()
    
    try:
        chat = client.chat(user_id="user123")
        
        # 注意：这里需要替换为实际的图片路径
        image_path = "example_image.jpg"
        
        if os.path.exists(image_path):
            response = await chat.model("qwen-vl-plus").image(
                "请详细描述这张图片的内容", 
                image_path
            )
            print(f"AI: {response['choices'][0]['message']['content']}")
        else:
            print("图片文件不存在，跳过图像理解示例")
        
    finally:
        await client.close()


async def search_example():
    """联网搜索示例"""
    print("\n=== 联网搜索示例 ===")
    
    client = create_async_client()
    await client.initialize()
    
    try:
        chat = client.chat(user_id="user123")
        
        # 启用搜索功能
        response = await chat.search(True).ask("今天北京的天气如何？")
        print(f"AI: {response['choices'][0]['message']['content']}")
        
    finally:
        await client.close()


async def memory_example():
    """记忆功能示例"""
    print("\n=== 记忆功能示例 ===")
    
    client = create_async_client()
    await client.initialize()
    
    try:
        chat = client.chat(user_id="user123", session_id="memory_test")
        
        # 第一轮对话
        print("第一轮对话：")
        response1 = await chat.ask("我的名字是张三，我喜欢编程")
        print(f"AI: {response1['choices'][0]['message']['content']}")
        
        # 第二轮对话（会记住之前的内容）
        print("\n第二轮对话：")
        response2 = await chat.ask("你还记得我的名字和爱好吗？")
        print(f"AI: {response2['choices'][0]['message']['content']}")
        
        # 查看历史记录
        history = await chat.get_history()
        print(f"\n历史记录数量: {len(history)}")
        
        # 清除记忆
        await chat.clear_memory()
        print("已清除记忆")
        
        # 测试记忆清除效果
        print("\n清除记忆后的对话：")
        response3 = await chat.ask("你还记得我的名字吗？")
        print(f"AI: {response3['choices'][0]['message']['content']}")
        
    finally:
        await client.close()


async def user_isolation_example():
    """用户隔离示例"""
    print("\n=== 用户隔离示例 ===")
    
    client = create_async_client()
    await client.initialize()
    
    try:
        # 用户A的对话
        chat_a = client.chat(user_id="user_a", session_id="session_a")
        await chat_a.ask("我喜欢蓝色，我是一名教师")
        
        # 用户B的对话
        chat_b = client.chat(user_id="user_b", session_id="session_b")
        await chat_b.ask("我喜欢红色，我是一名程序员")
        
        # 测试隔离效果
        print("用户A询问自己的信息：")
        result_a = await chat_a.ask("我喜欢什么颜色？我的职业是什么？")
        print(f"用户A: {result_a['choices'][0]['message']['content']}")
        
        print("\n用户B询问自己的信息：")
        result_b = await chat_b.ask("我喜欢什么颜色？我的职业是什么？")
        print(f"用户B: {result_b['choices'][0]['message']['content']}")
        
    finally:
        await client.close()


async def document_example():
    """文档处理示例"""
    print("\n=== 文档处理示例 ===")
    
    client = create_async_client()
    await client.initialize()
    
    try:
        chat = client.chat(user_id="user123")
        
        # 注意：这里需要替换为实际的文档路径
        doc_path = "example_document.pdf"
        
        if os.path.exists(doc_path):
            response = await chat.document(
                "请总结这个文档的主要内容", 
                doc_path
            )
            print(f"AI: {response['choices'][0]['message']['content']}")
        else:
            print("文档文件不存在，跳过文档处理示例")
        
    finally:
        await client.close()


async def comprehensive_example():
    """综合示例：展示多种功能组合使用"""
    print("\n=== 综合示例 ===")
    
    client = create_async_client()
    await client.initialize()
    
    try:
        # 创建一个带记忆的对话会话
        chat = client.chat(user_id="demo_user", session_id="comprehensive_demo")
        
        # 设置系统提示和参数
        chat = chat.model("qwen-plus").temperature(0.7).system(
            "你是一个智能助手，能够记住用户的偏好和历史对话"
        )
        
        # 第一轮：建立用户画像
        print("建立用户画像：")
        response1 = await chat.ask("我是一名Python开发者，对AI技术很感兴趣")
        print(f"AI: {response1['choices'][0]['message']['content']}")
        
        # 第二轮：基于记忆的个性化回答
        print("\n个性化推荐：")
        response2 = await chat.ask("能推荐一些适合我学习的AI框架吗？")
        print(f"AI: {response2['choices'][0]['message']['content']}")
        
        # 第三轮：联网搜索最新信息
        print("\n获取最新信息：")
        response3 = await chat.search(True).ask("最近有什么新的AI技术突破？")
        print(f"AI: {response3['choices'][0]['message']['content']}")
        
    finally:
        await client.close()


async def main():
    """主函数：运行所有示例"""
    print("千问大模型工具类使用示例")
    print("=" * 50)
    
    # 检查API密钥
    if not os.getenv('QIANWEN_API_KEY'):
        print("警告：未设置QIANWEN_API_KEY环境变量")
        print("请在.env文件中设置API密钥")
        return
    
    try:
        # 运行各种示例
        await basic_chat_example()
        await chain_call_example()
        await stream_chat_example()
        await image_understanding_example()
        await search_example()
        await memory_example()
        await user_isolation_example()
        await document_example()
        await comprehensive_example()
        
        print("\n=== 所有示例运行完成 ===")
        
    except Exception as e:
        print(f"运行示例时出错: {e}")
        print("请检查API密钥和网络连接")


if __name__ == "__main__":
    # 运行示例
    asyncio.run(main())