import psycopg2
from config import DB_CONFIG
from datetime import datetime, timedelta

conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()

# 检查最近的论文时间
cur.execute('SELECT added_at FROM papers ORDER BY added_at DESC LIMIT 5')
results = cur.fetchall()
print('最近5篇论文的时间:')
for r in results:
    print(f'  {r[0]}')

print(f'当前时间: {datetime.now()}')
print(f'24小时前: {datetime.now() - timedelta(days=1)}')

# 检查过去24小时的论文数量
yesterday = datetime.now() - timedelta(days=1)
cur.execute('SELECT COUNT(*) FROM papers WHERE added_at >= %s', (yesterday,))
count_24h = cur.fetchone()[0]
print(f'过去24小时论文数: {count_24h}')

conn.close()