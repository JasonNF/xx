#!/bin/bash

#===============================================
# 修复中文命令的异步问题
#===============================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  修复中文命令异步问题${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

CHINESE_CMD_FILE="/opt/xiuxian-bot/src/bot/handlers/chinese_commands.py"

echo -e "${YELLOW}1. 备份chinese_commands.py...${NC}"
cp "$CHINESE_CMD_FILE" "${CHINESE_CMD_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
echo -e "${GREEN}✓ 已备份${NC}"

echo ""
echo -e "${YELLOW}2. 修复handle_chinese_command函数...${NC}"

sudo -u xiuxian /opt/xiuxian-bot/venv/bin/python3 << 'PYEOF'
import re

chinese_cmd_file = '/opt/xiuxian-bot/src/bot/handlers/chinese_commands.py'

with open(chinese_cmd_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 新的handle_chinese_command实现
new_implementation = '''async def handle_chinese_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理中文命令 - 修改消息文本为英文命令并让application重新处理"""
    if not update.message or not update.message.text:
        return

    text = update.message.text.strip()

    # 检查是否是中文命令
    if text not in CHINESE_COMMANDS:
        return

    # 获取对应的英文命令
    english_cmd = CHINESE_COMMANDS[text]

    logger.info(f"收到中文命令: {text} -> /{english_cmd}")

    try:
        # 修改消息文本为英文命令格式
        # 创建一个新的Update对象，文本改为英文命令
        import copy
        new_update = copy.copy(update)
        new_message = copy.copy(update.message)
        new_message.text = f"/{english_cmd}"
        new_update.message = new_message
        
        # 让application重新处理这个update
        await context.application.process_update(new_update)

    except Exception as e:
        logger.error(f"执行命令 {english_cmd} 时出错: {e}", exc_info=True)
        await update.message.reply_text(
            f"⚠️ 命令执行失败\\n"
            f"请使用 .帮助 查看所有可用命令"
        )
'''

# 找到并替换handle_chinese_command函数
pattern = r'async def handle_chinese_command\(.*?\):.*?(?=\n(?:async )?def |$)'
content = re.sub(pattern, new_implementation, content, flags=re.DOTALL)

with open(chinese_cmd_file, 'w', encoding='utf-8') as f:
    f.write(content)

print('✓ 已修复异步问题')
print('  - 使用copy.copy创建新的Update对象')
print('  - 修改消息文本为英文命令')
print('  - 让application.process_update重新处理')
PYEOF

echo -e "${GREEN}✓ 修复完成${NC}"

echo ""
echo -e "${YELLOW}3. 重启服务...${NC}"

systemctl restart xiuxian-bot

sleep 5

if systemctl is-active --quiet xiuxian-bot; then
    echo -e "${GREEN}✓ 服务运行正常!${NC}"

    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  修复成功!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "🎮 测试命令:"
    echo "  中文: .开始 .状态 .修炼"
    echo "  英文: /start /info /cultivate"
    echo ""

    echo "最近日志:"
    journalctl -u xiuxian-bot -n 15 --no-pager

else
    echo -e "${RED}✗ 服务启动失败${NC}"
    journalctl -u xiuxian-bot -n 30 --no-pager
    exit 1
fi

echo ""
echo "📊 实时监控: journalctl -u xiuxian-bot -f"
echo ""
