@echo off
REM 运行分析模式（只分析不发推文）
REM Run analyze mode (analyze only, no tweets)

echo 🔍 分析模式 - 只分析论文，不发推文
echo 🔍 Analyze Mode - Analyze papers only, no tweets
echo ================================================

python automated_paper_bot.py analyze

echo.
echo 按任意键退出... / Press any key to exit...
pause >nul