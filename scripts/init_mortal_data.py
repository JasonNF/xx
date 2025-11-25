"""凡人修仙传 - 初始化游戏数据"""
import asyncio
import json
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from bot.models.database import init_db, AsyncSessionLocal
from bot.models.player import RealmType, Skill, SpiritRootElement
from bot.models.item import Item, ItemType, TreasureGrade
from bot.models.sect import Sect, SectFaction, SectRegion
from bot.models.battle import Monster
from bot.models.secret_realm import (
    SecretRealm, RealmType as SecretRealmType, RealmDifficulty, RealmStatus,
    RealmLootPool, RealmEvent
)
from bot.models.quest import Quest, QuestType


async def create_initial_sects():
    """创建初始门派 - 天南七派"""
    async with AsyncSessionLocal() as session:
        sects_data = [
            # 天南七派（正道）
            {
                "name": "黄枫谷",
                "description": "天南七派之一，韩立所在门派，以炼制法器和符箓闻名",
                "faction": SectFaction.RIGHTEOUS,
                "region": SectRegion.TIANNAN,
                "is_npc_sect": True,
                "max_members": 500,
                "level": 5,
            },
            {
                "name": "灵兽山",
                "description": "天南七派之一，擅长驯养灵兽",
                "faction": SectFaction.RIGHTEOUS,
                "region": SectRegion.TIANNAN,
                "is_npc_sect": True,
                "max_members": 500,
                "level": 5,
            },
            {
                "name": "清虚门",
                "description": "天南七派之一，符箓大宗",
                "faction": SectFaction.RIGHTEOUS,
                "region": SectRegion.TIANNAN,
                "is_npc_sect": True,
                "max_members": 500,
                "level": 5,
            },
            {
                "name": "掩月宗",
                "description": "天南七派之一，女修门派",
                "faction": SectFaction.RIGHTEOUS,
                "region": SectRegion.TIANNAN,
                "is_npc_sect": True,
                "max_members": 400,
                "level": 5,
            },
            {
                "name": "巨剑门",
                "description": "天南七派之一，剑修宗门",
                "faction": SectFaction.RIGHTEOUS,
                "region": SectRegion.TIANNAN,
                "is_npc_sect": True,
                "max_members": 450,
                "level": 5,
            },
            {
                "name": "天阙堡",
                "description": "天南七派之一，炼器名门",
                "faction": SectFaction.RIGHTEOUS,
                "region": SectRegion.TIANNAN,
                "is_npc_sect": True,
                "max_members": 400,
                "level": 5,
            },
            {
                "name": "化刀坞",
                "description": "天南七派之一，刀修宗门",
                "faction": SectFaction.RIGHTEOUS,
                "region": SectRegion.TIANNAN,
                "is_npc_sect": True,
                "max_members": 400,
                "level": 5,
            },

            # 魔道六宗
            {
                "name": "鬼灵门",
                "description": "魔道六宗之一，御鬼之道",
                "faction": SectFaction.DEMONIC,
                "region": SectRegion.TIANNAN,
                "is_npc_sect": True,
                "max_members": 400,
                "level": 5,
            },
            {
                "name": "合欢宗",
                "description": "魔道六宗之一，双修魔功",
                "faction": SectFaction.DEMONIC,
                "region": SectRegion.TIANNAN,
                "is_npc_sect": True,
                "max_members": 300,
                "level": 5,
            },
            {
                "name": "御灵宗",
                "description": "魔道六宗之一，炼尸控傀",
                "faction": SectFaction.DEMONIC,
                "region": SectRegion.TIANNAN,
                "is_npc_sect": True,
                "max_members": 350,
                "level": 5,
            },
        ]

        for sect_info in sects_data:
            sect = Sect(**sect_info)
            session.add(sect)

        await session.commit()
        print(f"✅ 创建了 {len(sects_data)} 个门派")


