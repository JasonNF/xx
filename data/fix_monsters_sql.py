import re

# 读取原始SQL
with open('init_monsters.sql', 'r', encoding='utf-8') as f:
    content = f.read()

# 替换INSERT语句
# 模式: INSERT INTO monsters (...) VALUES
content = re.sub(
    r'INSERT INTO monsters \(name, description, level, realm, hp, attack, defense, speed, exp_reward, spirit_stones_min, spirit_stones_max, is_boss\) VALUES',
    r'INSERT INTO monsters (name, description, level, realm, hp, attack, defense, speed, exp_reward, spirit_stones_min, spirit_stones_max, drop_items, drop_rate, is_boss, created_at) VALUES',
    content
)

# 替换所有的行尾 , 0); 为 , NULL, 0.0, 0, datetime('now'));
content = re.sub(r", 0\);$", ", NULL, 0.0, 0, datetime('now'));", content, flags=re.MULTILINE)

# 替换所有的行尾 , 1); 为 , NULL, 0.3, 1, datetime('now'));
content = re.sub(r", 1\);$", ", NULL, 0.3, 1, datetime('now'));", content, flags=re.MULTILINE)

# 写入新文件
with open('init_monsters_fixed.sql', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ 已修复 init_monsters.sql")
