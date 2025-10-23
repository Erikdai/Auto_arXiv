# 自动化Agent论文机器人部署指南 / Automated Agent Paper Bot Deployment Guide

## 概述 / Overview

这个自动化机器人会每天下午4点自动运行，爬取过去24小时内发布的Agent相关论文，并自动发布到Twitter。

This automated bot runs daily at 4 PM, crawling Agent-related papers published in the last 24 hours and automatically posting them to Twitter.

## 功能特点 / Features

- ✅ **智能服务检查 / Smart Service Check**: 运行前检查arXiv、数据库、Twitter API可用性 / Checks arXiv, database, and Twitter API availability before running
- ✅ **24小时论文爬取 / 24-Hour Paper Crawling**: 爬取过去24小时内发布的论文 / Crawls papers published in the last 24 hours
- ✅ **AI智能筛选 / AI Smart Filtering**: 使用LLM分析论文相关性，只发布高质量内容 / Uses LLM to analyze paper relevance, only publishes high-quality content
- ✅ **自动错误处理 / Automatic Error Handling**: 网络错误重试，服务不可用时停止执行 / Network error retry, stops execution when services are unavailable
- ✅ **详细日志记录 / Detailed Logging**: 完整的运行日志和错误报告 / Complete runtime logs and error reports
- ✅ **本地定时运行 / Local Scheduled Execution**: 使用Windows任务计划程序自动执行 / Uses Windows Task Scheduler for automatic execution

## 部署步骤 / Deployment Steps

### 1. 环境准备 / Environment Setup

确保你已经安装了以下依赖：
Make sure you have installed the following dependencies:

```bash
pip install -r requirements.txt
```

### 2. 系统测试 / System Test

在配置之前，先运行系统测试检查所有组件：
Before configuration, run system test to check all components:

```bash
python test_system.py
```

这会测试：/ This will test:
- 环境变量配置 / Environment variable configuration
- 文件读写权限 / File read/write permissions
- arXiv网站访问 / arXiv website access
- 数据库连接 / Database connection
- Twitter API
- Groq API
- Scrapy爬虫配置 / Scrapy spider configuration

### 3. 配置环境变量 / Configure Environment Variables

确保 `.env` 文件包含所有必要的配置：
Make sure the `.env` file contains all necessary configurations:

```env
# 数据库配置 / Database Configuration
DB_HOST=localhost
DB_DATABASE=arxiv
DB_USER=postgres
DB_PASSWORD=your_password
DB_PORT=5432

# Twitter API配置 / Twitter API Configuration
TWITTER_CONSUMER_KEY=your_consumer_key
TWITTER_CONSUMER_SECRET=your_consumer_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret

# Groq API配置 (用于AI分析) / Groq API Configuration (for AI analysis)
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.1-8b-instant
```

### 4. 测试运行 / Test Run

在设置定时任务之前，先测试一下系统是否正常工作：
Before setting up scheduled tasks, test if the system works properly:

```bash
# 方法1: 使用Python命令 / Method 1: Using Python command
python automated_paper_bot.py test

# 方法2: 使用批处理文件 / Method 2: Using batch file
run_manual.bat
```

测试运行会：/ Test run will:
1. 检查所有服务的可用性 / Check availability of all services
2. 爬取过去24小时的论文 / Crawl papers from the last 24 hours
3. 使用AI分析筛选论文 / Use AI to analyze and filter papers
4. 发布到Twitter / Publish to Twitter

### 5. 设置Windows定时任务 / Setup Windows Scheduled Task

#### 方法1: 使用自动化脚本（推荐）/ Method 1: Using Automated Script (Recommended)

以**管理员身份**运行：
Run as **Administrator**:

```bash
setup_windows_task.bat
```

这会自动创建一个名为"Agent论文机器人"的定时任务。
This will automatically create a scheduled task named "Agent论文机器人".

#### 方法2: 手动设置 / Method 2: Manual Setup

1. 打开"任务计划程序"（Task Scheduler）/ Open "Task Scheduler"
2. 点击"创建基本任务" / Click "Create Basic Task"
3. 填写任务信息：/ Fill in task information:
   - **名称 / Name**: Agent论文机器人
   - **描述 / Description**: 每天自动爬取和发布Agent论文 / Daily automatic Agent paper crawling and publishing
4. 设置触发器：/ Set trigger:
   - **触发器 / Trigger**: 每天 / Daily
   - **时间 / Time**: 16:00 (下午4点 / 4 PM)
5. 设置操作：/ Set action:
   - **程序 / Program**: `python`
   - **参数 / Arguments**: `automated_paper_bot.py`
   - **起始位置 / Start in**: 项目根目录路径 / Project root directory path

### 6. 验证定时任务 / Verify Scheduled Task

检查任务是否创建成功：
Check if the task was created successfully:

```bash
schtasks /query /tn "Agent论文机器人"
```

立即运行任务进行测试：
Run the task immediately for testing:

```bash
schtasks /run /tn "Agent论文机器人"
```

## 运行模式 / Running Modes

### 定时模式（默认）/ Scheduled Mode (Default)

```bash
python automated_paper_bot.py
```

程序会等待每天下午4点自动执行任务。
The program will wait to automatically execute tasks daily at 4 PM.

### 测试模式 / Test Mode

```bash
python automated_paper_bot.py test
```

立即执行一次完整的爬取和发布流程，用于测试。
Immediately execute a complete crawling and publishing process for testing.

## 日志和监控 / Logging and Monitoring

### 日志文件 / Log Files

- **主日志 / Main Log**: `paper_bot.log` - 包含所有运行信息 / Contains all runtime information
- **错误报告 / Error Reports**: `error_report_YYYYMMDD_HHMMSS.txt` - 严重错误的详细报告 / Detailed reports for critical errors

