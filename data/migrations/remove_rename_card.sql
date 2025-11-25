-- 移除改名卡商品
-- 原因：改名功能已从终生一次改为灵石直接购买（20,000灵石），不再需要改名卡

-- 将改名卡标记为不活跃（下架）
UPDATE credit_shop_items
SET is_active = 0,
    is_featured = 0,
    updated_at = CURRENT_TIMESTAMP
WHERE name = '改名卡'
  AND category = 'SPECIAL';

-- 说明：
-- 1. 不删除数据，保留历史购买记录
-- 2. 已购买的改名卡仍然有效，可以使用
-- 3. 新玩家无法再购买改名卡
-- 4. 改名现在统一使用 /改名 命令，消耗20,000灵石
