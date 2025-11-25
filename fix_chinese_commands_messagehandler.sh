#!/bin/bash

#===============================================
# 修复方案: 使用MessageHandler支持中文命令
# 将中文CommandHandler改为MessageHandler+filters.Text
#===============================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  修复中文命令支持${NC}"
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

# 2. 创建统一的中文命令处理器
echo ""
echo -e "${YELLOW}2. 创建中文命令处理模块...${NC}"

cat > "$INSTALL_DIR/src/bot/handlers/chinese_commands.py" <<'EOF'
"""
中文命令支持模块
使用MessageHandler + 文本匹配来支持中文命令
"""
from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters

# 中文命令到英文命令的映射
COMMAND_MAP = {
    # 基础命令
    "检测灵根": "start",
    "开始": "start",
    "帮助": "help",
    "个人信息": "info",
    "状态": "info",

    # 修炼相关
    "修炼": "cultivate",
    "收功": "finish",
    "取消修炼": "cancel",
    "突破": "breakthrough",

    # 战斗相关
    "战斗": "battle",
    "挑战": "challenge",
    "查看怪物": "monsters",

    # 技能相关
    "技能列表": "skills",
    "学习技能": "learn",
    "装备技能": "equip_skill",

    # 物品相关
    "背包": "bag",
    "使用": "use",
    "装备": "equip",
    "卸下": "unequip",

    # 商店相关
    "商店": "shop",
    "购买": "buy",

    # 宗门相关
    "宗门": "sect",
    "创建宗门": "create_sect",
    "加入宗门": "join_sect",
    "离开宗门": "leave_sect",
    "宗门信息": "sect_info",
    "宗门成员": "sect_members",
    "宗门贡献": "contribute",

    # 排行榜
    "排行榜": "rank",
    "境界榜": "rank_realm",
    "战力榜": "rank_power",

    # 签到
    "签到": "signin",
    "每日签到": "daily",

    # 其他功能
    "境界信息": "realm",
    "灵根信息": "spirit_root",
    "市场": "market",
    "出售": "sell",
    "拍卖": "auction",
    "炼丹": "alchemy",
    "丹方": "recipes",
    "炼器": "refinery",
    "炼器配方": "refine_recipes",
    "阵法": "formation",
    "符箓": "talisman",
    "灵兽": "pet",
    "捕捉": "catch",
    "洞府": "cave",
    "神识": "divine",
    "任务": "quest",
    "接取任务": "accept_quest",
    "完成任务": "complete_quest",
    "成就": "achievement",
    "秘境": "adventure",
    "探索": "explore",
    "竞技场": "arena",
    "世界BOSS": "worldboss",
    "宗门战": "sect_war",
    "积分商城": "credits",
    "改名": "rename",
    "寿元": "lifespan",
    "金丹品质": "core",
    "功法": "method",
    "修炼功法": "practice",
    "长老": "elder",
    "宗门排行": "sect_rank",
}


