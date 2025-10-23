import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv(override=True)

# Database Configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "database": os.getenv("DB_DATABASE", "arxiv"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", ""),
    "port": int(os.getenv("DB_PORT", 5432))
}

# Telegram Configuration
TELEGRAM_CONFIG = {
    "token": os.getenv("TELEGRAM_TOKEN", ""),
    "group_id": os.getenv("TELEGRAM_GROUP_ID", "")
}

# Twitter Configuration (官方API)
TWITTER_API_CONFIG = {
    "client_id": os.getenv("TWITTER_CLIENT_ID", ""),
    "client_secret": os.getenv("TWITTER_CLIENT_SECRET", ""),
    "consumer_key": os.getenv("TWITTER_CONSUMER_KEY", ""),
    "consumer_secret": os.getenv("TWITTER_CONSUMER_SECRET", ""),
    "access_token": os.getenv("TWITTER_ACCESS_TOKEN", ""),
    "access_token_secret": os.getenv("TWITTER_ACCESS_TOKEN_SECRET", "")
}

# Twitter Configuration (Twikit备用)
TWITTER_CONFIG = {
    "username": os.getenv("TWITTER_USERNAME", ""),
    "email": os.getenv("TWITTER_EMAIL", ""),
    "password": os.getenv("TWITTER_PASSWORD", "")
}

# Groq API Configuration
GROQ_CONFIG = {
    "api_key": os.getenv("GROQ_API_KEY", ""),
    "model": os.getenv("GROQ_MODEL", "qwen/qwen3-32b")
}