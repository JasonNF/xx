# 🚀 立即部署 - 3分钟上线指南

> **最快的部署方式** - 适合立即部署到生产环境

---

## 📋 前置准备

在开始之前,确保你有:

- ✅ Debian/Ubuntu Linux VPS (已登录root)
- ✅ Telegram Bot Token (从 @BotFather 获取)
- ✅ 你的Telegram用户ID (从 @userinfobot 获取)

---

## ⚡ 一键部署

### 在服务器上执行:

```bash
# 1. 克隆项目
git clone https://github.com/JasonNF/xx.git
cd xx

# 2. 运行部署脚本
sudo bash deploy.sh
```

### 部署过程中会提示输入:

1. **Bot Token** - 你的Telegram Bot Token
2. **Admin IDs** - 管理员ID (多个用逗号分隔)

### 等待5-10分钟,脚本会自动:

- ✅ 安装 Python, PostgreSQL, Redis
- ✅ 创建数据库和用户
- ✅ 部署应用程序
- ✅ 配置systemd服务
- ✅ 启动Bot

---

## ✅ 验证部署

### 1. 检查服务状态

```bash
sudo systemctl status xiuxian-bot
```

应该看到 `Active: active (running)`

### 2. 查看日志

```bash
sudo journalctl -u xiuxian-bot -f
```

应该看到 "Bot 启动成功" 的消息

### 3. 测试Bot

在Telegram中:
- 找到你的Bot
- 发送 `/start`
- 应该收到注册成功的消息

---

## 🎮 常用管理命令

```bash
# 查看状态
sudo systemctl status xiuxian-bot

# 重启服务
sudo systemctl restart xiuxian-bot

# 查看日志
sudo journalctl -u xiuxian-bot -f

# 停止服务
sudo systemctl stop xiuxian-bot
```

---

## 📍 重要路径

- **安装目录**: `/opt/xiuxian-bot`
- **配置文件**: `/opt/xiuxian-bot/.env`
- **日志文件**: `/opt/xiuxian-bot/data/logs/xiuxian.log`
- **数据库**: PostgreSQL `xiuxian_prod`

---

## 🔧 快速配置调整

### 修改游戏参数

```bash
# 编辑配置
sudo nano /opt/xiuxian-bot/.env

# 修改后重启生效
sudo systemctl restart xiuxian-bot
```

### 常用配置项:

```env
BASE_CULTIVATION_RATE=100       # 修炼速度
BREAKTHROUGH_BASE_CHANCE=0.7    # 突破成功率
DAILY_SIGN_REWARD=1000          # 签到奖励
NEWBIE_GIFT=5000                # 新手礼包
```

---

## ❓ 遇到问题?

### Bot无响应

```bash
# 1. 检查服务状态
sudo systemctl status xiuxian-bot

# 2. 查看错误日志
sudo journalctl -u xiuxian-bot -n 50

# 3. 验证Token
curl "https://api.telegram.org/bot你的TOKEN/getMe"
```

### 重新部署

```bash
# 停止服务
sudo systemctl stop xiuxian-bot

# 重新运行部署脚本
cd /path/to/xx
sudo bash deploy.sh
```

---

## 📚 详细文档

需要更多信息?查看:

- **完整部署指南**: `PRODUCTION_DEPLOYMENT.md`
- **功能说明**: `README.md`
- **命令列表**: `COMMANDS.md`
- **快速开始**: `QUICK_START.md`

---

## 🔒 安全提示

1. **保护.env文件** - 包含敏感信息,不要泄露
2. **定期备份** - 使用提供的备份脚本
3. **更新系统** - 定期运行 `sudo apt-get update && sudo apt-get upgrade`
4. **监控日志** - 定期检查异常

---

## 💾 备份数据

```bash
# 快速备份
sudo -u postgres pg_dump xiuxian_prod > backup_$(date +%Y%m%d).sql

# 备份数据文件
sudo tar -czf data_backup_$(date +%Y%m%d).tar.gz /opt/xiuxian-bot/data
```

---

## 🎉 部署成功!

你的修仙世界Bot已经上线了!

**下一步**:
1. 在Telegram中测试所有功能
2. 调整游戏参数 (可选)
3. 设置定时备份
4. 邀请玩家开始游戏!

---

**祝你的修仙世界繁荣昌盛!** ⚔️✨

有问题?查看 `PRODUCTION_DEPLOYMENT.md` 获取详细帮助
