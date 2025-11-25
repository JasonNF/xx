-- 物品和装备初始数据
-- 总计: 230+ 项物品
-- 分类: 丹药(50)、材料(80)、武器(40)、防具(30)、饰品(20)、宝物(10+)

-- ============================================
-- 丹药类 (50个)
-- ============================================

-- 炼气期丹药 (15个)
INSERT INTO items (name, description, item_type, treasure_grade, is_tradable, is_stackable, max_stack, buy_price, sell_price, required_realm, required_level, attack_bonus, defense_bonus, hp_bonus, spiritual_bonus, speed_bonus, special_ability, hp_restore, spiritual_restore, exp_bonus, breakthrough_bonus, herb_age, created_at) VALUES
('聚气丹', '炼气期基础丹药，恢复100灵力', 'pill', NULL, 1, 1, 99, 100, 50, '凡人', 0, 0, 0, 0, 0, 0, NULL, 0, 100, 0, 0.0, 0, datetime('now')),
('回春丹', '基础治疗丹药，恢复200生命', 'pill', NULL, 1, 1, 99, 150, 75, '凡人', 0, 0, 0, 0, 0, 0, NULL, 200, 0, 0, 0.0, 0, datetime('now')),
('凝神丹', '炼气期修炼丹药，增加500修为', 'pill', NULL, 1, 1, 50, 200, 100, '炼气期', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 500, 0.0, 0, datetime('now')),
('辟谷丹', '代替食物的丹药，7天不饥', 'pill', NULL, 1, 1, 30, 80, 40, '凡人', 0, 0, 0, 0, 0, 0, '{"duration_days": 7}', 0, 0, 0, 0.0, 0, datetime('now')),
('解毒丹', '解除毒素效果', 'pill', NULL, 1, 1, 50, 120, 60, '凡人', 0, 0, 0, 0, 0, 0, '{"remove_poison": true}', 50, 0, 0, 0.0, 0, datetime('now')),
('培元丹', '炼气期中级丹药，恢复300灵力', 'pill', NULL, 1, 1, 99, 300, 150, '炼气期', 3, 0, 0, 0, 0, 0, NULL, 0, 300, 0, 0.0, 0, datetime('now')),
('养气丹', '炼气期修炼丹药，增加1000修为', 'pill', NULL, 1, 1, 50, 500, 250, '炼气期', 5, 0, 0, 0, 0, 0, NULL, 0, 0, 1000, 0.0, 0, datetime('now')),
('炼气丹', '炼气期高级修炼丹药，增加2000修为', 'pill', NULL, 1, 1, 30, 1000, 500, '炼气期', 8, 0, 0, 0, 0, 0, NULL, 0, 0, 2000, 0.0, 0, datetime('now')),
('破障丹', '增加5%突破成功率', 'pill', '下品', 1, 1, 10, 2000, 1000, '炼气期', 10, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.05, 0, datetime('now')),
('小还丹', '恢复500生命和500灵力', 'pill', '中品', 1, 1, 50, 800, 400, '炼气期', 5, 0, 0, 0, 0, 0, NULL, 500, 500, 0, 0.0, 0, datetime('now')),
('增寿丹', '增加1年寿命', 'pill', '中品', 1, 1, 20, 5000, 2500, '炼气期', 0, 0, 0, 0, 0, 0, '{"lifespan_increase": 365}', 0, 0, 0, 0.0, 0, datetime('now')),
('养魂丹', '滋养神魂，恢复神识', 'pill', '中品', 1, 1, 30, 1200, 600, '炼气期', 5, 0, 0, 0, 0, 0, '{"divine_sense_restore": 50}', 0, 0, 0, 0.0, 0, datetime('now')),
('金创药', '疗伤圣药，恢复800生命', 'pill', NULL, 1, 1, 99, 600, 300, '炼气期', 0, 0, 0, 0, 0, 0, NULL, 800, 0, 0, 0.0, 0, datetime('now')),
('化瘀丹', '治疗内伤，恢复500生命', 'pill', NULL, 1, 1, 50, 400, 200, '炼气期', 0, 0, 0, 0, 0, 0, '{"cure_internal_injury": true}', 500, 0, 0, 0.0, 0, datetime('now')),
('清心丹', '清心明志，抵抗心魔', 'pill', '中品', 1, 1, 20, 1500, 750, '炼气期', 8, 0, 0, 0, 0, 0, '{"resist_inner_demon": 0.3}', 0, 0, 0, 0.0, 0, datetime('now'));

-- 筑基期丹药 (15个)
INSERT INTO items (name, description, item_type, treasure_grade, is_tradable, is_stackable, max_stack, buy_price, sell_price, required_realm, required_level, attack_bonus, defense_bonus, hp_bonus, spiritual_bonus, speed_bonus, special_ability, hp_restore, spiritual_restore, exp_bonus, breakthrough_bonus, herb_age, created_at) VALUES
('筑基丹', '筑基期关键丹药，增加10%筑基成功率', 'pill', '上品', 1, 1, 5, 50000, 25000, '炼气期', 13, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.10, 0, datetime('now')),
('玄元丹', '筑基期修炼丹药，增加5000修为', 'pill', '中品', 1, 1, 30, 3000, 1500, '筑基期', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 5000, 0.0, 0, datetime('now')),
('归元丹', '筑基期高级修炼丹药，增加10000修为', 'pill', '上品', 1, 1, 20, 8000, 4000, '筑基期', 5, 0, 0, 0, 0, 0, NULL, 0, 0, 10000, 0.0, 0, datetime('now')),
('复灵丹', '恢复1000灵力', 'pill', '中品', 1, 1, 99, 1000, 500, '筑基期', 0, 0, 0, 0, 0, 0, NULL, 0, 1000, 0, 0.0, 0, datetime('now')),
('大还丹', '恢复2000生命和1000灵力', 'pill', '上品', 1, 1, 50, 5000, 2500, '筑基期', 0, 0, 0, 0, 0, 0, NULL, 2000, 1000, 0, 0.0, 0, datetime('now')),
('洗髓丹', '洗涤髓脉，增加灵根纯度', 'pill', '极品', 1, 1, 3, 100000, 50000, '筑基期', 0, 0, 0, 0, 0, 0, '{"purity_increase": 5}', 0, 0, 0, 0.0, 0, datetime('now')),
('凝丹助药', '辅助结丹，增加8%结丹成功率', 'pill', '上品', 1, 1, 5, 80000, 40000, '筑基期', 10, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.08, 0, datetime('now')),
('养神丹', '滋养元神，恢复200神识', 'pill', '上品', 1, 1, 20, 5000, 2500, '筑基期', 0, 0, 0, 0, 0, 0, '{"divine_sense_restore": 200}', 0, 0, 0, 0.0, 0, datetime('now')),
('避火丹', '3小时内火焰伤害减少50%', 'pill', '中品', 1, 1, 20, 3000, 1500, '筑基期', 0, 0, 0, 0, 0, 0, '{"fire_resistance": 0.5, "duration": 180}', 0, 0, 0, 0.0, 0, datetime('now')),
('避水丹', '3小时内水下呼吸', 'pill', '中品', 1, 1, 20, 3000, 1500, '筑基期', 0, 0, 0, 0, 0, 0, '{"water_breathing": true, "duration": 180}', 0, 0, 0, 0.0, 0, datetime('now')),
('天元丹', '筑基期顶级修炼丹药，增加20000修为', 'pill', '极品', 1, 1, 10, 20000, 10000, '筑基期', 10, 0, 0, 0, 0, 0, NULL, 0, 0, 20000, 0.0, 0, datetime('now')),
('续命丹', '增加5年寿命', 'pill', '上品', 1, 1, 10, 30000, 15000, '筑基期', 0, 0, 0, 0, 0, 0, '{"lifespan_increase": 1825}', 0, 0, 0, 0.0, 0, datetime('now')),
('速愈丹', '快速恢复伤势，每秒恢复200生命，持续5回合', 'pill', '上品', 1, 1, 20, 8000, 4000, '筑基期', 0, 0, 0, 0, 0, 0, '{"hp_regen": 200, "duration": 5}', 1000, 0, 0, 0.0, 0, datetime('now')),
('定神丹', '稳固心神，抵抗幻术', 'pill', '上品', 1, 1, 15, 6000, 3000, '筑基期', 5, 0, 0, 0, 0, 0, '{"resist_illusion": 0.5}', 0, 0, 0, 0.0, 0, datetime('now')),
('化血丹', '邪道丹药，吸取他人血气恢复3000生命', 'pill', '中品', 1, 1, 10, 10000, 5000, '筑基期', 0, 0, 0, 0, 0, 0, '{"life_steal": true}', 3000, 0, 0, 0.0, 0, datetime('now'));

