-- 修仙游戏数据库迁移脚本
-- 用于将修仙游戏表添加到PMSManageBot的data.db中

-- =====================================================
-- 1. 玩家基础表
-- =====================================================
CREATE TABLE IF NOT EXISTS xiuxian_players (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER NOT NULL UNIQUE,
    name VARCHAR(50) NOT NULL,
    realm VARCHAR(20) NOT NULL DEFAULT '凡人',
    realm_level INTEGER NOT NULL DEFAULT 0,

    -- 基础属性
    hp INTEGER NOT NULL DEFAULT 100,
    max_hp INTEGER NOT NULL DEFAULT 100,
    spiritual_power INTEGER NOT NULL DEFAULT 50,
    max_spiritual_power INTEGER NOT NULL DEFAULT 50,
    attack INTEGER NOT NULL DEFAULT 10,
    defense INTEGER NOT NULL DEFAULT 5,
    speed INTEGER NOT NULL DEFAULT 5,

    -- 修炼属性
    comprehension INTEGER NOT NULL DEFAULT 10,
    root_bone INTEGER NOT NULL DEFAULT 10,
    cultivation_exp INTEGER NOT NULL DEFAULT 0,
    cultivation_exp_required INTEGER NOT NULL DEFAULT 1000,

    -- 资源
    spirit_stones INTEGER NOT NULL DEFAULT 0,

    -- 装备槽位
    weapon_id INTEGER,
    armor_id INTEGER,
    accessory_id INTEGER,

    -- 功法与技能
    cultivation_method_id INTEGER,

    -- 宗门
    sect_id INTEGER,
    sect_position VARCHAR(20),
    sect_contribution INTEGER NOT NULL DEFAULT 0,

    -- 战斗统计
    total_battles INTEGER NOT NULL DEFAULT 0,
    battles_won INTEGER NOT NULL DEFAULT 0,
    battles_lost INTEGER NOT NULL DEFAULT 0,

    -- 修炼状态
    is_cultivating BOOLEAN NOT NULL DEFAULT 0,
    cultivation_start_time TIMESTAMP,
    cultivation_duration_hours REAL,

    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_sign_in_date DATE,
    sign_in_streak INTEGER NOT NULL DEFAULT 0,
    last_battle_time TIMESTAMP,

    FOREIGN KEY (sect_id) REFERENCES xiuxian_sects(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_xiuxian_players_telegram_id ON xiuxian_players(telegram_id);
CREATE INDEX IF NOT EXISTS idx_xiuxian_players_realm ON xiuxian_players(realm, realm_level);
CREATE INDEX IF NOT EXISTS idx_xiuxian_players_sect ON xiuxian_players(sect_id);

-- =====================================================
-- 2. 物品/装备/丹药表
-- =====================================================
CREATE TABLE IF NOT EXISTS xiuxian_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) NOT NULL,
    item_type VARCHAR(20) NOT NULL, -- WEAPON, ARMOR, ACCESSORY, PILL, MATERIAL
    grade VARCHAR(20) NOT NULL, -- COMMON, UNCOMMON, RARE, EPIC, LEGENDARY, MYTHIC
    description TEXT,
    properties TEXT, -- JSON格式存储属性
    price INTEGER NOT NULL DEFAULT 0,
    is_tradable BOOLEAN NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_xiuxian_items_type ON xiuxian_items(item_type);
CREATE INDEX IF NOT EXISTS idx_xiuxian_items_grade ON xiuxian_items(grade);

-- =====================================================
-- 3. 玩家背包表
-- =====================================================
CREATE TABLE IF NOT EXISTS xiuxian_player_inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER NOT NULL,
    item_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    enhancement_level INTEGER NOT NULL DEFAULT 0,
    obtained_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (player_id) REFERENCES xiuxian_players(id) ON DELETE CASCADE,
    FOREIGN KEY (item_id) REFERENCES xiuxian_items(id) ON DELETE CASCADE,
    UNIQUE(player_id, item_id)
);

CREATE INDEX IF NOT EXISTS idx_xiuxian_inventory_player ON xiuxian_player_inventory(player_id);

