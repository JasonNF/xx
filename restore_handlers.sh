#!/bin/bash

#===============================================
# 恢复命令处理器 - 从备份中恢复
#===============================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  恢复命令处理器${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

HANDLERS_DIR="/opt/xiuxian-bot/src/bot/handlers"

echo -e "${YELLOW}1. 查找备份目录...${NC}"

# 找到最新的备份
BACKUP_DIR=$(ls -td /opt/xiuxian-bot-handlers-backup-* 2>/dev/null | head -1)

if [ -z "$BACKUP_DIR" ]; then
    echo -e "${RED}✗ 未找到备份目录${NC}"
    echo ""
    echo "可用的备份:"
    ls -lhd /opt/xiuxian-bot-handlers-backup-* 2>/dev/null || echo "  无备份"
    exit 1
fi

echo "找到备份: $BACKUP_DIR"
echo ""

echo -e "${YELLOW}2. 检查备份内容...${NC}"
ls -lh "$BACKUP_DIR"/*.py | wc -l
echo "  文件数量: $(ls "$BACKUP_DIR"/*.py 2>/dev/null | wc -l)"
echo ""

echo -e "${YELLOW}3. 恢复handler文件(保留chinese_commands.py)...${NC}"

# 备份当前的chinese_commands.py
if [ -f "$HANDLERS_DIR/chinese_commands.py" ]; then
    cp "$HANDLERS_DIR/chinese_commands.py" /tmp/chinese_commands.py.save
    echo "  ✓ 已保存 chinese_commands.py"
fi

# 恢复所有handler文件
cp -v "$BACKUP_DIR"/*.py "$HANDLERS_DIR/" 2>&1 | head -10

# 恢复chinese_commands.py
if [ -f /tmp/chinese_commands.py.save ]; then
    cp /tmp/chinese_commands.py.save "$HANDLERS_DIR/chinese_commands.py"
    echo "  ✓ 已恢复 chinese_commands.py"
fi

echo -e "${GREEN}✓ 文件已恢复${NC}"
echo ""

echo -e "${YELLOW}4. 只删除中文CommandHandler(保留英文)...${NC}"

# 使用Python精确删除中文CommandHandler
cat > /tmp/remove_only_chinese.py << 'PYEOF'
#!/usr/bin/env python3
import re
import os

def has_chinese(text):
    """检查是否包含中文"""
    return bool(re.search(r'[\u4e00-\u9fff]', text))

def remove_chinese_handlers(file_path):
    """只删除包含中文的CommandHandler行"""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    removed = 0

    for line in lines:
        # 只删除同时满足以下条件的行:
        # 1. 包含CommandHandler
        # 2. 包含中文字符
        if 'CommandHandler(' in line and has_chinese(line):
            print(f"删除: {line.strip()[:80]}")
            removed += 1
            continue
        new_lines.append(line)

    if removed > 0:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)

    return removed

handlers_dir = '/opt/xiuxian-bot/src/bot/handlers'
total = 0

for filename in os.listdir(handlers_dir):
    if filename.endswith('.py') and filename != 'chinese_commands.py':
        filepath = os.path.join(handlers_dir, filename)
        removed = remove_chinese_handlers(filepath)
        if removed > 0:
            print(f"  {filename}: 删除了 {removed} 行")
            total += removed

print(f"\n总计删除: {total} 行中文CommandHandler")
PYEOF

sudo -u xiuxian /opt/xiuxian-bot/venv/bin/python /tmp/remove_only_chinese.py

echo -e "${GREEN}✓ 中文CommandHandler已清理${NC}"
echo ""

echo -e "${YELLOW}5. 修正权限...${NC}"
chown -R xiuxian:xiuxian "$HANDLERS_DIR"
echo -e "${GREEN}✓ 权限已修正${NC}"

echo ""
echo -e "${YELLOW}6. 验证start.py中的命令...${NC}"
echo "英文CommandHandler:"
grep "CommandHandler(" "$HANDLERS_DIR/start.py" | grep -v "^#" | grep -v chinese | head -5

echo ""
echo -e "${YELLOW}7. 重启服务...${NC}"

systemctl restart xiuxian-bot

sleep 5

if systemctl is-active --quiet xiuxian-bot; then
    echo -e "${GREEN}✓ 服务运行正常!${NC}"

    echo ""
    echo "最近日志:"
    journalctl -u xiuxian-bot -n 20 --no-pager

else
    echo -e "${RED}✗ 服务启动失败${NC}"
    journalctl -u xiuxian-bot -n 30 --no-pager
    exit 1
fi

echo ""
echo "📊 实时监控: journalctl -u xiuxian-bot -f"
echo ""

# 清理临时文件
rm -f /tmp/remove_only_chinese.py /tmp/chinese_commands.py.save