-- 结丹期丹药 (10个)
INSERT INTO items (name, description, item_type, treasure_grade, is_tradable, is_stackable, max_stack, buy_price, sell_price, required_realm, required_level, attack_bonus, defense_bonus, hp_bonus, spiritual_bonus, speed_bonus, special_ability, hp_restore, spiritual_restore, exp_bonus, breakthrough_bonus, herb_age, created_at) VALUES
('结金丹', '结丹期关键丹药，增加15%结丹成功率', 'pill', '极品', 1, 1, 3, 200000, 100000, '筑基期', 19, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.15, 0, datetime('now')),
('金丹期修炼丹', '结丹期修炼丹药，增加50000修为', 'pill', '上品', 1, 1, 20, 30000, 15000, '结丹期', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 50000, 0.0, 0, datetime('now')),
('九转还魂丹', '绝世疗伤圣药，复活并恢复50%生命', 'pill', '仙品', 0, 1, 1, 500000, 250000, '结丹期', 0, 0, 0, 0, 0, 0, '{"revive": true, "hp_restore_pct": 0.5}', 0, 0, 0, 0.0, 0, datetime('now')),
('破婴丹', '辅助凝婴，增加10%元婴成功率', 'pill', '极品', 1, 1, 3, 300000, 150000, '结丹期', 25, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.10, 0, datetime('now')),
('紫府金丹', '结丹期顶级丹药，增加100000修为', 'pill', '极品', 1, 1, 10, 80000, 40000, '结丹期', 10, 0, 0, 0, 0, 0, NULL, 0, 0, 100000, 0.0, 0, datetime('now')),
('万灵丹', '恢复5000生命和3000灵力', 'pill', '极品', 1, 1, 30, 30000, 15000, '结丹期', 0, 0, 0, 0, 0, 0, NULL, 5000, 3000, 0, 0.0, 0, datetime('now')),
('固本培元丹', '稳固金丹，增加金丹品质', 'pill', '极品', 1, 1, 5, 150000, 75000, '结丹期', 0, 0, 0, 0, 0, 0, '{"core_quality_increase": 5}', 0, 0, 0, 0.0, 0, datetime('now')),
('养婴丹', '滋养元婴，增加修为', 'pill', '上品', 1, 1, 15, 50000, 25000, '结丹期', 10, 0, 0, 0, 0, 0, NULL, 0, 0, 80000, 0.0, 0, datetime('now')),
('天罡丹', '增加灵力上限500点', 'pill', '极品', 1, 1, 5, 100000, 50000, '结丹期', 0, 0, 0, 0, 500, 0, '{"permanent_effect": true}', 0, 0, 0, 0.0, 0, datetime('now')),
('延寿丹', '增加10年寿命', 'pill', '极品', 1, 1, 5, 100000, 50000, '结丹期', 0, 0, 0, 0, 0, 0, '{"lifespan_increase": 3650}', 0, 0, 0, 0.0, 0, datetime('now'));

-- 元婴期丹药 (5个)
INSERT INTO items (name, description, item_type, treasure_grade, is_tradable, is_stackable, max_stack, buy_price, sell_price, required_realm, required_level, attack_bonus, defense_bonus, hp_bonus, spiritual_bonus, speed_bonus, special_ability, hp_restore, spiritual_restore, exp_bonus, breakthrough_bonus, herb_age, created_at) VALUES
('化神丹', '辅助化神，增加12%化神成功率', 'pill', '仙品', 1, 1, 2, 1000000, 500000, '元婴期', 32, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.12, 0, datetime('now')),
('元婴期修炼丹', '元婴期修炼丹药，增加200000修为', 'pill', '极品', 1, 1, 15, 150000, 75000, '元婴期', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 200000, 0.0, 0, datetime('now')),
('涅槃重生丹', '死后自动复活，恢复100%生命（一次性）', 'pill', '仙品', 0, 1, 1, 2000000, 1000000, '元婴期', 0, 0, 0, 0, 0, 0, '{"auto_revive": true, "hp_restore_pct": 1.0}', 0, 0, 0, 0.0, 0, datetime('now')),
('破镜丹', '突破瓶颈，增加20%突破成功率', 'pill', '仙品', 1, 1, 3, 500000, 250000, '元婴期', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.20, 0, datetime('now')),
('太乙金丹', '传说中的仙丹，增加1000000修为', 'pill', '仙品', 1, 1, 3, 800000, 400000, '元婴期', 10, 0, 0, 0, 0, 0, NULL, 0, 0, 1000000, 0.0, 0, datetime('now'));

-- 化神期丹药 (5个)
INSERT INTO items (name, description, item_type, treasure_grade, is_tradable, is_stackable, max_stack, buy_price, sell_price, required_realm, required_level, attack_bonus, defense_bonus, hp_bonus, spiritual_bonus, speed_bonus, special_ability, hp_restore, spiritual_restore, exp_bonus, breakthrough_bonus, herb_age, created_at) VALUES
('飞升丹', '增加飞升成功率15%', 'pill', '仙品', 0, 1, 1, 5000000, 2500000, '化神期', 38, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.15, 0, datetime('now')),
('化神期修炼丹', '化神期修炼丹药，增加500000修为', 'pill', '仙品', 1, 1, 10, 500000, 250000, '化神期', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 500000, 0.0, 0, datetime('now')),
('不死丹', '增加50年寿命', 'pill', '仙品', 0, 1, 2, 3000000, 1500000, '化神期', 0, 0, 0, 0, 0, 0, '{"lifespan_increase": 18250}', 0, 0, 0, 0.0, 0, datetime('now')),
('九转金丹', '仙界丹药，恢复所有生命和灵力', 'pill', '仙品', 0, 1, 5, 1000000, 500000, '化神期', 0, 0, 0, 0, 0, 0, '{"full_restore": true}', 99999, 99999, 0, 0.0, 0, datetime('now')),
('造化丹', '逆天改命，提升悟性', 'pill', '仙品', 0, 1, 1, 10000000, 5000000, '化神期', 0, 0, 0, 0, 0, 0, '{"comprehension_increase": 10}', 0, 0, 0, 0.0, 0, datetime('now'));

-- ============================================
-- 材料类 (80个)
-- ============================================