async def create_basic_skills():
    """创建基础法术技能"""
    async with AsyncSessionLocal() as session:
        skills = [
            # 五行基础法术
            {
                "name": "火球术",
                "description": "基础火系攻击法术",
                "skill_type": "攻击",
                "element": "火",
                "base_power": 100,
                "damage_multiplier": 1.2,
                "spiritual_cost": 10,
                "cooldown_rounds": 0,
                "required_realm": RealmType.QI_REFINING,
                "learning_cost": 100,
            },
            {
                "name": "冰锥术",
                "description": "水系攻击法术，有几率减速",
                "skill_type": "攻击",
                "element": "水",
                "base_power": 90,
                "damage_multiplier": 1.1,
                "spiritual_cost": 10,
                "cooldown_rounds": 0,
                "special_effects": json.dumps(["减速"]),
                "required_realm": RealmType.QI_REFINING,
                "learning_cost": 100,
            },
            {
                "name": "金刃术",
                "description": "金系攻击法术，锋利无比",
                "skill_type": "攻击",
                "element": "金",
                "base_power": 110,
                "damage_multiplier": 1.3,
                "spiritual_cost": 15,
                "cooldown_rounds": 1,
                "required_realm": RealmType.QI_REFINING,
                "required_spirit_root": "金",
                "learning_cost": 200,
            },
            # 防御法术
            {
                "name": "金光护体",
                "description": "金系防御法术，提升防御力",
                "skill_type": "防御",
                "element": "金",
                "base_power": 0,
                "damage_multiplier": 0.0,
                "spiritual_cost": 20,
                "cooldown_rounds": 3,
                "required_realm": RealmType.QI_REFINING,
                "learning_cost": 300,
            },
            # 青元剑诀相关
            {
                "name": "青元剑芒",
                "description": "青元剑诀第三层法术，凝聚剑气攻敌",
                "skill_type": "攻击",
                "element": "金",
                "base_power": 150,
                "damage_multiplier": 1.5,
                "spiritual_cost": 25,
                "cooldown_rounds": 1,
                "required_realm": RealmType.QI_REFINING,
                "learning_cost": 5000,
            },
            {
                "name": "护体剑盾",
                "description": "青元剑诀第五层法术，剑气化盾",
                "skill_type": "防御",
                "element": "金",
                "base_power": 0,
                "damage_multiplier": 0.0,
                "spiritual_cost": 30,
                "cooldown_rounds": 5,
                "required_realm": RealmType.FOUNDATION,
                "learning_cost": 10000,
            },
        ]

        for skill_data in skills:
            skill = Skill(**skill_data)
            session.add(skill)

        await session.commit()
        print(f"✅ 创建了 {len(skills)} 个法术技能")


async def create_basic_items():
    """创建基础物品"""
    async with AsyncSessionLocal() as session:
        items = [
            # 丹药
            {
                "name": "筑基丹",
                "description": "辅助筑基的珍贵丹药，提升50%成功率",
                "item_type": ItemType.PILL,
                "breakthrough_bonus": 0.5,
                "buy_price": 100000,
                "sell_price": 50000,
                "is_stackable": True,
                "max_stack": 10,
            },
            {
                "name": "凝金丹",
                "description": "辅助结丹的稀有丹药，提升30%成功率",
                "item_type": ItemType.PILL,
                "breakthrough_bonus": 0.3,
                "buy_price": 500000,
                "sell_price": 250000,
                "is_stackable": True,
                "max_stack": 5,
            },
            {
                "name": "回春丹",
                "description": "快速恢复生命值的丹药",
                "item_type": ItemType.PILL,
                "hp_restore": 500,
                "buy_price": 1000,
                "sell_price": 500,
                "is_stackable": True,
                "max_stack": 99,
            },
            {
                "name": "聚灵丹",
                "description": "快速恢复灵力的丹药",
                "item_type": ItemType.PILL,
                "spiritual_restore": 300,
                "buy_price": 800,
                "sell_price": 400,
                "is_stackable": True,
                "max_stack": 99,
            },

            # 法器
            {
                "name": "青竹蜂云剑",
                "description": "韩立炼气期主力飞剑，由青竹蜂剑炼化而成",
                "item_type": ItemType.WEAPON,
                "treasure_grade": TreasureGrade.MAGIC_TOOL_HIGH,
                "attack_bonus": 50,
                "speed_bonus": 10,
                "buy_price": 20000,
                "sell_price": 10000,
                "required_realm": "炼气期",
                "required_level": 7,
            },
            {
                "name": "金刚盾",
                "description": "坚固的下品法器，提供基础防护",
                "item_type": ItemType.ARMOR,
                "treasure_grade": TreasureGrade.MAGIC_TOOL_LOW,
                "defense_bonus": 30,
                "hp_bonus": 100,
                "buy_price": 5000,
                "sell_price": 2500,
                "required_realm": "炼气期",
                "required_level": 5,
            },

            # 灵药
            {
                "name": "玉随芝",
                "description": "筑基丹主药之一，生长在血色禁地",
                "item_type": ItemType.HERB,
                "herb_age": 300,
                "buy_price": 30000,
                "sell_price": 15000,
                "is_stackable": True,
                "max_stack": 50,
            },
        ]

        for item_data in items:
            item = Item(**item_data)
            session.add(item)

        await session.commit()
        print(f"✅ 创建了 {len(items)} 种物品")


