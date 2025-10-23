#!/bin/bash

# 自动化Agent论文机器人 - 手动模式 (macOS)
# 提供交互式选择菜单

echo "📋 自动化Agent论文机器人 - 手动模式"
echo "=================================="

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

echo ""
echo "请选择运行模式："
echo "1) 分析模式 (analyze) - 分析论文但不发推文"
echo "2) 测试模式 (test) - 完整流程包括发推文"
echo "3) 生产模式 (production) - 用于定时任务"
echo "4) 数据库检查 (check-db) - 检查数据库状态"
echo "5) 爬虫测试 (crawler) - 只运行爬虫"
echo "6) 退出"
echo ""

read -p "请输入选择 (1-6): " choice

case $choice in
    1)
        echo "🔍 启动分析模式..."
        python automated_paper_bot.py analyze
        ;;
    2)
        echo "🧪 启动测试模式..."
        python automated_paper_bot.py test
        ;;
    3)
        echo "🚀 启动生产模式..."
        python automated_paper_bot.py
        ;;
    4)
        echo "🗄️ 检查数据库状态..."
        python check_db.py
        ;;
    5)
        echo "🕷️ 运行爬虫测试..."
        python -m scrapy crawl arxiv -s LOG_LEVEL=INFO
        ;;
    6)
        echo "👋 退出"
        exit 0
        ;;
    *)
        echo "❌ 无效选择，请输入1-6之间的数字"
        exit 1
        ;;
esac

echo ""
echo "✅ 操作完成！"