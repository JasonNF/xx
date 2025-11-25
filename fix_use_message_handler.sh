#!/bin/bash

#===============================================
# 使用MessageHandler支持中文命令
# 将CommandHandler("中文")改为MessageHandler支持
#===============================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  修改为MessageHandler支持中文${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

if [[ $EUID -ne 0 ]]; then
    echo -e "${RED}需要root权限${NC}"
    exit 1
fi

INSTALL_DIR="/opt/xiuxian-bot"
HANDLERS_DIR="$INSTALL_DIR/src/bot/handlers"

# 简单方案:直接移除所有中文CommandHandler,只保留英文的
echo -e "${YELLOW}1. 备份文件...${NC}"
BACKUP_DIR="/opt/xiuxian-bot-handlers-backup-$(date +%Y%m%d_%H%M%S)"
cp -r "$HANDLERS_DIR" "$BACKUP_DIR"
echo -e "${GREEN}✓ 已备份到 $BACKUP_DIR${NC}"

echo ""
echo -e "${YELLOW}2. 移除中文CommandHandler...${NC}"

# 查找并注释掉所有包含中文的CommandHandler
find "$HANDLERS_DIR" -name "*.py" -type f | while read file; do
    # 如果文件包含中文CommandHandler
    if grep -P 'CommandHandler\("[\\u4e00-\\u9fff]' "$file" >/dev/null 2>&1 || \
       grep -E 'CommandHandler\("[\x{4e00}-\x{9fff}]' "$file" >/dev/null 2>&1 || \
       grep '检测灵根\|修炼\|战斗\|背包\|商店\|宗门\|排行榜\|签到\|帮助\|状态' "$file" >/dev/null 2>&1; then

        echo "  处理: $(basename $file)"

        # 注释掉包含中文的CommandHandler行
        sed -i '/CommandHandler("检测灵根"/d' "$file"
        sed -i '/CommandHandler("帮助"/d' "$file"
        sed -i '/CommandHandler("状态"/d' "$file"
        sed -i '/CommandHandler("修炼"/d' "$file"
        sed -i '/CommandHandler("收功"/d' "$file"
        sed -i '/CommandHandler("取消修炼"/d' "$file"
        sed -i '/CommandHandler("突破"/d' "$file"
        sed -i '/CommandHandler("战斗"/d' "$file"
        sed -i '/CommandHandler("挑战"/d' "$file"
        sed -i '/CommandHandler("查看怪物"/d' "$file"
        sed -i '/CommandHandler("技能列表"/d' "$file"
        sed -i '/CommandHandler("学习技能"/d' "$file"
        sed -i '/CommandHandler("装备技能"/d' "$file"
        sed -i '/CommandHandler("背包"/d' "$file"
        sed -i '/CommandHandler("使用"/d' "$file"
        sed -i '/CommandHandler("装备"/d' "$file"
        sed -i '/CommandHandler("卸下"/d' "$file"
        sed -i '/CommandHandler("商店"/d' "$file"
        sed -i '/CommandHandler("购买"/d' "$file"
        sed -i '/CommandHandler("宗门"/d' "$file"
        sed -i '/CommandHandler("创建宗门"/d' "$file"
        sed -i '/CommandHandler("加入宗门"/d' "$file"
        sed -i '/CommandHandler("离开宗门"/d' "$file"
        sed -i '/CommandHandler("宗门信息"/d' "$file"
        sed -i '/CommandHandler("宗门成员"/d' "$file"
        sed -i '/CommandHandler("宗门贡献"/d' "$file"
        sed -i '/CommandHandler("排行榜"/d' "$file"
        sed -i '/CommandHandler("境界榜"/d' "$file"
        sed -i '/CommandHandler("战力榜"/d' "$file"
        sed -i '/CommandHandler("签到"/d' "$file"
        sed -i '/CommandHandler("每日签到"/d' "$file"
        sed -i '/CommandHandler("境界信息"/d' "$file"
        sed -i '/CommandHandler("灵根信息"/d' "$file"
        sed -i '/CommandHandler("市场"/d' "$file"
        sed -i '/CommandHandler("出售"/d' "$file"
        sed -i '/CommandHandler("拍卖"/d' "$file"
        sed -i '/CommandHandler("炼丹"/d' "$file"
        sed -i '/CommandHandler("丹方"/d' "$file"
        sed -i '/CommandHandler("炼器"/d' "$file"
        sed -i '/CommandHandler("炼器配方"/d' "$file"
        sed -i '/CommandHandler("阵法"/d' "$file"
        sed -i '/CommandHandler("符箓"/d' "$file"
        sed -i '/CommandHandler("灵兽"/d' "$file"
        sed -i '/CommandHandler("捕捉"/d' "$file"
        sed -i '/CommandHandler("洞府"/d' "$file"
        sed -i '/CommandHandler("神识"/d' "$file"
        sed -i '/CommandHandler("任务"/d' "$file"
        sed -i '/CommandHandler("接取任务"/d' "$file"
        sed -i '/CommandHandler("完成任务"/d' "$file"
        sed -i '/CommandHandler("成就"/d' "$file"
        sed -i '/CommandHandler("秘境"/d' "$file"
        sed -i '/CommandHandler("探索"/d' "$file"
        sed -i '/CommandHandler("竞技场"/d' "$file"
        sed -i '/CommandHandler("世界BOSS"/d' "$file"
        sed -i '/CommandHandler("宗门战"/d' "$file"
        sed -i '/CommandHandler("积分商城"/d' "$file"
        sed -i '/CommandHandler("改名"/d' "$file"
        sed -i '/CommandHandler("寿元"/d' "$file"
        sed -i '/CommandHandler("金丹品质"/d' "$file"
        sed -i '/CommandHandler("功法"/d' "$file"
        sed -i '/CommandHandler("修炼功法"/d' "$file"
        sed -i '/CommandHandler("长老"/d' "$file"
        sed -i '/CommandHandler("宗门排行"/d' "$file"
    fi
done

echo -e "${GREEN}✓ 已移除中文命令${NC}"

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
    echo "Bot已启动,现在使用英文命令:"
    echo "  /start      - 开始游戏"
    echo "  /help       - 帮助"
    echo "  /info       - 个人信息 (代替 /状态)"
    echo "  /cultivate  - 修炼"
    echo "  /finish     - 收功"
    echo "  /breakthrough - 突破"
    echo "  /battle     - 战斗"
    echo "  /skills     - 技能列表"
    echo "  /bag        - 背包"
    echo "  /shop       - 商店"
    echo "  /sect       - 宗门"
    echo "  /rank       - 排行榜"
    echo "  /signin     - 签到"
    echo ""

else
    echo -e "${RED}✗ 服务启动失败${NC}"
    echo ""
    journalctl -u xiuxian-bot -n 30 --no-pager
    exit 1
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  修复完成!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "查看日志:"
echo "  journalctl -u xiuxian-bot -f"
echo ""
