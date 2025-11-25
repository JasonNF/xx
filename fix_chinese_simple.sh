#!/bin/bash

#===============================================
# 简单方案: 移除中文CommandHandler,保留英文命令
# 用户可以通过英文命令使用bot,同时在帮助信息中说明中文含义
#===============================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  修复Telegram Bot命令问题${NC}"
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

# 2. 删除所有中文CommandHandler注册行
echo ""
echo -e "${YELLOW}2. 移除中文CommandHandler...${NC}"

# 定义所有需要删除的中文命令
CHINESE_COMMANDS=(
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
for cmd in "${CHINESE_COMMANDS[@]}"; do
    # 在所有.py文件中删除包含该中文命令的CommandHandler行
    if grep -r "CommandHandler(\"$cmd\"" "$HANDLERS_DIR" >/dev/null 2>&1; then
        find "$HANDLERS_DIR" -name "*.py" -type f -exec sed -i "/CommandHandler(\"$cmd\"/d" {} \;
        echo "  ✓ 已移除: $cmd"
        ((count++))
    fi
done

echo -e "${GREEN}✓ 共移除 $count 个中文命令${NC}"

# 3. 修正权限
echo ""
echo -e "${YELLOW}3. 修正文件权限...${NC}"
chown -R xiuxian:xiuxian "$HANDLERS_DIR"
echo -e "${GREEN}✓ 权限已修正${NC}"

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
    echo "⚠️  注意: 由于Telegram限制,只能使用英文命令"
    echo ""
    echo "可用命令列表:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "基础:"
    echo "  /start         开始游戏/检测灵根"
    echo "  /help          查看帮助"
    echo "  /info          个人信息/状态"
    echo ""
    echo "修炼:"
    echo "  /cultivate     开始修炼"
    echo "  /finish        收功"
    echo "  /cancel        取消修炼"
    echo "  /breakthrough  突破境界"
    echo ""
    echo "战斗:"
    echo "  /battle        战斗"
    echo "  /challenge     挑战"
    echo "  /monsters      查看怪物"
    echo ""
    echo "技能:"
    echo "  /skills        技能列表"
    echo "  /learn         学习技能"
    echo "  /equip_skill   装备技能"
    echo ""
    echo "物品:"
    echo "  /bag           背包"
    echo "  /use           使用物品"
    echo "  /equip         装备"
    echo "  /unequip       卸下装备"
    echo ""
    echo "商店:"
    echo "  /shop          商店"
    echo "  /buy           购买"
    echo ""
    echo "宗门:"
    echo "  /sect          宗门"
    echo "  /create_sect   创建宗门"
    echo "  /join_sect     加入宗门"
    echo "  /leave_sect    离开宗门"
    echo "  /sect_info     宗门信息"
    echo "  /sect_members  宗门成员"
    echo "  /contribute    宗门贡献"
    echo ""
    echo "排行:"
    echo "  /rank          排行榜"
    echo "  /rank_realm    境界榜"
    echo "  /rank_power    战力榜"
    echo ""
    echo "其他:"
    echo "  /signin        签到"
    echo "  /market        市场"
    echo "  /alchemy       炼丹"
    echo "  /refinery      炼器"
    echo "  /pet           灵兽"
    echo "  /quest         任务"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

else
    echo -e "${RED}✗ 服务启动失败${NC}"
    echo ""
    journalctl -u xiuxian-bot -n 30 --no-pager
    exit 1
fi

echo "查看实时日志:"
echo "  journalctl -u xiuxian-bot -f"
echo ""
