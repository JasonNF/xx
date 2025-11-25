# 修仙世界 Telegram Bot - 文档索引

## 🚀 快速入口

### 紧急修复
- **[快速开始](QUICKSTART.md)** ⭐ 如果bot启动失败，从这里开始
- **[核心修复脚本](final_cleanup_chinese_handlers.sh)** - 一键清理中文CommandHandler

### 完整文档
- **[部署文档](README_DEPLOYMENT.md)** - 完整的部署指南和故障排除
- **[解决方案总结](SOLUTION_SUMMARY.md)** - 技术方案详解和实现原理

## 📁 文件结构

```
xx/
├── INDEX.md                              # 本文件 - 文档索引
├── QUICKSTART.md                         # 快速开始指南
├── README_DEPLOYMENT.md                  # 完整部署文档
├── SOLUTION_SUMMARY.md                   # 问题解决方案总结
│
├── final_cleanup_chinese_handlers.sh     # ⭐ 核心修复脚本
│
├── deploy.sh                             # 完整部署脚本
├── deploy_without_redis.sh               # 无Redis部署
├── deploy_use_existing_redis.sh          # 使用现有Redis
│
├── fix_config.sh                         # 配置修复
├── fix_service.sh                        # systemd服务修复
├── fix_database_url.sh                   # 数据库连接修复
├── install_missing_deps.sh               # 安装依赖
│
├── restore_all_handlers_from_backup.sh   # 完全恢复handlers
├── restore_handlers.sh                   # 部分恢复
├── check_and_fix_english_commands.sh     # 检查英文命令
├── diagnose_chinese_commands.sh          # 诊断中文命令
│
└── [其他辅助脚本...]
```

## 🎯 使用场景

### 场景1：Bot启动失败
**错误信息**：`ValueError: Command '中文' is not a valid bot command`

**解决方案**：
1. 查看 [QUICKSTART.md](QUICKSTART.md)
2. 执行 `final_cleanup_chinese_handlers.sh`

### 场景2：首次部署
**需求**：在新服务器上部署bot

**解决方案**：
1. 查看 [README_DEPLOYMENT.md](README_DEPLOYMENT.md) 的"主要部署脚本"章节
2. 根据是否有Redis选择对应的deploy脚本

### 场景3：了解技术实现
**需求**：理解中文命令支持的实现原理

**解决方案**：
查看 [SOLUTION_SUMMARY.md](SOLUTION_SUMMARY.md) 的"解决方案"章节

### 场景4：数据库连接错误
**错误信息**：`PermissionError: postgresql.key`

**解决方案**：
1. 查看 [README_DEPLOYMENT.md](README_DEPLOYMENT.md) 的"常见问题"章节
2. 执行 `fix_database_url.sh`

### 场景5：Redis端口冲突
**错误信息**：`Port 6379 already in use`

**解决方案**：
使用 `deploy_without_redis.sh` 进行部署

## 📊 脚本功能对照表

| 脚本 | 功能 | 使用时机 |
|------|------|----------|
| final_cleanup_chinese_handlers.sh | 清理中文CommandHandler | Bot启动失败 ⭐ |
| deploy.sh | 完整部署 | 首次部署 |
| deploy_without_redis.sh | 无Redis部署 | Redis端口冲突 |
| fix_config.sh | 修复配置格式 | ADMIN_IDS等配置错误 |
| fix_service.sh | 修复systemd | 模块导入错误 |
| fix_database_url.sh | 修复数据库连接 | PostgreSQL SSL错误 |
| restore_all_handlers_from_backup.sh | 恢复所有handlers | 误删handlers |
| diagnose_chinese_commands.sh | 诊断中文命令 | 调试中文命令问题 |

## 🔧 常用命令

### 服务管理
```bash
# 查看状态
systemctl status xiuxian-bot

# 重启服务
systemctl restart xiuxian-bot

# 查看日志
journalctl -u xiuxian-bot -f
```

### 测试命令
```bash
# 在Telegram中测试
/start      # 英文命令
.开始       # 中文命令
```

### 检查配置
```bash
# 查看环境变量
cat /opt/xiuxian-bot/.env

# 检查Python路径
grep PYTHONPATH /etc/systemd/system/xiuxian-bot.service
```

## 📞 获取帮助

如遇问题，请按以下顺序检查：

1. **查看日志**：`journalctl -u xiuxian-bot -n 100`
2. **检查服务状态**：`systemctl status xiuxian-bot`
3. **查看相关文档**：
   - 快速问题 → [QUICKSTART.md](QUICKSTART.md)
   - 详细问题 → [README_DEPLOYMENT.md](README_DEPLOYMENT.md)
   - 技术细节 → [SOLUTION_SUMMARY.md](SOLUTION_SUMMARY.md)

## 📝 版本历史

- **2025-11-26** - 完整的文档和修复脚本系统
- **2025-11-25** - 初始部署和问题修复

## 🎮 项目简介

修仙世界是一个基于Telegram的文字修仙游戏bot，包含：
- 修炼系统（境界突破、功法修炼）
- 战斗系统（PVE、PVP）
- 物品系统（装备、丹药、法宝）
- 宗门系统（创建、管理、贡献）
- 社交系统（排行榜、成就）

**技术栈**：
- Python 3.11+
- python-telegram-bot 21.x (async)
- PostgreSQL 15+
- SQLAlchemy 2.x (async)

---

**最后更新**：2025-11-26
**维护者**：Claude Code
