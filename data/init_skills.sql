-- 技能初始数据
-- 设计原则：每个元素8-10个技能，覆盖不同境界和用途

-- ============================================
-- 金系技能 (8个)
-- ============================================

-- 基础金系攻击技能
INSERT INTO skills (name, description, skill_type, element, base_power, damage_multiplier, spiritual_cost, cooldown_rounds, special_effects, required_realm, required_spirit_root, learning_cost) VALUES
('金刃斩', '凝聚金属性灵力化作锋利刃芒，造成1.2倍伤害', 'attack', '金', 50, 1.2, 10, 0, NULL, '炼气期', '金', 100),
('金光护体', '金属性防御法术，提升防御力', 'defense', '金', 0, 0.0, 20, 3, '{"defense_boost": 20, "duration": 2}', '炼气期', '金', 150),
('庚金剑气', '剑修基础技能，凝练剑气攻击敌人，1.4倍伤害', 'attack', '金', 80, 1.4, 18, 0, '{"crit_rate_boost": 0.05}', '炼气期', '金', 200),
('金刚不坏', '顶级防御技能，大幅提升防御和血量', 'defense', '金', 0, 0.0, 50, 5, '{"defense_boost": 50, "hp_shield": 200}', '筑基期', '金', 1000),
('七星剑阵', '剑阵攻击，连续七击，1.8倍伤害', 'attack', '金', 150, 1.8, 40, 2, '{"multi_hit": 7, "crit_damage_boost": 0.2}', '筑基期', '金', 1500),
('金刚伏魔剑', '金系顶级剑技，2.5倍伤害并附带破防', 'attack', '金', 300, 2.5, 80, 3, '{"armor_penetration": 0.3, "stun_chance": 0.1}', '结丹期', '金', 5000),
('万剑诀', '御使万剑攻击，3.0倍AOE伤害', 'attack', '金', 500, 3.0, 120, 4, '{"aoe": true, "crit_rate_boost": 0.15}', '元婴期', '金', 15000),
('太乙金光剑', '金系禁术，4.0倍单体毁灭伤害', 'attack', '金', 1000, 4.0, 200, 5, '{"true_damage": 0.2, "ignore_defense": 0.5}', '化神期', '金', 50000);

-- ============================================
-- 木系技能 (8个)
-- ============================================

INSERT INTO skills (name, element, description, damage_multiplier, spiritual_cost, required_realm, skill_type, cooldown_rounds, special_effects) VALUES
('藤蔓缠绕', '木', '召唤藤蔓缠住敌人，造成1.0倍伤害并减速', 1.0, 10, '炼气期', 'attack', 1, '{"slow": 0.2, "duration": 1}'),
('春生术', '木', '木系治疗法术，恢复生命值', 0.0, 15, '炼气期', 'heal', 2, '{"heal_amount": 100}'),
('木遁', '木', '利用木属性灵力提升闪避', 0.0, 20, '炼气期', 'buff', 3, '{"dodge_rate": 0.15, "duration": 2}'),
('青木长生诀', '木', '持续恢复生命值，3回合', 0.0, 35, '筑基期', 'heal', 4, '{"heal_per_turn": 80, "duration": 3}'),
('森罗万象', '木', '召唤森林之力束缚敌人，1.5倍伤害', 1.5, 45, '筑基期', 'attack', 2, '{"bind_chance": 0.3, "duration": 1}'),
('天木神雷', '木', '木系融合雷属性，2.2倍伤害', 2.2, 75, '结丹期', 'attack', 3, '{"element_fusion": "thunder", "paralyze_chance": 0.15}'),
('生生不息', '木', '木系禁术，完全恢复生命值', 0.0, 150, '元婴期', 'heal', 10, '{"full_heal": true, "remove_debuffs": true}'),
('青莲地心火', '木', '木火双属性禁术，3.5倍伤害', 3.5, 180, '化神期', 'attack', 5, '{"element_fusion": "fire", "burn_damage": 100}');

-- ============================================
-- 水系技能 (8个)
-- ============================================

