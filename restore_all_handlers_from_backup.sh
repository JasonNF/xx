#!/bin/bash

#===============================================
# 从备份完全恢复所有handler文件
#===============================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  从备份恢复所有handlers${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

HANDLERS_DIR="/opt/xiuxian-bot/src/bot/handlers"

echo -e "${YELLOW}1. 查找最早的备份(应该是最完整的)...${NC}"

# 列出所有备份目录
echo "可用备份:"
ls -lhd /opt/xiuxian-bot-handlers-backup-* 2>/dev/null || echo "无备份"
echo ""

# 找到最早的备份（可能是最完整的，在我们开始删除之前）
BACKUP_DIR=$(ls -td /opt/xiuxian-bot-handlers-backup-* 2>/dev/null | tail -1)

if [ -z "$BACKUP_DIR" ]; then
    echo -e "${RED}✗ 未找到备份目录${NC}"
    exit 1
fi

echo "使用备份: $BACKUP_DIR"
echo "备份时间: $(basename $BACKUP_DIR | sed 's/.*-//')"
echo ""

echo -e "${YELLOW}2. 检查备份完整性...${NC}"

# 检查备份中start.py的CommandHandler数量
if [ -f "$BACKUP_DIR/start.py" ]; then
    cmd_count=$(grep -c "CommandHandler" "$BACKUP_DIR/start.py" 2>/dev/null || echo 0)
    echo "start.py 中的 CommandHandler 数量: $cmd_count"

    if [ "$cmd_count" -le 2 ]; then
        echo -e "${YELLOW}⚠ 这个备份可能不完整，尝试其他备份...${NC}"

        # 尝试倒数第二个备份
        BACKUP_DIR=$(ls -td /opt/xiuxian-bot-handlers-backup-* 2>/dev/null | tail -2 | head -1)
        echo "尝试备份: $BACKUP_DIR"

        if [ -f "$BACKUP_DIR/start.py" ]; then
            cmd_count=$(grep -c "CommandHandler" "$BACKUP_DIR/start.py" 2>/dev/null || echo 0)
            echo "start.py 中的 CommandHandler 数量: $cmd_count"
        fi
    fi
else
    echo -e "${RED}✗ 备份中没有start.py${NC}"
    exit 1
fi

if [ "$cmd_count" -le 2 ]; then
    echo -e "${RED}✗ 所有备份都不完整${NC}"
    echo ""
    echo "需要从源代码仓库恢复，或者手动编写CommandHandler"
    exit 1
fi

echo -e "${GREEN}✓ 备份完整${NC}"
echo ""

echo -e "${YELLOW}3. 保存chinese_commands.py...${NC}"
if [ -f "$HANDLERS_DIR/chinese_commands.py" ]; then
    cp "$HANDLERS_DIR/chinese_commands.py" /tmp/chinese_commands.py.save
    echo -e "${GREEN}✓ 已保存${NC}"
fi

echo ""
echo -e "${YELLOW}4. 恢复所有handler文件...${NC}"

# 删除当前handlers目录的所有.py文件（除了__init__.py）
find "$HANDLERS_DIR" -name "*.py" ! -name "__init__.py" -type f -delete

# 从备份恢复
cp -v "$BACKUP_DIR"/*.py "$HANDLERS_DIR/" | head -10
echo "..."
echo "共恢复 $(ls "$BACKUP_DIR"/*.py | wc -l) 个文件"

echo -e "${GREEN}✓ 已恢复${NC}"

echo ""
echo -e "${YELLOW}5. 恢复chinese_commands.py...${NC}"
if [ -f /tmp/chinese_commands.py.save ]; then
    cp /tmp/chinese_commands.py.save "$HANDLERS_DIR/chinese_commands.py"
    echo -e "${GREEN}✓ 已恢复${NC}"
fi

echo ""
echo -e "${YELLOW}6. 只删除中文CommandHandler（保留英文）...${NC}"

# 创建Python脚本来精确删除中文CommandHandler
sudo -u xiuxian /opt/xiuxian-bot/venv/bin/python << 'PYEOF'
import re
import os

def has_chinese(text):
    return bool(re.search(r'[\u4e00-\u9fff]', text))

handlers_dir = '/opt/xiuxian-bot/src/bot/handlers'
total_removed = 0

for filename in os.listdir(handlers_dir):
    if not filename.endswith('.py') or filename in ['chinese_commands.py', '__init__.py']:
        continue

    filepath = os.path.join(handlers_dir, filename)

    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    removed = 0

    for line in lines:
        # 只删除包含中文的CommandHandler行
        if 'CommandHandler(' in line and has_chinese(line):
            removed += 1
            continue
        new_lines.append(line)

    if removed > 0:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print(f"{filename}: 删除了 {removed} 个中文CommandHandler")
        total_removed += removed

print(f"\n总计删除: {total_removed} 个中文CommandHandler")
PYEOF

echo -e "${GREEN}✓ 清理完成${NC}"

echo ""
echo -e "${YELLOW}7. 验证start.py...${NC}"
echo ""
echo "register_handlers 函数:"
sed -n '/^def register_handlers/,/^def /p' "$HANDLERS_DIR/start.py" | head -15

echo ""
echo "CommandHandler 注册:"
grep "CommandHandler" "$HANDLERS_DIR/start.py" | grep -v "^#" | grep -v "import" | head -5

echo ""
echo -e "${YELLOW}8. 修正权限...${NC}"
chown -R xiuxian:xiuxian "$HANDLERS_DIR"
echo -e "${GREEN}✓ 权限已修正${NC}"

echo ""
echo -e "${YELLOW}9. 重启服务...${NC}"

systemctl restart xiuxian-bot

sleep 5

if systemctl is-active --quiet xiuxian-bot; then
    echo -e "${GREEN}✓ 服务运行正常!${NC}"

    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  恢复完成!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "🎮 测试命令:"
    echo "  /start"
    echo "  .开始"
    echo "  /help"
    echo "  .帮助"
    echo ""

    journalctl -u xiuxian-bot -n 20 --no-pager

else
    echo -e "${RED}✗ 服务启动失败${NC}"
    journalctl -u xiuxian-bot -n 30 --no-pager
    exit 1
fi

echo ""
echo "📊 实时监控: journalctl -u xiuxian-bot -f"
echo ""
