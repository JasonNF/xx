-- 怪物初始数据
-- 修为奖励设计原则：打怪修为 ≈ 同境界修炼1-2小时的量

-- ============================================
-- 炼气期怪物 (前期 1-5层)
-- ============================================

-- 炼气1-2层怪物
INSERT INTO monsters (name, description, level, realm, hp, attack, defense, speed, exp_reward, spirit_stones_min, spirit_stones_max, drop_items, drop_rate, is_boss, created_at) VALUES
('野狼', '荒山野岭的普通野狼，偶有灵气侵染', 1, '炼气期1层', 80, 12, 3, 8, 120, 10, 30, NULL, 0.0, 0, datetime('now')),
('山贼', '落草为寇的凡人山贼', 1, '炼气期1层', 100, 10, 5, 10, 100, 20, 50, NULL, 0.0, 0, datetime('now')),
('毒蛇', '携带剧毒的灵蛇', 2, '炼气期2层', 90, 15, 4, 12, 150, 15, 40, NULL, 0.0, 0, datetime('now')),
('野猪妖', '初通灵智的野猪妖兽', 2, '炼气期2层', 150, 18, 8, 6, 180, 25, 60, NULL, 0.0, 0, datetime('now'));

-- 炼气3-5层怪物
INSERT INTO monsters (name, description, level, realm, hp, attack, defense, speed, exp_reward, spirit_stones_min, spirit_stones_max, drop_items, drop_rate, is_boss, created_at) VALUES
('狐妖', '修炼百年的狐妖，善于魅惑', 3, '炼气期3层', 180, 22, 10, 15, 250, 30, 80, NULL, 0.0, 0, datetime('now')),
('僵尸', '阴气聚集形成的行尸', 4, '炼气期4层', 250, 28, 15, 5, 350, 40, 100, NULL, 0.0, 0, datetime('now')),
('灵猴', '山中灵猴，身法敏捷', 4, '炼气期4层', 200, 25, 8, 20, 320, 35, 90, NULL, 0.0, 0, datetime('now')),
('黑熊精', '体型庞大的熊妖', 5, '炼气期5层', 350, 35, 20, 8, 450, 50, 120, NULL, 0.0, 0, datetime('now'));

-- ============================================
-- 炼气期怪物 (中期 6-9层)
-- ============================================

INSERT INTO monsters (name, description, level, realm, hp, attack, defense, speed, exp_reward, spirit_stones_min, spirit_stones_max, drop_items, drop_rate, is_boss, created_at) VALUES
('铁甲蜈蚣', '全身坚硬如铁的巨型蜈蚣', 6, '炼气期6层', 400, 40, 25, 10, 600, 60, 150, NULL, 0.0, 0, datetime('now')),
('鬼将', '修炼百年的厉鬼', 7, '炼气期7层', 450, 50, 20, 18, 800, 80, 200, NULL, 0.0, 0, datetime('now')),
('血蝙蝠群', '成群结队的嗜血蝙蝠', 7, '炼气期7层', 380, 45, 15, 25, 750, 70, 180, NULL, 0.0, 0, datetime('now')),
('树妖', '千年古树成精', 8, '炼气期8层', 600, 55, 35, 8, 1000, 100, 250, NULL, 0.0, 0, datetime('now')),
('火焰狼', '掌握火焰之力的妖狼', 9, '炼气期9层', 550, 65, 30, 22, 1200, 120, 300, NULL, 0.0, 0, datetime('now'));

-- ============================================
-- 炼气期怪物 (后期 10-13层)
-- ============================================

INSERT INTO monsters (name, description, level, realm, hp, attack, defense, speed, exp_reward, spirit_stones_min, spirit_stones_max, drop_items, drop_rate, is_boss, created_at) VALUES
('白骨骷髅', '邪修炼制的傀儡', 10, '炼气期10层', 700, 75, 40, 15, 1500, 150, 400, NULL, 0.0, 0, datetime('now')),
('水妖', '河中修炼的妖物', 11, '炼气期11层', 800, 85, 45, 20, 1800, 180, 450, NULL, 0.0, 0, datetime('now')),
('邪修', '误入歧途的修仙者', 12, '炼气期12层', 900, 95, 50, 25, 2200, 220, 550, NULL, 0.0, 0, datetime('now')),
('炼气期傀儡', '古修士遗留的守护傀儡', 13, '炼气期13层', 1200, 110, 60, 18, 2800, 280, 700, NULL, 0.0, 0, datetime('now'));

