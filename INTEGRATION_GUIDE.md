# PMSManageBot与修仙游戏对接指南

## 📋 对接方案

### 方案概述

将修仙游戏集成到PMSManageBot中，实现积分系统互通：
- PMS积分可以兑换修仙灵石
- PMS积分可以直接购买修仙道具
- 共享用户体系（telegram_id）
- 统一Bot管理

---

## 🏗️ 架构设计

### 系统关系图

```
PMSManageBot (主系统)
├── user表 (tg_id, credits)
├── emby_user表
└── 修仙游戏模块
    ├── players表 (telegram_id → tg_id)
    ├── exchange_records表 (积分兑换记录)
    └── credits_purchases表 (积分购买记录)
```

### 数据流向

```
用户观看Emby/Plex → 获得PMS积分
     ↓
PMS积分 → 兑换 → 修仙灵石
     ↓
修仙灵石 → 购买 → 修仙道具
```

或

```
PMS积分 → 直接购买 → 修仙道具（积分专区）
```

---

## 🔧 实施方案

### 方案A：模块集成（推荐）⭐

#### 目录结构

```
PMSManageBot/
├── src/app/
│   ├── db.py (现有)
│   ├── main.py (现有)
│   ├── handlers/ (现有)
│   └── xiuxian/ (新增修仙游戏模块)
│       ├── __init__.py
│       ├── models/
│       │   ├── player.py
│       │   ├── item.py
│       │   ├── sect.py
│       │   └── bridge.py (积分桥接)
│       ├── services/
│       │   ├── player_service.py
│       │   ├── cultivation_service.py
│       │   ├── battle_service.py
│       │   └── credits_bridge_service.py (新增)
│       └── handlers/
│           ├── xiuxian_start.py
│           ├── xiuxian_cultivation.py
│           └── xiuxian_exchange.py (新增)
```

#### 核心功能模块

##### 1. 积分桥接服务

```python
# src/app/xiuxian/services/credits_bridge_service.py

from app.db import DB  # 导入PMSManageBot的DB类

class CreditsBridgeService:
    """PMS积分桥接服务"""

    @staticmethod
    def get_pms_credits(telegram_id: int) -> int:
        """获取PMS积分余额"""
        db = DB()
        user = db.get_user(telegram_id)
        if user:
            return user.get('credits', 0)
        return 0

    @staticmethod
    def deduct_pms_credits(telegram_id: int, amount: int) -> bool:
        """扣除PMS积分"""
        db = DB()
        user = db.get_user(telegram_id)
        if user and user.get('credits', 0) >= amount:
            new_credits = user['credits'] - amount
            db.update_credits(telegram_id, new_credits)
            return True
        return False

    @staticmethod
    def exchange_to_spirit_stones(
        telegram_id: int,
        credits_amount: int,
        exchange_rate: float = 0.1  # 1积分=0.1灵石
    ) -> tuple[bool, str, int]:
        """积分兑换灵石

        Returns:
            (success, message, spirit_stones_gained)
        """
        # 检查积分余额
        current_credits = CreditsBridgeService.get_pms_credits(telegram_id)
        if current_credits < credits_amount:
            return False, f"积分不足，当前积分：{current_credits}", 0

        # 计算灵石数量
        spirit_stones = int(credits_amount * exchange_rate)
        if spirit_stones < 1:
            return False, "兑换数量太少，至少需要10积分", 0

        # 扣除积分
        if not CreditsBridgeService.deduct_pms_credits(telegram_id, credits_amount):
            return False, "积分扣除失败", 0

        # 记录兑换
        # TODO: 保存到exchange_records表

        return True, f"兑换成功！消耗{credits_amount}积分，获得{spirit_stones}灵石", spirit_stones
```

##### 2. 积分商店物品