async def create_basic_monsters():
    """创建基础怪物"""
    async with AsyncSessionLocal() as session:
        monsters = [
            {
                "name": "野狼",
                "description": "普通的野狼，适合炼气初期修士历练",
                "level": 1,
                "realm": "炼气期1层",
                "hp": 100,
                "attack": 15,
                "defense": 5,
                "speed": 12,
                "exp_reward": 50,
                "spirit_stones_min": 10,
                "spirit_stones_max": 30,
                "drop_rate": 0.1,
                "is_boss": False,
            },
            {
                "name": "炼气期修士",
                "description": "敌对的炼气期修士",
                "level": 5,
                "realm": "炼气期5层",
                "hp": 300,
                "attack": 40,
                "defense": 20,
                "speed": 25,
                "exp_reward": 200,
                "spirit_stones_min": 50,
                "spirit_stones_max": 150,
                "drop_rate": 0.2,
                "is_boss": False,
            },
            {
                "name": "筑基期妖兽",
                "description": "筑基期境界的强大妖兽",
                "level": 15,
                "realm": "筑基期初期",
                "hp": 2000,
                "attack": 150,
                "defense": 80,
                "speed": 60,
                "exp_reward": 2000,
                "spirit_stones_min": 500,
                "spirit_stones_max": 1500,
                "drop_rate": 0.3,
                "is_boss": True,
            },
        ]

        for monster_data in monsters:
            monster = Monster(**monster_data)
            session.add(monster)

        await session.commit()
        print(f"✅ 创建了 {len(monsters)} 种怪物")


