"""
游戏常量配置
"""

# 游戏基础配置
GAME_NAME = "大富翁"
GAME_VERSION = "1.0.0"

# 地图配置
MAP_WIDTH = 20
MAP_HEIGHT = 20
CELL_SIZE = 40  # 每个格子的像素大小

# 玩家配置
MIN_PLAYERS = 3
MAX_PLAYERS = 6
INITIAL_MONEY = 200000  # 初始资金
INITIAL_BANK_MONEY = 100000  # 银行初始资金
INITIAL_ITEMS = ["路障", "路障", "路障"]  # 初始道具

# 颜色配置
COLORS = {
    "WHITE": (255, 255, 255),
    "BLACK": (0, 0, 0),
    "RED": (255, 0, 0),
    "GREEN": (0, 255, 0),
    "BLUE": (0, 0, 255),
    "YELLOW": (255, 255, 0),
    "PURPLE": (128, 0, 128),
    "ORANGE": (255, 165, 0),
    "GRAY": (128, 128, 128),
    "LIGHT_GRAY": (192, 192, 192),
    "DARK_GRAY": (64, 64, 64),
    "BROWN": (139, 69, 19),
    "PINK": (255, 192, 203),
    "CYAN": (0, 255, 255),
    "MAGENTA": (255, 0, 255)
}

# 格子类型
CELL_TYPES = {
    "EMPTY": "empty",      # 空地（可建房产）
    "WALL": "wall",        # 墙（不可移动）
    "VOID": "void",        # 空格（不可移动，无任何功能）
    "BANK": "bank",        # 银行
    "SHOP": "shop",        # 道具商店
    "DICE_SHOP": "dice_shop",  # 骰子商店
    "JAIL": "jail",        # 监狱
    "LUCK": "luck",        # 好运格
    "BAD_LUCK": "bad_luck" # 厄运格
}

# 格子颜色映射
CELL_COLORS = {
    "empty": COLORS["WHITE"],
    "wall": COLORS["DARK_GRAY"],
    "void": COLORS["BLACK"],
    "bank": COLORS["GREEN"],
    "shop": COLORS["ORANGE"],
    "dice_shop": COLORS["CYAN"],  # 骰子商店用青色
    "jail": COLORS["RED"],
    "luck": COLORS["PURPLE"],
    "bad_luck": COLORS["BROWN"]
}

# 道具配置
ITEMS = {
    "路障": {
        "price": 10000,
        "description": "在距自身直线距离不超过14的格子上放置路障，碰到立即停止"
    },
    "再装逼让你飞起来!!": {
        "price": 20000,
        "description": "获得起飞效果，下次移动可无视地图限制，落地后钱散落周围"
    },
    "庇护术": {
        "price": 20000,
        "description": "直到下次使用道具卡前不受任何道具影响"
    },
    "六百六十六": {
        "price": 15000,
        "description": "下次投掷时每个骰子结果总为6"
    },
    "违规爆建": {
        "price": 25000,
        "description": "使自身房产升一级或使他人房产降一级"
    }
}

# 房产配置
PROPERTY_LEVELS = {
    1: {"cost": 10000, "rent": 5000},
    2: {"cost": 20000, "rent": 10000},
    3: {"cost": 30000, "rent": 15000},
    4: {"cost": 0, "rent": 50000}  # 四级房产只能通过道具升级
}

# 银行利息配置
BANK_INTEREST = {
    100000: 0.05,   # 资产<100,000：5%利息
    300000: 0.10,   # 资产≥100,000：10%利息
    500000: 0.20,   # 资产≥300,000：20%利息
    999999999: 0.30  # 资产≥500,000：30%利息
}

# 骰子配置
DICE_TYPES = {
    "d6": {"sides": 6, "count": 1},
    "d8": {"sides": 8, "count": 1},
    "d12": {"sides": 12, "count": 1},
    "d20": {"sides": 20, "count": 1},
    "2d6": {"sides": 6, "count": 2},
    "2d8": {"sides": 8, "count": 2},
    "3d6": {"sides": 6, "count": 3},
    "2d20": {"sides": 20, "count": 2}
}

# 骰子商店价格
DICE_PRICES = {
    "d8": {"money": 10000, "items": 1},
    "d12": {"money": 50000, "items": 1},
    "2d6": {"money": 10000, "items": 3},
    "2d8": {"money": 50000, "items": 3},
    "3d6": {"money": 40000, "items": 4},
    "2d20": {"money": 77777, "items": 7}
}

# 游戏状态
GAME_STATES = {
    "WAITING": "waiting",      # 等待开始
    "PLAYING": "playing",      # 游戏中
    "PAUSED": "paused",        # 暂停
    "FINISHED": "finished"     # 游戏结束
}

# 回合阶段
TURN_PHASES = {
    "PREPARATION": "preparation",  # 准备阶段
    "ACTION": "action",            # 行动阶段
    "SETTLEMENT": "settlement",    # 结算阶段
    "END": "end"                   # 结束阶段
} 