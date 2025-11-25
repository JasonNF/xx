-- 初始化四象套装数据
-- 执行日期：2025-01-XX
-- 用途：创建青龙、朱雀、玄武、白虎四大套装及其装备

-- ============================================
-- 清理旧数据（如果重新初始化）
-- ============================================

-- DELETE FROM equipment_set_bonuses;
-- DELETE FROM equipment_sets;
-- DELETE FROM items WHERE set_id IS NOT NULL;

-- ============================================
-- 1. 创建四象套装定义
-- ============================================

-- 青龙套装（攻击型）
INSERT INTO equipment_sets (id, name, description, element, set_type)
VALUES (1, '青龙套装', '传说中东方青龙之力凝聚的套装，主攻击与速度', '木', '攻击型');

-- 朱雀套装（爆发型）
INSERT INTO equipment_sets (id, name, description, element, set_type)
VALUES (2, '朱雀套装', '传说中南方朱雀之力凝聚的套装，主爆发与灵力', '火', '爆发型');

-- 玄武套装（防御型）
INSERT INTO equipment_sets (id, name, description, element, set_type)
VALUES (3, '玄武套装', '传说中北方玄武之力凝聚的套装，主防御与生命', '水', '防御型');

-- 白虎套装（平衡型）
INSERT INTO equipment_sets (id, name, description, element, set_type)
VALUES (4, '白虎套装', '传说中西方白虎之力凝聚的套装，主全面平衡', '金', '平衡型');

-- ============================================
-- 2. 创建套装效果
-- ============================================

-- 青龙套装效果
INSERT INTO equipment_set_bonuses (set_id, piece_count, bonus_type, bonus_value, special_effect)
VALUES
(1, 2, 'attack_percent', 0.10, '{"desc": "攻击力+10%"}'),
(1, 2, 'speed_percent', 0.05, '{"desc": "速度+5%"}'),
(1, 4, 'crit_rate', 0.15, '{"desc": "暴击率+15%"}'),
(1, 4, 'combo_chance', 0.10, '{"desc": "连击概率+10%"}'),
(1, 6, 'attack_percent', 0.20, '{"desc": "攻击力+20%"}'),
(1, 6, 'special_skill', 1, '{"name": "青龙啸", "desc": "释放青龙啸，对敌人造成300%伤害"}');

-- 朱雀套装效果
INSERT INTO equipment_set_bonuses (set_id, piece_count, bonus_type, bonus_value, special_effect)
VALUES
(2, 2, 'attack_percent', 0.15, '{"desc": "攻击力+15%"}'),
(2, 4, 'crit_damage', 0.30, '{"desc": "暴击伤害+30%"}'),
(2, 4, 'spiritual_percent', 0.10, '{"desc": "灵力上限+10%"}'),
(2, 6, 'attack_percent', 0.25, '{"desc": "攻击力+25%"}'),
(2, 6, 'special_skill', 1, '{"name": "朱雀炎", "desc": "释放朱雀真火，灼烧敌人5回合"}');

-- 玄武套装效果
INSERT INTO equipment_set_bonuses (set_id, piece_count, bonus_type, bonus_value, special_effect)
VALUES
(3, 2, 'defense_percent', 0.15, '{"desc": "防御力+15%"}'),
(3, 2, 'hp_percent', 0.10, '{"desc": "生命值+10%"}'),
(3, 4, 'damage_reduction', 0.20, '{"desc": "受到伤害-20%"}'),
(3, 4, 'hp_regen', 0.05, '{"desc": "每回合恢复5%生命"}'),
(3, 6, 'defense_percent', 0.30, '{"desc": "防御力+30%"}'),
(3, 6, 'special_skill', 1, '{"name": "玄武护", "desc": "生成护盾，吸收50%最大生命值伤害"}');

