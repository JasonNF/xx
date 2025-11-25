-- 为cultivation_methods表添加宗门功法字段
-- 用于支持宗门专属功法系统
-- 执行日期: 2025-11-25

-- 添加宗门ID字段 (NULL表示通用功法,非NULL表示宗门专属功法)
ALTER TABLE cultivation_methods ADD COLUMN sect_id INTEGER DEFAULT NULL REFERENCES sects(id);

-- 添加职位等级要求字段 (1-7: 外门弟子到掌门)
ALTER TABLE cultivation_methods ADD COLUMN required_position_level INTEGER DEFAULT NULL;

-- 创建索引以提升查询性能
CREATE INDEX IF NOT EXISTS idx_cultivation_methods_sect_id ON cultivation_methods(sect_id);

-- 说明:
-- 1. sect_id为NULL: 通用功法,任何人都可以学习(需满足其他条件)
-- 2. sect_id不为NULL: 宗门专属功法,只有对应宗门的成员可以学习
-- 3. required_position_level: 学习需要的职位等级
--    1=外门弟子, 2=内门弟子, 3=真传弟子, 4=执事, 5=堂主, 6=长老, 7=掌门
-- 4. 学习后的功法永久保留,退出宗门后依然可以使用