```python
# src/app/xiuxian/models/bridge.py

from sqlalchemy import Column, Integer, BigInteger, String, DateTime
from datetime import datetime

class ExchangeRecord(Base):
    """积分兑换记录"""
    __tablename__ = "exchange_records"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, nullable=False, index=True)
    credits_amount = Column(Integer, nullable=False)  # 消耗积分
    spirit_stones_gained = Column(Integer, nullable=False)  # 获得灵石
    exchange_rate = Column(Float, nullable=False)  # 兑换比例
    created_at = Column(DateTime, default=datetime.now)


class CreditsPurchase(Base):
    """积分购买道具记录"""
    __tablename__ = "credits_purchases"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, nullable=False, index=True)
    item_id = Column(Integer, nullable=False)
    item_name = Column(String(100), nullable=False)
    credits_cost = Column(Integer, nullable=False)  # 积分消耗
    quantity = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.now)
```

##### 3. 兑换命令处理器

```python
# src/app/xiuxian/handlers/xiuxian_exchange.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

async def exchange_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """积分兑换灵石命令"""
    user = update.effective_user

    # 获取积分余额
    credits = CreditsBridgeService.get_pms_credits(user.id)

    keyboard = [
        [
            InlineKeyboardButton("100积分→10灵石", callback_data="exchange_100"),
            InlineKeyboardButton("500积分→50灵石", callback_data="exchange_500"),
        ],
        [
            InlineKeyboardButton("1000积分→100灵石", callback_data="exchange_1000"),
            InlineKeyboardButton("5000积分→500灵石", callback_data="exchange_5000"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = f"""
💱 **积分兑换中心**

📊 当前PMS积分：{credits}

兑换比例：10积分 = 1灵石

请选择兑换数量：
"""

    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")
```

---

## 📝 实施步骤

### 步骤1：准备工作

```bash
# 1. 备份PMSManageBot数据
cp -r PMSManageBot PMSManageBot_backup

# 2. 在PMSManageBot项目中创建xiuxian目录
cd PMSManageBot/src/app
mkdir -p xiuxian/{models,services,handlers}
```

### 步骤2：复制修仙游戏代码

```bash
# 复制模型文件
cp /path/to/xiuxian-game/src/bot/models/* PMSManageBot/src/app/xiuxian/models/

# 复制服务文件
cp /path/to/xiuxian-game/src/bot/services/* PMSManageBot/src/app/xiuxian/services/

# 复制处理器文件
cp /path/to/xiuxian-game/src/bot/handlers/* PMSManageBot/src/app/xiuxian/handlers/
```

### 步骤3：创建积分桥接服务

创建 `PMSManageBot/src/app/xiuxian/services/credits_bridge_service.py`

（使用上面提供的代码）

### 步骤4：修改数据库连接

修改 `PMSManageBot/src/app/xiuxian/models/database.py`：

```python
# 使用PMSManageBot的数据库配置
from app.config import settings

DATABASE_URL = f"sqlite:///{settings.DATA_PATH}/data.db"
```

### 步骤5：注册命令到主Bot

修改 `PMSManageBot/src/app/main.py`：

```python
# 导入修仙游戏handlers
from app.xiuxian.handlers import xiuxian_start, xiuxian_cultivation, xiuxian_exchange

# 在main函数中注册
def main():
    application = ApplicationBuilder().token(settings.BOT_TOKEN).build()

    # ... 现有handlers ...

    # 注册修仙游戏handlers
    application.add_handler(CommandHandler("xiuxian", xiuxian_start.start_command))
    application.add_handler(CommandHandler("exchange", xiuxian_exchange.exchange_command))
    application.add_handler(CommandHandler("cultivate", xiuxian_cultivation.cultivate_command))
    # ... 更多修仙命令 ...

    application.run_polling()
```

### 步骤6：添加主菜单入口

修改PMSManageBot的start命令，添加修仙入口：

```python
keyboard = [
    [
        InlineKeyboardButton("📊 Emby状态", callback_data="emby_status"),
        InlineKeyboardButton("🎬 Plex状态", callback_data="plex_status"),
    ],
    [
        InlineKeyboardButton("🧘 修仙世界", callback_data="xiuxian_world"),  # 新增
        InlineKeyboardButton("💱 积分兑换", callback_data="credits_exchange"),  # 新增
    ],
    # ... 其他按钮 ...
]
```

