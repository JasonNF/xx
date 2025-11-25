# ⚡ 5分钟快速启动指南

> 最快速的部署方式，适合快速测试

---

## 1️⃣ 前置要求

```bash
# 检查 Python 版本 (需要 3.11+)
python3 --version

# 检查 pip
pip3 --version
```

---

## 2️⃣ 获取 Bot Token

1. 打开 Telegram，找到 [@BotFather](https://t.me/BotFather)
2. 发送 `/newbot`
3. 按提示设置名称和用户名
4. **复制** Bot Token（格式：`123456:ABC-DEF...`）
5. 获取你的用户ID：找到 [@userinfobot](https://t.me/userinfobot)，发送 `/start`

---

## 3️⃣ 快速部署

### 方法A: 一键脚本（推荐）

```bash
# 1. 进入项目目录
cd /path/to/xiuxian-game

# 2. 配置 Token
cp .env.example .env
nano .env  # 修改 BOT_TOKEN 和 ADMIN_IDS

# 3. 安装依赖
pip3 install -r requirements.txt

# 4. 导入游戏数据
cd data
./import_all_data.sh  # 按提示输入 yes
cd ..

# 5. 启动 Bot
./start.sh
```

### 方法B: 手动步骤

```bash
# 1. 配置环境
cp .env.example .env
nano .env  # 填入你的 BOT_TOKEN

# 2. 安装依赖
pip3 install -r requirements.txt

# 3. 导入数据
cd data
sqlite3 xiuxian.db < init_skills_new.sql
sqlite3 xiuxian.db < init_monsters_fixed.sql
sqlite3 xiuxian.db < init_items_equipment.sql
cd ..

# 4. 启动
python3 -m src.bot.main
```

---

## 4️⃣ 验证部署

在 Telegram 中测试：

```
/start          ← 注册账号
/info           ← 查看信息
/修炼           ← 开始修炼
/战斗 野狼      ← 测试战斗
/技能列表       ← 查看技能
```

✅ 如果都能正常响应，部署成功！

---

## 🔧 常见问题

### Bot 无响应？

```bash
# 1. 检查 Token
grep BOT_TOKEN .env

# 2. 测试 Token 是否有效
curl "https://api.telegram.org/bot你的TOKEN/getMe"

# 3. 查看日志
tail -f data/logs/xiuxian.log
```

### 数据不完整？

```bash
# 验证数据
sqlite3 data/xiuxian.db "SELECT COUNT(*) FROM skills; SELECT COUNT(*) FROM monsters; SELECT COUNT(*) FROM items;"

# 应该显示: 70, 92, 230
# 如果不对，重新导入
cd data && ./import_all_data.sh
```

### 启动报错？

```bash
# 重新安装依赖
pip3 install -r requirements.txt --upgrade

# 检查 Python 版本
python3 --version  # 需要 >= 3.11
```

---

## 📚 更多信息

- **完整部署指南**: `DEPLOYMENT_GUIDE_COMPLETE.md`
- **命令列表**: `COMMANDS.md`
- **功能说明**: `FEATURE_COMPLETENESS_REPORT.md`
- **数据报告**: `data/DATA_IMPORT_REPORT.md`

---

## 🚀 生产环境部署

### 使用 systemd（后台运行）

```bash
# 创建服务
sudo nano /etc/systemd/system/xiuxian-bot.service

# 粘贴配置（修改路径和用户）
[Unit]
Description=修仙世界 Telegram Bot
After=network.target

[Service]
Type=simple
User=你的用户名
WorkingDirectory=/path/to/xiuxian-game
ExecStart=/usr/bin/python3 -m src.bot.main
Restart=always

[Install]
WantedBy=multi-user.target

# 启动服务
sudo systemctl daemon-reload
sudo systemctl start xiuxian-bot
sudo systemctl enable xiuxian-bot

# 查看状态
sudo systemctl status xiuxian-bot
```

### 使用 screen（简单方式）

```bash
# 创建 screen 会话
screen -S xiuxian

# 启动 Bot
./start.sh

# 按 Ctrl+A 然后按 D 脱离
# Bot 会在后台继续运行

# 重新连接
screen -r xiuxian
```

---

## ⚙️ 配置说明

### .env 关键配置

```env
# ⚠️ 必须修改
BOT_TOKEN=你的真实Token
ADMIN_IDS=[你的用户ID]

# 可选调整
BASE_CULTIVATION_RATE=100      # 修炼速度
BREAKTHROUGH_BASE_CHANCE=0.7   # 突破成功率
DAILY_SIGN_REWARD=1000         # 签到奖励
NEWBIE_GIFT=5000               # 新手礼包
```

---

## 📊 数据统计

当前游戏数据：
- ✅ **70** 个技能（10种元素）
- ✅ **92** 个怪物（5个境界）
- ✅ **230** 个物品装备
- ✅ **392** 项数据（超额完成22.5%）

---

## 🎮 核心命令速查

| 命令 | 说明 | 示例 |
|------|------|------|
| `/start` | 注册账号 | `/start` |
| `/info` | 查看信息 | `/info` |
| `/修炼` | 开始修炼 | `/修炼` |
| `/战斗` | 挑战怪物 | `/战斗 野狼` |
| `/技能列表` | 查看技能 | `/技能列表` |
| `/学习技能` | 学习技能 | `/学习技能 火球术` |
| `/背包` | 查看物品 | `/背包` |
| `/排行榜` | 查看排名 | `/排行榜` |
| `/宗门` | 宗门系统 | `/宗门` |
| `/签到` | 每日签到 | `/签到` |

完整命令列表请查看 `COMMANDS.md`

---

**部署完成！祝你的修仙世界 Bot 运行顺利！** ✨

有问题？查看 `DEPLOYMENT_GUIDE_COMPLETE.md` 获取详细帮助。
