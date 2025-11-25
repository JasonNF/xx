# 修仙游戏 × PMSManageBot 集成包

## 📦 这是什么？

这是一个完整的集成包，用于将修仙RPG游戏添加到您的PMSManageBot中。

**核心功能**:
- 💱 使用PMS积分兑换修仙游戏灵石（10积分=1灵石）
- 🧘 完整的修仙游戏系统（修炼、战斗、突破等）
- 📊 17个数据库表存储游戏数据
- 🎮 20+个游戏命令和交互界面

---

## 🚀 快速开始（3分钟完成）

### 步骤1: 运行一键集成脚本

```bash
cd /Users/zc/EC-AI/xiuxian-game/integration
./integrate.sh
```

### 步骤2: 重启PMSManageBot

```bash
cd /Users/zc/EC-AI/PMSManageBot/src
python -m app.main
```

### 步骤3: 在Telegram测试

发送以下命令测试：
- `/start` - 创建修仙角色
- `/status` - 查看角色状态
- `/exchange` - 积分兑换灵石

**完成！** ✨

---

## 📁 文件说明

| 文件 | 说明 | 用途 |
|------|------|------|
| **integrate.sh** | ⭐ 一键集成脚本 | 自动完成所有集成步骤 |
| **INTEGRATION_COMPLETE.md** | 📖 完成指南 | 集成后的使用说明 |
| **QUICK_INTEGRATION_GUIDE.md** | 📚 快速指南 | 5步手动集成教程 |
| **INTEGRATION_GUIDE.md** | 📘 详细文档 | 完整技术文档 |
| migrate_xiuxian_tables.sql | 数据库迁移 | 添加游戏表到数据库 |
| credits_bridge_service.py | 积分桥接 | 连接PMS积分和灵石 |
| xiuxian_exchange_handler.py | 兑换处理器 | 处理/exchange命令 |
| xiuxian_handlers.py | 游戏处理器 | 所有游戏命令处理 |
| init_xiuxian_data.py | 数据初始化 | 初始化怪物、物品等 |

---

## 🎮 功能预览

### 积分兑换系统

```
用户在Telegram发送: /exchange

Bot回复:
┌─────────────────────────┐
│  💱 积分兑换中心        │
├─────────────────────────┤
│ 📊 当前PMS积分: 5000    │
│ 💎 兑换比例: 10积分=1灵石│
│ 📅 今日已兑换: 0/10000  │
├─────────────────────────┤
│ [100积分→10灵石]        │
│ [1000积分→100灵石]      │
│ [📊 兑换历史]           │
└─────────────────────────┘
```

### 修仙游戏系统

**角色创建**:
- 随机资质（悟性8-15，根骨8-15）
- 初始1000灵石
- 从凡人境界开始

**修炼系统**:
- 选择2/4/8/12小时修炼
- 离线挂机，自动获得修为
- 顿悟/走火入魔随机事件

**战斗系统**:
- 挑战野外怪物
- 击败Boss获得丰厚奖励
- 战斗冷却机制

**境界系统**:
- 15个大境界（凡人→大罗金仙）
- 每个境界9层
- 突破需要修为和成功率

---

## 📊 数据统计

**初始游戏内容**:
- 🐺 13种怪物（3个Boss）
- 🎒 21种物品（武器/护甲/丹药）
- 📖 6种功法
- ⚔️ 5种技能
- 📋 6个任务
- 🏆 7个成就

**数据库**:
- 17个新表
- 统一存储在PMSManageBot的data.db中
- 通过telegram_id关联PMS用户

---

## ⚙️ 配置参数

### 兑换系统

```python
EXCHANGE_RATE = 0.1      # 兑换比例（10积分=1灵石）
DAILY_LIMIT = 10000      # 每日兑换上限
MIN_EXCHANGE = 100       # 最小兑换数量
```

### 游戏平衡

```python
# 修炼
BASE_CULTIVATION_RATE = 100  # 基础修炼速度（每小时修为）

# 突破
BREAKTHROUGH_BASE_CHANCE = 0.70  # 基础突破成功率70%

# 战斗
BATTLE_COOLDOWN_MINUTES = 5  # 战斗冷却5分钟
```

---

## 🛠️ 集成方式

### 方式A: 自动集成（推荐）

```bash
./integrate.sh
```

自动完成：
1. ✅ 备份数据库
2. ✅ 执行数据库迁移
3. ✅ 复制文件到PMSManageBot
4. ✅ 更新main.py注册handlers
5. ✅ 初始化游戏数据

### 方式B: 手动集成

查看 `QUICK_INTEGRATION_GUIDE.md` 了解详细步骤。

---

## ✅ 验证检查

集成完成后，验证以下功能：

**数据库**:
```bash
sqlite3 /path/to/data.db "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'xiuxian%';"
# 应该返回17个表
```

**Telegram命令**:
- `/灵根测试` - 创建角色
- `/状态` - 显示状态
- `/兑换灵石` - 兑换功能
- `/闭关` - 修炼功能
- `/历练` - 战斗功能

**数据流**:
- 积分扣除 → 灵石到账 → 记录保存

---

## 🐛 问题排查

### 常见问题

**Q: 运行integrate.sh失败**
A: 检查路径是否正确，确保有执行权限：`chmod +x integrate.sh`

**Q: 积分兑换失败**
A: 检查用户积分是否足够，是否超过每日限额

**Q: 修仙命令无响应**
A: 检查main.py是否正确注册了handlers，查看日志排查错误

**Q: 数据库表不存在**
A: 重新运行迁移脚本：`sqlite3 data.db < migrate_xiuxian_tables.sql`

---

## 📚 完整文档

- **INTEGRATION_COMPLETE.md** - 集成完成后的完整使用指南
- **QUICK_INTEGRATION_GUIDE.md** - 5步快速集成教程
- **INTEGRATION_GUIDE.md** - 详细的技术文档和架构说明

---

## 🎯 下一步

1. **运行集成脚本**
   ```bash
   ./integrate.sh
   ```

2. **重启Bot**
   ```bash
   cd /Users/zc/EC-AI/PMSManageBot/src
   python -m app.main
   ```

3. **测试功能**
   - 在Telegram中发送 `/start`
   - 使用 `/exchange` 兑换灵石
   - 开始修仙之旅！

4. **查看完整文档**
   - 阅读 `INTEGRATION_COMPLETE.md` 了解所有功能
   - 根据需要调整配置参数
   - 添加更多游戏内容

---

## 💡 技术栈

- **Python 3.11+**
- **python-telegram-bot 21+**
- **SQLite3**
- **JSON数据存储**

---

## 📞 支持

如遇到问题：
1. 查看日志文件
2. 检查数据库完整性
3. 查看对应文档的"故障排除"部分

---

## 🎉 开始使用

```bash
# 一键集成
./integrate.sh

# 重启Bot
cd /Users/zc/EC-AI/PMSManageBot/src && python -m app.main

# 在Telegram测试
/start
```

**祝您修仙愉快！** ✨

---

**集成包版本**: 1.0
**创建日期**: 2025-11-23
**兼容**: PMSManageBot (python-telegram-bot 21+)
