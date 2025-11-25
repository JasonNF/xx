-- 技能初始数据 (完全匹配数据库schema)
-- 字段: name, description, skill_type, element, base_power, damage_multiplier, spiritual_cost,
-- cooldown_rounds, special_effects, required_realm, required_spirit_root, learning_cost

INSERT INTO skills (name, description, skill_type, element, base_power, damage_multiplier, spiritual_cost, cooldown_rounds, special_effects, required_realm, required_spirit_root, learning_cost, created_at) VALUES
('金刃斩', '凝聚金属性灵力化作锋利刃芒，造成1.2倍伤害', 'attack', '金', 50, 1.2, 10, 0, NULL, '炼气期', '金', 100, datetime('now'));

INSERT INTO skills (name, description, skill_type, element, base_power, damage_multiplier, spiritual_cost, cooldown_rounds, special_effects, required_realm, required_spirit_root, learning_cost, created_at) VALUES
('金光护体', '金属性防御法术，提升防御力', 'defense', '金', 0, 0.0, 20, 3, '{"defense_boost": 20, "duration": 2}', '炼气期', '金', 150, datetime('now'));

INSERT INTO skills (name, description, skill_type, element, base_power, damage_multiplier, spiritual_cost, cooldown_rounds, special_effects, required_realm, required_spirit_root, learning_cost, created_at) VALUES
('庚金剑气', '剑修基础技能，凝练剑气攻击敌人，1.4倍伤害', 'attack', '金', 80, 1.4, 18, 0, '{"crit_rate_boost": 0.05}', '炼气期', '金', 200, datetime('now'));

INSERT INTO skills (name, description, skill_type, element, base_power, damage_multiplier, spiritual_cost, cooldown_rounds, special_effects, required_realm, required_spirit_root, learning_cost, created_at) VALUES
('金刚不坏', '顶级防御技能，大幅提升防御和血量', 'defense', '金', 0, 0.0, 50, 5, '{"defense_boost": 50, "hp_shield": 200}', '筑基期', '金', 1000, datetime('now'));

INSERT INTO skills (name, description, skill_type, element, base_power, damage_multiplier, spiritual_cost, cooldown_rounds, special_effects, required_realm, required_spirit_root, learning_cost, created_at) VALUES
('七星剑阵', '剑阵攻击，连续七击，1.8倍伤害', 'attack', '金', 150, 1.8, 40, 2, '{"multi_hit": 7, "crit_damage_boost": 0.2}', '筑基期', '金', 1500, datetime('now'));

INSERT INTO skills (name, description, skill_type, element, base_power, damage_multiplier, spiritual_cost, cooldown_rounds, special_effects, required_realm, required_spirit_root, learning_cost, created_at) VALUES
('金刚伏魔剑', '金系顶级剑技，2.5倍伤害并附带破防', 'attack', '金', 300, 2.5, 80, 3, '{"armor_penetration": 0.3, "stun_chance": 0.1}', '结丹期', '金', 5000, datetime('now'));

INSERT INTO skills (name, description, skill_type, element, base_power, damage_multiplier, spiritual_cost, cooldown_rounds, special_effects, required_realm, required_spirit_root, learning_cost, created_at) VALUES
('万剑诀', '御使万剑攻击，3.0倍AOE伤害', 'attack', '金', 500, 3.0, 120, 4, '{"aoe": true, "crit_rate_boost": 0.15}', '元婴期', '金', 15000, datetime('now'));

INSERT INTO skills (name, description, skill_type, element, base_power, damage_multiplier, spiritual_cost, cooldown_rounds, special_effects, required_realm, required_spirit_root, learning_cost, created_at) VALUES
('太乙金光剑', '金系禁术，4.0倍单体毁灭伤害', 'attack', '金', 1000, 4.0, 200, 5, '{"true_damage": 0.2, "ignore_defense": 0.5}', '化神期', '金', 50000, datetime('now'));

