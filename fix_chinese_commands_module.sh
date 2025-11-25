#!/bin/bash

#===============================================
# 修复中文命令模块的处理器查找逻辑
#===============================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  修复中文命令模块${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

CHINESE_CMD_FILE="/opt/xiuxian-bot/src/bot/handlers/chinese_commands.py"

echo -e "${YELLOW}1. 备份当前文件...${NC}"
cp "$CHINESE_CMD_FILE" "${CHINESE_CMD_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
echo -e "${GREEN}✓ 已备份${NC}"

echo ""
echo -e "${YELLOW}2. 重写中文命令模块...${NC}"

cat > "$CHINESE_CMD_FILE" << 'PYEOF'
"""
中文命令支持模块
使用 .命令 格式 (例如: .修炼, .战斗, .背包)
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters, CommandHandler

logger = logging.getLogger(__name__)

# 中文命令映射表 (.开头)
CHINESE_COMMANDS = {
    # 基础命令
    ".检测灵根": "start",
    ".开始": "start",
    ".帮助": "help",
    ".个人信息": "info",
    ".状态": "info",

    # 修炼相关
    ".修炼": "cultivate",
    ".收功": "finish",
    ".取消修炼": "cancel",
    ".突破": "breakthrough",

    # 战斗相关
    ".战斗": "battle",
    ".挑战": "challenge",
    ".查看怪物": "monsters",
    ".怪物": "monsters",

    # 技能相关
    ".技能列表": "skills",
    ".技能": "skills",
    ".学习技能": "learn",
    ".学习": "learn",
    ".装备技能": "equip_skill",

    # 物品相关
    ".背包": "bag",
    ".使用": "use",
    ".装备": "equip",
    ".卸下": "unequip",

    # 商店相关
    ".商店": "shop",
    ".购买": "buy",

    # 宗门相关
    ".宗门": "sect",
    ".创建宗门": "create_sect",
    ".加入宗门": "join_sect",
    ".加入": "join_sect",
    ".离开宗门": "leave_sect",
    ".离开": "leave_sect",
    ".宗门信息": "sect_info",
    ".宗门成员": "sect_members",
    ".成员": "sect_members",
    ".宗门贡献": "contribute",
    ".贡献": "contribute",

    # 排行榜
    ".排行榜": "rank",
    ".排行": "rank",
    ".境界榜": "rank_realm",
    ".战力榜": "rank_power",

    # 签到
    ".签到": "signin",
    ".每日签到": "daily",

    # 其他功能
    ".境界信息": "realm",
    ".境界": "realm",
    ".灵根信息": "spirit_root",
    ".灵根": "spirit_root",
    ".市场": "market",
    ".出售": "sell",
    ".拍卖": "auction",
    ".炼丹": "alchemy",
    ".丹方": "recipes",
    ".炼器": "refinery",
    ".炼器配方": "refine_recipes",
    ".阵法": "formation",
    ".符箓": "talisman",
    ".灵兽": "pet",
    ".宠物": "pet",
    ".捕捉": "catch",
    ".洞府": "cave",
    ".神识": "divine",
    ".任务": "quest",
    ".接取任务": "accept_quest",
    ".接取": "accept_quest",
    ".完成任务": "complete_quest",
    ".完成": "complete_quest",
    ".成就": "achievement",
    ".秘境": "adventure",
    ".探索": "explore",
    ".竞技场": "arena",
    ".世界BOSS": "worldboss",
    ".BOSS": "worldboss",
    ".宗门战": "sect_war",
    ".积分商城": "credits",
    ".积分": "credits",
    ".改名": "rename",
    ".寿元": "lifespan",
    ".金丹品质": "core",
    ".金丹": "core",
    ".功法": "method",
    ".修炼功法": "practice",
    ".长老": "elder",
    ".宗门排行": "sect_rank",
}


async def handle_chinese_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理中文命令 - 直接转换为英文命令并重新处理"""
    if not update.message or not update.message.text:
        return

    text = update.message.text.strip()

    # 检查是否是中文命令
    if text not in CHINESE_COMMANDS:
        return

    # 获取对应的英文命令
    english_cmd = CHINESE_COMMANDS[text]

    logger.info(f"收到中文命令: {text} -> /{english_cmd}")

    # 创建新的消息副本,将文本改为英文命令
    # 然后让Telegram重新路由这个命令
    original_text = update.message.text
    update.message.text = f"/{english_cmd}"

    try:
        # 直接通过application处理这个命令
        # 获取application实例并处理更新
        application = context.application

        # 重新处理这个update
        await application.process_update(update)

    except Exception as e:
        logger.error(f"执行命令 {english_cmd} 时出错: {e}")
        await update.message.reply_text(
            f"⚠️ 命令执行失败\n"
            f"请使用 .帮助 查看所有可用命令"
        )
    finally:
        # 恢复原始文本
        update.message.text = original_text


def setup_chinese_commands(application):
    """注册中文命令处理器"""

    # 创建文本过滤器 - 匹配所有 .开头的中文命令
    commands_list = list(CHINESE_COMMANDS.keys())
    pattern = "^(" + "|".join([cmd.replace(".", r"\.") for cmd in commands_list]) + ")$"

    text_filter = filters.TEXT & filters.Regex(pattern)

    # 添加MessageHandler - 设置group=1以便在其他handler之前处理
    message_handler = MessageHandler(text_filter, handle_chinese_command)
    application.add_handler(message_handler, group=-1)

    logger.info(f"✅ 已加载 {len(commands_list)} 个中文命令")

    return len(commands_list)
PYEOF

chown xiuxian:xiuxian "$CHINESE_CMD_FILE"

echo -e "${GREEN}✓ 中文命令模块已重写${NC}"

echo ""
echo -e "${YELLOW}3. 重启服务...${NC}"

systemctl restart xiuxian-bot

sleep 5

if systemctl is-active --quiet xiuxian-bot; then
    echo -e "${GREEN}✓ 服务运行正常!${NC}"

    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  修复完成!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "请在Telegram中测试命令:"
    echo "  .开始"
    echo "  /start"
    echo "  .状态"
    echo ""

    echo "最近日志:"
    journalctl -u xiuxian-bot -n 20 --no-pager | tail -15

else
    echo -e "${RED}✗ 服务启动失败${NC}"
    journalctl -u xiuxian-bot -n 30 --no-pager
    exit 1
fi

echo ""
echo "实时监控: journalctl -u xiuxian-bot -f"
echo ""