INSERT INTO skills (name, element, description, damage_multiplier, spiritual_cost, required_realm, skill_type, cooldown_rounds, special_effects) VALUES
('水球术', '水', '基础水系攻击法术，1.1倍伤害', 1.1, 8, '炼气期', 'attack', 0, NULL),
('冰锥术', '水', '凝聚冰锥攻击敌人，1.3倍伤害并减速', 1.3, 12, '炼气期', 'attack', 0, '{"slow": 0.15}'),
('水镜术', '水', '水系防御技能，反弹部分伤害', 0.0, 25, '炼气期', 'defense', 3, '{"reflect_damage": 0.15, "duration": 2}'),
('寒冰箭雨', '水', '召唤冰箭雨攻击，1.6倍AOE伤害', 1.6, 40, '筑基期', 'attack', 2, '{"aoe": true, "freeze_chance": 0.2}'),
('玄冰护盾', '水', '冰属性防御罩，吸收伤害', 0.0, 50, '筑基期', 'defense', 4, '{"hp_shield": 300, "slow_attacker": 0.1}'),
('天一真水', '水', '至阴至寒的水系神通，2.5倍伤害', 2.5, 85, '结丹期', 'attack', 3, '{"freeze_chance": 0.4, "defense_reduction": 0.2}'),
('水龙吟', '水', '召唤水龙攻击，3.2倍伤害', 3.2, 130, '元婴期', 'attack', 4, '{"knock_back": true, "drown_effect": 0.2}'),
('弱水三千', '水', '水系禁术，AOE 4.0倍伤害并封印', 4.0, 220, '化神期', 'attack', 6, '{"aoe": true, "seal_chance": 0.3}');

-- ============================================
-- 火系技能 (8个)
-- ============================================

INSERT INTO skills (name, element, description, damage_multiplier, spiritual_cost, required_realm, skill_type, cooldown_rounds, special_effects) VALUES
('火球术', '火', '基础火系法术，1.2倍伤害', 1.2, 10, '炼气期', 'attack', 0, NULL),
('火墙术', '火', '召唤火墙阻挡敌人并造成持续伤害', 0.8, 15, '炼气期', 'attack', 2, '{"burn_damage": 20, "duration": 2}'),
('炎爆术', '火', '火球爆炸，1.5倍AOE伤害', 1.5, 20, '炼气期', 'attack', 1, '{"aoe": true, "burn_chance": 0.2}'),
('烈焰风暴', '火', '召唤火焰风暴，2.0倍AOE伤害', 2.0, 50, '筑基期', 'attack', 2, '{"aoe": true, "burn_damage": 40, "duration": 2}'),
('凤凰真火', '火', '传说中的凤凰之火，2.8倍单体伤害', 2.8, 90, '结丹期', 'attack', 3, '{"true_damage": 0.15, "burn_damage": 80}'),
('三昧真火', '火', '道家至高火焰，3.5倍伤害无视防御', 3.5, 140, '元婴期', 'attack', 4, '{"ignore_defense": 0.4, "burn_duration": 3}'),
('业火红莲', '火', '佛门业火，4.2倍毁灭伤害', 4.2, 200, '化神期', 'attack', 5, '{"purify_evil": true, "burn_soul": 0.3}'),
('火凤涅槃', '火', '凤凰涅槃重生，复活并恢复50%生命', 0.0, 250, '化神期', 'special', 20, '{"revive": true, "hp_restore": 0.5}');

-- ============================================
-- 土系技能 (8个)
-- ============================================

INSERT INTO skills (name, element, description, damage_multiplier, spiritual_cost, required_realm, skill_type, cooldown_rounds, special_effects) VALUES
('土刺术', '土', '从地面刺出土刺，1.1倍伤害', 1.1, 9, '炼气期', 'attack', 0, NULL),
('石肤术', '土', '土系防御法术，提升防御力', 0.0, 15, '炼气期', 'defense', 2, '{"defense_boost": 15, "duration": 2}'),
('陷地术', '土', '让敌人陷入泥沼，减速并造成1.2倍伤害', 1.2, 18, '炼气期', 'attack', 1, '{"slow": 0.25, "duration": 2}'),
('土墙术', '土', '召唤土墙防御，吸收大量伤害', 0.0, 35, '筑基期', 'defense', 4, '{"hp_shield": 400, "reflect_damage": 0.1}'),
('流沙地狱', '土', '召唤流沙困住敌人，1.8倍伤害', 1.8, 55, '筑基期', 'attack', 2, '{"bind_chance": 0.35, "defense_reduction": 0.15}'),
('厚土载物', '土', '土系顶级防御，大幅提升防御和生命', 0.0, 100, '结丹期', 'defense', 6, '{"defense_boost": 100, "max_hp_boost": 500}'),
('五岳镇压', '土', '召唤五岳之力镇压，3.0倍伤害', 3.0, 120, '元婴期', 'attack', 4, '{"stun_chance": 0.3, "armor_penetration": 0.25}'),
('后土神通', '土', '土系禁术，4.5倍毁灭伤害并封印', 4.5, 230, '化神期', 'attack', 6, '{"aoe": true, "seal_chance": 0.4, "true_damage": 0.25}');