INSERT INTO skills (name, description, skill_type, element, base_power, damage_multiplier, spiritual_cost, cooldown_rounds, special_effects, required_realm, required_spirit_root, learning_cost, created_at) VALUES
('藤蔓缠绕', '召唤藤蔓缠住敌人，造成1.0倍伤害并减速', 'attack', '木', 45, 1.0, 10, 1, '{"slow": 0.2, "duration": 1}', '炼气期', '木', 100, datetime('now'));

INSERT INTO skills (name, description, skill_type, element, base_power, damage_multiplier, spiritual_cost, cooldown_rounds, special_effects, required_realm, required_spirit_root, learning_cost, created_at) VALUES
('春生术', '木系治疗法术，恢复生命值', 'heal', '木', 0, 0.0, 15, 2, '{"heal_amount": 100}', '炼气期', '木', 120, datetime('now'));

INSERT INTO skills (name, description, skill_type, element, base_power, damage_multiplier, spiritual_cost, cooldown_rounds, special_effects, required_realm, required_spirit_root, learning_cost, created_at) VALUES
('木遁', '利用木属性灵力提升闪避', 'buff', '木', 0, 0.0, 20, 3, '{"dodge_rate": 0.15, "duration": 2}', '炼气期', '木', 150, datetime('now'));

INSERT INTO skills (name, description, skill_type, element, base_power, damage_multiplier, spiritual_cost, cooldown_rounds, special_effects, required_realm, required_spirit_root, learning_cost, created_at) VALUES
('青木长生诀', '持续恢复生命值，3回合', 'heal', '木', 0, 0.0, 35, 4, '{"heal_per_turn": 80, "duration": 3}', '筑基期', '木', 1000, datetime('now'));

INSERT INTO skills (name, description, skill_type, element, base_power, damage_multiplier, spiritual_cost, cooldown_rounds, special_effects, required_realm, required_spirit_root, learning_cost, created_at) VALUES
('森罗万象', '召唤森林之力束缚敌人，1.5倍伤害', 'attack', '木', 120, 1.5, 45, 2, '{"bind_chance": 0.3, "duration": 1}', '筑基期', '木', 1200, datetime('now'));

INSERT INTO skills (name, description, skill_type, element, base_power, damage_multiplier, spiritual_cost, cooldown_rounds, special_effects, required_realm, required_spirit_root, learning_cost, created_at) VALUES
('天木神雷', '木系融合雷属性，2.2倍伤害', 'attack', '木', 280, 2.2, 75, 3, '{"element_fusion": "thunder", "paralyze_chance": 0.15}', '结丹期', '木', 5000, datetime('now'));

INSERT INTO skills (name, description, skill_type, element, base_power, damage_multiplier, spiritual_cost, cooldown_rounds, special_effects, required_realm, required_spirit_root, learning_cost, created_at) VALUES
('生生不息', '木系禁术，完全恢复生命值', 'heal', '木', 0, 0.0, 150, 10, '{"full_heal": true, "remove_debuffs": true}', '元婴期', '木', 20000, datetime('now'));

INSERT INTO skills (name, description, skill_type, element, base_power, damage_multiplier, spiritual_cost, cooldown_rounds, special_effects, required_realm, required_spirit_root, learning_cost, created_at) VALUES
('青莲地心火', '木火双属性禁术，3.5倍伤害', 'attack', '木', 800, 3.5, 180, 5, '{"element_fusion": "fire", "burn_damage": 100}', '化神期', '木', 50000, datetime('now'));

INSERT INTO skills (name, description, skill_type, element, base_power, damage_multiplier, spiritual_cost, cooldown_rounds, special_effects, required_realm, required_spirit_root, learning_cost, created_at) VALUES
('水球术', '基础水系攻击法术，1.1倍伤害', 'attack', '水', 48, 1.1, 8, 0, NULL, '炼气期', '水', 100, datetime('now'));

