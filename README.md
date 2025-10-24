# Automated Agent Paper Bot

An intelligent Agent paper crawler and Twitter bot that automatically scrapes Agent-related papers from arXiv daily, uses AI to analyze and filter high-quality content, and automatically posts to Twitter.

## Key Features

- ✅ **24-Hour Paper Crawling** - Crawls Agent-related papers published in the last 24 hours
- ✅ **AI-Driven Filtering** - Uses Groq LLM to analyze paper relevance and ensure content quality
- ✅ **Cross-Platform Automation** - Supports Windows Task Scheduler and macOS scheduled tasks
- ✅ **Smart Deduplication** - Automatically skips papers already in the database
- ✅ **Tweet Optimization** - Clean tweet format with title, authors, and links

## Step-by-Step Deployment Guide

### Step 1: Install PostgreSQL Database

**Windows:**
1. Download PostgreSQL: https://www.postgresql.org/download/windows/
2. Remember the superuser password during installation
3. Ensure pgAdmin GUI tool is installed

**macOS:**
```bash
# Install using Homebrew
brew install postgresql
brew services start postgresql
```

**Create Database:**
```sql
-- Open pgAdmin or use psql command line
CREATE DATABASE arxiv;
CREATE USER arxiv_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE arxiv TO arxiv_user;
\q or Ctrl+C exit
```
or 
```bash
python setup_database.py
```


### Step 2: Setup Python Environment

```bash
# 1. Clone the project
git clone <repository-url>
cd arxiv-scraper

# 2. Create virtual environment
# Windows:
python -m venv venv
venv\Scripts\activate

# macOS:
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

### Step 3: Obtain API Keys

**Twitter API:**
1. Visit https://developer.twitter.com/
2. Create developer account and apply for API access
3. Create app and get 4 keys: Consumer Key/Secret, Access Token/Secret

**Groq API:**
1. Visit https://console.groq.com/
2. Register account and get API key

### Step 4: Configure Environment Variables

Create `.env` file:
```env
# Database Configuration
DB_HOST=localhost
DB_DATABASE=arxiv
DB_USER=postgres
DB_PASSWORD=your_database_password
DB_PORT=5432

# Twitter API Configuration
TWITTER_CONSUMER_KEY=your_consumer_key
TWITTER_CONSUMER_SECRET=your_consumer_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret

# Groq API Configuration
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.1-8b-instant
```

### Step 5: Test System

```bash
# 1. Test database connection
python check_db.py

# 2. Test crawler
python -m scrapy crawl arxiv -s LOG_LEVEL=INFO

# 3. Test complete analysis workflow (no tweets)
python automated_paper_bot.py analyze

# 4. Test complete workflow (with tweets)
python automated_paper_bot.py test
```

### Step 6: Setup Scheduled Tasks

**Windows:**
```bash
# Run Command Prompt as Administrator
setup_windows_task.bat
```

**macOS:**
```bash
# Set execution permissions
chmod +x setup_macos_task.sh run_*.sh

# Run setup script
./setup_macos_task.sh
```

The scheduled task will run automatically every day at 4:00 PM.

## Project Architecture

```
📱 User Interface Layer
├── run_analyze.bat/.sh ──┐
├── run_bot.bat/.sh ──────┤
└── run_manual.bat/.sh ───┤
                          │
🤖 Main Control Layer     │
└── automated_paper_bot.py ←──┘
    ├── Calls paper_analyzer.py (AI Analysis)
    ├── Calls tutorial/spiders/arxiv.py (Crawler)
    ├── Uses config.py (Configuration)
    └── Writes paper_bot.log (Logging)

🧠 AI Analysis Layer
└── paper_analyzer.py
    ├── Uses config.py (Groq API Config)
    └── Connects PostgreSQL (Read Paper Data)

🕷️ Data Collection Layer
└── tutorial/spiders/arxiv.py
    ├── Uses tutorial/settings.py (Crawler Config)
    ├── Through tutorial/pipelines.py (Data Pipeline)
    └── Stores to PostgreSQL (Paper Data)

⚙️ Configuration Layer
├── config.py ← Reads .env (Environment Variables)
└── scrapy.cfg (Scrapy Project Config)

🗄️ Data Layer
├── PostgreSQL Database (Paper Storage)
└── paper_bot.log (Runtime Logs)
```

### Data Flow
1. **Crawling Phase**: arXiv API → arxiv.py → pipelines.py → PostgreSQL
2. **Analysis Phase**: PostgreSQL → paper_analyzer.py → Groq API → Scoring Results
3. **Publishing Phase**: Scoring Results → automated_paper_bot.py → Twitter API → Tweet Publishing

## File Descriptions

### 🤖 Core Programs
- **`automated_paper_bot.py`** - Main program containing the complete workflow
- **`paper_analyzer.py`** - AI analyzer using Groq LLM to analyze paper relevance
- **`config.py`** - Configuration management, loads all environment variables from .env
- **`check_db.py`** - Database utility for testing connections and displaying statistics

### 🕷️ Crawler System
- **`tutorial/spiders/arxiv.py`** - arXiv paper crawler for scraping Agent-related papers
- **`tutorial/pipelines.py`** - Data processing pipeline for deduplication and database storage
- **`tutorial/settings.py`** - Scrapy crawler configuration

### 🚀 Deployment Scripts
- **`setup_windows_task.bat`** - Windows scheduled task auto-setup
- **`setup_macos_task.sh`** - macOS scheduled task auto-setup
- **`run_analyze.bat/.sh`** - Quick launch for analysis mode (no tweets)
- **`run_bot.bat/.sh`** - Quick launch for complete mode (with tweets)
- **`run_manual.bat/.sh`** - Interactive manual execution

### 📋 Configuration Files
- **`.env`** - Environment variables containing all API keys and database config
- **`requirements.txt`** - Python dependency list
- **`scrapy.cfg`** - Scrapy project configuration

### 📊 Runtime Files
- **`paper_bot.log`** - Main runtime log
- **`cron.log`** / **`launchd.log`** - macOS scheduled task logs

## Usage

### Basic Run Modes
```bash
# Analysis mode (recommended for testing)
python automated_paper_bot.py analyze

# Test mode (complete workflow)
python automated_paper_bot.py test

# Production mode (for scheduled tasks)
python automated_paper_bot.py
```

### Quick Launch Scripts
```bash
# Windows
run_analyze.bat    # Analysis mode
run_bot.bat        # Complete mode
run_manual.bat     # Interactive selection

# macOS
./run_analyze.sh   # Analysis mode
./run_bot.sh       # Complete mode
./run_manual.sh    # Interactive selection
```

## System Requirements

- **Operating System**: Windows 10/11 or macOS 10.14+
- **Python**: 3.8+
- **Database**: PostgreSQL 12+
- **Network**: Stable internet connection
- **APIs**: Twitter API v2, Groq APIs
