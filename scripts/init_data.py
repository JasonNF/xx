"""初始化游戏数据脚本"""
import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from bot.models import get_db, Monster, Item, ItemType, ItemGrade, CultivationMethod, RealmType, Skill
from bot.models.player import RealmType


async def init_monsters():
    """初始化怪物数据"""
    print("初始化怪物数据...")

    monsters_data = [
        # 炼气期怪物
        {"name": "野狼", "description": "普通野狼", "level": 1, "realm": "炼气期",
         "hp": 150, "attack": 15, "defense": 8, "speed": 12,
         "exp_reward": 50, "spirit_stones_min": 10, "spirit_stones_max": 30, "is_boss": False},
        {"name": "狐妖", "description": "修炼有成的狐妖", "level": 3, "realm": "炼气期",
         "hp": 200, "attack": 20, "defense": 10, "speed": 15,
         "exp_reward": 80, "spirit_stones_min": 20, "spirit_stones_max": 50, "is_boss": False},
        {"name": "炼气期Boss - 山贼头目", "description": "盘踞山头的强盗头子", "level": 9, "realm": "炼气期",
         "hp": 500, "attack": 50, "defense": 25, "speed": 20,
         "exp_reward": 500, "spirit_stones_min": 100, "spirit_stones_max": 200, "is_boss": True},

        # 筑基期怪物
        {"name": "赤焰蛇", "description": "修炼火属性的蛇妖", "level": 1, "realm": "筑基期",
         "hp": 800, "attack": 80, "defense": 40, "speed": 30,
         "exp_reward": 300, "spirit_stones_min": 50, "spirit_stones_max": 100, "is_boss": False},
        {"name": "水晶蝎", "description": "全身晶莹剔透的毒蝎", "level": 5, "realm": "筑基期",
         "hp": 1200, "attack": 100, "defense": 60, "speed": 35,
         "exp_reward": 500, "spirit_stones_min": 100, "spirit_stones_max": 200, "is_boss": False},

        # 金丹期怪物
        {"name": "黑熊精", "description": "力大无穷的熊妖", "level": 1, "realm": "金丹期",
         "hp": 3000, "attack": 200, "defense": 150, "speed": 40,
         "exp_reward": 1000, "spirit_stones_min": 200, "spirit_stones_max": 500, "is_boss": False},
    ]

    async with get_db() as db:
        for data in monsters_data:
            monster = Monster(**data)
            db.add(monster)
        await db.commit()

    print(f"✅ 初始化了 {len(monsters_data)} 个怪物")


async def init_items():
    """初始化物品数据"""
    print("初始化物品数据...")

    items_data = [
        # 武器
        {"name": "木剑", "description": "普通的木制剑", "item_type": ItemType.WEAPON, "grade": ItemGrade.COMMON,
         "buy_price": 100, "sell_price": 20, "attack_bonus": 5, "is_tradable": True},
        {"name": "铁剑", "description": "铁制长剑", "item_type": ItemType.WEAPON, "grade": ItemGrade.UNCOMMON,
         "buy_price": 500, "sell_price": 100, "attack_bonus": 15, "is_tradable": True},
        {"name": "青锋剑", "description": "锋利的法器长剑", "item_type": ItemType.WEAPON, "grade": ItemGrade.RARE,
         "buy_price": 2000, "sell_price": 500, "attack_bonus": 50, "crit_rate_bonus": 0.05, "is_tradable": True},

        # 护甲
        {"name": "布衣", "description": "普通布衣", "item_type": ItemType.ARMOR, "grade": ItemGrade.COMMON,
         "buy_price": 80, "sell_price": 15, "defense_bonus": 3, "hp_bonus": 20, "is_tradable": True},
        {"name": "皮甲", "description": "兽皮制成的护甲", "item_type": ItemType.ARMOR, "grade": ItemGrade.UNCOMMON,
         "buy_price": 400, "sell_price": 80, "defense_bonus": 10, "hp_bonus": 50, "is_tradable": True},

        # 饰品
        {"name": "玉佩", "description": "温润的玉石佩饰", "item_type": ItemType.ACCESSORY, "grade": ItemGrade.UNCOMMON,
         "buy_price": 600, "sell_price": 120, "spiritual_bonus": 50, "is_tradable": True},

        # 丹药
        {"name": "回春丹", "description": "恢复生命值的丹药", "item_type": ItemType.PILL, "grade": ItemGrade.COMMON,
         "buy_price": 200, "sell_price": 40, "hp_restore": 200, "is_stackable": True, "max_stack": 99},
        {"name": "回灵丹", "description": "恢复灵力的丹药", "item_type": ItemType.PILL, "grade": ItemGrade.COMMON,
         "buy_price": 150, "sell_price": 30, "spiritual_restore": 150, "is_stackable": True, "max_stack": 99},
        {"name": "筑基丹", "description": "帮助筑基的珍贵丹药", "item_type": ItemType.PILL, "grade": ItemGrade.RARE,
         "buy_price": 5000, "sell_price": 1000, "exp_bonus": 5000, "is_stackable": True, "max_stack": 10},
    ]

    async with get_db() as db:
        for data in items_data:
            item = Item(**data)
            db.add(item)
        await db.commit()

    print(f"✅ 初始化了 {len(items_data)} 个物品")


async def init_cultivation_methods():
    """初始化功法数据"""
    print("初始化功法数据...")

    methods_data = [
        {"name": "基础吐纳术", "description": "最基础的修炼功法", "grade": "黄",
         "cultivation_speed_bonus": 1.0, "required_realm": RealmType.MORTAL, "required_level": 1, "learning_cost": 0},
        {"name": "五行诀", "description": "五行属性均衡的功法", "grade": "玄",
         "cultivation_speed_bonus": 1.5, "attack_bonus": 10, "required_realm": RealmType.QI_REFINING, "required_level": 5, "learning_cost": 1000},
        {"name": "紫霄神功", "description": "雷属性顶级功法", "grade": "地",
         "cultivation_speed_bonus": 2.0, "attack_bonus": 30, "speed_bonus": 10,
         "required_realm": RealmType.FOUNDATION, "required_level": 1, "learning_cost": 5000},
        {"name": "九转玄功", "description": "传说中的仙家功法", "grade": "天",
         "cultivation_speed_bonus": 3.0, "attack_bonus": 100, "defense_bonus": 50, "hp_bonus": 500,
         "required_realm": RealmType.GOLDEN_CORE, "required_level": 1, "learning_cost": 50000},
    ]

    async with get_db() as db:
        for data in methods_data:
            method = CultivationMethod(**data)
            db.add(method)
        await db.commit()

    print(f"✅ 初始化了 {len(methods_data)} 个功法")


async def main():
    """主函数"""
    print("="*50)
    print("修仙世界 - 游戏数据初始化")
    print("="*50)

    try:
        await init_monsters()
        await init_items()
        await init_cultivation_methods()

        print("\n"+"="*50)
        print("✨ 游戏数据初始化完成！")
        print("="*50)

    except Exception as e:
        print(f"\n❌ 初始化失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
