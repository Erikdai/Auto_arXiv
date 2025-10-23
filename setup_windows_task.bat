@echo off
REM 自动化Agent论文机器人 - Windows任务计划程序设置脚本
REM 此脚本将创建一个每天下午4点20分运行的定时任务

echo 🤖 设置自动化Agent论文机器人定时任务
echo 🤖 Setup Automated Agent Paper Bot Scheduled Task
echo ================================================

REM 获取当前目录和Python路径
set CURRENT_DIR=%~dp0
set PYTHON_PATH=python
set SCRIPT_PATH=%CURRENT_DIR%run_bot.bat

echo 📁 当前目录: %CURRENT_DIR%
echo 🐍 Python路径: %PYTHON_PATH%
echo 📄 脚本路径: %SCRIPT_PATH%

REM 创建定时任务
echo.
echo 📅 创建定时任务...
schtasks /create /tn "AgentPaperBot" /tr "\"%SCRIPT_PATH%\"" /sc daily /st 16:20 /f

if %errorlevel% == 0 (
    echo ✅ 定时任务创建成功！
    echo.
    echo 📋 任务详情:
    echo    Task Name: AgentPaperBot
    echo    执行时间: 每天下午4:20
    echo    执行命令: run_bot.bat
    echo.
    echo 💡 管理任务:
    echo    View Task: schtasks /query /tn "AgentPaperBot"
    echo    Delete Task: schtasks /delete /tn "AgentPaperBot" /f
    echo    Run Now: schtasks /run /tn "AgentPaperBot"
    echo.
    echo 📝 日志文件: paper_bot.log
) else (
    echo ❌ 定时任务创建失败！
    echo 💡 请以管理员身份运行此脚本
)

echo.
echo 按任意键退出... / Press any key to exit...
pause >nul