-- =====================================================
-- 4. 怪物表
-- =====================================================
CREATE TABLE IF NOT EXISTS xiuxian_monsters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) NOT NULL,
    level INTEGER NOT NULL DEFAULT 1,
    realm VARCHAR(20) NOT NULL,
    hp INTEGER NOT NULL,
    attack INTEGER NOT NULL,
    defense INTEGER NOT NULL,
    speed INTEGER NOT NULL,
    exp_reward INTEGER NOT NULL DEFAULT 100,
    spirit_stones_reward INTEGER NOT NULL DEFAULT 10,
    is_boss BOOLEAN NOT NULL DEFAULT 0,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_xiuxian_monsters_realm ON xiuxian_monsters(realm);
CREATE INDEX IF NOT EXISTS idx_xiuxian_monsters_level ON xiuxian_monsters(level);

-- =====================================================
-- 5. 战斗记录表
-- =====================================================
CREATE TABLE IF NOT EXISTS xiuxian_battle_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER NOT NULL,
    opponent_id INTEGER, -- 玩家PVP时使用
    monster_id INTEGER, -- PVE时使用
    battle_type VARCHAR(20) NOT NULL, -- PVE, PVP, BOSS, ARENA
    result VARCHAR(10) NOT NULL, -- WIN, LOSE, DRAW
    exp_gained INTEGER NOT NULL DEFAULT 0,
    spirit_stones_gained INTEGER NOT NULL DEFAULT 0,
    items_gained TEXT, -- JSON格式
    battle_log TEXT, -- 战斗日志
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (player_id) REFERENCES xiuxian_players(id) ON DELETE CASCADE,
    FOREIGN KEY (opponent_id) REFERENCES xiuxian_players(id) ON DELETE SET NULL,
    FOREIGN KEY (monster_id) REFERENCES xiuxian_monsters(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_xiuxian_battles_player ON xiuxian_battle_records(player_id);
CREATE INDEX IF NOT EXISTS idx_xiuxian_battles_time ON xiuxian_battle_records(created_at);

-- =====================================================
-- 6. 宗门表
-- =====================================================
CREATE TABLE IF NOT EXISTS xiuxian_sects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) NOT NULL UNIQUE,
    master_id INTEGER NOT NULL,
    level INTEGER NOT NULL DEFAULT 1,
    exp INTEGER NOT NULL DEFAULT 0,
    treasury INTEGER NOT NULL DEFAULT 0, -- 宗门灵石
    member_limit INTEGER NOT NULL DEFAULT 10,
    announcement TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (master_id) REFERENCES xiuxian_players(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_xiuxian_sects_master ON xiuxian_sects(master_id);

-- =====================================================
-- 7. 宗门建筑表
-- =====================================================
CREATE TABLE IF NOT EXISTS xiuxian_sect_buildings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sect_id INTEGER NOT NULL,
    building_type VARCHAR(30) NOT NULL, -- MAIN_HALL, LIBRARY, ALCHEMY_ROOM等
    level INTEGER NOT NULL DEFAULT 1,

    FOREIGN KEY (sect_id) REFERENCES xiuxian_sects(id) ON DELETE CASCADE,
    UNIQUE(sect_id, building_type)
);

-- =====================================================
-- 8. 功法表
-- =====================================================
CREATE TABLE IF NOT EXISTS xiuxian_cultivation_methods (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) NOT NULL,
    grade VARCHAR(20) NOT NULL, -- COMMON, UNCOMMON, RARE, EPIC, LEGENDARY
    description TEXT,
    speed_bonus REAL NOT NULL DEFAULT 1.0,
    hp_bonus INTEGER NOT NULL DEFAULT 0,
    attack_bonus INTEGER NOT NULL DEFAULT 0,
    defense_bonus INTEGER NOT NULL DEFAULT 0,
    requirement_realm VARCHAR(20),
    price INTEGER NOT NULL DEFAULT 1000,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- 9. 技能表
-- =====================================================
CREATE TABLE IF NOT EXISTS xiuxian_skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) NOT NULL,
    skill_type VARCHAR(20) NOT NULL, -- ATTACK, DEFENSE, HEAL, BUFF
    description TEXT,
    spiritual_power_cost INTEGER NOT NULL DEFAULT 10,
    effects TEXT, -- JSON格式
    cooldown_seconds INTEGER NOT NULL DEFAULT 0,
    requirement_realm VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- 10. 玩家技能关联表
