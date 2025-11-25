-- 宗门功法初始化数据
-- 为各大宗门配置专属功法
-- 不同职位可学习不同等级的功法
-- 注意: 运行此脚本前需要先执行 add_sect_fields_to_cultivation_methods.sql

-- ============================================
-- 黄枫谷功法 (sect_id=1, 假设)
-- 天南七派之一,以炼器闻名
-- ============================================

-- 外门弟子功法 (职位等级1)
INSERT INTO cultivation_methods (
    name, description, grade, method_type,
    cultivation_speed_bonus, attack_bonus, defense_bonus, hp_bonus,
    required_realm, required_level, learning_cost,
    sect_id, required_position_level
) VALUES (
    '黄枫基础剑诀',
    '黄枫谷外门弟子入门剑法,简单实用,适合初学者快速上手',
    '人级',
    '剑修',
    1.1,  -- 修炼速度 +10%
    15, 5, 50,
    'qi_refining', 1,
    500,  -- 500灵石
    1, 1  -- 黄枫谷, 外门弟子
);

-- 内门弟子功法 (职位等级2)
INSERT INTO cultivation_methods (
    name, description, grade, method_type,
    cultivation_speed_bonus, attack_bonus, defense_bonus, hp_bonus, spiritual_power_bonus,
    required_realm, required_level, learning_cost,
    sect_id, required_position_level
) VALUES (
    '青木长春功',
    '黄枫谷内门功法,以木属性灵气滋养肉身,延年益寿',
    '黄级',
    '通用',
    1.2,  -- 修炼速度 +20%
    25, 20, 100, 50,
    'qi_refining', 5,
    2000,
    1, 2  -- 黄枫谷, 内门弟子
);

-- 真传弟子功法 (职位等级3)
INSERT INTO cultivation_methods (
    name, description, grade, method_type,
    cultivation_speed_bonus, attack_bonus, defense_bonus, hp_bonus, spiritual_power_bonus,
    required_realm, required_level, learning_cost,
    sect_id, required_position_level
) VALUES (
    '青罡剑诀',
    '黄枫谷镇派剑诀之一,剑气凌厉,攻守兼备',
    '玄级',
    '剑修',
    1.3,  -- 修炼速度 +30%
    50, 30, 150, 80,
    'qi_refining', 10,
    8000,
    1, 3  -- 黄枫谷, 真传弟子
);

-- 长老功法 (职位等级6)
INSERT INTO cultivation_methods (
    name, description, grade, method_type,
    cultivation_speed_bonus, attack_bonus, defense_bonus, hp_bonus, spiritual_power_bonus,
    required_realm, required_level, learning_cost,
    sect_id, required_position_level
) VALUES (
    '青罡剑光',
    '青罡剑诀的进阶版,长老专修,剑光纵横,威力惊人',
    '地级',
    '剑修',
    1.5,  -- 修炼速度 +50%
    120, 80, 300, 200,
    'foundation', 5,
    50000,
    1, 6  -- 黄枫谷, 长老
);

-- ============================================
-- 灵兽山功法 (sect_id=2, 假设)
-- 天南七派之一,擅长御兽之道
-- ============================================

-- 外门弟子功法
INSERT INTO cultivation_methods (
    name, description, grade, method_type,
    cultivation_speed_bonus, attack_bonus, defense_bonus, hp_bonus,
    required_realm, required_level, learning_cost,
    sect_id, required_position_level
) VALUES (
    '驭兽入门心法',
    '灵兽山外门功法,修炼后可初步感应妖兽心意',
    '人级',
    '通用',
    1.05,
    10, 10, 80,
    'qi_refining', 1,
    500,
    2, 1  -- 灵兽山, 外门弟子
);

-- 内门弟子功法
INSERT INTO cultivation_methods (
    name, description, grade, method_type,
    cultivation_speed_bonus, attack_bonus, defense_bonus, hp_bonus, spiritual_power_bonus,
    required_realm, required_level, learning_cost,
    sect_id, required_position_level
) VALUES (
    '万兽同心诀',
    '灵兽山内门功法,可与灵兽心意相通,战力倍增',
    '黄级',
    '通用',
    1.15,
    20, 25, 120, 60,
    'qi_refining', 5,
    2000,
    2, 2  -- 灵兽山, 内门弟子
);

-- 真传弟子功法
INSERT INTO cultivation_methods (
    name, description, grade, method_type,
    cultivation_speed_bonus, attack_bonus, defense_bonus, hp_bonus, spiritual_power_bonus,
    required_realm, required_level, learning_cost,
    sect_id, required_position_level
) VALUES (
    '百兽朝宗功',
    '灵兽山镇派功法,修炼至高深处可同时御使百兽',
    '玄级',
    '通用',
    1.3,
    40, 40, 180, 100,
    'qi_refining', 10,
    8000,
    2, 3  -- 灵兽山, 真传弟子
);

-- 长老功法
INSERT INTO cultivation_methods (
    name, description, grade, method_type,
    cultivation_speed_bonus, attack_bonus, defense_bonus, hp_bonus, spiritual_power_bonus,
    required_realm, required_level, learning_cost,
    sect_id, required_position_level
) VALUES (
    '兽王变',
    '灵兽山长老专修秘法,可短暂化身兽王,战力暴涨',
    '地级',
    '通用',
    1.5,
    100, 100, 350, 250,
    'foundation', 5,
    50000,
    2, 6  -- 灵兽山, 长老
);

-- ============================================
-- 掩月宗功法 (sect_id=3, 假设)
-- 天南七派之一,擅长阵法和幻术
-- ============================================

