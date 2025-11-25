-- 装备系统：品质、强化、套装
-- 执行日期：2025-01-XX
-- 用途：添加装备系统核心表结构和字段

-- ============================================
-- 1. 扩展物品表（items）
-- ============================================

-- 添加装备品质字段
ALTER TABLE items
ADD COLUMN quality VARCHAR(20);

-- 添加套装ID字段
ALTER TABLE items
ADD COLUMN set_id INTEGER;

-- 添加装备槽位字段
ALTER TABLE items
ADD COLUMN equipment_slot VARCHAR(20);

-- ============================================
-- 2. 扩展玩家背包表（player_inventory）
-- ============================================

-- 添加强化等级字段
ALTER TABLE player_inventory
ADD COLUMN enhancement_level INTEGER DEFAULT 0 NOT NULL;

-- ============================================
-- 3. 创建套装定义表
-- ============================================

CREATE TABLE IF NOT EXISTS equipment_sets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT NOT NULL,
    element VARCHAR(20) NOT NULL,  -- 青龙/朱雀/玄武/白虎
    set_type VARCHAR(50) NOT NULL,  -- 攻击型/防御型/平衡型/爆发型
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- ============================================
-- 4. 创建套装效果表
-- ============================================

CREATE TABLE IF NOT EXISTS equipment_set_bonuses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    set_id INTEGER NOT NULL,
    piece_count INTEGER NOT NULL,  -- 2/4/6件
    bonus_type VARCHAR(50) NOT NULL,
    -- 类型: attack_percent, defense_percent, hp_percent, crit_rate, special_skill等
    bonus_value REAL NOT NULL,
    special_effect TEXT,  -- JSON格式特殊效果
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,

    FOREIGN KEY (set_id) REFERENCES equipment_sets(id)
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_set_bonuses_set ON equipment_set_bonuses(set_id);
CREATE INDEX IF NOT EXISTS idx_set_bonuses_piece_count ON equipment_set_bonuses(set_id, piece_count);

-- ============================================
-- 5. 创建强化记录表
-- ============================================

CREATE TABLE IF NOT EXISTS enhancement_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER NOT NULL,
    inventory_id INTEGER NOT NULL,

    -- 强化信息
    from_level INTEGER NOT NULL,
    to_level INTEGER NOT NULL,
    success BOOLEAN NOT NULL,

    -- 强化成本
    cost INTEGER NOT NULL,
    used_protection BOOLEAN DEFAULT 0 NOT NULL,

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,

    FOREIGN KEY (player_id) REFERENCES players(id),
    FOREIGN KEY (inventory_id) REFERENCES player_inventory(id)
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_enhancement_records_player ON enhancement_records(player_id);
CREATE INDEX IF NOT EXISTS idx_enhancement_records_inventory ON enhancement_records(inventory_id);
CREATE INDEX IF NOT EXISTS idx_enhancement_records_date ON enhancement_records(created_at);

-- ============================================
-- 说明
-- ============================================
-- 本次迁移添加了装备系统的核心功能：
--
-- 1. 品质系统：
--    - quality 字段：凡品/仙品/神品
--    - 影响强化上限和属性倍率
--
-- 2. 强化系统：
--    - enhancement_level 记录强化等级（0-20）
--    - enhancement_records 记录强化历史
--    - 强化成功率随等级递减
--
-- 3. 套装系统：
--    - equipment_sets 定义套装
--    - equipment_set_bonuses 定义套装效果
--    - 支持2/4/6件套装效果