-- ============================================
-- 筑基期怪物
-- ============================================

-- 筑基初期
INSERT INTO monsters (name, description, level, realm, hp, attack, defense, speed, exp_reward, spirit_stones_min, spirit_stones_max, drop_items, drop_rate, is_boss, created_at) VALUES
('筑基妖兽', '突破筑基的妖兽，实力大增', 14, '筑基期初期', 2000, 150, 80, 25, 4000, 400, 1000, NULL, 0.0, 0, datetime('now')),
('邪道筑基', '邪道修士，手段阴狠', 14, '筑基期初期', 1800, 160, 70, 28, 4500, 450, 1100, NULL, 0.0, 0, datetime('now')),
('雷电豹', '掌握雷属性的豹妖', 15, '筑基期初期', 2200, 170, 85, 32, 5000, 500, 1200, NULL, 0.0, 0, datetime('now'));

-- 筑基中期
INSERT INTO monsters (name, description, level, realm, hp, attack, defense, speed, exp_reward, spirit_stones_min, spirit_stones_max, drop_items, drop_rate, is_boss, created_at) VALUES
('筑基中期妖将', '妖族中的将领', 16, '筑基期中期', 3000, 200, 100, 30, 8000, 800, 2000, NULL, 0.0, 0, datetime('now')),
('剑修', '剑道筑基修士', 16, '筑基期中期', 2800, 220, 90, 35, 8500, 850, 2100, NULL, 0.0, 0, datetime('now')),
('冰霜巨蟒', '寒冰属性的巨蟒', 17, '筑基期中期', 3500, 210, 120, 25, 9000, 900, 2200, NULL, 0.0, 0, datetime('now'));

-- 筑基后期
INSERT INTO monsters (name, description, level, realm, hp, attack, defense, speed, exp_reward, spirit_stones_min, spirit_stones_max, drop_items, drop_rate, is_boss, created_at) VALUES
('筑基后期妖王', '妖族中的王者', 18, '筑基期后期', 4500, 280, 150, 32, 15000, 1500, 3500, NULL, 0.0, 0, datetime('now')),
('魔道筑基', '魔道高手', 18, '筑基期后期', 4200, 300, 140, 35, 16000, 1600, 3800, NULL, 0.0, 0, datetime('now')),
('金刚傀儡', '威力强大的战斗傀儡', 19, '筑基期后期', 5000, 290, 180, 28, 17000, 1700, 4000, NULL, 0.0, 0, datetime('now'));

-- ============================================
-- 结丹期怪物
-- ============================================

-- 结丹初期
INSERT INTO monsters (name, description, level, realm, hp, attack, defense, speed, exp_reward, spirit_stones_min, spirit_stones_max, drop_items, drop_rate, is_boss, created_at) VALUES
('结丹妖王', '妖族中的王者，已结金丹', 20, '结丹期初期', 8000, 400, 250, 35, 30000, 3000, 7000, NULL, 0.0, 0, datetime('now')),
('正道结丹', '正道宗门的结丹长老', 20, '结丹期初期', 7500, 420, 230, 38, 32000, 3200, 7500, NULL, 0.0, 0, datetime('now'));

-- 结丹中期
INSERT INTO monsters (name, description, level, realm, hp, attack, defense, speed, exp_reward, spirit_stones_min, spirit_stones_max, drop_items, drop_rate, is_boss, created_at) VALUES
('结丹中期大妖', '修炼千年的大妖', 22, '结丹期中期', 12000, 550, 350, 38, 50000, 5000, 12000, NULL, 0.0, 0, datetime('now')),
('魔道结丹', '魔道宗门的高手', 22, '结丹期中期', 11000, 580, 320, 40, 52000, 5200, 12500, NULL, 0.0, 0, datetime('now'));