-- 白虎套装效果
INSERT INTO equipment_set_bonuses (set_id, piece_count, bonus_type, bonus_value, special_effect)
VALUES
(4, 2, 'attack_percent', 0.08, '{"desc": "攻击力+8%"}'),
(4, 2, 'defense_percent', 0.08, '{"desc": "防御力+8%"}'),
(4, 4, 'all_attributes', 0.10, '{"desc": "全属性+10%"}'),
(4, 6, 'all_attributes', 0.15, '{"desc": "全属性+15%"}'),
(4, 6, 'special_skill', 1, '{"name": "白虎杀", "desc": "释放白虎杀气，大幅提升下次攻击伤害"}');

-- ============================================
-- 3. 创建套装装备（青龙套装 - 仙品）
-- ============================================

INSERT INTO items (name, description, item_type, quality, set_id, equipment_slot,
                   attack_bonus, defense_bonus, hp_bonus, spiritual_bonus, speed_bonus,
                   buy_price, sell_price, required_level)
VALUES
('青龙战剑', '青龙之力凝聚的神兵利器，剑身缠绕青色灵气', '武器', '仙品', 1, '武器',
 120, 20, 100, 80, 30, 100000, 50000, 30),

('青龙战盔', '青龙鳞片锻造的头盔，坚固且轻盈', '护甲', '仙品', 1, '头盔',
 40, 80, 200, 50, 20, 80000, 40000, 30),

('青龙战甲', '青龙皮革制成的战甲，防御力惊人', '护甲', '仙品', 1, '胸甲',
 50, 100, 300, 60, 15, 120000, 60000, 30),

('青龙护腿', '青龙筋腱编织的护腿，提供优秀防护', '护甲', '仙品', 1, '护腿',
 30, 70, 150, 40, 25, 70000, 35000, 30),

('青龙战靴', '青龙羽翼加持的靴子，移动如风', '护甲', '仙品', 1, '靴子',
 20, 50, 100, 30, 50, 60000, 30000, 30),

('青龙玉佩', '蕴含青龙精魄的玉佩，大幅提升灵力', '饰品', '仙品', 1, '饰品',
 60, 40, 150, 100, 15, 90000, 45000, 30);

-- ============================================
-- 4. 创建套装装备（朱雀套装 - 神品）
-- ============================================

INSERT INTO items (name, description, item_type, quality, set_id, equipment_slot,
                   attack_bonus, defense_bonus, hp_bonus, spiritual_bonus, speed_bonus,
                   buy_price, sell_price, required_level)
VALUES
('朱雀焚天剑', '朱雀真火淬炼的神剑，挥舞间烈焰滔天', '武器', '神品', 2, '武器',
 180, 30, 150, 120, 40, 200000, 100000, 50),

('朱雀烈焰盔', '朱雀羽毛编织的头盔，炽热却不灼伤', '护甲', '神品', 2, '头盔',
 60, 120, 300, 80, 30, 160000, 80000, 50),

('朱雀火羽甲', '朱雀翎羽制成的战甲，轻盈且坚固', '护甲', '神品', 2, '胸甲',
 70, 150, 450, 90, 25, 240000, 120000, 50),

('朱雀炎腿', '朱雀火焰包裹的护腿，提供极强防护', '护甲', '神品', 2, '护腿',
 50, 110, 250, 60, 35, 140000, 70000, 50),

('朱雀灵靴', '朱雀神速加持的靴子，健步如飞', '护甲', '神品', 2, '靴子',
 40, 80, 180, 50, 70, 120000, 60000, 50),

('朱雀炎珠', '封印朱雀火种的宝珠，灵力无穷', '饰品', '神品', 2, '饰品',
 90, 60, 200, 150, 20, 180000, 90000, 50);

-- ============================================
-- 5. 创建套装装备（玄武套装 - 神品）
-- ============================================

INSERT INTO items (name, description, item_type, quality, set_id, equipment_slot,
                   attack_bonus, defense_bonus, hp_bonus, spiritual_bonus, speed_bonus,
                   buy_price, sell_price, required_level)
