"""数据模型包初始化"""
from .database import Base, AsyncSessionLocal, get_db, init_db, close_db
from .player import Player, RealmType, CultivationMethod, PlayerSkill, Skill, SpiritRoot, SpiritRootElement
from .item import Item, ItemType, TreasureGrade, PlayerInventory
from .sect import Sect, SectApplication, SectShopItem, SectContribution, SectWar, SectWarStatus, SectWarParticipation
from .battle import Monster, BattleRecord, BattleType, BattleResult, Arena
from .quest import Quest, PlayerQuest, QuestType, QuestStatus, Achievement, PlayerAchievement, AchievementCategory, PlayerTitle, AchievementStats
from .market import Shop, PlayerPurchase, Market, TradeRecord, Auction, AuctionBid
from .secret_realm import (
    SecretRealm, SecretRealmType, RealmDifficulty, RealmStatus,
    RealmLootPool, RealmExploration, ExplorationReward, RealmEvent
)
from .alchemy import PillRecipe, PlayerAlchemy, AlchemyRecord
from .refinery import RefineryRecipe, PlayerRefinery, RefineryRecord, ItemEnhancement
from .core_quality import PlayerCore, CoreFormationAttempt, CoreRefinementRecord, CoreQualityGrade
from .spirit_beast import SpiritBeastTemplate, PlayerSpiritBeast, BeastTrainingRecord, BeastBattleRecord, BeastType, BeastGrade
from .formation import FormationTemplate, PlayerFormation, ActiveFormation, FormationBreakRecord, FormationTrainingRecord, FormationType, FormationGrade
from .talisman import TalismanRecipe, PlayerTalismanSkill, PlayerTalisman, TalismanCraftRecord, TalismanUsageRecord, TalismanType, TalismanGrade
from .cave_dwelling import CaveDwelling, CaveRoom, SpiritField, CaveUpgradeRecord, CaveVisitRecord, CaveDwellingGrade, CaveRoomType
from .adventure import AdventureTemplate, PlayerAdventure, AdventureExploration, LuckEvent, AdventureCooldown, AdventureType, AdventureRarity
from .world_boss import WorldBoss, WorldBossParticipation, WorldBossTemplate, WorldBossStatus
from .credit_shop import (
    CreditType, CreditShopCategory, CreditShopItem, PlayerCreditRecord,
    CreditShopPurchase, PlayerCreditShopLimit
)

__all__ = [
    # Database
    "Base",
    "AsyncSessionLocal",
    "get_db",
    "init_db",
    "close_db",
    # Player
    "Player",
    "RealmType",
    "CultivationMethod",
    "PlayerSkill",
    "Skill",
    "SpiritRoot",
    "SpiritRootElement",
    # Item
    "Item",
    "ItemType",
    "TreasureGrade",
    "PlayerInventory",
    # Sect
    "Sect",
    "SectApplication",
    "SectShopItem",
    "SectContribution",
    "SectWar",
    "SectWarStatus",
    "SectWarParticipation",
    # Battle
    "Monster",
    "BattleRecord",
    "BattleType",
    "BattleResult",
    "Arena",
    # Quest
    "Quest",
    "PlayerQuest",
    "QuestType",
    "QuestStatus",
    "Achievement",
    "PlayerAchievement",
    "AchievementCategory",
    "PlayerTitle",
    "AchievementStats",
    # Market
    "Shop",
    "PlayerPurchase",
    "Market",
    "TradeRecord",
    "Auction",
    "AuctionBid",
    # Secret Realm
    "SecretRealm",
    "SecretRealmType",
    "RealmDifficulty",
    "RealmStatus",
    "RealmLootPool",
    "RealmExploration",
    "ExplorationReward",
    "RealmEvent",
    # Alchemy
    "PillRecipe",
    "PlayerAlchemy",
    "AlchemyRecord",
    # Refinery
    "RefineryRecipe",
    "PlayerRefinery",
    "RefineryRecord",
    "ItemEnhancement",
    # Core Quality
    "PlayerCore",
    "CoreFormationAttempt",
    "CoreRefinementRecord",
    "CoreQualityGrade",
    # Spirit Beast
    "SpiritBeastTemplate",
    "PlayerSpiritBeast",
    "BeastTrainingRecord",
    "BeastBattleRecord",
    "BeastType",
    "BeastGrade",
    # Formation
    "FormationTemplate",
    "PlayerFormation",
    "ActiveFormation",
    "FormationBreakRecord",
    "FormationTrainingRecord",
    "FormationType",
    "FormationGrade",
    # Talisman
    "TalismanRecipe",
    "PlayerTalismanSkill",
    "PlayerTalisman",
    "TalismanCraftRecord",
    "TalismanUsageRecord",
    "TalismanType",
    "TalismanGrade",
    # Cave Dwelling
    "CaveDwelling",
    "CaveRoom",
    "SpiritField",
    "CaveUpgradeRecord",
    "CaveVisitRecord",
    "CaveDwellingGrade",
    "CaveRoomType",
    # Adventure
    "AdventureTemplate",
    "PlayerAdventure",
    "AdventureExploration",
    "LuckEvent",
    "AdventureCooldown",
    "AdventureType",
    "AdventureRarity",
    # World Boss
    "WorldBoss",
    "WorldBossParticipation",
    "WorldBossTemplate",
    "WorldBossStatus",
    # Credit Shop
    "CreditType",
    "CreditShopCategory",
    "CreditShopItem",
    "PlayerCreditRecord",
    "CreditShopPurchase",
    "PlayerCreditShopLimit",
]
