# 🎲 大富翁游戏 | Monopoly Game

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Pygame](https://img.shields.io/badge/Pygame-2.6+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)

**一个功能完整的多人在线大富翁游戏，基于Python和Pygame开发**

[特性](#-特性) • [安装](#-安装) • [快速开始](#-快速开始) • [游戏模式](#-游戏模式) • [开发文档](#-开发文档)

</div>

---

## 📖 项目简介

这是一个基于Python开发的现代化大富翁游戏，支持单机AI对战和多人在线游戏。项目采用模块化设计，具有完整的游戏系统、美观的图形界面和强大的扩展性。

### 🎯 核心特色

- 🎮 **多种游戏模式**：单机、AI对战、多人联机
- 🎨 **现代化界面**：基于Pygame的精美图形界面
- 🗺️ **地图编辑器**：可视化地图创建和编辑工具
- 💾 **完整存档系统**：支持JSON和SQLite多种格式
- 🌐 **网络对战**：基于WebSocket的实时多人游戏
- 🎲 **丰富道具系统**：多种骰子、道具和策略元素

## ✨ 特性

### 🎮 游戏核心

- **玩家系统**：支持3-6名玩家，人机混合对战
- **智能AI**：多种难度的AI对手，策略丰富
- **房产系统**：购买、建设、升级房产
- **银行系统**：存款取款、利息计算
- **道具系统**：路障、传送门、金钱卡等
- **骰子系统**：多种特殊骰子（d6、d8、d12、2d6等）

### 🛠️ 开发特性

- **模块化架构**：清晰的MVC设计模式
- **完整测试**：37个测试文件，覆盖核心功能
- **文档齐全**：详细的开发和使用文档
- **工具丰富**：地图编辑器、调试工具、修复脚本

### 🌐 网络功能

- **房间系统**：创建和加入游戏房间
- **实时通信**：WebSocket协议，低延迟
- **状态同步**：游戏状态实时同步
- **断线重连**：网络异常自动恢复

## 🚀 安装

### 系统要求

- **Python**: 3.8 或更高版本
- **操作系统**: Windows 10+, macOS 10.14+, Linux (Ubuntu 18.04+)
- **内存**: 512MB RAM (推荐 1GB+)
- **存储**: 100MB 可用空间

### 安装步骤

1. **克隆项目**
   ```bash
   git clone https://github.com/your-username/monopoly-game.git
   cd monopoly-game
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **验证安装**
   ```bash
   python gui_main.py
   ```

### 虚拟环境（推荐）

```bash
# 创建虚拟环境
python -m venv DaFuWeng

# 激活虚拟环境
# Windows:
DaFuWeng\Scripts\activate
# macOS/Linux:
source DaFuWeng/bin/activate

# 安装依赖
pip install -r requirements.txt
```

## 🎮 快速开始

### 启动游戏

```bash
# 图形界面版本（推荐）
python gui_main.py

# 命令行版本
python main.py
```

### 基本操作

1. **选择游戏模式**：单机模式
2. **配置玩家**：设置玩家数量和AI难度
3. **选择地图**：使用内置地图或自定义地图
4. **开始游戏**：按照提示进行游戏

### 快捷键

| 快捷键 | 功能 |
|--------|------|
| `F5` | 快速保存 |
| `F9` | 快速加载 |
| `Ctrl+S` | 保存游戏 |
| `Ctrl+L` | 加载游戏 |
| `Ctrl+M` | 打开地图编辑器 |
| `ESC` | 返回主菜单 |

## 🎯 游戏模式

### 单机模式
- 与AI对手进行游戏
- 支持1-5个AI玩家
- 多种AI难度设置


### 自定义游戏
- 使用地图编辑器创建地图
- 自定义游戏规则
- 导入/导出地图文件

## 🛠️ 开发文档

### 项目结构

```
monopoly-game/
├── src/                    # 源代码
│   ├── core/              # 核心模块
│   ├── models/            # 数据模型
│   ├── systems/           # 游戏系统
│   ├── ui/                # 用户界面
│   ├── network/           # 网络模块
│   └── utils/             # 工具函数
├── assets/                # 游戏资源
│   ├── images/            # 图片资源
│   ├── sounds/            # 音效资源
│   └── maps/              # 地图文件
├── tests/                 # 测试文件
├── tools/                 # 开发工具
├── scripts/               # 脚本文件
├── server/                # 服务器文件
├── network/               # 网络客户端
├── examples/              # 示例代码
├── docs/                  # 详细文档
└── data/                  # 游戏数据
```

### 开发指南

详细的开发文档请参考 [`docs/`](docs/) 目录：

- 📋 [项目总体设计文档](docs/项目总体设计文档.md)
- 🎮 [基本程序设计文档](docs/基本程序设计文档.md)
- 🗺️ [地图程序设计文档](docs/地图程序设计文档.md)
- 🌐 [联机程序设计文档](docs/联机程序设计文档.md)
- 🎨 [素材美术设计文档](docs/素材美术设计文档.md)

### 运行测试

```bash
# 运行所有测试
python -m pytest tests/ -v

# 运行特定测试
python -m pytest tests/test_game_core.py -v

# 生成测试覆盖率报告
python -m pytest tests/ --cov=src --cov-report=html
```

## 🔧 工具使用

### 地图编辑器

```bash
# 启动图形化地图编辑器
python tools/enhanced_map_editor.py

# 启动简化版编辑器
python tools/run_enhanced_editor.py
```

**地图编辑器功能**：
- 🖱️ 可视化编辑界面
- 🎨 多种格子类型
- 🏠 房产设置
- 🚧 路障放置
- 💾 多格式保存（JSON、Excel）

### 服务器管理

```bash
# 启动游戏服务器
python server/start_multiplayer_server.py

# 启动房间服务器
python server/room_server.py

# 服务器状态检查
python network/quick_client.py
```

## 📝 更新日志

### v2.0.0 (最新)
- 🎨 重构用户界面
- 🗺️ 增强地图编辑器
- 💾 改进存档系统
- 🔧 大量bug修复

### v1.5.0
- 🎲 新增特殊骰子系统
- 🛍️ 完善道具商店
- 🏦 改进银行系统
- 🤖 增强AI智能

## 🤝 贡献指南

我们欢迎所有形式的贡献！

1. **Fork** 项目
2. 创建你的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开一个 **Pull Request**

### 开发环境配置

```bash
# 安装开发依赖
pip install -r requirements.txt

# 安装代码检查工具
pip install flake8 black

# 运行代码格式化
black src/

# 运行代码检查
flake8 src/
```

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 🆘 支持

- 📧 **邮箱**: support@monopoly-game.com
- 🐛 **Bug报告**: [Issues](https://github.com/your-username/monopoly-game/issues)
- 💬 **讨论**: [Discussions](https://github.com/your-username/monopoly-game/discussions)
- 📖 **文档**: [Wiki](https://github.com/your-username/monopoly-game/wiki)

## 🌟 致谢

- 感谢所有贡献者的努力
- 特别感谢测试团队的反馈
- 感谢开源社区的支持

---

<div align="center">

**如果这个项目对你有帮助，请给我们一个 ⭐️**

Made with ❤️ by [HxiaoLZ23]

</div> 
