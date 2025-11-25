#!/bin/bash

#===============================================
# 安装缺失的Python依赖
#===============================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  安装缺失的依赖${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

if [[ $EUID -ne 0 ]]; then
    echo -e "${RED}需要root权限${NC}"
    exit 1
fi

INSTALL_DIR="/opt/xiuxian-bot"
SERVICE_USER="xiuxian"

# 1. 停止服务
echo -e "${YELLOW}1. 停止服务...${NC}"
systemctl stop xiuxian-bot
echo -e "${GREEN}✓ 已停止${NC}"

# 2. 安装asyncpg
echo ""
echo -e "${YELLOW}2. 安装asyncpg (PostgreSQL异步驱动)...${NC}"

cd "$INSTALL_DIR"
sudo -u "$SERVICE_USER" "$INSTALL_DIR/venv/bin/pip" install asyncpg -q

echo -e "${GREEN}✓ asyncpg已安装${NC}"

# 3. 验证依赖
echo ""
echo -e "${YELLOW}3. 验证所有依赖...${NC}"

# 检查关键依赖
DEPS=(
    "telegram"
    "sqlalchemy"
    "asyncpg"
    "aiosqlite"
    "pydantic"
    "pydantic_settings"
    "python-dotenv"
)

for dep in "${DEPS[@]}"; do
    if sudo -u "$SERVICE_USER" "$INSTALL_DIR/venv/bin/python" -c "import $dep" 2>/dev/null; then
        echo -e "  ${GREEN}✓${NC} $dep"
    else
        echo -e "  ${RED}✗${NC} $dep (正在安装...)"
        sudo -u "$SERVICE_USER" "$INSTALL_DIR/venv/bin/pip" install "$dep" -q
    fi
done

echo -e "${GREEN}✓ 所有依赖已就绪${NC}"

# 4. 测试数据库连接
echo ""
echo -e "${YELLOW}4. 测试数据库连接...${NC}"

cd "$INSTALL_DIR"
TEST_SCRIPT=$(cat <<'PYTHON'
import asyncio
from bot.config import settings
from bot.models.database import engine

async def test_db():
    try:
        async with engine.begin() as conn:
            await conn.execute("SELECT 1")
        print("Database connection OK")
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_db())
    exit(0 if result else 1)
PYTHON
)

if sudo -u "$SERVICE_USER" PYTHONPATH="$INSTALL_DIR/src" "$INSTALL_DIR/venv/bin/python" -c "$TEST_SCRIPT" 2>&1; then
    echo -e "${GREEN}✓ 数据库连接正常${NC}"
else
    echo -e "${YELLOW}⚠ 数据库连接测试失败 (首次启动时会自动初始化)${NC}"
fi

# 5. 启动服务
echo ""
echo -e "${YELLOW}5. 启动服务...${NC}"

systemctl start xiuxian-bot

sleep 5

if systemctl is-active --quiet xiuxian-bot; then
    echo -e "${GREEN}✓ 服务运行正常!${NC}"

    echo ""
    echo "查看日志:"
    journalctl -u xiuxian-bot -n 20 --no-pager
else
    echo -e "${RED}✗ 服务启动失败${NC}"
    echo ""
    echo "查看详细日志:"
    journalctl -u xiuxian-bot -n 30 --no-pager
    exit 1
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  依赖安装完成!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "服务状态:"
systemctl status xiuxian-bot --no-pager | head -10
echo ""
echo "持续查看日志:"
echo "  journalctl -u xiuxian-bot -f"
echo ""
