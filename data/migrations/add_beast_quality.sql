-- 添加灵兽品质等级字段
-- 支持凡品、仙品、神品三个品质等级

-- 添加品质字段到灵兽模板表
ALTER TABLE spirit_beast_templates
ADD COLUMN quality VARCHAR(20) DEFAULT '凡品' NOT NULL;

-- 根据稀有度自动设置品质等级
-- 凡品：1-5星
UPDATE spirit_beast_templates SET quality = '凡品' WHERE rarity BETWEEN 1 AND 5;

-- 仙品：6-8星
UPDATE spirit_beast_templates SET quality = '仙品' WHERE rarity BETWEEN 6 AND 8;

-- 神品：9-10星
UPDATE spirit_beast_templates SET quality = '神品' WHERE rarity BETWEEN 9 AND 10;

-- 创建索引加速查询
CREATE INDEX IF NOT EXISTS idx_spirit_beast_quality ON spirit_beast_templates(quality);
CREATE INDEX IF NOT EXISTS idx_spirit_beast_rarity ON spirit_beast_templates(rarity);

-- 说明：
-- 品质等级决定灵兽的整体强度和获取难度
-- 凡品（🟦）: 1-5星，适合炼气期至筑基期
-- 仙品（🟪）: 6-8星，适合结丹期至元婴期
-- 神品（🟨）: 9-10星，适合化神期及以上
