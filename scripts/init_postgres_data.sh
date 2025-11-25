#!/bin/bash

#===============================================
# PostgreSQL数据库初始化脚本
# 用于将SQLite SQL脚本转换并导入到PostgreSQL
#===============================================

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 数据库配置 (从环境变量或.env读取)
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-xiuxian_prod}"
DB_USER="${DB_USER:-xiuxian}"
DB_PASSWORD="${DB_PASSWORD}"

# 检查psql命令
if ! command -v psql &> /dev/null; then
    echo -e "${RED}错误: 未找到 psql 命令${NC}"
    echo "请安装 PostgreSQL 客户端"
    exit 1
fi

# 检查环境变量
if [ -z "$DB_PASSWORD" ]; then
    echo -e "${YELLOW}请输入数据库密码:${NC}"
    read -s DB_PASSWORD
    export PGPASSWORD=$DB_PASSWORD
fi

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  PostgreSQL 数据库初始化${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# SQL转换函数 (SQLite -> PostgreSQL)
convert_sql_for_postgres() {
    local input_file=$1
    local output_file=$2

    # 基本转换
    sed -e 's/INTEGER PRIMARY KEY AUTOINCREMENT/SERIAL PRIMARY KEY/g' \
        -e 's/DATETIME/TIMESTAMP/g' \
        -e 's/REAL/NUMERIC/g' \
        -e 's/TEXT/VARCHAR/g' \
        -e 's/BOOLEAN/BOOLEAN/g' \
        "$input_file" > "$output_file"
}

# 进入data目录
cd "$(dirname "$0")/../data" || exit 1

echo -e "${YELLOW}1. 测试数据库连接...${NC}"
if psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT version();" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ 数据库连接成功${NC}"
else
    echo -e "${RED}✗ 数据库连接失败${NC}"
    echo "请检查数据库配置和密码"
    exit 1
fi

echo ""
echo -e "${YELLOW}2. 创建表结构...${NC}"
echo "注意: 表结构会在首次运行应用时自动创建"
echo "SQLAlchemy会根据模型定义自动创建表"
echo -e "${GREEN}✓ 跳过手动创建表${NC}"

echo ""
echo -e "${YELLOW}3. 导入游戏数据...${NC}"

# 数据文件列表
DATA_FILES=(
    "init_skills_new.sql"
    "init_monsters_fixed.sql"
    "init_items_equipment.sql"
    "init_equipment_sets.sql"
    "init_spirit_beasts.sql"
    "init_secret_realms.sql"
    "init_world_boss_templates.sql"
    "init_sect_cultivation_methods.sql"
    "init_sect_quests.sql"
    "init_sect_shop.sql"
    "init_refinery_materials.sql"
    "init_refinery_recipes.sql"
    "init_credit_shop.sql"
)

total=${#DATA_FILES[@]}
current=0

for sql_file in "${DATA_FILES[@]}"; do
    current=$((current + 1))

    if [ -f "$sql_file" ]; then
        echo -n "  [$current/$total] 导入 $sql_file ... "

        # 转换SQL (如果需要)
        temp_file="/tmp/postgres_${sql_file}"
        convert_sql_for_postgres "$sql_file" "$temp_file"

        # 导入到PostgreSQL
        if PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$temp_file" > /dev/null 2>&1; then
            echo -e "${GREEN}✓${NC}"
        else
            echo -e "${YELLOW}⚠ (跳过)${NC}"
        fi

        rm -f "$temp_file"
    else
        echo -e "  [$current/$total] ${YELLOW}文件不存在: $sql_file${NC}"
    fi
done

echo ""
echo -e "${YELLOW}4. 验证数据...${NC}"

# 验证各表数据量
check_table() {
    local table=$1
    local count=$(PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT COUNT(*) FROM $table;" 2>/dev/null | tr -d ' ')

    if [ -n "$count" ] && [ "$count" != "0" ]; then
        echo -e "  ✓ $table: ${GREEN}$count${NC} 条记录"
    else
        echo -e "  ⚠ $table: ${YELLOW}$count${NC} 条记录"
    fi
}

# 检查主要数据表
check_table "skills"
check_table "monsters"
check_table "items"
check_table "spirit_beasts"
check_table "equipment_sets"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  数据库初始化完成!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "提示:"
echo "  - 如果某些表为空,应用首次启动时会自动创建"
echo "  - 可以通过应用的数据初始化脚本导入更多数据"
echo ""
