# 灵兽系统 v2.0 部署指南

## 🚀 快速部署

### 方案A：新用户全新部署

适用于首次部署游戏的用户。

```bash
# 1. 进入项目目录
cd /Users/zc/EC-AI/xiuxian-game

# 2. 创建数据库并初始化（包含30种灵兽和所有扩展功能）
sqlite3 data/xiuxian.db < data/init_spirit_beasts.sql

# 3. 启动游戏
python src/main.py
```

---

### 方案B：现有用户升级部署

适用于已有数据库的用户，保留现有玩家数据。

```bash
# 1. 进入项目目录
cd /Users/zc/EC-AI/xiuxian-game

# 2. 备份现有数据库（重要！）
cp data/xiuxian.db data/xiuxian.db.backup.$(date +%Y%m%d_%H%M%S)

# 3. 执行品质系统迁移
sqlite3 data/xiuxian.db < data/migrations/add_beast_quality.sql

# 4. 执行扩展系统迁移
sqlite3 data/xiuxian.db < data/migrations/add_beast_extensions.sql

# 5. 导入30种灵兽数据（如果之前没有灵兽数据）
sqlite3 data/xiuxian.db < data/init_spirit_beasts.sql

# 6. 重启游戏
python src/main.py
```

---

## ✅ 部署验证

### 1. 检查数据库结构

```bash
# 检查 player_spirit_beasts 表是否包含新字段
sqlite3 data/xiuxian.db "PRAGMA table_info(player_spirit_beasts);"
```

**预期输出**（应包含）：
```
...
talents|TEXT|0||1
evolution_stage|INTEGER|1|0|0
...
```

### 2. 检查新表是否创建

```bash
# 检查进化记录表
sqlite3 data/xiuxian.db "SELECT name FROM sqlite_master WHERE type='table' AND name='beast_evolution_records';"

# 检查融合记录表
sqlite3 data/xiuxian.db "SELECT name FROM sqlite_master WHERE type='table' AND name='beast_fusion_records';"
```

**预期输出**：
```
beast_evolution_records
beast_fusion_records
```

### 3. 检查灵兽数据

```bash
# 检查灵兽总数
sqlite3 data/xiuxian.db "SELECT COUNT(*) FROM spirit_beast_templates;"

# 检查品质分布
sqlite3 data/xiuxian.db "SELECT quality, COUNT(*) FROM spirit_beast_templates GROUP BY quality;"
```

**预期输出**：
```
30

凡品|10
仙品|10
神品|10
```

---

## 🎮 功能测试

### 测试步骤

1. **启动Bot**
```bash
python src/main.py
```

2. **测试基础命令**
```
/灵根              # 注册新玩家
/灵兽图鉴          # 查看30种灵兽
/捕捉灵兽          # 捕捉灵兽（应显示天赋）
/灵兽              # 查看灵兽列表（应显示天赋）
```

3. **测试扩展功能**
```
/训练灵兽 <昵称> 1  # 训练到Lv.10
/灵兽进化 <昵称>     # 测试进化（如果是仙品或神品）
/灵兽融合 <昵称1> <昵称2>  # 测试融合（需要2只同品质灵兽）
```

---

## 🔧 常见问题

### Q1: 执行迁移时提示 "duplicate column name"

**原因**：字段已存在，可能已执行过迁移。

**解决方案**：
```bash
# 检查字段是否已存在
sqlite3 data/xiuxian.db "PRAGMA table_info(player_spirit_beasts);"

# 如果已有 talents 和 evolution_stage 字段，跳过迁移
# 如果没有，重新执行迁移
```

### Q2: 灵兽数据导入失败

**原因**：可能表结构不匹配或数据已存在。

