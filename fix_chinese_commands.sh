#!/bin/bash

#===============================================
# 修复Telegram Bot中文命令问题
# Telegram命令只能使用英文、数字和下划线
#===============================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  修复Bot命令（中文->英文）${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

if [[ $EUID -ne 0 ]]; then
    echo -e "${RED}需要root权限${NC}"
    exit 1
fi

INSTALL_DIR="/opt/xiuxian-bot"
HANDLERS_DIR="$INSTALL_DIR/src/bot/handlers"

# 备份
echo -e "${YELLOW}1. 备份处理器文件...${NC}"
BACKUP_DIR="/opt/xiuxian-bot-handlers-backup-$(date +%Y%m%d_%H%M%S)"
cp -r "$HANDLERS_DIR" "$BACKUP_DIR"
echo -e "${GREEN}✓ 已备份到 $BACKUP_DIR${NC}"

echo ""
echo -e "${YELLOW}2. 替换中文命令为英文...${NC}"

# 定义中文到英文的映射
declare -A CMD_MAP=(
    # start.py
    ["检测灵根"]="start"
    ["个人信息"]="info"
    ["帮助"]="help"

    # cultivation.py
    ["修炼"]="cultivate"
    ["收功"]="finish"
    ["取消修炼"]="cancel"
    ["突破"]="breakthrough"

    # battle.py
    ["战斗"]="battle"
    ["挑战"]="challenge"
    ["查看怪物"]="monsters"

    # skill.py
    ["技能列表"]="skills"
    ["学习技能"]="learn"
    ["装备技能"]="equip_skill"

    # inventory.py
    ["背包"]="bag"
    ["使用"]="use"
    ["装备"]="equip"
    ["卸下"]="unequip"

    # shop.py
    ["商店"]="shop"
    ["购买"]="buy"

    # sect.py
    ["宗门"]="sect"
    ["创建宗门"]="create_sect"
    ["加入宗门"]="join_sect"
    ["离开宗门"]="leave_sect"
    ["宗门信息"]="sect_info"
    ["宗门成员"]="sect_members"
    ["宗门贡献"]="contribute"

    # ranking.py
    ["排行榜"]="rank"
    ["境界榜"]="rank_realm"
    ["战力榜"]="rank_power"

    # signin.py
    ["签到"]="signin"
    ["每日签到"]="daily"

    # realm.py
    ["境界信息"]="realm"

    # spirit_root.py
    ["灵根信息"]="spirit_root"

    # market.py
    ["市场"]="market"
    ["出售"]="sell"
    ["拍卖"]="auction"

    # alchemy.py
    ["炼丹"]="alchemy"
    ["丹方"]="recipes"

    # refinery.py
    ["炼器"]="refinery"
    ["炼器配方"]="refine_recipes"

    # formation.py
    ["阵法"]="formation"

    # talisman.py
    ["符箓"]="talisman"

    # spirit_beast.py
    ["灵兽"]="pet"
    ["捕捉"]="catch"

    # cave_dwelling.py
    ["洞府"]="cave"

    # divine_sense.py
    ["神识"]="divine"

    # quest.py
    ["任务"]="quest"
    ["接取任务"]="accept_quest"
    ["完成任务"]="complete_quest"

    # achievement.py
    ["成就"]="achievement"

    # adventure.py
    ["秘境"]="adventure"
    ["探索"]="explore"

    # arena.py
    ["竞技场"]="arena"

    # world_boss.py
    ["世界BOSS"]="worldboss"

    # sect_war.py
    ["宗门战"]="sect_war"

    # credit_shop.py
    ["积分商城"]="credits"

    # rename.py
    ["改名"]="rename"

    # lifespan.py
    ["寿元"]="lifespan"

    # core_quality.py
    ["金丹品质"]="core"

    # cultivation_method.py
    ["功法"]="method"
    ["修炼功法"]="practice"

    # sect_elder.py
    ["长老"]="elder"

    # sect_ranking.py
    ["宗门排行"]="sect_rank"
)

# 执行替换
count=0
for chinese in "${!CMD_MAP[@]}"; do
    english="${CMD_MAP[$chinese]}"

    # 在所有处理器文件中替换
    if grep -r "CommandHandler(\"$chinese\"" "$HANDLERS_DIR" >/dev/null 2>&1; then
        find "$HANDLERS_DIR" -name "*.py" -type f -exec sed -i "s/CommandHandler(\"$chinese\"/CommandHandler(\"$english\"/g" {} \;
        echo "  $chinese -> $english"
        ((count++))
    fi
done

echo -e "${GREEN}✓ 已替换 $count 个命令${NC}"

# 3. 修改文件所有权
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
else
    echo -e "${RED}✗ 服务启动失败${NC}"
    echo ""
    journalctl -u xiuxian-bot -n 20 --no-pager
    exit 1
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  命令修复完成!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "现在可以使用英文命令了:"
echo "  /start  - 开始游戏"
echo "  /info   - 个人信息"
echo "  /help   - 帮助"
echo "  /cultivate - 修炼"
echo "  /battle - 战斗"
echo "  /skills - 技能列表"
echo "  /bag    - 背包"
echo "  /shop   - 商店"
echo "  /sect   - 宗门"
echo "  /rank   - 排行榜"
echo "  /signin - 签到"
echo ""
echo "查看日志:"
echo "  journalctl -u xiuxian-bot -f"
echo ""
