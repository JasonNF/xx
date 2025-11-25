#!/bin/bash

#===============================================
# 修复PostgreSQL证书权限问题
#===============================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  修复PostgreSQL权限${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

SERVICE_USER="xiuxian"
PG_DIR="/home/$SERVICE_USER/.postgresql"

echo -e "${YELLOW}1. 检查PostgreSQL配置目录...${NC}"

if [ -d "$PG_DIR" ]; then
    echo "  找到目录: $PG_DIR"
    ls -la "$PG_DIR"
    echo ""

    echo -e "${YELLOW}2. 修正所有权...${NC}"
    chown -R "$SERVICE_USER:$SERVICE_USER" "$PG_DIR"
    echo -e "${GREEN}✓ 所有权已修正${NC}"

    echo ""
    echo -e "${YELLOW}3. 修正权限...${NC}"

    # 目录权限
    chmod 700 "$PG_DIR"
    echo "  ✓ 目录: 700"

    # 密钥文件权限
    if [ -f "$PG_DIR/postgresql.key" ]; then
        chmod 600 "$PG_DIR/postgresql.key"
        echo "  ✓ postgresql.key: 600"
    fi

    # 证书文件权限
    if [ -f "$PG_DIR/postgresql.crt" ]; then
        chmod 600 "$PG_DIR/postgresql.crt"
        echo "  ✓ postgresql.crt: 600"
    fi

    # 根证书权限
    if [ -f "$PG_DIR/root.crt" ]; then
        chmod 600 "$PG_DIR/root.crt"
        echo "  ✓ root.crt: 600"
    fi

    echo ""
    echo -e "${YELLOW}4. 验证权限...${NC}"
    ls -la "$PG_DIR"

else
    echo -e "${YELLOW}PostgreSQL配置目录不存在,创建它...${NC}"

    # 创建目录
    mkdir -p "$PG_DIR"
    chown "$SERVICE_USER:$SERVICE_USER" "$PG_DIR"
    chmod 700 "$PG_DIR"

    echo -e "${GREEN}✓ 目录已创建${NC}"
fi

echo ""
echo -e "${YELLOW}5. 测试xiuxian用户访问...${NC}"

# 测试xiuxian用户能否访问
if sudo -u "$SERVICE_USER" test -r "$PG_DIR"; then
    echo -e "${GREEN}✓ xiuxian用户可以访问目录${NC}"

    if [ -f "$PG_DIR/postgresql.key" ]; then
        if sudo -u "$SERVICE_USER" test -r "$PG_DIR/postgresql.key"; then
            echo -e "${GREEN}✓ xiuxian用户可以读取 postgresql.key${NC}"
        else
            echo -e "${RED}✗ xiuxian用户无法读取 postgresql.key${NC}"
        fi
    fi
else
    echo -e "${RED}✗ xiuxian用户无法访问目录${NC}"
fi

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

    journalctl -u xiuxian-bot -n 20 --no-pager

else
    echo -e "${RED}✗ 服务仍有问题${NC}"
    echo ""
    echo "最新日志:"
    journalctl -u xiuxian-bot -n 30 --no-pager
    exit 1
fi

echo ""
echo "实时监控: journalctl -u xiuxian-bot -f"
echo ""
