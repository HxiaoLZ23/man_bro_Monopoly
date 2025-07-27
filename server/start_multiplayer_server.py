#!/usr/bin/env python3
"""
多人联机游戏服务器启动脚本
简化版本，用于快速启动和测试
"""

import asyncio
import logging
import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(__file__))

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    from src.network.server.enhanced_game_server import EnhancedGameServer
except ImportError:
    # 如果增强版服务器不可用，使用简单服务器
    try:
        from simple_server import SimpleGameServer as EnhancedGameServer
    except ImportError:
        logger.error("无法导入服务器模块，请检查项目结构")
        sys.exit(1)


async def main():
    """主函数"""
    print("🎮 大富翁多人联机服务器")
    print("=" * 40)
    
    # 解析命令行参数
    import argparse
    parser = argparse.ArgumentParser(description="大富翁多人联机服务器")
    parser.add_argument("--host", default="localhost", help="服务器主机地址 (默认: localhost)")
    parser.add_argument("--port", type=int, default=8765, help="服务器端口 (默认: 8765)")
    parser.add_argument("--max-connections", type=int, default=100, help="最大连接数 (默认: 100)")
    parser.add_argument("--max-rooms", type=int, default=20, help="最大房间数 (默认: 20)")
    parser.add_argument("--debug", action="store_true", help="启用调试模式")
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.info("🐛 调试模式已启用")
    
    # 创建服务器实例
    try:
        server = EnhancedGameServer(args.host, args.port)
        
        # 配置服务器
        if hasattr(server, 'config'):
            server.config["max_connections"] = args.max_connections
            server.config["max_rooms"] = args.max_rooms
        
        print(f"🌐 服务器地址: ws://{args.host}:{args.port}")
        print(f"👥 最大连接数: {args.max_connections}")
        print(f"🏠 最大房间数: {args.max_rooms}")
        print("-" * 40)
        print("按 Ctrl+C 停止服务器")
        print()
        
        # 启动服务器
        await server.start()
        
    except KeyboardInterrupt:
        logger.info("👋 收到停止信号")
    except Exception as e:
        logger.error(f"❌ 服务器错误: {e}")
        sys.exit(1)
    finally:
        if 'server' in locals():
            try:
                await server.stop()
            except:
                pass
        logger.info("✅ 服务器已关闭")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 再见!")
    except Exception as e:
        logger.error(f"启动失败: {e}")
        sys.exit(1) 