"""消息工具模块 - 提供自动删除消息功能"""
import asyncio
import logging
from typing import Optional, Union

from telegram import Message, InlineKeyboardMarkup

logger = logging.getLogger(__name__)

# 默认消息自动删除延迟（秒）
DEFAULT_DELETE_DELAY = 60


async def delete_message_after(message: Message, delay: int = DEFAULT_DELETE_DELAY) -> None:
    """延迟删除消息

    Args:
        message: 要删除的消息对象
        delay: 延迟时间（秒），默认60秒
    """
    try:
        await asyncio.sleep(delay)
        await message.delete()
        logger.debug(f"已删除消息 {message.message_id}")
    except Exception as e:
        # 消息可能已被手动删除或过期
        logger.debug(f"删除消息失败: {e}")


async def send_and_delete(
    original_message: Message,
    text: str,
    reply_markup: Optional[InlineKeyboardMarkup] = None,
    parse_mode: Optional[str] = None,
    delete_delay: int = DEFAULT_DELETE_DELAY,
    delete_original: bool = False,
) -> Message:
    """发送消息并在指定时间后自动删除

    Args:
        original_message: 原始消息对象（用于回复）
        text: 要发送的文本内容
        reply_markup: 内联键盘（可选）
        parse_mode: 解析模式，如 "Markdown" 或 "HTML"（可选）
        delete_delay: 删除延迟时间（秒），默认60秒
        delete_original: 是否同时删除原始消息，默认False

    Returns:
        发送的消息对象
    """
    # 发送新消息
    sent_message = await original_message.reply_text(
        text=text,
        reply_markup=reply_markup,
        parse_mode=parse_mode,
    )

    # 创建后台任务删除发送的消息
    asyncio.create_task(delete_message_after(sent_message, delete_delay))

    # 如果需要，同时删除原始消息
    if delete_original:
        asyncio.create_task(delete_message_after(original_message, delay=1))

    return sent_message


async def send_temp_message(
    chat_id: int,
    text: str,
    bot,
    reply_markup: Optional[InlineKeyboardMarkup] = None,
    parse_mode: Optional[str] = None,
    delete_delay: int = DEFAULT_DELETE_DELAY,
) -> Message:
    """直接发送临时消息到聊天（不是回复）

    Args:
        chat_id: 聊天ID
        text: 要发送的文本内容
        bot: Bot对象
        reply_markup: 内联键盘（可选）
        parse_mode: 解析模式（可选）
        delete_delay: 删除延迟时间（秒）

    Returns:
        发送的消息对象
    """
    sent_message = await bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=reply_markup,
        parse_mode=parse_mode,
    )

    # 创建后台任务删除消息
    asyncio.create_task(delete_message_after(sent_message, delete_delay))

    return sent_message


async def edit_and_delete(
    message: Message,
    text: str,
    reply_markup: Optional[InlineKeyboardMarkup] = None,
    parse_mode: Optional[str] = None,
    delete_delay: int = DEFAULT_DELETE_DELAY,
) -> Message:
    """编辑消息内容并在指定时间后删除

    Args:
        message: 要编辑的消息对象
        text: 新的文本内容
        reply_markup: 内联键盘（可选）
        parse_mode: 解析模式（可选）
        delete_delay: 删除延迟时间（秒）

    Returns:
        编辑后的消息对象
    """
    try:
        edited_message = await message.edit_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode=parse_mode,
        )

        # 创建后台任务删除消息
        asyncio.create_task(delete_message_after(edited_message, delete_delay))

        return edited_message
    except Exception as e:
        logger.warning(f"编辑消息失败: {e}")
        return message
