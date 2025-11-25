"""灵兽系统服务层"""
import json
import random
from typing import List, Tuple, Optional, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from bot.models.spirit_beast import (
    PlayerSpiritBeast,
    SpiritBeastTemplate,
    BeastTalent,
    BeastEvolutionRecord,
    BeastFusionRecord,
    BeastQuality
)
from bot.models import Player
from bot.config.talent_config import (
    TALENT_CONFIG,
    TALENT_COUNT_BY_QUALITY,
    TALENT_WEIGHT_BY_RARITY
)


class SpiritBeastService:
    """灵兽系统服务"""

    @staticmethod
    def generate_random_talents(quality: str) -> List[Dict]:
        """根据品质生成随机天赋

        Args:
            quality: 灵兽品质（凡品/仙品/神品）

        Returns:
            天赋列表 [{"name": "暴击", "rarity": "稀有"}, ...]
        """
        # 获取天赋数量范围
        min_count, max_count = TALENT_COUNT_BY_QUALITY.get(quality, (1, 1))
        talent_count = random.randint(min_count, max_count)

        # 构建带权重的天赋池
        talent_pool = []
        for talent, config in TALENT_CONFIG.items():
            rarity = config["rarity"]
            weight = TALENT_WEIGHT_BY_RARITY.get(rarity, 10)
            talent_pool.extend([talent] * weight)

        # 随机抽取天赋（不重复）
        selected_talents = []
        available_talents = list(TALENT_CONFIG.keys())

        for _ in range(talent_count):
            if not available_talents:
                break

            # 从可用天赋中随机选择
            talent = random.choice(available_talents)
            available_talents.remove(talent)  # 移除已选择的天赋

            config = TALENT_CONFIG[talent]
            selected_talents.append({
                "name": config["name"],
                "rarity": config["rarity"].value,
                "description": config["description"],
                "icon": config["icon"]
            })

        return selected_talents

    @staticmethod
    def format_talents_display(talents_json: Optional[str]) -> str:
        """格式化天赋显示

        Args:
            talents_json: JSON格式的天赋字符串

        Returns:
            格式化的天赋显示文本
        """
        if not talents_json:
            return "无"

        try:
            talents = json.loads(talents_json)
            if not talents:
                return "无"

            result = []
            for talent in talents:
                icon = talent.get("icon", "")
                name = talent["name"]
                rarity = talent.get("rarity", "普通")

                # 根据稀有度选择颜色标记
                rarity_color = {
                    "普通": "⚪",
                    "稀有": "🔵",
                    "史诗": "🟣",
                    "传说": "🟡"
                }.get(rarity, "")

                result.append(f"{icon}{rarity_color}{name}")

            return " ".join(result)
        except (json.JSONDecodeError, KeyError):
            return "无"

    @staticmethod
    def get_talent_effects(talents_json: Optional[str]) -> Dict:
        """获取天赋效果汇总

        Args:
            talents_json: JSON格式的天赋字符串

        Returns:
            效果字典 {"attack_bonus": 0.3, "defense_bonus": 0.2, ...}
        """
        effects = {}

        if not talents_json:
            return effects

        try:
            talents = json.loads(talents_json)

            for talent in talents:
                talent_name = talent["name"]

                # 查找对应的天赋配置
                for talent_enum, config in TALENT_CONFIG.items():
                    if config["name"] == talent_name:
                        # 合并效果
                        for effect_key, effect_value in config["effects"].items():
                            if effect_key in effects:
                                # 累加数值效果
                                if isinstance(effect_value, (int, float)):
                                    effects[effect_key] += effect_value
                                else:
                                    effects[effect_key] = effect_value
                            else:
                                effects[effect_key] = effect_value
                        break

            return effects
        except (json.JSONDecodeError, KeyError):
            return effects

    @staticmethod
    async def can_evolve(
        db: AsyncSession,
        beast: PlayerSpiritBeast,
        template: SpiritBeastTemplate
    ) -> Tuple[bool, str]:
        """检查灵兽是否可以进化

        Args:
            db: 数据库会话
            beast: 玩家灵兽
            template: 灵兽模板

        Returns:
            (是否可进化, 原因说明)
        """
        # 检查是否已达到最大进化阶段
        if beast.evolution_stage >= 3:
            return False, "已达到最大进化阶段"

        # 检查等级要求
        required_level = (beast.evolution_stage + 1) * 10
        if beast.level < required_level:
            return False, f"等级不足，需要达到 Lv.{required_level}"

        # 检查亲密度要求
        required_intimacy = 60 + (beast.evolution_stage * 20)
        if beast.intimacy < required_intimacy:
            return False, f"亲密度不足，需要达到 {required_intimacy}"

        # 某些灵兽才能进化（这里简化为仙品和神品可进化）
        if template.quality == BeastQuality.COMMON.value:
            return False, "凡品灵兽无法进化"

        return True, "满足进化条件"

    @staticmethod
    async def evolve_beast(
        db: AsyncSession,
        player: Player,
        beast: PlayerSpiritBeast,
        template: SpiritBeastTemplate
    ) -> Tuple[bool, str, Optional[Dict]]:
        """进化灵兽

        Args:
            db: 数据库会话
            player: 玩家
            beast: 灵兽
            template: 灵兽模板

        Returns:
            (是否成功, 消息, 进化数据)
        """
        # 检查是否可以进化
        can_evo, reason = await SpiritBeastService.can_evolve(db, beast, template)
        if not can_evo:
            return False, f"❌ {reason}", None

        # 计算进化成本
        evolution_cost = 50000 * (beast.evolution_stage + 1)

        if player.spirit_stones < evolution_cost:
            return False, f"❌ 灵石不足，需要 {evolution_cost:,} 灵石", None

        # 扣除灵石
        player.spirit_stones -= evolution_cost

        # 提升属性（每次进化+50%基础属性）
        attack_gain = int(template.base_attack * 0.5)
        defense_gain = int(template.base_defense * 0.5)
        hp_gain = int(template.base_hp * 0.5)

        beast.attack += attack_gain
        beast.defense += defense_gain
        beast.max_hp += hp_gain
        beast.hp = beast.max_hp  # 满血

        # 提升进化阶段
        from_stage = beast.evolution_stage
        beast.evolution_stage += 1
        to_stage = beast.evolution_stage

        # 可能获得新天赋（30%概率）
        new_talent = None
        if random.random() < 0.3:
            new_talents = SpiritBeastService.generate_random_talents(template.quality)
            if new_talents:
                existing_talents = json.loads(beast.talents) if beast.talents else []
                existing_talents.extend(new_talents)
                beast.talents = json.dumps(existing_talents, ensure_ascii=False)
                new_talent = new_talents[0]

        # 记录进化
        evolution_record = BeastEvolutionRecord(
            player_id=player.id,
            beast_id=beast.id,
            from_stage=from_stage,
            to_stage=to_stage,
            beast_name=beast.nickname,
            attack_gain=attack_gain,
            defense_gain=defense_gain,
            hp_gain=hp_gain,
            spirit_stones_cost=evolution_cost
        )
        db.add(evolution_record)

        await db.commit()
        await db.refresh(beast)

        evolution_data = {
            "from_stage": from_stage,
            "to_stage": to_stage,
            "attack_gain": attack_gain,
            "defense_gain": defense_gain,
            "hp_gain": hp_gain,
            "cost": evolution_cost,
            "new_talent": new_talent
        }

        return True, "进化成功", evolution_data

    @staticmethod
    async def can_fuse(
        db: AsyncSession,
        beast1: PlayerSpiritBeast,
        beast2: PlayerSpiritBeast,
        template1: SpiritBeastTemplate,
        template2: SpiritBeastTemplate
    ) -> Tuple[bool, str]:
        """检查是否可以融合

        Args:
            db: 数据库会话
            beast1: 灵兽1
            beast2: 灵兽2
            template1: 灵兽1模板
            template2: 灵兽2模板

        Returns:
            (是否可融合, 原因说明)
        """
        # 检查是否为同一只灵兽
        if beast1.id == beast2.id:
            return False, "不能选择同一只灵兽"

        # 检查品质是否相同
        if template1.quality != template2.quality:
            return False, "只能融合相同品质的灵兽"

        # 检查等级要求
        if beast1.level < 10 or beast2.level < 10:
            return False, "两只灵兽都需要达到 Lv.10"

        # 检查亲密度要求
        if beast1.intimacy < 50 or beast2.intimacy < 50:
            return False, "两只灵兽的亲密度都需要达到 50"

        # 检查是否在训练或出战
        if beast1.is_training or beast2.is_training:
            return False, "训练中的灵兽无法融合"

        if beast1.is_active or beast2.is_active:
            return False, "出战中的灵兽无法融合"

        return True, "满足融合条件"

    @staticmethod
    async def fuse_beasts(
        db: AsyncSession,
        player: Player,
        beast1: PlayerSpiritBeast,
        beast2: PlayerSpiritBeast,
        template1: SpiritBeastTemplate,
        template2: SpiritBeastTemplate
    ) -> Tuple[bool, str, Optional[PlayerSpiritBeast]]:
        """融合两只灵兽

        Args:
            db: 数据库会话
            player: 玩家
            beast1: 灵兽1
            beast2: 灵兽2
            template1: 灵兽1模板
            template2: 灵兽2模板

        Returns:
            (是否成功, 消息, 新灵兽)
        """
        # 检查是否可以融合
        can_fus, reason = await SpiritBeastService.can_fuse(
            db, beast1, beast2, template1, template2
        )
        if not can_fus:
            return False, f"❌ {reason}", None

        # 融合成本
        fusion_cost = 50000

        if player.spirit_stones < fusion_cost:
            return False, f"❌ 灵石不足，需要 {fusion_cost:,} 灵石", None

        # 扣除灵石
        player.spirit_stones -= fusion_cost

        # 获取所有灵兽模板，随机选择一个作为融合结果
        result = await db.execute(
            select(SpiritBeastTemplate).where(
                SpiritBeastTemplate.quality == template1.quality
            )
        )
        same_quality_templates = result.scalars().all()

        if not same_quality_templates:
            return False, "❌ 没有找到合适的融合结果", None

        # 随机选择融合结果模板
        result_template = random.choice(same_quality_templates)

        # 计算融合后的属性（取较高值+10%）
        new_attack = int(max(beast1.attack, beast2.attack) * 1.1)
        new_defense = int(max(beast1.defense, beast2.defense) * 1.1)
        new_hp = int(max(beast1.max_hp, beast2.max_hp) * 1.1)
        new_speed = int(max(beast1.speed, beast2.speed) * 1.1)
        new_level = max(beast1.level, beast2.level)

        # 继承天赋（合并两只灵兽的天赋，去重）
        talents1 = json.loads(beast1.talents) if beast1.talents else []
        talents2 = json.loads(beast2.talents) if beast2.talents else []

        # 去重合并
        all_talents = talents1 + talents2
        unique_talents = []
        seen_names = set()

        for talent in all_talents:
            if talent["name"] not in seen_names:
                unique_talents.append(talent)
                seen_names.add(talent["name"])

        # 最多保留4个天赋
        if len(unique_talents) > 4:
            unique_talents = unique_talents[:4]

        # 创建新灵兽
        new_beast = PlayerSpiritBeast(
            player_id=player.id,
            template_id=result_template.id,
            nickname=f"{result_template.name}(融合)",
            level=new_level,
            attack=new_attack,
            defense=new_defense,
            hp=new_hp,
            max_hp=new_hp,
            speed=new_speed,
            intimacy=50,
            talents=json.dumps(unique_talents, ensure_ascii=False) if unique_talents else None
        )

        db.add(new_beast)
        await db.flush()  # 获取新灵兽ID

        # 记录融合
        fusion_record = BeastFusionRecord(
            player_id=player.id,
            material_beast1_id=beast1.id,
            material_beast1_name=beast1.nickname,
            material_beast1_level=beast1.level,
            material_beast2_id=beast2.id,
            material_beast2_name=beast2.nickname,
            material_beast2_level=beast2.level,
            result_beast_id=new_beast.id,
            result_beast_name=new_beast.nickname,
            inherited_talents=json.dumps(unique_talents, ensure_ascii=False) if unique_talents else None,
            spirit_stones_cost=fusion_cost
        )
        db.add(fusion_record)

        # 删除原有灵兽
        await db.delete(beast1)
        await db.delete(beast2)

        await db.commit()
        await db.refresh(new_beast)

        return True, "融合成功", new_beast
