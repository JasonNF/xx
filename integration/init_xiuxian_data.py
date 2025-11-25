#!/usr/bin/env python3
"""
修仙游戏数据初始化脚本
用于向PMSManageBot数据库中添加游戏初始数据
"""
import sqlite3
import json
from pathlib import Path

# 数据库路径
DB_PATH = Path(__file__).parent.parent.parent / "PMSManageBot" / "data" / "data.db"

def init_monsters():
    """初始化怪物数据"""
    monsters = [
        # 凡人境界
        ("野狼", 1, "凡人", 100, 15, 5, 8, 50, 10, 0, "山林中的野狼"),
        ("野猪", 2, "凡人", 150, 18, 8, 6, 60, 15, 0, "凶猛的野猪"),

        # 炼气期
        ("狐妖", 5, "炼气期", 200, 25, 10, 12, 100, 30, 0, "修炼成精的狐狸"),
        ("山贼", 6, "炼气期", 250, 30, 15, 10, 120, 35, 0, "占山为王的山贼"),
        ("邪修", 8, "炼气期", 300, 35, 18, 15, 150, 45, 0, "误入歧途的修士"),

        # 炼气期Boss
        ("狐妖王", 10, "炼气期", 500, 50, 25, 18, 500, 200, 1, "狐妖一族的首领"),

        # 筑基期
        ("妖虎", 12, "筑基期", 400, 45, 22, 20, 200, 60, 0, "深山中的妖虎"),
        ("邪灵", 15, "筑基期", 500, 55, 28, 25, 250, 80, 0, "游荡的邪恶灵体"),
        ("魔修", 18, "筑基期", 600, 65, 35, 30, 300, 100, 0, "堕入魔道的修士"),

        # 筑基期Boss
        ("虎妖王", 20, "筑基期", 1000, 80, 45, 35, 1000, 500, 1, "妖虎一族的王者"),

        # 金丹期
        ("蛟龙", 25, "金丹期", 800, 90, 50, 40, 500, 150, 0, "化形失败的蛟龙"),
        ("魔头", 30, "金丹期", 1000, 110, 60, 50, 600, 200, 0, "作恶多端的魔头"),

        # 金丹期Boss
        ("蛟龙王", 35, "金丹期", 2000, 150, 80, 60, 2000, 1000, 1, "蛟龙一族的霸主"),
    ]

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("DELETE FROM xiuxian_monsters")

    for monster in monsters:
        cur.execute("""
            INSERT INTO xiuxian_monsters
            (name, level, realm, hp, attack, defense, speed, exp_reward, spirit_stones_reward, is_boss, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, monster)

    conn.commit()
    conn.close()
    print(f"✓ 初始化了 {len(monsters)} 个怪物")


def init_items():
    """初始化物品数据"""
    items = [
        # 武器 - 普通
        ("木剑", "WEAPON", "COMMON", "最基础的木制剑",
         json.dumps({"attack": 5}), 100, 1),
        ("铁剑", "WEAPON", "COMMON", "普通的铁剑",
         json.dumps({"attack": 10}), 500, 1),

        # 武器 - 稀有
        ("玄铁重剑", "WEAPON", "UNCOMMON", "重剑无锋，大巧不工",
         json.dumps({"attack": 25, "defense": 5}), 2000, 1),
        ("青锋剑", "WEAPON", "RARE", "削铁如泥的宝剑",
         json.dumps({"attack": 50, "crit_rate": 0.1}), 5000, 1),

        # 武器 - 传说
        ("龙渊剑", "WEAPON", "LEGENDARY", "传说中的神剑",
         json.dumps({"attack": 100, "crit_rate": 0.2, "crit_damage": 1.5}), 20000, 1),

        # 护甲 - 普通
        ("布衣", "ARMOR", "COMMON", "普通的布制衣服",
         json.dumps({"defense": 5, "hp": 50}), 100, 1),
        ("皮甲", "ARMOR", "COMMON", "兽皮制成的护甲",
         json.dumps({"defense": 10, "hp": 100}), 500, 1),

        # 护甲 - 稀有
        ("玄铁甲", "ARMOR", "UNCOMMON", "玄铁打造的重甲",
         json.dumps({"defense": 25, "hp": 300}), 2000, 1),
        ("龙鳞甲", "ARMOR", "RARE", "龙鳞打造的宝甲",
         json.dumps({"defense": 50, "hp": 600}), 5000, 1),

        # 护甲 - 传说
        ("天蚕衣", "ARMOR", "LEGENDARY", "天蚕丝织成的神甲",
         json.dumps({"defense": 100, "hp": 1000, "speed": 10}), 20000, 1),

        # 饰品
        ("灵玉佩", "ACCESSORY", "UNCOMMON", "蕴含灵气的玉佩",
         json.dumps({"spiritual_power": 100, "comprehension": 2}), 3000, 1),
        ("龙凤环", "ACCESSORY", "RARE", "龙凤图案的戒指",
         json.dumps({"attack": 20, "defense": 20, "speed": 10}), 6000, 1),

        # 丹药 - 恢复类
        ("回血丹", "PILL", "COMMON", "恢复生命值",
         json.dumps({"effect": "heal_hp", "value": 200}), 100, 1),
        ("回灵丹", "PILL", "COMMON", "恢复灵力",
         json.dumps({"effect": "heal_sp", "value": 100}), 100, 1),

        # 丹药 - 修炼类
        ("聚气丹", "PILL", "UNCOMMON", "增加修为",
         json.dumps({"effect": "add_exp", "value": 500}), 500, 1),
        ("筑基丹", "PILL", "RARE", "增加突破成功率20%",
         json.dumps({"effect": "breakthrough_bonus", "value": 0.2}), 5000, 1),

        # 丹药 - 永久提升
        ("洗髓丹", "PILL", "LEGENDARY", "永久提升根骨+1",
         json.dumps({"effect": "permanent_root_bone", "value": 1}), 50000, 1),
        ("悟道丹", "PILL", "LEGENDARY", "永久提升悟性+1",
         json.dumps({"effect": "permanent_comprehension", "value": 1}), 50000, 1),

        # 材料
        ("灵草", "MATERIAL", "COMMON", "炼丹材料",
         json.dumps({}), 50, 1),
        ("妖兽内丹", "MATERIAL", "UNCOMMON", "珍贵的炼丹材料",
         json.dumps({}), 500, 1),
    ]

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("DELETE FROM xiuxian_items")

    for item in items:
        cur.execute("""
            INSERT INTO xiuxian_items
            (name, item_type, grade, description, properties, price, is_tradable)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, item)

    conn.commit()
    conn.close()
    print(f"✓ 初始化了 {len(items)} 个物品")


