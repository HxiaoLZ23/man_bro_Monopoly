#!/usr/bin/env python3
"""
大富翁联机游戏服务器启动器
"""
import asyncio
import signal
import sys
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.network.server.game_server import GameServer

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('game_server.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


class ServerLauncher:
    """服务器启动器"""
    
    def __init__(self):
        self.server = None
        self.shutdown_event = asyncio.Event()
    
    async def start_server(self, host: str = "localhost", port: int = 8765):
        """启动服务器"""
        try:
            logger.info("🚀 正在启动大富翁联机游戏服务器...")
            
            # 创建服务器实例
            self.server = GameServer(host, port)
            
            # 设置信号处理
            self._setup_signal_handlers()
            
            # 启动服务器
            server_task = asyncio.create_task(self.server.start())
            shutdown_task = asyncio.create_task(self.shutdown_event.wait())
            
            # 等待服务器启动或关闭信号
            done, pending = await asyncio.wait(
                [server_task, shutdown_task],
                return_when=asyncio.FIRST_COMPLETED
            )
            
            # 取消未完成的任务
            for task in pending:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            
            # 检查是否有异常
            for task in done:
                if task.exception():
                    raise task.exception()
        
        except KeyboardInterrupt:
            logger.info("⌨️ 收到键盘中断信号")
        except Exception as e:
            logger.error(f"❌ 服务器启动失败: {e}")
            raise
        finally:
            await self._shutdown()
    
    def _setup_signal_handlers(self):
        """设置信号处理器"""
        def signal_handler(signum, frame):
            logger.info(f"📡 收到信号 {signum}，准备关闭服务器...")
            asyncio.create_task(self._trigger_shutdown())
        
        # 注册信号处理器
        if sys.platform != "win32":
            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)
    
    async def _trigger_shutdown(self):
        """触发关闭"""
        self.shutdown_event.set()
    
    async def _shutdown(self):
        """关闭服务器"""
        if self.server:
            logger.info("🛑 正在关闭服务器...")
            await self.server.stop()
            logger.info("✅ 服务器已关闭")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="大富翁联机游戏服务器")
    parser.add_argument("--host", default="localhost", help="服务器主机地址")
    parser.add_argument("--port", type=int, default=8765, help="服务器端口")
    parser.add_argument("--debug", action="store_true", help="启用调试模式")
    
    args = parser.parse_args()
    
    # 设置日志级别
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("🐛 调试模式已启用")
    
    # 显示启动信息
    print("=" * 60)
    print("🎮 大富翁联机游戏服务器")
    print("=" * 60)
    print(f"📍 服务器地址: {args.host}:{args.port}")
    print(f"🔧 调试模式: {'开启' if args.debug else '关闭'}")
    print("=" * 60)
    print("💡 使用 Ctrl+C 停止服务器")
    print("=" * 60)
    
    # 启动服务器
    launcher = ServerLauncher()
    
    try:
        asyncio.run(launcher.start_server(args.host, args.port))
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.error(f"❌ 服务器运行出错: {e}")
        sys.exit(1)
    
    print("\n👋 再见！")


if __name__ == "__main__":
    main() 