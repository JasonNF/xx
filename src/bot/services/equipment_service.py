"""装备系统服务层"""
import random
from typing import Tuple, Optional, Dict, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from bot.models.item import (
    Item,
    PlayerInventory,
    EquipmentQuality,
    EquipmentSlot,
    EquipmentSet,
    EquipmentSetBonus,
    EnhancementRecord
)
from bot.models import Player
from bot.config.equipment_config import (
    get_enhancement_success_rate,
    calculate_enhancement_cost,
    get_enhancement_penalty,
    ENHANCEMENT_MAX_LEVEL,
    ENHANCEMENT_ATTRIBUTE_BONUS_PER_LEVEL,
    QUALITY_ATTRIBUTE_MULTIPLIER,
    EQUIPMENT_SETS_CONFIG
)


class EquipmentService:
    """装备系统服务"""

    @staticmethod
    async def enhance_equipment(
        db: AsyncSession,
        player: Player,
        inventory_item: PlayerInventory,
        item: Item,
        use_protection: bool = False
    ) -> Tuple[bool, str, Optional[Dict]]:
        """强化装备

        Args:
            db: 数据库会话
            player: 玩家
            inventory_item: 背包中的装备
            item: 装备物品
            use_protection: 是否使用保护符

        Returns:
            (是否成功, 消息, 强化数据)
        """
        # 检查是否是装备
        if not item.quality:
            return False, "❌ 该物品不是装备，无法强化", None

        # 检查是否已达最大强化等级
        max_level = ENHANCEMENT_MAX_LEVEL.get(item.quality.value, 10)
        if inventory_item.enhancement_level >= max_level:
            return False, f"❌ 该装备已达最大强化等级 +{max_level}", None

        # 计算强化消耗
        cost = calculate_enhancement_cost(inventory_item.enhancement_level, item.quality.value)

        # 检查灵石
        if player.spirit_stones < cost:
            return False, f"❌ 灵石不足，需要 {cost:,} 灵石", None

        # 扣除灵石
        player.spirit_stones -= cost

        # 获取成功率
        success_rate = get_enhancement_success_rate(inventory_item.enhancement_level)

        # 判定成功
        roll = random.random()
        success = roll < success_rate

        from_level = inventory_item.enhancement_level
        to_level = from_level

        if success:
            # 强化成功，等级+1
            inventory_item.enhancement_level += 1
            to_level = inventory_item.enhancement_level
            message = f"✅ 强化成功！{item.name} +{from_level} → +{to_level}"
        else:
            # 强化失败
            penalty = get_enhancement_penalty(inventory_item.enhancement_level)

            if use_protection or penalty == 0:
                # 使用保护符或低等级不掉级
                message = f"💔 强化失败！{item.name} 等级未变 +{from_level}"
            else:
                # 掉级
                inventory_item.enhancement_level = max(0, inventory_item.enhancement_level + penalty)
                to_level = inventory_item.enhancement_level
                message = f"💥 强化失败！{item.name} +{from_level} → +{to_level}"

        # 记录强化
        enhancement_record = EnhancementRecord(
            player_id=player.id,
            inventory_id=inventory_item.id,
            from_level=from_level,
            to_level=to_level,
            success=success,
            cost=cost,
            used_protection=use_protection
        )
        db.add(enhancement_record)

        await db.commit()
        await db.refresh(inventory_item)

        enhancement_data = {
            "success": success,
            "from_level": from_level,
            "to_level": to_level,
            "cost": cost,
            "success_rate": success_rate,
            "used_protection": use_protection
        }

        return True, message, enhancement_data

    @staticmethod
    async def calculate_equipment_attributes(
        db: AsyncSession,
        inventory_item: PlayerInventory,
        item: Item
    ) -> Dict[str, int]:
        """计算装备的最终属性

        Args:
            db: 数据库会话
            inventory_item: 背包中的装备
            item: 装备物品

        Returns:
            属性字典 {"attack": 100, "defense": 50, ...}
        """
        attributes = {
            "attack": item.attack_bonus,
            "defense": item.defense_bonus,
            "hp": item.hp_bonus,
            "spiritual": item.spiritual_bonus,
            "speed": item.speed_bonus
        }

        # 应用品质倍率
        if item.quality:
            quality_multiplier = QUALITY_ATTRIBUTE_MULTIPLIER.get(item.quality.value, 1.0)
            for key in attributes:
                attributes[key] = int(attributes[key] * quality_multiplier)

        # 应用强化加成
        enhancement_multiplier = 1.0 + (inventory_item.enhancement_level * ENHANCEMENT_ATTRIBUTE_BONUS_PER_LEVEL)
        for key in attributes:
            attributes[key] = int(attributes[key] * enhancement_multiplier)

        return attributes

    @staticmethod
    async def check_set_bonus(
        db: AsyncSession,
        player_id: int
    ) -> Dict[str, List[Dict]]:
        """检查玩家的套装效果

        Args:
            db: 数据库会话
            player_id: 玩家ID

        Returns:
            套装效果字典 {
                "青龙": [
                    {"piece_count": 2, "bonuses": [...]},
                    {"piece_count": 4, "bonuses": [...]}
                ]
            }
        """
        # 获取玩家所有装备的物品
        result = await db.execute(
            select(PlayerInventory, Item)
            .join(Item, PlayerInventory.item_id == Item.id)
            .where(
                PlayerInventory.player_id == player_id,
                PlayerInventory.is_equipped == True,
                Item.set_id.isnot(None)
            )
        )
        equipped_items = result.all()

        # 按套装分组
        set_counts: Dict[int, List[Tuple[PlayerInventory, Item]]] = {}
        for inv_item, item in equipped_items:
            if item.set_id not in set_counts:
                set_counts[item.set_id] = []
            set_counts[item.set_id].append((inv_item, item))

        # 获取套装信息
        active_sets: Dict[str, List[Dict]] = {}

        for set_id, items in set_counts.items():
            piece_count = len(items)

            # 获取套装定义
            result = await db.execute(
                select(EquipmentSet).where(EquipmentSet.id == set_id)
            )
            equipment_set = result.scalar_one_or_none()

            if not equipment_set:
                continue

            # 获取套装效果
            result = await db.execute(
                select(EquipmentSetBonus)
                .where(
                    EquipmentSetBonus.set_id == set_id,
                    EquipmentSetBonus.piece_count <= piece_count
                )
                .order_by(EquipmentSetBonus.piece_count)
            )
            bonuses = result.scalars().all()

            if bonuses:
                set_name = equipment_set.name.replace("套装", "")  # 青龙套装 -> 青龙

                active_sets[set_name] = []
                for bonus in bonuses:
                    # 从配置中获取完整的bonus描述
                    config_bonuses = []
                    if set_name in EQUIPMENT_SETS_CONFIG:
                        set_config = EQUIPMENT_SETS_CONFIG[set_name]
                        if bonus.piece_count in set_config["bonuses"]:
                            config_bonuses = set_config["bonuses"][bonus.piece_count]

                    active_sets[set_name].append({
                        "piece_count": bonus.piece_count,
                        "bonuses": config_bonuses
                    })

        return active_sets

    @staticmethod
    async def get_equipped_items(
        db: AsyncSession,
        player_id: int
    ) -> Dict[str, Tuple[PlayerInventory, Item]]:
        """获取玩家装备的所有装备

        Args:
            db: 数据库会话
            player_id: 玩家ID

        Returns:
            装备字典 {"武器": (inventory_item, item), "头盔": (...), ...}
        """
        result = await db.execute(
            select(PlayerInventory, Item)
            .join(Item, PlayerInventory.item_id == Item.id)
            .where(
                PlayerInventory.player_id == player_id,
                PlayerInventory.is_equipped == True
            )
        )
        equipped_list = result.all()

        equipped_dict: Dict[str, Tuple[PlayerInventory, Item]] = {}
        for inv_item, item in equipped_list:
            if item.equipment_slot:
                equipped_dict[item.equipment_slot.value] = (inv_item, item)

        return equipped_dict

    @staticmethod
    async def equip_item(
        db: AsyncSession,
        player_id: int,
        inventory_item: PlayerInventory,
        item: Item
    ) -> Tuple[bool, str]:
        """装备物品

        Args:
            db: 数据库会话
            player_id: 玩家ID
            inventory_item: 背包中的装备
            item: 装备物品

        Returns:
            (是否成功, 消息)
        """
        # 检查是否是装备
        if not item.equipment_slot:
            return False, "❌ 该物品不是装备"

        # 检查是否已装备
        if inventory_item.is_equipped:
            return False, "❌ 该装备已装备"

        # 检查使用条件
        result = await db.execute(
            select(Player).where(Player.id == player_id)
        )
        player = result.scalar_one_or_none()

        if not player:
            return False, "❌ 玩家不存在"

        # TODO: 检查境界要求（需要添加境界系统）
        # if item.required_realm and player.realm < item.required_realm:
        #     return False, f"❌ 境界不足，需要达到 {item.required_realm}"

        # 卸下同槽位的装备
        result = await db.execute(
            select(PlayerInventory, Item)
            .join(Item, PlayerInventory.item_id == Item.id)
            .where(
                PlayerInventory.player_id == player_id,
                PlayerInventory.is_equipped == True,
                Item.equipment_slot == item.equipment_slot
            )
        )
        existing = result.first()

        if existing:
            existing_inv_item, existing_item = existing
            existing_inv_item.is_equipped = False

        # 装备新物品
        inventory_item.is_equipped = True

        await db.commit()

        return True, f"✅ 已装备 {item.name}"

    @staticmethod
    async def unequip_item(
        db: AsyncSession,
        inventory_item: PlayerInventory,
        item: Item
    ) -> Tuple[bool, str]:
        """卸下装备

        Args:
            db: 数据库会话
            inventory_item: 背包中的装备
            item: 装备物品

        Returns:
            (是否成功, 消息)
        """
        # 检查是否已装备
        if not inventory_item.is_equipped:
            return False, "❌ 该装备未装备"

        # 卸下装备
        inventory_item.is_equipped = False

        await db.commit()

        return True, f"✅ 已卸下 {item.name}"

    @staticmethod
    def format_enhancement_display(level: int) -> str:
        """格式化强化等级显示

        Args:
            level: 强化等级

        Returns:
            格式化文本
        """
        if level == 0:
            return ""
        elif level <= 5:
            return f" +{level}"
        elif level <= 10:
            return f" +{level}⭐"
        elif level <= 15:
            return f" +{level}✨"
        else:
            return f" +{level}💫"

    @staticmethod
    def format_quality_display(quality: EquipmentQuality) -> str:
        """格式化品质显示

        Args:
            quality: 装备品质

        Returns:
            格式化文本
        """
        quality_colors = {
            EquipmentQuality.COMMON: "🟦",
            EquipmentQuality.IMMORTAL: "🟪",
            EquipmentQuality.DIVINE: "🟨"
        }
        return f"{quality_colors.get(quality, '')} {quality.value}"