INSERT INTO skills (name, description, skill_type, element, base_power, damage_multiplier, spiritual_cost, cooldown_rounds, special_effects, required_realm, required_spirit_root, learning_cost, created_at) VALUES
('冰锥术', '凝聚冰锥攻击敌人，1.3倍伤害并减速', 'attack', '水', 70, 1.3, 12, 0, '{"slow": 0.15}', '炼气期', '水', 150, datetime('now'));

INSERT INTO skills (name, description, skill_type, element, base_power, damage_multiplier, spiritual_cost, cooldown_rounds, special_effects, required_realm, required_spirit_root, learning_cost, created_at) VALUES
('水镜术', '水系防御技能，反弹部分伤害', 'defense', '水', 0, 0.0, 25, 3, '{"reflect_damage": 0.15, "duration": 2}', '炼气期', '水', 180, datetime('now'));

INSERT INTO skills (name, description, skill_type, element, base_power, damage_multiplier, spiritual_cost, cooldown_rounds, special_effects, required_realm, required_spirit_root, learning_cost, created_at) VALUES
('寒冰箭雨', '召唤冰箭雨攻击，1.6倍AOE伤害', 'attack', '水', 140, 1.6, 40, 2, '{"aoe": true, "freeze_chance": 0.2}', '筑基期', '水', 1200, datetime('now'));

INSERT INTO skills (name, description, skill_type, element, base_power, damage_multiplier, spiritual_cost, cooldown_rounds, special_effects, required_realm, required_spirit_root, learning_cost, created_at) VALUES
('玄冰护盾', '冰属性防御罩，吸收伤害', 'defense', '水', 0, 0.0, 50, 4, '{"hp_shield": 300, "slow_attacker": 0.1}', '筑基期', '水', 1500, datetime('now'));

INSERT INTO skills (name, description, skill_type, element, base_power, damage_multiplier, spiritual_cost, cooldown_rounds, special_effects, required_realm, required_spirit_root, learning_cost, created_at) VALUES
('天一真水', '至阴至寒的水系神通，2.5倍伤害', 'attack', '水', 320, 2.5, 85, 3, '{"freeze_chance": 0.4, "defense_reduction": 0.2}', '结丹期', '水', 5500, datetime('now'));

INSERT INTO skills (name, description, skill_type, element, base_power, damage_multiplier, spiritual_cost, cooldown_rounds, special_effects, required_realm, required_spirit_root, learning_cost, created_at) VALUES
('水龙吟', '召唤水龙攻击，3.2倍伤害', 'attack', '水', 600, 3.2, 130, 4, '{"knock_back": true, "drown_effect": 0.2}', '元婴期', '水', 18000, datetime('now'));

INSERT INTO skills (name, description, skill_type, element, base_power, damage_multiplier, spiritual_cost, cooldown_rounds, special_effects, required_realm, required_spirit_root, learning_cost, created_at) VALUES
('弱水三千', '水系禁术，AOE 4.0倍伤害并封印', 'attack', '水', 950, 4.0, 220, 6, '{"aoe": true, "seal_chance": 0.3}', '化神期', '水', 55000, datetime('now'));

INSERT INTO skills (name, description, skill_type, element, base_power, damage_multiplier, spiritual_cost, cooldown_rounds, special_effects, required_realm, required_spirit_root, learning_cost, created_at) VALUES
('火球术', '基础火系法术，1.2倍伤害', 'attack', '火', 52, 1.2, 10, 0, NULL, '炼气期', '火', 100, datetime('now'));

INSERT INTO skills (name, description, skill_type, element, base_power, damage_multiplier, spiritual_cost, cooldown_rounds, special_effects, required_realm, required_spirit_root, learning_cost, created_at) VALUES
('火墙术', '召唤火墙阻挡敌人并造成持续伤害', 'attack', '火', 40, 0.8, 15, 2, '{"burn_damage": 20, "duration": 2}', '炼气期', '火', 130, datetime('now'));

