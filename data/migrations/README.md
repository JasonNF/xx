# 数据库迁移说明

本目录包含所有数据库迁移脚本，用于更新数据库结构或数据。

## 迁移文件列表

### 1. add_credit_shop_tables.sql
**用途**: 创建积分商城相关表
- `credit_shop_items` - 商品表
- `player_credit_records` - 积分记录表
- `credit_shop_purchases` - 购买记录表
- `player_credit_shop_limits` - 限购记录表

**执行时机**: 首次部署积分商城系统时

### 2. add_rename_fields.sql
**用途**: 添加改名相关字段到玩家表
- `has_renamed` - 是否已改名
- `rename_time` - 改名时间
- `credits` - 积分字段

**执行时机**: 首次部署积分商城系统时

### 3. remove_rename_card.sql
**用途**: 将改名卡从商城下架
- 改名功能已统一为灵石购买方式（20,000灵石）
- 不删除历史数据，已购买的改名卡仍有效
- 新玩家无法再购买改名卡

**执行时机**: 更新到最新版本时

### 4. add_beast_quality.sql
**用途**: 添加灵兽品质系统
- 添加 `quality` 字段到 spirit_beast_templates 表
- 根据稀有度自动设置品质（凡品/仙品/神品）
- 创建品质和稀有度索引

**执行时机**: 部署灵兽品质系统时

### 5. add_beast_extensions.sql
**用途**: 添加灵兽扩展系统（天赋、进化、融合）
- 添加 `talents` 字段（存储天赋JSON）
- 添加 `evolution_stage` 字段（进化阶段）
- 创建 `beast_evolution_records` 表（进化记录）
- 创建 `beast_fusion_records` 表（融合记录）

**执行时机**: 部署灵兽扩展系统时

### 6. update_quality_terminology.sql
**用途**: 更新品质术语（凡级→凡品、仙级→仙品、神级→神品）
- 更新已有数据库中的 `quality` 字段值
- 确保术语一致性

**执行时机**: 如果已有数据库使用旧术语时执行（可选）

### 7. add_equipment_system.sql ⭐ 最新
**用途**: 添加装备系统（品质、强化、套装）
- 扩展 `items` 表添加 `quality`, `set_id`, `equipment_slot` 字段
- 扩展 `player_inventory` 表添加 `enhancement_level` 字段
- 创建 `equipment_sets` 表（套装定义）
- 创建 `equipment_set_bonuses` 表（套装效果）
- 创建 `enhancement_records` 表（强化记录）

**执行时机**: 首次部署装备系统时

## 执行迁移

### SQLite 数据库
```bash
# 进入项目目录
cd /Users/zc/EC-AI/xiuxian-game

# 备份数据库
cp data/xiuxian.db data/xiuxian.db.backup.$(date +%Y%m%d_%H%M%S)

# 执行装备系统迁移（最新）
sqlite3 data/xiuxian.db < data/migrations/add_equipment_system.sql

# 初始化四象套装数据
sqlite3 data/xiuxian.db < data/init_equipment_sets.sql
```

### 验证迁移
```bash
# 检查装备系统字段
sqlite3 data/xiuxian.db "PRAGMA table_info(items);" | grep -E "quality|set_id|equipment_slot"
sqlite3 data/xiuxian.db "PRAGMA table_info(player_inventory);" | grep "enhancement_level"

# 检查新表是否创建
sqlite3 data/xiuxian.db "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'equipment_%';"

# 应该显示:
# equipment_sets
# equipment_set_bonuses

# 检查套装数据
sqlite3 data/xiuxian.db "SELECT name, element, set_type FROM equipment_sets;"

# 应该显示:
# 青龙套装|木|攻击型
# 朱雀套装|火|爆发型
# 玄武套装|水|防御型
# 白虎套装|金|平衡型
```

## 迁移注意事项

1. **备份数据库**: 执行迁移前务必备份数据库
   ```bash
   cp data/xiuxian.db data/xiuxian.db.backup.$(date +%Y%m%d_%H%M%S)
   ```

2. **测试环境**: 先在测试环境执行迁移，确认无误后再在生产环境执行

3. **回滚计划**: 如需回滚，可恢复备份或手动执行反向操作
   ```sql
   -- 回滚 remove_rename_card.sql
   UPDATE credit_shop_items
   SET is_active = 1
   WHERE name = '改名卡';
   ```

4. **执行顺序**: 按文件编号顺序执行迁移

## 迁移历史

| 日期 | 文件 | 描述 |
|------|------|------|
| 2025-01-XX | add_credit_shop_tables.sql | 创建积分商城系统 |
| 2025-01-XX | add_rename_fields.sql | 添加改名和积分字段 |
| 2025-01-XX | remove_rename_card.sql | 下架改名卡商品 |
| 2025-01-XX | add_beast_quality.sql | 添加灵兽品质系统 |
| 2025-01-XX | add_beast_extensions.sql | 添加天赋/进化/融合系统 |
| 2025-01-XX | update_quality_terminology.sql | 更新品质术语为"品" |
| 2025-01-XX | add_equipment_system.sql | 添加装备系统（品质/强化/套装） |