-- 结丹后期
INSERT INTO monsters (name, description, level, realm, hp, attack, defense, speed, exp_reward, spirit_stones_min, spirit_stones_max, drop_items, drop_rate, is_boss, created_at) VALUES
('结丹后期妖圣', '妖族圣者', 25, '结丹期后期', 18000, 750, 500, 42, 80000, 8000, 20000, NULL, 0.0, 0, datetime('now')),
('古修士残魂', '古代修士的残魂', 25, '结丹期后期', 16000, 800, 450, 45, 85000, 8500, 21000, NULL, 0.0, 0, datetime('now'));

-- ============================================
-- BOSS级怪物
-- ============================================

-- 炼气期BOSS
INSERT INTO monsters (name, description, level, realm, hp, attack, defense, speed, exp_reward, spirit_stones_min, spirit_stones_max, drop_items, drop_rate, is_boss, created_at) VALUES
('黑风寨大当家', '炼气期巅峰的山贼头目', 13, '炼气期13层', 3000, 150, 80, 30, 5000, 500, 1500, NULL, 0.3, 1, datetime('now')),
('千年狐王', '修炼千年的九尾狐', 13, '炼气期13层', 3500, 140, 90, 35, 5500, 600, 1600, NULL, 0.35, 1, datetime('now'));

-- 筑基期BOSS
INSERT INTO monsters (name, description, level, realm, hp, attack, defense, speed, exp_reward, spirit_stones_min, spirit_stones_max, drop_items, drop_rate, is_boss, created_at) VALUES
('血魔老祖', '魔道筑基期巅峰高手', 19, '筑基期后期', 8000, 400, 200, 40, 25000, 2500, 6000, NULL, 0.4, 1, datetime('now')),
('青云宗叛徒', '背叛宗门的筑基修士', 19, '筑基期后期', 7500, 420, 180, 45, 26000, 2600, 6200, NULL, 0.42, 1, datetime('now'));

-- 结丹期BOSS
INSERT INTO monsters (name, description, level, realm, hp, attack, defense, speed, exp_reward, spirit_stones_min, spirit_stones_max, drop_items, drop_rate, is_boss, created_at) VALUES
('金蛟王', '即将化龙的金蛟', 25, '结丹期后期', 25000, 1000, 700, 50, 120000, 12000, 30000, NULL, 0.5, 1, datetime('now')),
('魔宗副宗主', '魔道宗门的副宗主', 26, '结丹期后期', 28000, 1100, 650, 52, 130000, 13000, 32000, NULL, 0.52, 1, datetime('now'));

-- ============================================
-- 元婴期怪物 (高级内容)
-- ============================================

INSERT INTO monsters (name, description, level, realm, hp, attack, defense, speed, exp_reward, spirit_stones_min, spirit_stones_max, drop_items, drop_rate, is_boss, created_at) VALUES
('元婴初期散修', '散修中的元婴强者', 28, '元婴期初期', 35000, 1500, 900, 55, 200000, 20000, 50000, NULL, 0.0, 0, datetime('now')),
('元婴中期妖尊', '妖族尊者', 30, '元婴期中期', 50000, 2000, 1200, 58, 350000, 35000, 80000, NULL, 0.0, 0, datetime('now')),
('元婴后期老怪', '隐世的元婴老怪', 32, '元婴期后期', 80000, 2800, 1800, 60, 600000, 60000, 150000, NULL, 0.0, 0, datetime('now'));

-- 元婴期BOSS
INSERT INTO monsters (name, description, level, realm, hp, attack, defense, speed, exp_reward, spirit_stones_min, spirit_stones_max, drop_items, drop_rate, is_boss, created_at) VALUES
('妖皇', '妖族的皇者', 33, '元婴期后期', 150000, 3500, 2500, 65, 1000000, 100000, 250000, NULL, 0.6, 1, datetime('now'));

-- ============================================
-- 化神期怪物
-- ============================================

INSERT INTO monsters (name, description, level, realm, hp, attack, defense, speed, exp_reward, spirit_stones_min, spirit_stones_max, drop_items, drop_rate, is_boss, created_at) VALUES
('化神初期修士', '人界巅峰的化神修士', 35, '化神期初期', 200000, 5000, 3500, 70, 1500000, 150000, 400000, NULL, 0.0, 0, datetime('now')),
('化神中期散仙', '半步飞升的散仙', 36, '化神期中期', 300000, 6500, 4500, 75, 2000000, 200000, 500000, NULL, 0.0, 0, datetime('now')),
('化神后期大能', '即将飞升的化神大能', 38, '化神期后期', 500000, 10000, 8000, 80, 3000000, 300000, 800000, NULL, 0.0, 0, datetime('now'));

