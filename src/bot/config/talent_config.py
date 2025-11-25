"""灵兽天赋配置"""
from bot.models.spirit_beast import BeastTalent, TalentRarity

# 天赋详细配置
TALENT_CONFIG = {
    # 攻击系天赋
    BeastTalent.CRITICAL_STRIKE: {
        "name": "暴击",
        "description": "增加15%暴击率，暴击伤害+50%",
        "rarity": TalentRarity.RARE,
        "icon": "💥",
        "effects": {
            "crit_rate": 0.15,
            "crit_damage": 0.50
        }
    },
    BeastTalent.ARMOR_PIERCE: {
        "name": "破甲",
        "description": "攻击无视敌人30%防御",
        "rarity": TalentRarity.RARE,
        "icon": "🗡️",
        "effects": {
            "armor_pierce": 0.30
        }
    },
    BeastTalent.COMBO_ATTACK: {
        "name": "连击",
        "description": "20%概率连续攻击2次",
        "rarity": TalentRarity.EPIC,
        "icon": "⚔️",
        "effects": {
            "combo_chance": 0.20,
            "combo_hits": 2
        }
    },
    BeastTalent.LIFE_STEAL: {
        "name": "吸血",
        "description": "攻击回复造成伤害20%的生命值",
        "rarity": TalentRarity.RARE,
        "icon": "🩸",
        "effects": {
            "life_steal": 0.20
        }
    },
    BeastTalent.FURY: {
        "name": "狂怒",
        "description": "生命值低于50%时攻击力+40%",
        "rarity": TalentRarity.EPIC,
        "icon": "😡",
        "effects": {
            "fury_threshold": 0.50,
            "fury_bonus": 0.40
        }
    },

    # 防御系天赋
    BeastTalent.BLOCK: {
        "name": "格挡",
        "description": "减少受到伤害的25%",
        "rarity": TalentRarity.COMMON,
        "icon": "🛡️",
        "effects": {
            "block_rate": 0.25
        }
    },
    BeastTalent.COUNTER: {
        "name": "反伤",
        "description": "反弹受到伤害的30%",
        "rarity": TalentRarity.RARE,
        "icon": "⚡",
        "effects": {
            "counter_damage": 0.30
        }
    },
    BeastTalent.SHIELD: {
        "name": "护盾",
        "description": "受到致命伤害时触发护盾，免疫并恢复30%生命值（冷却3回合）",
        "rarity": TalentRarity.EPIC,
        "icon": "🔰",
        "effects": {
            "shield_heal": 0.30,
            "cooldown": 3
        }
    },
    BeastTalent.REGENERATION: {
        "name": "回复",
        "description": "每回合恢复5%生命值",
        "rarity": TalentRarity.COMMON,
        "icon": "💚",
        "effects": {
            "regen_rate": 0.05
        }
    },
    BeastTalent.IRON_SKIN: {
        "name": "铁皮",
        "description": "防御力+30%",
        "rarity": TalentRarity.COMMON,
        "icon": "🔩",
        "effects": {
            "defense_bonus": 0.30
        }
    },

    # 速度系天赋
    BeastTalent.FIRST_STRIKE: {
        "name": "先攻",
        "description": "战斗开始时必定先手",
        "rarity": TalentRarity.RARE,
        "icon": "⚡",
        "effects": {
            "first_strike": True
        }
    },
    BeastTalent.DODGE: {
        "name": "闪避",
        "description": "25%概率闪避攻击",
        "rarity": TalentRarity.RARE,
        "icon": "💨",
        "effects": {
            "dodge_rate": 0.25
        }
    },
    BeastTalent.PURSUIT: {
        "name": "追击",
        "description": "击败敌人后可额外攻击一次",
        "rarity": TalentRarity.EPIC,
        "icon": "🏃",
        "effects": {
            "pursuit": True
        }
    },
    BeastTalent.SWIFT: {
        "name": "迅捷",
        "description": "速度+50%",
        "rarity": TalentRarity.RARE,
        "icon": "💫",
        "effects": {
            "speed_bonus": 0.50
        }
    },

    # 特殊系天赋
    BeastTalent.SPIRIT_RESONANCE: {
        "name": "灵气共鸣",
        "description": "主人修炼速度+15%",
        "rarity": TalentRarity.LEGENDARY,
        "icon": "🔮",
        "effects": {
            "cultivation_bonus": 0.15
        }
    },
    BeastTalent.ELEMENT_MASTERY: {
        "name": "元素精通",
        "description": "元素伤害+40%",
        "rarity": TalentRarity.EPIC,
        "icon": "🌟",
        "effects": {
            "element_bonus": 0.40
        }
    },
    BeastTalent.BATTLE_SPIRIT: {
        "name": "战意",
        "description": "每次战斗获得+5%攻击力，最多叠加10层",
        "rarity": TalentRarity.EPIC,
        "icon": "🔥",
        "effects": {
            "battle_bonus": 0.05,
            "max_stacks": 10
        }
    },
    BeastTalent.FORTUNE: {
        "name": "幸运",
        "description": "提升10%捕捉成功率和掉落概率",
        "rarity": TalentRarity.LEGENDARY,
        "icon": "🍀",
        "effects": {
            "luck_bonus": 0.10
        }
    },
    BeastTalent.WISDOM: {
        "name": "睿智",
        "description": "经验获取+30%",
        "rarity": TalentRarity.RARE,
        "icon": "📚",
        "effects": {
            "exp_bonus": 0.30
        }
    },
}


# 根据品质获取可随机的天赋数量
TALENT_COUNT_BY_QUALITY = {
    "凡品": (1, 1),     # 1个天赋
    "仙品": (1, 2),     # 1-2个天赋
    "神品": (2, 3),     # 2-3个天赋
}

# 根据稀有度获取天赋权重
TALENT_WEIGHT_BY_RARITY = {
    TalentRarity.COMMON: 50,      # 普通天赋权重
    TalentRarity.RARE: 30,        # 稀有天赋权重
    TalentRarity.EPIC: 15,        # 史诗天赋权重
    TalentRarity.LEGENDARY: 5,    # 传说天赋权重
}