INSERT INTO skills (name, description, skill_type, element, base_power, damage_multiplier, spiritual_cost, cooldown_rounds, special_effects, required_realm, required_spirit_root, learning_cost, created_at) VALUES
('炎爆术', '火球爆炸，1.5倍AOE伤害', 'attack', '火', 85, 1.5, 20, 1, '{"aoe": true, "burn_chance": 0.2}', '炼气期', '火', 200, datetime('now'));

INSERT INTO skills (name, description, skill_type, element, base_power, damage_multiplier, spiritual_cost, cooldown_rounds, special_effects, required_realm, required_spirit_root, learning_cost, created_at) VALUES
('烈焰风暴', '召唤火焰风暴，2.0倍AOE伤害', 'attack', '火', 180, 2.0, 50, 2, '{"aoe": true, "burn_damage": 40, "duration": 2}', '筑基期', '火', 1300, datetime('now'));

INSERT INTO skills (name, description, skill_type, element, base_power, damage_multiplier, spiritual_cost, cooldown_rounds, special_effects, required_realm, required_spirit_root, learning_cost, created_at) VALUES
('凤凰真火', '传说中的凤凰之火，2.8倍单体伤害', 'attack', '火', 380, 2.8, 90, 3, '{"true_damage": 0.15, "burn_damage": 80}', '结丹期', '火', 6000, datetime('now'));

INSERT INTO skills (name, description, skill_type, element, base_power, damage_multiplier, spiritual_cost, cooldown_rounds, special_effects, required_realm, required_spirit_root, learning_cost, created_at) VALUES
('三昧真火', '道家至高火焰，3.5倍伤害无视防御', 'attack', '火', 700, 3.5, 140, 4, '{"ignore_defense": 0.4, "burn_duration": 3}', '元婴期', '火', 20000, datetime('now'));

INSERT INTO skills (name, description, skill_type, element, base_power, damage_multiplier, spiritual_cost, cooldown_rounds, special_effects, required_realm, required_spirit_root, learning_cost, created_at) VALUES
('业火红莲', '佛门业火，4.2倍毁灭伤害', 'attack', '火', 1050, 4.2, 200, 5, '{"purify_evil": true, "burn_soul": 0.3}', '化神期', '火', 60000, datetime('now'));

INSERT INTO skills (name, description, skill_type, element, base_power, damage_multiplier, spiritual_cost, cooldown_rounds, special_effects, required_realm, required_spirit_root, learning_cost, created_at) VALUES
('火凤涅槃', '凤凰涅槃重生，复活并恢复50%生命', 'special', '火', 0, 0.0, 250, 20, '{"revive": true, "hp_restore": 0.5}', '化神期', '火', 80000, datetime('now'));

INSERT INTO skills (name, description, skill_type, element, base_power, damage_multiplier, spiritual_cost, cooldown_rounds, special_effects, required_realm, required_spirit_root, learning_cost, created_at) VALUES
('土刺术', '从地面刺出土刺，1.1倍伤害', 'attack', '土', 49, 1.1, 9, 0, NULL, '炼气期', '土', 100, datetime('now'));

INSERT INTO skills (name, description, skill_type, element, base_power, damage_multiplier, spiritual_cost, cooldown_rounds, special_effects, required_realm, required_spirit_root, learning_cost, created_at) VALUES
('石肤术', '土系防御法术，提升防御力', 'defense', '土', 0, 0.0, 15, 2, '{"defense_boost": 15, "duration": 2}', '炼气期', '土', 120, datetime('now'));

INSERT INTO skills (name, description, skill_type, element, base_power, damage_multiplier, spiritual_cost, cooldown_rounds, special_effects, required_realm, required_spirit_root, learning_cost, created_at) VALUES
('陷地术', '让敌人陷入泥沼，减速并造成1.2倍伤害', 'attack', '土', 58, 1.2, 18, 1, '{"slow": 0.25, "duration": 2}', '炼气期', '土', 160, datetime('now'));