**解决方案**：
```bash
# 1. 检查 spirit_beast_templates 表是否有 quality 字段
sqlite3 data/xiuxian.db "PRAGMA table_info(spirit_beast_templates);"

# 2. 如果没有，先执行品质迁移
sqlite3 data/xiuxian.db < data/migrations/add_beast_quality.sql

# 3. 清空旧数据（可选，谨慎操作）
sqlite3 data/xiuxian.db "DELETE FROM spirit_beast_templates;"

# 4. 重新导入
sqlite3 data/xiuxian.db < data/init_spirit_beasts.sql
```

### Q3: 捕捉灵兽没有显示天赋

**原因**：代码未更新或导入失败。

**解决方案**：
```bash
# 1. 确认服务层文件存在
ls -la src/bot/services/spirit_beast_service.py

# 2. 确认配置文件存在
ls -la src/bot/config/talent_config.py

# 3. 重启Bot
pkill -f "python src/main.py"
python src/main.py
```

### Q4: 进化命令不可用

**原因**：命令未注册或数据库字段缺失。

**解决方案**：
```bash
# 1. 检查字段
sqlite3 data/xiuxian.db "PRAGMA table_info(player_spirit_beasts);" | grep evolution

# 2. 检查handler文件
grep "evolve_beast_command" src/bot/handlers/spirit_beast.py

# 3. 重启Bot
python src/main.py
```

---

## 📦 文件清单

部署需要以下文件：

### 核心代码
- ✅ `src/bot/models/spirit_beast.py` - 数据模型
- ✅ `src/bot/services/spirit_beast_service.py` - 服务层（新增）
- ✅ `src/bot/config/talent_config.py` - 天赋配置（新增）
- ✅ `src/bot/handlers/spirit_beast.py` - 命令处理器

### 数据库
- ✅ `data/init_spirit_beasts.sql` - 灵兽初始数据
- ✅ `data/migrations/add_beast_quality.sql` - 品质迁移
- ✅ `data/migrations/add_beast_extensions.sql` - 扩展迁移（新增）

### 文档
- ✅ `docs/灵兽品质系统说明.md` - 品质系统文档
- ✅ `docs/灵兽扩展系统说明.md` - 扩展系统文档（新增）
- ✅ `docs/灵兽系统更新总览.md` - 更新总览（新增）
- ✅ `DEPLOYMENT.md` - 本部署指南（新增）

---

## 🔄 回滚方案

如果部署后出现问题，可以回滚到之前版本：

```bash
# 1. 停止Bot
pkill -f "python src/main.py"

# 2. 恢复数据库备份
cp data/xiuxian.db.backup.YYYYMMDD_HHMMSS data/xiuxian.db

# 3. 恢复代码（如果使用git）
git checkout HEAD~1

# 4. 重启Bot
python src/main.py
```

---

## 📊 性能监控

### 监控指标

1. **数据库大小**
```bash
du -h data/xiuxian.db
```

2. **灵兽总数**
```bash
sqlite3 data/xiuxian.db "SELECT COUNT(*) FROM player_spirit_beasts;"
```

3. **进化记录**
```bash
sqlite3 data/xiuxian.db "SELECT COUNT(*) FROM beast_evolution_records;"
```

4. **融合记录**
```bash
sqlite3 data/xiuxian.db "SELECT COUNT(*) FROM beast_fusion_records;"
```

---

## 🎯 下一步

部署完成后，建议：

1. **阅读文档**
   - `docs/灵兽扩展系统说明.md` - 了解所有新功能
   - `docs/灵兽品质系统说明.md` - 了解30种灵兽

2. **测试功能**
   - 创建测试账号
   - 依次测试捕捉、训练、进化、融合功能
   - 验证天赋系统工作正常

3. **通知玩家**
   - 发布更新公告
   - 说明新增命令和功能
   - 提供游戏指引

---

## 📞 技术支持

如遇到问题，请检查：

1. **日志文件**（如果有配置）
2. **数据库完整性**：`sqlite3 data/xiuxian.db "PRAGMA integrity_check;"`
3. **Python依赖**：确保所有依赖已安装

---

**版本**：v2.0.0
**最后更新**：2025-01-XX
**状态**：✅ 已完成测试
