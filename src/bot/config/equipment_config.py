"""装备系统配置"""
from typing import Dict, Tuple

# ============================================
# 强化系统配置
# ============================================

def get_enhancement_success_rate(level: int) -> float:
    """获取强化成功率

    强化等级 → 成功率:
    +0 → +5:   100% (必成功)
    +5 → +10:  90% → 60% (每级-6%)
    +10 → +15: 50% → 30% (每级-4%)
    +15 → +20: 25% → 15% (每级-2%)

    Args:
        level: 当前强化等级

    Returns:
        成功率 (0.0-1.0)
    """
    if level < 5:
        return 1.0
    elif level < 10:
        return 0.90 - (level - 5) * 0.06
    elif level < 15:
        return 0.50 - (level - 10) * 0.04
    else:  # 15-19
        return max(0.15, 0.25 - (level - 15) * 0.02)


# 强化消耗品质系数
QUALITY_COST_MULTIPLIER = {
    "凡品": 1.0,
    "仙品": 1.5,
    "神品": 2.0
}


def calculate_enhancement_cost(level: int, quality: str) -> int:
    """计算强化消耗（灵石）

    基础消耗 = 1000 * (等级 + 1) * 品质系数

    示例:
    - 凡品 +0→+1: 1,000灵石
    - 凡品 +9→+10: 10,000灵石
    - 神品 +19→+20: 40,000灵石

    Args:
        level: 当前强化等级
        quality: 装备品质（凡品/仙品/神品）

    Returns:
        强化消耗的灵石数量
    """
    base_cost = 1000 * (level + 1)
    multiplier = QUALITY_COST_MULTIPLIER.get(quality, 1.0)
    return int(base_cost * multiplier)


def get_enhancement_penalty(level: int) -> int:
    """获取强化失败惩罚

    失败惩罚规则:
    +0 → +10:  失败不掉级 (0)
    +11 → +15: 失败-1级
    +16 → +20: 失败-2级

    Args:
        level: 当前强化等级

    Returns:
        失败后的等级变化（负数表示下降）
    """
    if level <= 10:
        return 0
    elif level <= 15:
        return -1
    else:
        return -2


# 强化等级上限（按品质）
ENHANCEMENT_MAX_LEVEL = {
    "凡品": 10,
    "仙品": 15,
    "神品": 20
}

# 每级强化属性加成百分比
ENHANCEMENT_ATTRIBUTE_BONUS_PER_LEVEL = 0.05  # 每级+5%基础属性

# 品质属性倍率
QUALITY_ATTRIBUTE_MULTIPLIER = {
    "凡品": 1.0,
    "仙品": 1.5,
    "神品": 2.0
}


# ============================================
# 套装系统配置
# ============================================