def init_cultivation_methods():
    """初始化功法数据"""
    methods = [
        # 基础功法
        ("五行诀", "COMMON", "最基础的五行功法", 1.2, 50, 5, 5, "凡人", 1000),
        ("玄元功", "UNCOMMON", "道家基础功法", 1.5, 100, 10, 10, "炼气期", 5000),

        # 中级功法
        ("紫霄神功", "RARE", "传承久远的紫霄功法", 1.8, 200, 20, 20, "筑基期", 10000),
        ("九转金丹诀", "RARE", "金丹期功法", 2.0, 300, 30, 30, "金丹期", 20000),

        # 高级功法
        ("太乙真经", "EPIC", "太乙门不传之秘", 2.5, 500, 50, 50, "元婴期", 50000),
        ("混元天功", "LEGENDARY", "上古功法残篇", 3.0, 1000, 100, 100, "化神期", 100000),
    ]

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("DELETE FROM xiuxian_cultivation_methods")

    for method in methods:
        cur.execute("""
            INSERT INTO xiuxian_cultivation_methods
            (name, grade, description, speed_bonus, hp_bonus, attack_bonus, defense_bonus, requirement_realm, price)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, method)

    conn.commit()
    conn.close()
    print(f"✓ 初始化了 {len(methods)} 个功法")


def init_skills():
    """初始化技能数据"""
    skills = [
        # 攻击技能
        ("破空斩", "ATTACK", "挥剑破空，造成150%伤害", 20,
         json.dumps({"damage_multiplier": 1.5}), 0, "炼气期"),
        ("烈焰掌", "ATTACK", "烈焰焚身，造成200%火焰伤害", 30,
         json.dumps({"damage_multiplier": 2.0, "element": "fire"}), 0, "筑基期"),

        # 防御技能
        ("金刚护体", "DEFENSE", "金刚罩体，减少50%伤害持续2回合", 25,
         json.dumps({"damage_reduction": 0.5, "duration": 2}), 0, "炼气期"),

        # 治疗技能
        ("回春术", "HEAL", "恢复30%最大生命值", 20,
         json.dumps({"heal_percent": 0.3}), 0, "炼气期"),

        # 增益技能
        ("御风术", "BUFF", "提升速度50%持续3回合", 15,
         json.dumps({"speed_boost": 0.5, "duration": 3}), 0, "炼气期"),
    ]

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("DELETE FROM xiuxian_skills")

    for skill in skills:
        cur.execute("""
            INSERT INTO xiuxian_skills
            (name, skill_type, description, spiritual_power_cost, effects, cooldown_seconds, requirement_realm)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, skill)

    conn.commit()
    conn.close()
    print(f"✓ 初始化了 {len(skills)} 个技能")


