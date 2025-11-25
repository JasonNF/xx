-- 添加改名相关字段到 players 表
-- 执行时间: 2025-01-XX

-- 添加 has_renamed 字段（是否已改过名）
ALTER TABLE players ADD COLUMN has_renamed BOOLEAN NOT NULL DEFAULT 0;

-- 添加 rename_time 字段（改名时间）
ALTER TABLE players ADD COLUMN rename_time DATETIME NULL;

-- 为已存在的玩家设置默认值
UPDATE players SET has_renamed = 0 WHERE has_renamed IS NULL;

-- 创建索引（可选，如果需要查询改名记录）
CREATE INDEX IF NOT EXISTS idx_players_has_renamed ON players(has_renamed);
CREATE INDEX IF NOT EXISTS idx_players_rename_time ON players(rename_time);