-- 外门弟子功法
INSERT INTO cultivation_methods (
    name, description, grade, method_type,
    cultivation_speed_bonus, attack_bonus, defense_bonus, hp_bonus, spiritual_power_bonus,
    required_realm, required_level, learning_cost,
    sect_id, required_position_level
) VALUES (
    '月华凝神诀',
    '掩月宗外门功法,以月华精华滋养神识',
    '人级',
    '法修',
    1.08,
    8, 12, 60, 40,
    'qi_refining', 1,
    500,
    3, 1  -- 掩月宗, 外门弟子
);

-- 内门弟子功法
INSERT INTO cultivation_methods (
    name, description, grade, method_type,
    cultivation_speed_bonus, attack_bonus, defense_bonus, hp_bonus, spiritual_power_bonus,
    required_realm, required_level, learning_cost,
    sect_id, required_position_level
) VALUES (
    '月影幻术',
    '掩月宗内门功法,可施展月影分身,迷惑敌人',
    '黄级',
    '法修',
    1.2,
    30, 15, 100, 80,
    'qi_refining', 5,
    2000,
    3, 2  -- 掩月宗, 内门弟子
);

-- 真传弟子功法
INSERT INTO cultivation_methods (
    name, description, grade, method_type,
    cultivation_speed_bonus, attack_bonus, defense_bonus, hp_bonus, spiritual_power_bonus,
    required_realm, required_level, learning_cost,
    sect_id, required_position_level
) VALUES (
    '掩月大法',
    '掩月宗镇派功法,可布置幻阵困敌,攻守兼备',
    '玄级',
    '法修',
    1.35,
    60, 40, 150, 150,
    'qi_refining', 10,
    8000,
    3, 3  -- 掩月宗, 真传弟子
);

-- 长老功法
INSERT INTO cultivation_methods (
    name, description, grade, method_type,
    cultivation_speed_bonus, attack_bonus, defense_bonus, hp_bonus, spiritual_power_bonus,
    required_realm, required_level, learning_cost,
    sect_id, required_position_level
) VALUES (
    '月神降世',
    '掩月宗长老秘传,可短暂引动月神之力,实力暴增',
    '地级',
    '法修',
    1.6,
    150, 100, 300, 300,
    'foundation', 5,
    50000,
    3, 6  -- 掩月宗, 长老
);

-- ============================================
-- 巨剑门功法 (sect_id=4, 假设)
-- 天南七派之一,擅长巨剑之道
-- ============================================

-- 外门弟子功法
INSERT INTO cultivation_methods (
    name, description, grade, method_type,
    cultivation_speed_bonus, attack_bonus, defense_bonus, hp_bonus,
    required_realm, required_level, learning_cost,
    sect_id, required_position_level
) VALUES (
    '巨剑基础剑法',
    '巨剑门外门功法,以力破法,开大合大',
    '人级',
    '剑修',
    1.05,
    20, 5, 70,
    'qi_refining', 1,
    500,
    4, 1  -- 巨剑门, 外门弟子
);

-- 内门弟子功法
INSERT INTO cultivation_methods (
    name, description, grade, method_type,
    cultivation_speed_bonus, attack_bonus, defense_bonus, hp_bonus, spiritual_power_bonus,
    required_realm, required_level, learning_cost,
    sect_id, required_position_level
) VALUES (
    '霸剑诀',
    '巨剑门内门功法,剑势霸道,一剑破万法',
    '黄级',
    '剑修',
    1.15,
    40, 10, 150, 40,
    'qi_refining', 5,
    2000,
    4, 2  -- 巨剑门, 内门弟子
);

-- 真传弟子功法
INSERT INTO cultivation_methods (
    name, description, grade, method_type,
    cultivation_speed_bonus, attack_bonus, defense_bonus, hp_bonus, spiritual_power_bonus,
    required_realm, required_level, learning_cost,
    sect_id, required_position_level
) VALUES (
    '巨剑通天诀',
    '巨剑门镇派剑诀,一剑可开山裂地',
    '玄级',
    '剑修',
    1.25,
    80, 20, 200, 60,
    'qi_refining', 10,
    8000,
    4, 3  -- 巨剑门, 真传弟子
);

-- 长老功法
INSERT INTO cultivation_methods (
    name, description, grade, method_type,
    cultivation_speed_bonus, attack_bonus, defense_bonus, hp_bonus, spiritual_power_bonus,
    required_realm, required_level, learning_cost,
    sect_id, required_position_level
) VALUES (
    '开天巨剑',
    '巨剑门长老秘传,一剑可斩天地,威力无匹',
    '地级',
    '剑修',
    1.4,
    180, 50, 350, 150,
    'foundation', 5,
    50000,
    4, 6  -- 巨剑门, 长老
);

-- ============================================
-- 使用说明
-- ============================================

-- 1. sect_id需要根据实际数据库中的宗门ID进行调整
-- 2. required_position_level对应职位等级:
--    1=外门弟子, 2=内门弟子, 3=真传弟子, 4=执事, 5=堂主, 6=长老, 7=掌门
-- 3. learning_cost是学习功法需要消耗的灵石
-- 4. 功法效果随职位等级递增
-- 5. 学习后的功法永久保留,退出宗门后依然可用

-- 查询当前宗门ID的SQL:
-- SELECT id, name, level FROM sects ORDER BY id;

-- 查询某个宗门的所有功法:
-- SELECT name, grade, required_position_level, learning_cost
-- FROM cultivation_methods
-- WHERE sect_id = 1
-- ORDER BY required_position_level;

-- 查询玩家可学习的宗门功法:
-- SELECT cm.*
-- FROM cultivation_methods cm
-- JOIN players p ON p.sect_id = cm.sect_id
-- WHERE p.id = ? AND cm.required_position_level <= ?
-- ORDER BY cm.required_position_level;
