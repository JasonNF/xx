#!/bin/bash

#===============================================
# 添加消息自动删除功能（15秒后删除）
#===============================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  添加消息自动删除功能${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

HANDLERS_DIR="/opt/xiuxian-bot/src/bot/handlers"
UTILS_FILE="/opt/xiuxian-bot/src/bot/utils/message_utils.py"

echo -e "${YELLOW}1. 创建消息工具模块...${NC}"

# 创建utils目录（如果不存在）
sudo -u xiuxian mkdir -p /opt/xiuxian-bot/src/bot/utils

# 创建message_utils.py
sudo -u xiuxian cat > "$UTILS_FILE" << 'PYEOF'
"""
消息工具模块 - 处理消息自动删除等功能
"""
import asyncio
import logging
from typing import Optional
from telegram import Message

logger = logging.getLogger(__name__)

AUTO_DELETE_SECONDS = 15  # 消息自动删除时间（秒）


async def send_and_delete(message: Message, text: str, delete_after: int = AUTO_DELETE_SECONDS, **kwargs) -> Optional[Message]:
    """
    发送消息并在指定时间后自动删除

    Args:
        message: 用户的原始消息对象
        text: 要发送的回复文本
        delete_after: 多少秒后删除消息（默认15秒）
        **kwargs: 传递给reply_text的其他参数（如parse_mode等）

    Returns:
        发送的消息对象，如果发送失败则返回None
    """
    try:
        # 发送回复消息
        bot_message = await message.reply_text(text, **kwargs)

        # 创建异步任务来删除消息
        asyncio.create_task(_delete_messages_after_delay(
            user_message=message,
            bot_message=bot_message,
            delay=delete_after
        ))

        return bot_message

    except Exception as e:
        logger.error(f"发送消息失败: {e}", exc_info=True)
        return None


async def _delete_messages_after_delay(user_message: Message, bot_message: Message, delay: int):
    """
    延迟删除用户消息和bot消息

    Args:
        user_message: 用户的消息
        bot_message: bot的回复消息
        delay: 延迟时间（秒）
    """
    try:
        # 等待指定时间
        await asyncio.sleep(delay)

        # 删除bot的回复
        try:
            await bot_message.delete()
            logger.debug(f"已删除bot消息 {bot_message.message_id}")
        except Exception as e:
            logger.warning(f"删除bot消息失败 {bot_message.message_id}: {e}")

        # 删除用户的命令消息
        try:
            await user_message.delete()
            logger.debug(f"已删除用户消息 {user_message.message_id}")
        except Exception as e:
            logger.warning(f"删除用户消息失败 {user_message.message_id}: {e}")

    except Exception as e:
        logger.error(f"消息自动删除任务失败: {e}", exc_info=True)


async def delete_message_after(message: Message, delay: int = AUTO_DELETE_SECONDS):
    """
    单独删除某条消息

    Args:
        message: 要删除的消息
        delay: 延迟时间（秒）
    """
    try:
        await asyncio.sleep(delay)
        await message.delete()
        logger.debug(f"已删除消息 {message.message_id}")
    except Exception as e:
        logger.warning(f"删除消息失败 {message.message_id}: {e}")
PYEOF

echo -e "${GREEN}✓ 已创建message_utils.py${NC}"

echo ""
echo -e "${YELLOW}2. 修改start.py使用自动删除功能...${NC}"

sudo -u xiuxian /opt/xiuxian-bot/venv/bin/python3 << 'PYEOF'
import re

start_file = '/opt/xiuxian-bot/src/bot/handlers/start.py'

with open(start_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 添加导入
if 'from bot.utils.message_utils import send_and_delete' not in content:
    # 在其他import之后添加
    import_pattern = r'(from bot\.database import get_db)'
    content = re.sub(
        import_pattern,
        r'\1\nfrom bot.utils.message_utils import send_and_delete',
        content
    )

# 修改detect_spirit_root_command函数
# 将所有的 await update.message.reply_text(...) 替换为 await send_and_delete(update.message, ...)
old_pattern = r'await update\.message\.reply_text\((.*?), parse_mode="Markdown"\)'
new_pattern = r'await send_and_delete(update.message, \1, parse_mode="Markdown")'
content = re.sub(old_pattern, new_pattern, content, flags=re.DOTALL)

# 处理没有parse_mode的情况
old_pattern2 = r'await update\.message\.reply_text\((.*?)\)(?!\))'
new_pattern2 = r'await send_and_delete(update.message, \1)'
content = re.sub(old_pattern2, new_pattern2, content)

with open(start_file, 'w', encoding='utf-8') as f:
    f.write(content)

print('✓ 已修改detect_spirit_root_command使用自动删除')
PYEOF

echo -e "${GREEN}✓ start.py修改完成${NC}"

echo ""
echo -e "${YELLOW}3. 修改chinese_commands.py...${NC}"

sudo -u xiuxian /opt/xiuxian-bot/venv/bin/python3 << 'PYEOF'
import re

chinese_cmd_file = '/opt/xiuxian-bot/src/bot/handlers/chinese_commands.py'

with open(chinese_cmd_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 添加导入
if 'from bot.utils.message_utils import send_and_delete' not in content:
    import_pattern = r'(import logging)'
    content = re.sub(
        import_pattern,
        r'\1\nfrom bot.utils.message_utils import send_and_delete',
        content
    )

# 修改handle_chinese_command中的reply_text
content = re.sub(
    r'await update\.message\.reply_text\(',
    r'await send_and_delete(update.message, ',
    content
)

with open(chinese_cmd_file, 'w', encoding='utf-8') as f:
    f.write(content)

print('✓ 已修改chinese_commands.py使用自动删除')
PYEOF

echo -e "${GREEN}✓ chinese_commands.py修改完成${NC}"

echo ""
echo -e "${YELLOW}4. 创建__init__.py...${NC}"

sudo -u xiuxian cat > "/opt/xiuxian-bot/src/bot/utils/__init__.py" << 'PYEOF'
"""Bot工具模块"""
from .message_utils import send_and_delete, delete_message_after, AUTO_DELETE_SECONDS

__all__ = ['send_and_delete', 'delete_message_after', 'AUTO_DELETE_SECONDS']
PYEOF

echo -e "${GREEN}✓ 已创建__init__.py${NC}"

echo ""
echo -e "${YELLOW}5. 验证文件结构...${NC}"
ls -la /opt/xiuxian-bot/src/bot/utils/

echo ""
echo -e "${YELLOW}6. 重启服务...${NC}"

systemctl restart xiuxian-bot

sleep 5

if systemctl is-active --quiet xiuxian-bot; then
    echo -e "${GREEN}✓ 服务运行正常！${NC}"

    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  自动删除功能添加成功！${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "📝 功能说明:"
    echo "  • 用户发送的命令消息：15秒后自动删除"
    echo "  • Bot回复的消息：15秒后自动删除"
    echo "  • 保持群组/频道整洁"
    echo ""
    echo "🎮 测试命令:"
    echo "  /start 或 .开始 - 观察15秒后消息自动消失"
    echo "  /info 或 .状态 - 观察15秒后消息自动消失"
    echo ""
    echo "⚙️  修改删除时间:"
    echo "  编辑 /opt/xiuxian-bot/src/bot/utils/message_utils.py"
    echo "  修改 AUTO_DELETE_SECONDS = 15 为其他值"
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
