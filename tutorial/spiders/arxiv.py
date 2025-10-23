import scrapy
from urllib.parse import urljoin
from datetime import datetime, timedelta
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config import DB_CONFIG
from tutorial.pipelines import PostgresNoDuplicatesPipeline

# arXiv分类 - 专注Agent相关领域
ARXIV_CATEGORIES = ["cs.CL", "cs.AI"]  # 计算语言学和人工智能

class ArxivSpider(scrapy.Spider):
    name = "arxiv"
    allowed_domains = ["arxiv.org"]

    def start_requests(self):
        """生成初始请求 - 爬取过去24小时的论文"""
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        
        today_str = today.strftime('%y%m%d')
        yesterday_str = yesterday.strftime('%y%m%d')
        
        for category in ARXIV_CATEGORIES:
            # 爬取今天的论文
            url = f"https://arxiv.org/list/{category}/{today_str}?show=100"
            self.logger.info(f"爬取{category}今天({today_str})的论文: {url}")
            yield scrapy.Request(
                url=url, 
                callback=self.parse_listing, 
                meta={'category': category, 'date': today_str, 'target_date': today.strftime('%Y-%m-%d')}
            )
            
            # 爬取昨天的论文
            url = f"https://arxiv.org/list/{category}/{yesterday_str}?show=100"
            self.logger.info(f"爬取{category}昨天({yesterday_str})的论文: {url}")
            yield scrapy.Request(
                url=url, 
                callback=self.parse_listing, 
                meta={'category': category, 'date': yesterday_str, 'target_date': yesterday.strftime('%Y-%m-%d')}
            )
            
            # 爬取最近一周的论文作为补充
            for skip in range(0, 100, 25):
                url = f"https://arxiv.org/list/{category}/pastweek?skip={skip}&show=25"
                self.logger.info(f"爬取{category}最近论文: {url}")
                yield scrapy.Request(
                    url=url, 
                    callback=self.parse_listing, 
                    meta={'category': category, 'backup': True, 'target_date': 'recent'}
                )

    def parse_listing(self, response):
        """解析论文列表页面"""
        category = response.meta['category']
        articles = response.css('div.list-title.mathjax')
        authors = response.css('div.list-authors')
        abs_links = response.css('a[title="Abstract"]::attr(href)').getall()
        ids = response.css('a[title="Abstract"]::attr(id)').getall()

        self.logger.info(f"在{category}分类中找到 {len(articles)} 篇论文")

        for i in range(min(len(articles), len(authors), len(abs_links), len(ids))):
            paper_id = ids[i].split('-')[-1]
            article_title = ''.join([t.strip() for t in articles[i].css('::text').getall() if t.strip()])
            author_text = ''.join([a.strip() for a in authors[i].css('::text').getall() if a.strip()])
            abs_url = urljoin(response.url, abs_links[i])

            yield scrapy.Request(
                url=abs_url, 
                callback=self.parse_abstract, 
                meta={
                    "id": paper_id,
                    'title': article_title,
                    'authors': author_text,
                    'category': category
                }
            )

    def parse_abstract(self, response):
        """解析论文摘要页面"""
        abstract_text = ''.join([
            a.strip() for a in response.css('blockquote.abstract.mathjax::text').getall() if a.strip()
        ])
        
        title = response.meta['title']
        
        # 检查是否包含Agent相关关键词 - 更严格的筛选
        # 核心Agent关键词（必须在标题或摘要中出现）
        core_agent_keywords = [
            'multi-agent', 'agentic', 'llm agent', 'ai agent', 'autonomous agent',
            'agent-based', 'intelligent agent', 'conversational agent', 'agent system',
            'agent framework', 'agent architecture', 'agent interaction', 'agent planning',
            'agent reasoning', 'agent learning', 'agent coordination', 'agent communication'
        ]
        
        # 标题中的Agent关键词（权重更高）
        title_agent_keywords = ['agent', 'agents']
        
        title_lower = title.lower()
        abstract_lower = abstract_text.lower()
        
        # 检查核心关键词
        has_core_keyword = any(keyword in title_lower or keyword in abstract_lower 
                              for keyword in core_agent_keywords)
        
        # 检查标题中是否有Agent关键词
        has_title_agent = any(keyword in title_lower for keyword in title_agent_keywords)
        
        # 排除非Agent相关的词汇
        exclude_keywords = [
            'user agent', 'software agent', 'web agent', 'browser agent',
            'reagent', 'magnetic agent', 'contrast agent', 'therapeutic agent',
            'chemical agent', 'biological agent', 'cleaning agent'
        ]
        
        has_exclude_keyword = any(keyword in title_lower or keyword in abstract_lower 
                                 for keyword in exclude_keywords)
        
        # 只有满足条件且不包含排除词汇的论文才处理
        if not (has_core_keyword or has_title_agent) or has_exclude_keyword:
            self.logger.info(f"跳过非Agent论文: {title[:50]}...")
            return None  # 不处理非Agent论文
        
        # 确定论文的添加日期
        target_date = response.meta.get('target_date', datetime.now().strftime('%Y-%m-%d'))
        if target_date == 'recent':
            target_date = datetime.now().strftime('%Y-%m-%d')
        
        result = {
            'id': response.meta['id'],
            'category': response.meta['category'],
            'title': response.meta['title'],
            'authors': response.meta['authors'],
            'abstract': abstract_text,
            'url': response.url,
            'added_at': target_date
        }

        self.logger.info(f"✅ Agent论文: {result['title'][:50]}...")
        return result