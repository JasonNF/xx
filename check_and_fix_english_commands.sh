#!/bin/bash

#===============================================
# 检查并修复英文命令
#===============================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  检查英文命令${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

START_FILE="/opt/xiuxian-bot/src/bot/handlers/start.py"

echo -e "${YELLOW}1. 检查start.py的register_handlers函数...${NC}"
echo ""

if grep -q "def register_handlers" "$START_FILE"; then
    echo "register_handlers函数存在"
    echo ""
    echo "函数内容:"
    sed -n '/^def register_handlers/,/^def /p' "$START_FILE" | head -20
else
    echo -e "${RED}✗ register_handlers函数不存在！${NC}"
fi

echo ""
echo -e "${YELLOW}2. 查找CommandHandler注册...${NC}"
echo ""

cmd_count=$(grep -c "CommandHandler" "$START_FILE" 2>/dev/null || echo 0)
echo "找到 CommandHandler 行数: $cmd_count"

if [ "$cmd_count" -eq 0 ] || [ "$cmd_count" -eq 1 ]; then
    echo -e "${RED}✗ 没有CommandHandler注册（或只有import）${NC}"
    echo ""
    echo -e "${YELLOW}需要恢复start.py...${NC}"

    # 查找备份
    BACKUP_DIR=$(ls -td /opt/xiuxian-bot-handlers-backup-* 2>/dev/null | head -1)

    if [ -n "$BACKUP_DIR" ] && [ -f "$BACKUP_DIR/start.py" ]; then
        echo "从备份恢复: $BACKUP_DIR/start.py"

        # 检查备份中是否有CommandHandler
        backup_cmd_count=$(grep -c "CommandHandler" "$BACKUP_DIR/start.py" 2>/dev/null || echo 0)
        echo "备份中的CommandHandler数量: $backup_cmd_count"

        if [ "$backup_cmd_count" -gt 2 ]; then
            echo ""
            echo -e "${YELLOW}3. 恢复start.py...${NC}"
            cp "$BACKUP_DIR/start.py" "$START_FILE"
            chown xiuxian:xiuxian "$START_FILE"
            echo -e "${GREEN}✓ 已恢复${NC}"

            echo ""
            echo -e "${YELLOW}4. 验证恢复后的内容...${NC}"
            echo ""
            grep "CommandHandler" "$START_FILE" | grep -v "^#" | grep -v "import" | head -5
        else
            echo -e "${RED}✗ 备份文件也没有CommandHandler！${NC}"
        fi
    else
        echo -e "${RED}✗ 未找到可用的备份${NC}"
    fi
else
    echo -e "${GREEN}✓ CommandHandler存在${NC}"
    echo ""
    echo "已注册的命令:"
    grep "CommandHandler" "$START_FILE" | grep -v "^#" | grep -v "import"
fi

echo ""
echo -e "${YELLOW}5. 检查其他handler文件...${NC}"
echo ""

for handler in cultivation battle inventory shop; do
    file="/opt/xiuxian-bot/src/bot/handlers/${handler}.py"
    if [ -f "$file" ]; then
        count=$(grep -c "CommandHandler" "$file" 2>/dev/null || echo 0)
        if [ "$count" -gt 1 ]; then
            echo -e "${GREEN}✓${NC} $handler.py: $count 个命令"
        else
            echo -e "${RED}✗${NC} $handler.py: $count 个命令"
        fi
    fi
done

echo ""
echo -e "${YELLOW}6. 重启服务...${NC}"

systemctl restart xiuxian-bot

sleep 5

if systemctl is-active --quiet xiuxian-bot; then
    echo -e "${GREEN}✓ 服务运行正常${NC}"

    echo ""
    echo "测试命令:"
    echo "  /start"
    echo "  .开始"
    echo ""

    journalctl -u xiuxian-bot -n 15 --no-pager
else
    echo -e "${RED}✗ 服务启动失败${NC}"
    journalctl -u xiuxian-bot -n 30 --no-pager
fi

echo ""
