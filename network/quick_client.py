# -*- coding: utf-8 -*-
"""
大富翁快速测试客户端
"""

import asyncio
import json

def safe_input(prompt="按 Enter 键继续..."):
    try:
        return input(prompt)
    except:
        print("\n程序退出")
        return ""

async def test_client():
    try:
        import websockets
        print(f"✅ websockets版本: {websockets.__version__}")
    except ImportError:
        print("❌ 缺少websockets模块")
        safe_input()
        return
    
    uri = "ws://localhost:8765"
    print(f"🔗 正在连接到: {uri}")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ 连接成功！")
            
            test_message = {
                "type": "test",
                "message": "你好，服务器！"
            }
            
            await websocket.send(json.dumps(test_message, ensure_ascii=False))
            print("📤 已发送测试消息")
            
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(response)
                print(f"📥 服务器回应: {data}")
            except asyncio.TimeoutError:
                print("⏰ 等待服务器回应超时")
            
            print("🎮 客户端测试完成")
    
    except ConnectionRefusedError:
        print("❌ 连接被拒绝 - 请确保服务器正在运行")
    except Exception as e:
        print(f"❌ 连接错误: {e}")

def main():
    print("=" * 50)
    print("🎮 大富翁快速测试客户端")
    print("=" * 50)
    
    try:
        asyncio.run(test_client())
    except KeyboardInterrupt:
        print("\n⌨️ 用户停止客户端")
    except Exception as e:
        print(f"❌ 运行错误: {e}")
    finally:
        print("\n🔚 客户端已停止")
        safe_input("按 Enter 键关闭...")

if __name__ == "__main__":
    main() 