# 🚀 生产环境部署指南

**版本**: v2.0.0
**更新日期**: 2025-11-25
**适用环境**: Debian/Ubuntu Linux VPS
**技术栈**: PostgreSQL + Redis + systemd

---

## 📋 目录

1. [快速部署](#快速部署)
2. [手动部署](#手动部署)
3. [配置说明](#配置说明)
4. [服务管理](#服务管理)
5. [监控与维护](#监控与维护)
6. [故障排查](#故障排查)
7. [升级指南](#升级指南)
8. [备份恢复](#备份恢复)

---

## ⚡ 快速部署

### 一键自动部署 (推荐)

```bash
# 1. 克隆项目到服务器
git clone https://github.com/JasonNF/xx.git
cd xx

# 2. 运行部署脚本 (需要root权限)
sudo bash deploy.sh
```

**部署脚本会自动完成**:
- ✅ 安装系统依赖 (Python, PostgreSQL, Redis)
- ✅ 创建服务用户和数据库
- ✅ 部署应用程序
- ✅ 配置环境变量
- ✅ 设置systemd自动启动
- ✅ 启动服务

**执行时间**: 约5-10分钟

---

## 🛠️ 手动部署

如果需要更精细的控制,可以选择手动部署:

### 步骤1: 安装系统依赖

```bash
# 更新软件源
sudo apt-get update

# 安装必需软件
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    postgresql \
    postgresql-contrib \
    redis-server \
    git \
    build-essential \
    libpq-dev
```

### 步骤2: 配置PostgreSQL

```bash
# 切换到postgres用户
sudo -u postgres psql

# 在PostgreSQL中执行:
CREATE USER xiuxian WITH PASSWORD 'your_secure_password';
CREATE DATABASE xiuxian_prod OWNER xiuxian;
GRANT ALL PRIVILEGES ON DATABASE xiuxian_prod TO xiuxian;
\q
```

### 步骤3: 配置Redis

```bash
# 启动Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

# 验证Redis运行
redis-cli ping
# 应该返回: PONG
```

### 步骤4: 创建服务用户

```bash
# 创建专用用户
sudo useradd -r -m -s /bin/bash xiuxian

# 创建安装目录
sudo mkdir -p /opt/xiuxian-bot
```

### 步骤5: 部署应用

```bash
# 复制项目文件
sudo cp -r /path/to/xx/* /opt/xiuxian-bot/

# 设置所有权
sudo chown -R xiuxian:xiuxian /opt/xiuxian-bot

# 切换到项目目录
cd /opt/xiuxian-bot
```

### 步骤6: 配置Python环境

```bash
# 切换到服务用户
sudo su - xiuxian

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install --upgrade pip
pip install -r requirements.txt
pip install psycopg2-binary  # PostgreSQL驱动

# 退出服务用户
exit
```

### 步骤7: 配置环境变量

```bash
# 复制生产环境配置模板
sudo cp /opt/xiuxian-bot/.env.production /opt/xiuxian-bot/.env

# 编辑配置
sudo nano /opt/xiuxian-bot/.env
```

**必须修改的配置项**:
```env
# Telegram Bot Token (从 @BotFather 获取)
BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11

# 数据库连接
DATABASE_URL=postgresql+asyncpg://xiuxian:your_password@localhost/xiuxian_prod

# 管理员ID (从 @userinfobot 获取)
ADMIN_IDS=123456789,987654321
```

### 步骤8: 初始化数据库

```bash
# 设置数据库环境变量
export DB_NAME=xiuxian_prod
export DB_USER=xiuxian
export DB_PASSWORD=your_password

# 运行数据库初始化
cd /opt/xiuxian-bot
sudo -u xiuxian bash scripts/init_postgres_data.sh
```

### 步骤9: 配置systemd服务

```bash
# 创建systemd服务文件
sudo nano /etc/systemd/system/xiuxian-bot.service
```

**服务配置内容**:
```ini
[Unit]
Description=修仙世界 Telegram Bot
After=network.target postgresql.service redis-server.service
Wants=postgresql.service redis-server.service

[Service]
Type=simple
User=xiuxian
Group=xiuxian
WorkingDirectory=/opt/xiuxian-bot
Environment="PATH=/opt/xiuxian-bot/venv/bin"
ExecStart=/opt/xiuxian-bot/venv/bin/python -m src.bot.main
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# 安全设置
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/xiuxian-bot/data

[Install]
WantedBy=multi-user.target
```

### 步骤10: 启动服务

```bash
# 重载systemd配置
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start xiuxian-bot

# 设置开机自启
sudo systemctl enable xiuxian-bot

# 检查服务状态
sudo systemctl status xiuxian-bot
```

---

## ⚙️ 配置说明

### 环境变量详解

#### Telegram配置
```env
BOT_TOKEN=           # Bot Token (必填)
BOT_USERNAME=        # Bot用户名 (可选)
```

#### 数据库配置
```env
# PostgreSQL (推荐生产环境)
DATABASE_URL=postgresql+asyncpg://user:pass@host/db

# MySQL
DATABASE_URL=mysql+aiomysql://user:pass@host/db

# SQLite (仅开发测试)
DATABASE_URL=sqlite+aiosqlite:///./data/xiuxian.db
```

#### Redis配置
```env
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=      # 如果有密码
```

#### 游戏平衡性配置
```env
BASE_CULTIVATION_RATE=100       # 修炼速度
BREAKTHROUGH_BASE_CHANCE=0.7    # 突破成功率
PVE_COOLDOWN=300                # PVE冷却(秒)
PVP_COOLDOWN=600                # PVP冷却(秒)
DAILY_SIGN_REWARD=1000          # 签到奖励
NEWBIE_GIFT=5000                # 新手礼包
```

#### 日志配置
```env
LOG_LEVEL=INFO                  # DEBUG/INFO/WARNING/ERROR
LOG_FILE=./data/logs/xiuxian.log
```

---

## 🎮 服务管理

### 常用命令

```bash
# 查看服务状态
sudo systemctl status xiuxian-bot

# 启动服务
sudo systemctl start xiuxian-bot

# 停止服务
sudo systemctl stop xiuxian-bot

# 重启服务
sudo systemctl restart xiuxian-bot

# 查看实时日志
sudo journalctl -u xiuxian-bot -f

# 查看最近100行日志
sudo journalctl -u xiuxian-bot -n 100

# 查看今天的日志
sudo journalctl -u xiuxian-bot --since today
```

### 日志管理

```bash
# 应用日志位置
tail -f /opt/xiuxian-bot/data/logs/xiuxian.log

# 清理旧日志
sudo journalctl --vacuum-time=7d  # 保留7天
sudo journalctl --vacuum-size=500M  # 保留500MB
```

---

## 📊 监控与维护

### 性能监控

```bash
# 检查CPU和内存使用
ps aux | grep python

# 检查数据库连接
sudo -u postgres psql -c "SELECT count(*) FROM pg_stat_activity WHERE datname='xiuxian_prod';"

# 检查Redis内存
redis-cli info memory

# 检查磁盘使用
df -h /opt/xiuxian-bot/data
```

### 健康检查脚本

创建健康检查脚本 `/opt/xiuxian-bot/health_check.sh`:

```bash
#!/bin/bash

echo "=== Bot健康检查 ==="
echo ""

# 检查服务状态
echo -n "服务状态: "
if systemctl is-active --quiet xiuxian-bot; then
    echo "✓ 运行中"
else
    echo "✗ 已停止"
    exit 1
fi

# 检查数据库连接
echo -n "数据库连接: "
if sudo -u postgres psql -d xiuxian_prod -c "SELECT 1" > /dev/null 2>&1; then
    echo "✓ 正常"
else
    echo "✗ 失败"
fi

# 检查Redis
echo -n "Redis连接: "
if redis-cli ping > /dev/null 2>&1; then
    echo "✓ 正常"
else
    echo "✗ 失败"
fi

# 检查磁盘空间
echo -n "磁盘空间: "
DISK_USAGE=$(df -h /opt/xiuxian-bot | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -lt 80 ]; then
    echo "✓ ${DISK_USAGE}%"
else
    echo "⚠ ${DISK_USAGE}% (告警)"
fi

echo ""
echo "=== 检查完成 ==="
```

### 定时任务

添加到crontab,每小时检查一次:
```bash
# 编辑crontab
sudo crontab -e

# 添加:
0 * * * * /opt/xiuxian-bot/health_check.sh >> /var/log/xiuxian-health.log 2>&1
```

---

## 🔧 故障排查

### Bot无响应

1. **检查服务状态**
   ```bash
   sudo systemctl status xiuxian-bot
   ```

2. **查看错误日志**
   ```bash
   sudo journalctl -u xiuxian-bot -n 50
   ```

3. **验证Bot Token**
   ```bash
   curl "https://api.telegram.org/bot你的TOKEN/getMe"
   ```

### 数据库连接失败

1. **检查PostgreSQL服务**
   ```bash
   sudo systemctl status postgresql
   ```

2. **测试数据库连接**
   ```bash
   psql -h localhost -U xiuxian -d xiuxian_prod
   ```

3. **检查连接配置**
   ```bash
   grep DATABASE_URL /opt/xiuxian-bot/.env
   ```

### Redis连接问题

```bash
# 检查Redis服务
sudo systemctl status redis-server

# 测试连接
redis-cli ping

# 查看Redis日志
sudo tail -f /var/log/redis/redis-server.log
```

### 内存不足

```bash
# 检查内存使用
free -h

# 添加swap (如果需要)
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

---

## 🔄 升级指南

### 平滑升级步骤

```bash
# 1. 备份数据库
sudo -u postgres pg_dump xiuxian_prod > /backup/xiuxian_$(date +%Y%m%d).sql

# 2. 停止服务
sudo systemctl stop xiuxian-bot

# 3. 备份代码
sudo cp -r /opt/xiuxian-bot /opt/xiuxian-bot.backup

# 4. 拉取最新代码
cd /opt/xiuxian-bot
sudo -u xiuxian git pull origin main

# 5. 更新依赖
sudo -u xiuxian /opt/xiuxian-bot/venv/bin/pip install -r requirements.txt --upgrade

# 6. 运行数据库迁移(如果有)
sudo -u xiuxian /opt/xiuxian-bot/venv/bin/python scripts/migrate_db.py

# 7. 重启服务
sudo systemctl start xiuxian-bot

# 8. 验证运行
sudo systemctl status xiuxian-bot
sudo journalctl -u xiuxian-bot -f
```

---

## 💾 备份恢复

### 自动备份脚本

创建 `/opt/xiuxian-bot/backup.sh`:

```bash
#!/bin/bash

BACKUP_DIR="/backup/xiuxian"
DATE=$(date +%Y%m%d_%H%M%S)

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份数据库
sudo -u postgres pg_dump xiuxian_prod | gzip > "$BACKUP_DIR/db_$DATE.sql.gz"

# 备份数据文件
tar -czf "$BACKUP_DIR/data_$DATE.tar.gz" /opt/xiuxian-bot/data

# 备份配置
cp /opt/xiuxian-bot/.env "$BACKUP_DIR/env_$DATE"

# 保留最近7天的备份
find $BACKUP_DIR -type f -mtime +7 -delete

echo "备份完成: $DATE"
```

### 定时备份

```bash
# 添加到crontab,每天凌晨2点备份
sudo crontab -e

# 添加:
0 2 * * * /opt/xiuxian-bot/backup.sh
```

### 恢复数据

```bash
# 1. 停止服务
sudo systemctl stop xiuxian-bot

# 2. 恢复数据库
gunzip < /backup/xiuxian/db_20251125.sql.gz | sudo -u postgres psql xiuxian_prod

# 3. 恢复数据文件
sudo tar -xzf /backup/xiuxian/data_20251125.tar.gz -C /

# 4. 恢复配置
sudo cp /backup/xiuxian/env_20251125 /opt/xiuxian-bot/.env

# 5. 启动服务
sudo systemctl start xiuxian-bot
```

---

## 🔒 安全建议

### 1. 防火墙配置

```bash
# 只开放必要端口
sudo ufw allow 22/tcp    # SSH
sudo ufw enable
```

### 2. 定期更新

```bash
# 更新系统
sudo apt-get update
sudo apt-get upgrade

# 更新Python包
sudo -u xiuxian /opt/xiuxian-bot/venv/bin/pip list --outdated
```

### 3. 权限控制

```bash
# 确保敏感文件权限正确
sudo chmod 600 /opt/xiuxian-bot/.env
sudo chown xiuxian:xiuxian /opt/xiuxian-bot/.env
```

### 4. 日志审计

```bash
# 定期检查异常登录
sudo journalctl -u xiuxian-bot | grep -i error
```

---

## 📞 支持

遇到问题?
- 查看日志: `sudo journalctl -u xiuxian-bot -f`
- GitHub Issues: https://github.com/JasonNF/xx/issues
- 查看完整文档: `DEPLOYMENT_GUIDE_COMPLETE.md`

---

**祝你的修仙世界Bot运行顺利!** ✨
