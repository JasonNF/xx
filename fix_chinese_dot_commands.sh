#!/bin/bash

#===============================================
# 中文命令方案: 使用 .命令 格式
# 例如: .修炼 .战斗 .背包
# 完美区分命令和普通聊天
#===============================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  配置中文命令支持 (.命令)${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

if [[ $EUID -ne 0 ]]; then
    echo -e "${RED}需要root权限${NC}"
    exit 1
fi

INSTALL_DIR="/opt/xiuxian-bot"
HANDLERS_DIR="$INSTALL_DIR/src/bot/handlers"

# 1. 备份
echo -e "${YELLOW}1. 备份处理器文件...${NC}"
BACKUP_DIR="/opt/xiuxian-bot-handlers-backup-$(date +%Y%m%d_%H%M%S)"
cp -r "$HANDLERS_DIR" "$BACKUP_DIR"
echo -e "${GREEN}✓ 已备份到 $BACKUP_DIR${NC}"

# 2. 创建中文命令处理模块
echo ""
echo -e "${YELLOW}2. 创建中文命令处理模块...${NC}"

cat > "$INSTALL_DIR/src/bot/handlers/chinese_commands.py" <<'PYEOF'
"""
中文命令支持模块
使用 .命令 格式 (例如: .修炼, .战斗, .背包)
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters

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


class ChineseCommandHandler:
    """中文命令处理器"""

    def __init__(self, application):
        self.application = application
        self.command_handlers = {}
        self._build_handler_map()

    def _build_handler_map(self):
        """构建命令处理器映射"""
        # 遍历所有已注册的处理器,找到CommandHandler
        from telegram.ext import CommandHandler

        for handler in self.application.handlers.get(0, []):
            if isinstance(handler, CommandHandler):
                for command in handler.commands:
                    self.command_handlers[command] = handler.callback

    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理中文命令"""
        if not update.message or not update.message.text:
            return

        text = update.message.text.strip()

        # 检查是否是中文命令
        if text not in CHINESE_COMMANDS:
            return

        # 获取对应的英文命令
        english_cmd = CHINESE_COMMANDS[text]

        logger.info(f"收到中文命令: {text} -> /{english_cmd}")

        # 查找对应的处理器
        if english_cmd in self.command_handlers:
            try:
                # 直接调用英文命令的处理器
                await self.command_handlers[english_cmd](update, context)
            except Exception as e:
                logger.error(f"执行命令 {english_cmd} 时出错: {e}")
                await update.message.reply_text(f"❌ 命令执行失败: {str(e)}")
        else:
            await update.message.reply_text(
                f"⚠️ 命令 {text} 暂未实现\n"
                f"请使用 .帮助 查看所有可用命令"
            )


def setup_chinese_commands(application):
    """注册中文命令处理器"""

    # 创建处理器实例
    handler = ChineseCommandHandler(application)

    # 创建文本过滤器 - 匹配所有 .开头的中文命令
    commands_list = list(CHINESE_COMMANDS.keys())
    pattern = "^(" + "|".join([cmd.replace(".", r"\.") for cmd in commands_list]) + ")$"

    text_filter = filters.TEXT & filters.Regex(pattern)

    # 添加MessageHandler
    message_handler = MessageHandler(text_filter, handler.handle)
    application.add_handler(message_handler, group=1)

    logger.info(f"✅ 已加载 {len(commands_list)} 个中文命令")

    return len(commands_list)
PYEOF

chown xiuxian:xiuxian "$INSTALL_DIR/src/bot/handlers/chinese_commands.py"
echo -e "${GREEN}✓ 中文命令模块已创建${NC}"

# 3. 修改main.py集成中文命令
echo ""
echo -e "${YELLOW}3. 集成中文命令到主程序...${NC}"

MAIN_FILE="$INSTALL_DIR/src/bot/main.py"

# 检查是否已经添加过
if grep -q "from bot.handlers.chinese_commands import setup_chinese_commands" "$MAIN_FILE"; then
    echo -e "${BLUE}ℹ 中文命令支持已经集成${NC}"
else
    # 找到 application.run_polling() 之前的位置
    # 在所有handler加载完成后添加中文命令支持

    # 创建临时文件
    TEMP_FILE=$(mktemp)

    # 读取文件并在适当位置插入代码
    awk '
    /application\.run_polling/ && !inserted {
        print "    # 设置中文命令支持 (.命令格式)"
        print "    try:"
        print "        from bot.handlers.chinese_commands import setup_chinese_commands"
        print "        cmd_count = setup_chinese_commands(application)"
        print "        logger.info(f\"✅ 已加载 {cmd_count} 个中文命令支持 (使用 .命令 格式)\")"
        print "    except Exception as e:"
        print "        logger.warning(f\"⚠️ 中文命令加载失败: {e}\")"
        print ""
        inserted = 1
    }
    { print }
    ' "$MAIN_FILE" > "$TEMP_FILE"

    # 替换原文件
    mv "$TEMP_FILE" "$MAIN_FILE"
    chown xiuxian:xiuxian "$MAIN_FILE"

    echo -e "${GREEN}✓ 已集成到主程序${NC}"
