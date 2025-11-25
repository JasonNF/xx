import re

# 读取原始SQL
with open('init_monsters.sql', 'r', encoding='utf-8') as f:
    lines = f.readlines()

output_lines = []
for line in lines:
    # 替换INSERT头
    if 'INSERT INTO monsters' in line and 'is_boss) VALUES' in line:
        line = line.replace('is_boss) VALUES', 'drop_items, drop_rate, is_boss, created_at) VALUES')
    
    # 处理VALUES行
    if line.strip().startswith('(') and line.strip().endswith(');'):
        # 这是一个完整的VALUES行
        if ', 0);' in line:
            # 普通怪物
            line = line.replace(', 0);', ', NULL, 0.0, 0, datetime(\'now\'));')
        elif ', 1);' in line:
            # BOSS怪物
            line = line.replace(', 1);', ', NULL, 0.3, 1, datetime(\'now\'));')
    
    output_lines.append(line)

# 写入新文件
with open('init_monsters_fixed.sql', 'w', encoding='utf-8') as f:
    f.writelines(output_lines)

print("✅ 已修复 init_monsters.sql")

# 统计怪物数量
monster_count = sum(1 for line in output_lines if line.strip().startswith('(\'') and 'datetime' in line)
print(f"📊 共 {monster_count} 个怪物")
