"""符箓系统初始化脚本 - 凡人修仙传版本"""
import asyncio
import json
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from bot.models.database import init_db, AsyncSessionLocal
from bot.models.item import Item, ItemType
from bot.models.talisman import TalismanRecipe, TalismanType, TalismanGrade
from sqlalchemy import select


async def create_talisman_materials():
    """创建符箓制作材料（10种基础材料）"""
    async with AsyncSessionLocal() as session:
        materials = [
            # 符纸类（4种）
            {
                "name": "白符纸",
                "description": "基础符纸，用于制作下品符箓",
                "item_type": ItemType.MATERIAL,
                "buy_price": 10,
                "sell_price": 5,
                "is_stackable": True,
                "max_stack": 999,
            },
            {
                "name": "黄符纸",
                "description": "中级符纸，用于制作中品符箓，以百年黄纸制成",
                "item_type": ItemType.MATERIAL,
                "buy_price": 100,
                "sell_price": 50,
                "is_stackable": True,
                "max_stack": 999,
            },
            {
                "name": "玉符纸",
                "description": "高级符纸，用于制作上品符箓，以玉石纤维制成",
                "item_type": ItemType.MATERIAL,
                "buy_price": 1000,
                "sell_price": 500,
                "is_stackable": True,
                "max_stack": 999,
            },
            {
                "name": "仙符纸",
                "description": "顶级符纸，用于制作极品符箓，以仙界灵材制成",
                "item_type": ItemType.MATERIAL,
                "buy_price": 10000,
                "sell_price": 5000,
                "is_stackable": True,
                "max_stack": 99,
            },

            # 墨料类（3种）
            {
                "name": "朱砂",
                "description": "基础符墨，用于绘制符箓",
                "item_type": ItemType.MATERIAL,
                "buy_price": 5,
                "sell_price": 2,
                "is_stackable": True,
                "max_stack": 999,
            },
            {
                "name": "精制朱砂",
                "description": "精制符墨，纯度更高，用于中品符箓",
                "item_type": ItemType.MATERIAL,
                "buy_price": 50,
                "sell_price": 25,
                "is_stackable": True,
                "max_stack": 999,
            },
            {
                "name": "天雷沙",
                "description": "天雷淬炼的灵沙，用于高品符箓，蕴含雷电之力",
                "item_type": ItemType.MATERIAL,
                "buy_price": 500,
                "sell_price": 250,
                "is_stackable": True,
                "max_stack": 999,
            },

            # 特殊材料（3种）
            {
                "name": "金雷竹粉末",
                "description": "金雷竹磨成的粉末，制作金雷竹符的必需材料，韩立成名之宝",
                "item_type": ItemType.MATERIAL,
                "buy_price": 5000,
                "sell_price": 2500,
                "is_stackable": True,
                "max_stack": 99,
            },
            {
                "name": "五行灵粉",
                "description": "五行精华混合而成的灵粉，制作五行遁符的关键材料",
                "item_type": ItemType.MATERIAL,
                "buy_price": 2000,
                "sell_price": 1000,
                "is_stackable": True,
                "max_stack": 99,
            },
            {
                "name": "研磨工具",
                "description": "用于将灵药研磨成粉末的工具，不会消耗",
                "item_type": ItemType.MISC,
                "buy_price": 1000,
                "sell_price": 500,
                "is_stackable": False,
                "max_stack": 1,
                "special_ability": "可将灵药研磨成粉末用于制符",
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
            print(f"✅ 创建材料：{material_data['name']} - {material_data['buy_price']:,}灵石")

        await session.commit()
        print(f"\n🎉 符箓材料创建完成！新增 {added_count} 种，跳过 {skipped_count} 种")
        return added_count


async def create_talisman_recipes():
    """创建符箓配方（30种）"""
    async with AsyncSessionLocal() as session:
        # 获取所有物品，建立名称到ID的映射
        result = await session.execute(select(Item))
        items = result.scalars().all()
        item_map = {item.name: item.id for item in items}

        # 定义所有符箓配方
        recipes = [
            # ========== 攻击符（10种）==========

            # 下品攻击符（5种）
            {
                "name": "火球符",
                "description": "发射一个火球攻击敌人的基础攻击符箓",
                "talisman_type": TalismanType.ATTACK.value,
                "grade": TalismanGrade.LOW.value,
                "required_realm": "炼气期",
                "required_level": 1,
                "required_talisman_skill": 1,
                "materials": [
                    {"item": "白符纸", "quantity": 1},
                    {"item": "朱砂", "quantity": 2},
                ],
                "base_success_rate": 0.85,
                "spiritual_power_cost": 20,
                "duration_hours": 1,  # 0.5小时用1表示
                "effect_power": 120,  # 基础攻击×1.2
                "effect_duration": 0,
                "cooldown": 0,
            },
            {
                "name": "冰锥符",
                "description": "发射冰锥攻击敌人，有几率减速",
                "talisman_type": TalismanType.ATTACK.value,
                "grade": TalismanGrade.LOW.value,
                "required_realm": "炼气期",
                "required_level": 1,
                "required_talisman_skill": 1,
                "materials": [
                    {"item": "白符纸", "quantity": 1},
                    {"item": "朱砂", "quantity": 2},
                ],
                "base_success_rate": 0.85,
                "spiritual_power_cost": 20,
                "duration_hours": 1,
                "effect_power": 120,
                "effect_duration": 0,
                "cooldown": 0,
            },
            {
                "name": "金刃符",
                "description": "召唤金属刃片进行攻击",
                "talisman_type": TalismanType.ATTACK.value,
                "grade": TalismanGrade.LOW.value,
                "required_realm": "炼气期",
                "required_level": 2,
                "required_talisman_skill": 2,
                "materials": [
                    {"item": "白符纸", "quantity": 1},
                    {"item": "朱砂", "quantity": 3},
                ],
                "base_success_rate": 0.8,
                "spiritual_power_cost": 25,
                "duration_hours": 1,
                "effect_power": 130,
                "effect_duration": 0,
                "cooldown": 0,
            },
            {
                "name": "藤蔓缠绕符",
                "description": "召唤藤蔓缠绕敌人，造成伤害并束缚1回合",
                "talisman_type": TalismanType.ATTACK.value,
                "grade": TalismanGrade.LOW.value,
                "required_realm": "炼气期",
                "required_level": 2,
                "required_talisman_skill": 2,
                "materials": [
                    {"item": "白符纸", "quantity": 1},
                    {"item": "朱砂", "quantity": 2},
                ],
                "base_success_rate": 0.8,
                "spiritual_power_cost": 25,
                "duration_hours": 1,
                "effect_power": 80,
                "effect_duration": 3,  # 束缚3秒
                "cooldown": 0,
            },
            {
                "name": "雷击符",
                "description": "召唤雷电攻击敌人",
                "talisman_type": TalismanType.ATTACK.value,
                "grade": TalismanGrade.LOW.value,
                "required_realm": "炼气期",
                "required_level": 3,
                "required_talisman_skill": 3,
                "materials": [
                    {"item": "白符纸", "quantity": 1},
                    {"item": "朱砂", "quantity": 3},
                ],
                "base_success_rate": 0.75,
                "spiritual_power_cost": 30,
                "duration_hours": 1,
                "effect_power": 150,
                "effect_duration": 0,
                "cooldown": 0,
            },

            # 中品攻击符（3种）
            {
                "name": "金雷竹符",
                "description": "金雷交织，强大的雷电攻击，韩立在血色禁地的保命之宝",
                "talisman_type": TalismanType.ATTACK.value,
                "grade": TalismanGrade.MEDIUM.value,
                "required_realm": "筑基期",
                "required_level": 8,
                "required_talisman_skill": 8,
                "materials": [
                    {"item": "黄符纸", "quantity": 1},
                    {"item": "精制朱砂", "quantity": 3},
                    {"item": "金雷竹粉末", "quantity": 1},
                ],
                "base_success_rate": 0.6,
                "spiritual_power_cost": 80,
                "duration_hours": 3,
                "effect_power": 200,
                "effect_duration": 0,
                "cooldown": 0,
            },
            {
                "name": "烈焰符",
                "description": "释放大面积火焰，范围攻击",
                "talisman_type": TalismanType.ATTACK.value,
                "grade": TalismanGrade.MEDIUM.value,
                "required_realm": "筑基期",
                "required_level": 7,
                "required_talisman_skill": 7,
                "materials": [
                    {"item": "黄符纸", "quantity": 1},
                    {"item": "精制朱砂", "quantity": 3},
                    {"item": "赤火果", "quantity": 1},
                ],
                "base_success_rate": 0.65,
                "spiritual_power_cost": 70,
                "duration_hours": 3,
                "effect_power": 180,
                "effect_duration": 0,
                "cooldown": 0,
            },
            {
                "name": "寒冰爆符",
                "description": "冰霜爆炸，冻结敌人2回合",
                "talisman_type": TalismanType.ATTACK.value,
                "grade": TalismanGrade.MEDIUM.value,
                "required_realm": "筑基期",
                "required_level": 8,
                "required_talisman_skill": 8,
                "materials": [
                    {"item": "黄符纸", "quantity": 1},
                    {"item": "精制朱砂", "quantity": 3},
                    {"item": "寒冰莲", "quantity": 2},
                ],
                "base_success_rate": 0.6,
                "spiritual_power_cost": 80,
                "duration_hours": 3,
                "effect_power": 190,
                "effect_duration": 6,  # 冻结6秒
                "cooldown": 0,
            },

            # 上品攻击符（2种）
            {
                "name": "五雷符",
                "description": "召唤五道雷电连续攻击",
                "talisman_type": TalismanType.ATTACK.value,
                "grade": TalismanGrade.HIGH.value,
                "required_realm": "金丹期",
                "required_level": 15,
                "required_talisman_skill": 15,
                "materials": [
                    {"item": "玉符纸", "quantity": 1},
                    {"item": "天雷沙", "quantity": 2},
                    {"item": "龙血草", "quantity": 1},
                ],
                "base_success_rate": 0.4,
                "spiritual_power_cost": 150,
                "duration_hours": 8,
                "effect_power": 280,
                "effect_duration": 0,
                "cooldown": 0,
            },
            {
                "name": "剑气符",
                "description": "凝聚剑气斩击，无视30%防御",
                "talisman_type": TalismanType.ATTACK.value,
                "grade": TalismanGrade.HIGH.value,
                "required_realm": "金丹期",
                "required_level": 16,
                "required_talisman_skill": 16,
                "materials": [
                    {"item": "玉符纸", "quantity": 1},
                    {"item": "天雷沙", "quantity": 2},
                    {"item": "金刚果", "quantity": 2},
                ],
                "base_success_rate": 0.35,
                "spiritual_power_cost": 160,
                "duration_hours": 10,
                "effect_power": 300,
                "effect_duration": 0,
                "cooldown": 0,
            },

            # ========== 防御符（6种）==========

            # 下品防御符（3种）
            {
                "name": "金光符",
                "description": "形成金色护盾，持续3回合",
                "talisman_type": TalismanType.DEFENSE.value,
                "grade": TalismanGrade.LOW.value,
                "required_realm": "炼气期",
                "required_level": 2,
                "required_talisman_skill": 2,
                "materials": [
                    {"item": "白符纸", "quantity": 1},
                    {"item": "朱砂", "quantity": 2},
                ],
                "base_success_rate": 0.8,
                "spiritual_power_cost": 25,
                "duration_hours": 1,
                "effect_power": 50,  # 防御+50
                "effect_duration": 9,  # 持续9秒（3回合）
                "cooldown": 0,
            },
            {
                "name": "土墙符",
                "description": "召唤土墙阻挡攻击，持续2回合",
                "talisman_type": TalismanType.DEFENSE.value,
                "grade": TalismanGrade.LOW.value,
                "required_realm": "炼气期",
                "required_level": 2,
                "required_talisman_skill": 2,
                "materials": [
                    {"item": "白符纸", "quantity": 1},
                    {"item": "朱砂", "quantity": 2},
                ],
                "base_success_rate": 0.8,
                "spiritual_power_cost": 25,
                "duration_hours": 1,
                "effect_power": 60,
                "effect_duration": 6,
                "cooldown": 0,
            },
            {
                "name": "护体符",
                "description": "全身护罩，持续5回合，减免20%伤害",
                "talisman_type": TalismanType.DEFENSE.value,
                "grade": TalismanGrade.LOW.value,
                "required_realm": "炼气期",
                "required_level": 3,
                "required_talisman_skill": 3,
                "materials": [
                    {"item": "白符纸", "quantity": 1},
                    {"item": "朱砂", "quantity": 3},
                ],
                "base_success_rate": 0.75,
                "spiritual_power_cost": 30,
                "duration_hours": 1,
                "effect_power": 20,  # 减伤20%
                "effect_duration": 15,
                "cooldown": 0,
            },

            # 中品防御符（2种）
            {
                "name": "金刚符",
                "description": "金刚护体，持续10回合",
                "talisman_type": TalismanType.DEFENSE.value,
                "grade": TalismanGrade.MEDIUM.value,
                "required_realm": "筑基期",
                "required_level": 9,
                "required_talisman_skill": 9,
                "materials": [
                    {"item": "黄符纸", "quantity": 1},
                    {"item": "精制朱砂", "quantity": 3},
                    {"item": "金刚果", "quantity": 2},
                ],
                "base_success_rate": 0.55,
                "spiritual_power_cost": 90,
                "duration_hours": 3,
                "effect_power": 150,
                "effect_duration": 30,
                "cooldown": 0,
            },
            {
                "name": "玄冰盾符",
                "description": "冰盾护体，吸收3000点伤害直到破碎",
                "talisman_type": TalismanType.DEFENSE.value,
                "grade": TalismanGrade.MEDIUM.value,
                "required_realm": "筑基期",
                "required_level": 10,
                "required_talisman_skill": 10,
                "materials": [
                    {"item": "黄符纸", "quantity": 1},
                    {"item": "精制朱砂", "quantity": 3},
                    {"item": "寒冰莲", "quantity": 2},
                    {"item": "玉随芝", "quantity": 1},
                ],
                "base_success_rate": 0.5,
                "spiritual_power_cost": 100,
                "duration_hours": 4,
                "effect_power": 3000,  # 吸收伤害值
                "effect_duration": 60,
                "cooldown": 0,
            },

            # 上品防御符（1种）
            {
                "name": "金刚不坏符",
                "description": "金刚不坏，减伤50%，持续1分钟，免疫控制",
                "talisman_type": TalismanType.DEFENSE.value,
                "grade": TalismanGrade.HIGH.value,
                "required_realm": "金丹期",
                "required_level": 17,
                "required_talisman_skill": 17,
                "materials": [
                    {"item": "玉符纸", "quantity": 1},
                    {"item": "天雷沙", "quantity": 2},
                    {"item": "紫髓晶", "quantity": 1},
                ],
                "base_success_rate": 0.3,
                "spiritual_power_cost": 180,
                "duration_hours": 12,
                "effect_power": 50,  # 减伤50%
                "effect_duration": 60,
                "cooldown": 0,
            },

            # ========== 治疗符（4种）==========

            # 下品治疗符（2种）
            {
                "name": "回春符",
                "description": "瞬间恢复500点生命值",
                "talisman_type": TalismanType.HEALING.value,
                "grade": TalismanGrade.LOW.value,
                "required_realm": "炼气期",
                "required_level": 1,
                "required_talisman_skill": 1,
                "materials": [
                    {"item": "白符纸", "quantity": 1},
                    {"item": "朱砂", "quantity": 2},
                ],
                "base_success_rate": 0.85,
                "spiritual_power_cost": 20,
                "duration_hours": 1,
                "effect_power": 500,
                "effect_duration": 0,
                "cooldown": 0,
            },
            {
                "name": "聚灵符",
                "description": "瞬间恢复300点灵力值",
                "talisman_type": TalismanType.HEALING.value,
                "grade": TalismanGrade.LOW.value,
                "required_realm": "炼气期",
                "required_level": 1,
                "required_talisman_skill": 1,
                "materials": [
                    {"item": "白符纸", "quantity": 1},
                    {"item": "朱砂", "quantity": 2},
                ],
                "base_success_rate": 0.85,
                "spiritual_power_cost": 20,
                "duration_hours": 1,
                "effect_power": 300,
                "effect_duration": 0,
                "cooldown": 0,
            },

            # 中品治疗符（1种）
            {
                "name": "大回春符",
                "description": "大幅恢复2000点生命值",
                "talisman_type": TalismanType.HEALING.value,
                "grade": TalismanGrade.MEDIUM.value,
                "required_realm": "筑基期",
                "required_level": 8,
                "required_talisman_skill": 8,
                "materials": [
                    {"item": "黄符纸", "quantity": 1},
                    {"item": "精制朱砂", "quantity": 3},
                    {"item": "玉随芝", "quantity": 1},
                ],
                "base_success_rate": 0.6,
                "spiritual_power_cost": 80,
                "duration_hours": 3,
                "effect_power": 2000,
                "effect_duration": 0,
                "cooldown": 0,
            },

            # 上品治疗符（1种）
            {
                "name": "续命符",
                "description": "濒死时自动触发，恢复50%生命和灵力，救命符箓",
                "talisman_type": TalismanType.HEALING.value,
                "grade": TalismanGrade.HIGH.value,
                "required_realm": "金丹期",
                "required_level": 18,
                "required_talisman_skill": 18,
                "materials": [
                    {"item": "玉符纸", "quantity": 1},
                    {"item": "天雷沙", "quantity": 2},
                    {"item": "龙血草", "quantity": 1},
                    {"item": "紫髓晶", "quantity": 1},
                ],
                "base_success_rate": 0.25,
                "spiritual_power_cost": 200,
                "duration_hours": 15,
                "effect_power": 50,  # 恢复50%
                "effect_duration": 0,
                "cooldown": 0,
            },

            # ========== 遁符（4种）==========

            # 下品遁符（2种）
            {
                "name": "轻身符",
                "description": "短时间加快移动速度50%，持续10分钟",
                "talisman_type": TalismanType.ESCAPE.value,
                "grade": TalismanGrade.LOW.value,
                "required_realm": "炼气期",
                "required_level": 2,
                "required_talisman_skill": 2,
                "materials": [
                    {"item": "白符纸", "quantity": 1},
                    {"item": "朱砂", "quantity": 2},
                ],
                "base_success_rate": 0.8,
                "spiritual_power_cost": 25,
                "duration_hours": 1,
                "effect_power": 50,  # 速度+50%
                "effect_duration": 600,  # 10分钟
                "cooldown": 0,
            },
            {
                "name": "遁地符",
                "description": "遁入地下短距离移动，逃跑成功率+30%",
                "talisman_type": TalismanType.ESCAPE.value,
                "grade": TalismanGrade.LOW.value,
                "required_realm": "炼气期",
                "required_level": 3,
                "required_talisman_skill": 3,
                "materials": [
                    {"item": "白符纸", "quantity": 1},
                    {"item": "朱砂", "quantity": 3},
                ],
                "base_success_rate": 0.75,
                "spiritual_power_cost": 30,
                "duration_hours": 1,
                "effect_power": 30,  # 逃跑成功率+30%
                "effect_duration": 5,
                "cooldown": 0,
            },

            # 中品遁符（1种）
            {
                "name": "五行遁符",
                "description": "选择金木水火土一种进行短距离瞬移100米",
                "talisman_type": TalismanType.ESCAPE.value,
                "grade": TalismanGrade.MEDIUM.value,
                "required_realm": "筑基期",
                "required_level": 12,
                "required_talisman_skill": 12,
                "materials": [
                    {"item": "黄符纸", "quantity": 1},
                    {"item": "精制朱砂", "quantity": 5},
                    {"item": "五行灵粉", "quantity": 1},
                ],
                "base_success_rate": 0.45,
                "spiritual_power_cost": 120,
                "duration_hours": 6,
                "effect_power": 100,  # 瞬移100米
                "effect_duration": 0,
                "cooldown": 0,
            },

            # 极品遁符（1种）
            {
                "name": "血影遁符",
                "description": "韩立绝技，消耗气血强行瞬移1000米",
                "talisman_type": TalismanType.ESCAPE.value,
                "grade": TalismanGrade.SUPREME.value,
                "required_realm": "元婴期",
                "required_level": 20,
                "required_talisman_skill": 20,
                "materials": [
                    {"item": "仙符纸", "quantity": 1},
                    {"item": "天雷沙", "quantity": 5},
                    {"item": "血参精", "quantity": 1},
                ],
                "base_success_rate": 0.15,
                "spiritual_power_cost": 300,
                "duration_hours": 24,
                "effect_power": 1000,  # 瞬移1000米
                "effect_duration": 0,
                "cooldown": 0,
            },

            # ========== 辅助符（6种）==========

            # 下品辅助符（3种）
            {
                "name": "探灵符",
                "description": "探测周围100米范围的灵气和妖兽",
                "talisman_type": TalismanType.AUXILIARY.value,
                "grade": TalismanGrade.LOW.value,
                "required_realm": "炼气期",
                "required_level": 1,
                "required_talisman_skill": 1,
                "materials": [
                    {"item": "白符纸", "quantity": 1},
                    {"item": "朱砂", "quantity": 2},
                ],
                "base_success_rate": 0.85,
                "spiritual_power_cost": 20,
                "duration_hours": 1,
                "effect_power": 100,  # 探测范围100米
                "effect_duration": 60,
                "cooldown": 0,
            },
            {
                "name": "隐身符",
                "description": "隐匿身形10分钟，避开低级妖兽",
                "talisman_type": TalismanType.AUXILIARY.value,
                "grade": TalismanGrade.LOW.value,
                "required_realm": "炼气期",
                "required_level": 3,
                "required_talisman_skill": 3,
                "materials": [
                    {"item": "白符纸", "quantity": 1},
                    {"item": "朱砂", "quantity": 3},
                    {"item": "九幽草", "quantity": 1},
                ],
                "base_success_rate": 0.75,
                "spiritual_power_cost": 30,
                "duration_hours": 1,
                "effect_power": 1,  # 隐身标记
                "effect_duration": 600,
                "cooldown": 0,
            },
            {
                "name": "破禁符",
                "description": "破解炼气期禁制阵法",
                "talisman_type": TalismanType.AUXILIARY.value,
                "grade": TalismanGrade.LOW.value,
                "required_realm": "炼气期",
                "required_level": 4,
                "required_talisman_skill": 4,
                "materials": [
                    {"item": "白符纸", "quantity": 1},
                    {"item": "朱砂", "quantity": 3},
                ],
                "base_success_rate": 0.7,
                "spiritual_power_cost": 35,
                "duration_hours": 2,
                "effect_power": 1,  # 破禁等级
                "effect_duration": 0,
                "cooldown": 0,
            },

            # 中品辅助符（2种）
            {
                "name": "神识增幅符",
                "description": "短时间大幅增强神识100%，持续1小时",
                "talisman_type": TalismanType.AUXILIARY.value,
                "grade": TalismanGrade.MEDIUM.value,
                "required_realm": "筑基期",
                "required_level": 10,
                "required_talisman_skill": 10,
                "materials": [
                    {"item": "黄符纸", "quantity": 1},
                    {"item": "精制朱砂", "quantity": 4},
                    {"item": "星月露", "quantity": 1},
                ],
                "base_success_rate": 0.5,
                "spiritual_power_cost": 100,
                "duration_hours": 4,
                "effect_power": 100,  # 神识+100%
                "effect_duration": 3600,
                "cooldown": 0,
            },
            {
                "name": "破阵符",
                "description": "强行破解筑基期阵法",
                "talisman_type": TalismanType.AUXILIARY.value,
                "grade": TalismanGrade.MEDIUM.value,
                "required_realm": "筑基期",
                "required_level": 11,
                "required_talisman_skill": 11,
                "materials": [
                    {"item": "黄符纸", "quantity": 1},
                    {"item": "精制朱砂", "quantity": 4},
                    {"item": "天灵果", "quantity": 1},
                ],
                "base_success_rate": 0.45,
                "spiritual_power_cost": 110,
                "duration_hours": 5,
                "effect_power": 2,  # 破禁等级
                "effect_duration": 0,
                "cooldown": 0,
            },

            # 极品辅助符（1种）
            {
                "name": "锁空符",
                "description": "短暂封锁周围空间，禁止瞬移和传送",
                "talisman_type": TalismanType.AUXILIARY.value,
                "grade": TalismanGrade.SUPREME.value,
                "required_realm": "化神期",
                "required_level": 22,
                "required_talisman_skill": 22,
                "materials": [
                    {"item": "仙符纸", "quantity": 1},
                    {"item": "天雷沙", "quantity": 5},
                    {"item": "化神花", "quantity": 1},
                ],
                "base_success_rate": 0.1,
                "spiritual_power_cost": 400,
                "duration_hours": 30,
                "effect_power": 1,  # 锁空标记
                "effect_duration": 30,
                "cooldown": 0,
            },
        ]

        added_count = 0
        skipped_count = 0
        missing_items = []

        for recipe_data in recipes:
            # 检查是否已存在
            result = await session.execute(
                select(TalismanRecipe).where(TalismanRecipe.name == recipe_data["name"])
            )
            if result.scalar_one_or_none():
                print(f"⏭️  跳过：{recipe_data['name']}（已存在）")
                skipped_count += 1
                continue

            # 构建材料JSON
            materials_json = []
            all_materials_found = True

            for mat in recipe_data["materials"]:
                item_name = mat["item"]
                if item_name not in item_map:
                    print(f"❌ 错误：找不到材料 {item_name}")
                    missing_items.append(item_name)
                    all_materials_found = False
                    break

                materials_json.append({
                    "item_id": item_map[item_name],
                    "quantity": mat["quantity"]
                })

            if not all_materials_found:
                continue

            # 创建符箓配方
            recipe = TalismanRecipe(
                name=recipe_data["name"],
                description=recipe_data["description"],
                talisman_type=recipe_data["talisman_type"],
                grade=recipe_data["grade"],
                required_realm=recipe_data["required_realm"],
                required_level=recipe_data["required_level"],
                required_talisman_skill=recipe_data["required_talisman_skill"],
                materials=json.dumps(materials_json),
                base_success_rate=recipe_data["base_success_rate"],
                spiritual_power_cost=recipe_data["spiritual_power_cost"],
                duration_hours=recipe_data["duration_hours"],
                effect_power=recipe_data["effect_power"],
                effect_duration=recipe_data["effect_duration"],
                cooldown=recipe_data["cooldown"],
            )

            session.add(recipe)
            added_count += 1

            # 格式化材料列表
            mat_str = ", ".join([f"{mat['item']}×{mat['quantity']}" for mat in recipe_data["materials"]])
            print(f"✅ 创建符箓：{recipe_data['name']}")
            print(f"   类型：{recipe_data['talisman_type']} | 品阶：{recipe_data['grade']}")
            print(f"   材料：{mat_str}")
            print(f"   成功率：{recipe_data['base_success_rate']*100:.0f}% | 制符等级：{recipe_data['required_talisman_skill']} | 时长：{recipe_data['duration_hours']}小时")

        await session.commit()
        print(f"\n🎉 符箓配方创建完成！新增 {added_count} 种，跳过 {skipped_count} 种")

        if missing_items:
            print(f"\n⚠️  警告：以下物品未找到：")
            for item in set(missing_items):
                print(f"   - {item}")

        return added_count


async def main():
    """主函数"""
    print("=" * 60)
    print("📜 凡人修仙传 - 符箓系统初始化")
    print("=" * 60)

    print("\n📝 开始创建符箓系统数据...\n")

    # 创建材料
    print("━" * 60)
    print("第一步：创建符箓材料（10种基础材料）")
    print("━" * 60)
    materials_added = await create_talisman_materials()

    # 创建符箓配方
    print("\n" + "━" * 60)
    print("第二步：创建符箓配方（30种符箓）")
    print("━" * 60)
    recipes_added = await create_talisman_recipes()

    # 总结
    print("\n" + "=" * 60)
    print("🎉 符箓系统初始化完成！")
    print("=" * 60)
    print(f"\n📊 数据统计：")
    print(f"   • 符箓材料：新增 {materials_added} 种")
    print(f"   • 符箓配方：新增 {recipes_added} 种")
    print(f"\n符箓类型分布：")
    print(f"   • 攻击符：10种")
    print(f"   • 防御符：6种")
    print(f"   • 治疗符：4种")
    print(f"   • 遁符：4种")
    print(f"   • 辅助符：6种")

    print("\n💡 下一步：")
    print("1. 测试制符命令: /制符 [符箓名称]")
    print("2. 查看符箓配方: /符箓列表")
    print("3. 查看制符等级: /制符等级")
    print("4. 收集材料开始制作符箓吧！\n")


if __name__ == "__main__":
    asyncio.run(main())
