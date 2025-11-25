-- 宗门任务初始化数据
-- 包含日常任务、周常任务和特殊任务
-- 完成任务可获得宗门声望(contribution_reward)

-- ============================================
-- 日常宗门任务 (每日可重复)
-- ============================================

-- 日常任务1: 巡逻宗门
INSERT INTO quests (
    name, description, quest_type,
    objective_type, objective_target, objective_count,
    required_realm, required_level,
    exp_reward, spirit_stones_reward, contribution_reward,
    is_repeatable, cooldown_hours
) VALUES (
    '巡逻宗门',
    '在宗门范围内巡逻,维护宗门治安',
    'sect',
    'patrol', 'sect_area', 1,
    'qi_refining', 1,
    50, 20, 50,
    1, 24
);

-- 日常任务2: 采集灵草
INSERT INTO quests (
    name, description, quest_type,
    objective_type, objective_target, objective_count,
    required_realm, required_level,
    exp_reward, spirit_stones_reward, contribution_reward,
    is_repeatable, cooldown_hours
) VALUES (
    '采集灵草',
    '前往宗门灵田采集10株青灵草',
    'sect',
    'collect_item', 'qing_ling_grass', 10,
    'qi_refining', 1,
    40, 15, 50,
    1, 24
);

-- 日常任务3: 清理妖兽
INSERT INTO quests (
    name, description, quest_type,
    objective_type, objective_target, objective_count,
    required_realm, required_level,
    exp_reward, spirit_stones_reward, contribution_reward,
    is_repeatable, cooldown_hours
) VALUES (
    '清理妖兽',
    '击杀宗门附近的野生妖兽,保护宗门安全',
    'sect',
    'kill_monster', 'wild_beast', 5,
    'qi_refining', 3,
    60, 30, 50,
    1, 24
);

-- 日常任务4: 炼丹辅助
INSERT INTO quests (
    name, description, quest_type,
    objective_type, objective_target, objective_count,
    required_realm, required_level,
    exp_reward, spirit_stones_reward, contribution_reward,
    is_repeatable, cooldown_hours
) VALUES (
    '炼丹辅助',
    '协助炼丹房长老处理药材,辅助炼制丹药',
    'sect',
    'alchemy_assist', 'pill_house', 1,
    'qi_refining', 5,
    70, 25, 50,
    1, 24
);

-- 日常任务5: 炼器辅助
INSERT INTO quests (
    name, description, quest_type,
    objective_type, objective_target, objective_count,
    required_realm, required_level,
    exp_reward, spirit_stones_reward, contribution_reward,
    is_repeatable, cooldown_hours
) VALUES (
    '炼器辅助',
    '协助炼器阁长老锻造法器,学习炼器技艺',
    'sect',
    'refinery_assist', 'refinery_pavilion', 1,
    'qi_refining', 5,
    70, 25, 50,
    1, 24
);

-- ============================================
-- 周常宗门任务 (每周可重复)
-- ============================================

-- 周常任务1: 护送商队
INSERT INTO quests (
    name, description, quest_type,
    objective_type, objective_target, objective_count,
    required_realm, required_level,
    exp_reward, spirit_stones_reward, contribution_reward,
    is_repeatable, cooldown_hours
) VALUES (
    '护送商队',
    '护送宗门商队前往坊市,确保货物安全送达',
    'sect',
    'escort', 'sect_caravan', 1,
    'qi_refining', 5,
    200, 100, 200,
    1, 168
);

-- 周常任务2: 宗门大比
INSERT INTO quests (
    name, description, quest_type,
    objective_type, objective_target, objective_count,
    required_realm, required_level,
    exp_reward, spirit_stones_reward, contribution_reward,
    is_repeatable, cooldown_hours
) VALUES (
    '宗门大比',
    '参加宗门内部比武大会,提升实战经验',
    'sect',
    'sect_tournament', 'tournament_arena', 3,
    'qi_refining', 3,
    250, 150, 200,
    1, 168
);

-- 周常任务3: 探索秘境
INSERT INTO quests (
    name, description, quest_type,
    objective_type, objective_target, objective_count,
    required_realm, required_level,
    exp_reward, spirit_stones_reward, contribution_reward,
    is_repeatable, cooldown_hours
) VALUES (
    '探索秘境',
    '进入宗门秘境探索,寻找天材地宝',
    'sect',
    'explore_secret_realm', 'sect_secret_realm', 1,
    'foundation', 1,
    300, 200, 200,
    1, 168
);