INSERT INTO skills (name, description, skill_type, element, base_power, damage_multiplier, spiritual_cost, cooldown_rounds, special_effects, required_realm, required_spirit_root, learning_cost, created_at) VALUES
('土墙术', '召唤土墙防御，吸收大量伤害', 'defense', '土', 0, 0.0, 35, 4, '{"hp_shield": 400, "reflect_damage": 0.1}', '筑基期', '土', 1100, datetime('now'));

INSERT INTO skills (name, description, skill_type, element, base_power, damage_multiplier, spiritual_cost, cooldown_rounds, special_effects, required_realm, required_spirit_root, learning_cost, created_at) VALUES
('流沙地狱', '召唤流沙困住敌人，1.8倍伤害', 'attack', '土', 160, 1.8, 55, 2, '{"bind_chance": 0.35, "defense_reduction": 0.15}', '筑基期', '土', 1400, datetime('now'));

INSERT INTO skills (name, description, skill_type, element, base_power, damage_multiplier, spiritual_cost, cooldown_rounds, special_effects, required_realm, required_spirit_root, learning_cost, created_at) VALUES
('厚土载物', '土系顶级防御，大幅提升防御和生命', 'defense', '土', 0, 0.0, 100, 6, '{"defense_boost": 100, "max_hp_boost": 500}', '结丹期', '土', 5800, datetime('now'));

INSERT INTO skills (name, description, skill_type, element, base_power, damage_multiplier, spiritual_cost, cooldown_rounds, special_effects, required_realm, required_spirit_root, learning_cost, created_at) VALUES
('五岳镇压', '召唤五岳之力镇压，3.0倍伤害', 'attack', '土', 550, 3.0, 120, 4, '{"stun_chance": 0.3, "armor_penetration": 0.25}', '元婴期', '土', 17000, datetime('now'));

INSERT INTO skills (name, description, skill_type, element, base_power, damage_multiplier, spiritual_cost, cooldown_rounds, special_effects, required_realm, required_spirit_root, learning_cost, created_at) VALUES
('后土神通', '土系禁术，4.5倍毁灭伤害并封印', 'attack', '土', 1100, 4.5, 230, 6, '{"aoe": true, "seal_chance": 0.4, "true_damage": 0.25}', '化神期', '土', 65000, datetime('now'));

INSERT INTO skills (name, description, skill_type, element, base_power, damage_multiplier, spiritual_cost, cooldown_rounds, special_effects, required_realm, required_spirit_root, learning_cost, created_at) VALUES
('雷击术', '召唤雷电攻击，1.4倍伤害', 'attack', '雷', 75, 1.4, 15, 0, '{"paralyze_chance": 0.1}', '炼气期', '雷', 200, datetime('now'));

INSERT INTO skills (name, description, skill_type, element, base_power, damage_multiplier, spiritual_cost, cooldown_rounds, special_effects, required_realm, required_spirit_root, learning_cost, created_at) VALUES
('紫霄神雷', '雷系高级法术，2.2倍伤害并麻痹', 'attack', '雷', 220, 2.2, 60, 2, '{"paralyze_chance": 0.25, "crit_rate_boost": 0.1}', '筑基期', '雷', 2000, datetime('now'));

INSERT INTO skills (name, description, skill_type, element, base_power, damage_multiplier, spiritual_cost, cooldown_rounds, special_effects, required_realm, required_spirit_root, learning_cost, created_at) VALUES
('五雷正法', '召唤五道天雷，2.8倍AOE伤害', 'attack', '雷', 400, 2.8, 100, 3, '{"aoe": true, "paralyze_chance": 0.3}', '结丹期', '雷', 7000, datetime('now'));

INSERT INTO skills (name, description, skill_type, element, base_power, damage_multiplier, spiritual_cost, cooldown_rounds, special_effects, required_realm, required_spirit_root, learning_cost, created_at) VALUES
('九天应元雷', '九霄神雷，3.8倍单体伤害', 'attack', '雷', 750, 3.8, 160, 4, '{"ignore_defense": 0.3, "chain_lightning": 2}', '元婴期', '雷', 25000, datetime('now'));