---

## 🎮 功能设计

### 1. 积分兑换系统

**兑换比例**：
- 默认：10 PMS积分 = 1 修仙灵石
- 可在配置中调整

**兑换命令**：
- `/exchange` - 打开兑换菜单
- `/exchange 1000` - 直接兑换1000积分

**兑换限制**：
- 单次最少兑换：100积分
- 单日兑换上限：可配置（例如10000积分）

### 2. 积分商店

**专区设计**：
- 普通商店（灵石购买）
- 积分商店（PMS积分购买）

**积分商店物品示例**：
```
- 高级筑基丹：1000积分
- 精良武器：2000积分
- 稀有功法：5000积分
- 宗门建筑加速：3000积分
```

### 3. 用户界面

**修仙主菜单**：
```
🧘 修仙世界

📊 角色状态
💎 当前灵石：5000
💰 PMS积分：10000

快捷操作：
[🧘 修炼] [⚔️ 战斗] [🏪 商店]
[💱 兑换] [🏛️ 宗门] [📖 帮助]
```

---

## ⚙️ 配置参数

### 在 .env 中添加

```env
# 修仙游戏配置
XIUXIAN_ENABLED=true
XIUXIAN_EXCHANGE_RATE=0.1  # 1积分=0.1灵石
XIUXIAN_DAILY_EXCHANGE_LIMIT=10000  # 每日兑换上限
XIUXIAN_MIN_EXCHANGE=100  # 最小兑换数量
```

---

## 🔍 数据库迁移

### 添加新表

在PMSManageBot的数据库中添加修仙游戏相关表：

```sql
-- 修仙玩家表
CREATE TABLE IF NOT EXISTS xiuxian_players(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER UNIQUE NOT NULL,
    nickname TEXT NOT NULL,
    realm TEXT DEFAULT 'MORTAL',
    realm_level INTEGER DEFAULT 0,
    cultivation_exp INTEGER DEFAULT 0,
    spirit_stones INTEGER DEFAULT 0,
    hp INTEGER DEFAULT 100,
    max_hp INTEGER DEFAULT 100,
    attack INTEGER DEFAULT 10,
    defense INTEGER DEFAULT 5,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 积分兑换记录
CREATE TABLE IF NOT EXISTS xiuxian_exchange_records(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER NOT NULL,
    credits_amount INTEGER NOT NULL,
    spirit_stones_gained INTEGER NOT NULL,
    exchange_rate REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 积分购买记录
CREATE TABLE IF NOT EXISTS xiuxian_credits_purchases(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER NOT NULL,
    item_id INTEGER NOT NULL,
    item_name TEXT NOT NULL,
    credits_cost INTEGER NOT NULL,
    quantity INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_xiuxian_players_telegram ON xiuxian_players(telegram_id);
CREATE INDEX IF NOT EXISTS idx_exchange_records_telegram ON xiuxian_exchange_records(telegram_id);
CREATE INDEX IF NOT EXISTS idx_credits_purchases_telegram ON xiuxian_credits_purchases(telegram_id);
```

---

## 📊 数据同步

### 用户关联

```python
def link_pms_user_to_xiuxian(telegram_id):
    """关联PMS用户到修仙系统"""
    # 1. 检查PMS用户是否存在
    pms_user = db.get_user(telegram_id)
    if not pms_user:
        return False, "PMS用户不存在"

    # 2. 检查修仙角色是否已创建
    xiuxian_player = get_xiuxian_player(telegram_id)
    if xiuxian_player:
        return True, "已关联"

    # 3. 创建修仙角色
    create_xiuxian_player(telegram_id, pms_user['username'])

    return True, "关联成功"
```

---

## 🚀 启动流程

### 修改后的启动命令

