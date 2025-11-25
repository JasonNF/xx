"""炼丹系统初始化脚本 - 凡人修仙传版本"""
import asyncio
import json
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from bot.models.database import init_db, AsyncSessionLocal
from bot.models.item import Item, ItemType
from bot.models.alchemy import PillRecipe
from sqlalchemy import select


async def create_alchemy_materials():
    """创建炼丹材料（16种灵药）"""
    async with AsyncSessionLocal() as session:
        materials = [
            # 基础灵草（4种）
            {
                "name": "青灵草",
                "description": "最基础的灵草，生长在灵气充沛之地，常用于炼制回春丹等基础丹药",
                "item_type": ItemType.HERB,
                "herb_age": 10,
                "buy_price": 50,
                "sell_price": 25,
                "is_stackable": True,
                "max_stack": 999,
            },
            {
                "name": "碧心花",
                "description": "蓝色小花，蕴含纯净灵力，是恢复灵力丹药的主要材料",
                "item_type": ItemType.HERB,
                "herb_age": 20,
                "buy_price": 80,
                "sell_price": 40,
                "is_stackable": True,
                "max_stack": 999,
            },
            {
                "name": "紫云芝",
                "description": "紫色云纹灵芝，可增强修为，炼气期修士常用",
                "item_type": ItemType.HERB,
                "herb_age": 50,
                "buy_price": 150,
                "sell_price": 75,
                "is_stackable": True,
                "max_stack": 999,
            },
            {
                "name": "金线藤",
                "description": "藤蔓上有金色纹路，强化体魄的珍贵材料",
                "item_type": ItemType.HERB,
                "herb_age": 30,
                "buy_price": 200,
                "sell_price": 100,
                "is_stackable": True,
                "max_stack": 999,
            },

            # 中级灵药（5种，玉随芝已存在，跳过）
            {
                "name": "赤火果",
                "description": "火红色灵果，内含炽热火灵力，提升火属性法术威力",
                "item_type": ItemType.HERB,
                "herb_age": 100,
                "buy_price": 5000,
                "sell_price": 2500,
                "is_stackable": True,
                "max_stack": 99,
            },
            {
                "name": "寒冰莲",
                "description": "生长在寒潭的莲花，清心凝神，水属性灵物",
                "item_type": ItemType.HERB,
                "herb_age": 120,
                "buy_price": 6000,
                "sell_price": 3000,
                "is_stackable": True,
                "max_stack": 99,
            },
            {
                "name": "金刚果",
                "description": "坚硬如铁的金色灵果，服用后可强化防御",
                "item_type": ItemType.HERB,
                "herb_age": 80,
                "buy_price": 4000,
                "sell_price": 2000,
                "is_stackable": True,
                "max_stack": 99,
            },
            {
                "name": "九幽草",
                "description": "阴属性灵草，解毒排毒的珍稀灵药",
                "item_type": ItemType.HERB,
                "herb_age": 150,
                "buy_price": 8000,
                "sell_price": 4000,
                "is_stackable": True,
                "max_stack": 99,
            },

            # 高级灵物（5种）
            {
                "name": "天灵果",
                "description": "千年才结一次果的灵树之果，结丹灵物之一",
                "item_type": ItemType.HERB,
                "herb_age": 1000,
                "buy_price": 100000,
                "sell_price": 50000,
                "is_stackable": True,
                "max_stack": 10,
            },
            {
                "name": "紫髓晶",
                "description": "紫色晶石，内含生命精华，元婴期疗伤圣药材料",
                "item_type": ItemType.HERB,
                "herb_age": 500,
                "buy_price": 80000,
                "sell_price": 40000,
                "is_stackable": True,
                "max_stack": 20,
            },
            {
                "name": "龙血草",
                "description": "传说被妖兽龙血滋养的灵草，极其罕见",
                "item_type": ItemType.HERB,
                "herb_age": 800,
                "buy_price": 150000,
                "sell_price": 75000,
                "is_stackable": True,
                "max_stack": 10,
            },
            {
                "name": "凤羽花",
                "description": "极阳之物，花瓣如凤凰羽毛，破婴丹辅药",
                "item_type": ItemType.HERB,
                "herb_age": 1200,
                "buy_price": 200000,
                "sell_price": 100000,
                "is_stackable": True,
                "max_stack": 10,
            },
            {
                "name": "星月露",
                "description": "夜间吸收星月之力凝聚的露水，灵气纯净",
                "item_type": ItemType.HERB,
                "herb_age": 0,  # 露水没有年份
                "buy_price": 50000,
                "sell_price": 25000,
                "is_stackable": True,
                "max_stack": 50,
            },

            # 顶级仙药（2种）
            {
                "name": "血参精",
                "description": "万年血参的精华，元婴期至宝",
                "item_type": ItemType.HERB,
                "herb_age": 10000,
                "buy_price": 2000000,
                "sell_price": 1000000,
                "is_stackable": True,
                "max_stack": 5,
            },
            {
                "name": "化神花",
                "description": "化神灵物，人界罕见，传说中的仙药",
                "item_type": ItemType.HERB,
                "herb_age": 5000,
                "buy_price": 10000000,
                "sell_price": 5000000,
                "is_stackable": True,
                "max_stack": 3,
            },
        ]

        added_count = 0
        skipped_count = 0

        for material_data in materials:
            # 检查是否已存在
            result = await session.execute(
                select(Item).where(Item.name == material_data["name"])
            )
            if result.scalar_one_or_none():
                print(f"⏭️  跳过：{material_data['name']}（已存在）")
                skipped_count += 1
                continue

            material = Item(**material_data)
            session.add(material)
            added_count += 1
            print(f"✅ 创建材料：{material_data['name']} - {material_data['herb_age']}年 - {material_data['buy_price']:,}灵石")

        await session.commit()
        print(f"\n🎉 炼丹材料创建完成！新增 {added_count} 种，跳过 {skipped_count} 种")
        return added_count