def init_quests():
    """初始化任务数据"""
    quests = [
        # 主线任务
        ("踏入修仙", "MAIN", "完成第一次修炼",
         json.dumps({"type": "cultivate", "count": 1}),
         json.dumps({"exp": 100, "spirit_stones": 500}),
         "凡人", 0),

        ("初次战斗", "MAIN", "战胜第一个敌人",
         json.dumps({"type": "battle_win", "count": 1}),
         json.dumps({"exp": 200, "spirit_stones": 1000}),
         "凡人", 0),

        ("境界提升", "MAIN", "突破到炼气期1层",
         json.dumps({"type": "breakthrough", "target_realm": "炼气期"}),
         json.dumps({"exp": 500, "spirit_stones": 2000, "item_id": 1}),
         "凡人", 0),

        # 每日任务
        ("每日修炼", "DAILY", "完成2小时修炼",
         json.dumps({"type": "cultivate", "hours": 2}),
         json.dumps({"spirit_stones": 500}),
         None, 1),

        ("每日战斗", "DAILY", "战胜3个敌人",
         json.dumps({"type": "battle_win", "count": 3}),
         json.dumps({"spirit_stones": 1000}),
         None, 1),

        # 周常任务
        ("每周修炼", "WEEKLY", "累计修炼20小时",
         json.dumps({"type": "cultivate", "hours": 20}),
         json.dumps({"spirit_stones": 5000, "item_id": 14}),
         None, 1),
    ]

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("DELETE FROM xiuxian_quests")

    for quest in quests:
        cur.execute("""
            INSERT INTO xiuxian_quests
            (name, quest_type, description, objectives, rewards, requirement_realm, is_repeatable)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, quest)

    conn.commit()
    conn.close()
    print(f"✓ 初始化了 {len(quests)} 个任务")


def init_achievements():
    """初始化成就数据"""
    achievements = [
        ("初出茅庐", "第一次修炼", "cultivate_count", 1,
         json.dumps({"spirit_stones": 1000})),
        ("修炼狂人", "累计修炼100小时", "cultivate_hours", 100,
         json.dumps({"spirit_stones": 10000, "title": "修炼狂人"})),

        ("初尝胜利", "第一次战斗胜利", "battle_win", 1,
         json.dumps({"spirit_stones": 1000})),
        ("百战百胜", "累计胜利100场", "battle_win", 100,
         json.dumps({"spirit_stones": 20000, "title": "百战百胜"})),

        ("小有成就", "突破到筑基期", "realm_level", 1,
         json.dumps({"spirit_stones": 5000})),
        ("金丹大道", "突破到金丹期", "realm_level", 2,
         json.dumps({"spirit_stones": 50000})),

        ("灵石富翁", "拥有100000灵石", "spirit_stones", 100000,
         json.dumps({"title": "灵石富翁"})),
    ]

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("DELETE FROM xiuxian_achievements")

    for achievement in achievements:
        cur.execute("""
            INSERT INTO xiuxian_achievements
            (name, description, condition_type, condition_value, rewards)
            VALUES (?, ?, ?, ?, ?)
        """, achievement)

    conn.commit()
    conn.close()
    print(f"✓ 初始化了 {len(achievements)} 个成就")


def main():
    """主函数"""
    print("=" * 50)
    print("修仙游戏数据初始化")
    print("=" * 50)

    if not DB_PATH.exists():
        print(f"❌ 数据库文件不存在: {DB_PATH}")
        print("请先运行数据库迁移脚本")
        return

    print(f"\n数据库路径: {DB_PATH}\n")

    try:
        init_monsters()
        init_items()
        init_cultivation_methods()
        init_skills()
        init_quests()
        init_achievements()

        print("\n" + "=" * 50)
        print("✅ 数据初始化完成！")
        print("=" * 50)

    except Exception as e:
        print(f"\n❌ 初始化失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
