#!/bin/bash

# 修仙世界 Telegram Bot 启动脚本
# 使用方法: ./start.sh

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo "======================================="
echo "  修仙世界 Telegram Bot 启动脚本"
echo "  版本: v1.0.0"
echo "======================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查Python版本
echo "🔍 检查环境..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ 错误: 未找到 python3${NC}"
    echo "  请先安装 Python 3.11+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✓${NC} Python 版本: $PYTHON_VERSION"

# 检查.env文件
if [ ! -f ".env" ]; then
    echo -e "${RED}✗ 错误: .env 文件不存在${NC}"
    echo "  请执行以下步骤:"
    echo "  1. cp .env.example .env"
    echo "  2. 编辑 .env 文件，填入你的 BOT_TOKEN"
    exit 1
fi
echo -e "${GREEN}✓${NC} 配置文件存在"

# 检查BOT_TOKEN是否配置
BOT_TOKEN=$(grep "^BOT_TOKEN=" .env | cut -d '=' -f2)
if [ -z "$BOT_TOKEN" ] || [ "$BOT_TOKEN" = "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11" ]; then
    echo -e "${YELLOW}⚠ 警告: BOT_TOKEN 未配置或使用示例值${NC}"
    echo "  请编辑 .env 文件，填入真实的 Bot Token"
    echo "  如何获取: https://t.me/BotFather"
    read -p "是否继续？ (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 检查数据库
if [ ! -f "data/xiuxian.db" ]; then
    echo -e "${YELLOW}⚠ 警告: 数据库文件不存在${NC}"
    echo "  将在首次启动时自动创建"
else
    echo -e "${GREEN}✓${NC} 数据库文件存在"

    # 检查数据完整性
    SKILL_COUNT=$(sqlite3 data/xiuxian.db "SELECT COUNT(*) FROM skills;" 2>/dev/null)
    MONSTER_COUNT=$(sqlite3 data/xiuxian.db "SELECT COUNT(*) FROM monsters;" 2>/dev/null)
    ITEM_COUNT=$(sqlite3 data/xiuxian.db "SELECT COUNT(*) FROM items;" 2>/dev/null)

    if [ "$SKILL_COUNT" = "0" ] || [ "$MONSTER_COUNT" = "0" ] || [ "$ITEM_COUNT" = "0" ]; then
        echo -e "${YELLOW}⚠ 警告: 游戏数据不完整${NC}"
        echo "  技能: $SKILL_COUNT, 怪物: $MONSTER_COUNT, 物品: $ITEM_COUNT"
        echo "  建议执行: cd data && ./import_all_data.sh"
    else
        echo -e "${GREEN}✓${NC} 游戏数据完整 (技能:$SKILL_COUNT 怪物:$MONSTER_COUNT 物品:$ITEM_COUNT)"
    fi
fi

# 检查依赖
echo ""
echo "🔍 检查依赖..."
if [ -f "requirements.txt" ]; then
    if python3 -c "import telegram" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} 依赖包已安装"
    else
        echo -e "${YELLOW}⚠ 警告: 缺少依赖包${NC}"
        echo "  正在安装依赖..."
        pip3 install -r requirements.txt
    fi
fi

# 激活虚拟环境（如果存在）
if [ -d "venv" ]; then
    echo ""
    echo "🔧 激活虚拟环境..."
    source venv/bin/activate
    echo -e "${GREEN}✓${NC} 虚拟环境已激活"
fi

# 创建日志目录
mkdir -p data/logs

echo ""
echo "======================================="
echo "  ✨ 正在启动 Bot..."
echo "======================================="
echo ""
echo "提示:"
echo "  - 按 Ctrl+C 可以停止 Bot"
echo "  - 日志文件: data/logs/xiuxian.log"
echo "  - 在 Telegram 中发送 /start 测试"
echo ""

# 启动Bot
python3 -m src.bot.main

# 退出时的提示
echo ""
echo "======================================="
echo "  Bot 已停止"
echo "======================================="
