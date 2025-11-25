#!/bin/bash

#===============================================
# 强力删除: 移除所有中文CommandHandler
# 使用Python脚本来可靠地处理中文
#===============================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  移除所有中文CommandHandler${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

INSTALL_DIR="/opt/xiuxian-bot"
HANDLERS_DIR="$INSTALL_DIR/src/bot/handlers"

echo -e "${YELLOW}1. 创建清理脚本...${NC}"

# 创建Python清理脚本
cat > /tmp/remove_chinese_handlers.py << 'PYEOF'
#!/usr/bin/env python3
import re
import os
import sys

def has_chinese(text):
    """检查文本是否包含中文字符"""
    return bool(re.search(r'[\u4e00-\u9fff]', text))

def remove_chinese_command_handlers(file_path):
    """从文件中移除所有包含中文的CommandHandler行"""
    if not os.path.exists(file_path):
        return 0

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    removed = 0
    new_lines = []

    for line in lines:
        # 检查是否是CommandHandler行
        if 'CommandHandler(' in line and has_chinese(line):
            # 跳过这一行
            removed += 1
            print(f"  删除: {line.strip()}")
            continue
        new_lines.append(line)

    if removed > 0:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)

    return removed

def main():
    handlers_dir = sys.argv[1] if len(sys.argv) > 1 else '/opt/xiuxian-bot/src/bot/handlers'

    total_removed = 0
    processed_files = []

    print(f"扫描目录: {handlers_dir}\n")

    for root, dirs, files in os.walk(handlers_dir):
        for file in files:
            if file.endswith('.py') and file != 'chinese_commands.py':
                file_path = os.path.join(root, file)
                removed = remove_chinese_command_handlers(file_path)
                if removed > 0:
                    processed_files.append(file)
                    total_removed += removed

    print(f"\n总计:")
    print(f"  处理文件: {len(processed_files)}")
    print(f"  删除行数: {total_removed}")

    return 0 if total_removed >= 0 else 1

if __name__ == '__main__':
    sys.exit(main())
PYEOF

chmod +x /tmp/remove_chinese_handlers.py

echo -e "${GREEN}✓ 清理脚本已创建${NC}"

echo ""
echo -e "${YELLOW}2. 执行清理...${NC}"

# 使用Python脚本清理
sudo -u xiuxian "$INSTALL_DIR/venv/bin/python" /tmp/remove_chinese_handlers.py "$HANDLERS_DIR"

echo ""
echo -e "${GREEN}✓ 清理完成${NC}"

echo ""
echo -e "${YELLOW}3. 修正权限...${NC}"
chown -R xiuxian:xiuxian "$HANDLERS_DIR"
echo -e "${GREEN}✓ 权限已修正${NC}"

echo ""
echo -e "${YELLOW}4. 重启服务...${NC}"

systemctl restart xiuxian-bot

sleep 5

if systemctl is-active --quiet xiuxian-bot; then
    echo -e "${GREEN}✓ 服务运行正常!${NC}"

    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  部署完成!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "✅ Bot成功启动!"
    echo ""
    echo "🎮 中文命令格式: .命令"
    echo "   例如: .开始  .修炼  .战斗  .背包"
    echo ""
    echo "💡 英文命令: /命令"
    echo "   例如: /start /cultivate /battle /bag"
    echo ""

    echo -e "${YELLOW}最近日志:${NC}"
    journalctl -u xiuxian-bot -n 20 --no-pager | tail -20

else
    echo -e "${RED}✗ 服务启动失败${NC}"
    echo ""
    echo "详细日志:"
    journalctl -u xiuxian-bot -n 50 --no-pager
    exit 1
fi

echo ""
echo "📊 实时监控:"
echo "  journalctl -u xiuxian-bot -f"
echo ""

# 清理临时文件
rm -f /tmp/remove_chinese_handlers.py
