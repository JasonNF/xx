-- 灵兽系统扩展：天赋系统、进化系统、融合系统
-- 执行日期：2025-01-XX

-- ============================================
-- 1. 添加新字段到玩家灵兽表
-- ============================================

-- 添加天赋字段
ALTER TABLE player_spirit_beasts
ADD COLUMN talents TEXT;

-- 添加进化阶段字段
ALTER TABLE player_spirit_beasts
ADD COLUMN evolution_stage INTEGER DEFAULT 0 NOT NULL;

-- ============================================
-- 2. 创建灵兽进化记录表
-- ============================================

CREATE TABLE IF NOT EXISTS beast_evolution_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER NOT NULL,
    beast_id INTEGER NOT NULL,

    -- 进化信息
    from_stage INTEGER NOT NULL,
    to_stage INTEGER NOT NULL,
    beast_name VARCHAR(100) NOT NULL,

    -- 属性提升
    attack_gain INTEGER DEFAULT 0 NOT NULL,
    defense_gain INTEGER DEFAULT 0 NOT NULL,
    hp_gain INTEGER DEFAULT 0 NOT NULL,

    -- 进化成本
    spirit_stones_cost INTEGER NOT NULL,
    evolution_item_used VARCHAR(100),

    evolved_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,

    FOREIGN KEY (player_id) REFERENCES players(id),
    FOREIGN KEY (beast_id) REFERENCES player_spirit_beasts(id)
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_beast_evolution_player ON beast_evolution_records(player_id);
CREATE INDEX IF NOT EXISTS idx_beast_evolution_beast ON beast_evolution_records(beast_id);

-- ============================================
-- 3. 创建灵兽融合记录表
-- ============================================

CREATE TABLE IF NOT EXISTS beast_fusion_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER NOT NULL,

    -- 融合材料
    material_beast1_id INTEGER NOT NULL,
    material_beast1_name VARCHAR(100) NOT NULL,
    material_beast1_level INTEGER NOT NULL,

    material_beast2_id INTEGER NOT NULL,
    material_beast2_name VARCHAR(100) NOT NULL,
    material_beast2_level INTEGER NOT NULL,

    -- 融合结果
    result_beast_id INTEGER NOT NULL,
    result_beast_name VARCHAR(100) NOT NULL,
    inherited_talents TEXT,

    -- 融合成本
    spirit_stones_cost INTEGER NOT NULL,

    fused_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,

    FOREIGN KEY (player_id) REFERENCES players(id),
    FOREIGN KEY (result_beast_id) REFERENCES player_spirit_beasts(id)
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_beast_fusion_player ON beast_fusion_records(player_id);
CREATE INDEX IF NOT EXISTS idx_beast_fusion_result ON beast_fusion_records(result_beast_id);

-- ============================================
-- 说明
-- ============================================
-- 本次迁移添加了三个扩展系统：
--
-- 1. 天赋系统：
--    - talents 字段存储JSON格式的天赋列表
--    - 捕捉时根据品质随机生成1-3个天赋
--
-- 2. 进化系统：
--    - evolution_stage 记录进化阶段（0-3）
--    - beast_evolution_records 记录进化历史
--    - 进化需要满足等级、亲密度和灵石条件
--
-- 3. 融合系统：
--    - beast_fusion_records 记录融合历史
--    - 融合需要两只同品质灵兽
--    - 融合后继承天赋和属性