async def handle_chinese_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理中文命令"""
    if not update.message or not update.message.text:
        return

    text = update.message.text.strip()

    # 检查是否是中文命令
    if text in COMMAND_MAP:
        # 转换为英文命令并触发
        english_cmd = COMMAND_MAP[text]
        # 修改消息文本为英文命令格式
        update.message.text = f"/{english_cmd}"

        # 通过调度器重新处理为英文命令
        # 这样可以复用现有的英文命令处理逻辑
        from bot.handlers import get_handler_for_command
        handler = get_handler_for_command(english_cmd)
        if handler:
            await handler(update, context)


def setup_chinese_commands(application):
    """注册中文命令处理器"""
    # 创建文本过滤器,匹配所有中文命令
    chinese_commands = list(COMMAND_MAP.keys())
    text_filter = filters.TEXT & filters.Regex(f"^({'|'.join(chinese_commands)})$")

    # 添加MessageHandler来处理中文命令
    handler = MessageHandler(text_filter, handle_chinese_command)
    application.add_handler(handler)

    return len(chinese_commands)
EOF

chown xiuxian:xiuxian "$INSTALL_DIR/src/bot/handlers/chinese_commands.py"
echo -e "${GREEN}✓ 中文命令模块已创建${NC}"

# 3. 修改main.py集成中文命令支持
echo ""
echo -e "${YELLOW}3. 集成中文命令到主程序...${NC}"

MAIN_FILE="$INSTALL_DIR/src/bot/main.py"

# 检查是否已经添加过
if grep -q "from bot.handlers.chinese_commands import setup_chinese_commands" "$MAIN_FILE"; then
    echo -e "${BLUE}ℹ 中文命令支持已经集成${NC}"
else
    # 在文件末尾的application.run_polling()之前添加
    sed -i '/application\.run_polling/i\    # 设置中文命令支持\n    from bot.handlers.chinese_commands import setup_chinese_commands\n    cmd_count = setup_chinese_commands(application)\n    logger.info(f"已加载 {cmd_count} 个中文命令支持")\n' "$MAIN_FILE"

    echo -e "${GREEN}✓ 已集成到主程序${NC}"
fi

# 4. 移除所有中文CommandHandler注册
echo ""
echo -e "${YELLOW}4. 移除原有的中文CommandHandler...${NC}"

find "$HANDLERS_DIR" -name "*.py" -type f | while read file; do
    # 跳过新创建的chinese_commands.py
    if [[ "$file" == *"chinese_commands.py" ]]; then
        continue
    fi

    # 检查是否包含中文CommandHandler
    if grep -E 'CommandHandler\("[^"]*[\x{4e00}-\x{9fff}]' "$file" >/dev/null 2>&1 || \
       grep '检测灵根\|修炼\|战斗\|背包\|商店\|宗门\|排行榜\|签到\|帮助\|状态' "$file" >/dev/null 2>&1; then

        echo "  处理: $(basename $file)"

        # 注释掉包含中文的CommandHandler行
        sed -i 's/^\([[:space:]]*\)application\.add_handler(CommandHandler("\([^"]*[\x{4e00}-\x{9fff}][^"]*\)"/\1# application.add_handler(CommandHandler("\2"  # 已迁移到chinese_commands.py/g' "$file"

        # 如果上面的正则不work,用具体的中文词
        sed -i 's/^\([[:space:]]*\)\(.*CommandHandler("检测灵根".*\)/\1# \2  # 已迁移到chinese_commands.py/' "$file"
        sed -i 's/^\([[:space:]]*\)\(.*CommandHandler("帮助".*\)/\1# \2  # 已迁移到chinese_commands.py/' "$file"
        sed -i 's/^\([[:space:]]*\)\(.*CommandHandler("状态".*\)/\1# \2  # 已迁移到chinese_commands.py/' "$file"
        sed -i 's/^\([[:space:]]*\)\(.*CommandHandler("修炼".*\)/\1# \2  # 已迁移到chinese_commands.py/' "$file"
        sed -i 's/^\([[:space:]]*\)\(.*CommandHandler("收功".*\)/\1# \2  # 已迁移到chinese_commands.py/' "$file"
        sed -i 's/^\([[:space:]]*\)\(.*CommandHandler("突破".*\)/\1# \2  # 已迁移到chinese_commands.py/' "$file"
        sed -i 's/^\([[:space:]]*\)\(.*CommandHandler("战斗".*\)/\1# \2  # 已迁移到chinese_commands.py/' "$file"
        sed -i 's/^\([[:space:]]*\)\(.*CommandHandler("背包".*\)/\1# \2  # 已迁移到chinese_commands.py/' "$file"
        sed -i 's/^\([[:space:]]*\)\(.*CommandHandler("商店".*\)/\1# \2  # 已迁移到chinese_commands.py/' "$file"
        sed -i 's/^\([[:space:]]*\)\(.*CommandHandler("宗门".*\)/\1# \2  # 已迁移到chinese_commands.py/' "$file"
        sed -i 's/^\([[:space:]]*\)\(.*CommandHandler("排行榜".*\)/\1# \2  # 已迁移到chinese_commands.py/' "$file"
        sed -i 's/^\([[:space:]]*\)\(.*CommandHandler("签到".*\)/\1# \2  # 已迁移到chinese_commands.py/' "$file"
    fi
done

echo -e "${GREEN}✓ 已移除中文CommandHandler${NC}"

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
    echo -e "${GREEN}  修复完成!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "✅ 现在同时支持中文和英文命令:"
    echo ""
    echo "中文命令示例:"
    echo "  检测灵根  - 开始游戏"
    echo "  帮助      - 查看帮助"
    echo "  状态      - 个人信息"
    echo "  修炼      - 开始修炼"
    echo "  战斗      - 进入战斗"
    echo "  背包      - 查看背包"
    echo "  商店      - 打开商店"
    echo "  宗门      - 宗门功能"
    echo "  排行榜    - 查看排行"
    echo "  签到      - 每日签到"
    echo ""
    echo "英文命令示例:"
    echo "  /start      - 开始游戏"
    echo "  /help       - 查看帮助"
    echo "  /info       - 个人信息"
    echo "  /cultivate  - 开始修炼"
    echo "  /battle     - 进入战斗"
    echo "  /bag        - 查看背包"
    echo "  /shop       - 打开商店"
    echo "  /sect       - 宗门功能"
    echo "  /rank       - 查看排行"
    echo "  /signin     - 每日签到"
    echo ""

else
    echo -e "${RED}✗ 服务启动失败${NC}"
    echo ""
    echo "查看错误日志:"
    journalctl -u xiuxian-bot -n 30 --no-pager
    exit 1
fi

echo "查看实时日志:"
echo "  journalctl -u xiuxian-bot -f"
echo ""