-- ============================================
-- 雷系技能（变异灵根）(6个)
-- ============================================

INSERT INTO skills (name, element, description, damage_multiplier, spiritual_cost, required_realm, skill_type, cooldown_rounds, special_effects) VALUES
('雷击术', '雷', '召唤雷电攻击，1.4倍伤害', 1.4, 15, '炼气期', 'attack', 0, '{"paralyze_chance": 0.1}'),
('紫霄神雷', '雷', '雷系高级法术，2.2倍伤害并麻痹', 2.2, 60, '筑基期', 'attack', 2, '{"paralyze_chance": 0.25, "crit_rate_boost": 0.1}'),
('五雷正法', '雷', '召唤五道天雷，2.8倍AOE伤害', 2.8, 100, '结丹期', 'attack', 3, '{"aoe": true, "paralyze_chance": 0.3}'),
('九天应元雷', '雷', '九霄神雷，3.8倍单体伤害', 3.8, 160, '元婴期', 'attack', 4, '{"ignore_defense": 0.3, "chain_lightning": 2}'),
('神霄天劫', '雷', '雷系禁术，5.0倍毁灭伤害', 5.0, 250, '化神期', 'attack', 5, '{"true_damage": 0.4, "paralyze_duration": 2}'),
('雷遁', '雷', '雷系身法，大幅提升速度', 0.0, 40, '筑基期', 'buff', 3, '{"speed_boost": 50, "dodge_rate": 0.2, "duration": 2}');

-- ============================================
-- 冰系技能（变异灵根）(6个)
-- ============================================

INSERT INTO skills (name, element, description, damage_multiplier, spiritual_cost, required_realm, skill_type, cooldown_rounds, special_effects) VALUES
('寒冰箭', '冰', '冰属性攻击，1.3倍伤害并冰冻', 1.3, 13, '炼气期', 'attack', 0, '{"freeze_chance": 0.15}'),
('冰封千里', '冰', '大范围冰封，1.8倍AOE伤害', 1.8, 55, '筑基期', 'attack', 2, '{"aoe": true, "freeze_chance": 0.3, "slow": 0.3}'),
('玄冰牢笼', '冰', '冰牢困住敌人，持续伤害', 1.0, 45, '筑基期', 'attack', 3, '{"bind_chance": 0.4, "freeze_damage": 50, "duration": 2}'),
('极寒冰域', '冰', '召唤极寒领域，2.5倍AOE持续伤害', 2.5, 110, '结丹期', 'attack', 4, '{"aoe": true, "freeze_damage": 100, "duration": 3}'),
('永恒冰晶', '冰', '冰系禁术，4.0倍伤害并永久冰冻', 4.0, 180, '元婴期', 'attack', 5, '{"freeze_duration": 99, "shatter_damage": 1.5}'),
('绝对零度', '冰', '冰系终极禁术，5.5倍毁灭', 5.5, 280, '化神期', 'attack', 6, '{"instant_freeze": true, "aoe": true, "time_stop": 1}');

-- ============================================
-- 风系技能（变异灵根）(5个)
-- ============================================

