#!/bin/bash

# 自动化Agent论文机器人 - 完整模式 (macOS)
# 运行完整流程包括发布推文

echo "🤖 启动完整机器人模式..."

# 检查是否在项目根目录
if [ ! -f "automated_paper_bot.py" ]; then
    echo "❌ 错误：请在项目根目录运行此脚本"
    exit 1
fi

# 激活虚拟环境（如果存在）
if [ -d "venv" ]; then
    echo "✅ 激活虚拟环境..."
    source venv/bin/activate
fi

# 运行测试模式（完整流程）
python automated_paper_bot.py test

echo "✅ 机器人运行完成！"