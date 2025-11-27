#!/bin/bash

#===============================================
# 为所有handler添加CommandHandler
#===============================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  添加所有CommandHandler${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

echo -e "${YELLOW}分析并添加CommandHandler到各个模块...${NC}"

sudo -u xiuxian /opt/xiuxian-bot/venv/bin/python3 << 'PYEOF'
import os
import re

handlers_dir = '/opt/xiuxian-bot/src/bot/handlers'

# 定义每个handler文件需要注册的命令
# 格式: 文件名: [(命令名, 函数名), ...]
command_mappings = {
    'cultivation.py': [
        ('cultivate', 'cultivate_command'),
        ('finish', 'finish_cultivate_command'),
        ('cancel', 'cancel_cultivate_command'),
        ('breakthrough', 'breakthrough_command'),
    ],
    'spirit_root.py': [
        ('spirit_root', 'spirit_root_command'),
    ],
    'realm.py': [
        ('realm', 'realm_command'),
    ],
    'skill.py': [
        ('skills', 'skills_command'),
        ('learn', 'learn_skill_command'),
        ('equip_skill', 'equip_skill_command'),
    ],
    'quest.py': [
        ('quest', 'quest_command'),
        ('accept_quest', 'accept_quest_command'),
        ('complete_quest', 'complete_quest_command'),
    ],
    'battle.py': [
        ('battle', 'battle_command'),
        ('challenge', 'challenge_command'),
        ('monsters', 'monsters_command'),
    ],
    'inventory.py': [
        ('bag', 'inventory_command'),
        ('use', 'use_item_command'),
        ('equip', 'equip_item_command'),
        ('unequip', 'unequip_item_command'),
    ],
    'shop.py': [
        ('shop', 'shop_command'),
        ('buy', 'buy_command'),
    ],
    'sect.py': [
        ('sect', 'sect_command'),
        ('create_sect', 'create_sect_command'),
        ('join_sect', 'join_sect_command'),
        ('leave_sect', 'leave_sect_command'),
        ('sect_info', 'sect_info_command'),
        ('sect_members', 'sect_members_command'),
        ('contribute', 'contribute_command'),
    ],
    'ranking.py': [
        ('rank', 'ranking_command'),
        ('rank_realm', 'realm_ranking_command'),
        ('rank_power', 'power_ranking_command'),
    ],
    'signin.py': [
        ('signin', 'signin_command'),
        ('daily', 'daily_signin_command'),
    ],
    'rename.py': [
        ('rename', 'rename_command'),
    ],
    'cultivation_method.py': [
        ('method', 'method_command'),
        ('practice', 'practice_command'),
    ],
    'alchemy.py': [
        ('alchemy', 'alchemy_command'),
        ('recipes', 'recipes_command'),
    ],
    'lifespan.py': [
        ('lifespan', 'lifespan_command'),
    ],
    'refinery.py': [
        ('refinery', 'refinery_command'),
        ('refine_recipes', 'refine_recipes_command'),
    ],
    'market.py': [
        ('market', 'market_command'),
        ('sell', 'sell_command'),
        ('auction', 'auction_command'),
    ],
    'core_quality.py': [
        ('core', 'core_command'),
    ],
    'divine_sense.py': [
        ('divine', 'divine_sense_command'),
    ],
    'spirit_beast.py': [
        ('pet', 'pet_command'),
        ('catch', 'catch_command'),
    ],
    'formation.py': [
        ('formation', 'formation_command'),
    ],
    'talisman.py': [
        ('talisman', 'talisman_command'),
    ],
    'cave_dwelling.py': [
        ('cave', 'cave_command'),
    ],
    'adventure.py': [
        ('adventure', 'adventure_command'),
        ('explore', 'explore_command'),
    ],
    'achievement.py': [
        ('achievement', 'achievement_command'),
    ],
    'sect_war.py': [
        ('sect_war', 'sect_war_command'),
    ],
    'arena.py': [
        ('arena', 'arena_command'),
    ],
    'world_boss.py': [
        ('worldboss', 'worldboss_command'),
    ],
    'credit_shop.py': [
        ('credits', 'credits_command'),
    ],
    'sect_elder.py': [
        ('elder', 'elder_command'),
    ],
    'sect_ranking.py': [
        ('sect_rank', 'sect_ranking_command'),
    ],
}

def add_command_handlers_to_file(filepath, commands):
    """为文件添加CommandHandler注册"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否已经有CommandHandler导入
    if 'from telegram.ext import' in content and 'CommandHandler' not in content:
        # 添加CommandHandler到导入
        content = re.sub(
            r'(from telegram\.ext import [^)]+)',
            lambda m: m.group(1) + ', CommandHandler' if 'CommandHandler' not in m.group(1) else m.group(1),
            content
        )

    # 查找register_handlers函数
    register_pattern = r'def register_handlers\(application\):.*?""".*?"""'
    match = re.search(register_pattern, content, re.DOTALL)

    if not match:
        print(f"  ⚠️  {os.path.basename(filepath)}: 未找到register_handlers函数")
        return False

    # 构建CommandHandler注册代码
    handlers_code = '\n'
    for cmd, func in commands:
        handlers_code += f'    application.add_handler(CommandHandler("{cmd}", {func}))\n'

    # 在函数文档字符串后插入CommandHandler
    insert_pos = match.end()
    content = content[:insert_pos] + handlers_code + content[insert_pos:]

    # 写回文件
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    return True

# 处理每个文件
success_count = 0
fail_count = 0

for filename, commands in command_mappings.items():
    filepath = os.path.join(handlers_dir, filename)
    if not os.path.exists(filepath):
        print(f"✗ {filename}: 文件不存在")
        fail_count += 1
        continue

    try:
        if add_command_handlers_to_file(filepath, commands):
            print(f"✓ {filename}: 添加了 {len(commands)} 个CommandHandler")
            success_count += 1
        else:
            fail_count += 1
    except Exception as e:
        print(f"✗ {filename}: 错误 - {e}")
        fail_count += 1

print(f"\n总计: {success_count} 个文件成功, {fail_count} 个文件失败")
PYEOF

echo ""
echo -e "${GREEN}✓ CommandHandler添加完成${NC}"

echo ""
echo -e "${YELLOW}重启服务...${NC}"

systemctl restart xiuxian-bot

sleep 6

if systemctl is-active --quiet xiuxian-bot; then
    echo -e "${GREEN}✓ 服务运行正常！${NC}"

    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  所有命令已启用${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "🎮 现在可以测试所有命令了："
    echo ""
    echo "  基础: .状态 .帮助 .检测灵根"
    echo "  修炼: .修炼 .结算 .突破"
    echo "  战斗: .战斗 .挑战 .技能"
    echo "  物品: .背包 .商店"
    echo "  宗门: .宗门 .创建宗门 .加入宗门"
    echo "  其他: .签到 .排行榜 .任务"
    echo ""

    echo "最近日志:"
    journalctl -u xiuxian-bot -n 20 --no-pager

else
    echo -e "${RED}✗ 服务启动失败${NC}"
    journalctl -u xiuxian-bot -n 50 --no-pager
    exit 1
fi

echo ""
echo "📊 实时监控: journalctl -u xiuxian-bot -f"
echo ""
