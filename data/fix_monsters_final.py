import re

# 读取原始SQL
with open('init_monsters.sql', 'r', encoding='utf-8') as f:
    content = f.read()

# 替换INSERT语句头（添加created_at字段）
content = re.sub(
    r'INSERT INTO monsters \(name, description, level, realm, hp, attack, defense, speed, exp_reward, spirit_stones_min, spirit_stones_max, drop_items, drop_rate, is_boss\) VALUES',
    r'INSERT INTO monsters (name, description, level, realm, hp, attack, defense, speed, exp_reward, spirit_stones_min, spirit_stones_max, drop_items, drop_rate, is_boss, created_at) VALUES',
    content
)

# 在每一行的结尾添加created_at
# 情况1: 以 , 0), 结尾
content = re.sub(r", 0\),(\s*)$", r", 0, datetime('now')),\1", content, flags=re.MULTILINE)

# 情况2: 以 , 0); 结尾
content = re.sub(r", 0\);(\s*)$", r", 0, datetime('now'));\1", content, flags=re.MULTILINE)

# 情况3: 以 , 1), 结尾
content = re.sub(r", 1\),(\s*)$", r", 1, datetime('now')),\1", content, flags=re.MULTILINE)

# 情况4: 以 , 1); 结尾
content = re.sub(r", 1\);(\s*)$", r", 1, datetime('now'));\1", content, flags=re.MULTILINE)

# 写入新文件
with open('init_monsters_fixed.sql', 'w', encoding='utf-8') as f:
    f.write(content)

# 统计怪物数量
monster_count = content.count("datetime('now')")
print(f"✅ 已修复 init_monsters.sql，共 {monster_count} 个怪物")
