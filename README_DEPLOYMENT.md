# 修仙世界 Telegram Bot 部署文档

## 快速修复 - 清理中文CommandHandler

如果bot启动失败并报错 `ValueError: Command '中文' is not a valid bot command`，请执行：

```bash
cd /root
wget https://raw.githubusercontent.com/JasonNF/xx/main/final_cleanup_chinese_handlers.sh
chmod +x final_cleanup_chinese_handlers.sh
sudo ./final_cleanup_chinese_handlers.sh
```

该脚本会：
1. 自动备份当前handlers目录
2. 扫描并删除所有中文CommandHandler
3. 保留英文CommandHandler和chinese_commands.py模块
4. 验证并重启服务

## 部署脚本说明

### 主要部署脚本

1. **deploy.sh** - 完整部署脚本
   - 安装所有依赖（PostgreSQL, Redis, Python等）
   - 配置数据库和环境变量
   - 创建systemd服务

2. **deploy_without_redis.sh** - 无Redis部署
   - 用于Redis端口冲突时
   - 功能与deploy.sh相同但不安装Redis

3. **deploy_use_existing_redis.sh** - 使用现有Redis
   - 连接到其他端口的Redis实例

### 问题修复脚本

#### 核心修复
- **final_cleanup_chinese_handlers.sh** ⭐ 推荐
  - 彻底清理所有中文CommandHandler
  - 解决bot启动失败问题

#### 配置修复
- **fix_config.sh** - 修复.env配置格式
- **fix_service.sh** - 修复systemd服务配置
- **fix_database_url.sh** - 修复PostgreSQL连接

#### 依赖修复
- **install_missing_deps.sh** - 安装缺失的Python依赖
- **fix_permissions_and_deps.sh** - 修复权限和依赖

#### Handler恢复
- **restore_all_handlers_from_backup.sh** - 从备份完全恢复
- **restore_handlers.sh** - 部分恢复handlers

#### 调试工具
- **diagnose_chinese_commands.sh** - 诊断中文命令模块
- **check_and_fix_english_commands.sh** - 检查英文命令完整性

## 中文命令支持

Bot支持两种命令格式：
- 英文：`/start` `/cultivate` `/battle`
- 中文：`.开始` `.修炼` `.战斗`

实现方式：
- 英文命令使用Telegram标准的CommandHandler
- 中文命令使用MessageHandler + Regex匹配，然后映射到英文命令

核心文件：`/opt/xiuxian-bot/src/bot/handlers/chinese_commands.py`

## 常见问题

### 1. Bot无响应
```bash
# 检查服务状态
systemctl status xiuxian-bot

# 查看日志
journalctl -u xiuxian-bot -n 50

# 重启服务
systemctl restart xiuxian-bot
```

### 2. 中文命令报错
执行 `final_cleanup_chinese_handlers.sh` 清理中文CommandHandler

### 3. PostgreSQL连接错误
```bash
# 禁用SSL
./fix_database_url.sh
```

### 4. Redis端口冲突
```bash
# 使用无Redis部署
./deploy_without_redis.sh
```

## 环境要求

- Debian 11/12 或 Ubuntu 20.04+
- Python 3.11+
- PostgreSQL 15+
- Redis 7+ (可选)

## 配置文件

`.env` 文件示例：
```env
BOT_TOKEN=你的token
DATABASE_URL=postgresql+asyncpg://xiuxian:密码@localhost/xiuxian_prod
ADMIN_IDS=[你的telegram_id]
```

## 服务管理

```bash
# 启动
systemctl start xiuxian-bot

# 停止
systemctl stop xiuxian-bot

# 重启
systemctl restart xiuxian-bot

# 查看状态
systemctl status xiuxian-bot

# 查看日志
journalctl -u xiuxian-bot -f
```

## 技术架构

- **Bot框架**: python-telegram-bot 21.x (async)
- **数据库**: PostgreSQL + asyncpg
- **ORM**: SQLAlchemy 2.x (async)
- **配置管理**: Pydantic Settings
- **进程管理**: systemd

## 获取帮助

如遇问题，请提供：
1. 错误日志：`journalctl -u xiuxian-bot -n 100`
2. 服务状态：`systemctl status xiuxian-bot`
3. Python版本：`python3 --version`
4. 系统版本：`cat /etc/os-release`
