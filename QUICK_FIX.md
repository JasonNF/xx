# 快速修复指南

## 🚀 一键修复命令

复制以下命令到服务器执行：

```bash
cd /root && \
wget -q https://raw.githubusercontent.com/JasonNF/xx/main/fix_start_imports.sh -O fix_start_imports.sh && \
chmod +x fix_start_imports.sh && \
./fix_start_imports.sh
```

## 📋 或者分步执行

### 步骤1：下载修复脚本
```bash
cd /root
wget https://raw.githubusercontent.com/JasonNF/xx/main/fix_start_imports.sh
```

### 步骤2：添加执行权限
```bash
chmod +x fix_start_imports.sh
```

### 步骤3：执行修复
```bash
./fix_start_imports.sh
```

## 🔍 如果修复失败

### 查看详细错误
```bash
journalctl -u xiuxian-bot -n 100 --no-pager
```

### 手动恢复备份
```bash
# 查看所有备份
ls -la /opt/xiuxian-bot/src/bot/handlers/start.py.backup.*

# 恢复到最早的备份（修改前的版本）
EARLIEST_BACKUP=$(ls -t /opt/xiuxian-bot/src/bot/handlers/start.py.backup.* | tail -1)
cp "$EARLIEST_BACKUP" /opt/xiuxian-bot/src/bot/handlers/start.py

# 重启服务
systemctl restart xiuxian-bot
```

## 📊 验证修复成功

```bash
# 检查服务状态
systemctl status xiuxian-bot

# 查看日志
journalctl -u xiuxian-bot -n 30

# 实时监控
journalctl -u xiuxian-bot -f
```

## ✅ 成功标志

日志中应该看到：
- ✅ `Bot 启动成功！`
- ✅ `✅ 已加载 81 个中文命令支持`
- ✅ `✅ start handlers已注册: /start, /help, /info`

## 🎮 测试命令

在Telegram中测试：
- `/start` - 应该显示灵根检测
- `.开始` - 应该显示灵根检测
- `/info` - 应该显示玩家状态
- `.状态` - 应该显示玩家状态

**重要**：消息会在15秒后自动删除！

## 🆘 紧急恢复

如果一切都失败了，恢复到没有自动删除功能的版本：

```bash
cd /root
wget https://raw.githubusercontent.com/JasonNF/xx/main/fix_status_command_attributes.sh
chmod +x fix_status_command_attributes.sh
./fix_status_command_attributes.sh
```

这会恢复到之前的稳定版本（没有自动删除功能，但所有命令都能工作）。