VALUES
('玄武镇海刀', '玄武之力镇压的重刀，厚重如山', '武器', '神品', 3, '武器',
 140, 60, 200, 100, 20, 200000, 100000, 50),

('玄武铁盔', '玄武甲壳铸造的头盔，坚不可摧', '护甲', '神品', 3, '头盔',
 50, 180, 500, 70, 10, 160000, 80000, 50),

('玄武重甲', '玄武龟甲锻造的重甲，防御无双', '护甲', '神品', 3, '胸甲',
 60, 220, 700, 80, 5, 240000, 120000, 50),

('玄武护腿', '玄武精铁制成的护腿，厚实牢固', '护甲', '神品', 3, '护腿',
 40, 160, 450, 50, 15, 140000, 70000, 50),

('玄武战靴', '玄武加持的重靴，稳重如山', '护甲', '神品', 3, '靴子',
 30, 140, 350, 40, 20, 120000, 60000, 50),

('玄武龟印', '玄武印记的宝印，生命力旺盛', '饰品', '神品', 3, '饰品',
 70, 100, 400, 120, 10, 180000, 90000, 50);

-- ============================================
-- 6. 创建套装装备（白虎套装 - 仙品）
-- ============================================

INSERT INTO items (name, description, item_type, quality, set_id, equipment_slot,
                   attack_bonus, defense_bonus, hp_bonus, spiritual_bonus, speed_bonus,
                   buy_price, sell_price, required_level)
VALUES
('白虎斩魂剑', '白虎杀气凝聚的利剑，锋利无比', '武器', '仙品', 4, '武器',
 110, 40, 120, 90, 35, 100000, 50000, 30),

('白虎战盔', '白虎之骨锻造的头盔，攻防兼备', '护甲', '仙品', 4, '头盔',
 45, 90, 220, 60, 25, 80000, 40000, 30),

('白虎战甲', '白虎之皮制成的战甲，平衡优秀', '护甲', '仙品', 4, '胸甲',
 55, 110, 330, 70, 20, 120000, 60000, 30),

('白虎护腿', '白虎精钢编织的护腿，坚固灵活', '护甲', '仙品', 4, '护腿',
 35, 80, 180, 50, 30, 70000, 35000, 30),

('白虎战靴', '白虎速度加持的靴子，快如闪电', '护甲', '仙品', 4, '靴子',
 25, 60, 130, 40, 45, 60000, 30000, 30),

('白虎令', '白虎权威的象征，全属性提升', '饰品', '仙品', 4, '饰品',
 65, 50, 170, 110, 20, 90000, 45000, 30);

-- ============================================
-- 验证数据
-- ============================================

-- 查看套装
-- SELECT * FROM equipment_sets;

-- 查看套装效果
-- SELECT es.name, esb.piece_count, esb.bonus_type, esb.bonus_value
-- FROM equipment_set_bonuses esb
-- JOIN equipment_sets es ON esb.set_id = es.id
-- ORDER BY es.id, esb.piece_count;

-- 查看套装装备
-- SELECT i.name, i.quality, es.name AS set_name, i.equipment_slot,
--        i.attack_bonus, i.defense_bonus, i.hp_bonus
-- FROM items i
-- JOIN equipment_sets es ON i.set_id = es.id
-- ORDER BY es.id, i.equipment_slot;

-- ============================================
-- 说明
-- ============================================
-- 本脚本初始化了四象套装系统：
--
-- 1. 四大套装：
--    - 青龙套装：攻击型（仙品）
--    - 朱雀套装：爆发型（神品）
--    - 玄武套装：防御型（神品）
--    - 白虎套装：平衡型（仙品）
--
-- 2. 每个套装包含6件装备：
--    - 武器、头盔、胸甲、护腿、靴子、饰品
--
-- 3. 套装效果：
--    - 2件套：基础属性加成
--    - 4件套：进阶效果加成
--    - 6件套：特殊技能加成