INSERT INTO skills (name, description, skill_type, element, base_power, damage_multiplier, spiritual_cost, cooldown_rounds, special_effects, required_realm, required_spirit_root, learning_cost, created_at) VALUES
('神霄天劫', '雷系禁术，5.0倍毁灭伤害', 'attack', '雷', 1300, 5.0, 250, 5, '{"true_damage": 0.4, "paralyze_duration": 2}', '化神期', '雷', 70000, datetime('now'));

INSERT INTO skills (name, description, skill_type, element, base_power, damage_multiplier, spiritual_cost, cooldown_rounds, special_effects, required_realm, required_spirit_root, learning_cost, created_at) VALUES
('雷遁', '雷系身法，大幅提升速度', 'buff', '雷', 0, 0.0, 40, 3, '{"speed_boost": 50, "dodge_rate": 0.2, "duration": 2}', '筑基期', '雷', 1800, datetime('now'));

INSERT INTO skills (name, description, skill_type, element, base_power, damage_multiplier, spiritual_cost, cooldown_rounds, special_effects, required_realm, required_spirit_root, learning_cost, created_at) VALUES
('寒冰箭', '冰属性攻击，1.3倍伤害并冰冻', 'attack', '冰', 68, 1.3, 13, 0, '{"freeze_chance": 0.15}', '炼气期', '冰', 180, datetime('now'));

INSERT INTO skills (name, description, skill_type, element, base_power, damage_multiplier, spiritual_cost, cooldown_rounds, special_effects, required_realm, required_spirit_root, learning_cost, created_at) VALUES
('冰封千里', '大范围冰封，1.8倍AOE伤害', 'attack', '冰', 170, 1.8, 55, 2, '{"aoe": true, "freeze_chance": 0.3, "slow": 0.3}', '筑基期', '冰', 1900, datetime('now'));

INSERT INTO skills (name, description, skill_type, element, base_power, damage_multiplier, spiritual_cost, cooldown_rounds, special_effects, required_realm, required_spirit_root, learning_cost, created_at) VALUES
('玄冰牢笼', '冰牢困住敌人，持续伤害', 'attack', '冰', 90, 1.0, 45, 3, '{"bind_chance": 0.4, "freeze_damage": 50, "duration": 2}', '筑基期', '冰', 1600, datetime('now'));

INSERT INTO skills (name, description, skill_type, element, base_power, damage_multiplier, spiritual_cost, cooldown_rounds, special_effects, required_realm, required_spirit_root, learning_cost, created_at) VALUES
('极寒冰域', '召唤极寒领域，2.5倍AOE持续伤害', 'attack', '冰', 350, 2.5, 110, 4, '{"aoe": true, "freeze_damage": 100, "duration": 3}', '结丹期', '冰', 6500, datetime('now'));

INSERT INTO skills (name, description, skill_type, element, base_power, damage_multiplier, spiritual_cost, cooldown_rounds, special_effects, required_realm, required_spirit_root, learning_cost, created_at) VALUES
('永恒冰晶', '冰系禁术，4.0倍伤害并永久冰冻', 'attack', '冰', 850, 4.0, 180, 5, '{"freeze_duration": 99, "shatter_damage": 1.5}', '元婴期', '冰', 28000, datetime('now'));

INSERT INTO skills (name, description, skill_type, element, base_power, damage_multiplier, spiritual_cost, cooldown_rounds, special_effects, required_realm, required_spirit_root, learning_cost, created_at) VALUES
('绝对零度', '冰系终极禁术，5.5倍毁灭', 'attack', '冰', 1400, 5.5, 280, 6, '{"instant_freeze": true, "aoe": true, "time_stop": 1}', '化神期', '冰', 75000, datetime('now'));