### 日志内容 / Log Content

日志包含以下信息：/ Logs contain the following information:
- 服务健康检查结果 / Service health check results
- 爬虫运行状态 / Crawler running status
- 论文分析结果 / Paper analysis results
- Twitter发布状态 / Twitter publishing status
- 错误和异常信息 / Error and exception information

### 监控建议 / Monitoring Recommendations

1. **定期检查日志文件 / Regular Log Check**，确保系统正常运行 / Ensure system is running properly
2. **关注错误报告文件 / Monitor Error Reports**，及时处理问题 / Address issues promptly
3. **验证Twitter发布 / Verify Twitter Posts**，确保推文正常发布 / Ensure tweets are published correctly

## 错误处理 / Error Handling

系统具有完善的错误处理机制：
The system has comprehensive error handling mechanisms:

### 服务检查失败 / Service Check Failure

如果以下服务不可用，系统会停止执行：
If the following services are unavailable, the system will stop execution:
- arXiv网站无法访问 / arXiv website inaccessible
- 数据库连接失败 / Database connection failure
- Twitter API认证失败 / Twitter API authentication failure

### 网络错误 / Network Errors

- 自动重试最多3次 / Automatic retry up to 3 times
- 重试间隔5秒 / Retry interval of 5 seconds
- 3次失败后停止执行 / Stop execution after 3 failures

### 错误恢复 / Error Recovery

1. 检查网络连接 / Check network connection
2. 验证API密钥和配置 / Verify API keys and configuration
3. 查看日志文件了解具体错误 / Check log files for specific errors
4. 手动运行测试模式验证修复 / Run test mode manually to verify fixes

## 任务管理命令 / Task Management Commands

### 查看任务状态 / View Task Status

```bash
schtasks /query /tn "Agent论文机器人"
```

### 立即运行任务 / Run Task Immediately

```bash
schtasks /run /tn "Agent论文机器人"
```

### 删除任务 / Delete Task

```bash
schtasks /delete /tn "Agent论文机器人" /f
```

### 修改任务时间 / Modify Task Time

```bash
schtasks /change /tn "Agent论文机器人" /st 18:00
```

## 系统要求 / System Requirements

- **操作系统 / Operating System**: Windows 10/11
- **Python**: 3.8+
- **数据库 / Database**: PostgreSQL
- **网络 / Network**: 稳定的互联网连接 / Stable internet connection
- **权限 / Permissions**: 管理员权限（用于创建定时任务）/ Administrator privileges (for creating scheduled tasks)

## 故障排除 / Troubleshooting

### 常见问题 / Common Issues

1. **任务创建失败 / Task Creation Failed**
   - 确保以管理员身份运行 / Ensure running as administrator
   - 检查Python路径是否正确 / Check if Python path is correct

2. **爬虫运行失败 / Crawler Failed**
   - 检查网络连接 / Check network connection
   - 验证arXiv网站可访问性 / Verify arXiv website accessibility

3. **Twitter发布失败 / Twitter Publishing Failed**
   - 检查API密钥配置 / Check API key configuration
   - 验证账户权限和限制 / Verify account permissions and limits

4. **数据库连接失败 / Database Connection Failed**
   - 确保PostgreSQL服务运行 / Ensure PostgreSQL service is running
   - 检查数据库配置信息 / Check database configuration

### 获取帮助 / Getting Help

如果遇到问题：/ If you encounter issues:
1. 查看 `paper_bot.log` 日志文件 / Check the `paper_bot.log` file
2. 运行测试模式检查具体错误 / Run test mode to check specific errors
3. 检查所有配置文件和环境变量 / Check all configuration files and environment variables

## 注意事项 / Important Notes

1. **保持电脑开机 / Keep Computer On**: 定时任务需要电脑在下午4点时开机 / Scheduled task requires computer to be on at 4 PM
2. **网络连接 / Network Connection**: 确保网络连接稳定 / Ensure stable network connection
3. **API限制 / API Limits**: 注意Twitter API的使用限制 / Be aware of Twitter API usage limits
4. **定期维护 / Regular Maintenance**: 定期检查日志和清理旧文件 / Regularly check logs and clean old files

## 更新和维护 / Updates and Maintenance

### 更新代码 / Update Code

1. 停止定时任务 / Stop scheduled task
2. 更新代码文件 / Update code files
3. 运行测试模式验证 / Run test mode to verify
4. 重新启动定时任务 / Restart scheduled task

### 备份重要文件 / Backup Important Files

定期备份：/ Regular backup:
- `.env` 配置文件 / Configuration file
- 数据库数据 / Database data
- 日志文件 / Log files

## 高级配置 / Advanced Configuration

### 自定义论文筛选 / Custom Paper Filtering

编辑 `tutorial/spiders/arxiv.py` 中的关键词：
Edit keywords in `tutorial/spiders/arxiv.py`:

```python
agent_keywords = ['agent', 'multi-agent', 'agentic', 'agents']
```

### 调整AI分析参数 / Adjust AI Analysis Parameters

修改 `automated_paper_bot.py` 中的参数：
Modify parameters in `automated_paper_bot.py`:

```python
# 最低相关性评分 / Minimum relevance score
if analysis['relevance_score'] < 7:

# 最大发布论文数 / Maximum papers to publish
top_papers = self.analyze_and_select_papers(papers, max_papers=5)
```

### 修改运行时间 / Modify Runtime

编辑 `automated_paper_bot.py` 中的时间设置：
Edit time settings in `automated_paper_bot.py`:

```python
schedule.every().day.at("16:00").do(self.daily_task)
```

这样你就有了一个完全自动化的Agent论文机器人系统！
Now you have a fully automated Agent paper bot system!