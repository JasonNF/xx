#!/bin/bash

#===============================================
# 最终清理：彻底删除所有中文CommandHandler
#===============================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  彻底清理中文CommandHandler${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

HANDLERS_DIR="/opt/xiuxian-bot/src/bot/handlers"

echo -e "${YELLOW}1. 备份handlers目录...${NC}"
BACKUP_DIR="/opt/xiuxian-bot-handlers-backup-$(date +%Y%m%d_%H%M%S)"
cp -r "$HANDLERS_DIR" "$BACKUP_DIR"
echo -e "${GREEN}✓ 备份到: $BACKUP_DIR${NC}"

echo ""
echo -e "${YELLOW}2. 扫描并删除所有中文CommandHandler...${NC}"
echo ""

# 使用Python脚本进行精确清理
sudo -u xiuxian /opt/xiuxian-bot/venv/bin/python3 << 'PYEOF'
import os
import re

handlers_dir = '/opt/xiuxian-bot/src/bot/handlers'

def has_chinese(text):
    """检查文本是否包含中文字符"""
    return bool(re.search(r'[\u4e00-\u9fff]', text))

total_removed = 0
files_modified = []

for filename in os.listdir(handlers_dir):
    # 跳过特殊文件
    if not filename.endswith('.py') or filename in ['chinese_commands.py', '__init__.py']:
        continue

    filepath = os.path.join(handlers_dir, filename)

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"❌ 读取失败 {filename}: {e}")
        continue

    new_lines = []
    removed = 0

    for line in lines:
        # 只删除包含中文的CommandHandler行
        if 'CommandHandler(' in line and has_chinese(line):
            # 显示被删除的内容（截断到80字符）
            preview = line.strip()[:80]
            print(f"  删除 {filename}: {preview}")
            removed += 1
            continue

        new_lines.append(line)

    # 如果有修改，写回文件
    if removed > 0:
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            files_modified.append(filename)
            total_removed += removed
            print(f"✓ {filename}: 删除了 {removed} 个中文CommandHandler\n")
        except Exception as e:
            print(f"❌ 写入失败 {filename}: {e}\n")

print(f"\n{'='*50}")
print(f"总结:")
print(f"  修改文件数: {len(files_modified)}")
print(f"  删除总数: {total_removed} 个中文CommandHandler")
print(f"{'='*50}\n")

if files_modified:
    print("修改的文件:")
    for f in files_modified:
        print(f"  - {f}")
PYEOF

echo ""
echo -e "${GREEN}✓ 清理完成${NC}"

echo ""
echo -e "${YELLOW}3. 验证英文CommandHandler完整性...${NC}"
echo ""

echo "start.py 的 CommandHandler:"
grep "CommandHandler" "$HANDLERS_DIR/start.py" | grep -v "^#" | grep -v "import" || echo "  (无)"

echo ""
echo "cultivation.py 的 CommandHandler:"
grep "CommandHandler" "$HANDLERS_DIR/cultivation.py" | grep -v "^#" | grep -v "import" || echo "  (无)"

echo ""
echo -e "${YELLOW}4. 修正文件权限...${NC}"
chown -R xiuxian:xiuxian "$HANDLERS_DIR"
chmod 644 "$HANDLERS_DIR"/*.py
echo -e "${GREEN}✓ 权限已修正${NC}"

echo ""
echo -e "${YELLOW}5. 重启服务...${NC}"

systemctl restart xiuxian-bot

sleep 5

if systemctl is-active --quiet xiuxian-bot; then
    echo -e "${GREEN}✓ 服务运行正常!${NC}"

    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  清理成功完成!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "🎮 测试命令:"
    echo "  英文: /start /info /cultivate"
    echo "  中文: .开始 .状态 .修炼"
    echo ""

    echo "最近日志:"
    journalctl -u xiuxian-bot -n 20 --no-pager

else
    echo -e "${RED}✗ 服务启动失败${NC}"
    echo ""
    echo "错误日志:"
    journalctl -u xiuxian-bot -n 30 --no-pager
    echo ""
    echo -e "${YELLOW}可以从备份恢复: $BACKUP_DIR${NC}"
    exit 1
fi

echo ""
echo "📊 实时监控: journalctl -u xiuxian-bot -f"
echo ""