async def create_secret_realms():
    """创建秘境 - 血色禁地等"""
    async with AsyncSessionLocal() as session:
        # 首先需要获取已创建的物品ID用于掉落配置
        from sqlalchemy import select

        realms_data = [
            {
                "name": "血色禁地",
                "description": "天南修仙界著名的凶险之地，盛产筑基丹主药玉随芝和妖兽材料",
                "realm_type": SecretRealmType.FORBIDDEN_LAND,
                "difficulty": RealmDifficulty.HARD,
                "status": RealmStatus.PERMANENT,
                "min_realm_requirement": "炼气期7层",
                "max_realm_limit": "筑基期后期",
                "min_level": 7,
                "entry_cost": 5000,
                "duration_minutes": 120,
                "cooldown_hours": 48,
                "base_exp_reward": 5000,
                "base_spirit_stones": 2000,
                "danger_level": 8,
                "is_story_realm": True,
                "story_chapter": "第一章·升仙大会",
                "max_players": 10,
            },
            {
                "name": "虚天殿遗迹",
                "description": "上古修士留下的神秘殿宇，传说中有古宝和稀有功法",
                "realm_type": SecretRealmType.ANCIENT_RUIN,
                "difficulty": RealmDifficulty.HELL,
                "status": RealmStatus.UNOPENED,
                "min_realm_requirement": "筑基期",
                "max_realm_limit": "结丹期",
                "min_level": 1,
                "entry_cost": 50000,
                "duration_minutes": 180,
                "cooldown_hours": 168,  # 7天
                "base_exp_reward": 50000,
                "base_spirit_stones": 20000,
                "danger_level": 10,
                "is_story_realm": True,
                "story_chapter": "第三章·虚天殿",
                "max_players": 5,
            },
            {
                "name": "太岳山脉洞府",
                "description": "散落在太岳山脉的古修士洞府，有一定几率发现法器和丹药",
                "realm_type": SecretRealmType.CAVE_MANSION,
                "difficulty": RealmDifficulty.NORMAL,
                "status": RealmStatus.PERMANENT,
                "min_realm_requirement": "炼气期5层",
                "min_level": 5,
                "entry_cost": 1000,
                "duration_minutes": 60,
                "cooldown_hours": 24,
                "base_exp_reward": 2000,
                "base_spirit_stones": 800,
                "danger_level": 5,
                "is_story_realm": False,
                "max_players": 0,  # 无限制
            },
            {
                "name": "黄枫谷试炼地",
                "description": "宗门为弟子准备的试炼场所，相对安全",
                "realm_type": SecretRealmType.TRIAL_GROUND,
                "difficulty": RealmDifficulty.EASY,
                "status": RealmStatus.PERMANENT,
                "min_realm_requirement": "炼气期1层",
                "max_realm_limit": "炼气期13层",
                "min_level": 1,
                "entry_cost": 0,
                "duration_minutes": 30,
                "cooldown_hours": 12,
                "base_exp_reward": 500,
                "base_spirit_stones": 200,
                "danger_level": 2,
                "is_story_realm": False,
                "max_players": 20,
            },
        ]

        for realm_info in realms_data:
            realm = SecretRealm(**realm_info)
            session.add(realm)

        await session.commit()
        print(f"✅ 创建了 {len(realms_data)} 个秘境")


