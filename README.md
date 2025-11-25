# 修仙世界 - Telegram修仙游戏

<div align="center">

📜 一款完整的Telegram文字修仙RPG游戏

[功能特性](#功能特性) • [快速开始](#快速开始) • [游戏系统](#游戏系统) • [开发文档](#开发文档)

</div>

---

## 功能特性

### 核心系统 ✨

- **🧘 修炼系统** - 离线挂机修炼，自动获得修为
- **⚔️ 战斗系统** - PVE挑战怪物，PVP玩家对战
- **🌟 境界系统** - 从凡人到大罗金仙，15个大境界
- **💎 装备系统** - 武器、护甲、饰品，强化提升属性
- **💊 丹药系统** - 炼丹、使用丹药，快速提升实力
- **🏛️ 宗门系统** - 创建/加入宗门，共同发展
- **📋 任务系统** - 主线、每日、周常任务
- **🏪 商店系统** - 购买物品，玩家间交易、拍卖
- **🏆 排行榜** - 境界、战力、财富多维度排名
- **✅ 签到系统** - 每日签到获得奖励

### 技术特点 🚀

- **异步架构** - 基于python-telegram-bot异步框架
- **数据持久化** - SQLAlchemy + SQLite/PostgreSQL/MySQL
- **缓存优化** - Redis缓存支持
- **定时任务** - APScheduler定时任务调度
- **可扩展性** - 模块化设计，易于扩展新功能

---

## 快速开始

### 环境要求

- Python 3.11+
- SQLite/PostgreSQL/MySQL（任选一种）
- Redis（可选，用于缓存）

### 安装步骤

#### 1. 克隆项目

```bash
cd xiuxian-game
```

#### 2. 安装依赖

```bash
pip install -e .
```

或使用uv（推荐）：

```bash
uv pip install -e .
```

#### 3. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入您的配置：

```env
# Telegram Bot Token（必填）
BOT_TOKEN=your_bot_token_here

# 数据库配置
DATABASE_URL=sqlite+aiosqlite:///./data/xiuxian.db

# 其他配置（可选）
REDIS_HOST=localhost
REDIS_PORT=6379
```

#### 4. 获取Bot Token

1. 在Telegram中找到 [@BotFather](https://t.me/BotFather)
2. 发送 `/newbot` 创建新机器人
3. 按提示设置机器人名称和用户名
4. 复制获得的Token到 `.env` 文件

#### 5. 启动游戏

```bash
python -m bot.main
```

或

```bash
cd src
python -m bot.main
```

---

## 游戏系统

### 境界系统 🌟

游戏包含15个大境界，每个境界分9层：

```
凡人 → 炼气期 → 筑基期 → 金丹期 → 元婴期 → 化神期 →
炼虚期 → 合体期 → 大乘期 → 渡劫期 → 真仙 → 金仙 →
太乙金仙 → 大罗金仙
```

### 修炼系统 🧘

- **离线挂机**：设置修炼时长，到期自动获得修为
- **悟性影响**：悟性越高，修炼速度越快
- **功法加成**：学习高级功法，提升修炼效率
- **随机事件**：修炼中可能遇到机缘或走火入魔

### 战斗系统 ⚔️

#### PVE战斗
- 挑战不同境界的怪物
- 获得修为、灵石和装备奖励
- Boss战获得稀有物品

#### PVP战斗
- 挑战其他玩家
- 获得荣誉点数
- 提升排行榜排名

### 装备系统 💎

- **装备类型**：武器、护甲、饰品
- **品质等级**：普通 → 精良 → 稀有 → 史诗 → 传说 → 神话
- **装备强化**：消耗灵石提升装备等级
- **属性加成**：攻击、防御、生命、暴击等

### 宗门系统 🏛️

- **创建宗门**：消耗灵石建立自己的宗门
- **招募成员**：邀请其他玩家加入
- **宗门建筑**：大殿、藏经阁、炼器阁、炼丹房
- **宗门商店**：用贡献度兑换物品
- **宗门战**：与其他宗门争夺资源

---

## 游戏命令

### 基础命令

```
/start - 开始游戏/显示主菜单
/help - 显示帮助信息
/status - 查看角色状态
```

### 修炼命令

```
/cultivate [小时] - 开始修炼
/finish - 完成修炼收取修为
/cancel - 取消当前修炼
/breakthrough - 尝试突破境界
```

### 战斗命令

```
/battle - 挑战怪物(PVE)
/pvp [@用户] - 挑战玩家
/arena - 进入竞技场
```

### 经济命令

```
/sign - 每日签到
/shop - 商店
/bag - 背包
/use [物品ID] - 使用物品
```

### 宗门命令

```
/sect - 宗门信息
/sect create [名称] - 创建宗门
/sect join [ID] - 加入宗门
/sect leave - 离开宗门
```

---

## 项目结构

```
xiuxian-game/
├── src/bot/
│   ├── config/          # 配置文件
│   │   └── settings.py
│   ├── models/          # 数据模型
│   │   ├── database.py
│   │   ├── player.py
│   │   ├── item.py
│   │   ├── sect.py
│   │   ├── battle.py
│   │   ├── quest.py
│   │   └── market.py
│   ├── services/        # 业务逻辑
│   │   ├── player_service.py
│   │   ├── cultivation_service.py
│   │   └── battle_service.py
│   ├── handlers/        # 命令处理器
│   │   ├── start.py
│   │   └── cultivation.py
│   └── main.py          # 主程序入口
├── data/                # 数据目录
│   ├── xiuxian.db       # SQLite数据库
│   └── logs/            # 日志文件
├── tests/               # 测试文件
├── docs/                # 文档
├── pyproject.toml       # 项目配置
├── .env.example         # 环境变量示例
└── README.md            # 项目说明
```

---

## 开发计划

### 已完成 ✅

- [x] 数据库模型设计
- [x] 玩家系统
- [x] 修炼系统
- [x] 境界突破
- [x] 战斗系统（基础）
- [x] 签到系统

### 进行中 🚧

- [ ] 战斗系统完善（Boss战、技能）
- [ ] 装备系统完善（强化、附魔）
- [ ] 宗门系统完善（宗门战、建筑升级）

### 计划中 📋

- [ ] 任务系统
- [ ] 商店和交易系统
- [ ] 拍卖行
- [ ] 排行榜系统
- [ ] 成就系统
- [ ] 好友系统
- [ ] 秘境副本
- [ ] 活动系统

---

## 贡献指南

欢迎提交Issue和Pull Request！

### 开发环境设置

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest

# 代码格式化
black src/
isort src/

# 类型检查
mypy src/
```

---

## 许可证

MIT License

---

## 致谢

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) - Telegram Bot框架
- [SQLAlchemy](https://www.sqlalchemy.org/) - ORM框架
- [APScheduler](https://github.com/agronholm/apscheduler) - 任务调度

---

<div align="center">

**[⬆ 回到顶部](#修仙世界---telegram修仙游戏)**

Made with ❤️ by EC-AI

</div>
