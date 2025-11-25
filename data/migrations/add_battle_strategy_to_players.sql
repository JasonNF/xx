-- 为玩家表添加战斗策略字段
-- 日期: 2025-11-25
-- 说明: 添加battle_strategy字段用于存储玩家的战斗AI策略偏好

-- 添加战斗策略字段（默认为balanced平衡策略）
ALTER TABLE players ADD COLUMN battle_strategy VARCHAR(20) DEFAULT 'balanced' NOT NULL;

-- 创建索引以优化查询
CREATE INDEX IF NOT EXISTS idx_players_battle_strategy ON players(battle_strategy);

-- 注释说明
-- battle_strategy 可选值:
--   'defensive' - 保守策略：优先防御，保留40%灵力，技能使用率30%
--   'balanced' - 平衡策略：灵活应对，保留20%灵力，技能使用率60%（默认）
--   'aggressive' - 激进策略：优先进攻，保留10%灵力，技能使用率80%
