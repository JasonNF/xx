#!/bin/bash

#===============================================
# 诊断中文命令模块问题
#===============================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  诊断中文命令模块${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

echo -e "${YELLOW}1. 检查start.py的CommandHandler注册...${NC}"
echo ""
grep "CommandHandler" /opt/xiuxian-bot/src/bot/handlers/start.py | grep -v "^#" | grep -v "import"
echo ""

echo -e "${YELLOW}2. 查看register_handlers函数...${NC}"
echo ""
sed -n '208,220p' /opt/xiuxian-bot/src/bot/handlers/start.py
echo ""

echo -e "${YELLOW}3. 测试中文命令模块的逻辑...${NC}"
echo ""

sudo -u xiuxian PYTHONPATH=/opt/xiuxian-bot/src /opt/xiuxian-bot/venv/bin/python << 'PYEOF'
import sys
import os

# 设置环境变量
os.environ['BOT_TOKEN'] = 'test'
os.environ['DATABASE_URL'] = 'sqlite+aiosqlite:///test.db'

try:
    # 导入中文命令模块
    from bot.handlers.chinese_commands import ChineseCommandHandler, CHINESE_COMMANDS

    print(f"✓ 中文命令模块导入成功")
    print(f"✓ 中文命令数量: {len(CHINESE_COMMANDS)}")

    # 显示部分命令映射
    print("\n中文命令映射示例:")
    for i, (ch, en) in enumerate(list(CHINESE_COMMANDS.items())[:5]):
        print(f"  {ch} -> {en}")

    # 测试ChineseCommandHandler类
    print("\n✓ ChineseCommandHandler类存在")
    print(f"  方法: {[m for m in dir(ChineseCommandHandler) if not m.startswith('_')]}")

except Exception as e:
    print(f"✗ 错误: {e}")
    import traceback
    traceback.print_exc()

PYEOF

echo ""
echo -e "${YELLOW}4. 查看中文命令模块的完整代码...${NC}"
echo ""
echo "ChineseCommandHandler类定义:"
sed -n '156,200p' /opt/xiuxian-bot/src/bot/handlers/chinese_commands.py

echo ""
echo -e "${YELLOW}5. 检查main.py中文命令的集成...${NC}"
echo ""
grep -A 5 "setup_chinese_commands" /opt/xiuxian-bot/src/bot/main.py

echo ""