-- 周常任务4: 宗门建设
INSERT INTO quests (
    name, description, quest_type,
    objective_type, objective_target, objective_count,
    required_realm, required_level,
    exp_reward, spirit_stones_reward, contribution_reward,
    is_repeatable, cooldown_hours
) VALUES (
    '宗门建设',
    '参与宗门建筑修缮和扩建工作',
    'sect',
    'construction', 'sect_buildings', 1,
    'qi_refining', 1,
    180, 80, 200,
    1, 168
);

-- ============================================
-- 特殊宗门任务 (高难度,高奖励)
-- ============================================

-- 特殊任务1: 击杀妖兽首领
INSERT INTO quests (
    name, description, quest_type,
    objective_type, objective_target, objective_count,
    required_realm, required_level,
    exp_reward, spirit_stones_reward, contribution_reward,
    is_repeatable, cooldown_hours
) VALUES (
    '击杀妖兽首领',
    '击杀威胁宗门的二阶妖兽首领',
    'sect',
    'kill_boss', 'beast_leader_tier2', 1,
    'foundation', 3,
    500, 300, 500,
    1, 720
);

-- 特殊任务2: 夺回失地
INSERT INTO quests (
    name, description, quest_type,
    objective_type, objective_target, objective_count,
    required_realm, required_level,
    exp_reward, spirit_stones_reward, contribution_reward,
    is_repeatable, cooldown_hours
) VALUES (
    '夺回失地',
    '参与宗门夺回被妖兽占据的灵石矿脉',
    'sect',
    'reclaim_territory', 'spirit_stone_mine', 1,
    'foundation', 5,
    800, 500, 500,
    1, 720
);

-- 特殊任务3: 秘境探宝
INSERT INTO quests (
    name, description, quest_type,
    objective_type, objective_target, objective_count,
    required_realm, required_level,
    exp_reward, spirit_stones_reward, contribution_reward,
    item_rewards,
    is_repeatable, cooldown_hours
) VALUES (
    '秘境探宝',
    '深入险恶秘境,寻找上古修士洞府',
    'sect',
    'treasure_hunt', 'ancient_cave', 1,
    'foundation', 7,
    1000, 800, 500,
    '[{"item_name": "筑基丹", "quantity": 1}]',
    1, 720
);

-- 特殊任务4: 护送长老
INSERT INTO quests (
    name, description, quest_type,
    objective_type, objective_target, objective_count,
    required_realm, required_level,
    exp_reward, spirit_stones_reward, contribution_reward,
    is_repeatable, cooldown_hours
) VALUES (
    '护送长老',
    '护送宗门长老前往其他门派参加修仙界盛会',
    'sect',
    'escort_elder', 'cultivation_world_gathering', 1,
    'foundation', 5,
    600, 400, 500,
    1, 720
);

-- ============================================
-- 宗门战争任务 (需要宗门战争系统支持)
-- ============================================

-- 宗门战争任务1: 参与宗门战
INSERT INTO quests (
    name, description, quest_type,
    objective_type, objective_target, objective_count,
    required_realm, required_level,
    exp_reward, spirit_stones_reward, contribution_reward,
    is_repeatable, cooldown_hours
) VALUES (
    '参与宗门战',
    '参加宗门之间的领地争夺战',
    'sect',
    'sect_war', 'territory_war', 1,
    'foundation', 1,
    1500, 1000, 1000,
    1, 720
);

-- ============================================
-- 使用说明
-- ============================================

-- 1. quest_type固定为'sect'(宗门任务)
-- 2. contribution_reward是完成任务获得的宗门声望
-- 3. is_repeatable=1表示可重复任务
-- 4. cooldown_hours是冷却时间(小时):
--    - 24小时 = 每日任务
--    - 168小时 = 每周任务
--    - 720小时 = 每月任务
-- 5. objective_type需要在任务系统中实现相应的检测逻辑
-- 6. 声望奖励建议:
--    - 日常任务: 50声望
--    - 周常任务: 200声望
--    - 特殊任务: 500-1000声望

-- 查询所有宗门任务:
-- SELECT * FROM quests WHERE quest_type = 'sect' ORDER BY is_repeatable DESC, contribution_reward DESC;