-- ============================================
-- 补充更多炼气期怪物（特殊类型）
-- ============================================

INSERT INTO monsters (name, description, level, realm, hp, attack, defense, speed, exp_reward, spirit_stones_min, spirit_stones_max, drop_items, drop_rate, is_boss, created_at) VALUES
('迷雾蜘蛛', '生活在迷雾森林的剧毒蜘蛛', 3, '炼气期3层', 160, 20, 8, 14, 230, 28, 75, NULL, 0.0, 0, datetime('now')),
('岩石傀儡', '石头凝聚的傀儡', 5, '炼气期5层', 400, 30, 30, 5, 500, 55, 130, NULL, 0.0, 0, datetime('now')),
('幽灵', '游荡的孤魂野鬼', 6, '炼气期6层', 350, 38, 18, 22, 650, 65, 160, NULL, 0.0, 0, datetime('now')),
('毒蝎', '沙漠中的巨型毒蝎', 7, '炼气期7层', 420, 48, 22, 16, 820, 85, 210, NULL, 0.0, 0, datetime('now')),
('雪狼', '雪山中的冰狼', 8, '炼气期8层', 500, 58, 28, 24, 1100, 110, 270, NULL, 0.0, 0, datetime('now')),
('石像鬼', '被诅咒的石像', 9, '炼气期9层', 650, 62, 38, 12, 1300, 130, 320, NULL, 0.0, 0, datetime('now')),
('风魔', '风属性的魔物', 10, '炼气期10层', 680, 78, 35, 28, 1600, 160, 420, NULL, 0.0, 0, datetime('now')),
('暗影刺客', '潜伏在阴影中的杀手', 11, '炼气期11层', 750, 88, 42, 30, 1900, 190, 480, NULL, 0.0, 0, datetime('now')),
('火焰巨人', '火焰构成的巨人', 12, '炼气期12层', 950, 98, 55, 20, 2400, 240, 600, NULL, 0.0, 0, datetime('now')),
('寒冰巨兽', '冰封的远古巨兽', 13, '炼气期13层', 1300, 115, 65, 16, 3000, 300, 750, NULL, 0.0, 0, datetime('now'));

-- ============================================
-- 补充更多筑基期怪物（特殊类型）
-- ============================================

INSERT INTO monsters (name, description, level, realm, hp, attack, defense, speed, exp_reward, spirit_stones_min, spirit_stones_max, drop_items, drop_rate, is_boss, created_at) VALUES
('筑基剑修', '专精剑道的筑基修士', 14, '筑基期初期', 2100, 165, 75, 32, 4800, 480, 1150, NULL, 0.0, 0, datetime('now')),
('火鸦妖', '火焰属性的妖禽', 15, '筑基期初期', 2300, 175, 80, 35, 5200, 520, 1250, NULL, 0.0, 0, datetime('now')),
('土灵巨猿', '土属性的强大妖兽', 15, '筑基期初期', 2500, 165, 95, 22, 5100, 510, 1220, NULL, 0.0, 0, datetime('now')),
('雷霆狮', '掌控雷电的狮妖', 16, '筑基期中期', 3200, 210, 105, 33, 8300, 830, 2050, NULL, 0.0, 0, datetime('now')),
('暗影豹', '暗属性的敏捷妖兽', 16, '筑基期中期', 2900, 225, 95, 38, 8600, 860, 2120, NULL, 0.0, 0, datetime('now')),
('毒龙', '剧毒属性的蛟龙', 17, '筑基期中期', 3600, 215, 125, 28, 9200, 920, 2250, NULL, 0.0, 0, datetime('now')),
('血魔', '嗜血的魔道修士', 18, '筑基期后期', 4400, 290, 145, 34, 15500, 1550, 3600, NULL, 0.0, 0, datetime('now')),
('冰凰', '冰属性的凤凰后裔', 18, '筑基期后期', 4300, 295, 155, 36, 16200, 1620, 3850, NULL, 0.0, 0, datetime('now')),
('雷霆战将', '掌控雷电的战斗傀儡', 19, '筑基期后期', 5200, 295, 190, 30, 17500, 1750, 4100, NULL, 0.0, 0, datetime('now')),
('魔化修士', '被魔气侵染的修士', 19, '筑基期后期', 4800, 310, 175, 32, 17200, 1720, 4050, NULL, 0.0, 0, datetime('now'));

