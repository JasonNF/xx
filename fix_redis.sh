#!/bin/bash

#===============================================
# Redis修复脚本
# 诊断并修复Redis启动问题
#===============================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Redis问题诊断与修复${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 检查root权限
if [[ $EUID -ne 0 ]]; then
    echo -e "${RED}此脚本需要root权限${NC}"
    exit 1
fi

# 1. 检查Redis是否安装
echo -e "${YELLOW}1. 检查Redis安装...${NC}"
if ! command -v redis-server &> /dev/null; then
    echo -e "${RED}✗ Redis未安装${NC}"
    echo "正在安装Redis..."
    apt-get update -qq
    apt-get install -y redis-server redis-tools
    echo -e "${GREEN}✓ Redis已安装${NC}"
else
    echo -e "${GREEN}✓ Redis已安装${NC}"
fi

# 2. 检查Redis配置
echo ""
echo -e "${YELLOW}2. 检查Redis配置...${NC}"

# 备份原配置
if [ -f "/etc/redis/redis.conf" ]; then
    cp /etc/redis/redis.conf /etc/redis/redis.conf.backup.$(date +%Y%m%d)
    echo -e "${GREEN}✓ 已备份配置文件${NC}"
fi

# 3. 修复常见问题
echo ""
echo -e "${YELLOW}3. 修复常见配置问题...${NC}"

# 检查并修复supervised配置
if grep -q "^supervised systemd" /etc/redis/redis.conf 2>/dev/null; then
    echo "Redis已配置为systemd模式"
else
    echo "配置Redis为systemd模式..."
    sed -i 's/^supervised no/supervised systemd/' /etc/redis/redis.conf 2>/dev/null || \
    echo "supervised systemd" >> /etc/redis/redis.conf
fi

# 确保Redis监听本地
if ! grep -q "^bind 127.0.0.1" /etc/redis/redis.conf 2>/dev/null; then
    echo "bind 127.0.0.1 ::1" >> /etc/redis/redis.conf
fi

# 设置合理的内存策略
if ! grep -q "^maxmemory-policy" /etc/redis/redis.conf 2>/dev/null; then
    echo "maxmemory-policy allkeys-lru" >> /etc/redis/redis.conf
fi

echo -e "${GREEN}✓ 配置已优化${NC}"

# 4. 检查Redis目录权限
echo ""
echo -e "${YELLOW}4. 检查目录权限...${NC}"

mkdir -p /var/lib/redis
chown redis:redis /var/lib/redis
chmod 750 /var/lib/redis

mkdir -p /var/log/redis
chown redis:redis /var/log/redis
chmod 755 /var/log/redis

echo -e "${GREEN}✓ 权限已修正${NC}"

# 5. 清理旧的PID和Socket
echo ""
echo -e "${YELLOW}5. 清理旧文件...${NC}"

rm -f /var/run/redis/redis-server.pid
rm -f /var/run/redis/redis.sock

echo -e "${GREEN}✓ 旧文件已清理${NC}"

# 6. 停止所有Redis进程
echo ""
echo -e "${YELLOW}6. 停止旧的Redis进程...${NC}"

# 强制停止Redis
systemctl stop redis-server 2>/dev/null || true
killall redis-server 2>/dev/null || true
sleep 2

echo -e "${GREEN}✓ 旧进程已停止${NC}"

# 7. 重新加载systemd
echo ""
echo -e "${YELLOW}7. 重新加载systemd...${NC}"
systemctl daemon-reload
echo -e "${GREEN}✓ systemd已重载${NC}"

# 8. 启动Redis
echo ""
echo -e "${YELLOW}8. 启动Redis服务...${NC}"

if systemctl start redis-server; then
    echo -e "${GREEN}✓ Redis启动成功${NC}"

    # 等待Redis完全启动
    sleep 2

    # 测试连接
    if redis-cli ping | grep -q "PONG"; then
        echo -e "${GREEN}✓ Redis响应正常${NC}"
    else
        echo -e "${RED}✗ Redis无响应${NC}"
        echo "查看日志: journalctl -xeu redis-server.service"
        exit 1
    fi

    # 启用开机自启
    systemctl enable redis-server
    echo -e "${GREEN}✓ 已设置开机自启${NC}"

else
    echo -e "${RED}✗ Redis启动失败${NC}"
    echo ""
    echo -e "${YELLOW}查看详细错误:${NC}"
    systemctl status redis-server.service --no-pager
    echo ""
    echo -e "${YELLOW}查看日志:${NC}"
    journalctl -xeu redis-server.service -n 50 --no-pager
    exit 1
fi

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Redis修复完成!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${GREEN}状态检查:${NC}"
systemctl status redis-server --no-pager | head -10
echo ""
echo -e "${GREEN}连接测试:${NC}"
redis-cli ping
echo ""
echo "现在可以继续部署了!"
