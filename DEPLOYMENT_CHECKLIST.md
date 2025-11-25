# ✅ 生产环境部署检查清单

使用此清单确保所有部署步骤都已正确完成。

---

## 📋 部署前检查

### 服务器环境

- [ ] 服务器操作系统: Debian/Ubuntu Linux
- [ ] 有root/sudo权限
- [ ] 至少512MB内存 (推荐1GB+)
- [ ] 至少500MB可用磁盘空间
- [ ] 网络连接正常,可访问GitHub

### Telegram配置

- [ ] 已从 @BotFather 创建Bot
- [ ] 已获取Bot Token
- [ ] 已记录Bot用户名
- [ ] 已从 @userinfobot 获取管理员用户ID

### 准备材料

- [ ] Bot Token已准备
- [ ] 管理员ID列表已准备
- [ ] 已规划域名 (如果需要API)
- [ ] 已准备SSL证书 (如果需要HTTPS)

---

## 🚀 部署步骤检查

### 1. 克隆项目

- [ ] 已克隆项目到服务器
  ```bash
  git clone https://github.com/JasonNF/xx.git
  ```

- [ ] 已进入项目目录
  ```bash
  cd xx
  ```

### 2. 运行部署脚本

- [ ] 以root权限运行部署脚本
  ```bash
  sudo bash deploy.sh
  ```

- [ ] 脚本执行完成,无报错

### 3. 配置信息已输入

- [ ] 已输入正确的Bot Token
- [ ] 已输入管理员ID
- [ ] 数据库凭证已自动生成

### 4. 系统依赖已安装

- [ ] Python 3.11+ 已安装
- [ ] PostgreSQL 已安装并运行
- [ ] Redis 已安装并运行
- [ ] 其他系统依赖已安装

### 5. 服务配置完成

- [ ] 服务用户 `xiuxian` 已创建
- [ ] 数据库 `xiuxian_prod` 已创建
- [ ] 数据库用户已创建并授权
- [ ] systemd服务已配置

### 6. 应用程序已部署

- [ ] 项目文件已复制到 `/opt/xiuxian-bot`
- [ ] Python虚拟环境已创建
- [ ] 依赖包已安装
- [ ] .env配置文件已创建

---

## ✅ 部署后验证

### 服务状态检查

- [ ] 服务正在运行
  ```bash
  sudo systemctl status xiuxian-bot
  # 应该显示: Active: active (running)
  ```

- [ ] 服务已设置开机自启
  ```bash
  sudo systemctl is-enabled xiuxian-bot
  # 应该显示: enabled
  ```

### 日志检查

- [ ] 系统日志无严重错误
  ```bash
  sudo journalctl -u xiuxian-bot -n 50
  ```

- [ ] 看到 "Bot 启动成功" 消息
- [ ] 看到 "数据库初始化完成" 消息
- [ ] 看到 "调度器已启动" 消息

### 数据库检查

- [ ] PostgreSQL服务运行正常
  ```bash
  sudo systemctl status postgresql
  ```

- [ ] 可以连接数据库
  ```bash
  sudo -u postgres psql -d xiuxian_prod -c "SELECT version();"
  ```

- [ ] 数据表已创建
  ```bash
  sudo -u postgres psql -d xiuxian_prod -c "\dt"
  ```

### Redis检查

- [ ] Redis服务运行正常
  ```bash
  sudo systemctl status redis-server
  ```

- [ ] Redis响应正常
  ```bash
  redis-cli ping
  # 应该返回: PONG
  ```

### 功能测试

- [ ] 在Telegram中找到Bot
- [ ] 发送 `/start` 命令
- [ ] 收到注册成功消息
- [ ] 发送 `/info` 查看角色信息
- [ ] 发送 `/help` 查看帮助
- [ ] 尝试 `/修炼` 命令
- [ ] 尝试 `/战斗 野狼` 命令

---

## 🔧 配置优化检查

### 环境变量配置

- [ ] 已检查 `/opt/xiuxian-bot/.env` 文件
- [ ] BOT_TOKEN 正确
- [ ] DATABASE_URL 正确
- [ ] ADMIN_IDS 正确
- [ ] 其他参数根据需要调整

