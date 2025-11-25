# 🚀 修仙世界 Telegram Bot - 完整部署指南

**版本**: v1.0.0
**更新日期**: 2025-11-25
**部署难度**: ⭐⭐ (中等)
**预计时间**: 15-30分钟

---

## 📋 目录

1. [前置要求](#前置要求)
2. [快速部署（开发环境）](#快速部署开发环境)
3. [生产环境部署](#生产环境部署)
4. [Docker 部署](#docker-部署)
5. [常见问题排查](#常见问题排查)
6. [维护与监控](#维护与监控)

---

## 前置要求

### 系统要求
- **操作系统**: Linux (推荐 Ubuntu 20.04+) / macOS / Windows (WSL2)
- **Python**: 3.11+
- **内存**: 最低 512MB (推荐 1GB+)
- **磁盘**: 最低 500MB (数据库会增长)

### 必需软件
```bash
# Python 3.11+
python3 --version

# pip (Python包管理器)
pip3 --version

# Git (用于克隆项目)
git --version

# SQLite3 (数据库)
sqlite3 --version
```

### Telegram Bot Token
1. 在 Telegram 中找到 [@BotFather](https://t.me/BotFather)
2. 发送 `/newbot` 创建新Bot
3. 按提示设置Bot名称和用户名
4. 获取 Bot Token (格式: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)
5. 记下你的 Telegram 用户ID (发送 `/start` 给 [@userinfobot](https://t.me/userinfobot))

---

## 快速部署（开发环境）

### 1️⃣ 克隆项目 (如果还没有)

```bash
cd ~
git clone <项目地址> xiuxian-game
cd xiuxian-game
```

**或者如果已经有项目文件：**
```bash
cd /path/to/xiuxian-game
```

### 2️⃣ 创建虚拟环境（推荐）

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
# Linux/macOS:
source venv/bin/activate

# Windows (PowerShell):
.\venv\Scripts\Activate.ps1

# Windows (CMD):
.\venv\Scripts\activate.bat
```

### 3️⃣ 安装依赖

```bash
pip install -r requirements.txt
```

**预期输出**:
```
Successfully installed python-telegram-bot-21.x sqlalchemy-2.x aiosqlite-x.x ...
```

### 4️⃣ 配置环境变量 ⭐ 关键步骤

```bash
# 复制示例配置
cp .env.example .env

# 编辑配置文件
nano .env
# 或使用其他编辑器: vim .env / code .env
```

**必须修改的配置**:
```env
# ⚠️ 必须填写真实的 Token
BOT_TOKEN=你的真实Bot_Token

# 可选：修改Bot用户名
BOT_USERNAME=xiuxian_bot

# ⚠️ 推荐：添加管理员ID (你的Telegram用户ID)
ADMIN_IDS=[123456789, 987654321]  # JSON数组格式，多个用逗号分隔
```

**其他配置说明**:
```env
# 数据库配置 (默认SQLite，无需修改)
DATABASE_URL=sqlite+aiosqlite:///./data/xiuxian.db

# 游戏参数 (可根据需要调整)
BASE_CULTIVATION_RATE=100        # 修炼速度
BREAKTHROUGH_BASE_CHANCE=0.7     # 突破基础成功率
DAILY_SIGN_REWARD=1000           # 每日签到奖励
NEWBIE_GIFT=5000                 # 新手礼包

# 日志级别 (开发用DEBUG，生产用INFO)
LOG_LEVEL=INFO
```

### 5️⃣ 初始化数据库 ⭐⭐⭐ 最关键

**检查数据文件是否存在**:
```bash
ls -lh data/*.sql
```

预期看到：
- `init_skills_new.sql` (70个技能)
- `init_monsters_fixed.sql` (92个怪物)
- `init_items_equipment.sql` (230个物品)

**导入数据**:
```bash
# 进入data目录
cd data

# 方法1: 一键导入所有数据（推荐）
sqlite3 xiuxian.db << 'EOSQL'
-- 清空现有数据
DELETE FROM skills;
DELETE FROM monsters;
DELETE FROM items;
DELETE FROM sqlite_sequence WHERE name IN ('skills', 'monsters', 'items');

-- 导入新数据
.read init_skills_new.sql
.read init_monsters_fixed.sql
.read init_items_equipment.sql

-- 显示统计
SELECT '技能总数: ' || COUNT(*) FROM skills;
SELECT '怪物总数: ' || COUNT(*) FROM monsters;
SELECT '物品总数: ' || COUNT(*) FROM items;
EOSQL

# 方法2: 分步导入
sqlite3 xiuxian.db "DELETE FROM skills; DELETE FROM sqlite_sequence WHERE name='skills';"
sqlite3 xiuxian.db < init_skills_new.sql

sqlite3 xiuxian.db "DELETE FROM monsters; DELETE FROM sqlite_sequence WHERE name='monsters';"
sqlite3 xiuxian.db < init_monsters_fixed.sql

sqlite3 xiuxian.db "DELETE FROM items; DELETE FROM sqlite_sequence WHERE name='items';"
sqlite3 xiuxian.db < init_items_equipment.sql

# 验证导入结果
sqlite3 xiuxian.db "SELECT COUNT(*) as 技能 FROM skills; SELECT COUNT(*) as 怪物 FROM monsters; SELECT COUNT(*) as 物品 FROM items;"

# 返回项目根目录
cd ..
```

**预期输出**:
```
技能总数: 70
怪物总数: 92
物品总数: 230
```

### 6️⃣ 启动Bot

```bash
# 确保在项目根目录
cd /path/to/xiuxian-game

# 启动Bot
python3 -m src.bot.main

# 或使用提供的启动脚本
# chmod +x run.sh
# ./run.sh
```

**成功启动的标志**:
```
2025-11-25 22:00:00 - INFO - 正在启动 修仙世界 v1.0.0...
2025-11-25 22:00:01 - INFO - 注册命令处理器...
2025-11-25 22:00:01 - INFO - 初始化数据库...
2025-11-25 22:00:01 - INFO - 数据库初始化完成
2025-11-25 22:00:01 - INFO - 调度器已启动
2025-11-25 22:00:01 - INFO - Bot 启动成功！
2025-11-25 22:00:02 - INFO - 启动 Bot...
2025-11-25 22:00:03 - INFO - Start polling...
```

### 7️⃣ 测试Bot

在 Telegram 中找到你的Bot并测试：

```
1. /start          # 注册账号
2. /info           # 查看个人信息
3. /灵根           # 测试灵根（随机分配）
4. /修炼           # 开始修炼
5. /战斗 野狼      # 测试战斗系统
6. /技能列表       # 查看可学习技能
7. /背包           # 查看物品
```

如果都能正常响应，说明部署成功！🎉

---

## 生产环境部署

### 使用 systemd（推荐 - Linux系统）

#### 1. 创建系统服务文件

```bash
sudo nano /etc/systemd/system/xiuxian-bot.service
```

**粘贴以下内容** (修改路径和用户名):
```ini
[Unit]
Description=修仙世界 Telegram Bot
After=network.target

[Service]
Type=simple
User=你的用户名
WorkingDirectory=/path/to/xiuxian-game
Environment="PATH=/path/to/xiuxian-game/venv/bin"
ExecStart=/path/to/xiuxian-game/venv/bin/python3 -m src.bot.main
Restart=always
RestartSec=10

# 日志
StandardOutput=append:/path/to/xiuxian-game/data/logs/bot.log
StandardError=append:/path/to/xiuxian-game/data/logs/bot_error.log

[Install]
WantedBy=multi-user.target
```

**修改示例**:
```ini
User=ubuntu
WorkingDirectory=/home/ubuntu/xiuxian-game
Environment="PATH=/home/ubuntu/xiuxian-game/venv/bin"
ExecStart=/home/ubuntu/xiuxian-game/venv/bin/python3 -m src.bot.main
StandardOutput=append:/home/ubuntu/xiuxian-game/data/logs/bot.log
StandardError=append:/home/ubuntu/xiuxian-game/data/logs/bot_error.log
```

#### 2. 启动和管理服务

```bash
# 重新加载systemd配置
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start xiuxian-bot

# 查看状态
sudo systemctl status xiuxian-bot

# 设置开机自启
sudo systemctl enable xiuxian-bot

# 查看日志
sudo journalctl -u xiuxian-bot -f

# 重启服务
sudo systemctl restart xiuxian-bot

# 停止服务
sudo systemctl stop xiuxian-bot
```

### 使用 Screen（简单方式 - 所有系统）

```bash
# 安装screen（如果没有）
# Ubuntu/Debian:
sudo apt-get install screen
# CentOS/RHEL:
sudo yum install screen
# macOS:
brew install screen

# 创建新screen会话
screen -S xiuxian

# 在screen中启动Bot
cd /path/to/xiuxian-game
source venv/bin/activate  # 如果使用虚拟环境
python3 -m src.bot.main

# 按 Ctrl+A 然后按 D 脱离screen
# Bot会在后台继续运行

# 重新连接screen
screen -r xiuxian

# 查看所有screen会话
screen -ls

# 结束screen会话
screen -X -S xiuxian quit
```

### 使用 PM2（Node.js生态，但支持Python）

```bash
# 安装PM2
npm install -g pm2

# 创建PM2配置文件
cat > ecosystem.config.js << 'EOF'
module.exports = {
  apps: [{
    name: 'xiuxian-bot',
    script: 'python3',
    args: '-m src.bot.main',
    cwd: '/path/to/xiuxian-game',
    interpreter: 'none',
    autorestart: true,
    watch: false,
    max_memory_restart: '500M',
    env: {
      NODE_ENV: 'production'
    }
  }]
};
EOF

# 启动Bot
pm2 start ecosystem.config.js

# 查看状态
pm2 status

# 查看日志
pm2 logs xiuxian-bot

# 重启
pm2 restart xiuxian-bot

# 停止
pm2 stop xiuxian-bot

# 设置开机自启
pm2 startup
pm2 save
```

---

## Docker 部署

### 1. 创建 Dockerfile

```dockerfile
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 创建数据目录
RUN mkdir -p /app/data/logs

# 暴露端口（如果需要API）
# EXPOSE 8000

# 启动命令
CMD ["python3", "-m", "src.bot.main"]
```

### 2. 创建 docker-compose.yml

```yaml
version: '3.8'

services:
  xiuxian-bot:
    build: .
    container_name: xiuxian-bot
    restart: unless-stopped
    volumes:
      - ./data:/app/data
      - ./.env:/app/.env
    environment:
      - TZ=Asia/Shanghai
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### 3. 构建和运行

```bash
# 构建镜像
docker-compose build

# 启动容器
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止容器
docker-compose down

# 重启容器
docker-compose restart

# 查看状态
docker-compose ps
```

---

## 常见问题排查

### ❌ 问题1: `BOT_TOKEN is required`

**原因**: .env 文件未配置或 BOT_TOKEN 为空

**解决**:
```bash
# 检查.env文件是否存在
ls -la .env

# 查看配置
cat .env | grep BOT_TOKEN

# 确保TOKEN格式正确
BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
```

### ❌ 问题2: `no such column: players.credits`

**原因**: 未执行数据库迁移

**解决**:
```bash
cd data/migrations

# 执行所有迁移脚本
for f in *.sql; do
    echo "执行迁移: $f"
    sqlite3 ../xiuxian.db < "$f"
done

# 验证
sqlite3 ../xiuxian.db "PRAGMA table_info(players);" | grep credits
```

### ❌ 问题3: Bot无响应

**原因**: Token错误或网络问题

**解决**:
```bash
# 1. 测试Token是否有效
curl "https://api.telegram.org/bot你的TOKEN/getMe"

# 正确响应示例:
# {"ok":true,"result":{"id":123456,"is_bot":true,"first_name":"修仙世界",...}}

# 2. 检查网络连接
ping api.telegram.org

# 3. 查看Bot日志
tail -f data/logs/xiuxian.log
```

### ❌ 问题4: 导入错误 `ModuleNotFoundError`

**原因**: 依赖包未安装或虚拟环境未激活

**解决**:
```bash
# 确认Python版本
python3 --version  # 应该 >= 3.11

# 重新安装依赖
pip install -r requirements.txt

# 如果使用虚拟环境，确保已激活
source venv/bin/activate
which python3  # 应该指向venv目录
```

### ❌ 问题5: 数据库锁定 `database is locked`

**原因**: 多个进程同时访问数据库

**解决**:
```bash
# 1. 查找占用数据库的进程
lsof data/xiuxian.db

# 2. 关闭所有Bot进程
pkill -f "python3 -m src.bot.main"

# 3. 确认没有残留进程
ps aux | grep "src.bot.main"

# 4. 重新启动
python3 -m src.bot.main
```

### ❌ 问题6: 权限错误 `Permission denied`

**原因**: 文件权限不正确

**解决**:
```bash
# 修改项目目录权限
chmod -R 755 /path/to/xiuxian-game

# 确保数据目录可写
chmod -R 755 data/
chmod 644 data/xiuxian.db

# 确保日志目录可写
mkdir -p data/logs
chmod 755 data/logs
```

---

## 维护与监控

### 查看日志

```bash
# 实时查看日志
tail -f data/logs/xiuxian.log

# 查看错误日志
tail -f data/logs/bot_error.log

# 搜索特定错误
grep "ERROR" data/logs/xiuxian.log

# 查看最近100行
tail -n 100 data/logs/xiuxian.log
```

### 数据库备份

```bash
# 手动备份
sqlite3 data/xiuxian.db ".backup 'data/backup_$(date +%Y%m%d_%H%M%S).db'"

# 定期备份（添加到crontab）
crontab -e
# 添加以下行（每天凌晨3点备份）
0 3 * * * cd /path/to/xiuxian-game && sqlite3 data/xiuxian.db ".backup 'data/backup_$(date +\%Y\%m\%d).db'"

# 保留最近7天的备份
find data/ -name "backup_*.db" -mtime +7 -delete
```

### 更新Bot

```bash
# 1. 停止Bot
sudo systemctl stop xiuxian-bot
# 或: screen -X -S xiuxian quit

# 2. 备份数据库
sqlite3 data/xiuxian.db ".backup 'data/backup_before_update.db'"

# 3. 拉取最新代码
git pull

# 4. 更新依赖
pip install -r requirements.txt --upgrade

# 5. 执行新的迁移（如果有）
cd data/migrations
for f in *.sql; do sqlite3 ../xiuxian.db < "$f" 2>/dev/null; done
cd ../..

# 6. 重启Bot
sudo systemctl start xiuxian-bot
# 或重新创建screen会话
```

### 性能监控

```bash
# 查看Bot进程资源占用
ps aux | grep "src.bot.main"

# 查看数据库大小
du -h data/xiuxian.db

# 查看日志大小
du -h data/logs/

# 清理旧日志（保留最近7天）
find data/logs/ -name "*.log" -mtime +7 -delete

# 数据库优化
sqlite3 data/xiuxian.db "VACUUM; ANALYZE;"
```

### 玩家数据统计

```bash
sqlite3 data/xiuxian.db << 'EOF'
.mode column
.headers on

-- 总玩家数
SELECT COUNT(*) as 总玩家数 FROM players;

-- 各境界玩家分布
SELECT realm as 境界, COUNT(*) as 人数 FROM players GROUP BY realm ORDER BY id;

-- 活跃玩家（最近7天有活动）
SELECT COUNT(*) as 活跃玩家 FROM players
WHERE updated_at > datetime('now', '-7 days');

-- 在线修炼人数
SELECT COUNT(*) as 修炼中 FROM players
WHERE is_cultivating = 1;
EOF
```

---

## 🎯 部署检查清单

部署前检查：
- [ ] Python 3.11+ 已安装
- [ ] 已获取有效的 Telegram Bot Token
- [ ] 已克隆/下载项目代码
- [ ] 已安装所有依赖 (`pip install -r requirements.txt`)
- [ ] 已配置 `.env` 文件（特别是 BOT_TOKEN）
- [ ] 已导入所有游戏数据（技能、怪物、物品）
- [ ] 已执行数据库迁移脚本

部署后验证：
- [ ] Bot能正常启动（无错误日志）
- [ ] `/start` 命令正常响应
- [ ] `/info` 能显示玩家信息
- [ ] `/修炼` 修炼系统正常
- [ ] `/战斗` 战斗系统正常
- [ ] `/技能列表` 显示所有技能
- [ ] `/背包` 物品系统正常

生产环境额外检查：
- [ ] 已设置开机自启（systemd/PM2）
- [ ] 已配置日志轮转
- [ ] 已设置数据库定期备份
- [ ] 已添加管理员ID（ADMIN_IDS）
- [ ] 已配置监控告警（可选）

---

## 📞 获取帮助

- **项目文档**: 查看 `docs/` 目录
- **功能文档**: `FEATURE_COMPLETENESS_REPORT.md`
- **命令列表**: `COMMANDS.md`
- **数据报告**: `data/DATA_IMPORT_REPORT.md`

---

## 📝 附录

### A. 完整的启动脚本 (start.sh)

```bash
#!/bin/bash

# 修仙世界 Bot 启动脚本

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo "======================================="
echo "  修仙世界 Telegram Bot 启动脚本"
echo "======================================="

# 检查Python版本
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python 版本: $PYTHON_VERSION"

# 检查.env文件
if [ ! -f ".env" ]; then
    echo "✗ 错误: .env 文件不存在"
    echo "  请复制 .env.example 并配置 BOT_TOKEN"
    exit 1
fi
echo "✓ 配置文件存在"

# 检查数据库
if [ ! -f "data/xiuxian.db" ]; then
    echo "✗ 警告: 数据库文件不存在"
    echo "  将在首次启动时自动创建"
fi

# 激活虚拟环境（如果存在）
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✓ 虚拟环境已激活"
fi

# 创建日志目录
mkdir -p data/logs

echo "======================================="
echo "  正在启动 Bot..."
echo "======================================="

# 启动Bot
python3 -m src.bot.main
```

使用方法：
```bash
chmod +x start.sh
./start.sh
```

### B. 环境变量完整列表

| 变量名 | 必需 | 默认值 | 说明 |
|--------|------|--------|------|
| BOT_TOKEN | ✅ 是 | - | Telegram Bot Token |
| BOT_USERNAME | 否 | xiuxian_bot | Bot用户名 |
| DATABASE_URL | 否 | sqlite+aiosqlite:///./data/xiuxian.db | 数据库连接 |
| REDIS_HOST | 否 | localhost | Redis主机 |
| REDIS_PORT | 否 | 6379 | Redis端口 |
| GAME_NAME | 否 | 修仙世界 | 游戏名称 |
| GAME_VERSION | 否 | 1.0.0 | 游戏版本 |
| BASE_CULTIVATION_RATE | 否 | 100 | 基础修炼速度 |
| BREAKTHROUGH_BASE_CHANCE | 否 | 0.7 | 基础突破成功率 |
| PVE_COOLDOWN | 否 | 300 | PVE冷却时间(秒) |
| PVP_COOLDOWN | 否 | 600 | PVP冷却时间(秒) |
| DAILY_SIGN_REWARD | 否 | 1000 | 每日签到奖励 |
| NEWBIE_GIFT | 否 | 5000 | 新手礼包 |
| LOG_LEVEL | 否 | INFO | 日志级别 |
| LOG_FILE | 否 | ./data/logs/xiuxian.log | 日志文件 |
| ADMIN_IDS | 否 | [] | 管理员ID列表 |

---

**部署完成后，祝你的修仙世界Bot运行顺利！** 🎮✨

如有问题，请查看日志文件或参考本文档的"常见问题排查"部分。