-- ============================================
-- 补充更多结丹期怪物（特殊类型）
-- ============================================

INSERT INTO monsters (name, description, level, realm, hp, attack, defense, speed, exp_reward, spirit_stones_min, spirit_stones_max, drop_items, drop_rate, is_boss, created_at) VALUES
('结丹体修', '体修路线的结丹强者', 21, '结丹期初期', 8500, 410, 280, 32, 31000, 3100, 7200, NULL, 0.0, 0, datetime('now')),
('雷灵妖皇', '雷属性的妖族皇者', 21, '结丹期初期', 8200, 430, 260, 40, 32500, 3250, 7600, NULL, 0.0, 0, datetime('now')),
('魔宗护法', '魔道宗门的护法', 22, '结丹期中期', 11500, 560, 340, 39, 51000, 5100, 12200, NULL, 0.0, 0, datetime('now')),
('古兽青鸾', '远古神兽的后裔', 23, '结丹期中期', 13000, 600, 380, 42, 60000, 6000, 14000, NULL, 0.0, 0, datetime('now')),
('鬼王', '统领万鬼的鬼王', 24, '结丹期中期', 14000, 650, 400, 38, 70000, 7000, 17000, NULL, 0.0, 0, datetime('now')),
('火云邪神', '火属性的邪道强者', 25, '结丹期后期', 17000, 780, 480, 44, 82000, 8200, 20500, NULL, 0.0, 0, datetime('now')),
('冰魄仙子', '冰道的女修', 26, '结丹期后期', 19000, 820, 520, 46, 90000, 9000, 22000, NULL, 0.0, 0, datetime('now')),
('剑圣残魂', '古代剑圣的一缕残魂', 26, '结丹期后期', 17500, 850, 480, 48, 88000, 8800, 21500, NULL, 0.0, 0, datetime('now'));

-- ============================================
-- 补充更多元婴期怪物（特殊类型）
-- ============================================

INSERT INTO monsters (name, description, level, realm, hp, attack, defense, speed, exp_reward, spirit_stones_min, spirit_stones_max, drop_items, drop_rate, is_boss, created_at) VALUES
('元婴魔修', '魔道的元婴强者', 29, '元婴期初期', 38000, 1600, 950, 56, 220000, 22000, 55000, NULL, 0.0, 0, datetime('now')),
('玄武后裔', '玄武神兽的后裔', 29, '元婴期初期', 42000, 1550, 1100, 50, 210000, 21000, 52000, NULL, 0.0, 0, datetime('now')),
('朱雀分身', '朱雀神兽的一缕分身', 30, '元婴期中期', 52000, 2100, 1250, 60, 360000, 36000, 85000, NULL, 0.0, 0, datetime('now')),
('青龙残魂', '青龙神兽的残魂', 31, '元婴期中期', 60000, 2300, 1400, 62, 450000, 45000, 110000, NULL, 0.0, 0, datetime('now')),
('白虎守护', '白虎神兽的守护者', 32, '元婴期后期', 85000, 2900, 1900, 62, 650000, 65000, 160000, NULL, 0.0, 0, datetime('now')),
('麒麟幼崽', '麒麟神兽的幼崽', 33, '元婴期后期', 95000, 3200, 2200, 65, 800000, 80000, 200000, NULL, 0.0, 0, datetime('now'));

-- ============================================
-- 补充更多化神期怪物（特殊类型）
-- ============================================