# 四象套装完整配置
EQUIPMENT_SETS_CONFIG = {
    "青龙": {
        "name": "青龙套装",
        "description": "传说中东方青龙之力凝聚的套装，主攻击与速度",
        "element": "木",
        "type": "攻击型",
        "pieces": ["青龙战剑", "青龙战盔", "青龙战甲", "青龙护腿", "青龙战靴", "青龙玉佩"],
        "bonuses": {
            2: [
                {"type": "attack_percent", "value": 0.10, "desc": "攻击力+10%"},
                {"type": "speed_percent", "value": 0.05, "desc": "速度+5%"}
            ],
            4: [
                {"type": "crit_rate", "value": 0.15, "desc": "暴击率+15%"},
                {"type": "combo_chance", "value": 0.10, "desc": "连击概率+10%"}
            ],
            6: [
                {"type": "attack_percent", "value": 0.20, "desc": "攻击力+20%"},
                {"type": "special_skill", "value": "青龙啸", "desc": "释放青龙啸，对敌人造成300%伤害"}
            ]
        }
    },
    "朱雀": {
        "name": "朱雀套装",
        "description": "传说中南方朱雀之力凝聚的套装，主爆发与灵力",
        "element": "火",
        "type": "爆发型",
        "pieces": ["朱雀焚天剑", "朱雀烈焰盔", "朱雀火羽甲", "朱雀炎腿", "朱雀灵靴", "朱雀炎珠"],
        "bonuses": {
            2: [
                {"type": "attack_percent", "value": 0.15, "desc": "攻击力+15%"}
            ],
            4: [
                {"type": "crit_damage", "value": 0.30, "desc": "暴击伤害+30%"},
                {"type": "spiritual_percent", "value": 0.10, "desc": "灵力上限+10%"}
            ],
            6: [
                {"type": "attack_percent", "value": 0.25, "desc": "攻击力+25%"},
                {"type": "special_skill", "value": "朱雀炎", "desc": "释放朱雀真火，灼烧敌人5回合"}
            ]
        }
    },
    "玄武": {
        "name": "玄武套装",
        "description": "传说中北方玄武之力凝聚的套装，主防御与生命",
        "element": "水",
        "type": "防御型",
        "pieces": ["玄武镇海刀", "玄武铁盔", "玄武重甲", "玄武护腿", "玄武战靴", "玄武龟印"],
        "bonuses": {
            2: [
                {"type": "defense_percent", "value": 0.15, "desc": "防御力+15%"},
                {"type": "hp_percent", "value": 0.10, "desc": "生命值+10%"}
            ],
            4: [
                {"type": "damage_reduction", "value": 0.20, "desc": "受到伤害-20%"},
                {"type": "hp_regen", "value": 0.05, "desc": "每回合恢复5%生命"}
            ],
            6: [
                {"type": "defense_percent", "value": 0.30, "desc": "防御力+30%"},
                {"type": "special_skill", "value": "玄武护", "desc": "生成护盾，吸收50%最大生命值伤害"}
            ]
        }
    },
    "白虎": {
        "name": "白虎套装",
        "description": "传说中西方白虎之力凝聚的套装，主全面平衡",
        "element": "金",
        "type": "平衡型",
        "pieces": ["白虎斩魂剑", "白虎战盔", "白虎战甲", "白虎护腿", "白虎战靴", "白虎令"],
        "bonuses": {
            2: [
                {"type": "attack_percent", "value": 0.08, "desc": "攻击力+8%"},
                {"type": "defense_percent", "value": 0.08, "desc": "防御力+8%"}
            ],
            4: [
                {"type": "all_attributes", "value": 0.10, "desc": "全属性+10%"}
            ],
            6: [
                {"type": "all_attributes", "value": 0.15, "desc": "全属性+15%"},
                {"type": "special_skill", "value": "白虎杀", "desc": "释放白虎杀气，大幅提升下次攻击伤害"}
            ]
        }
    }
}


# ============================================
# 辅助函数
# ============================================

def get_quality_max_enhancement(quality: str) -> int:
    """获取品质对应的最大强化等级

    Args:
        quality: 装备品质

    Returns:
        最大强化等级
    """
    return ENHANCEMENT_MAX_LEVEL.get(quality, 10)


def get_quality_multiplier(quality: str) -> float:
    """获取品质属性倍率

    Args:
        quality: 装备品质

    Returns:
        属性倍率
    """
    return QUALITY_ATTRIBUTE_MULTIPLIER.get(quality, 1.0)


def format_bonus_description(bonus_type: str, bonus_value: float) -> str:
    """格式化套装加成描述

    Args:
        bonus_type: 加成类型
        bonus_value: 加成数值

    Returns:
        格式化后的描述文本
    """
    bonus_map = {
        "attack_percent": f"攻击力+{bonus_value * 100:.0f}%",
        "defense_percent": f"防御力+{bonus_value * 100:.0f}%",
        "hp_percent": f"生命值+{bonus_value * 100:.0f}%",
        "speed_percent": f"速度+{bonus_value * 100:.0f}%",
        "spiritual_percent": f"灵力+{bonus_value * 100:.0f}%",
        "crit_rate": f"暴击率+{bonus_value * 100:.0f}%",
        "crit_damage": f"暴击伤害+{bonus_value * 100:.0f}%",
        "damage_reduction": f"受到伤害-{bonus_value * 100:.0f}%",
        "hp_regen": f"每回合恢复{bonus_value * 100:.0f}%生命",
        "combo_chance": f"连击概率+{bonus_value * 100:.0f}%",
        "all_attributes": f"全属性+{bonus_value * 100:.0f}%",
    }
    return bonus_map.get(bonus_type, f"{bonus_type}: {bonus_value}")