async def create_alchemy_pills():
    """创建丹药物品（36种）"""
    async with AsyncSessionLocal() as session:
        pills = [
            # 凡品丹药（8种）- 筑基丹、回春丹、聚灵丹已存在
            {
                "name": "炼气丹",
                "description": "增加修为的基础丹药，适合炼气期修士",
                "item_type": ItemType.PILL,
                "exp_bonus": 500,
                "buy_price": 1500,
                "sell_price": 800,
                "is_stackable": True,
                "max_stack": 99,
            },
            {
                "name": "凝气丹",
                "description": "永久增加灵力上限的珍贵丹药",
                "item_type": ItemType.PILL,
                "spiritual_bonus": 20,
                "buy_price": 3000,
                "sell_price": 1500,
                "is_stackable": True,
                "max_stack": 50,
            },
            {
                "name": "强体丹",
                "description": "永久增强体魄的丹药",
                "item_type": ItemType.PILL,
                "hp_bonus": 30,
                "buy_price": 3000,
                "sell_price": 1500,
                "is_stackable": True,
                "max_stack": 50,
            },
            {
                "name": "清心丹",
                "description": "解除中毒、虚弱等负面状态的丹药",
                "item_type": ItemType.PILL,
                "hp_restore": 100,
                "buy_price": 4000,
                "sell_price": 2000,
                "is_stackable": True,
                "max_stack": 99,
                "special_ability": "解除所有负面状态",
            },
            {
                "name": "疾速丹",
                "description": "短时间内大幅提升速度的丹药",
                "item_type": ItemType.PILL,
                "speed_bonus": 50,
                "buy_price": 5000,
                "sell_price": 2500,
                "is_stackable": True,
                "max_stack": 99,
                "special_ability": "30分钟内速度+50%",
            },
            {
                "name": "防御丹",
                "description": "短时间内大幅提升防御的丹药",
                "item_type": ItemType.PILL,
                "defense_bonus": 50,
                "buy_price": 6000,
                "sell_price": 3000,
                "is_stackable": True,
                "max_stack": 99,
                "special_ability": "30分钟内防御+50%",
            },

            # 灵品丹药（10种）- 筑基丹已存在
            {
                "name": "大回春丹",
                "description": "高级疗伤丹药，迅速恢复大量生命值",
                "item_type": ItemType.PILL,
                "hp_restore": 2000,
                "buy_price": 15000,
                "sell_price": 8000,
                "is_stackable": True,
                "max_stack": 99,
            },
            {
                "name": "大聚灵丹",
                "description": "高级恢复灵力的丹药",
                "item_type": ItemType.PILL,
                "spiritual_restore": 1000,
                "buy_price": 12000,
                "sell_price": 6000,
                "is_stackable": True,
                "max_stack": 99,
            },
            {
                "name": "增元丹",
                "description": "大幅增加修为的珍贵丹药",
                "item_type": ItemType.PILL,
                "exp_bonus": 3000,
                "buy_price": 30000,
                "sell_price": 15000,
                "is_stackable": True,
                "max_stack": 50,
            },
            {
                "name": "火灵丹",
                "description": "提升火属性法术威力的丹药",
                "item_type": ItemType.PILL,
                "attack_bonus": 30,
                "buy_price": 20000,
                "sell_price": 10000,
                "is_stackable": True,
                "max_stack": 50,
                "special_ability": "7天内火属性法术伤害+30%",
            },
            {
                "name": "冰魄丹",
                "description": "提升水属性法术威力的丹药",
                "item_type": ItemType.PILL,
                "attack_bonus": 30,
                "buy_price": 20000,
                "sell_price": 10000,
                "is_stackable": True,
                "max_stack": 50,
                "special_ability": "7天内水属性法术伤害+30%",
            },
            {
                "name": "破障丹",
                "description": "辅助小境界突破的丹药",
                "item_type": ItemType.PILL,
                "breakthrough_bonus": 0.2,
                "buy_price": 40000,
                "sell_price": 20000,
                "is_stackable": True,
                "max_stack": 20,
                "special_ability": "炼气期小境界突破成功率+20%",
            },
            {
                "name": "金身丹",
                "description": "永久增强防御力的珍贵丹药",
                "item_type": ItemType.PILL,
                "defense_bonus": 50,
                "buy_price": 50000,
                "sell_price": 25000,
                "is_stackable": True,
                "max_stack": 20,
            },
            {
                "name": "疗毒丹",
                "description": "治疗剧毒的高级丹药",
                "item_type": ItemType.PILL,
                "hp_restore": 500,
                "buy_price": 25000,
                "sell_price": 12000,
                "is_stackable": True,
                "max_stack": 99,
                "special_ability": "解除所有中毒效果",
            },
            {
                "name": "灵智丹",
                "description": "提升悟性的珍稀丹药",
                "item_type": ItemType.PILL,
                "exp_bonus": 1000,
                "buy_price": 70000,
                "sell_price": 35000,
                "is_stackable": True,
                "max_stack": 10,
                "special_ability": "7天内修炼速度+20%,顿悟几率+5%",
            },

            # 宝品丹药（8种）- 凝金丹已存在
            {
                "name": "返魂丹",
                "description": "起死回生的灵丹妙药",
                "item_type": ItemType.PILL,
                "hp_restore": 5000,
                "spiritual_restore": 3000,
                "buy_price": 200000,
                "sell_price": 100000,
                "is_stackable": True,
                "max_stack": 10,
                "special_ability": "濒死状态下自动触发,恢复50%生命和灵力",
            },
            {
                "name": "金丹培元丹",
                "description": "金丹期修士的修为丹药",
                "item_type": ItemType.PILL,
                "exp_bonus": 20000,
                "buy_price": 600000,
                "sell_price": 300000,
                "is_stackable": True,
                "max_stack": 20,
            },
            {
                "name": "龙虎丹",
                "description": "大幅提升战力的猛药",
                "item_type": ItemType.PILL,
                "attack_bonus": 100,
                "defense_bonus": 50,
                "buy_price": 300000,
                "sell_price": 150000,
                "is_stackable": True,
                "max_stack": 20,
                "special_ability": "1小时内攻击+100%,防御+50%",
            },
            {
                "name": "破瓶丹",
                "description": "辅助金丹期小境界突破",
                "item_type": ItemType.PILL,
                "breakthrough_bonus": 0.3,
                "buy_price": 800000,
                "sell_price": 400000,
                "is_stackable": True,
                "max_stack": 10,
                "special_ability": "金丹期小境界突破成功率+30%",
            },
            {
                "name": "五行丹",
                "description": "增强所有五行法术的高级丹药",
                "item_type": ItemType.PILL,
                "attack_bonus": 50,
                "spiritual_bonus": 100,
                "buy_price": 1000000,
                "sell_price": 500000,
                "is_stackable": True,
                "max_stack": 10,
                "special_ability": "30天内所有五行法术伤害+50%",
            },
            {
                "name": "紫髓丹",
                "description": "疗伤圣药，可治愈重伤",
                "item_type": ItemType.PILL,
                "hp_restore": 8000,
                "buy_price": 700000,
                "sell_price": 350000,
                "is_stackable": True,
                "max_stack": 10,
            },
            {
                "name": "固元丹",
                "description": "永久增加灵力上限的高级丹药",
                "item_type": ItemType.PILL,
                "spiritual_bonus": 100,
                "buy_price": 1200000,
                "sell_price": 600000,
                "is_stackable": True,
                "max_stack": 10,
            },

            # 仙品丹药（6种）
            {
                "name": "破婴丹",
                "description": "辅助凝婴的传说丹药",
                "item_type": ItemType.PILL,
                "breakthrough_bonus": 0.2,
                "buy_price": 4000000,
                "sell_price": 2000000,
                "is_stackable": True,
                "max_stack": 5,
                "special_ability": "提升20%元婴突破成功率",
            },
            {
                "name": "元婴培元丹",
                "description": "元婴期修为丹药",
                "item_type": ItemType.PILL,
                "exp_bonus": 100000,
                "buy_price": 3000000,
                "sell_price": 1500000,
                "is_stackable": True,
                "max_stack": 10,
            },
            {
                "name": "涅槃丹",
                "description": "复活丹药，死后重生",
                "item_type": ItemType.PILL,
                "hp_restore": 10000,
                "spiritual_restore": 5000,
                "buy_price": 6000000,
                "sell_price": 3000000,
                "is_stackable": True,
                "max_stack": 3,
                "special_ability": "死亡后自动复活,恢复50%状态",
            },
            {
                "name": "化婴丹",
                "description": "强化元婴的仙丹",
                "item_type": ItemType.PILL,
                "attack_bonus": 200,
                "defense_bonus": 200,
                "hp_bonus": 200,
                "spiritual_bonus": 200,
                "buy_price": 10000000,
                "sell_price": 5000000,
                "is_stackable": True,
                "max_stack": 5,
            },
            {
                "name": "续命丹",
                "description": "延长寿元的宝丹",
                "item_type": ItemType.PILL,
                "buy_price": 5000000,
                "sell_price": 2500000,
                "is_stackable": True,
                "max_stack": 5,
                "special_ability": "延长寿元100年",
            },
            {
                "name": "神通丹",
                "description": "有机会领悟神通的逆天丹药",
                "item_type": ItemType.PILL,
                "buy_price": 16000000,
                "sell_price": 8000000,
                "is_stackable": True,
                "max_stack": 3,
                "special_ability": "有一定几率领悟一门神通技能",
            },

            # 神品丹药（4种）
            {
                "name": "化神丹",
                "description": "辅助化神突破的仙丹",
                "item_type": ItemType.PILL,
                "breakthrough_bonus": 0.15,
                "buy_price": 40000000,
                "sell_price": 20000000,
                "is_stackable": True,
                "max_stack": 3,
                "special_ability": "提升15%化神突破成功率",
            },
            {
                "name": "化神培元丹",
                "description": "化神期修为丹药",
                "item_type": ItemType.PILL,
                "exp_bonus": 500000,
                "buy_price": 30000000,
                "sell_price": 15000000,
                "is_stackable": True,
                "max_stack": 5,
            },
            {
                "name": "天劫丹",
                "description": "抵抗天劫的神丹",
                "item_type": ItemType.PILL,
                "buy_price": 60000000,
                "sell_price": 30000000,
                "is_stackable": True,
                "max_stack": 3,
                "special_ability": "渡劫时抵抗一次天雷攻击",
            },
            {
                "name": "大还丹",
                "description": "起死回生圣药，完全恢复",
                "item_type": ItemType.PILL,
                "hp_restore": 999999,
                "spiritual_restore": 999999,
                "buy_price": 50000000,
                "sell_price": 25000000,
                "is_stackable": True,
                "max_stack": 3,
                "special_ability": "完全恢复所有生命和灵力,治愈一切伤势",
            },
        ]

        added_count = 0
        skipped_count = 0

        for pill_data in pills:
            # 检查是否已存在
            result = await session.execute(
                select(Item).where(Item.name == pill_data["name"])
            )
            if result.scalar_one_or_none():
                print(f"⏭️  跳过：{pill_data['name']}（已存在）")
                skipped_count += 1
                continue

            pill = Item(**pill_data)
            session.add(pill)
            added_count += 1
            print(f"✅ 创建丹药：{pill_data['name']} - {pill_data['buy_price']:,}灵石")

        await session.commit()
        print(f"\n🎉 丹药创建完成！新增 {added_count} 种，跳过 {skipped_count} 种")
        return added_count