-- =====================================================
CREATE TABLE IF NOT EXISTS xiuxian_player_skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER NOT NULL,
    skill_id INTEGER NOT NULL,
    skill_level INTEGER NOT NULL DEFAULT 1,
    learned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (player_id) REFERENCES xiuxian_players(id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES xiuxian_skills(id) ON DELETE CASCADE,
    UNIQUE(player_id, skill_id)
);

-- =====================================================
-- 11. 任务表
-- =====================================================
CREATE TABLE IF NOT EXISTS xiuxian_quests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    quest_type VARCHAR(20) NOT NULL, -- MAIN, DAILY, WEEKLY, SECT
    description TEXT,
    objectives TEXT, -- JSON格式
    rewards TEXT, -- JSON格式
    requirement_realm VARCHAR(20),
    is_repeatable BOOLEAN NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- 12. 玩家任务进度表
-- =====================================================
CREATE TABLE IF NOT EXISTS xiuxian_player_quests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER NOT NULL,
    quest_id INTEGER NOT NULL,
    progress TEXT, -- JSON格式
    status VARCHAR(20) NOT NULL DEFAULT 'IN_PROGRESS', -- IN_PROGRESS, COMPLETED, CLAIMED
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,

    FOREIGN KEY (player_id) REFERENCES xiuxian_players(id) ON DELETE CASCADE,
    FOREIGN KEY (quest_id) REFERENCES xiuxian_quests(id) ON DELETE CASCADE
);

-- =====================================================
-- 13. 市场交易表
-- =====================================================
CREATE TABLE IF NOT EXISTS xiuxian_market_listings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    seller_id INTEGER NOT NULL,
    item_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    price INTEGER NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE', -- ACTIVE, SOLD, CANCELLED
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sold_at TIMESTAMP,

    FOREIGN KEY (seller_id) REFERENCES xiuxian_players(id) ON DELETE CASCADE,
    FOREIGN KEY (item_id) REFERENCES xiuxian_items(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_xiuxian_market_status ON xiuxian_market_listings(status);

-- =====================================================
-- 14. 竞技场表
-- =====================================================
CREATE TABLE IF NOT EXISTS xiuxian_arenas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER NOT NULL UNIQUE,
    rank INTEGER NOT NULL,
    points INTEGER NOT NULL DEFAULT 1000,
    wins INTEGER NOT NULL DEFAULT 0,
    losses INTEGER NOT NULL DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (player_id) REFERENCES xiuxian_players(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_xiuxian_arena_rank ON xiuxian_arenas(rank);

-- =====================================================
-- 15. 成就表
-- =====================================================
CREATE TABLE IF NOT EXISTS xiuxian_achievements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    condition_type VARCHAR(30) NOT NULL,
    condition_value INTEGER NOT NULL,
    rewards TEXT, -- JSON格式
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- 16. 玩家成就表
-- =====================================================
CREATE TABLE IF NOT EXISTS xiuxian_player_achievements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER NOT NULL,
    achievement_id INTEGER NOT NULL,
    unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (player_id) REFERENCES xiuxian_players(id) ON DELETE CASCADE,
    FOREIGN KEY (achievement_id) REFERENCES xiuxian_achievements(id) ON DELETE CASCADE,
    UNIQUE(player_id, achievement_id)
);

-- =====================================================
-- 17. 积分兑换记录表 (已在credits_bridge_service.py中动态创建，这里确保存在)
-- =====================================================
CREATE TABLE IF NOT EXISTS xiuxian_exchange_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER NOT NULL,
    credits_amount INTEGER NOT NULL,
    spirit_stones_gained INTEGER NOT NULL,
    exchange_rate REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_xiuxian_exchange_telegram ON xiuxian_exchange_records(telegram_id);
CREATE INDEX IF NOT EXISTS idx_xiuxian_exchange_date ON xiuxian_exchange_records(DATE(created_at));

-- =====================================================
-- 完成
-- =====================================================
-- 迁移完成后，建议运行VACUUM优化数据库
-- VACUUM;
