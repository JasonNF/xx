#!/bin/bash

#===============================================
# 修复权限和依赖问题
#===============================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  修复权限和依赖${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

INSTALL_DIR="/opt/xiuxian-bot"
SERVICE_USER="xiuxian"

# 1. 修复PostgreSQL客户端证书权限
echo -e "${YELLOW}1. 修复PostgreSQL权限问题...${NC}"

PG_DIR="/home/$SERVICE_USER/.postgresql"

if [ -d "$PG_DIR" ]; then
    echo "  发现PostgreSQL配置目录: $PG_DIR"

    # 修正所有权
    chown -R "$SERVICE_USER:$SERVICE_USER" "$PG_DIR"

    # 修正权限 (密钥文件需要0600)
    if [ -f "$PG_DIR/postgresql.key" ]; then
        chmod 600 "$PG_DIR/postgresql.key"
        echo "  ✓ 已修正 postgresql.key 权限"
    fi

    if [ -f "$PG_DIR/postgresql.crt" ]; then
        chmod 600 "$PG_DIR/postgresql.crt"
        echo "  ✓ 已修正 postgresql.crt 权限"
    fi

    echo -e "${GREEN}✓ PostgreSQL权限已修正${NC}"
else
    echo -e "${YELLOW}  ℹ PostgreSQL配置目录不存在,跳过${NC}"
fi

# 2. 安装缺失的Python依赖
echo ""
echo -e "${YELLOW}2. 安装缺失的依赖...${NC}"

cd "$INSTALL_DIR"

# 检查并安装apscheduler
if ! sudo -u "$SERVICE_USER" "$INSTALL_DIR/venv/bin/python" -c "import apscheduler" 2>/dev/null; then
    echo "  正在安装 apscheduler..."
    sudo -u "$SERVICE_USER" "$INSTALL_DIR/venv/bin/pip" install apscheduler -q
    echo -e "${GREEN}  ✓ apscheduler已安装${NC}"
else
    echo -e "${GREEN}  ✓ apscheduler已存在${NC}"
fi

# 检查其他可能缺失的依赖
DEPS=(
    "telegram"
    "sqlalchemy"
    "asyncpg"
    "aiosqlite"
    "pydantic"
    "pydantic_settings"
    "python-dotenv"
)

echo ""
echo "  验证关键依赖:"
missing=0
for dep in "${DEPS[@]}"; do
    if sudo -u "$SERVICE_USER" "$INSTALL_DIR/venv/bin/python" -c "import $dep" 2>/dev/null; then
        echo "    ✓ $dep"
    else
        echo "    ✗ $dep (缺失)"
        ((missing++))
    fi
done

if [ $missing -gt 0 ]; then
    echo ""
    echo -e "${YELLOW}  发现 $missing 个缺失依赖,正在安装...${NC}"

    # 尝试从requirements.txt安装
    if [ -f "$INSTALL_DIR/requirements.txt" ]; then
        sudo -u "$SERVICE_USER" "$INSTALL_DIR/venv/bin/pip" install -r "$INSTALL_DIR/requirements.txt" -q
        echo -e "${GREEN}  ✓ 依赖已安装${NC}"
    else
        echo -e "${YELLOW}  ⚠ requirements.txt不存在,请手动安装${NC}"
    fi
else
    echo -e "${GREEN}✓ 所有依赖已就绪${NC}"
fi

# 3. 测试数据库连接
echo ""
echo -e "${YELLOW}3. 测试数据库连接...${NC}"

TEST_SCRIPT=$(cat <<'PYEOF'
import asyncio
import sys
import os

# 添加src到路径
sys.path.insert(0, '/opt/xiuxian-bot/src')

async def test():
    try:
        from bot.config import settings
        print(f"✓ 配置加载成功")
        print(f"  DATABASE_URL: {settings.DATABASE_URL[:30]}...")

        from bot.models.database import engine
        async with engine.begin() as conn:
            await conn.execute("SELECT 1")
        print(f"✓ 数据库连接成功")
        return True
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False

if __name__ == '__main__':
    result = asyncio.run(test())
    sys.exit(0 if result else 1)
PYEOF
)

if sudo -u "$SERVICE_USER" PYTHONPATH="$INSTALL_DIR/src" "$INSTALL_DIR/venv/bin/python" -c "$TEST_SCRIPT" 2>&1; then
    echo -e "${GREEN}✓ 数据库测试通过${NC}"
else
    echo -e "${YELLOW}⚠ 数据库测试失败 (首次启动时会自动初始化)${NC}"
fi

# 4. 重启服务
echo ""
echo -e "${YELLOW}4. 重启服务...${NC}"

systemctl restart xiuxian-bot

sleep 5

if systemctl is-active --quiet xiuxian-bot; then
    echo -e "${GREEN}✓ 服务运行正常!${NC}"

    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  修复完成!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "✅ Bot成功启动!"
    echo ""
    echo "🎮 中文命令格式: .命令"
    echo "   .开始  .修炼  .战斗  .背包  .商店  .宗门"
    echo ""
    echo "💡 英文命令格式: /命令"
    echo "   /start /cultivate /battle /bag /shop /sect"
    echo ""

    echo -e "${YELLOW}最近日志:${NC}"
    journalctl -u xiuxian-bot -n 20 --no-pager

else
    echo -e "${RED}✗ 服务启动失败${NC}"
    echo ""
    echo "详细日志:"
    journalctl -u xiuxian-bot -n 50 --no-pager
    exit 1
fi

echo ""
echo "📊 实时监控:"
echo "  journalctl -u xiuxian-bot -f"
echo ""