-- 草药材料 (30个)
INSERT INTO items (name, description, item_type, treasure_grade, is_tradable, is_stackable, max_stack, buy_price, sell_price, required_realm, required_level, attack_bonus, defense_bonus, hp_bonus, spiritual_bonus, speed_bonus, special_ability, hp_restore, spiritual_restore, exp_bonus, breakthrough_bonus, herb_age, created_at) VALUES
('灵草', '最基础的炼丹材料', 'material', NULL, 1, 1, 999, 10, 5, '凡人', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.0, 1, datetime('now')),
('血参', '珍贵药材，可炼制回血丹药', 'material', NULL, 1, 1, 999, 50, 25, '凡人', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.0, 10, datetime('now')),
('灵芝', '百年灵芝，可炼制增寿丹', 'material', '下品', 1, 1, 500, 100, 50, '炼气期', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.0, 100, datetime('now')),
('何首乌', '黑发药材，炼制养颜丹', 'material', NULL, 1, 1, 500, 80, 40, '炼气期', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.0, 50, datetime('now')),
('人参', '大补药材', 'material', NULL, 1, 1, 500, 150, 75, '炼气期', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.0, 30, datetime('now')),
('雪莲', '天山雪莲，寒性药材', 'material', '中品', 1, 1, 300, 500, 250, '筑基期', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.0, 300, datetime('now')),
('千年人参', '千年人参王', 'material', '上品', 1, 1, 100, 5000, 2500, '筑基期', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.0, 1000, datetime('now')),
('灵药草', '炼制聚气丹的主材料', 'material', NULL, 1, 1, 999, 30, 15, '炼气期', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.0, 5, datetime('now')),
('青莲花', '水属性药材', 'material', '中品', 1, 1, 300, 200, 100, '炼气期', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.0, 100, datetime('now')),
('火莲', '火属性药材，生长在火山', 'material', '中品', 1, 1, 300, 300, 150, '筑基期', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.0, 200, datetime('now')),
('冰莲', '冰属性药材，生长在冰川', 'material', '中品', 1, 1, 300, 300, 150, '筑基期', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.0, 200, datetime('now')),
('紫灵芝', '千年紫灵芝', 'material', '上品', 1, 1, 200, 3000, 1500, '筑基期', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.0, 1000, datetime('now')),
('金线莲', '金属性药材', 'material', '中品', 1, 1, 300, 400, 200, '筑基期', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.0, 150, datetime('now')),
('木灵根', '木属性药材', 'material', '中品', 1, 1, 300, 400, 200, '筑基期', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.0, 150, datetime('now')),
('地黄', '土属性药材', 'material', '中品', 1, 1, 300, 400, 200, '筑基期', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.0, 150, datetime('now')),
('龙须草', '传说中的仙草', 'material', '极品', 1, 1, 50, 10000, 5000, '结丹期', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.0, 5000, datetime('now')),
('七叶一枝花', '解毒圣药', 'material', '上品', 1, 1, 200, 2000, 1000, '筑基期', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.0, 500, datetime('now')),
('朱果', '传说中的朱果，可增加修为', 'material', '极品', 1, 1, 50, 20000, 10000, '结丹期', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 50000, 0.0, 10000, datetime('now')),
('菩提子', '佛门圣物，增加悟性', 'material', '仙品', 1, 1, 10, 100000, 50000, '元婴期', 0, 0, 0, 0, 0, 0, '{"comprehension_increase": 5}', 0, 0, 0, 0.0, 50000, datetime('now')),
('混沌青莲', '开天辟地之时的青莲', 'material', '仙品', 0, 1, 1, 10000000, 5000000, '化神期', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.0, 999999, datetime('now')),
('龙血草', '沾染龙血的仙草', 'material', '极品', 1, 1, 30, 50000, 25000, '元婴期', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.0, 10000, datetime('now')),
('凤凰花', '凤凰涅槃之地的花朵', 'material', '极品', 1, 1, 30, 50000, 25000, '元婴期', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.0, 10000, datetime('now')),
('麒麟果', '麒麟栖息地的果实', 'material', '极品', 1, 1, 30, 50000, 25000, '元婴期', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.0, 10000, datetime('now')),
('九幽草', '生长在九幽之地的阴草', 'material', '上品', 1, 1, 100, 8000, 4000, '结丹期', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.0, 3000, datetime('now')),
('太阳花', '吸收太阳精华的花', 'material', '上品', 1, 1, 100, 8000, 4000, '结丹期', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.0, 3000, datetime('now')),
('太阴花', '吸收太阴精华的花', 'material', '上品', 1, 1, 100, 8000, 4000, '结丹期', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.0, 3000, datetime('now')),
('星辰草', '吸收星辰之力的仙草', 'material', '极品', 1, 1, 50, 30000, 15000, '元婴期', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.0, 8000, datetime('now')),
('血玉芝', '珍稀血芝', 'material', '上品', 1, 1, 80, 6000, 3000, '结丹期', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.0, 2000, datetime('now')),
('金乌羽', '金乌的羽毛', 'material', '极品', 1, 1, 20, 80000, 40000, '元婴期', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.0, 50000, datetime('now')),
('建木枝', '神树建木的树枝', 'material', '仙品', 1, 1, 5, 200000, 100000, '化神期', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.0, 100000, datetime('now'));

-- 矿石材料 (25个)
INSERT INTO items (name, description, item_type, treasure_grade, is_tradable, is_stackable, max_stack, buy_price, sell_price, required_realm, required_level, attack_bonus, defense_bonus, hp_bonus, spiritual_bonus, speed_bonus, special_ability, hp_restore, spiritual_restore, exp_bonus, breakthrough_bonus, herb_age, created_at) VALUES
('铁矿石', '最普通的矿石', 'material', NULL, 1, 1, 999, 5, 2, '凡人', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.0, 0, datetime('now')),
('铜矿石', '铜矿石', 'material', NULL, 1, 1, 999, 8, 4, '凡人', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.0, 0, datetime('now')),
('银矿石', '银矿石', 'material', NULL, 1, 1, 999, 20, 10, '炼气期', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.0, 0, datetime('now')),
('金矿石', '黄金矿石', 'material', '下品', 1, 1, 500, 50, 25, '炼气期', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.0, 0, datetime('now')),
('紫铜精', '紫铜精华', 'material', '中品', 1, 1, 300, 200, 100, '炼气期', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.0, 0, datetime('now')),
('精铁', '精炼过的铁', 'material', '下品', 1, 1, 500, 100, 50, '炼气期', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.0, 0, datetime('now')),
('寒铁', '寒属性矿石', 'material', '中品', 1, 1, 300, 500, 250, '筑基期', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.0, 0, datetime('now')),
('赤铜', '火属性矿石', 'material', '中品', 1, 1, 300, 500, 250, '筑基期', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.0, 0, datetime('now')),
('玄铁', '黑色玄铁', 'material', '上品', 1, 1, 200, 2000, 1000, '筑基期', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.0, 0, datetime('now')),
('秘银', '传说中的秘银', 'material', '上品', 1, 1, 200, 3000, 1500, '筑基期', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.0, 0, datetime('now')),
('精金', '炼器必备的精金', 'material', '上品', 1, 1, 200, 5000, 2500, '结丹期', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.0, 0, datetime('now')),
('陨铁', '从天而降的陨石', 'material', '极品', 1, 1, 100, 10000, 5000, '结丹期', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.0, 0, datetime('now')),
('星辰铁', '星辰陨落凝聚的矿石', 'material', '极品', 1, 1, 50, 30000, 15000, '元婴期', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.0, 0, datetime('now')),
('龙鳞铁', '沾染龙鳞气息的矿石', 'material', '极品', 1, 1, 50, 40000, 20000, '元婴期', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.0, 0, datetime('now')),
('凤凰金', '凤凰涅槃之地的矿石', 'material', '极品', 1, 1, 50, 40000, 20000, '元婴期', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.0, 0, datetime('now')),
('混沌石', '混沌孕育的奇石', 'material', '仙品', 1, 1, 20, 100000, 50000, '化神期', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.0, 0, datetime('now')),
('五色石', '女娲补天剩余的石头', 'material', '仙品', 1, 1, 10, 200000, 100000, '化神期', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.0, 0, datetime('now')),
('庚金', '至刚至硬的矿石', 'material', '极品', 1, 1, 80, 25000, 12500, '元婴期', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.0, 0, datetime('now')),
('水晶石', '透明水晶', 'material', '下品', 1, 1, 500, 80, 40, '炼气期', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.0, 0, datetime('now')),
('翡翠石', '绿色翡翠', 'material', '中品', 1, 1, 300, 300, 150, '筑基期', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.0, 0, datetime('now')),
('玉石', '温润玉石', 'material', '中品', 1, 1, 300, 400, 200, '筑基期', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.0, 0, datetime('now')),
('灵玉', '蕴含灵气的玉石', 'material', '上品', 1, 1, 200, 3000, 1500, '结丹期', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.0, 0, datetime('now')),
('琉璃', '七彩琉璃', 'material', '极品', 1, 1, 100, 15000, 7500, '元婴期', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.0, 0, datetime('now')),
('紫晶', '紫色晶石', 'material', '上品', 1, 1, 150, 5000, 2500, '结丹期', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.0, 0, datetime('now')),
('黑曜石', '漆黑的矿石', 'material', '中品', 1, 1, 300, 600, 300, '筑基期', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.0, 0, datetime('now'));

