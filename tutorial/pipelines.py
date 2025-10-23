import psycopg2
from requests import post
import tweepy
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DB_CONFIG, TELEGRAM_CONFIG, TWITTER_CONFIG

def send_message_to_telegram(message):
    """发送消息到Telegram（如果配置了的话）"""
    if not TELEGRAM_CONFIG['token'] or not TELEGRAM_CONFIG['group_id']:
        print("Telegram未配置，跳过通知")
        return
    
    url = f"https://api.telegram.org/bot{TELEGRAM_CONFIG['token']}/sendMessage"
    payload = {
        "text": message,
        "disable_web_page_preview": False,
        "disable_notification": False,
        "reply_to_message_id": None,
        "chat_id": TELEGRAM_CONFIG['group_id']
    }
    headers = {
        "accept": "application/json",
        "User-Agent": "Telegram Bot SDK - (https://github.com/irazasyed/telegram-bot-sdk)",
        "content-type": "application/json"
    }
    
    try:
        response = post(url, json=payload, headers=headers)
        print(f"Telegram通知发送成功: {response.status_code}")
    except Exception as e:
        print(f"Telegram通知发送失败: {e}")

def post_on_tweet(message):
    """发布到Twitter（如果配置了的话）"""
    try:
        # 检查Twitter配置是否存在
        if not hasattr(config, 'TWITTER_CONFIG') or not TWITTER_CONFIG:
            print("Twitter未配置，跳过发布")
            return
            
        # 检查必要的配置项
        required_keys = ['consumer_key', 'consumer_secret', 'access_token', 'access_secret']
        if not all(key in TWITTER_CONFIG and TWITTER_CONFIG[key] for key in required_keys):
            print("Twitter配置不完整，跳过发布")
            return
    except:
        print("Twitter未配置，跳过发布")
        return
    
    try:
        client = tweepy.Client(
            consumer_key=TWITTER_CONFIG['consumer_key'],
            consumer_secret=TWITTER_CONFIG['consumer_secret'],
            access_token=TWITTER_CONFIG['access_token'],
            access_token_secret=TWITTER_CONFIG['access_secret']
        )
        response = client.create_tweet(text=message)
        print("Twitter发布成功")
    except Exception as e:
        print(f"Twitter发布失败: {e}")

class PostgresNoDuplicatesPipeline:
    """PostgreSQL数据库管道，避免重复数据"""
    
    def open_spider(self, spider):
        # 使用配置文件连接数据库
        self.connection = psycopg2.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database'],
            port=DB_CONFIG['port']
        )
        
        # 创建游标
        self.cur = self.connection.cursor()
        
        # 创建表（如果不存在）
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS papers(
            SN serial PRIMARY KEY, 
            id text,
            category text,
            title text,
            authors text,
            abstract text,
            url text,
            added_at date
        );
        """)
        self.connection.commit()
        spider.logger.info("数据库连接已建立")

    def process_item(self, item, spider):
        # 检查是否已存在
        paper_id = item["id"]
        self.cur.execute("SELECT * FROM papers WHERE id = %s;", (paper_id,))
        result = self.cur.fetchone()

        if result:
            spider.logger.info(f"论文已存在于数据库: {item['id']}")
        else:
            # 插入新数据
            self.cur.execute(
                """
                INSERT INTO papers (id, category, title, authors, abstract, url, added_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    item["id"],
                    item["category"],
                    item["title"],
                    item["authors"],
                    item["abstract"],
                    item["url"],
                    item["added_at"]
                )
            )
            self.connection.commit()
            spider.logger.info(f"新论文已保存: {item['id']} - {item['title'][:50]}...")
            
            # 发送通知（如果配置了的话）
            notification_message = f"新论文: {item['title']}\n作者: {item['authors']}\n摘要: {item['abstract'][:200]}...\n链接: {item['url']}"
            send_message_to_telegram(notification_message)
            
            tweet_message = f"{item['title'][:100]}... by {item['authors'][:50]} {item['url']}"
            post_on_tweet(tweet_message)
        
        return item

    def close_spider(self, spider):
        # 关闭数据库连接
        self.cur.close()
        self.connection.close()
        spider.logger.info("数据库连接已关闭")