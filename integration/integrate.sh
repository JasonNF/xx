#!/bin/bash

# 修仙游戏一键集成脚本
# 将修仙游戏自动集成到PMSManageBot

set -e  # 遇到错误立即退出

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 路径配置
XIUXIAN_DIR="/Users/zc/EC-AI/xiuxian-game"
PMS_DIR="/Users/zc/EC-AI/PMSManageBot"
INTEGRATION_DIR="${XIUXIAN_DIR}/integration"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  修仙游戏集成脚本 v1.0${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 检查PMSManageBot目录
if [ ! -d "$PMS_DIR" ]; then
    echo -e "${RED}❌ 错误: PMSManageBot目录不存在: $PMS_DIR${NC}"
    exit 1
fi

echo -e "${GREEN}✓ 找到PMSManageBot目录${NC}"

# 步骤1: 备份数据库
echo ""
echo -e "${YELLOW}[1/5] 备份数据库...${NC}"
DB_PATH="${PMS_DIR}/data/data.db"
if [ -f "$DB_PATH" ]; then
    BACKUP_PATH="${PMS_DIR}/data/data.db.backup.$(date +%Y%m%d_%H%M%S)"
    cp "$DB_PATH" "$BACKUP_PATH"
    echo -e "${GREEN}✓ 数据库已备份到: $BACKUP_PATH${NC}"
else
    echo -e "${RED}❌ 错误: 数据库文件不存在: $DB_PATH${NC}"
    exit 1
fi

# 步骤2: 执行数据库迁移
echo ""
echo -e "${YELLOW}[2/5] 执行数据库迁移...${NC}"
if sqlite3 "$DB_PATH" < "${INTEGRATION_DIR}/migrate_xiuxian_tables.sql"; then
    echo -e "${GREEN}✓ 数据库迁移成功${NC}"

    # 验证表是否创建
    TABLE_COUNT=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name LIKE 'xiuxian%';")
    echo -e "${GREEN}✓ 创建了 $TABLE_COUNT 个修仙游戏表${NC}"
else
    echo -e "${RED}❌ 数据库迁移失败${NC}"
    echo -e "${YELLOW}正在恢复备份...${NC}"
    cp "$BACKUP_PATH" "$DB_PATH"
    echo -e "${GREEN}✓ 已恢复备份${NC}"
    exit 1
fi

# 步骤3: 复制集成文件
echo ""
echo -e "${YELLOW}[3/5] 复制集成文件...${NC}"

# 创建xiuxian模块目录
XIUXIAN_MODULE_DIR="${PMS_DIR}/src/app/xiuxian"
mkdir -p "$XIUXIAN_MODULE_DIR"
echo -e "${GREEN}✓ 创建目录: $XIUXIAN_MODULE_DIR${NC}"

# 复制Python文件
cp "${INTEGRATION_DIR}/credits_bridge_service.py" "$XIUXIAN_MODULE_DIR/"
echo -e "${GREEN}✓ 复制: credits_bridge_service.py${NC}"

cp "${INTEGRATION_DIR}/xiuxian_exchange_handler.py" "$XIUXIAN_MODULE_DIR/"
echo -e "${GREEN}✓ 复制: xiuxian_exchange_handler.py${NC}"

cp "${INTEGRATION_DIR}/xiuxian_handlers.py" "$XIUXIAN_MODULE_DIR/"
echo -e "${GREEN}✓ 复制: xiuxian_handlers.py${NC}"

# 创建__init__.py
touch "${XIUXIAN_MODULE_DIR}/__init__.py"
echo -e "${GREEN}✓ 创建: __init__.py${NC}"

# 步骤4: 更新main.py
echo ""
echo -e "${YELLOW}[4/5] 更新main.py...${NC}"

MAIN_PY="${PMS_DIR}/src/app/main.py"
MAIN_PY_BACKUP="${MAIN_PY}.backup.$(date +%Y%m%d_%H%M%S)"

# 备份main.py
cp "$MAIN_PY" "$MAIN_PY_BACKUP"
echo -e "${GREEN}✓ main.py已备份到: $MAIN_PY_BACKUP${NC}"

# 检查是否已经添加过
if grep -q "from app.xiuxian" "$MAIN_PY"; then
    echo -e "${YELLOW}⚠ main.py已经包含修仙游戏导入，跳过修改${NC}"
else
    # 添加导入语句（在其他imports之后）
    sed -i '' '/from app.handlers.user import/a\
\
# 修仙游戏handlers\
from app.xiuxian.xiuxian_handlers import (\
    xiuxian_start_handler,\
    xiuxian_status_handler,\
    xiuxian_cultivate_handler,\
    xiuxian_finish_handler,\
    xiuxian_breakthrough_handler,\
    xiuxian_sign_handler,\
    xiuxian_help_handler,\
    xiuxian_callback_handler,\
)\
from app.xiuxian import xiuxian_exchange_handler
' "$MAIN_PY"

    # 添加handler注册（在application初始化之后）
    sed -i '' '/application = ApplicationBuilder/a\
\
    # 注册修仙游戏handlers\
    xiuxian_exchange_handler.register_exchange_handlers(application)
' "$MAIN_PY"

    echo -e "${GREEN}✓ main.py已更新${NC}"
fi

# 步骤5: 初始化游戏数据
echo ""
echo -e "${YELLOW}[5/5] 初始化游戏数据...${NC}"

if python3 "${INTEGRATION_DIR}/init_xiuxian_data.py"; then
    echo -e "${GREEN}✓ 游戏数据初始化成功${NC}"
else
    echo -e "${RED}❌ 游戏数据初始化失败${NC}"
    echo -e "${YELLOW}⚠ 可以稍后手动运行: python3 ${INTEGRATION_DIR}/init_xiuxian_data.py${NC}"
fi

# 完成
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✅ 集成完成！${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${GREEN}下一步操作：${NC}"
echo -e "1. 重启PMSManageBot:"
echo -e "   ${BLUE}cd ${PMS_DIR}/src && python -m app.main${NC}"
echo ""
echo -e "2. 在Telegram中测试:"
echo -e "   ${BLUE}/start${NC} - 创建角色"
echo -e "   ${BLUE}/status${NC} - 查看状态"
echo -e "   ${BLUE}/exchange${NC} - 积分兑换"
echo ""
echo -e "${YELLOW}如遇到问题，可以恢复备份：${NC}"
echo -e "   数据库: ${BLUE}$BACKUP_PATH${NC}"
echo -e "   main.py: ${BLUE}$MAIN_PY_BACKUP${NC}"
echo ""
echo -e "${GREEN}祝您修仙愉快！${NC} ✨"