-- 妖兽材料 (25个)
INSERT INTO items (name, description, item_type, treasure_grade, is_tradable, is_stackable, max_stack, buy_price, sell_price, required_realm, required_level, attack_bonus, defense_bonus, hp_bonus, spiritual_bonus, speed_bonus, special_ability, hp_restore, spiritual_restore, exp_bonus, breakthrough_bonus, herb_age, created_at) VALUES
('妖兽皮', '普通妖兽的皮毛', 'material', NULL, 1, 1, 999, 20, 10, '炼气期', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.0, 0, datetime('now')),
('妖兽骨', '妖兽的骨头', 'material', NULL, 1, 1, 999, 30, 15, '炼气期', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.0, 0, datetime('now')),
('妖丹', '妖兽的内丹', 'material', '下品', 1, 1, 500, 100, 50, '炼气期', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.0, 0, datetime('now')),
('筑基妖丹', '筑基期妖兽的妖丹', 'material', '中品', 1, 1, 300, 1000, 500, '筑基期', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.0, 0, datetime('now')),
('结丹妖丹', '结丹期妖兽的妖丹', 'material', '上品', 1, 1, 200, 10000, 5000, '结丹期', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.0, 0, datetime('now')),
('龙鳞', '真龙的鳞片', 'material', '仙品', 1, 1, 20, 100000, 50000, '元婴期', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.0, 0, datetime('now')),
('凤凰羽', '凤凰的羽毛', 'material', '仙品', 1, 1, 20, 100000, 50000, '元婴期', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.0, 0, datetime('now')),
('麒麟角', '麒麟的角', 'material', '仙品', 1, 1, 10, 150000, 75000, '元婴期', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.0, 0, datetime('now')),
('玄武甲', '玄武的龟甲', 'material', '仙品', 1, 1, 10, 150000, 75000, '元婴期', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.0, 0, datetime('now')),
('虎骨', '老虎的骨头', 'material', '下品', 1, 1, 500, 50, 25, '炼气期', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.0, 0, datetime('now')),
('熊胆', '黑熊的熊胆', 'material', '下品', 1, 1, 500, 80, 40, '炼气期', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.0, 0, datetime('now')),
('蛇胆', '蛇的胆囊', 'material', NULL, 1, 1, 999, 30, 15, '炼气期', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.0, 0, datetime('now')),
('鹰爪', '老鹰的爪子', 'material', NULL, 1, 1, 999, 40, 20, '炼气期', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.0, 0, datetime('now')),
('狼牙', '野狼的牙齿', 'material', NULL, 1, 1, 999, 25, 12, '炼气期', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.0, 0, datetime('now')),
('蝎毒', '毒蝎的毒液', 'material', '下品', 1, 1, 500, 100, 50, '炼气期', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.0, 0, datetime('now')),
('蜘蛛丝', '灵蜘蛛的蛛丝', 'material', '下品', 1, 1, 500, 60, 30, '炼气期', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.0, 0, datetime('now')),
('蝙蝠翼', '血蝙蝠的翅膀', 'material', '下品', 1, 1, 500, 70, 35, '炼气期', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.0, 0, datetime('now')),
('龙血', '真龙之血', 'material', '仙品', 1, 1, 10, 200000, 100000, '化神期', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.0, 0, datetime('now')),
('凤凰血', '凤凰之血', 'material', '仙品', 1, 1, 10, 200000, 100000, '化神期', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.0, 0, datetime('now')),
('金蛟鳞', '金蛟的鳞片', 'material', '极品', 1, 1, 50, 50000, 25000, '元婴期', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.0, 0, datetime('now')),
('银蟒皮', '银蟒的皮', 'material', '上品', 1, 1, 100, 8000, 4000, '结丹期', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.0, 0, datetime('now')),
('雷鸟羽', '雷鸟的羽毛', 'material', '上品', 1, 1, 100, 6000, 3000, '结丹期', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.0, 0, datetime('now')),
('火乌翎', '火乌的翎羽', 'material', '上品', 1, 1, 100, 6000, 3000, '结丹期', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.0, 0, datetime('now')),
('冰蝶粉', '冰蝶的鳞粉', 'material', '中品', 1, 1, 300, 1000, 500, '筑基期', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.0, 0, datetime('now')),
('灵猿筋', '灵猴的筋腱', 'material', '中品', 1, 1, 300, 1200, 600, '筑基期', 0, 0, 0, 0, 0, 0, NULL, 0, 0, 0, 0.0, 0, datetime('now'));

-- ============================================
-- 武器类 (40个)
-- ============================================

-- 炼气期武器 (12个)
INSERT INTO items (name, description, item_type, treasure_grade, is_tradable, is_stackable, max_stack, buy_price, sell_price, required_realm, required_level, attack_bonus, defense_bonus, hp_bonus, spiritual_bonus, speed_bonus, special_ability, hp_restore, spiritual_restore, exp_bonus, breakthrough_bonus, herb_age, created_at) VALUES
('木剑', '普通木剑', 'weapon', NULL, 1, 0, 1, 50, 25, '凡人', 0, 5, 0, 0, 0, 0, NULL, 0, 0, 0, 0.0, 0, datetime('now')),
('铁剑', '普通铁剑', 'weapon', NULL, 1, 0, 1, 200, 100, '炼气期', 1, 15, 0, 0, 0, 0, NULL, 0, 0, 0, 0.0, 0, datetime('now')),
('青铜剑', '青铜打造的剑', 'weapon', '下品', 1, 0, 1, 500, 250, '炼气期', 3, 25, 0, 0, 0, 2, NULL, 0, 0, 0, 0.0, 0, datetime('now')),
('精钢剑', '精钢打造的剑', 'weapon', '下品', 1, 0, 1, 1000, 500, '炼气期', 5, 40, 0, 0, 0, 3, NULL, 0, 0, 0, 0.0, 0, datetime('now')),
('寒铁剑', '寒铁打造，附带冰属性', 'weapon', '中品', 1, 0, 1, 3000, 1500, '炼气期', 8, 60, 0, 0, 0, 5, '{"element": "ice", "freeze_chance": 0.1}', 0, 0, 0, 0.0, 0, datetime('now')),
('烈焰刀', '烈焰刀法，火属性武器', 'weapon', '中品', 1, 0, 1, 3000, 1500, '炼气期', 8, 65, 0, 0, 0, 4, '{"element": "fire", "burn_chance": 0.1}', 0, 0, 0, 0.0, 0, datetime('now')),
('青钢枪', '青钢长枪', 'weapon', '中品', 1, 0, 1, 2500, 1250, '炼气期', 7, 55, 0, 0, 0, 6, NULL, 0, 0, 0, 0.0, 0, datetime('now')),
('乌木弓', '上等乌木打造的弓', 'weapon', '下品', 1, 0, 1, 1500, 750, '炼气期', 5, 45, 0, 0, 0, 8, '{"range_weapon": true}', 0, 0, 0, 0.0, 0, datetime('now')),
('飞剑', '炼气期基础飞剑', 'weapon', '中品', 1, 0, 1, 5000, 2500, '炼气期', 10, 80, 0, 0, 50, 10, '{"flying_sword": true}', 0, 0, 0, 0.0, 0, datetime('now')),
('玄铁重剑', '重达百斤的玄铁剑', 'weapon', '上品', 1, 0, 1, 8000, 4000, '炼气期', 12, 100, 5, 0, 0, -5, '{"heavy_weapon": true, "armor_penetration": 0.2}', 0, 0, 0, 0.0, 0, datetime('now')),
('柳叶刀', '轻盈的柳叶刀', 'weapon', '中品', 1, 0, 1, 2000, 1000, '炼气期', 6, 50, 0, 0, 0, 12, '{"light_weapon": true, "crit_rate": 0.05}', 0, 0, 0, 0.0, 0, datetime('now')),
('雷电法杖', '雷属性法杖', 'weapon', '上品', 1, 0, 1, 10000, 5000, '炼气期', 13, 90, 0, 0, 100, 5, '{"element": "thunder", "paralyze_chance": 0.15}', 0, 0, 0, 0.0, 0, datetime('now'));

