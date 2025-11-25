# 修仙游戏快速集成指南

## 📋 集成概览

将修仙游戏完整集成到PMSManageBot中，让用户可以使用PMS积分兑换灵石，并在Telegram Bot中享受完整的修仙RPG体验。

---

## 🚀 快速开始（5步完成集成）

### 步骤1: 迁移数据库表

将修仙游戏的数据表添加到PMSManageBot数据库中：

```bash
cd /Users/zc/EC-AI/PMSManageBot

# 备份现有数据库
cp data/data.db data/data.db.backup

# 执行迁移
sqlite3 data/data.db < /Users/zc/EC-AI/xiuxian-game/integration/migrate_xiuxian_tables.sql

# 验证迁移
sqlite3 data/data.db "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'xiuxian%';"
```

### 步骤2: 复制集成文件

将修仙游戏模块复制到PMSManageBot项目中：

```bash
cd /Users/zc/EC-AI/PMSManageBot/src/app

# 创建修仙模块目录
mkdir -p xiuxian

# 复制集成文件
cp /Users/zc/EC-AI/xiuxian-game/integration/credits_bridge_service.py xiuxian/
cp /Users/zc/EC-AI/xiuxian-game/integration/xiuxian_exchange_handler.py xiuxian/
cp /Users/zc/EC-AI/xiuxian-game/integration/xiuxian_handlers.py xiuxian/

# 创建__init__.py
touch xiuxian/__init__.py
```

### 步骤3: 注册命令处理器

编辑 `/Users/zc/EC-AI/PMSManageBot/src/app/main.py`，添加修仙游戏handlers：

在文件顶部添加导入：
```python
# 修仙游戏handlers
from app.xiuxian.xiuxian_handlers import (
    xiuxian_start_handler,
    xiuxian_status_handler,
    xiuxian_cultivate_handler,
    xiuxian_finish_handler,
    xiuxian_breakthrough_handler,
    xiuxian_sign_handler,
    xiuxian_help_handler,
    xiuxian_callback_handler,
)

# 积分兑换handlers
from app.xiuxian import xiuxian_exchange_handler
```

在 `if __name__ == "__main__":` 部分，注册处理器之前添加：
```python
    # 注册修仙游戏handlers
    xiuxian_exchange_handler.register_exchange_handlers(application)
```

### 步骤4: 初始化游戏数据

运行初始化脚本，创建怪物、物品等游戏数据：

```bash
cd /Users/zc/EC-AI/xiuxian-game
python integration/init_xiuxian_data.py
```

### 步骤5: 重启Bot

```bash
cd /Users/zc/EC-AI/PMSManageBot
# 如果使用systemd
sudo systemctl restart pmsmanagebot

# 或者直接运行
cd src
python -m app.main
```

---

## 🎮 使用指南

### 积分兑换功能

用户可以在Telegram Bot中使用以下命令：

```
/兑换灵石 - 打开积分兑换菜单
/兑换灵石 1000 - 快速兑换1000积分
```

**兑换规则**:
- 兑换比例：10积分 = 1灵石
- 最小兑换：100积分
- 每日上限：10000积分
- 自动记录兑换历史

### 修仙游戏命令（中文风格）

```
📋 基础命令:
/灵根测试 - 创建角色，测试修仙资质
/状态 - 查看角色状态
/签到 - 每日签到领取灵石
/NPC - 查看帮助信息

🧘 修炼系统:
/闭关 - 开始闭关修炼
/出关 - 完成修炼收取修为
/渡劫 - 境界突破

⚔️ 战斗系统:
/历练 - 外出斩妖除魔
/切磋 @道友 - 玩家切磋比试

🎒 物品系统:
/储物袋 - 查看储物袋
/使用 [物品] - 使用物品

🏪 坊市系统:
/坊市 - 进入坊市
/购买 [物品] - 购买物品

💱 积分兑换:
/兑换灵石 - PMS积分兑换灵石
```

---

## 📂 文件结构

集成后的PMSManageBot目录结构：

```
PMSManageBot/
├── src/app/
│   ├── xiuxian/                    # 修仙游戏模块（新增）
│   │   ├── __init__.py
│   │   ├── credits_bridge_service.py
│   │   ├── xiuxian_exchange_handler.py
│   │   └── xiuxian_handlers.py
│   ├── main.py                     # 已修改，添加了修仙handlers注册
│   └── ... （其他现有文件）
├── data/
│   ├── data.db                     # 已扩展，包含修仙表
│   └── data.db.backup              # 备份
└── ...
```

---

## 🔧 配置说明

### 兑换参数配置

在 `xiuxian_exchange_handler.py` 中可以调整：

```python
# 兑换比例：1积分=0.1灵石（即10积分=1灵石）
EXCHANGE_RATE = 0.1

# 每日兑换上限
DAILY_LIMIT = 10000

# 最小兑换数量
MIN_EXCHANGE = 100

# 数据库路径
PMS_DB_PATH = "./data/data.db"
XIUXIAN_DB_PATH = "./data/data.db"  # 已集成到同一数据库
```

### 战斗冷却配置

在 `xiuxian_handlers.py` 中：

