#!/usr/bin/env python3
"""
大富翁联机游戏客户端测试工具
"""
import asyncio
import json
import websockets
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.network.protocol import NetworkProtocol, MessageType, NetworkMessage


class TestClient:
    """测试客户端"""
    
    def __init__(self, server_url: str = "ws://localhost:8765"):
        self.server_url = server_url
        self.websocket = None
        self.client_id = None
        self.room_id = None
        self.player_name = None
        self.running = False
    
    async def connect(self):
        """连接到服务器"""
        try:
            print(f"🔗 正在连接到服务器: {self.server_url}")
            self.websocket = await websockets.connect(self.server_url)
            self.running = True
            
            # 启动消息接收循环
            receive_task = asyncio.create_task(self._receive_messages())
            
            print("✅ 连接成功！")
            print("💡 输入命令 (help 查看帮助):")
            
            # 启动用户输入循环
            input_task = asyncio.create_task(self._input_loop())
            
            # 等待任一任务完成
            done, pending = await asyncio.wait(
                [receive_task, input_task],
                return_when=asyncio.FIRST_COMPLETED
            )
            
            # 取消未完成的任务
            for task in pending:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        except Exception as e:
            print(f"❌ 连接失败: {e}")
        finally:
            await self.disconnect()
    
    async def disconnect(self):
        """断开连接"""
        self.running = False
        if self.websocket:
            await self.websocket.close()
            print("👋 已断开连接")
    
    async def _receive_messages(self):
        """接收消息循环"""
        try:
            async for raw_message in self.websocket:
                try:
                    message = NetworkMessage.from_json(raw_message)
                    await self._handle_message(message)
                except json.JSONDecodeError:
                    print("⚠️ 收到无效的JSON消息")
                except Exception as e:
                    print(f"⚠️ 处理消息时出错: {e}")
        except websockets.exceptions.ConnectionClosed:
            print("🔌 服务器连接已关闭")
            self.running = False
        except Exception as e:
            print(f"❌ 接收消息时出错: {e}")
            self.running = False
    
    async def _handle_message(self, message: NetworkMessage):
        """处理收到的消息"""
        msg_type = message.message_type
        data = message.data
        
        if msg_type == MessageType.SUCCESS.value:
            print(f"✅ {data.get('message', '操作成功')}")
            
            # 提取客户端ID
            if 'client_id' in data:
                self.client_id = data['client_id']
                print(f"🆔 客户端ID: {self.client_id}")
            
            # 提取房间信息
            if 'room_id' in data:
                self.room_id = data['room_id']
                print(f"🏠 房间ID: {self.room_id}")
        
        elif msg_type == MessageType.ERROR.value:
            print(f"❌ 错误: {data.get('message', '未知错误')}")
        
        elif msg_type == MessageType.HEARTBEAT.value:
            # 心跳消息，静默处理
            pass
        
        elif msg_type == MessageType.ROOM_LIST.value:
            rooms = data.get('rooms', [])
            print(f"\n📋 房间列表 ({len(rooms)} 个房间):")
            if not rooms:
                print("  暂无房间")
            else:
                for room in rooms:
                    status = "游戏中" if room.get('is_game_running') else "等待中"
                    players = f"{room.get('player_count', 0)}/{room.get('max_players', 0)}"
                    print(f"  🏠 {room['room_name']} (ID: {room['room_id']}) - {players} 玩家 - {status}")
        
        elif msg_type == MessageType.PLAYER_STATE_UPDATE.value:
            players = data.get('players', [])
            print(f"\n👥 玩家列表更新 ({len(players)} 名玩家):")
            for player in players:
                status = "💰" if not player.get('is_bankrupt') else "💸"
                print(f"  {status} {player['name']} - 位置: {player['position']} - 金钱: ${player['money']}")
        
        elif msg_type == MessageType.CHAT_MESSAGE.value:
            sender = data.get('sender_name', '未知')
            content = data.get('content', '')
            msg_type_str = data.get('message_type', 'public')
            
            if msg_type_str == 'system':
                print(f"📢 系统: {content}")
            elif msg_type_str == 'game':
                print(f"🎮 游戏: {content}")
            else:
                print(f"💬 {sender}: {content}")
        
        elif msg_type == MessageType.GAME_START.value:
            print("🎮 游戏开始！")
            game_config = data.get('game_config', {})
            print(f"⚙️ 游戏配置: 最多 {game_config.get('max_players', 0)} 名玩家")
        
        elif msg_type == MessageType.GAME_END.value:
            reason = data.get('reason', '游戏结束')
            rankings = data.get('rankings', [])
            print(f"🏁 {reason}")
            
            if rankings:
                print("🏆 最终排名:")
                for rank in rankings:
                    medal = "🥇" if rank['rank'] == 1 else "🥈" if rank['rank'] == 2 else "🥉" if rank['rank'] == 3 else "  "
                    print(f"  {medal} {rank['rank']}. {rank['name']} - 总资产: ${rank['total_assets']}")
        
        else:
            print(f"📨 收到消息: {msg_type}")
            if data:
                print(f"   数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
    
    async def _input_loop(self):
        """用户输入循环"""
        while self.running:
            try:
                # 使用异步输入
                command = await asyncio.get_event_loop().run_in_executor(
                    None, input, ">>> "
                )
                
                if not command.strip():
                    continue
                
                await self._handle_command(command.strip())
            
            except (EOFError, KeyboardInterrupt):
                print("\n👋 退出中...")
                break
            except Exception as e:
                print(f"⚠️ 输入处理错误: {e}")
    
    async def _handle_command(self, command: str):
        """处理用户命令"""
        parts = command.split()
        cmd = parts[0].lower()
        
        if cmd == "help":
            self._show_help()
        
        elif cmd == "rooms":
            await self._send_message(MessageType.ROOM_LIST, {})
        
        elif cmd == "create":
            room_name = " ".join(parts[1:]) if len(parts) > 1 else f"房间_{self.client_id[:8]}"
            await self._send_message(MessageType.CREATE_ROOM, {
                "room_name": room_name,
                "max_players": 6
            })
        
        elif cmd == "join":
            if len(parts) < 2:
                print("❌ 用法: join <房间ID> [玩家名]")
                return
            
            room_id = parts[1]
            player_name = parts[2] if len(parts) > 2 else f"玩家_{self.client_id[:8]}"
            self.player_name = player_name
            
            await self._send_message(MessageType.JOIN_ROOM, {
                "room_id": room_id,
                "player_name": player_name
            })
        
        elif cmd == "leave":
            await self._send_message(MessageType.LEAVE_ROOM, {})
        
        elif cmd == "start":
            await self._send_message(MessageType.GAME_START, {})
        
        elif cmd == "chat":
            if len(parts) < 2:
                print("❌ 用法: chat <消息内容>")
                return
            
            content = " ".join(parts[1:])
            await self._send_message(MessageType.CHAT_MESSAGE, {
                "content": content,
                "message_type": "public"
            })
        
        elif cmd == "action":
            if len(parts) < 2:
                print("❌ 用法: action <操作类型> [数据]")
                return
            
            action = parts[1]
            data = {}
            if len(parts) > 2:
                try:
                    data = json.loads(" ".join(parts[2:]))
                except json.JSONDecodeError:
                    print("❌ 无效的JSON数据")
                    return
            
            await self._send_message(MessageType.PLAYER_ACTION, {
                "action": action,
                "data": data
            })
        
        elif cmd == "quit" or cmd == "exit":
            self.running = False
        
        else:
            print(f"❌ 未知命令: {cmd} (输入 help 查看帮助)")
    
    def _show_help(self):
        """显示帮助信息"""
        print("""
📖 可用命令:
  help              - 显示此帮助信息
  rooms             - 获取房间列表
  create [房间名]    - 创建房间
  join <房间ID> [玩家名] - 加入房间
  leave             - 离开房间
  start             - 开始游戏 (仅房主)
  chat <消息>       - 发送聊天消息
  action <操作> [数据] - 执行游戏操作
  quit/exit         - 退出客户端
        """)
    
    async def _send_message(self, message_type: MessageType, data: dict):
        """发送消息"""
        if not self.websocket:
            print("❌ 未连接到服务器")
            return
        
        try:
            message = NetworkProtocol.create_message(
                message_type,
                data,
                sender_id=self.client_id
            )
            await self.websocket.send(message.to_json())
        except Exception as e:
            print(f"❌ 发送消息失败: {e}")


async def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="大富翁联机游戏测试客户端")
    parser.add_argument("--host", default="localhost", help="服务器主机地址")
    parser.add_argument("--port", type=int, default=8765, help="服务器端口")
    
    args = parser.parse_args()
    server_url = f"ws://{args.host}:{args.port}"
    
    print("=" * 60)
    print("🎮 大富翁联机游戏测试客户端")
    print("=" * 60)
    print(f"🔗 服务器地址: {server_url}")
    print("=" * 60)
    
    client = TestClient(server_url)
    await client.connect()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 再见！") 