async def create_pill_recipes():
    """创建丹方配方（36种）"""
    async with AsyncSessionLocal() as session:
        # 获取所有物品，建立名称到ID的映射
        result = await session.execute(select(Item))
        items = result.scalars().all()
        item_map = {item.name: item.id for item in items}

        # 定义所有丹方
        recipes = [
            # 凡品丹药（8种）
            {
                "name": "回春丹丹方",
                "description": "基础疗伤丹药配方，适合新手炼丹师",
                "result_pill": "回春丹",
                "result_quantity_min": 1,
                "result_quantity_max": 3,
                "required_alchemy_level": 1,
                "base_success_rate": 0.9,
                "ingredients": [
                    {"item": "青灵草", "quantity": 3},
                    {"item": "碧心花", "quantity": 2},
                ],
                "spiritual_power_cost": 30,
                "duration_hours": 1,  # 0.5小时用1表示
            },
            {
                "name": "聚灵丹丹方",
                "description": "基础恢复灵力丹药配方",
                "result_pill": "聚灵丹",
                "result_quantity_min": 1,
                "result_quantity_max": 3,
                "required_alchemy_level": 1,
                "base_success_rate": 0.9,
                "ingredients": [
                    {"item": "碧心花", "quantity": 3},
                    {"item": "紫云芝", "quantity": 2},
                ],
                "spiritual_power_cost": 30,
                "duration_hours": 1,
            },
            {
                "name": "炼气丹丹方",
                "description": "增加修为的基础丹药配方",
                "result_pill": "炼气丹",
                "result_quantity_min": 1,
                "result_quantity_max": 2,
                "required_alchemy_level": 1,
                "base_success_rate": 0.85,
                "ingredients": [
                    {"item": "紫云芝", "quantity": 4},
                    {"item": "青灵草", "quantity": 3},
                ],
                "spiritual_power_cost": 40,
                "duration_hours": 1,
            },
            {
                "name": "凝气丹丹方",
                "description": "永久增加灵力上限的丹药配方",
                "result_pill": "凝气丹",
                "result_quantity_min": 1,
                "result_quantity_max": 1,
                "required_alchemy_level": 2,
                "base_success_rate": 0.8,
                "ingredients": [
                    {"item": "碧心花", "quantity": 4},
                    {"item": "金线藤", "quantity": 2},
                ],
                "spiritual_power_cost": 50,
                "duration_hours": 1,
            },
            {
                "name": "强体丹丹方",
                "description": "增强体魄的丹药配方",
                "result_pill": "强体丹",
                "result_quantity_min": 1,
                "result_quantity_max": 1,
                "required_alchemy_level": 2,
                "base_success_rate": 0.8,
                "ingredients": [
                    {"item": "金线藤", "quantity": 4},
                    {"item": "青灵草", "quantity": 2},
                ],
                "spiritual_power_cost": 50,
                "duration_hours": 1,
            },
            {
                "name": "清心丹丹方",
                "description": "去除负面状态的丹药配方",
                "result_pill": "清心丹",
                "result_quantity_min": 1,
                "result_quantity_max": 2,
                "required_alchemy_level": 2,
                "base_success_rate": 0.75,
                "ingredients": [
                    {"item": "寒冰莲", "quantity": 2},
                    {"item": "碧心花", "quantity": 3},
                ],
                "spiritual_power_cost": 60,
                "duration_hours": 2,
            },
            {
                "name": "疾速丹丹方",
                "description": "短时提升速度的丹药配方",
                "result_pill": "疾速丹",
                "result_quantity_min": 1,
                "result_quantity_max": 2,
                "required_alchemy_level": 3,
                "base_success_rate": 0.75,
                "ingredients": [
                    {"item": "金线藤", "quantity": 3},
                    {"item": "紫云芝", "quantity": 3},
                ],
                "spiritual_power_cost": 60,
                "duration_hours": 2,
            },
            {
                "name": "防御丹丹方",
                "description": "短时提升防御的丹药配方",
                "result_pill": "防御丹",
                "result_quantity_min": 1,
                "result_quantity_max": 2,
                "required_alchemy_level": 3,
                "base_success_rate": 0.7,
                "ingredients": [
                    {"item": "金刚果", "quantity": 2},
                    {"item": "青灵草", "quantity": 4},
                ],
                "spiritual_power_cost": 60,
                "duration_hours": 2,
            },

            # 灵品丹药（10种）
            {
                "name": "筑基丹丹方",
                "description": "辅助筑基的珍贵丹方，七派秘传",
                "result_pill": "筑基丹",
                "result_quantity_min": 1,
                "result_quantity_max": 1,
                "required_alchemy_level": 5,
                "base_success_rate": 0.6,
                "ingredients": [
                    {"item": "玉随芝", "quantity": 2},
                    {"item": "紫云芝", "quantity": 5},
                    {"item": "碧心花", "quantity": 5},
                ],
                "spiritual_power_cost": 100,
                "duration_hours": 4,
            },
            {
                "name": "大回春丹丹方",
                "description": "高级疗伤丹药配方",
                "result_pill": "大回春丹",
                "result_quantity_min": 1,
                "result_quantity_max": 2,
                "required_alchemy_level": 4,
                "base_success_rate": 0.65,
                "ingredients": [
                    {"item": "青灵草", "quantity": 5},
                    {"item": "玉随芝", "quantity": 1},
                    {"item": "寒冰莲", "quantity": 2},
                ],
                "spiritual_power_cost": 80,
                "duration_hours": 2,
            },
            {
                "name": "大聚灵丹丹方",
                "description": "高级恢复灵力丹药配方",
                "result_pill": "大聚灵丹",
                "result_quantity_min": 1,
                "result_quantity_max": 2,
                "required_alchemy_level": 4,
                "base_success_rate": 0.65,
                "ingredients": [
                    {"item": "碧心花", "quantity": 5},
                    {"item": "玉随芝", "quantity": 1},
                    {"item": "紫云芝", "quantity": 3},
                ],
                "spiritual_power_cost": 80,
                "duration_hours": 2,
            },
            {
                "name": "增元丹丹方",
                "description": "大幅增加修为的珍贵丹方",
                "result_pill": "增元丹",
                "result_quantity_min": 1,
                "result_quantity_max": 1,
                "required_alchemy_level": 5,
                "base_success_rate": 0.6,
                "ingredients": [
                    {"item": "紫云芝", "quantity": 6},
                    {"item": "玉随芝", "quantity": 1},
                    {"item": "赤火果", "quantity": 2},
                ],
                "spiritual_power_cost": 100,
                "duration_hours": 3,
            },
            {
                "name": "火灵丹丹方",
                "description": "提升火属性法术威力的丹方",
                "result_pill": "火灵丹",
                "result_quantity_min": 1,
                "result_quantity_max": 1,
                "required_alchemy_level": 5,
                "base_success_rate": 0.55,
                "ingredients": [
                    {"item": "赤火果", "quantity": 3},
                    {"item": "紫云芝", "quantity": 3},
                    {"item": "金线藤", "quantity": 2},
                ],
                "spiritual_power_cost": 90,
                "duration_hours": 2,
            },
            {
                "name": "冰魄丹丹方",
                "description": "提升水属性法术威力的丹方",
                "result_pill": "冰魄丹",
                "result_quantity_min": 1,
                "result_quantity_max": 1,
                "required_alchemy_level": 5,
                "base_success_rate": 0.55,
                "ingredients": [
                    {"item": "寒冰莲", "quantity": 3},
                    {"item": "紫云芝", "quantity": 3},
                    {"item": "碧心花", "quantity": 3},
                ],
                "spiritual_power_cost": 90,
                "duration_hours": 2,
            },
            {
                "name": "破障丹丹方",
                "description": "辅助小境界突破的丹方",
                "result_pill": "破障丹",
                "result_quantity_min": 1,
                "result_quantity_max": 1,
                "required_alchemy_level": 6,
                "base_success_rate": 0.5,
                "ingredients": [
                    {"item": "玉随芝", "quantity": 1},
                    {"item": "紫云芝", "quantity": 5},
                    {"item": "九幽草", "quantity": 2},
                ],
                "spiritual_power_cost": 120,
                "duration_hours": 3,
            },
            {
                "name": "金身丹丹方",
                "description": "永久增强防御的丹方",
                "result_pill": "金身丹",
                "result_quantity_min": 1,
                "result_quantity_max": 1,
                "required_alchemy_level": 6,
                "base_success_rate": 0.5,
                "ingredients": [
                    {"item": "金刚果", "quantity": 3},
                    {"item": "玉随芝", "quantity": 1},
                    {"item": "金线藤", "quantity": 5},
                ],
                "spiritual_power_cost": 120,
                "duration_hours": 3,
            },
            {
                "name": "疗毒丹丹方",
                "description": "治疗剧毒的高级丹方",
                "result_pill": "疗毒丹",
                "result_quantity_min": 1,
                "result_quantity_max": 2,
                "required_alchemy_level": 6,
                "base_success_rate": 0.55,
                "ingredients": [
                    {"item": "九幽草", "quantity": 4},
                    {"item": "寒冰莲", "quantity": 2},
                    {"item": "碧心花", "quantity": 3},
                ],
                "spiritual_power_cost": 100,
                "duration_hours": 3,
            },
            {
                "name": "灵智丹丹方",
                "description": "提升悟性的珍稀丹方",
                "result_pill": "灵智丹",
                "result_quantity_min": 1,
                "result_quantity_max": 1,
                "required_alchemy_level": 7,
                "base_success_rate": 0.45,
                "ingredients": [
                    {"item": "紫云芝", "quantity": 5},
                    {"item": "玉随芝", "quantity": 1},
                    {"item": "星月露", "quantity": 1},
                ],
                "spiritual_power_cost": 150,
                "duration_hours": 4,
            },

            # 宝品丹药（8种）
            {
                "name": "凝金丹丹方",
                "description": "辅助结丹的稀有丹方",
                "result_pill": "凝金丹",
                "result_quantity_min": 1,
                "result_quantity_max": 1,
                "required_alchemy_level": 10,
                "base_success_rate": 0.4,
                "ingredients": [
                    {"item": "天灵果", "quantity": 1},
                    {"item": "玉随芝", "quantity": 3},
                    {"item": "紫髓晶", "quantity": 1},
                ],
                "spiritual_power_cost": 200,
                "duration_hours": 8,
            },
            {
                "name": "返魂丹丹方",
                "description": "起死回生的灵丹配方",
                "result_pill": "返魂丹",
                "result_quantity_min": 1,
                "result_quantity_max": 1,
                "required_alchemy_level": 9,
                "base_success_rate": 0.35,
                "ingredients": [
                    {"item": "玉随芝", "quantity": 5},
                    {"item": "龙血草", "quantity": 1},
                    {"item": "寒冰莲", "quantity": 5},
                ],
                "spiritual_power_cost": 180,
                "duration_hours": 6,
            },
            {
                "name": "金丹培元丹丹方",
                "description": "金丹期修为丹药配方",
                "result_pill": "金丹培元丹",
                "result_quantity_min": 1,
                "result_quantity_max": 1,
                "required_alchemy_level": 11,
                "base_success_rate": 0.35,
                "ingredients": [
                    {"item": "天灵果", "quantity": 1},
                    {"item": "紫云芝", "quantity": 10},
                    {"item": "赤火果", "quantity": 3},
                ],
                "spiritual_power_cost": 250,
                "duration_hours": 8,
            },
            {
                "name": "龙虎丹丹方",
                "description": "大幅提升战力的猛药配方",
                "result_pill": "龙虎丹",
                "result_quantity_min": 1,
                "result_quantity_max": 1,
                "required_alchemy_level": 10,
                "base_success_rate": 0.4,
                "ingredients": [
                    {"item": "龙血草", "quantity": 2},
                    {"item": "金刚果", "quantity": 5},
                    {"item": "赤火果", "quantity": 3},
                ],
                "spiritual_power_cost": 200,
                "duration_hours": 6,
            },
            {
                "name": "破瓶丹丹方",
                "description": "辅助金丹期小境界突破配方",
                "result_pill": "破瓶丹",
                "result_quantity_min": 1,
                "result_quantity_max": 1,
                "required_alchemy_level": 11,
                "base_success_rate": 0.3,
                "ingredients": [
                    {"item": "天灵果", "quantity": 1},
                    {"item": "九幽草", "quantity": 5},
                    {"item": "紫髓晶", "quantity": 1},
                ],
                "spiritual_power_cost": 250,
                "duration_hours": 10,
            },
            {
                "name": "五行丹丹方",
                "description": "五行法术增强配方",
                "result_pill": "五行丹",
                "result_quantity_min": 1,
                "result_quantity_max": 1,
                "required_alchemy_level": 12,
                "base_success_rate": 0.3,
                "ingredients": [
                    {"item": "赤火果", "quantity": 2},
                    {"item": "寒冰莲", "quantity": 2},
                    {"item": "金刚果", "quantity": 2},
                    {"item": "紫云芝", "quantity": 5},
                ],
                "spiritual_power_cost": 300,
                "duration_hours": 10,
            },
            {
                "name": "紫髓丹丹方",
                "description": "疗伤圣药配方",
                "result_pill": "紫髓丹",
                "result_quantity_min": 1,
                "result_quantity_max": 1,
                "required_alchemy_level": 11,
                "base_success_rate": 0.35,
                "ingredients": [
                    {"item": "紫髓晶", "quantity": 2},
                    {"item": "龙血草", "quantity": 1},
                    {"item": "玉随芝", "quantity": 5},
                ],
                "spiritual_power_cost": 250,
                "duration_hours": 8,
            },
            {
                "name": "固元丹丹方",
                "description": "永久增加灵力上限的高级配方",
                "result_pill": "固元丹",
                "result_quantity_min": 1,
                "result_quantity_max": 1,
                "required_alchemy_level": 12,
                "base_success_rate": 0.3,
                "ingredients": [
                    {"item": "天灵果", "quantity": 1},
                    {"item": "碧心花", "quantity": 10},
                    {"item": "星月露", "quantity": 2},
                ],
                "spiritual_power_cost": 300,
                "duration_hours": 10,
            },

            # 仙品丹药（6种）
            {
                "name": "破婴丹丹方",
                "description": "辅助凝婴的传说丹方",
                "result_pill": "破婴丹",
                "result_quantity_min": 1,
                "result_quantity_max": 1,
                "required_alchemy_level": 15,
                "base_success_rate": 0.2,
                "ingredients": [
                    {"item": "血参精", "quantity": 1},
                    {"item": "凤羽花", "quantity": 2},
                    {"item": "紫髓晶", "quantity": 3},
                ],
                "spiritual_power_cost": 500,
                "duration_hours": 24,
            },
            {
                "name": "元婴培元丹丹方",
                "description": "元婴期修为丹药配方",
                "result_pill": "元婴培元丹",
                "result_quantity_min": 1,
                "result_quantity_max": 1,
                "required_alchemy_level": 14,
                "base_success_rate": 0.25,
                "ingredients": [
                    {"item": "血参精", "quantity": 1},
                    {"item": "天灵果", "quantity": 3},
                    {"item": "龙血草", "quantity": 2},
                ],
                "spiritual_power_cost": 400,
                "duration_hours": 16,
            },
            {
                "name": "涅槃丹丹方",
                "description": "复活丹药配方",
                "result_pill": "涅槃丹",
                "result_quantity_min": 1,
                "result_quantity_max": 1,
                "required_alchemy_level": 16,
                "base_success_rate": 0.15,
                "ingredients": [
                    {"item": "血参精", "quantity": 1},
                    {"item": "凤羽花", "quantity": 1},
                    {"item": "龙血草", "quantity": 2},
                    {"item": "紫髓晶", "quantity": 2},
                ],
                "spiritual_power_cost": 600,
                "duration_hours": 24,
            },
            {
                "name": "化婴丹丹方",
                "description": "强化元婴的仙丹配方",
                "result_pill": "化婴丹",
                "result_quantity_min": 1,
                "result_quantity_max": 1,
                "required_alchemy_level": 17,
                "base_success_rate": 0.15,
                "ingredients": [
                    {"item": "血参精", "quantity": 2},
                    {"item": "天灵果", "quantity": 3},
                    {"item": "星月露", "quantity": 5},
                ],
                "spiritual_power_cost": 600,
                "duration_hours": 30,
            },
            {
                "name": "续命丹丹方",
                "description": "延寿丹药配方",
                "result_pill": "续命丹",
                "result_quantity_min": 1,
                "result_quantity_max": 1,
                "required_alchemy_level": 15,
                "base_success_rate": 0.2,
                "ingredients": [
                    {"item": "血参精", "quantity": 1},
                    {"item": "玉随芝", "quantity": 10},
                    {"item": "寒冰莲", "quantity": 10},
                ],
                "spiritual_power_cost": 500,
                "duration_hours": 20,
            },
            {
                "name": "神通丹丹方",
                "description": "领悟神通的逆天丹方",
                "result_pill": "神通丹",
                "result_quantity_min": 1,
                "result_quantity_max": 1,
                "required_alchemy_level": 18,
                "base_success_rate": 0.1,
                "ingredients": [
                    {"item": "凤羽花", "quantity": 1},
                    {"item": "龙血草", "quantity": 2},
                    {"item": "天灵果", "quantity": 2},
                    {"item": "星月露", "quantity": 3},
                ],
                "spiritual_power_cost": 800,
                "duration_hours": 36,
            },

            # 神品丹药（4种）
            {
                "name": "化神丹丹方",
                "description": "辅助化神突破的仙丹配方",
                "result_pill": "化神丹",
                "result_quantity_min": 1,
                "result_quantity_max": 1,
                "required_alchemy_level": 20,
                "base_success_rate": 0.08,
                "ingredients": [
                    {"item": "化神花", "quantity": 1},
                    {"item": "血参精", "quantity": 3},
                    {"item": "凤羽花", "quantity": 3},
                    {"item": "紫髓晶", "quantity": 5},
                ],
                "spiritual_power_cost": 1000,
                "duration_hours": 48,
            },
            {
                "name": "化神培元丹丹方",
                "description": "化神期修为丹药配方",
                "result_pill": "化神培元丹",
                "result_quantity_min": 1,
                "result_quantity_max": 1,
                "required_alchemy_level": 19,
                "base_success_rate": 0.1,
                "ingredients": [
                    {"item": "化神花", "quantity": 1},
                    {"item": "血参精", "quantity": 2},
                    {"item": "天灵果", "quantity": 5},
                ],
                "spiritual_power_cost": 800,
                "duration_hours": 40,
            },
            {
                "name": "天劫丹丹方",
                "description": "抵抗天劫的神丹配方",
                "result_pill": "天劫丹",
                "result_quantity_min": 1,
                "result_quantity_max": 1,
                "required_alchemy_level": 21,
                "base_success_rate": 0.05,
                "ingredients": [
                    {"item": "化神花", "quantity": 1},
                    {"item": "凤羽花", "quantity": 3},
                    {"item": "龙血草", "quantity": 3},
                    {"item": "星月露", "quantity": 10},
                ],
                "spiritual_power_cost": 1200,
                "duration_hours": 72,
            },
            {
                "name": "大还丹丹方",
                "description": "起死回生圣药配方",
                "result_pill": "大还丹",
                "result_quantity_min": 1,
                "result_quantity_max": 1,
                "required_alchemy_level": 20,
                "base_success_rate": 0.08,
                "ingredients": [
                    {"item": "血参精", "quantity": 5},
                    {"item": "紫髓晶", "quantity": 10},
                    {"item": "龙血草", "quantity": 5},
                    {"item": "玉随芝", "quantity": 20},
                ],
                "spiritual_power_cost": 1000,
                "duration_hours": 48,
            },
        ]

        added_count = 0
        skipped_count = 0
        missing_items = []

        for recipe_data in recipes:
            # 检查是否已存在
            result = await session.execute(
                select(PillRecipe).where(PillRecipe.name == recipe_data["name"])
            )
            if result.scalar_one_or_none():
                print(f"⏭️  跳过：{recipe_data['name']}（已存在）")
                skipped_count += 1
                continue

            # 获取产出丹药ID
            result_pill_name = recipe_data["result_pill"]
            if result_pill_name not in item_map:
                print(f"❌ 错误：找不到丹药 {result_pill_name}")
                missing_items.append(result_pill_name)
                continue

            result_pill_id = item_map[result_pill_name]

            # 构建材料JSON
            ingredients_json = []
            all_ingredients_found = True

            for ing in recipe_data["ingredients"]:
                item_name = ing["item"]
                if item_name not in item_map:
                    print(f"❌ 错误：找不到材料 {item_name}")
                    missing_items.append(item_name)
                    all_ingredients_found = False
                    break

                ingredients_json.append({
                    "item_id": item_map[item_name],
                    "quantity": ing["quantity"]
                })

            if not all_ingredients_found:
                continue

            # 创建丹方
            recipe = PillRecipe(
                name=recipe_data["name"],
                description=recipe_data["description"],
                result_pill_id=result_pill_id,
                result_quantity_min=recipe_data["result_quantity_min"],
                result_quantity_max=recipe_data["result_quantity_max"],
                required_alchemy_level=recipe_data["required_alchemy_level"],
                base_success_rate=recipe_data["base_success_rate"],
                ingredients=json.dumps(ingredients_json),
                spiritual_power_cost=recipe_data["spiritual_power_cost"],
                duration_hours=recipe_data["duration_hours"],
            )

            session.add(recipe)
            added_count += 1

            # 格式化材料列表
            ing_str = ", ".join([f"{ing['item']}×{ing['quantity']}" for ing in recipe_data["ingredients"]])
            print(f"✅ 创建丹方：{recipe_data['name']}")
            print(f"   产出：{result_pill_name} ({recipe_data['result_quantity_min']}-{recipe_data['result_quantity_max']}颗)")
            print(f"   材料：{ing_str}")
            print(f"   成功率：{recipe_data['base_success_rate']*100:.0f}% | 炼丹等级：{recipe_data['required_alchemy_level']} | 时长：{recipe_data['duration_hours']}小时")

        await session.commit()
        print(f"\n🎉 丹方创建完成！新增 {added_count} 种，跳过 {skipped_count} 种")

        if missing_items:
            print(f"\n⚠️  警告：以下物品未找到：")
            for item in set(missing_items):
                print(f"   - {item}")

        return added_count