-- 筑基期武器 (12个)
INSERT INTO items (name, description, item_type, treasure_grade, is_tradable, is_stackable, max_stack, buy_price, sell_price, required_realm, required_level, attack_bonus, defense_bonus, hp_bonus, spiritual_bonus, speed_bonus, special_ability, hp_restore, spiritual_restore, exp_bonus, breakthrough_bonus, herb_age, created_at) VALUES
('秘银剑', '秘银打造的上品宝剑', 'weapon', '上品', 1, 0, 1, 20000, 10000, '筑基期', 0, 150, 10, 0, 0, 8, '{"spiritual_damage": 50}', 0, 0, 0, 0.0, 0, datetime('now')),
('青虹剑', '筑基期名剑', 'weapon', '上品', 1, 0, 1, 30000, 15000, '筑基期', 5, 200, 15, 0, 100, 12, '{"sword_qi": true, "crit_damage": 0.3}', 0, 0, 0, 0.0, 0, datetime('now')),
('龙泉剑', '传说中的龙泉宝剑', 'weapon', '极品', 1, 0, 1, 80000, 40000, '筑基期', 12, 280, 20, 0, 150, 15, '{"dragon_power": true, "attack_boost": 0.2}', 0, 0, 0, 0.0, 0, datetime('now')),
('霜寒刀', '至寒之刀', 'weapon', '上品', 1, 0, 1, 35000, 17500, '筑基期', 8, 220, 10, 0, 0, 10, '{"element": "ice", "freeze_chance": 0.25, "slow": 0.3}', 0, 0, 0, 0.0, 0, datetime('now')),
('赤炎枪', '火属性长枪', 'weapon', '上品', 1, 0, 1, 35000, 17500, '筑基期', 8, 230, 12, 0, 0, 14, '{"element": "fire", "burn_damage": 100}', 0, 0, 0, 0.0, 0, datetime('now')),
('紫金锤', '紫金打造的重锤', 'weapon', '极品', 1, 0, 1, 60000, 30000, '筑基期', 10, 300, 30, 0, 0, -10, '{"stun_chance": 0.3, "armor_penetration": 0.4}', 0, 0, 0, 0.0, 0, datetime('now')),
('流星弓', '远程神器', 'weapon', '上品', 1, 0, 1, 40000, 20000, '筑基期', 7, 210, 0, 0, 0, 20, '{"range_weapon": true, "piercing": true}', 0, 0, 0, 0.0, 0, datetime('now')),
('碧玉箫', '音律武器', 'weapon', '上品', 1, 0, 1, 50000, 25000, '筑基期', 9, 180, 10, 0, 200, 8, '{"sonic_attack": true, "confusion_chance": 0.2}', 0, 0, 0, 0.0, 0, datetime('now')),
('飞虹剑', '高阶飞剑', 'weapon', '极品', 1, 0, 1, 100000, 50000, '筑基期', 15, 350, 25, 0, 200, 25, '{"flying_sword": true, "sword_array": 7}', 0, 0, 0, 0.0, 0, datetime('now')),
('七星剑', '北斗七星之力', 'weapon', '极品', 1, 0, 1, 120000, 60000, '筑基期', 18, 400, 30, 0, 250, 20, '{"seven_stars": true, "crit_rate": 0.15}', 0, 0, 0, 0.0, 0, datetime('now')),
('金刚杵', '佛门法器', 'weapon', '上品', 1, 0, 1, 45000, 22500, '筑基期', 10, 250, 40, 100, 100, 5, '{"buddha_power": true, "demon_damage": 1.5}', 0, 0, 0, 0.0, 0, datetime('now')),
('阴阳扇', '阴阳两仪之力', 'weapon', '极品', 1, 0, 1, 90000, 45000, '筑基期', 14, 320, 20, 0, 180, 18, '{"yin_yang": true, "element_all": true}', 0, 0, 0, 0.0, 0, datetime('now'));

-- 结丹期武器 (8个)
INSERT INTO items (name, description, item_type, treasure_grade, is_tradable, is_stackable, max_stack, buy_price, sell_price, required_realm, required_level, attack_bonus, defense_bonus, hp_bonus, spiritual_bonus, speed_bonus, special_ability, hp_restore, spiritual_restore, exp_bonus, breakthrough_bonus, herb_age, created_at) VALUES
('斩仙剑', '传说中的斩仙神剑', 'weapon', '仙品', 1, 0, 1, 500000, 250000, '结丹期', 0, 600, 50, 0, 300, 30, '{"ignore_defense": 0.3, "true_damage": 0.2}', 0, 0, 0, 0.0, 0, datetime('now')),
('九天玄刃', '九天神雷凝聚', 'weapon', '仙品', 1, 0, 1, 600000, 300000, '结丹期', 5, 700, 60, 0, 400, 35, '{"element": "thunder", "chain_lightning": 3}', 0, 0, 0, 0.0, 0, datetime('now')),
('太乙拂尘', '道门至宝', 'weapon', '极品', 1, 0, 1, 400000, 200000, '结丹期', 0, 500, 80, 200, 500, 25, '{"dao_power": true, "purify": true}', 0, 0, 0, 0.0, 0, datetime('now')),
('凤凰琴', '凤凰神音', 'weapon', '仙品', 1, 0, 1, 550000, 275000, '结丹期', 8, 650, 40, 0, 450, 28, '{"sonic_attack": true, "phoenix_fire": true}', 0, 0, 0, 0.0, 0, datetime('now')),
('屠龙刀', '屠龙神刀', 'weapon', '仙品', 1, 0, 1, 650000, 325000, '结丹期', 10, 750, 70, 0, 0, 20, '{"dragon_slayer": true, "armor_penetration": 0.5}', 0, 0, 0, 0.0, 0, datetime('now')),
('轩辕剑', '人皇之剑', 'weapon', '仙品', 0, 0, 1, 2000000, 1000000, '结丹期', 15, 1000, 100, 500, 500, 40, '{"emperor_power": true, "all_stats_boost": 0.3}', 0, 0, 0, 0.0, 0, datetime('now')),
('诛仙剑阵', '诛仙四剑', 'weapon', '仙品', 0, 0, 1, 3000000, 1500000, '结丹期', 20, 1200, 80, 0, 600, 50, '{"sword_array": 4, "formation_power": true}', 0, 0, 0, 0.0, 0, datetime('now')),
('番天印', '翻天覆地之力', 'weapon', '仙品', 1, 0, 1, 800000, 400000, '结丹期', 12, 900, 150, 300, 200, -20, '{"mountain_power": true, "stun_chance": 0.5}', 0, 0, 0, 0.0, 0, datetime('now'));

