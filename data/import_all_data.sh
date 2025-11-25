#!/bin/bash

# 游戏数据一键导入脚本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "======================================="
echo "  修仙世界 - 游戏数据导入脚本"
echo "======================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 检查数据库文件
if [ ! -f "xiuxian.db" ]; then
    echo -e "${YELLOW}⚠ 数据库文件不存在，将在导入时自动创建${NC}"
fi

# 检查SQL文件
echo "🔍 检查数据文件..."
MISSING_FILES=0

if [ ! -f "init_skills_new.sql" ]; then
    echo -e "${RED}✗ 缺少 init_skills_new.sql${NC}"
    MISSING_FILES=$((MISSING_FILES + 1))
else
    echo -e "${GREEN}✓${NC} init_skills_new.sql"
fi

if [ ! -f "init_monsters_fixed.sql" ]; then
    echo -e "${RED}✗ 缺少 init_monsters_fixed.sql${NC}"
    MISSING_FILES=$((MISSING_FILES + 1))
else
    echo -e "${GREEN}✓${NC} init_monsters_fixed.sql"
fi

if [ ! -f "init_items_equipment.sql" ]; then
    echo -e "${RED}✗ 缺少 init_items_equipment.sql${NC}"
    MISSING_FILES=$((MISSING_FILES + 1))
else
    echo -e "${GREEN}✓${NC} init_items_equipment.sql"
fi

if [ $MISSING_FILES -gt 0 ]; then
    echo -e "${RED}错误: 缺少 $MISSING_FILES 个数据文件${NC}"
    echo "请确保以下文件存在:"
    echo "  - init_skills_new.sql (70个技能)"
    echo "  - init_monsters_fixed.sql (92个怪物)"
    echo "  - init_items_equipment.sql (230个物品)"
    exit 1
fi

echo ""
echo -e "${YELLOW}⚠ 警告: 此操作将清空并重新导入以下数据:${NC}"
echo "  - 技能 (skills)"
echo "  - 怪物 (monsters)"
echo "  - 物品 (items)"
echo ""
echo -e "${RED}现有数据将被删除！${NC}"
echo ""
read -p "确认继续? (yes/no): " -r
echo

if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo "已取消"
    exit 0
fi

# 备份现有数据库
if [ -f "xiuxian.db" ]; then
    BACKUP_FILE="xiuxian_backup_$(date +%Y%m%d_%H%M%S).db"
    echo ""
    echo "📦 备份现有数据库..."
    cp xiuxian.db "$BACKUP_FILE"
    echo -e "${GREEN}✓${NC} 备份保存至: $BACKUP_FILE"
fi

echo ""
echo "======================================="
echo "  开始导入数据..."
echo "======================================="
echo ""

# 导入技能数据
echo -e "${BLUE}[1/3]${NC} 导入技能数据..."
sqlite3 xiuxian.db << 'EOSQL'
DELETE FROM skills;
DELETE FROM sqlite_sequence WHERE name='skills';
.read init_skills_new.sql
EOSQL

SKILL_COUNT=$(sqlite3 xiuxian.db "SELECT COUNT(*) FROM skills;")
if [ "$SKILL_COUNT" -gt 0 ]; then
    echo -e "${GREEN}✓${NC} 成功导入 $SKILL_COUNT 个技能"
else
    echo -e "${RED}✗${NC} 技能导入失败"
    exit 1
fi

# 导入怪物数据
echo -e "${BLUE}[2/3]${NC} 导入怪物数据..."
sqlite3 xiuxian.db << 'EOSQL'
DELETE FROM monsters;
DELETE FROM sqlite_sequence WHERE name='monsters';
.read init_monsters_fixed.sql
EOSQL

MONSTER_COUNT=$(sqlite3 xiuxian.db "SELECT COUNT(*) FROM monsters;")
if [ "$MONSTER_COUNT" -gt 0 ]; then
    echo -e "${GREEN}✓${NC} 成功导入 $MONSTER_COUNT 个怪物"
else
    echo -e "${RED}✗${NC} 怪物导入失败"
    exit 1
fi

# 导入物品数据
echo -e "${BLUE}[3/3]${NC} 导入物品装备数据..."
sqlite3 xiuxian.db << 'EOSQL'
DELETE FROM items;
DELETE FROM sqlite_sequence WHERE name='items';
.read init_items_equipment.sql
EOSQL

ITEM_COUNT=$(sqlite3 xiuxian.db "SELECT COUNT(*) FROM items;")
if [ "$ITEM_COUNT" -gt 0 ]; then
    echo -e "${GREEN}✓${NC} 成功导入 $ITEM_COUNT 个物品"
else
    echo -e "${RED}✗${NC} 物品导入失败"
    exit 1
fi

# 显示统计信息
echo ""
echo "======================================="
echo "  📊 导入统计"
echo "======================================="

sqlite3 xiuxian.db << 'EOSQL'
.mode column
.headers on

SELECT '技能' as 类别, COUNT(*) as 数量 FROM skills
UNION ALL
SELECT '怪物', COUNT(*) FROM monsters
UNION ALL
SELECT '物品', COUNT(*) FROM items
UNION ALL
SELECT '总计',
  (SELECT COUNT(*) FROM skills) +
  (SELECT COUNT(*) FROM monsters) +
  (SELECT COUNT(*) FROM items);
EOSQL

echo ""
echo "======================================="
echo "  ✨ 数据导入完成!"
echo "======================================="
echo ""
echo "数据详情:"
echo "  • 技能: $SKILL_COUNT (目标 70+)"
echo "  • 怪物: $MONSTER_COUNT (目标 70+)"
echo "  • 物品: $ITEM_COUNT (目标 200+)"
echo ""
echo "下一步:"
echo "  1. 返回项目根目录: cd .."
echo "  2. 启动Bot: ./start.sh"
echo "  3. 在Telegram中测试: /start"
echo ""
