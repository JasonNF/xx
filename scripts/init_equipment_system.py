"""完整装备体系初始化脚本 - 67件装备"""
import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from bot.models.database import init_db, AsyncSessionLocal
from bot.models.item import Item, ItemType, EquipmentQuality, EquipmentSlot
from sqlalchemy import select


async def create_mortal_equipment():
    """创建凡品装备（15件）"""
    async with AsyncSessionLocal() as session:
        equipment_data = [
            # ========== 武器系列（3件） ==========
            {
                "name": "青铜剑",
                "description": "最基础的修士武器，适合入门弟子",
                "item_type": ItemType.WEAPON,
                "quality": EquipmentQuality.MORTAL,
                "equipment_slot": EquipmentSlot.WEAPON,
                "attack_bonus": 20,
                "speed_bonus": 3,
                "buy_price": 1000,
                "sell_price": 500,
                "required_level": 1,
            },
            {
                "name": "精铁长剑",
                "description": "以精铁锻造的长剑，锋利耐用",
                "item_type": ItemType.WEAPON,
                "quality": EquipmentQuality.MORTAL,
                "equipment_slot": EquipmentSlot.WEAPON,
                "attack_bonus": 30,
                "speed_bonus": 5,
                "buy_price": 3000,
                "sell_price": 1500,
                "required_level": 3,
            },
            {
                "name": "青钢剑",
                "description": "青钢材质，锋芒初露，略有灵性",
                "item_type": ItemType.WEAPON,
                "quality": EquipmentQuality.MORTAL,
                "equipment_slot": EquipmentSlot.WEAPON,
                "attack_bonus": 40,
                "speed_bonus": 8,
                "buy_price": 8000,
                "sell_price": 4000,
                "required_level": 5,
                "special_attributes": '{"crit_rate": 0.03}',  # 暴击+3%
            },

            # ========== 副手系列（2件） ==========
            {
                "name": "木盾",
                "description": "简陋的木制盾牌，�供基础防护",
                "item_type": ItemType.ARMOR,
                "quality": EquipmentQuality.MORTAL,
                "equipment_slot": EquipmentSlot.OFF_HAND,
                "defense_bonus": 15,
                "hp_bonus": 50,
                "buy_price": 800,
                "sell_price": 400,
                "required_level": 1,
            },
            {
                "name": "铁盾",
                "description": "铁质盾牌，可有效格挡攻击",
                "item_type": ItemType.ARMOR,
                "quality": EquipmentQuality.MORTAL,
                "equipment_slot": EquipmentSlot.OFF_HAND,
                "defense_bonus": 25,
                "hp_bonus": 100,
                "buy_price": 2500,
                "sell_price": 1250,
                "required_level": 3,
                "special_attributes": '{"block_rate": 0.05}',  # 格挡+5%
            },

            # ========== 头部系列（2件） ==========
            {
                "name": "布帽",
                "description": "普通的布制头巾",
                "item_type": ItemType.ARMOR,
                "quality": EquipmentQuality.MORTAL,
                "equipment_slot": EquipmentSlot.HEAD,
                "defense_bonus": 10,
                "hp_bonus": 30,
                "buy_price": 500,
                "sell_price": 250,
                "required_level": 1,
            },
            {
                "name": "皮盔",
                "description": "兽皮制成的头盔，有一定防护力",
                "item_type": ItemType.ARMOR,
                "quality": EquipmentQuality.MORTAL,
                "equipment_slot": EquipmentSlot.HEAD,
                "defense_bonus": 20,
                "hp_bonus": 80,
                "buy_price": 2000,
                "sell_price": 1000,
                "required_level": 3,
            },

            # ========== 身体系列（3件） ==========
            {
                "name": "布衣",
                "description": "简单的布制长袍",
                "item_type": ItemType.ARMOR,
                "quality": EquipmentQuality.MORTAL,
                "equipment_slot": EquipmentSlot.BODY,
                "defense_bonus": 12,
                "hp_bonus": 40,
                "buy_price": 600,
                "sell_price": 300,
                "required_level": 1,
            },
            {
                "name": "皮甲",
                "description": "兽皮制成的轻甲，防御尚可",
                "item_type": ItemType.ARMOR,
                "quality": EquipmentQuality.MORTAL,
                "equipment_slot": EquipmentSlot.BODY,
                "defense_bonus": 25,
                "hp_bonus": 100,
                "buy_price": 2500,
                "sell_price": 1250,
                "required_level": 3,
            },
            {
                "name": "锁甲",
                "description": "铁环相连的锁子甲，防护力较强",
                "item_type": ItemType.ARMOR,
                "quality": EquipmentQuality.MORTAL,
                "equipment_slot": EquipmentSlot.BODY,
                "defense_bonus": 35,
                "hp_bonus": 150,
                "buy_price": 7000,
                "sell_price": 3500,
                "required_level": 5,
            },

            # ========== 腿部系列（2件） ==========
            {
                "name": "布裤",
                "description": "普通的布制长裤",
                "item_type": ItemType.ARMOR,
                "quality": EquipmentQuality.MORTAL,
                "equipment_slot": EquipmentSlot.LEGS,
                "defense_bonus": 8,
                "hp_bonus": 30,
                "buy_price": 400,
                "sell_price": 200,
                "required_level": 1,
            },
            {
                "name": "皮腿甲",
                "description": "兽皮制成的护腿",
                "item_type": ItemType.ARMOR,
                "quality": EquipmentQuality.MORTAL,
                "equipment_slot": EquipmentSlot.LEGS,
                "defense_bonus": 18,
                "hp_bonus": 80,
                "buy_price": 1800,
                "sell_price": 900,
                "required_level": 3,
            },

            # ========== 脚部系列（2件） ==========
            {
                "name": "布鞋",
                "description": "普通的布鞋",
                "item_type": ItemType.ARMOR,
                "quality": EquipmentQuality.MORTAL,
                "equipment_slot": EquipmentSlot.FEET,
                "defense_bonus": 6,
                "speed_bonus": 5,
                "buy_price": 300,
                "sell_price": 150,
                "required_level": 1,
            },
            {
                "name": "皮靴",
                "description": "轻便的皮革靴子",
                "item_type": ItemType.ARMOR,
                "quality": EquipmentQuality.MORTAL,
                "equipment_slot": EquipmentSlot.FEET,
                "defense_bonus": 15,
                "speed_bonus": 10,
                "buy_price": 1500,
                "sell_price": 750,
                "required_level": 3,
                "special_attributes": '{"dodge_rate": 0.03}',  # 闪避+3%
            },

            # ========== 饰品系列（1件） ==========
            {
                "name": "护身符",
                "description": "简单的护身符箓，可提供些许庇护",
                "item_type": ItemType.ACCESSORY,
                "quality": EquipmentQuality.MORTAL,
                "equipment_slot": EquipmentSlot.ACCESSORY,
                "hp_bonus": 50,
                "spiritual_power_bonus": 30,
                "buy_price": 2000,
                "sell_price": 1000,
                "required_level": 1,
            },
        ]

        for eq_data in equipment_data:
            equipment = Item(**eq_data)
            session.add(equipment)

        await session.commit()
        print(f"✅ 创建了 {len(equipment_data)} 件凡品装备")