async def create_main_quests():
    """创建主线任务 - 凡人修仙传剧情"""
    async with AsyncSessionLocal() as session:
        quests_data = [
            # 第一章：升仙大会
            {
                "name": "【第一章】初入修仙界",
                "description": "韩立初入修仙界，检测灵根资质，正式踏上修仙之路",
                "quest_type": QuestType.MAIN,
                "objective_type": "spirit_root_check",
                "objective_target": "complete",
                "objective_count": 1,
                "required_realm": "凡人",
                "required_level": 0,
                "exp_reward": 1000,
                "spirit_stones_reward": 5000,
                "is_repeatable": False,
            },
            {
                "name": "【第一章】加入黄枫谷",
                "description": "通过升仙大会的考核，正式成为黄枫谷外门弟子",
                "quest_type": QuestType.MAIN,
                "objective_type": "join_sect",
                "objective_target": "黄枫谷",
                "objective_count": 1,
                "required_realm": "炼气期1层",
                "required_level": 1,
                "exp_reward": 2000,
                "spirit_stones_reward": 10000,
                "contribution_reward": 100,
                "is_repeatable": False,
            },
            {
                "name": "【第一章】修炼长春功",
                "description": "学习宗门基础功法长春功，开始修炼生涯",
                "quest_type": QuestType.MAIN,
                "objective_type": "learn_method",
                "objective_target": "长春功",
                "objective_count": 1,
                "required_realm": "炼气期1层",
                "required_level": 1,
                "exp_reward": 1500,
                "spirit_stones_reward": 3000,
                "is_repeatable": False,
            },
            {
                "name": "【第一章】炼气期七层",
                "description": "努力修炼，突破到炼气期七层，准备参加血色禁地试炼",
                "quest_type": QuestType.MAIN,
                "objective_type": "reach_realm",
                "objective_target": "炼气期7层",
                "objective_count": 1,
                "required_realm": "炼气期1层",
                "required_level": 1,
                "exp_reward": 5000,
                "spirit_stones_reward": 15000,
                "is_repeatable": False,
            },
            # 第二章：血色禁地
            {
                "name": "【第二章】血色禁地试炼",
                "description": "七派联合开启血色禁地，前往寻找筑基丹主药玉随芝",
                "quest_type": QuestType.MAIN,
                "objective_type": "explore_realm",
                "objective_target": "血色禁地",
                "objective_count": 1,
                "required_realm": "炼气期7层",
                "required_level": 7,
                "exp_reward": 10000,
                "spirit_stones_reward": 30000,
                "item_rewards": json.dumps([{"item_name": "玉随芝", "quantity": 2}]),
                "is_repeatable": False,
            },
            {
                "name": "【第二章】炼制筑基丹",
                "description": "收集筑基丹所需材料，炼制筑基丹为突破做准备",
                "quest_type": QuestType.MAIN,
                "objective_type": "obtain_item",
                "objective_target": "筑基丹",
                "objective_count": 1,
                "required_realm": "炼气期7层",
                "required_level": 7,
                "exp_reward": 8000,
                "spirit_stones_reward": 0,
                "is_repeatable": False,
            },
            {
                "name": "【第二章】筑基成功",
                "description": "服用筑基丹，成功突破筑基期，成为真正的修仙者",
                "quest_type": QuestType.MAIN,
                "objective_type": "reach_realm",
                "objective_target": "筑基期",
                "objective_count": 1,
                "required_realm": "炼气期13层",
                "required_level": 13,
                "exp_reward": 20000,
                "spirit_stones_reward": 50000,
                "item_rewards": json.dumps([{"item_name": "青竹蜂云剑", "quantity": 1}]),
                "is_repeatable": False,
            },

            # 每日任务
            {
                "name": "【每日】修炼",
                "description": "每日坚持修炼，精进道行",
                "quest_type": QuestType.DAILY,
                "objective_type": "cultivate",
                "objective_count": 3600,  # 1小时秒数
                "exp_reward": 500,
                "spirit_stones_reward": 1000,
                "is_repeatable": True,
                "cooldown_hours": 24,
            },
            {
                "name": "【每日】历练",
                "description": "与妖兽战斗，磨练战斗技巧",
                "quest_type": QuestType.DAILY,
                "objective_type": "kill_monster",
                "objective_count": 5,
                "exp_reward": 800,
                "spirit_stones_reward": 1500,
                "is_repeatable": True,
                "cooldown_hours": 24,
            },
            {
                "name": "【每日】宗门贡献",
                "description": "完成宗门任务，积累贡献度",
                "quest_type": QuestType.SECT,
                "objective_type": "sect_task",
                "objective_count": 1,
                "exp_reward": 300,
                "spirit_stones_reward": 500,
                "contribution_reward": 50,
                "is_repeatable": True,
                "cooldown_hours": 24,
            },
        ]

        for quest_info in quests_data:
            quest = Quest(**quest_info)
            session.add(quest)

        await session.commit()
        print(f"✅ 创建了 {len(quests_data)} 个任务")


async def main():
    """主函数"""
    print("=" * 60)
    print("🎮 凡人修仙传 - 初始化游戏数据")
    print("=" * 60)

    # 初始化数据库
    print("\n📊 初始化数据库...")
    await init_db()
    print("✅ 数据库初始化完成\n")

    # 创建数据
    print("📝 开始创建游戏数据...\n")

    await create_initial_sects()
    # 功法系统已迁移到 init_cultivation_methods.py（43种完整功法）
    await create_basic_skills()
    await create_basic_items()
    await create_basic_monsters()
    await create_secret_realms()
    await create_main_quests()

    print("\n" + "=" * 60)
    print("🎉 所有游戏数据初始化完成！")
    print("=" * 60)
    print("\n下一步：")
    print("1. 启动Bot: python -m bot.main")
    print("2. 在Telegram发送 /start 开始游戏")
    print("3. 发送 /test_root 测试灵根检测")
    print("4. 查看任务: /quests")
    print("5. 探索秘境: /explore [秘境名称]\n")


if __name__ == "__main__":
    asyncio.run(main())
