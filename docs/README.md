# 大富翁游戏

基于Python开发的多人在线大富翁游戏，支持3-6名玩家同时在线游戏，包含AI对战功能。

## 功能特性

- 多人在线对战（3-6人）
- AI智能对战
- 丰富的道具系统
- 完整的房产系统
- 银行系统
- 骰子系统
- 存档功能
- **图形化地图编辑器（新增）**

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行游戏

```bash
python main.py
```

## 地图编辑器

### 命令行版本

```bash
python src/utils/map_editor.py
```

支持的命令：
- `new <width> <height>` - 创建新地图
- `load <file>` - 加载地图
- `save <file>` - 保存地图
- `display` - 显示地图
- `set <x> <y> <type>` - 设置格子类型
- `roadblock <x> <y>` - 切换路障
- `property <x> <y> <level> [owner]` - 设置房产
- `validate` - 验证地图
- `gui` - 启动图形界面
- `quit` - 退出

### 图形化版本

在命令行编辑器中输入 `gui` 命令启动图形化界面，或直接运行：

```bash
python -c "from src.utils.map_editor import MapEditor; editor = MapEditor(); editor.run_gui_editor()"
```

#### 图形化界面功能

1. **工具栏**
   - 🔍 选择工具：点击选择格子
   - 🏦 银行工具：设置银行格子
   - 🏪 商店工具：设置商店格子
   - 🚔 监狱工具：设置监狱格子
   - 🍀 好运格工具：设置好运格
   - 💀 厄运格工具：设置厄运格
   - 🚧 路障工具：放置/移除路障
   - 🏠 房产工具：设置房产
   - 🧽 橡皮擦工具：清除格子设置

2. **快捷键**
   - `Ctrl+N` - 新建地图
   - `Ctrl+O` - 打开地图
   - `Ctrl+S` - 保存地图
   - `Ctrl+Z` - 撤销
   - `Ctrl+Y` - 重做
   - `Ctrl++` - 放大
   - `Ctrl+-` - 缩小
   - `Ctrl+0` - 重置缩放
   - `1-6` - 快速切换格子类型
   - `R` - 路障工具
   - `P` - 房产工具
   - `E` - 橡皮擦工具

3. **文件格式支持**
   - JSON格式（推荐）
   - Excel格式（需要openpyxl）
   - SQLite数据库格式

#### 使用步骤

1. **创建新地图**
   - 点击"文件" → "新建地图"或按`Ctrl+N`
   - 输入地图尺寸（建议20x20）

2. **编辑地图**
   - 选择工具栏中的工具
   - 点击地图格子应用工具
   - 使用属性面板查看和编辑格子属性

3. **保存地图**
   - 点击"文件" → "保存地图"或按`Ctrl+S`
   - 选择保存格式和位置

4. **验证地图**
   - 点击"编辑" → "验证地图"
   - 查看验证结果

## 项目结构

```
monopoly/
├── src/                    # 源代码
│   ├── core/              # 核心模块
│   ├── models/            # 数据模型
│   ├── systems/           # 游戏系统
│   ├── ui/                # 用户界面
│   └── utils/             # 工具函数
│       └── map_editor.py  # 地图编辑器
├── assets/                # 资源文件
│   ├── images/            # 图片资源
│   ├── sounds/            # 音效资源
│   └── maps/              # 地图文件
├── tests/                 # 测试文件
├── docs/                  # 文档
└── data/                  # 游戏数据
```

## 开发说明

本项目采用MVC设计模式，三层架构：
- 表现层：用户界面和图形渲染
- 业务逻辑层：游戏核心逻辑
- 数据访问层：数据存储和管理

### 地图系统架构

地图系统包含以下组件：
- **Map模型**：地图数据结构和基础操作
- **MapDataManager**：地图数据管理，支持多种格式
- **MapEditor**：地图编辑器，支持命令行和图形界面
- **MapEditorGUI**：图形化地图编辑器界面

### 测试

运行所有测试：
```bash
python -m pytest tests/ -v
```

运行地图系统测试：
```bash
python tests/test_map_system.py
```

运行图形化编辑器测试：
```bash
python tests/test_gui_editor.py
``` 