#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试创建房间功能
"""

import asyncio
import sys
import os

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

async def test_create_room():
    """测试创建房间功能"""
    print("🎮 测试创建房间功能...")
    
    try:
        from src.network.client.network_client import NetworkClient
        
        # 创建网络客户端
        client = NetworkClient("localhost", 8765)
        
        print("📡 连接到服务器...")
        success = await client.start_client("测试玩家")
        
        if not success:
            print("❌ 连接服务器失败")
            return False
        
        print("✅ 连接成功")
        print(f"🆔 客户端ID: {client.client_id}")
        print(f"👤 玩家名称: {client.player_name}")
        print(f"🌐 连接状态: {client.is_connected()}")
        
        # 等待一下确保连接稳定
        await asyncio.sleep(1)
        
        print("🏠 创建房间...")
        create_success = await client.create_room("测试房间", 4, None)
        
        if create_success:
            print("✅ 创建房间请求发送成功")
        else:
            print("❌ 创建房间请求发送失败")
        
        # 等待响应
        await asyncio.sleep(2)
        
        # 停止客户端
        await client.stop_client()
        print("🔚 测试完成")
        
        return create_success
        
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("🎮 大富翁创建房间功能测试")
    print("=" * 50)
    
    print("\n📋 测试前准备:")
    print("1. 确保服务器正在运行 (python room_server.py)")
    print("2. 确保端口8765可用")
    
    input("\n按 Enter 键开始测试...")
    
    try:
        result = asyncio.run(test_create_room())
        if result:
            print("\n✅ 测试成功!")
        else:
            print("\n❌ 测试失败!")
    except KeyboardInterrupt:
        print("\n⌨️ 用户取消测试")
    except Exception as e:
        print(f"\n❌ 测试错误: {e}")
    
    input("\n按 Enter 键退出...")

if __name__ == "__main__":
    main() 