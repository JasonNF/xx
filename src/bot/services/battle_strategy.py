"""战斗AI策略系统

提供智能技能选择和战斗决策逻辑
"""
import enum
import random
from typing import Tuple, List, Optional, Dict

from bot.models import Player, Skill, PlayerSkill


class BattleStrategy(enum.Enum):
    """战斗策略类型"""
    DEFENSIVE = "defensive"      # 保守策略 - 优先防御和保存实力
    BALANCED = "balanced"        # 平衡策略 - 根据情况灵活应对
    AGGRESSIVE = "aggressive"    # 激进策略 - 优先高伤害输出


class BattleAI:
    """战斗AI决策系统"""

    # 策略配置
    STRATEGY_CONFIG = {
        BattleStrategy.DEFENSIVE: {
            "name": "保守策略",
            "spiritual_power_reserve": 0.4,  # 保留40%灵力
            "low_hp_threshold": 0.5,         # 低于50%血量视为危险
            "prefer_defense": True,
            "skill_usage_rate": 0.3,         # 30%回合使用技能
        },
        BattleStrategy.BALANCED: {
            "name": "平衡策略",
            "spiritual_power_reserve": 0.2,  # 保留20%灵力
            "low_hp_threshold": 0.3,         # 低于30%血量视为危险
            "prefer_defense": False,
            "skill_usage_rate": 0.6,         # 60%回合使用技能
        },
        BattleStrategy.AGGRESSIVE: {
            "name": "激进策略",
            "spiritual_power_reserve": 0.1,  # 保留10%灵力
            "low_hp_threshold": 0.2,         # 低于20%血量视为危险
            "prefer_defense": False,
            "skill_usage_rate": 0.8,         # 80%回合使用技能
        }
    }

    @staticmethod
    def select_action(
        player: Player,
        available_skills: List[Tuple[PlayerSkill, Skill]],
        strategy: BattleStrategy,
        current_hp: int,
        current_sp: int,
        opponent_hp: int,
        opponent_max_hp: int,
        round_num: int
    ) -> Tuple[str, Optional[Tuple[PlayerSkill, Skill]], str]:
        """选择战斗行动

        Args:
            player: 玩家对象
            available_skills: 可用技能列表 [(PlayerSkill, Skill), ...]
            strategy: 战斗策略
            current_hp: 当前血量
            current_sp: 当前灵力
            opponent_hp: 对手当前血量
            opponent_max_hp: 对手最大血量
            round_num: 当前回合数

        Returns:
            (action_type, skill_tuple_or_none, reason)
            action_type: "skill" 或 "attack"
            skill_tuple: (PlayerSkill, Skill) 或 None
            reason: 决策原因说明
        """
        # 计算百分比
        hp_percent = current_hp / player.max_hp
        sp_percent = current_sp / player.max_spiritual_power
        opponent_hp_percent = opponent_hp / opponent_max_hp

        # 获取策略配置
        config = BattleAI.STRATEGY_CONFIG[strategy]

        # 没有可用技能，使用普通攻击
        if not available_skills:
            return "attack", None, "无可用技能"

        # 检查是否应该保留灵力
        if sp_percent < config["spiritual_power_reserve"]:
            return "attack", None, f"灵力不足{int(config['spiritual_power_reserve']*100)}%，保留实力"

        # 根据策略决定是否使用技能
        skill_usage_roll = random.random()
        if skill_usage_roll > config["skill_usage_rate"]:
            return "attack", None, "本回合选择普通攻击"

        # 评分所有技能并选择最佳
        best_skill = None
        best_score = -1
        best_reason = ""

        for player_skill, skill in available_skills:
            score, reason = BattleAI._score_skill(
                skill=skill,
                player_skill=player_skill,
                player=player,
                strategy=strategy,
                hp_percent=hp_percent,
                sp_percent=sp_percent,
                opponent_hp_percent=opponent_hp_percent,
                config=config
            )

            if score > best_score:
                best_score = score
                best_skill = (player_skill, skill)
                best_reason = reason

        # 如果没有合适的技能（评分太低），使用普通攻击
        if best_score < 30:
            return "attack", None, "技能评分过低，使用普通攻击"

        return "skill", best_skill, best_reason

    @staticmethod
    def _score_skill(
        skill: Skill,
        player_skill: PlayerSkill,
        player: Player,
        strategy: BattleStrategy,
        hp_percent: float,
        sp_percent: float,
        opponent_hp_percent: float,
        config: Dict
    ) -> Tuple[float, str]:
        """为技能打分

        Returns:
            (score, reason) - 分数0-100，原因说明
        """
        score = 0.0
        reasons = []

        # 基础分：技能伤害倍率
        damage_score = skill.damage_multiplier * 20
        score += damage_score
        reasons.append(f"基础威力{damage_score:.0f}")

        # 技能等级加成
        level_score = player_skill.skill_level * 2
        score += level_score
        reasons.append(f"等级加成{level_score:.0f}")

        # 元素匹配加成
        if skill.element and player.spirit_root:
            if skill.element in player.spirit_root.element_list:
                element_count = player.spirit_root.element_count
                if element_count == 1:
                    element_score = 25  # 天灵根完美匹配
                elif element_count == 2:
                    element_score = 15  # 双灵根
                elif element_count == 3:
                    element_score = 10  # 三灵根
                else:
                    element_score = 5   # 伪灵根

                score += element_score
                reasons.append(f"元素匹配{element_score:.0f}")

        # 灵力消耗考虑（消耗越少越好）
        sp_cost_ratio = skill.spiritual_cost / player.max_spiritual_power
        if sp_cost_ratio < 0.1:
            sp_score = 10
        elif sp_cost_ratio < 0.2:
            sp_score = 5
        elif sp_cost_ratio < 0.3:
            sp_score = 0
        else:
            sp_score = -10  # 消耗过大扣分

        score += sp_score
        if sp_score != 0:
            reasons.append(f"灵力消耗{sp_score:+.0f}")

        # 策略相关调整
        if strategy == BattleStrategy.AGGRESSIVE:
            # 激进策略：优先高伤害技能
            if skill.damage_multiplier >= 2.0:
                score += 15
                reasons.append("激进加成+15")

        elif strategy == BattleStrategy.DEFENSIVE:
            # 保守策略：当血量低时降低高消耗技能评分
            if hp_percent < config["low_hp_threshold"]:
                if sp_cost_ratio > 0.2:
                    score -= 20
                    reasons.append("血量低扣分-20")

        elif strategy == BattleStrategy.BALANCED:
            # 平衡策略：根据对手血量调整
            if opponent_hp_percent < 0.3:
                # 对手血量低，使用高伤害技能快速击败
                if skill.damage_multiplier >= 1.5:
                    score += 10
                    reasons.append("斩杀加成+10")
            elif opponent_hp_percent > 0.7:
                # 对手血量高，稳扎稳打
                if sp_cost_ratio < 0.15:
                    score += 10
                    reasons.append("持久战加成+10")

        # 特殊效果加成
        if skill.special_effects:
            try:
                import json
                effects = json.loads(skill.special_effects)
                if effects:
                    score += 5 * len(effects)
                    reasons.append(f"特效加成+{5*len(effects)}")
            except:
                pass

        reason_str = ", ".join(reasons)
        return score, reason_str

    @staticmethod
    def get_strategy_description(strategy: BattleStrategy) -> str:
        """获取策略描述"""
        config = BattleAI.STRATEGY_CONFIG.get(strategy)
        if not config:
            return "未知策略"

        return f"""**{config['name']}**

灵力保留: {int(config['spiritual_power_reserve']*100)}%
技能使用率: {int(config['skill_usage_rate']*100)}%
危险血量线: {int(config['low_hp_threshold']*100)}%

适合场景: {"防御为主，稳扎稳打" if config['prefer_defense'] else "进攻为主，快速解决战斗"}"""

    @staticmethod
    def parse_strategy_from_string(strategy_str: str) -> Optional[BattleStrategy]:
        """从字符串解析策略"""
        mapping = {
            "保守": BattleStrategy.DEFENSIVE,
            "防御": BattleStrategy.DEFENSIVE,
            "defensive": BattleStrategy.DEFENSIVE,

            "平衡": BattleStrategy.BALANCED,
            "均衡": BattleStrategy.BALANCED,
            "balanced": BattleStrategy.BALANCED,

            "激进": BattleStrategy.AGGRESSIVE,
            "进攻": BattleStrategy.AGGRESSIVE,
            "aggressive": BattleStrategy.AGGRESSIVE,
        }
        return mapping.get(strategy_str.lower())