INSERT INTO skills (name, element, description, damage_multiplier, spiritual_cost, required_realm, skill_type, cooldown_rounds, special_effects) VALUES
('风刃术', '风', '凝聚风刃攻击，1.2倍伤害', 1.2, 11, '炼气期', 'attack', 0, '{"crit_rate_boost": 0.05}'),
('疾风步', '风', '风系身法，提升速度和闪避', 0.0, 20, '炼气期', 'buff', 2, '{"speed_boost": 30, "dodge_rate": 0.15, "duration": 2}'),
('狂风暴', '风', '召唤狂风，2.0倍AOE伤害', 2.0, 50, '筑基期', 'attack', 2, '{"aoe": true, "knock_back": true}'),
('九天罡风', '风', '至强罡风，3.5倍伤害无视防御', 3.5, 140, '元婴期', 'attack', 4, '{"ignore_defense": 0.5, "armor_shred": 0.3}'),
('风神降世', '风', '风系禁术，4.8倍毁灭伤害', 4.8, 240, '化神期', 'attack', 5, '{"aoe": true, "speed_reduction": 0.5, "silence": 0.3}');

-- ============================================
-- 暗系技能（变异灵根）(5个)
-- ============================================

INSERT INTO skills (name, element, description, damage_multiplier, spiritual_cost, required_realm, skill_type, cooldown_rounds, special_effects) VALUES
('暗影箭', '暗', '暗属性攻击，1.3倍伤害', 1.3, 14, '炼气期', 'attack', 0, '{"blind_chance": 0.1}'),
('黑暗侵蚀', '暗', '暗属性持续伤害，腐蚀敌人', 1.5, 35, '筑基期', 'attack', 2, '{"corrosion_damage": 40, "duration": 3}'),
('暗影分身', '暗', '制造暗影分身混淆敌人', 0.0, 45, '筑基期', 'buff', 4, '{"dodge_rate": 0.3, "duration": 2, "illusion": true}'),
('吞噬黑洞', '暗', '召唤黑洞吞噬一切，3.0倍伤害', 3.0, 120, '元婴期', 'attack', 4, '{"absorb_hp": 0.3, "defense_ignore": 0.4}'),
('永夜降临', '暗', '暗系禁术，5.0倍AOE毁灭', 5.0, 260, '化神期', 'attack', 6, '{"aoe": true, "blind_duration": 3, "life_steal": 0.4}');

-- ============================================
-- 无属性技能（通用）(8个)
-- ============================================

INSERT INTO skills (name, element, description, damage_multiplier, spiritual_cost, required_realm, skill_type, cooldown_rounds, special_effects) VALUES
('基础剑术', '无', '基础剑术攻击，1.1倍伤害', 1.1, 5, '炼气期', 'attack', 0, NULL),
('灵力爆发', '无', '瞬间爆发灵力，1.6倍伤害', 1.6, 25, '炼气期', 'attack', 1, '{"crit_damage_boost": 0.2}'),
('护体灵光', '无', '灵力护体，提升防御', 0.0, 20, '炼气期', 'defense', 3, '{"defense_boost": 25, "duration": 2}'),
('御剑飞行', '无', '御剑攻击，2.0倍伤害', 2.0, 60, '筑基期', 'attack', 2, '{"flying": true, "crit_rate_boost": 0.1}'),
('法力风暴', '无', '无属性法力风暴，2.5倍AOE', 2.5, 90, '结丹期', 'attack', 3, '{"aoe": true, "spiritual_drain": 50}'),
('空间传送', '无', '短距离空间传送，闪避攻击', 0.0, 80, '元婴期', 'special', 5, '{"teleport": true, "invulnerable": 1}'),
('时光倒流', '无', '时间系禁术，恢复到3回合前状态', 0.0, 200, '化神期', 'special', 15, '{"time_reverse": 3, "hp_restore": true}'),
('元神出窍', '无', '元神攻击，4.0倍真实伤害', 4.0, 180, '元婴期', 'attack', 5, '{"true_damage": 0.5, "soul_damage": true}');

-- 统计：
-- 金系: 8个
-- 木系: 8个
-- 水系: 8个
-- 火系: 8个
-- 土系: 8个
-- 雷系: 6个（变异）
-- 冰系: 6个（变异）
-- 风系: 5个（变异）
-- 暗系: 5个（变异）
-- 无属性: 8个
-- 总计: 70个技能

-- 境界分布：
-- 炼气期: 35个
-- 筑基期: 20个
-- 结丹期: 8个
-- 元婴期: 10个
-- 化神期: 15个

-- 类型分布：
-- attack: 55个
-- defense: 10个
-- heal: 3个
-- buff: 4个
-- special: 5个