async def main():
    """主函数"""
    print("=" * 60)
    print("🧪 凡人修仙传 - 炼丹系统初始化")
    print("=" * 60)

    print("\n📝 开始创建炼丹系统数据...\\n")

    # 创建材料
    print("━" * 60)
    print("第一步：创建炼丹材料（16种灵药）")
    print("━" * 60)
    materials_added = await create_alchemy_materials()

    # 创建丹药
    print("\n" + "━" * 60)
    print("第二步：创建丹药物品（36种丹药）")
    print("━" * 60)
    pills_added = await create_alchemy_pills()

    # 创建丹方
    print("\n" + "━" * 60)
    print("第三步：创建丹方配方（36种丹方）")
    print("━" * 60)
    recipes_added = await create_pill_recipes()

    # 总结
    print("\n" + "=" * 60)
    print("🎉 炼丹系统初始化完成！")
    print("=" * 60)
    print(f"\n📊 数据统计：")
    print(f"   • 炼丹材料：新增 {materials_added} 种")
    print(f"   • 丹药物品：新增 {pills_added} 种")
    print(f"   • 丹方配方：新增 {recipes_added} 种")

    print("\n💡 下一步：")
    print("1. 测试炼丹命令: /炼丹 [丹方名称]")
    print("2. 查看丹方: /丹方列表")
    print("3. 查看炼丹等级: /炼丹等级")
    print("4. 收集材料开始炼丹吧！\n")


if __name__ == "__main__":
    asyncio.run(main())