fi

# 4. 移除原有的中文CommandHandler
echo ""
echo -e "${YELLOW}4. 移除原有的中文CommandHandler...${NC}"

CHINESE_CMD_LIST=(
    "检测灵根" "个人信息" "帮助" "状态"
    "修炼" "收功" "取消修炼" "突破"
    "战斗" "挑战" "查看怪物"
    "技能列表" "学习技能" "装备技能"
    "背包" "使用" "装备" "卸下"
    "商店" "购买"
    "宗门" "创建宗门" "加入宗门" "离开宗门" "宗门信息" "宗门成员" "宗门贡献"
    "排行榜" "境界榜" "战力榜"
    "签到" "每日签到"
    "境界信息" "灵根信息"
    "市场" "出售" "拍卖"
    "炼丹" "丹方"
    "炼器" "炼器配方"
    "阵法" "符箓"
    "灵兽" "捕捉"
    "洞府" "神识"
    "任务" "接取任务" "完成任务"
    "成就"
    "秘境" "探索"
    "竞技场" "世界BOSS" "宗门战"
    "积分商城" "改名" "寿元" "金丹品质"
    "功法" "修炼功法"
    "长老" "宗门排行"
)

count=0
total=${#CHINESE_CMD_LIST[@]}
processed=0

for cmd in "${CHINESE_CMD_LIST[@]}"; do
    ((processed++))
    echo -ne "  处理中... [$processed/$total]\r"

    # 检查是否存在该命令
    found=$(grep -r "CommandHandler(\"$cmd\"" "$HANDLERS_DIR" 2>/dev/null | grep -v chinese_commands.py | wc -l)

    if [ "$found" -gt 0 ]; then
        # 删除该命令
        find "$HANDLERS_DIR" -name "*.py" -not -name "chinese_commands.py" -type f -exec sed -i "/CommandHandler(\"$cmd\"/d" {} \; 2>/dev/null || true
        ((count++))
    fi
done

echo -ne "\n"

if [ $count -eq 0 ]; then
    echo -e "${BLUE}ℹ 没有需要移除的中文CommandHandler${NC}"
else
    echo -e "${GREEN}✓ 已移除 $count 个旧的中文CommandHandler${NC}"
fi

# 5. 修正权限
echo ""
echo -e "${YELLOW}5. 修正文件权限...${NC}"
chown -R xiuxian:xiuxian "$HANDLERS_DIR"
chown -R xiuxian:xiuxian "$INSTALL_DIR/src/bot/"
echo -e "${GREEN}✓ 权限已修正${NC}"

# 6. 重启服务
echo ""
echo -e "${YELLOW}6. 重启服务...${NC}"

systemctl restart xiuxian-bot

sleep 5

if systemctl is-active --quiet xiuxian-bot; then
    echo -e "${GREEN}✓ 服务运行正常!${NC}"

    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  部署完成!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "✅ Bot现在支持中文命令了!"
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}命令格式: .命令 (注意前面的点)${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "🎮 基础命令:"
    echo "  .开始          开始游戏/检测灵根"
    echo "  .帮助          查看帮助"
    echo "  .状态          查看个人信息"
    echo ""
    echo "⚡ 修炼命令:"
    echo "  .修炼          开始修炼"
    echo "  .收功          收功"
    echo "  .突破          突破境界"
    echo ""
    echo "⚔️  战斗命令:"
    echo "  .战斗          进入战斗"
    echo "  .挑战          挑战其他玩家"
    echo "  .怪物          查看怪物列表"
    echo ""
    echo "🎒 物品命令:"
    echo "  .背包          查看背包"
    echo "  .装备          装备物品"
    echo "  .使用          使用物品"
    echo ""
    echo "🏪 商店命令:"
    echo "  .商店          打开商店"
    echo "  .购买          购买物品"
    echo ""
    echo "🏯 宗门命令:"
    echo "  .宗门          宗门系统"
    echo "  .加入          加入宗门"
    echo "  .贡献          宗门贡献"
    echo ""
    echo "🏆 其他命令:"
    echo "  .排行          查看排行榜"
    echo "  .签到          每日签到"
    echo "  .技能          技能列表"
    echo "  .市场          交易市场"
    echo "  .炼丹          炼丹系统"
    echo "  .任务          任务系统"
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "💡 提示: 英文命令(/start, /help等)仍然可用"
    echo ""

else
    echo -e "${RED}✗ 服务启动失败${NC}"
    echo ""
    echo "查看错误日志:"
    journalctl -u xiuxian-bot -n 30 --no-pager
    exit 1
fi

echo "📊 查看实时日志:"
echo "  journalctl -u xiuxian-bot -f"
echo ""
