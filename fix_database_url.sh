#!/bin/bash

#===============================================
# 修复DATABASE_URL - 移除sslmode参数
#===============================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  修复DATABASE_URL${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

ENV_FILE="/opt/xiuxian-bot/.env"

echo -e "${YELLOW}1. 备份配置文件...${NC}"
cp "$ENV_FILE" "${ENV_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
echo -e "${GREEN}✓ 已备份${NC}"

echo ""
echo -e "${YELLOW}2. 移除sslmode参数...${NC}"

# 读取当前的DATABASE_URL
CURRENT_URL=$(grep "^DATABASE_URL=" "$ENV_FILE" | cut -d'=' -f2-)

echo "当前URL: $CURRENT_URL"

# 移除所有URL参数（?后面的部分）
CLEAN_URL=$(echo "$CURRENT_URL" | cut -d'?' -f1)

echo "清理后URL: $CLEAN_URL"

# 替换配置文件中的DATABASE_URL
sed -i "s|^DATABASE_URL=.*|DATABASE_URL=${CLEAN_URL}|" "$ENV_FILE"

echo -e "${GREEN}✓ DATABASE_URL已清理${NC}"

echo ""
echo -e "${YELLOW}3. 删除.postgresql目录...${NC}"
if [ -d "/home/xiuxian/.postgresql" ]; then
    rm -rf /home/xiuxian/.postgresql
    echo -e "${GREEN}✓ 已删除${NC}"
else
    echo -e "${GREEN}✓ 目录不存在${NC}"
fi

echo ""
echo -e "${YELLOW}4. 修改数据库配置代码以禁用SSL...${NC}"

# 创建临时补丁脚本
cat > /tmp/patch_db.py << 'PYEOF'
import re

file_path = '/opt/xiuxian-bot/src/bot/models/database.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 查找 create_async_engine 调用
# 添加 connect_args 来禁用SSL

# 方案1: 如果已经有 connect_args
if 'connect_args' in content:
    print("已有 connect_args，检查是否需要添加 ssl=False")
    if "'ssl': False" not in content and '"ssl": False' not in content:
        # 在 connect_args 字典中添加 ssl: False
        content = re.sub(
            r'(connect_args\s*=\s*{)',
            r"\1\n        'ssl': False,",
            content
        )
        print("✓ 已添加 ssl: False")
else:
    # 方案2: 没有 connect_args，添加整个参数
    print("添加 connect_args 参数")
    content = re.sub(
        r'(create_async_engine\([^)]+)',
        r"\1,\n    connect_args={'ssl': False}",
        content
    )
    print("✓ 已添加 connect_args")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("数据库配置已更新")
PYEOF

sudo -u xiuxian /opt/xiuxian-bot/venv/bin/python /tmp/patch_db.py

echo -e "${GREEN}✓ 代码已修改${NC}"

echo ""
echo -e "${YELLOW}5. 验证配置...${NC}"
grep "^DATABASE_URL=" "$ENV_FILE"

echo ""
echo -e "${YELLOW}6. 重启服务...${NC}"

systemctl restart xiuxian-bot

sleep 5

if systemctl is-active --quiet xiuxian-bot; then
    echo -e "${GREEN}✓ 服务运行正常!${NC}"

    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  修复完成!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "✅ Bot成功启动!"
    echo ""
    echo "🎮 测试命令 (在Telegram中发送):"
    echo "  中文: .开始  .修炼  .战斗  .背包"
    echo "  英文: /start /cultivate /battle /bag"
    echo ""

    echo -e "${YELLOW}最近日志:${NC}"
    journalctl -u xiuxian-bot -n 20 --no-pager

else
    echo -e "${RED}✗ 服务启动失败${NC}"
    echo ""
    echo "详细日志:"
    journalctl -u xiuxian-bot -n 50 --no-pager
    exit 1
fi

echo ""
echo "📊 实时监控: journalctl -u xiuxian-bot -f"
echo ""

# 清理临时文件
rm -f /tmp/patch_db.py
