#!/usr/bin/env python3
"""
检查房间服务器状态
"""
import socket
import sys

def check_server(host="localhost", port=8766):
    """检查服务器是否在运行"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception as e:
        print(f"检查服务器时出错: {e}")
        return False

def main():
    """主函数"""
    print("🔍 检查房间服务器状态...")
    
    if check_server():
        print("✅ 房间服务器正在运行 (localhost:8766)")
    else:
        print("❌ 房间服务器未运行")
        print("💡 请运行: python room_server.py")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 