```python
# 战斗冷却时间（分钟）
BATTLE_COOLDOWN_MINUTES = 5
```

---

## 🗄️ 数据库说明

### 新增的核心表

| 表名 | 用途 | 关键字段 |
|------|------|---------|
| `xiuxian_players` | 玩家角色信息 | telegram_id, realm, cultivation_exp, spirit_stones |
| `xiuxian_items` | 物品/装备/丹药 | name, item_type, grade, properties |
| `xiuxian_monsters` | 怪物数据 | name, level, realm, hp, attack |
| `xiuxian_exchange_records` | 积分兑换记录 | telegram_id, credits_amount, spirit_stones_gained |
| `xiuxian_battle_records` | 战斗记录 | player_id, result, exp_gained |
| `xiuxian_sects` | 宗门信息 | name, master_id, level, treasury |

### 与PMS系统的关联

- **用户关联**: 通过 `telegram_id` 字段关联PMS的user表
- **积分系统**: 桥接服务读取 `user.credits` 或 `emby_user.emby_credits`
- **交易记录**: 所有兑换记录存储在 `xiuxian_exchange_records` 表

---

## 🧪 测试验证

### 测试积分兑换

```bash
# 进入Python环境
cd /Users/zc/EC-AI/PMSManageBot/src
python

# 测试脚本
from app.xiuxian.credits_bridge_service import CreditsBridgeService

bridge = CreditsBridgeService("../data/data.db")

# 查询积分
telegram_id = 123456789  # 替换为实际用户ID
credits = bridge.get_pms_credits(telegram_id)
print(f"当前积分：{credits}")

# 测试兑换
success, message, stones = bridge.exchange_to_spirit_stones(
    telegram_id=telegram_id,
    credits_amount=1000,
    exchange_rate=0.1,
    xiuxian_db_path="../data/data.db"
)
print(f"兑换结果：{message}, 获得灵石：{stones}")
```

### 测试修仙命令

在Telegram中：
1. 发送 `/start` - 应该创建角色并显示欢迎信息
2. 发送 `/status` - 应该显示角色面板
3. 发送 `/exchange` - 应该显示积分兑换菜单
4. 点击兑换按钮 - 应该成功兑换并获得灵石
5. 发送 `/sign` - 应该获得每日签到奖励

---

## ⚠️ 注意事项

### 1. 数据库备份
集成前务必备份数据库：
```bash
cp data/data.db data/data.db.backup.$(date +%Y%m%d)
```

### 2. 权限检查
确保Bot有足够权限执行所有命令

### 3. 命令冲突
如果PMSManageBot已有 `/start`、`/help` 等命令，需要：
- 选项A：将修仙命令改为 `/xiuxian_start`、`/xiuxian_help`
- 选项B：在现有命令中添加修仙入口（推荐）

### 4. 性能考虑
- 大量用户时建议添加Redis缓存
- 定期清理旧的战斗记录
- 考虑分表存储兑换历史

---

## 🐛 常见问题

### Q1: 运行迁移脚本时报错
**A**: 检查数据库文件路径是否正确，确保有写入权限

### Q2: 找不到xiuxian模块
**A**: 确认已创建 `app/xiuxian/__init__.py` 文件

### Q3: 积分扣除了但灵石没到账
**A**: 检查 `xiuxian_players` 表中 `telegram_id` 是否匹配

### Q4: 修炼时间到了但没法收取
**A**: 使用 `/finish` 命令手动收取修为

### Q5: 用户余额变为负数
**A**: 桥接服务有检查机制，如果出现请检查数据库事务是否正确

---

## 📈 进阶功能（可选）

### 添加定时任务

在 `main.py` 的 `add_init_scheduler_job()` 中添加：

```python
# 每小时恢复玩家生命值
scheduler.add_async_job(
    func=restore_player_hp,
    trigger="cron",
    id="restore_player_hp",
    replace_existing=True,
    max_instances=1,
    minute=0,
)

# 每天凌晨重置每日任务
scheduler.add_async_job(
    func=reset_daily_quests,
    trigger="cron",
    id="reset_daily_quests",
    replace_existing=True,
    max_instances=1,
    hour=0,
    minute=0,
)
```

### 添加WebApp界面

可以在PMSManageBot的WebApp中添加修仙游戏面板，提供更丰富的UI体验。

---

## 📞 技术支持

如遇到问题，请检查：
1. 日志文件：`data/logs/xiuxian.log`
2. 数据库完整性：使用SQLite工具检查
3. Python依赖：确保所有依赖已安装

---

## ✅ 集成检查清单

完成以下检查后即可上线：

- [ ] 数据库备份完成
- [ ] 迁移脚本执行成功
- [ ] 文件复制到正确位置
- [ ] main.py已更新并注册handlers
- [ ] 初始化数据脚本已运行
- [ ] 测试积分兑换功能正常
- [ ] 测试修仙命令响应正确
- [ ] 检查无命令冲突
- [ ] 验证数据一致性
- [ ] Bot重启成功

---

**集成完成！** 🎉

用户现在可以在PMSManageBot中使用PMS积分兑换灵石，并享受完整的修仙RPG游戏体验！