### 游戏平衡性参数

- [ ] BASE_CULTIVATION_RATE (修炼速度)
- [ ] BREAKTHROUGH_BASE_CHANCE (突破成功率)
- [ ] DAILY_SIGN_REWARD (签到奖励)
- [ ] NEWBIE_GIFT (新手礼包)
- [ ] PVE_COOLDOWN (PVE冷却)
- [ ] PVP_COOLDOWN (PVP冷却)

### 性能配置

- [ ] 数据库连接池大小合适
- [ ] Redis连接配置正确
- [ ] 日志级别设置为INFO或WARNING

---

## 🔒 安全检查

### 文件权限

- [ ] .env文件权限设置为600
  ```bash
  ls -la /opt/xiuxian-bot/.env
  # 应该显示: -rw------- xiuxian xiuxian
  ```

- [ ] 数据目录权限正确
  ```bash
  ls -ld /opt/xiuxian-bot/data
  ```

### 防火墙配置

- [ ] 仅开放必要端口
  ```bash
  sudo ufw status
  ```

- [ ] SSH端口已开放
- [ ] 不必要的端口已关闭

### 数据库安全

- [ ] 数据库密码已生成且复杂
- [ ] 数据库仅允许本地连接
- [ ] 已删除临时凭证文件
  ```bash
  sudo rm /tmp/db_credentials.txt
  ```

---

## 📊 监控配置检查

### 日志轮转

- [ ] 系统日志配置正确
- [ ] 应用日志写入正确位置
- [ ] 日志文件不会无限增长

### 健康检查

- [ ] 创建健康检查脚本
- [ ] 配置定时任务
  ```bash
  sudo crontab -l
  ```

### 备份配置

- [ ] 创建备份脚本
- [ ] 配置定时备份
- [ ] 测试备份恢复流程

---

## 📈 性能优化检查

### 资源使用

- [ ] 检查CPU使用率
  ```bash
  top -u xiuxian
  ```

- [ ] 检查内存使用
  ```bash
  ps aux | grep python
  ```

- [ ] 检查磁盘使用
  ```bash
  df -h /opt/xiuxian-bot
  ```

### 数据库性能

- [ ] 检查数据库连接数
  ```bash
  sudo -u postgres psql -c "SELECT count(*) FROM pg_stat_activity;"
  ```

- [ ] 检查慢查询 (如果有)

### Redis性能

- [ ] 检查Redis内存使用
  ```bash
  redis-cli info memory
  ```

- [ ] 检查Redis连接数
  ```bash
  redis-cli info clients
  ```

---

## 📚 文档检查

### 必读文档

- [ ] 已阅读 `DEPLOY_NOW.md`
- [ ] 已阅读 `PRODUCTION_DEPLOYMENT.md`
- [ ] 已了解常用管理命令
- [ ] 已了解故障排查方法

### 保留重要文件

- [ ] 已备份 `.env` 文件
- [ ] 已记录数据库密码
- [ ] 已记录重要配置信息

---

## 🎉 最终确认

### 部署完成标志

- [ ] ✅ 所有服务正常运行
- [ ] ✅ Bot在Telegram中响应正常
- [ ] ✅ 日志无严重错误
- [ ] ✅ 数据库连接正常
- [ ] ✅ Redis缓存工作正常
- [ ] ✅ 已测试核心功能
- [ ] ✅ 已配置监控和备份
- [ ] ✅ 安全设置已检查

### 部署后任务

- [ ] 通知团队成员部署完成
- [ ] 开始邀请测试用户
- [ ] 监控初期运行情况
- [ ] 根据反馈调整参数
- [ ] 建立定期维护计划

---

## 📞 问题记录

如果遇到问题,请记录:

**问题描述**:


**错误日志**:


**解决方案**:


**参考文档**: `PRODUCTION_DEPLOYMENT.md` 故障排查章节

---

## ✅ 签字确认

**部署人员**: _______________

**部署日期**: _______________

**服务器**: _______________

**Bot用户名**: _______________

**备注**:


---

**恭喜!部署检查全部完成!** 🎉

你的修仙世界Bot已经准备好迎接玩家了!