-- 元婴期武器 (5个)
INSERT INTO items (name, description, item_type, treasure_grade, is_tradable, is_stackable, max_stack, buy_price, sell_price, required_realm, required_level, attack_bonus, defense_bonus, hp_bonus, spiritual_bonus, speed_bonus, special_ability, hp_restore, spiritual_restore, exp_bonus, breakthrough_bonus, herb_age, created_at) VALUES
('盘古斧', '开天神斧', 'weapon', '仙品', 0, 0, 1, 5000000, 2500000, '元婴期', 0, 1500, 200, 1000, 0, 10, '{"chaos_power": true, "space_tear": true}', 0, 0, 0, 0.0, 0, datetime('now')),
('东皇钟', '时间之力', 'weapon', '仙品', 0, 0, 1, 8000000, 4000000, '元婴期', 10, 1800, 500, 2000, 1000, 0, '{"time_control": true, "invulnerable": 3}', 0, 0, 0, 0.0, 0, datetime('now')),
('昊天塔', '镇压万物', 'weapon', '仙品', 0, 0, 1, 6000000, 3000000, '元婴期', 5, 1600, 400, 1500, 800, 5, '{"suppress_power": true, "seal_enemy": true}', 0, 0, 0, 0.0, 0, datetime('now')),
('混沌钟', '混沌至宝', 'weapon', '仙品', 0, 0, 1, 10000000, 5000000, '元婴期', 15, 2000, 600, 3000, 1500, 20, '{"chaos_supreme": true, "reflect_damage": 0.5}', 0, 0, 0, 0.0, 0, datetime('now')),
('打神鞭', '封神之鞭', 'weapon', '仙品', 0, 0, 1, 7000000, 3500000, '元婴期', 8, 1700, 300, 1000, 1200, 30, '{"god_killer": true, "soul_damage": true}', 0, 0, 0, 0.0, 0, datetime('now'));

-- 化神期武器 (3个)
INSERT INTO items (name, description, item_type, treasure_grade, is_tradable, is_stackable, max_stack, buy_price, sell_price, required_realm, required_level, attack_bonus, defense_bonus, hp_bonus, spiritual_bonus, speed_bonus, special_ability, hp_restore, spiritual_restore, exp_bonus, breakthrough_bonus, herb_age, created_at) VALUES
('先天至宝', '先天孕育的至宝', 'weapon', '仙品', 0, 0, 1, 20000000, 10000000, '化神期', 0, 3000, 1000, 5000, 3000, 50, '{"innate_treasure": true, "law_power": true}', 0, 0, 0, 0.0, 0, datetime('now')),
('弑神枪', '弑杀神明之枪', 'weapon', '仙品', 0, 0, 1, 15000000, 7500000, '化神期', 5, 3500, 500, 2000, 2000, 60, '{"god_slayer": true, "penetrate_all": true}', 0, 0, 0, 0.0, 0, datetime('now')),
('造化玉碟', '大道之源', 'weapon', '仙品', 0, 0, 1, 50000000, 25000000, '化神期', 10, 5000, 2000, 10000, 5000, 100, '{"dao_origin": true, "comprehension_boost": 100}', 0, 0, 0, 0.0, 0, datetime('now'));

-- ============================================
-- 防具类 (30个)
-- ============================================

-- 炼气期防具 (10个)
INSERT INTO items (name, description, item_type, treasure_grade, is_tradable, is_stackable, max_stack, buy_price, sell_price, required_realm, required_level, attack_bonus, defense_bonus, hp_bonus, spiritual_bonus, speed_bonus, special_ability, hp_restore, spiritual_restore, exp_bonus, breakthrough_bonus, herb_age, created_at) VALUES
('布衣', '普通布衣', 'armor', NULL, 1, 0, 1, 30, 15, '凡人', 0, 0, 5, 50, 0, 0, NULL, 0, 0, 0, 0.0, 0, datetime('now')),
('皮甲', '兽皮制成的防具', 'armor', NULL, 1, 0, 1, 100, 50, '炼气期', 1, 0, 15, 100, 0, 0, NULL, 0, 0, 0, 0.0, 0, datetime('now')),
('铁甲', '铁制盔甲', 'armor', '下品', 1, 0, 1, 300, 150, '炼气期', 3, 0, 30, 200, 0, -3, NULL, 0, 0, 0, 0.0, 0, datetime('now')),
('青铜甲', '青铜盔甲', 'armor', '下品', 1, 0, 1, 600, 300, '炼气期', 5, 0, 45, 300, 0, -5, NULL, 0, 0, 0, 0.0, 0, datetime('now')),
('精钢甲', '精钢打造的盔甲', 'armor', '中品', 1, 0, 1, 1500, 750, '炼气期', 8, 0, 70, 500, 0, -8, NULL, 0, 0, 0, 0.0, 0, datetime('now')),
('法袍', '修仙者的法袍', 'armor', '中品', 1, 0, 1, 2000, 1000, '炼气期', 7, 0, 50, 300, 100, 5, '{"spiritual_defense": 30}', 0, 0, 0, 0.0, 0, datetime('now')),
('道袍', '道士的道袍', 'armor', '中品', 1, 0, 1, 2500, 1250, '炼气期', 9, 0, 55, 350, 120, 6, '{"dao_protection": true}', 0, 0, 0, 0.0, 0, datetime('now')),
('僧衣', '和尚的僧衣', 'armor', '中品', 1, 0, 1, 2500, 1250, '炼气期', 9, 0, 60, 400, 80, 4, '{"buddha_protection": true}', 0, 0, 0, 0.0, 0, datetime('now')),
('玄铁甲', '玄铁重甲', 'armor', '上品', 1, 0, 1, 5000, 2500, '炼气期', 12, 0, 100, 800, 0, -15, '{"physical_reduction": 0.2}', 0, 0, 0, 0.0, 0, datetime('now')),
('轻灵衣', '轻盈的防具', 'armor', '上品', 1, 0, 1, 4000, 2000, '炼气期', 11, 0, 60, 400, 150, 15, '{"dodge_rate": 0.1}', 0, 0, 0, 0.0, 0, datetime('now'));

-- 筑基期防具 (10个)
INSERT INTO items (name, description, item_type, treasure_grade, is_tradable, is_stackable, max_stack, buy_price, sell_price, required_realm, required_level, attack_bonus, defense_bonus, hp_bonus, spiritual_bonus, speed_bonus, special_ability, hp_restore, spiritual_restore, exp_bonus, breakthrough_bonus, herb_age, created_at) VALUES
('秘银甲', '秘银打造的盔甲', 'armor', '上品', 1, 0, 1, 15000, 7500, '筑基期', 0, 0, 150, 1000, 0, -5, '{"magic_resistance": 0.15}', 0, 0, 0, 0.0, 0, datetime('now')),
('金丝软甲', '柔软的内甲', 'armor', '上品', 1, 0, 1, 20000, 10000, '筑基期', 3, 0, 120, 800, 100, 10, '{"invisible_armor": true}', 0, 0, 0, 0.0, 0, datetime('now')),
('龙鳞甲', '龙鳞制成的盔甲', 'armor', '极品', 1, 0, 1, 80000, 40000, '筑基期', 12, 0, 250, 2000, 0, 0, '{"dragon_protection": true, "fire_resistance": 0.5}', 0, 0, 0, 0.0, 0, datetime('now')),
('凤羽衣', '凤凰羽毛编织', 'armor', '极品', 1, 0, 1, 80000, 40000, '筑基期', 12, 0, 200, 1500, 300, 20, '{"phoenix_rebirth": 0.1, "fire_immune": true}', 0, 0, 0, 0.0, 0, datetime('now')),
('天蚕丝袍', '天蚕丝制作', 'armor', '上品', 1, 0, 1, 30000, 15000, '筑基期', 6, 0, 160, 1200, 200, 12, '{"auto_repair": true}', 0, 0, 0, 0.0, 0, datetime('now')),
('玄武甲', '玄武龟甲', 'armor', '极品', 1, 0, 1, 100000, 50000, '筑基期', 15, 0, 300, 3000, 0, -10, '{"absolute_defense": true, "damage_reduction": 0.3}', 0, 0, 0, 0.0, 0, datetime('now')),
('冰蚕衣', '冰蚕丝制作', 'armor', '上品', 1, 0, 1, 35000, 17500, '筑基期', 8, 0, 170, 1300, 180, 8, '{"ice_resistance": 0.6}', 0, 0, 0, 0.0, 0, datetime('now')),
('金刚袈裟', '佛门宝物', 'armor', '极品', 1, 0, 1, 90000, 45000, '筑基期', 14, 0, 280, 2500, 200, 5, '{"buddha_blessing": true, "demon_resistance": 0.8}', 0, 0, 0, 0.0, 0, datetime('now')),
('星辰袍', '星辰之力', 'armor', '极品', 1, 0, 1, 70000, 35000, '筑基期', 10, 0, 220, 1800, 250, 15, '{"star_protection": true}', 0, 0, 0, 0.0, 0, datetime('now')),
('阴阳道袍', '阴阳两仪', 'armor', '上品', 1, 0, 1, 40000, 20000, '筑基期', 9, 0, 180, 1400, 220, 10, '{"yin_yang_balance": true}', 0, 0, 0, 0.0, 0, datetime('now'));

