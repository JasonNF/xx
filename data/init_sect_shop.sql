-- 宗门商店物品初始化
-- 为各大宗门配置商店可兑换物品
-- 注意: 运行此脚本前需要确保 items 表已有相关物品数据

-- ============================================
-- 黄枫谷商店 (sect_id=1, 假设)
-- ============================================

-- 基础丹药兑换
INSERT INTO sect_shop_items (sect_id, item_id, contribution_cost, stock, required_level)
SELECT 1, id, 100, -1, 1
FROM items
WHERE name = '回春丹'
AND NOT EXISTS (SELECT 1 FROM sect_shop_items WHERE sect_id = 1 AND item_id = items.id);

INSERT INTO sect_shop_items (sect_id, item_id, contribution_cost, stock, required_level)
SELECT 1, id, 150, -1, 1
FROM items
WHERE name = '聚灵丹'
AND NOT EXISTS (SELECT 1 FROM sect_shop_items WHERE sect_id = 1 AND item_id = items.id);

-- 筑基丹 (珍贵)
INSERT INTO sect_shop_items (sect_id, item_id, contribution_cost, stock, required_level)
SELECT 1, id, 5000, 5, 2
FROM items
WHERE name = '筑基丹'
AND NOT EXISTS (SELECT 1 FROM sect_shop_items WHERE sect_id = 1 AND item_id = items.id);

-- 凝金丹 (更珍贵)
INSERT INTO sect_shop_items (sect_id, item_id, contribution_cost, stock, required_level)
SELECT 1, id, 20000, 3, 3
FROM items
WHERE name = '凝金丹'
AND NOT EXISTS (SELECT 1 FROM sect_shop_items WHERE sect_id = 1 AND item_id = items.id);

-- ============================================
-- 灵兽山商店 (sect_id=2, 假设)
-- ============================================

-- 基础丹药
INSERT INTO sect_shop_items (sect_id, item_id, contribution_cost, stock, required_level)
SELECT 2, id, 100, -1, 1
FROM items
WHERE name = '回春丹'
AND NOT EXISTS (SELECT 1 FROM sect_shop_items WHERE sect_id = 2 AND item_id = items.id);

INSERT INTO sect_shop_items (sect_id, item_id, contribution_cost, stock, required_level)
SELECT 2, id, 150, -1, 1
FROM items
WHERE name = '聚灵丹'
AND NOT EXISTS (SELECT 1 FROM sect_shop_items WHERE sect_id = 2 AND item_id = items.id);

-- 筑基丹
INSERT INTO sect_shop_items (sect_id, item_id, contribution_cost, stock, required_level)
SELECT 2, id, 5000, 5, 2
FROM items
WHERE name = '筑基丹'
AND NOT EXISTS (SELECT 1 FROM sect_shop_items WHERE sect_id = 2 AND item_id = items.id);

-- ============================================
-- 通用商店物品配置函数
-- 为所有宗门添加基础物品
-- ============================================

-- 说明：以下物品会为所有宗门添加
-- 1. 回春丹 (100声望)
-- 2. 聚灵丹 (150声望)
-- 3. 筑基丹 (5000声望, 限量5个)
-- 4. 凝金丹 (20000声望, 限量3个)

-- 为黄枫谷(1)、灵兽山(2)、掩月宗(3)、巨剑门(4)、化刀坞(5)、鬼灵门(6) 等宗门添加基础物品

-- ============================================
-- 特殊功法材料 (高级宗门专属)
-- ============================================

-- 说明：
-- 宗门商店主要提供辅助物品(丹药、材料等)
-- 宗门功法通过"传功长老"系统学习，不在商店兑换
-- 玩家通过提升声望来晋升职位，从而解锁更高等级的功法

-- ============================================
-- 炼器/炼丹材料
-- ============================================

-- 寒铁矿石 (基础炼器材料)
INSERT INTO sect_shop_items (sect_id, item_id, contribution_cost, stock, required_level)
SELECT 1, id, 50, -1, 1
FROM items
WHERE name = '寒铁矿石'
AND NOT EXISTS (SELECT 1 FROM sect_shop_items WHERE sect_id = 1 AND item_id = items.id);

-- 妖兽皮 (基础炼器材料)
INSERT INTO sect_shop_items (sect_id, item_id, contribution_cost, stock, required_level)
SELECT 1, id, 40, -1, 1
FROM items
WHERE name = '妖兽皮'
AND NOT EXISTS (SELECT 1 FROM sect_shop_items WHERE sect_id = 1 AND item_id = items.id);

-- 青灵草 (基础炼丹材料)
INSERT INTO sect_shop_items (sect_id, item_id, contribution_cost, stock, required_level)
SELECT 1, id, 30, -1, 1
FROM items
WHERE name = '青灵草'
AND NOT EXISTS (SELECT 1 FROM sect_shop_items WHERE sect_id = 1 AND item_id = items.id);

-- ============================================
-- 使用说明
-- ============================================

-- 1. 此脚本需要在 init_mortal_data.py, init_alchemy_system.py, init_refinery_materials.sql 之后运行
-- 2. sect_id 需要根据实际数据库中的宗门ID进行调整
-- 3. 商店物品的 contribution_cost 是声望消耗
-- 4. stock = -1 表示无限库存
-- 5. required_level 是宗门等级要求(非职位等级)

-- 查询当前宗门ID的SQL:
-- SELECT id, name, level FROM sects ORDER BY id;

-- 查询可用物品的SQL:
-- SELECT id, name, item_type FROM items WHERE item_type IN ('PILL', 'ORE', 'MATERIAL') ORDER BY id;
