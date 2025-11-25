# 修仙游戏服务器部署指南

## 📋 部署概览

将修仙游戏集成到已部署的 PMSManageBot 服务器上。

---

## 🚀 快速部署（5步完成）

### 步骤1: 上传部署文件包

```bash
# 在本地执行
scp /Users/zc/EC-AI/xiuxian-game/integration/xiuxian-deploy.tar.gz user@your-server:/tmp/
```

### 步骤2: SSH 登录服务器

```bash
ssh user@your-server
```

### 步骤3: 解压并部署文件

```bash
# 进入 PMSManageBot 目录
cd /path/to/PMSManageBot

# 解压部署包
tar -xzf /tmp/xiuxian-deploy.tar.gz -C /tmp/

# 备份数据库
cp data/data.db data/data.db.backup.$(date +%Y%m%d_%H%M%S)

# 执行数据库迁移（添加修仙游戏表）
sqlite3 data/data.db < /tmp/migrate_xiuxian_tables.sql

# 验证表是否创建成功
sqlite3 data/data.db "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'xiuxian%';"
# 应该看到17个表

# 创建 xiuxian 模块目录
mkdir -p src/app/xiuxian

# 复制集成文件
cp /tmp/credits_bridge_service.py src/app/xiuxian/
cp /tmp/xiuxian_exchange_handler.py src/app/xiuxian/
cp /tmp/xiuxian_handlers.py src/app/xiuxian/

# 创建 __init__.py
touch src/app/xiuxian/__init__.py

# 初始化游戏数据
cd /tmp
python3 init_xiuxian_data.py
```

### 步骤4: 修改 main.py

备份并编辑 `src/app/main.py`：

```bash
# 备份 main.py
cp src/app/main.py src/app/main.py.backup.$(date +%Y%m%d_%H%M%S)

# 编辑 main.py
vim src/app/main.py  # 或使用 nano
```

**在文件顶部添加导入**（在其他 import 之后）：

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
    xiuxian_battle_handler,
    xiuxian_callback_handler,
)

# 积分兑换handlers
from app.xiuxian import xiuxian_exchange_handler
```

**在 `if __name__ == "__main__":` 部分，找到注册 handlers 的位置，添加**：

```python
    # 注册修仙游戏handlers
    application.add_handler(xiuxian_start_handler)
    application.add_handler(xiuxian_status_handler)
    application.add_handler(xiuxian_cultivate_handler)
    application.add_handler(xiuxian_finish_handler)
    application.add_handler(xiuxian_breakthrough_handler)
    application.add_handler(xiuxian_sign_handler)
    application.add_handler(xiuxian_help_handler)
    application.add_handler(xiuxian_battle_handler)
    application.add_handler(xiuxian_callback_handler)

    # 注册积分兑换handlers
    xiuxian_exchange_handler.register_exchange_handlers(application)
```

### 步骤5: 重启服务

```bash
# 如果使用 systemd
sudo systemctl restart pmsmanagebot

# 或者使用 Docker
docker-compose restart

# 或者使用 pm2
pm2 restart pmsmanagebot

# 查看日志确认启动成功
tail -f /path/to/logs/pmsmanagebot.log
```

---

## ✅ 验证部署

### 1. 检查数据库表

```bash
sqlite3 data/data.db "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'xiuxian%';"
```

应该看到这些表：
- xiuxian_players
- xiuxian_items
- xiuxian_monsters
- xiuxian_exchange_records
- xiuxian_battle_records
- xiuxian_player_items
- xiuxian_sects
- xiuxian_sect_members
- xiuxian_skills
- xiuxian_player_skills
- xiuxian_cultivation_methods
- xiuxian_player_methods
- xiuxian_quests
- xiuxian_player_quests
- xiuxian_achievements
- xiuxian_player_achievements
- xiuxian_market_listings

### 2. 检查模块文件

```bash
ls -la src/app/xiuxian/
```

应该看到：
- `__init__.py`
- `credits_bridge_service.py`
- `xiuxian_exchange_handler.py`
- `xiuxian_handlers.py`

### 3. 测试 Telegram 命令

在 Telegram 中测试：
- `/灵根测试` - 创建角色
- `/状态` - 查看状态
- `/兑换灵石` - 积分兑换

---

## 🎮 完整命令列表

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

## 🐛 故障排除

### 问题1: import 错误

**症状**: `ModuleNotFoundError: No module named 'app.xiuxian'`

**解决**:
```bash
# 检查 __init__.py 是否存在
ls src/app/xiuxian/__init__.py

# 如果不存在，创建它
touch src/app/xiuxian/__init__.py
```

### 问题2: 数据库表不存在

**症状**: `no such table: xiuxian_players`

**解决**:
```bash
# 重新执行迁移
sqlite3 data/data.db < /tmp/migrate_xiuxian_tables.sql
```

### 问题3: 命令无响应

**症状**: 发送命令后 Bot 无反应

**解决**:
- 检查日志文件查看错误
- 确认 handlers 已正确注册到 application
- 验证数据库路径配置正确

### 问题4: 积分兑换失败

**症状**: 点击兑换按钮提示失败

**解决**:
```bash
# 检查用户是否有足够积分
sqlite3 data/data.db "SELECT tg_id, credits FROM user LIMIT 5;"

# 检查 telegram_id 是否匹配
sqlite3 data/data.db "SELECT telegram_id FROM xiuxian_players LIMIT 5;"
```

---

## 🔄 回滚方案

如需回滚：

```bash
# 停止服务
sudo systemctl stop pmsmanagebot

# 恢复数据库
cp data/data.db.backup.YYYYMMDD_HHMMSS data/data.db

# 恢复 main.py
cp src/app/main.py.backup.YYYYMMDD_HHMMSS src/app/main.py

# 删除 xiuxian 模块
rm -rf src/app/xiuxian/

# 重启服务
sudo systemctl start pmsmanagebot
```

---

## ⚙️ 配置调整

### 修改兑换比例

编辑 `src/app/xiuxian/xiuxian_exchange_handler.py`:

```python
EXCHANGE_RATE = 0.1      # 10积分=1灵石
DAILY_LIMIT = 10000      # 每日限额
MIN_EXCHANGE = 100       # 最小兑换
```

### 修改战斗冷却

编辑 `src/app/xiuxian/xiuxian_handlers.py`:

```python
BATTLE_COOLDOWN_MINUTES = 5  # 战斗冷却分钟数
```

### 修改数据库路径

如果数据库不在默认位置，修改两个文件：

**`xiuxian_handlers.py`**:
```python
PMS_DB_PATH = "/your/path/to/data.db"
```

**`xiuxian_exchange_handler.py`**:
```python
PMS_DB_PATH = "/your/path/to/data.db"
XIUXIAN_DB_PATH = "/your/path/to/data.db"
```

---

## 📝 部署检查清单

部署完成后，确认以下项目：

- [ ] 数据库已备份
- [ ] 迁移脚本执行成功（17个表已创建）
- [ ] xiuxian 模块文件已复制
- [ ] `__init__.py` 已创建
- [ ] `main.py` 已正确修改
- [ ] 游戏数据已初始化
- [ ] 服务已重启
- [ ] `/灵根测试` 命令响应正常
- [ ] `/状态` 命令显示正常
- [ ] `/兑换灵石` 功能正常
- [ ] 日志无错误信息

---

## 🎉 完成！

部署完成后，用户就可以在 Telegram Bot 中：
- ✨ 使用PMS积分兑换修仙灵石
- 🧘 开始修仙之旅
- ⚔️ 挑战怪物获得奖励
- 💎 每日签到积累资源

**祝您修仙愉快！** ✨
