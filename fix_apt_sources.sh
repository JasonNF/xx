#!/bin/bash

#===============================================
# APT源修复脚本
# 用于修复常见的包管理器错误
#===============================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  修复APT软件源配置${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# 检查是否为root
if [[ $EUID -ne 0 ]]; then
    echo -e "${RED}此脚本需要root权限${NC}"
    echo "请使用: sudo bash fix_apt_sources.sh"
    exit 1
fi

# 1. 备份现有源
echo -e "${YELLOW}1. 备份现有源配置...${NC}"
if [ -d "/etc/apt/sources.list.d" ]; then
    mkdir -p /etc/apt/sources.list.d.backup
    cp /etc/apt/sources.list.d/* /etc/apt/sources.list.d.backup/ 2>/dev/null || true
    echo -e "${GREEN}✓ 已备份到 /etc/apt/sources.list.d.backup/${NC}"
fi

# 2. 移除有问题的源
echo ""
echo -e "${YELLOW}2. 移除有问题的源...${NC}"

# 移除NodeSource源(如果不需要)
if [ -f "/etc/apt/sources.list.d/nodesource.list" ]; then
    echo "移除 NodeSource 源"
    mv /etc/apt/sources.list.d/nodesource.list /etc/apt/sources.list.d/nodesource.list.disabled
fi

# 移除OpenResty源(如果不需要)
if [ -f "/etc/apt/sources.list.d/openresty.list" ]; then
    echo "移除 OpenResty 源"
    mv /etc/apt/sources.list.d/openresty.list /etc/apt/sources.list.d/openresty.list.disabled
fi

echo -e "${GREEN}✓ 已移除有问题的源${NC}"

# 3. 清理APT缓存
echo ""
echo -e "${YELLOW}3. 清理APT缓存...${NC}"
apt-get clean
rm -rf /var/lib/apt/lists/*
echo -e "${GREEN}✓ 缓存已清理${NC}"

# 4. 更新软件源
echo ""
echo -e "${YELLOW}4. 更新软件源...${NC}"
apt-get update -qq 2>&1 | grep -v "Policy will reject signature" | grep -v "does not have a Release file" || true
echo -e "${GREEN}✓ 软件源已更新${NC}"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  APT源修复完成!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "现在可以继续部署了:"
echo "  sudo bash deploy.sh"
echo ""