INSERT INTO skills (name, description, skill_type, element, base_power, damage_multiplier, spiritual_cost, cooldown_rounds, special_effects, required_realm, required_spirit_root, learning_cost, created_at) VALUES
('风刃术', '凝聚风刃攻击，1.2倍伤害', 'attack', '风', 55, 1.2, 11, 0, '{"crit_rate_boost": 0.05}', '炼气期', '风', 150, datetime('now'));

INSERT INTO skills (name, description, skill_type, element, base_power, damage_multiplier, spiritual_cost, cooldown_rounds, special_effects, required_realm, required_spirit_root, learning_cost, created_at) VALUES
('疾风步', '风系身法，提升速度和闪避', 'buff', '风', 0, 0.0, 20, 2, '{"speed_boost": 30, "dodge_rate": 0.15, "duration": 2}', '炼气期', '风', 170, datetime('now'));

INSERT INTO skills (name, description, skill_type, element, base_power, damage_multiplier, spiritual_cost, cooldown_rounds, special_effects, required_realm, required_spirit_root, learning_cost, created_at) VALUES
('狂风暴', '召唤狂风，2.0倍AOE伤害', 'attack', '风', 190, 2.0, 50, 2, '{"aoe": true, "knock_back": true}', '筑基期', '风', 1700, datetime('now'));

INSERT INTO skills (name, description, skill_type, element, base_power, damage_multiplier, spiritual_cost, cooldown_rounds, special_effects, required_realm, required_spirit_root, learning_cost, created_at) VALUES
('九天罡风', '至强罡风，3.5倍伤害无视防御', 'attack', '风', 720, 3.5, 140, 4, '{"ignore_defense": 0.5, "armor_shred": 0.3}', '元婴期', '风', 22000, datetime('now'));

INSERT INTO skills (name, description, skill_type, element, base_power, damage_multiplier, spiritual_cost, cooldown_rounds, special_effects, required_realm, required_spirit_root, learning_cost, created_at) VALUES
('风神降世', '风系禁术，4.8倍毁灭伤害', 'attack', '风', 1200, 4.8, 240, 5, '{"aoe": true, "speed_reduction": 0.5, "silence": 0.3}', '化神期', '风', 68000, datetime('now'));

INSERT INTO skills (name, description, skill_type, element, base_power, damage_multiplier, spiritual_cost, cooldown_rounds, special_effects, required_realm, required_spirit_root, learning_cost, created_at) VALUES
('暗影箭', '暗属性攻击，1.3倍伤害', 'attack', '暗', 66, 1.3, 14, 0, '{"blind_chance": 0.1}', '炼气期', '暗', 180, datetime('now'));

INSERT INTO skills (name, description, skill_type, element, base_power, damage_multiplier, spiritual_cost, cooldown_rounds, special_effects, required_realm, required_spirit_root, learning_cost, created_at) VALUES
('黑暗侵蚀', '暗属性持续伤害，腐蚀敌人', 'attack', '暗', 110, 1.5, 35, 2, '{"corrosion_damage": 40, "duration": 3}', '筑基期', '暗', 1500, datetime('now'));

INSERT INTO skills (name, description, skill_type, element, base_power, damage_multiplier, spiritual_cost, cooldown_rounds, special_effects, required_realm, required_spirit_root, learning_cost, created_at) VALUES
('暗影分身', '制造暗影分身混淆敌人', 'buff', '暗', 0, 0.0, 45, 4, '{"dodge_rate": 0.3, "duration": 2, "illusion": true}', '筑基期', '暗', 1800, datetime('now'));

INSERT INTO skills (name, description, skill_type, element, base_power, damage_multiplier, spiritual_cost, cooldown_rounds, special_effects, required_realm, required_spirit_root, learning_cost, created_at) VALUES
('吞噬黑洞', '召唤黑洞吞噬一切，3.0倍伤害', 'attack', '暗', 580, 3.0, 120, 4, '{"absorb_hp": 0.3, "defense_ignore": 0.4}', '元婴期', '暗', 23000, datetime('now'));

