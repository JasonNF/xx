#!/bin/bash

#===============================================
# Redis高级修复脚本
# 针对systemd配置冲突问题
#===============================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Redis高级修复${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

if [[ $EUID -ne 0 ]]; then
    echo -e "${RED}需要root权限${NC}"
    exit 1
fi

# 1. 停止Redis
echo -e "${YELLOW}1. 停止所有Redis进程...${NC}"
systemctl stop redis-server 2>/dev/null || true
killall -9 redis-server 2>/dev/null || true
sleep 2
echo -e "${GREEN}✓ 已停止${NC}"

# 2. 查看详细错误
echo ""
echo -e "${YELLOW}2. 查看错误日志...${NC}"
echo ""
journalctl -xeu redis-server.service -n 20 --no-pager | tail -10
echo ""

# 3. 检查配置文件
echo -e "${YELLOW}3. 检查配置冲突...${NC}"

REDIS_CONF="/etc/redis/redis.conf"

# 备份配置
cp $REDIS_CONF ${REDIS_CONF}.backup.$(date +%Y%m%d_%H%M%S)

# 修复daemonize配置 (systemd模式必须是no)
sed -i 's/^daemonize yes/daemonize no/' $REDIS_CONF
sed -i 's/^# daemonize no/daemonize no/' $REDIS_CONF

# 确保supervised配置正确
sed -i 's/^supervised no/supervised systemd/' $REDIS_CONF
sed -i 's/^# supervised systemd/supervised systemd/' $REDIS_CONF

# 检查是否存在冲突配置
if grep -q "^daemonize yes" $REDIS_CONF; then
    echo -e "${RED}警告: 发现daemonize yes配置${NC}"
fi

echo -e "${GREEN}✓ 配置已修复${NC}"

# 4. 检查日志文件
echo ""
echo -e "${YELLOW}4. 检查日志文件...${NC}"

LOGFILE=$(grep "^logfile" $REDIS_CONF | awk '{print $2}' | tr -d '"')
if [ -z "$LOGFILE" ] || [ "$LOGFILE" = "" ]; then
    LOGFILE="/var/log/redis/redis-server.log"
fi

mkdir -p $(dirname $LOGFILE)
touch $LOGFILE
chown redis:redis $LOGFILE
chmod 640 $LOGFILE

echo -e "${GREEN}✓ 日志文件: $LOGFILE${NC}"

# 5. 检查数据目录
echo ""
echo -e "${YELLOW}5. 检查数据目录...${NC}"

DBDIR=$(grep "^dir" $REDIS_CONF | awk '{print $2}')
if [ -z "$DBDIR" ]; then
    DBDIR="/var/lib/redis"
fi

mkdir -p $DBDIR
chown -R redis:redis $DBDIR
chmod 750 $DBDIR

# 清理可能损坏的dump文件
if [ -f "$DBDIR/dump.rdb" ]; then
    mv "$DBDIR/dump.rdb" "$DBDIR/dump.rdb.old.$(date +%Y%m%d_%H%M%S)" 2>/dev/null || true
    echo "已备份旧的dump.rdb"
fi

echo -e "${GREEN}✓ 数据目录: $DBDIR${NC}"

# 6. 测试配置文件
echo ""
echo -e "${YELLOW}6. 测试配置文件...${NC}"

if redis-server $REDIS_CONF --test-memory 1 2>&1 | grep -q "passed"; then
    echo -e "${GREEN}✓ 配置文件有效${NC}"
else
    echo -e "${RED}✗ 配置文件有问题${NC}"
    echo "尝试手动测试:"
    redis-server $REDIS_CONF --test-memory 1
fi

# 7. 使用简化配置尝试
echo ""
echo -e "${YELLOW}7. 创建简化配置...${NC}"

cat > /etc/redis/redis-simple.conf <<'EOF'
# Redis简化配置 - 用于systemd
bind 127.0.0.1 ::1
protected-mode yes
port 6379
tcp-backlog 511
timeout 0
tcp-keepalive 300
daemonize no
supervised systemd
pidfile /var/run/redis/redis-server.pid
loglevel notice
logfile /var/log/redis/redis-server.log
databases 16
save 900 1
save 300 10
save 60 10000
stop-writes-on-bgsave-error yes
rdbcompression yes
rdbchecksum yes
dbfilename dump.rdb
dir /var/lib/redis
maxmemory-policy allkeys-lru
appendonly no
EOF

chown redis:redis /etc/redis/redis-simple.conf
chmod 640 /etc/redis/redis-simple.conf

echo -e "${GREEN}✓ 简化配置已创建${NC}"

# 8. 修改systemd服务使用简化配置
echo ""
echo -e "${YELLOW}8. 更新systemd服务...${NC}"

cat > /etc/systemd/system/redis-server.service.d/override.conf <<'EOF'
[Service]
ExecStart=
ExecStart=/usr/bin/redis-server /etc/redis/redis-simple.conf
EOF

mkdir -p /etc/systemd/system/redis-server.service.d/
mv /etc/systemd/system/redis-server.service.d/override.conf /etc/systemd/system/redis-server.service.d/ 2>/dev/null || true

systemctl daemon-reload

echo -e "${GREEN}✓ systemd服务已更新${NC}"

# 9. 启动Redis
echo ""
echo -e "${YELLOW}9. 启动Redis...${NC}"

if systemctl start redis-server; then
    echo -e "${GREEN}✓ Redis启动成功${NC}"

    sleep 2

    # 测试连接
    if redis-cli ping 2>/dev/null | grep -q "PONG"; then
        echo -e "${GREEN}✓ Redis连接正常${NC}"

        # 设置开机自启
        systemctl enable redis-server
        echo -e "${GREEN}✓ 已启用开机自启${NC}"

    else
        echo -e "${YELLOW}⚠ Redis已启动但无响应,等待...${NC}"
        sleep 3
        redis-cli ping || echo "仍无响应"
    fi

else
    echo -e "${RED}✗ 启动失败${NC}"
    echo ""
    echo "查看状态:"
    systemctl status redis-server --no-pager
    echo ""
    echo "查看日志:"
    tail -20 $LOGFILE 2>/dev/null || journalctl -xeu redis-server -n 20 --no-pager
    exit 1
fi

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Redis修复完成!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
systemctl status redis-server --no-pager | head -8
echo ""
redis-cli ping
echo ""