```bash
# 1. 初始化修仙数据表
python scripts/init_xiuxian_tables.py

# 2. 导入初始数据（怪物、物品等）
python scripts/init_xiuxian_data.py

# 3. 启动Bot
python src/app/main.py
```

---

## 🎯 用户体验流程

### 场景1：积分兑换灵石

```
用户: /exchange
Bot: 显示当前积分和兑换菜单
用户: 点击"1000积分→100灵石"
Bot: 扣除1000积分，增加100灵石
Bot: "兑换成功！消耗1000积分，获得100灵石"
```

### 场景2：积分购买道具

```
用户: /shop
Bot: 显示商店菜单（灵石商店 | 积分商店）
用户: 点击"积分商店"
Bot: 显示可用积分购买的物品
用户: 选择"高级筑基丹(1000积分)"
Bot: 扣除1000积分，发放物品
Bot: "购买成功！获得高级筑基丹×1"
```

### 场景3：查看综合状态

```
用户: /status
Bot:
📊 角色状态

PMS系统：
💰 积分：10000
🎬 观看时长：120小时

修仙系统：
🌟 境界：筑基期3层
💎 灵石：5000
⚔️ 战力：850
```

---

## 🔒 安全考虑

### 1. 事务安全

```python
# 积分兑换需要事务保证
def safe_exchange(telegram_id, credits):
    try:
        # 1. 开始事务
        # 2. 扣除积分
        # 3. 增加灵石
        # 4. 记录兑换
        # 5. 提交事务
        pass
    except Exception as e:
        # 回滚事务
        rollback()
        return False, str(e)
```

### 2. 并发控制

使用Redis锁防止重复兑换：

```python
def exchange_with_lock(telegram_id, credits):
    lock_key = f"exchange_lock:{telegram_id}"
    if redis.exists(lock_key):
        return False, "操作进行中，请稍后"

    redis.setex(lock_key, 10, "1")  # 10秒锁
    try:
        result = do_exchange(telegram_id, credits)
        return result
    finally:
        redis.delete(lock_key)
```

### 3. 日志记录

所有积分操作都应记录：

```python
logger.info(f"Exchange: user={telegram_id}, credits={credits}, stones={stones}")
```

---

## 📈 数据统计

### 统计指标

- 每日兑换总量
- 每日积分消耗
- 热门积分商品
- 用户兑换习惯

### 统计查询

```sql
-- 今日兑换统计
SELECT
    COUNT(*) as exchange_count,
    SUM(credits_amount) as total_credits,
    SUM(spirit_stones_gained) as total_stones
FROM xiuxian_exchange_records
WHERE DATE(created_at) = DATE('now');

-- 积分商品热度
SELECT
    item_name,
    COUNT(*) as purchase_count,
    SUM(credits_cost) as total_credits
FROM xiuxian_credits_purchases
GROUP BY item_name
ORDER BY purchase_count DESC
LIMIT 10;
```

---

## 🎨 界面优化建议

### WebApp集成

在PMSManageBot的WebApp中添加修仙模块：

```
webapp-frontend/src/views/Xiuxian.vue
- 角色状态展示
- 积分兑换界面
- 积分商店
- 修炼进度
```

### 通知优化

```python
# 修炼完成通知
async def notify_cultivation_complete(telegram_id):
    await bot.send_message(
        chat_id=telegram_id,
        text="✨ 修炼完成！获得1000修为\n\n💡 使用PMS积分可以加速修炼哦！"
    )
```

---

## 📚 总结

通过这个对接方案，您可以实现：

✅ **统一用户体验** - 一个Bot管理两个系统
✅ **积分互通** - PMS积分转化为游戏资源
✅ **价值增强** - 观看影片的积分更有价值
✅ **游戏性提升** - 积分商店提供便捷购买
✅ **数据安全** - 事务保证和日志记录

---

## 🤝 后续支持

需要帮助实施？我可以：
1. 生成完整的代码文件
2. 编写迁移脚本
3. 测试对接功能
4. 优化性能
5. 添加更多功能

**请告诉我是否开始实施！** 🚀