-- 结丹期防具 (6个)
INSERT INTO items (name, description, item_type, treasure_grade, is_tradable, is_stackable, max_stack, buy_price, sell_price, required_realm, required_level, attack_bonus, defense_bonus, hp_bonus, spiritual_bonus, speed_bonus, special_ability, hp_restore, spiritual_restore, exp_bonus, breakthrough_bonus, herb_age, created_at) VALUES
('混沌战甲', '混沌之力', 'armor', '仙品', 1, 0, 1, 500000, 250000, '结丹期', 0, 50, 500, 5000, 300, 0, '{"chaos_defense": true, "all_resistance": 0.4}', 0, 0, 0, 0.0, 0, datetime('now')),
('天罡宝甲', '天罡护体', 'armor', '仙品', 1, 0, 1, 600000, 300000, '结丹期', 5, 0, 600, 6000, 400, 10, '{"tiangang_protection": true, "reflect_damage": 0.3}', 0, 0, 0, 0.0, 0, datetime('now')),
('紫霄道袍', '紫霄神雷', 'armor', '极品', 1, 0, 1, 400000, 200000, '结丹期', 0, 0, 450, 4000, 500, 20, '{"thunder_body": true}', 0, 0, 0, 0.0, 0, datetime('now')),
('太极八卦衣', '太极八卦', 'armor', '仙品', 1, 0, 1, 550000, 275000, '结丹期', 8, 0, 550, 5500, 600, 15, '{"taiji_power": true, "damage_transfer": 0.5}', 0, 0, 0, 0.0, 0, datetime('now')),
('不灭金身', '金身不坏', 'armor', '仙品', 1, 0, 1, 800000, 400000, '结丹期', 15, 0, 800, 8000, 0, -20, '{"immortal_body": true, "immune_fatal": true}', 0, 0, 0, 0.0, 0, datetime('now')),
('五行战甲', '五行之力', 'armor', '极品', 1, 0, 1, 450000, 225000, '结丹期', 3, 0, 480, 4500, 400, 8, '{"five_elements": true, "element_immunity": 0.3}', 0, 0, 0, 0.0, 0, datetime('now'));

-- 元婴期防具 (2个)
INSERT INTO items (name, description, item_type, treasure_grade, is_tradable, is_stackable, max_stack, buy_price, sell_price, required_realm, required_level, attack_bonus, defense_bonus, hp_bonus, spiritual_bonus, speed_bonus, special_ability, hp_restore, spiritual_restore, exp_bonus, breakthrough_bonus, herb_age, created_at) VALUES
('先天道体', '先天之体', 'armor', '仙品', 0, 0, 1, 5000000, 2500000, '元婴期', 0, 100, 1500, 15000, 2000, 30, '{"innate_body": true, "law_resistance": 0.5}', 0, 0, 0, 0.0, 0, datetime('now')),
('混元金甲', '混元一体', 'armor', '仙品', 0, 0, 1, 8000000, 4000000, '元婴期', 10, 150, 2000, 20000, 3000, 20, '{"hunyuan_protection": true, "absolute_immunity": 0.3}', 0, 0, 0, 0.0, 0, datetime('now'));

-- 化神期防具 (2个)
INSERT INTO items (name, description, item_type, treasure_grade, is_tradable, is_stackable, max_stack, buy_price, sell_price, required_realm, required_level, attack_bonus, defense_bonus, hp_bonus, spiritual_bonus, speed_bonus, special_ability, hp_restore, spiritual_restore, exp_bonus, breakthrough_bonus, herb_age, created_at) VALUES
('不死之身', '永恒不灭', 'armor', '仙品', 0, 0, 1, 20000000, 10000000, '化神期', 0, 200, 3000, 30000, 5000, 50, '{"undying": true, "auto_resurrect": 1}', 0, 0, 0, 0.0, 0, datetime('now')),
('大道圣衣', '大道庇护', 'armor', '仙品', 0, 0, 1, 50000000, 25000000, '化神期', 10, 500, 5000, 50000, 10000, 100, '{"dao_supreme": true, "invincible": true}', 0, 0, 0, 0.0, 0, datetime('now'));

-- ============================================
-- 饰品类 (20个)
-- ============================================

-- 炼气期饰品 (6个)
INSERT INTO items (name, description, item_type, treasure_grade, is_tradable, is_stackable, max_stack, buy_price, sell_price, required_realm, required_level, attack_bonus, defense_bonus, hp_bonus, spiritual_bonus, speed_bonus, special_ability, hp_restore, spiritual_restore, exp_bonus, breakthrough_bonus, herb_age, created_at) VALUES
('铜戒指', '普通铜戒', 'accessory', NULL, 1, 0, 1, 100, 50, '炼气期', 0, 5, 5, 50, 20, 0, NULL, 0, 0, 0, 0.0, 0, datetime('now')),
('玉佩', '温润玉佩', 'accessory', '下品', 1, 0, 1, 500, 250, '炼气期', 3, 0, 10, 100, 50, 0, '{"spiritual_regen": 5}', 0, 0, 0, 0.0, 0, datetime('now')),
('灵石项链', '灵石制作的项链', 'accessory', '中品', 1, 0, 1, 2000, 1000, '炼气期', 7, 10, 10, 150, 80, 2, '{"exp_boost": 0.05}', 0, 0, 0, 0.0, 0, datetime('now')),
('护身符', '避邪护身符', 'accessory', '中品', 1, 0, 1, 1500, 750, '炼气期', 5, 0, 20, 200, 0, 0, '{"evil_resistance": 0.3}', 0, 0, 0, 0.0, 0, datetime('now')),
('储物袋', '小型储物袋', 'accessory', '中品', 1, 0, 1, 3000, 1500, '炼气期', 8, 0, 0, 0, 0, 0, '{"storage_space": 50}', 0, 0, 0, 0.0, 0, datetime('now')),
('灵兽袋', '可以存放灵兽', 'accessory', '上品', 1, 0, 1, 5000, 2500, '炼气期', 10, 0, 0, 0, 0, 0, '{"beast_storage": 3}', 0, 0, 0, 0.0, 0, datetime('now'));

