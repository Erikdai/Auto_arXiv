#!/bin/bash

# 自动化Agent论文机器人 - macOS定时任务设置脚本
# 功能：创建每天下午4点运行的定时任务

echo "🤖 自动化Agent论文机器人 - macOS定时任务设置"
echo "================================================"

# 检查是否在项目根目录
if [ ! -f "automated_paper_bot.py" ]; then
    echo "❌ 错误：请在项目根目录运行此脚本"
    echo "   当前目录应包含 automated_paper_bot.py 文件"
    exit 1
fi

# 获取当前目录的绝对路径
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_PATH="$SCRIPT_DIR/automated_paper_bot.py"

# 检查Python路径
PYTHON_PATH=$(which python3)
if [ -z "$PYTHON_PATH" ]; then
    PYTHON_PATH=$(which python)
    if [ -z "$PYTHON_PATH" ]; then
        echo "❌ 错误：未找到Python解释器"
        echo "   请确保Python已安装并在PATH中"
        exit 1
    fi
fi

echo "✅ 检测到Python路径: $PYTHON_PATH"
echo "✅ 检测到脚本路径: $SCRIPT_PATH"

# 检查虚拟环境
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ 检测到虚拟环境: $VIRTUAL_ENV"
    PYTHON_PATH="$VIRTUAL_ENV/bin/python"
elif [ -d "$SCRIPT_DIR/venv" ]; then
    echo "✅ 检测到项目虚拟环境: $SCRIPT_DIR/venv"
    PYTHON_PATH="$SCRIPT_DIR/venv/bin/python"
fi

# 创建启动脚本
LAUNCH_SCRIPT="$SCRIPT_DIR/run_automated_bot.sh"
cat > "$LAUNCH_SCRIPT" << EOF
#!/bin/bash

# 自动化Agent论文机器人启动脚本
# 由setup_macos_task.sh自动生成

# 设置工作目录
cd "$SCRIPT_DIR"

# 设置环境变量
export PATH="$PATH"
export PYTHONPATH="$SCRIPT_DIR:\$PYTHONPATH"

# 记录启动时间
echo "\$(date): Starting Automated Paper Bot" >> "$SCRIPT_DIR/cron.log"

# 运行机器人
"$PYTHON_PATH" "$SCRIPT_PATH" >> "$SCRIPT_DIR/cron.log" 2>&1

# 记录完成时间
echo "\$(date): Automated Paper Bot completed" >> "$SCRIPT_DIR/cron.log"
EOF

# 设置执行权限
chmod +x "$LAUNCH_SCRIPT"
echo "✅ 创建启动脚本: $LAUNCH_SCRIPT"

# 方法1: 使用cron (传统方法)
echo ""
echo "📅 设置定时任务方法1: 使用cron"
echo "================================"

# 检查现有的cron任务
EXISTING_CRON=$(crontab -l 2>/dev/null | grep "automated_paper_bot.py\|run_automated_bot.sh" || true)

if [ ! -z "$EXISTING_CRON" ]; then
    echo "⚠️  发现现有的相关定时任务："
    echo "$EXISTING_CRON"
    echo ""
    read -p "是否要替换现有任务？(y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ 用户取消操作"
        exit 1
    fi
    
    # 移除现有任务
    crontab -l 2>/dev/null | grep -v "automated_paper_bot.py\|run_automated_bot.sh" | crontab -
    echo "✅ 已移除现有任务"
fi

# 添加新的cron任务 (每天下午4点)
(crontab -l 2>/dev/null; echo "0 16 * * * $LAUNCH_SCRIPT") | crontab -

if [ $? -eq 0 ]; then
    echo "✅ cron定时任务创建成功！"
    echo "   任务将在每天下午4:00运行"
    echo "   日志文件: $SCRIPT_DIR/cron.log"
else
    echo "❌ cron定时任务创建失败"
fi

# 方法2: 使用launchd (推荐方法)
echo ""
echo "📅 设置定时任务方法2: 使用launchd (推荐)"
echo "========================================"

# 创建launchd plist文件
PLIST_NAME="com.arxiv.agent.paperbot"
PLIST_FILE="$HOME/Library/LaunchAgents/$PLIST_NAME.plist"

# 确保LaunchAgents目录存在
mkdir -p "$HOME/Library/LaunchAgents"

# 创建plist文件
cat > "$PLIST_FILE" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>$PLIST_NAME</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>$LAUNCH_SCRIPT</string>
    </array>
    
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>16</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    
    <key>WorkingDirectory</key>
    <string>$SCRIPT_DIR</string>
    
    <key>StandardOutPath</key>
    <string>$SCRIPT_DIR/launchd.log</string>
    
    <key>StandardErrorPath</key>
    <string>$SCRIPT_DIR/launchd_error.log</string>
    
    <key>RunAtLoad</key>
    <false/>
    
    <key>KeepAlive</key>
    <false/>
</dict>
</plist>
EOF

echo "✅ 创建launchd配置文件: $PLIST_FILE"

# 加载launchd任务
launchctl unload "$PLIST_FILE" 2>/dev/null || true  # 先卸载（如果存在）
launchctl load "$PLIST_FILE"

if [ $? -eq 0 ]; then
    echo "✅ launchd定时任务创建成功！"
    echo "   任务将在每天下午4:00运行"
    echo "   标准输出日志: $SCRIPT_DIR/launchd.log"
    echo "   错误日志: $SCRIPT_DIR/launchd_error.log"
else
    echo "❌ launchd定时任务创建失败"
fi

# 显示设置完成信息
echo ""
echo "🎉 定时任务设置完成！"
echo "===================="
echo ""
echo "📋 任务信息："
echo "   • 运行时间: 每天下午4:00"
echo "   • Python路径: $PYTHON_PATH"
echo "   • 脚本路径: $SCRIPT_PATH"
echo "   • 工作目录: $SCRIPT_DIR"
echo ""
echo "📊 管理命令："
echo "   • 查看cron任务: crontab -l"
echo "   • 查看launchd任务: launchctl list | grep $PLIST_NAME"
echo "   • 手动运行测试: $LAUNCH_SCRIPT"
echo "   • 查看日志: tail -f $SCRIPT_DIR/cron.log"
echo "   • 查看launchd日志: tail -f $SCRIPT_DIR/launchd.log"
echo ""
echo "🔧 卸载命令："
echo "   • 移除cron任务: crontab -e (手动删除相关行)"
echo "   • 移除launchd任务: launchctl unload $PLIST_FILE && rm $PLIST_FILE"
echo ""
echo "⚠️  重要提醒："
echo "   • 确保Mac在下午4点时处于开机状态"
echo "   • 定时任务会在后台自动运行"
echo "   • 可以通过日志文件监控运行状态"
echo "   • 建议使用launchd方法，更稳定可靠"

# 测试运行
echo ""
read -p "是否要立即测试运行？(y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🧪 开始测试运行..."
    echo "=================="
    "$LAUNCH_SCRIPT"
    echo ""
    echo "✅ 测试完成！请检查日志文件确认运行结果。"
fi

echo ""
echo "✨ 设置完成！机器人将在每天下午4点自动运行。"