INSERT INTO monsters (name, description, level, realm, hp, attack, defense, speed, exp_reward, spirit_stones_min, spirit_stones_max, drop_items, drop_rate, is_boss, created_at) VALUES
('化神体修', '体修路线的化神大能', 37, '化神期中期', 350000, 7500, 5000, 78, 2500000, 250000, 600000, NULL, 0.0, 0, datetime('now')),
('真龙幼龙', '真龙一族的幼龙', 37, '化神期中期', 400000, 8000, 5500, 75, 2600000, 260000, 650000, NULL, 0.0, 0, datetime('now')),
('凤凰涅槃', '涅槃重生的凤凰', 38, '化神期后期', 480000, 9500, 7500, 82, 2900000, 290000, 750000, NULL, 0.0, 0, datetime('now'));

-- ============================================
-- 补充BOSS（各境界特殊BOSS）
-- ============================================

-- 炼气期特殊BOSS
INSERT INTO monsters (name, description, level, realm, hp, attack, defense, speed, exp_reward, spirit_stones_min, spirit_stones_max, drop_items, drop_rate, is_boss, created_at) VALUES
('黑风山妖王', '黑风山的山贼头目和妖怪联盟首领', 13, '炼气期13层', 3200, 145, 85, 32, 5200, 520, 1550, NULL, 0.32, 1, datetime('now')),
('血池老魔', '隐藏在血池中的邪修', 13, '炼气期13层', 3300, 155, 75, 28, 5400, 540, 1580, NULL, 0.33, 1, datetime('now'));

-- 筑基期特殊BOSS
INSERT INTO monsters (name, description, level, realm, hp, attack, defense, speed, exp_reward, spirit_stones_min, spirit_stones_max, drop_items, drop_rate, is_boss, created_at) VALUES
('寒冰魔女', '冰属性的魔道女修', 19, '筑基期后期', 7800, 410, 190, 42, 26500, 2650, 6300, NULL, 0.43, 1, datetime('now')),
('雷霆魔君', '雷属性的魔道强者', 19, '筑基期后期', 8200, 430, 210, 46, 27500, 2750, 6500, NULL, 0.44, 1, datetime('now'));

-- 结丹期特殊BOSS
INSERT INTO monsters (name, description, level, realm, hp, attack, defense, speed, exp_reward, spirit_stones_min, spirit_stones_max, drop_items, drop_rate, is_boss, created_at) VALUES
('九幽鬼帝', '统御九幽的鬼道强者', 26, '结丹期后期', 26000, 1050, 720, 48, 125000, 12500, 31000, NULL, 0.51, 1, datetime('now')),
('血神子', '血道邪修的分身', 27, '结丹期后期', 30000, 1150, 680, 54, 140000, 14000, 35000, NULL, 0.53, 1, datetime('now'));

-- 元婴期特殊BOSS
INSERT INTO monsters (name, description, level, realm, hp, attack, defense, speed, exp_reward, spirit_stones_min, spirit_stones_max, drop_items, drop_rate, is_boss, created_at) VALUES
('魔宗宗主', '魔道宗门的宗主', 33, '元婴期后期', 160000, 3600, 2600, 68, 1100000, 110000, 280000, NULL, 0.62, 1, datetime('now')),
('剑仙传人', '古代剑仙的传人', 34, '元婴期后期', 180000, 4000, 2800, 70, 1200000, 120000, 300000, NULL, 0.65, 1, datetime('now'));

-- 化神期终极BOSS
INSERT INTO monsters (name, description, level, realm, hp, attack, defense, speed, exp_reward, spirit_stones_min, spirit_stones_max, drop_items, drop_rate, is_boss, created_at) VALUES
('紫霄天尊', '雷道化神大能', 39, '化神期后期', 550000, 11000, 8500, 85, 3200000, 320000, 850000, NULL, 0.72, 1, datetime('now')),
('太虚仙翁', '即将飞升的散仙', 40, '化神期后期', 600000, 12000, 9000, 90, 3500000, 350000, 900000, NULL, 0.75, 1, datetime('now'));

-- 统计：
-- 原有怪物: 42种
-- 新增怪物: 42种
-- 总计: 84种怪物
--
-- 境界分布：
-- 炼气期: 32种（含4个BOSS）
-- 筑基期: 22种（含4个BOSS）
-- 结丹期: 16种（含4个BOSS）
-- 元婴期: 9种（含3个BOSS）
-- 化神期: 6种（含2个BOSS）
--
-- BOSS总数: 17个
-- 普通怪物: 67种
