# 快速开始 - 修仙世界Bot修复

## 🚨 紧急修复 - Bot启动失败

如果你的bot报错：`ValueError: Command '中文' is not a valid bot command`

**在服务器上执行以下命令：**

```bash
# 1. 进入root目录
cd /root

# 2. 拉取最新代码
cd /opt/xiuxian-bot
git pull origin main

# 3. 执行清理脚本
cd /root
wget https://raw.githubusercontent.com/JasonNF/xx/main/final_cleanup_chinese_handlers.sh
chmod +x final_cleanup_chinese_handlers.sh
sudo ./final_cleanup_chinese_handlers.sh
```

## ✅ 预期结果

脚本执行后会显示：

```
========================================
  彻底清理中文CommandHandler
========================================

✓ 备份到: /opt/xiuxian-bot-handlers-backup-XXXXXXXX
✓ 清理完成
✓ 权限已修正
✓ 服务运行正常!

========================================
  清理成功完成!
========================================

🎮 测试命令:
  英文: /start /info /cultivate
  中文: .开始 .状态 .修炼
```

## 🧪 测试

在Telegram中测试以下命令：

**英文命令：**
- `/start` - 检测灵根
- `/info` - 查看状态
- `/cultivate` - 开始修炼

**中文命令：**
- `.开始` - 检测灵根
- `.状态` - 查看状态
- `.修炼` - 开始修炼

## 📊 监控

```bash
# 实时查看日志
journalctl -u xiuxian-bot -f

# 查看最近日志
journalctl -u xiuxian-bot -n 50

# 检查服务状态
systemctl status xiuxian-bot
```

## ❓ 如果还是失败

1. 查看错误日志：
```bash
journalctl -u xiuxian-bot -n 100 --no-pager
```

2. 检查是否还有中文CommandHandler：
```bash
cd /opt/xiuxian-bot/src/bot/handlers
grep -r "CommandHandler.*[\u4e00-\u9fff]" *.py
```

3. 手动重启服务：
```bash
systemctl restart xiuxian-bot
systemctl status xiuxian-bot
```

## 📖 完整文档

详细文档请查看：[README_DEPLOYMENT.md](README_DEPLOYMENT.md)
