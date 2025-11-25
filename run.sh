#!/bin/bash

# 修仙世界启动脚本

echo "🎮 启动修仙世界..."

# 检查Python版本
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python版本: $python_version"

# 检查.env文件
if [ ! -f ".env" ]; then
    echo "⚠️  未找到.env文件，复制.env.example..."
    cp .env.example .env
    echo "请编辑.env文件，填入您的Bot Token"
    echo "然后重新运行此脚本"
    exit 1
fi

# 检查数据目录
if [ ! -d "data" ]; then
    echo "📁 创建数据目录..."
    mkdir -p data/logs
fi

# 启动Bot
echo "🚀 启动Bot..."
cd src
python3 -m bot.main