async def create_immortal_equipment():
    """创建仙品装备（28件）"""
    async with AsyncSessionLocal() as session:
        equipment_data = [
            # ========== 武器系列（4件） ==========
            {
                "name": "寒铁剑",
                "description": "以寒铁精炼而成的飞剑，剑身泛着淡淡寒气",
                "item_type": ItemType.WEAPON,
                "quality": EquipmentQuality.IMMORTAL,
                "equipment_slot": EquipmentSlot.WEAPON,
                "attack_bonus": 60,
                "speed_bonus": 12,
                "buy_price": 20000,
                "sell_price": 10000,
                "required_level": 8,
                "special_attributes": '{"crit_rate": 0.05}',
            },
            {
                "name": "玄铁重剑",
                "description": "玄铁锻造的厚重大剑，重剑无锋大巧不工",
                "item_type": ItemType.WEAPON,
                "quality": EquipmentQuality.IMMORTAL,
                "equipment_slot": EquipmentSlot.WEAPON,
                "attack_bonus": 75,
                "buy_price": 35000,
                "sell_price": 17500,
                "required_level": 10,
                "special_attributes": '{"crit_damage": 0.15}',  # 暴击伤害+15%
            },
            {
                "name": "飞虹剑",
                "description": "传说中的名剑，剑光如虹贯日",
                "item_type": ItemType.WEAPON,
                "quality": EquipmentQuality.IMMORTAL,
                "equipment_slot": EquipmentSlot.WEAPON,
                "attack_bonus": 85,
                "speed_bonus": 18,
                "buy_price": 50000,
                "sell_price": 25000,
                "required_level": 12,
                "special_attributes": '{"crit_rate": 0.08, "combo_chance": 0.05}',
            },
            {
                "name": "青竹蜂云剑",
                "description": "韩立炼气期主力飞剑，由青竹蜂剑炼化而成，蕴含剑阵之妙",
                "item_type": ItemType.WEAPON,
                "quality": EquipmentQuality.IMMORTAL,
                "equipment_slot": EquipmentSlot.WEAPON,
                "attack_bonus": 95,
                "speed_bonus": 22,
                "buy_price": 80000,
                "sell_price": 40000,
                "required_level": 14,
                "special_attributes": '{"crit_rate": 0.10, "attack_percent": 0.15}',
            },

            # ========== 副手系列（4件） ==========
            {
                "name": "金刚盾",
                "description": "坚固的下品法器，提供基础防护",
                "item_type": ItemType.ARMOR,
                "quality": EquipmentQuality.IMMORTAL,
                "equipment_slot": EquipmentSlot.OFF_HAND,
                "defense_bonus": 40,
                "hp_bonus": 200,
                "buy_price": 18000,
                "sell_price": 9000,
                "required_level": 8,
                "special_attributes": '{"block_rate": 0.08}',
            },
            {
                "name": "玄铁盾",
                "description": "玄铁铸造的厚重盾牌，可抵挡强力攻击",
                "item_type": ItemType.ARMOR,
                "quality": EquipmentQuality.IMMORTAL,
                "equipment_slot": EquipmentSlot.OFF_HAND,
                "defense_bonus": 55,
                "hp_bonus": 300,
                "buy_price": 32000,
                "sell_price": 16000,
                "required_level": 10,
                "special_attributes": '{"block_rate": 0.12, "damage_reduction": 0.05}',
            },
            {
                "name": "青木短剑",
                "description": "副手武器，可与主手武器形成双持",
                "item_type": ItemType.WEAPON,
                "quality": EquipmentQuality.IMMORTAL,
                "equipment_slot": EquipmentSlot.OFF_HAND,
                "attack_bonus": 25,
                "speed_bonus": 15,
                "buy_price": 28000,
                "sell_price": 14000,
                "required_level": 10,
                "special_attributes": '{"dual_wield_damage": 0.10}',
            },
            {
                "name": "龟甲盾",
                "description": "上古龟类妖兽甲壳炼制，坚不可摧",
                "item_type": ItemType.ARMOR,
                "quality": EquipmentQuality.IMMORTAL,
                "equipment_slot": EquipmentSlot.OFF_HAND,
                "defense_bonus": 70,
                "hp_bonus": 400,
                "buy_price": 60000,
                "sell_price": 30000,
                "required_level": 12,
                "special_attributes": '{"block_rate": 0.15, "reflect_damage": 0.03}',
            },

            # ========== 头部系列（4件） ==========
            {
                "name": "青铜战盔",
                "description": "青铜铸造的战盔，坚固耐用",
                "item_type": ItemType.ARMOR,
                "quality": EquipmentQuality.IMMORTAL,
                "equipment_slot": EquipmentSlot.HEAD,
                "defense_bonus": 35,
                "hp_bonus": 150,
                "buy_price": 15000,
                "sell_price": 7500,
                "required_level": 8,
            },
            {
                "name": "玄铁战盔",
                "description": "玄铁锻造的重型头盔",
                "item_type": ItemType.ARMOR,
                "quality": EquipmentQuality.IMMORTAL,
                "equipment_slot": EquipmentSlot.HEAD,
                "defense_bonus": 50,
                "hp_bonus": 250,
                "buy_price": 30000,
                "sell_price": 15000,
                "required_level": 10,
                "special_attributes": '{"damage_reduction": 0.03}',
            },
            {
                "name": "精钢战盔",
                "description": "精钢铸造，可抵抗眩晕效果",
                "item_type": ItemType.ARMOR,
                "quality": EquipmentQuality.IMMORTAL,
                "equipment_slot": EquipmentSlot.HEAD,
                "defense_bonus": 60,
                "hp_bonus": 350,
                "buy_price": 45000,
                "sell_price": 22500,
                "required_level": 12,
                "special_attributes": '{"stun_resist": 0.10}',
            },
            {
                "name": "凤翎冠",
                "description": "以凤凰羽毛编织的法冠，灵气逼人",
                "item_type": ItemType.ARMOR,
                "quality": EquipmentQuality.IMMORTAL,
                "equipment_slot": EquipmentSlot.HEAD,
                "defense_bonus": 55,
                "hp_bonus": 300,
                "spiritual_power_bonus": 150,
                "buy_price": 50000,
                "sell_price": 25000,
                "required_level": 12,
                "special_attributes": '{"spell_speed": 0.05}',
            },

            # ========== 身体系列（4件） ==========
            {
                "name": "青铜战甲",
                "description": "青铜打造的重甲",
                "item_type": ItemType.ARMOR,
                "quality": EquipmentQuality.IMMORTAL,
                "equipment_slot": EquipmentSlot.BODY,
                "defense_bonus": 45,
                "hp_bonus": 200,
                "buy_price": 20000,
                "sell_price": 10000,
                "required_level": 8,
            },
            {
                "name": "玄铁战甲",
                "description": "玄铁锻造的重型战甲",
                "item_type": ItemType.ARMOR,
                "quality": EquipmentQuality.IMMORTAL,
                "equipment_slot": EquipmentSlot.BODY,
                "defense_bonus": 65,
                "hp_bonus": 350,
                "buy_price": 40000,
                "sell_price": 20000,
                "required_level": 10,
                "special_attributes": '{"damage_reduction": 0.05}',
            },
            {
                "name": "精钢重甲",
                "description": "精钢铸造的超重型铠甲",
                "item_type": ItemType.ARMOR,
                "quality": EquipmentQuality.IMMORTAL,
                "equipment_slot": EquipmentSlot.BODY,
                "defense_bonus": 80,
                "hp_bonus": 500,
                "buy_price": 60000,
                "sell_price": 30000,
                "required_level": 12,
                "special_attributes": '{"damage_reduction": 0.08}',
            },
            {
                "name": "云纹道袍",
                "description": "绘有云纹的法修道袍，可增幅法术",
                "item_type": ItemType.ARMOR,
                "quality": EquipmentQuality.IMMORTAL,
                "equipment_slot": EquipmentSlot.BODY,
                "defense_bonus": 60,
                "hp_bonus": 300,
                "spiritual_power_bonus": 200,
                "buy_price": 55000,
                "sell_price": 27500,
                "required_level": 12,
                "special_attributes": '{"spell_damage": 0.10}',
            },

            # ========== 腿部系列（4件） ==========
            {
                "name": "青铜护腿",
                "description": "青铜护腿甲",
                "item_type": ItemType.ARMOR,
                "quality": EquipmentQuality.IMMORTAL,
                "equipment_slot": EquipmentSlot.LEGS,
                "defense_bonus": 30,
                "hp_bonus": 150,
                "buy_price": 12000,
                "sell_price": 6000,
                "required_level": 8,
            },
            {
                "name": "玄铁护腿",
                "description": "玄铁锻造的重型护腿",
                "item_type": ItemType.ARMOR,
                "quality": EquipmentQuality.IMMORTAL,
                "equipment_slot": EquipmentSlot.LEGS,
                "defense_bonus": 45,
                "hp_bonus": 250,
                "buy_price": 25000,
                "sell_price": 12500,
                "required_level": 10,
            },
            {
                "name": "精钢护腿",
                "description": "精钢制成的腿甲，可提升移动速度",
                "item_type": ItemType.ARMOR,
                "quality": EquipmentQuality.IMMORTAL,
                "equipment_slot": EquipmentSlot.LEGS,
                "defense_bonus": 55,
                "hp_bonus": 350,
                "buy_price": 38000,
                "sell_price": 19000,
                "required_level": 12,
                "special_attributes": '{"move_speed": 0.05}',
            },
            {
                "name": "云行裤",
                "description": "轻盈如云的法修裤装",
                "item_type": ItemType.ARMOR,
                "quality": EquipmentQuality.IMMORTAL,
                "equipment_slot": EquipmentSlot.LEGS,
                "defense_bonus": 50,
                "hp_bonus": 250,
                "speed_bonus": 20,
                "buy_price": 35000,
                "sell_price": 17500,
                "required_level": 12,
                "special_attributes": '{"dodge_rate": 0.08}',
            },

            # ========== 脚部系列（4件） ==========
            {
                "name": "铁靴",
                "description": "铁制战靴",
                "item_type": ItemType.ARMOR,
                "quality": EquipmentQuality.IMMORTAL,
                "equipment_slot": EquipmentSlot.FEET,
                "defense_bonus": 25,
                "speed_bonus": 15,
                "buy_price": 10000,
                "sell_price": 5000,
                "required_level": 8,
                "special_attributes": '{"dodge_rate": 0.05}',
            },
            {
                "name": "玄铁战靴",
                "description": "玄铁锻造的重型战靴",
                "item_type": ItemType.ARMOR,
                "quality": EquipmentQuality.IMMORTAL,
                "equipment_slot": EquipmentSlot.FEET,
                "defense_bonus": 38,
                "speed_bonus": 22,
                "buy_price": 22000,
                "sell_price": 11000,
                "required_level": 10,
                "special_attributes": '{"dodge_rate": 0.08, "move_speed": 0.05}',
            },
            {
                "name": "追风靴",
                "description": "传说中的神行靴，速度惊人",
                "item_type": ItemType.ARMOR,
                "quality": EquipmentQuality.IMMORTAL,
                "equipment_slot": EquipmentSlot.FEET,
                "defense_bonus": 45,
                "speed_bonus": 30,
                "buy_price": 35000,
                "sell_price": 17500,
                "required_level": 12,
                "special_attributes": '{"dodge_rate": 0.12, "move_speed": 0.10}',
            },
            {
                "name": "云履",
                "description": "踏云而行的仙家鞋履",
                "item_type": ItemType.ARMOR,
                "quality": EquipmentQuality.IMMORTAL,
                "equipment_slot": EquipmentSlot.FEET,
                "defense_bonus": 40,
                "speed_bonus": 28,
                "spiritual_power_bonus": 100,
                "buy_price": 32000,
                "sell_price": 16000,
                "required_level": 12,
                "special_attributes": '{"dodge_rate": 0.10}',
            },

            # ========== 饰品系列（4件） ==========
            {
                "name": "玉佩",
                "description": "温润的玉石佩饰，可提升全属性",
                "item_type": ItemType.ACCESSORY,
                "quality": EquipmentQuality.IMMORTAL,
                "equipment_slot": EquipmentSlot.ACCESSORY,
                "hp_bonus": 150,
                "spiritual_power_bonus": 100,
                "buy_price": 25000,
                "sell_price": 12500,
                "required_level": 8,
                "special_attributes": '{"all_attributes": 0.03}',
            },
            {
                "name": "护心镜",
                "description": "古修士遗留的护心宝镜",
                "item_type": ItemType.ACCESSORY,
                "quality": EquipmentQuality.IMMORTAL,
                "equipment_slot": EquipmentSlot.ACCESSORY,
                "hp_bonus": 250,
                "defense_bonus": 20,
                "buy_price": 35000,
                "sell_price": 17500,
                "required_level": 10,
                "special_attributes": '{"damage_reduction": 0.05}',
            },
            {
                "name": "灵石项链",
                "description": "镶嵌灵石的项链，可增幅灵力",
                "item_type": ItemType.ACCESSORY,
                "quality": EquipmentQuality.IMMORTAL,
                "equipment_slot": EquipmentSlot.ACCESSORY,
                "spiritual_power_bonus": 200,
                "buy_price": 40000,
                "sell_price": 20000,
                "required_level": 11,
                "special_attributes": '{"spell_damage": 0.08, "spirit_regen": 5}',
            },
            {
                "name": "凤凰羽",
                "description": "传说中凤凰的羽毛，蕴含重生之力",
                "item_type": ItemType.ACCESSORY,
                "quality": EquipmentQuality.IMMORTAL,
                "equipment_slot": EquipmentSlot.ACCESSORY,
                "hp_bonus": 200,
                "attack_bonus": 20,
                "buy_price": 80000,
                "sell_price": 40000,
                "required_level": 13,
                "special_attributes": '{"revive": 1}',  # 复活一次
                "description_extra": "死亡时自动触发，满血复活（冷却24小时）",
            },
        ]

        for eq_data in equipment_data:
            equipment = Item(**eq_data)
            session.add(equipment)

        await session.commit()
        print(f"✅ 创建了 {len(equipment_data)} 件仙品装备")


