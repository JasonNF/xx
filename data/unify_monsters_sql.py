import re

# 读取原始SQL
with open('init_monsters.sql', 'r', encoding='utf-8') as f:
    content = f.read()

# 方案：统一所有INSERT为完整字段格式
# 1. 先替换有完整字段的INSERT（添加created_at）
content = re.sub(
    r'INSERT INTO monsters \(name, description, level, realm, hp, attack, defense, speed, exp_reward, spirit_stones_min, spirit_stones_max, drop_items, drop_rate, is_boss\) VALUES',
    r'INSERT INTO monsters (name, description, level, realm, hp, attack, defense, speed, exp_reward, spirit_stones_min, spirit_stones_max, drop_items, drop_rate, is_boss, created_at) VALUES',
    content
)

# 2. 替换缺少字段的INSERT（添加drop_items, drop_rate, created_at）
content = re.sub(
    r'INSERT INTO monsters \(name, description, level, realm, hp, attack, defense, speed, exp_reward, spirit_stones_min, spirit_stones_max, is_boss\) VALUES',
    r'INSERT INTO monsters (name, description, level, realm, hp, attack, defense, speed, exp_reward, spirit_stones_min, spirit_stones_max, drop_items, drop_rate, is_boss, created_at) VALUES',
    content
)

# 3. 对于缺少drop_items/drop_rate的行，添加NULL, 0.0
#    特征：倒数第二个值是is_boss（0或1），后面只有一个值（现在是created_at的占位）
# 模式: , 数字, 数字, 0或1), 或 0或1);
content = re.sub(r", (\d+), (0|1)\),", r", \1, NULL, 0.0, \2, datetime('now')),", content)
content = re.sub(r", (\d+), (0|1)\);", r", \1, NULL, 0.0, \2, datetime('now'));", content)

# 4. 对于已有drop_items/drop_rate的行，只添加created_at
#    特征：..., NULL或其他, 浮点数, 0或1), 或 0或1);
content = re.sub(r", (NULL|'[^']*'), ([\d.]+), (0|1)\),", r", \1, \2, \3, datetime('now')),", content)
content = re.sub(r", (NULL|'[^']*'), ([\d.]+), (0|1)\);", r", \1, \2, \3, datetime('now'));", content)

# 写入新文件
with open('init_monsters_fixed.sql', 'w', encoding='utf-8') as f:
    f.write(content)

# 统计怪物数量
monster_count = content.count("datetime('now')")
print(f"✅ 已统一并修复 init_monsters.sql，共 {monster_count} 个怪物")
