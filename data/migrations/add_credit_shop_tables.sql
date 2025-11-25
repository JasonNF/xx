-- 积分商城系统数据表迁移
-- 创建日期：2024-01-XX

-- ============================================
-- 1. 积分商城商品表
-- ============================================
CREATE TABLE IF NOT EXISTS credit_shop_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    category VARCHAR(50) NOT NULL,  -- CULTIVATION_METHOD, TREASURE, PILL, SPECIAL

    -- 关联物品ID（如果是已存在的物品）
    item_id INTEGER NULL,

    -- 价格（积分）
    credit_price INTEGER NOT NULL,

    -- 库存控制
    total_stock INTEGER NOT NULL DEFAULT -1,  -- -1=无限
    remaining_stock INTEGER NOT NULL DEFAULT -1,  -- -1=无限
    sold_count INTEGER NOT NULL DEFAULT 0,

    -- 限购
    purchase_limit_per_player INTEGER NOT NULL DEFAULT -1,  -- -1=不限购
    daily_purchase_limit INTEGER NOT NULL DEFAULT -1,  -- 每日限购

    -- 购买条件
    required_realm VARCHAR(50) NULL,
    required_level INTEGER NOT NULL DEFAULT 1,
    required_vip_level INTEGER NOT NULL DEFAULT 0,

    -- 折扣
    discount_rate FLOAT NOT NULL DEFAULT 1.0,  -- 折扣率 0.8=8折

    -- 特殊效果（JSON格式存储）
    special_effects TEXT NULL,

    -- 商品图标/标签
    icon VARCHAR(50) NULL,  -- emoji或图标
    tags VARCHAR(200) NULL,  -- 标签：热门,限时,稀有

    -- 状态
    is_active BOOLEAN NOT NULL DEFAULT 1,
    is_featured BOOLEAN NOT NULL DEFAULT 0,  -- 是否精选
    sort_order INTEGER NOT NULL DEFAULT 0,  -- 排序

    -- 时间限制
    available_from DATETIME NULL,  -- 上架时间
    available_until DATETIME NULL,  -- 下架时间

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (item_id) REFERENCES items(id)
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_credit_shop_items_category ON credit_shop_items(category);
CREATE INDEX IF NOT EXISTS idx_credit_shop_items_active ON credit_shop_items(is_active);
CREATE INDEX IF NOT EXISTS idx_credit_shop_items_featured ON credit_shop_items(is_featured);

-- ============================================
-- 2. 玩家积分记录表
-- ============================================
CREATE TABLE IF NOT EXISTS player_credit_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER NOT NULL,

    -- 积分变动
    credit_change INTEGER NOT NULL,  -- 正数=获得，负数=消耗
    credit_before INTEGER NOT NULL,  -- 变动前积分
    credit_after INTEGER NOT NULL,   -- 变动后积分

    -- 来源/原因
    credit_type VARCHAR(50) NOT NULL,  -- SIGN_IN, TASK_COMPLETION, PVP_WIN, etc.
    reason VARCHAR(200) NOT NULL,
    reference_id INTEGER NULL,  -- 关联ID（如商品ID、任务ID等）

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (player_id) REFERENCES players(id)
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_player_credit_records_player ON player_credit_records(player_id);
CREATE INDEX IF NOT EXISTS idx_player_credit_records_type ON player_credit_records(credit_type);
CREATE INDEX IF NOT EXISTS idx_player_credit_records_created ON player_credit_records(created_at);

-- ============================================
-- 3. 积分商城购买记录表
-- ============================================
CREATE TABLE IF NOT EXISTS credit_shop_purchases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER NOT NULL,
    shop_item_id INTEGER NOT NULL,

    -- 购买信息
    item_name VARCHAR(100) NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    credit_cost INTEGER NOT NULL,  -- 实际花费积分
    original_price INTEGER NOT NULL,  -- 原价

    -- 购买时玩家信息（快照）
    player_realm VARCHAR(50) NOT NULL,
    player_level INTEGER NOT NULL,

    purchased_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (player_id) REFERENCES players(id),
    FOREIGN KEY (shop_item_id) REFERENCES credit_shop_items(id)
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_credit_shop_purchases_player ON credit_shop_purchases(player_id);
CREATE INDEX IF NOT EXISTS idx_credit_shop_purchases_item ON credit_shop_purchases(shop_item_id);
CREATE INDEX IF NOT EXISTS idx_credit_shop_purchases_purchased ON credit_shop_purchases(purchased_at);

-- ============================================
-- 4. 玩家商城限购记录表
-- ============================================
CREATE TABLE IF NOT EXISTS player_credit_shop_limits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER NOT NULL,
    shop_item_id INTEGER NOT NULL,

    -- 购买统计
    total_purchased INTEGER NOT NULL DEFAULT 0,  -- 总购买次数
    last_purchase_date DATETIME NULL,  -- 最后购买时间
    daily_purchased INTEGER NOT NULL DEFAULT 0,  -- 今日购买次数
    daily_reset_date DATETIME NULL,  -- 每日重置日期

    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (player_id) REFERENCES players(id),
    FOREIGN KEY (shop_item_id) REFERENCES credit_shop_items(id),

    UNIQUE(player_id, shop_item_id)
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_player_credit_shop_limits_player ON player_credit_shop_limits(player_id);
CREATE INDEX IF NOT EXISTS idx_player_credit_shop_limits_item ON player_credit_shop_limits(shop_item_id);

-- ============================================
-- 说明
-- ============================================
-- 此迁移脚本创建了积分商城系统的所有必要数据表：
-- 1. credit_shop_items: 商城商品信息
-- 2. player_credit_records: 玩家积分变动记录
-- 3. credit_shop_purchases: 商城购买记录
-- 4. player_credit_shop_limits: 玩家限购记录
--
-- 执行此脚本后，还需要：
-- 1. 执行 init_credit_shop.sql 导入初始商品数据
-- 2. 确保 players 表已添加 credits 字段