-- 筑基期饰品 (8个)
INSERT INTO items (name, description, item_type, treasure_grade, is_tradable, is_stackable, max_stack, buy_price, sell_price, required_realm, required_level, attack_bonus, defense_bonus, hp_bonus, spiritual_bonus, speed_bonus, special_ability, hp_restore, spiritual_restore, exp_bonus, breakthrough_bonus, herb_age, created_at) VALUES
('灵玉戒', '灵玉打造', 'accessory', '上品', 1, 0, 1, 20000, 10000, '筑基期', 0, 30, 20, 300, 150, 5, '{"spiritual_regen": 20}', 0, 0, 0, 0.0, 0, datetime('now')),
('储物戒', '空间戒指', 'accessory', '上品', 1, 0, 1, 50000, 25000, '筑基期', 5, 0, 0, 0, 0, 0, '{"storage_space": 200}', 0, 0, 0, 0.0, 0, datetime('now')),
('定魂珠', '稳定元神', 'accessory', '极品', 1, 0, 1, 80000, 40000, '筑基期', 10, 0, 50, 500, 200, 0, '{"soul_protection": true, "resist_soul_attack": 0.5}', 0, 0, 0, 0.0, 0, datetime('now')),
('风行靴', '加速靴子', 'accessory', '上品', 1, 0, 1, 30000, 15000, '筑基期', 3, 0, 15, 200, 0, 30, '{"movement_speed": 1.3}', 0, 0, 0, 0.0, 0, datetime('now')),
('护心镜', '护住心脉', 'accessory', '上品', 1, 0, 1, 40000, 20000, '筑基期', 7, 0, 80, 800, 0, 0, '{"fatal_protection": 0.3}', 0, 0, 0, 0.0, 0, datetime('now')),
('灵兽环', '高级灵兽袋', 'accessory', '极品', 1, 0, 1, 100000, 50000, '筑基期', 12, 0, 0, 0, 0, 0, '{"beast_storage": 10, "beast_boost": 0.2}', 0, 0, 0, 0.0, 0, datetime('now')),
('七星佩', '北斗七星', 'accessory', '极品', 1, 0, 1, 120000, 60000, '筑基期', 15, 50, 50, 500, 300, 10, '{"star_blessing": true, "luck_boost": 0.2}', 0, 0, 0, 0.0, 0, datetime('now')),
('阴阳镜', '照妖镜', 'accessory', '上品', 1, 0, 1, 60000, 30000, '筑基期', 9, 20, 30, 300, 150, 5, '{"see_truth": true, "illusion_immune": true}', 0, 0, 0, 0.0, 0, datetime('now'));

-- 结丹期饰品 (4个)
INSERT INTO items (name, description, item_type, treasure_grade, is_tradable, is_stackable, max_stack, buy_price, sell_price, required_realm, required_level, attack_bonus, defense_bonus, hp_bonus, spiritual_bonus, speed_bonus, special_ability, hp_restore, spiritual_restore, exp_bonus, breakthrough_bonus, herb_age, created_at) VALUES
('乾坤戒', '内含小世界', 'accessory', '仙品', 1, 0, 1, 500000, 250000, '结丹期', 0, 50, 50, 1000, 500, 10, '{"storage_space": 1000, "time_space": 1.5}', 0, 0, 0, 0.0, 0, datetime('now')),
('混沌珠', '混沌至宝', 'accessory', '仙品', 0, 0, 1, 2000000, 1000000, '结丹期', 10, 200, 200, 5000, 2000, 50, '{"chaos_power": true, "world_inside": true}', 0, 0, 0, 0.0, 0, datetime('now')),
('山河社稷图', '内含山河', 'accessory', '仙品', 0, 0, 1, 3000000, 1500000, '结丹期', 15, 100, 500, 10000, 3000, 20, '{"world_map": true, "seal_enemy": true}', 0, 0, 0, 0.0, 0, datetime('now')),
('定海神针', '稳定空间', 'accessory', '仙品', 1, 0, 1, 800000, 400000, '结丹期', 8, 300, 200, 3000, 1000, 0, '{"space_anchor": true, "stabilize": true}', 0, 0, 0, 0.0, 0, datetime('now'));

-- 元婴期饰品 (1个)
INSERT INTO items (name, description, item_type, treasure_grade, is_tradable, is_stackable, max_stack, buy_price, sell_price, required_realm, required_level, attack_bonus, defense_bonus, hp_bonus, spiritual_bonus, speed_bonus, special_ability, hp_restore, spiritual_restore, exp_bonus, breakthrough_bonus, herb_age, created_at) VALUES
('河图洛书', '先天至宝', 'accessory', '仙品', 0, 0, 1, 10000000, 5000000, '元婴期', 0, 500, 500, 20000, 10000, 100, '{"destiny_control": true, "comprehension_boost": 50}', 0, 0, 0, 0.0, 0, datetime('now'));

-- 化神期饰品 (1个)
INSERT INTO items (name, description, item_type, treasure_grade, is_tradable, is_stackable, max_stack, buy_price, sell_price, required_realm, required_level, attack_bonus, defense_bonus, hp_bonus, spiritual_bonus, speed_bonus, special_ability, hp_restore, spiritual_restore, exp_bonus, breakthrough_bonus, herb_age, created_at) VALUES
('鸿蒙紫气', '开天功德', 'accessory', '仙品', 0, 0, 1, 50000000, 25000000, '化神期', 0, 1000, 1000, 50000, 50000, 200, '{"hongmeng_power": true, "merit_protection": true, "saint_path": true}', 0, 0, 0, 0.0, 0, datetime('now'));

-- ============================================
-- 宝物类 (10个)
-- ============================================

INSERT INTO items (name, description, item_type, treasure_grade, is_tradable, is_stackable, max_stack, buy_price, sell_price, required_realm, required_level, attack_bonus, defense_bonus, hp_bonus, spiritual_bonus, speed_bonus, special_ability, hp_restore, spiritual_restore, exp_bonus, breakthrough_bonus, herb_age, created_at) VALUES
('聚灵阵盘', '提升修炼速度的阵盘', 'treasure', '中品', 1, 0, 1, 10000, 5000, '炼气期', 10, 0, 0, 0, 0, 0, '{"cultivation_speed": 1.5}', 0, 0, 0, 0.0, 0, datetime('now')),
('传送符', '一次性传送符', 'treasure', '中品', 1, 1, 99, 5000, 2500, '炼气期', 5, 0, 0, 0, 0, 0, '{"teleport": true, "one_time": true}', 0, 0, 0, 0.0, 0, datetime('now')),
('替死傀儡', '代替死亡一次', 'treasure', '上品', 1, 1, 10, 50000, 25000, '筑基期', 0, 0, 0, 0, 0, 0, '{"substitute_death": true, "one_time": true}', 0, 0, 0, 0.0, 0, datetime('now')),
('天机罗盘', '推演天机', 'treasure', '极品', 1, 0, 1, 200000, 100000, '结丹期', 0, 0, 0, 0, 0, 0, '{"divination": true, "danger_warning": true}', 0, 0, 0, 0.0, 0, datetime('now')),
('炼丹炉', '提升炼丹成功率', 'treasure', '上品', 1, 0, 1, 100000, 50000, '筑基期', 0, 0, 0, 0, 0, 0, '{"alchemy_boost": 0.3}', 0, 0, 0, 0.0, 0, datetime('now')),
('炼器炉', '提升炼器成功率', 'treasure', '上品', 1, 0, 1, 100000, 50000, '筑基期', 0, 0, 0, 0, 0, 0, '{"refining_boost": 0.3}', 0, 0, 0, 0.0, 0, datetime('now')),
('灵田', '种植灵药的灵田', 'treasure', '中品', 1, 0, 1, 50000, 25000, '筑基期', 0, 0, 0, 0, 0, 0, '{"grow_herbs": true, "speed_boost": 2.0}', 0, 0, 0, 0.0, 0, datetime('now')),
('养魂木', '温养元神', 'treasure', '极品', 1, 0, 1, 300000, 150000, '结丹期', 0, 0, 0, 0, 500, 0, '{"soul_nourish": true, "divine_sense_boost": 100}', 0, 0, 0, 0.0, 0, datetime('now')),
('悟道茶树', '增加悟性', 'treasure', '仙品', 0, 0, 1, 5000000, 2500000, '元婴期', 0, 0, 0, 0, 0, 0, '{"enlightenment": true, "comprehension_boost": 30}', 0, 0, 0, 0.0, 0, datetime('now')),
('混沌灵根', '先天灵根', 'treasure', '仙品', 0, 0, 1, 100000000, 50000000, '化神期', 0, 0, 0, 0, 0, 0, '{"root_upgrade": true, "purity_max": true}', 0, 0, 0, 0.0, 0, datetime('now'));

-- 统计信息
-- 丹药: 50个
-- 材料: 80个（草药30 + 矿石25 + 妖兽25）
-- 武器: 40个
-- 防具: 30个
-- 饰品: 20个
-- 宝物: 10个
-- 总计: 230个物品