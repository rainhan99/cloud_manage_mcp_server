#!/bin/bash

# 多云服务器管理系统 - 快速设置脚本

set -e

echo "🚀 多云服务器管理系统 - 快速设置"
echo "================================="

# 检查Python版本
echo "🔍 检查Python版本..."
python_version=$(python3 --version 2>&1 | cut -d" " -f2 | cut -d"." -f1,2)
required_version="3.10"

if ! python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" 2>/dev/null; then
    echo "❌ 错误: 需要Python 3.10或更高版本，当前版本: $python_version"
    echo "请升级Python到3.10+版本"
    exit 1
fi

echo "✅ Python版本检查通过: $python_version"

# 检查并安装uv
echo "🔍 检查uv包管理器..."
if ! command -v uv &> /dev/null; then
    echo "📦 正在安装uv包管理器..."
    if [[ "$OSTYPE" == "darwin"* ]] || [[ "$OSTYPE" == "linux-gnu"* ]]; then
        curl -LsSf https://astral.sh/uv/install.sh | sh
        export PATH="$HOME/.local/bin:$PATH"
    else
        echo "请手动安装uv: https://github.com/astral-sh/uv"
        exit 1
    fi
else
    echo "✅ uv已安装"
fi

# 显示uv版本
uv_version=$(uv --version 2>&1 || echo "无法获取版本")
echo "📦 uv版本: $uv_version"

# 安装项目依赖
echo "📦 正在安装项目依赖..."
uv sync

echo ""
echo "🎯 设置完成！"
echo ""

# 检查环境变量配置
echo "🔧 环境变量配置检查:"
if [ -f ".env" ]; then
    echo "✅ 发现.env文件"
else
    echo "⚠️  未发现.env文件"
    echo "   建议复制config.env.example为.env并配置您的API密钥"
    echo "   cp config.env.example .env"
fi

echo ""
echo "🚀 可用命令:"
echo "   make run          - 运行应用程序"
echo "   make status       - 查看系统状态"
echo "   make help         - 查看所有可用命令"
echo "   uv run python main.py  - 直接运行"
echo ""

# 运行系统检查
echo "📊 系统状态检查:"
echo "================================="
make status || echo "系统状态检查失败"

echo ""
echo "✅ 设置完成！现在您可以运行 'make run' 启动系统。" 