async def create_divine_equipment():
    """创建神品装备 - 四象套装（24件）"""
    async with AsyncSessionLocal() as session:
        # 首先获取或创建套装记录
        from bot.models.item import EquipmentSet

        # 创建四象套装定义
        sets_data = [
            {
                "name": "青龙套装",
                "description": "传说中东方青龙之力凝聚的套装，主攻击与速度",
                "element": "木",
                "set_type": "攻击型",
            },
            {
                "name": "朱雀套装",
                "description": "传说中南方朱雀之力凝聚的套装，主爆发与灵力",
                "element": "火",
                "set_type": "爆发型",
            },
            {
                "name": "玄武套装",
                "description": "传说中北方玄武之力凝聚的套装，主防御与生命",
                "element": "水",
                "set_type": "防御型",
            },
            {
                "name": "白虎套装",
                "description": "传说中西方白虎之力凝聚的套装，主全面平衡",
                "element": "金",
                "set_type": "平衡型",
            },
        ]

        set_ids = {}
        for set_data in sets_data:
            equipment_set = EquipmentSet(**set_data)
            session.add(equipment_set)
            await session.flush()  # 获取ID
            set_ids[set_data["name"]] = equipment_set.id

        # 创建装备数据
        equipment_data = [
            # ========== 青龙套装（6件）==========
            {
                "name": "青龙战剑",
                "description": "青龙之力凝聚的神兵，剑身盘绕青龙虚影",
                "item_type": ItemType.WEAPON,
                "quality": EquipmentQuality.DIVINE,
                "equipment_slot": EquipmentSlot.WEAPON,
                "set_id": set_ids["青龙套装"],
                "attack_bonus": 120,
                "speed_bonus": 35,
                "required_level": 15,
                "special_attributes": '{"crit_rate": 0.15, "crit_damage": 0.25}',
                "description_extra": "套装部件，收集完整套装可激活强大效果",
            },
            {
                "name": "青龙战盔",
                "description": "刻有青龙图腾的战盔",
                "item_type": ItemType.ARMOR,
                "quality": EquipmentQuality.DIVINE,
                "equipment_slot": EquipmentSlot.HEAD,
                "set_id": set_ids["青龙套装"],
                "defense_bonus": 75,
                "hp_bonus": 600,
                "attack_bonus": 25,
                "speed_bonus": 15,
                "required_level": 15,
            },
            {
                "name": "青龙战甲",
                "description": "刻有青龙鳞片纹路的战甲",
                "item_type": ItemType.ARMOR,
                "quality": EquipmentQuality.DIVINE,
                "equipment_slot": EquipmentSlot.BODY,
                "set_id": set_ids["青龙套装"],
                "defense_bonus": 95,
                "hp_bonus": 800,
                "attack_bonus": 30,
                "required_level": 15,
            },
            {
                "name": "青龙护腿",
                "description": "青龙之力加持的护腿",
                "item_type": ItemType.ARMOR,
                "quality": EquipmentQuality.DIVINE,
                "equipment_slot": EquipmentSlot.LEGS,
                "set_id": set_ids["青龙套装"],
                "defense_bonus": 70,
                "hp_bonus": 500,
                "attack_bonus": 20,
                "speed_bonus": 20,
                "required_level": 15,
            },
            {
                "name": "青龙战靴",
                "description": "迅捷如龙的战靴",
                "item_type": ItemType.ARMOR,
                "quality": EquipmentQuality.DIVINE,
                "equipment_slot": EquipmentSlot.FEET,
                "set_id": set_ids["青龙套装"],
                "defense_bonus": 55,
                "speed_bonus": 40,
                "attack_bonus": 15,
                "required_level": 15,
                "special_attributes": '{"dodge_rate": 0.15}',
            },
            {
                "name": "青龙玉佩",
                "description": "蕴含青龙精血的玉佩",
                "item_type": ItemType.ACCESSORY,
                "quality": EquipmentQuality.DIVINE,
                "equipment_slot": EquipmentSlot.ACCESSORY,
                "set_id": set_ids["青龙套装"],
                "hp_bonus": 400,
                "attack_bonus": 40,
                "speed_bonus": 30,
                "required_level": 15,
                "special_attributes": '{"all_attributes": 0.08}',
            },

            # ========== 朱雀套装（6件） ==========
            {
                "name": "朱雀焚天剑",
                "description": "朱雀真火淬炼的神剑，挥舞间火焰缭绕",
                "item_type": ItemType.WEAPON,
                "quality": EquipmentQuality.DIVINE,
                "equipment_slot": EquipmentSlot.WEAPON,
                "set_id": set_ids["朱雀套装"],
                "attack_bonus": 135,
                "required_level": 15,
                "special_attributes": '{"crit_rate": 0.18, "crit_damage": 0.40, "fire_damage": 0.20}',
            },
            {
                "name": "朱雀烈焰盔",
                "description": "烈火缠绕的战盔",
                "item_type": ItemType.ARMOR,
                "quality": EquipmentQuality.DIVINE,
                "equipment_slot": EquipmentSlot.HEAD,
                "set_id": set_ids["朱雀套装"],
                "defense_bonus": 70,
                "hp_bonus": 550,
                "attack_bonus": 30,
                "spiritual_power_bonus": 250,
                "required_level": 15,
            },
            {
                "name": "朱雀火羽甲",
                "description": "朱雀羽毛编织的战甲",
                "item_type": ItemType.ARMOR,
                "quality": EquipmentQuality.DIVINE,
                "equipment_slot": EquipmentSlot.BODY,
                "set_id": set_ids["朱雀套装"],
                "defense_bonus": 90,
                "hp_bonus": 750,
                "attack_bonus": 35,
                "required_level": 15,
                "special_attributes": '{"spell_damage": 0.15}',
            },
            {
                "name": "朱雀炎腿",
                "description": "烈焰加持的护腿",
                "item_type": ItemType.ARMOR,
                "quality": EquipmentQuality.DIVINE,
                "equipment_slot": EquipmentSlot.LEGS,
                "set_id": set_ids["朱雀套装"],
                "defense_bonus": 65,
                "hp_bonus": 450,
                "attack_bonus": 25,
                "spiritual_power_bonus": 200,
                "required_level": 15,
            },
            {
                "name": "朱雀灵靴",
                "description": "踏火而行的灵靴",
                "item_type": ItemType.ARMOR,
                "quality": EquipmentQuality.DIVINE,
                "equipment_slot": EquipmentSlot.FEET,
                "set_id": set_ids["朱雀套装"],
                "defense_bonus": 50,
                "speed_bonus": 35,
                "attack_bonus": 20,
                "spiritual_power_bonus": 180,
                "required_level": 15,
            },
            {
                "name": "朱雀炎珠",
                "description": "朱雀真火凝聚的宝珠",
                "item_type": ItemType.ACCESSORY,
                "quality": EquipmentQuality.DIVINE,
                "equipment_slot": EquipmentSlot.ACCESSORY,
                "set_id": set_ids["朱雀套装"],
                "hp_bonus": 350,
                "attack_bonus": 45,
                "spiritual_power_bonus": 300,
                "required_level": 15,
                "special_attributes": '{"crit_damage": 0.25}',
            },

            # ========== 玄武套装（6件） ==========
            {
                "name": "玄武镇海刀",
                "description": "玄武之力加持的厚重战刀",
                "item_type": ItemType.WEAPON,
                "quality": EquipmentQuality.DIVINE,
                "equipment_slot": EquipmentSlot.WEAPON,
                "set_id": set_ids["玄武套装"],
                "attack_bonus": 100,
                "defense_bonus": 40,
                "hp_bonus": 600,
                "required_level": 15,
                "special_attributes": '{"damage_reduction": 0.10}',
            },
            {
                "name": "玄武铁盔",
                "description": "坚如磐石的铁盔",
                "item_type": ItemType.ARMOR,
                "quality": EquipmentQuality.DIVINE,
                "equipment_slot": EquipmentSlot.HEAD,
                "set_id": set_ids["玄武套装"],
                "defense_bonus": 95,
                "hp_bonus": 800,
                "required_level": 15,
                "special_attributes": '{"damage_reduction": 0.08}',
            },
            {
                "name": "玄武重甲",
                "description": "厚重无比的龟甲战甲",
                "item_type": ItemType.ARMOR,
                "quality": EquipmentQuality.DIVINE,
                "equipment_slot": EquipmentSlot.BODY,
                "set_id": set_ids["玄武套装"],
                "defense_bonus": 120,
                "hp_bonus": 1200,
                "required_level": 15,
                "special_attributes": '{"damage_reduction": 0.12}',
            },
            {
                "name": "玄武护腿",
                "description": "坚不可摧的护腿",
                "item_type": ItemType.ARMOR,
                "quality": EquipmentQuality.DIVINE,
                "equipment_slot": EquipmentSlot.LEGS,
                "set_id": set_ids["玄武套装"],
                "defense_bonus": 85,
                "hp_bonus": 700,
                "required_level": 15,
                "special_attributes": '{"block_rate": 0.15}',
            },
            {
                "name": "玄武战靴",
                "description": "稳如泰山的战靴",
                "item_type": ItemType.ARMOR,
                "quality": EquipmentQuality.DIVINE,
                "equipment_slot": EquipmentSlot.FEET,
                "set_id": set_ids["玄武套装"],
                "defense_bonus": 70,
                "hp_bonus": 500,
                "required_level": 15,
                "special_attributes": '{"tenacity": 0.10}',
            },
            {
                "name": "玄武龟印",
                "description": "蕴含玄武精魂的印记",
                "item_type": ItemType.ACCESSORY,
                "quality": EquipmentQuality.DIVINE,
                "equipment_slot": EquipmentSlot.ACCESSORY,
                "set_id": set_ids["玄武套装"],
                "hp_bonus": 1000,
                "defense_bonus": 45,
                "required_level": 15,
                "special_attributes": '{"damage_reduction": 0.15, "hp_regen": 50}',
            },

            # ========== 白虎套装（6件） ==========
            {
                "name": "白虎斩魂剑",
                "description": "白虎煞气凝聚的杀剑",
                "item_type": ItemType.WEAPON,
                "quality": EquipmentQuality.DIVINE,
                "equipment_slot": EquipmentSlot.WEAPON,
                "set_id": set_ids["白虎套装"],
                "attack_bonus": 110,
                "defense_bonus": 20,
                "required_level": 15,
                "special_attributes": '{"all_attributes": 0.10, "attack_bonus": 25}',
            },
            {
                "name": "白虎战盔",
                "description": "白虎纹路的战盔",
                "item_type": ItemType.ARMOR,
                "quality": EquipmentQuality.DIVINE,
                "equipment_slot": EquipmentSlot.HEAD,
                "set_id": set_ids["白虎套装"],
                "defense_bonus": 80,
                "hp_bonus": 650,
                "attack_bonus": 20,
                "required_level": 15,
            },
            {
                "name": "白虎战甲",
                "description": "攻守兼备的战甲",
                "item_type": ItemType.ARMOR,
                "quality": EquipmentQuality.DIVINE,
                "equipment_slot": EquipmentSlot.BODY,
                "set_id": set_ids["白虎套装"],
                "defense_bonus": 100,
                "hp_bonus": 900,
                "attack_bonus": 25,
                "required_level": 15,
            },
            {
                "name": "白虎护腿",
                "description": "均衡的护腿装备",
                "item_type": ItemType.ARMOR,
                "quality": EquipmentQuality.DIVINE,
                "equipment_slot": EquipmentSlot.LEGS,
                "set_id": set_ids["白虎套装"],
                "defense_bonus": 75,
                "hp_bonus": 600,
                "attack_bonus": 18,
                "required_level": 15,
            },
            {
                "name": "白虎战靴",
                "description": "迅捷而稳固的战靴",
                "item_type": ItemType.ARMOR,
                "quality": EquipmentQuality.DIVINE,
                "equipment_slot": EquipmentSlot.FEET,
                "set_id": set_ids["白虎套装"],
                "defense_bonus": 60,
                "speed_bonus": 35,
                "attack_bonus": 15,
                "required_level": 15,
            },
            {
                "name": "白虎令",
                "description": "白虎之力的象征",
                "item_type": ItemType.ACCESSORY,
                "quality": EquipmentQuality.DIVINE,
                "equipment_slot": EquipmentSlot.ACCESSORY,
                "set_id": set_ids["白虎套装"],
                "hp_bonus": 500,
                "attack_bonus": 35,
                "defense_bonus": 35,
                "required_level": 15,
                "special_attributes": '{"all_attributes": 0.15}',
            },
        ]

        for eq_data in equipment_data:
            equipment = Item(**eq_data)
            session.add(equipment)

        await session.commit()
        print(f"✅ 创建了 {len(equipment_data)} 件神品装备（四象套装）")


async def main():
    """主函数"""
    print("=" * 60)
    print("⚔️ 完整装备体系初始化")
    print("=" * 60)

    print("\n📊 开始创建装备数据...\n")

    await create_mortal_equipment()  # 15件凡品
    await create_immortal_equipment()  # 28件仙品
    await create_divine_equipment()  # 24件神品

    print("\n" + "=" * 60)
    print("🎉 装备体系初始化完成！")
    print("=" * 60)
    print("\n📊 装备统计：")
    print("  • 凡品装备：15件")
    print("  • 仙品装备：28件")
    print("  • 神品装备：24件（四象套装）")
    print("  • 总计：67件装备")
    print("\n💡 下一步：")
    print("1. 运行此脚本初始化装备数据")
    print("2. 启动游戏测试装备系统")
    print("3. 使用 /商店 命令查看可购买装备")
    print("4. 使用 /背包 命令查看拥有的装备\n")


if __name__ == "__main__":
    asyncio.run(main())