INSERT INTO skills (name, description, skill_type, element, base_power, damage_multiplier, spiritual_cost, cooldown_rounds, special_effects, required_realm, required_spirit_root, learning_cost, created_at) VALUES
('永夜降临', '暗系禁术，5.0倍AOE毁灭', 'attack', '暗', 1350, 5.0, 260, 6, '{"aoe": true, "blind_duration": 3, "life_steal": 0.4}', '化神期', '暗', 72000, datetime('now'));

INSERT INTO skills (name, description, skill_type, element, base_power, damage_multiplier, spiritual_cost, cooldown_rounds, special_effects, required_realm, required_spirit_root, learning_cost, created_at) VALUES
('基础剑术', '基础剑术攻击，1.1倍伤害', 'attack', '无', 46, 1.1, 5, 0, NULL, '炼气期', NULL, 50, datetime('now'));

INSERT INTO skills (name, description, skill_type, element, base_power, damage_multiplier, spiritual_cost, cooldown_rounds, special_effects, required_realm, required_spirit_root, learning_cost, created_at) VALUES
('灵力爆发', '瞬间爆发灵力，1.6倍伤害', 'attack', '无', 100, 1.6, 25, 1, '{"crit_damage_boost": 0.2}', '炼气期', NULL, 200, datetime('now'));

INSERT INTO skills (name, description, skill_type, element, base_power, damage_multiplier, spiritual_cost, cooldown_rounds, special_effects, required_realm, required_spirit_root, learning_cost, created_at) VALUES
('护体灵光', '灵力护体，提升防御', 'defense', '无', 0, 0.0, 20, 3, '{"defense_boost": 25, "duration": 2}', '炼气期', NULL, 180, datetime('now'));

INSERT INTO skills (name, description, skill_type, element, base_power, damage_multiplier, spiritual_cost, cooldown_rounds, special_effects, required_realm, required_spirit_root, learning_cost, created_at) VALUES
('御剑飞行', '御剑攻击，2.0倍伤害', 'attack', '无', 200, 2.0, 60, 2, '{"flying": true, "crit_rate_boost": 0.1}', '筑基期', NULL, 1500, datetime('now'));

INSERT INTO skills (name, description, skill_type, element, base_power, damage_multiplier, spiritual_cost, cooldown_rounds, special_effects, required_realm, required_spirit_root, learning_cost, created_at) VALUES
('法力风暴', '无属性法力风暴，2.5倍AOE', 'attack', '无', 330, 2.5, 90, 3, '{"aoe": true, "spiritual_drain": 50}', '结丹期', NULL, 6000, datetime('now'));

INSERT INTO skills (name, description, skill_type, element, base_power, damage_multiplier, spiritual_cost, cooldown_rounds, special_effects, required_realm, required_spirit_root, learning_cost, created_at) VALUES
('空间传送', '短距离空间传送，闪避攻击', 'special', '无', 0, 0.0, 80, 5, '{"teleport": true, "invulnerable": 1}', '元婴期', NULL, 18000, datetime('now'));

INSERT INTO skills (name, description, skill_type, element, base_power, damage_multiplier, spiritual_cost, cooldown_rounds, special_effects, required_realm, required_spirit_root, learning_cost, created_at) VALUES
('时光倒流', '时间系禁术，恢复到3回合前状态', 'special', '无', 0, 0.0, 200, 15, '{"time_reverse": 3, "hp_restore": true}', '化神期', NULL, 60000, datetime('now'));

INSERT INTO skills (name, description, skill_type, element, base_power, damage_multiplier, spiritual_cost, cooldown_rounds, special_effects, required_realm, required_spirit_root, learning_cost, created_at) VALUES
('元神出窍', '元神攻击，4.0倍真实伤害', 'attack', '无', 900, 4.0, 180, 5, '{"true_damage": 0.5, "soul_damage": true}', '元婴期', NULL, 25000, datetime('now'));

