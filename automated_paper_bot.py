#!/usr/bin/env python3
"""
自动化Agent论文机器人 - 本地定时运行版本

功能：
1. 每天下午5点自动运行
2. 爬取过去24小时内发布的Agent相关论文
3. 自动发布到Twitter
4. 完善的错误处理和服务检查
"""
import psycopg2
import tweepy
import subprocess
import os

import time
import requests
import logging
from datetime import datetime, timedelta
from config import DB_CONFIG, TWITTER_API_CONFIG, GROQ_CONFIG
from paper_analyzer import PaperAnalyzer

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('paper_bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AutomatedPaperBot:
    def __init__(self):
        """初始化机器人"""
        self.twitter_client = None
        self.connection = None
        self.cursor = None
        self.analyzer = None
        
        logger.info("🤖 自动化Agent论文机器人初始化")

    def health_check(self):
        """执行服务可用性检查"""
        logger.info("🔍 开始服务健康检查...")
        
        # 检查arXiv网站可访问性
        if not self._check_arxiv_availability():
            logger.error("❌ arXiv网站不可访问，停止执行")
            return False
        
        # 检查数据库连接
        if not self._check_database_connection():
            logger.error("❌ 数据库连接失败，停止执行")
            return False
        
        # 检查Twitter API
        if not self._check_twitter_api():
            logger.error("❌ Twitter API认证失败，停止执行")
            return False
        
        logger.info("✅ 所有服务检查通过")
        return True

    def _check_arxiv_availability(self):
        """检查arXiv网站可访问性"""
        try:
            logger.info("  检查arXiv网站...")
            response = requests.get("https://arxiv.org", timeout=10)
            if response.status_code == 200:
                logger.info("  ✅ arXiv网站正常")
                return True
            else:
                logger.error(f"  ❌ arXiv返回状态码: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"  ❌ arXiv网站访问失败: {e}")
            return False

    def _check_database_connection(self):
        """检查数据库连接"""
        try:
            logger.info("  检查数据库连接...")
            self.connection = psycopg2.connect(**DB_CONFIG)
            self.cursor = self.connection.cursor()
            
            # 测试查询
            self.cursor.execute("SELECT 1;")
            result = self.cursor.fetchone()
            
            if result:
                logger.info("  ✅ 数据库连接正常")
                return True
            else:
                logger.error("  ❌ 数据库查询失败")
                return False
        except Exception as e:
            logger.error(f"  ❌ 数据库连接失败: {e}")
            return False

    def _check_twitter_api(self):
        """检查Twitter API认证"""
        try:
            logger.info("  检查Twitter API...")
            self.twitter_client = tweepy.Client(
                consumer_key=TWITTER_API_CONFIG['consumer_key'],
                consumer_secret=TWITTER_API_CONFIG['consumer_secret'],
                access_token=TWITTER_API_CONFIG['access_token'],
                access_token_secret=TWITTER_API_CONFIG['access_token_secret'],
                wait_on_rate_limit=True
            )
            
            # 测试API调用
            me = self.twitter_client.get_me()
            if me.data:
                logger.info(f"  ✅ Twitter API正常 (@{me.data.username})")
                return True
            else:
                logger.error("  ❌ Twitter API认证失败")
                return False
        except Exception as e:
            logger.error(f"  ❌ Twitter API检查失败: {e}")
            return False

    def crawl_last_24h_papers(self):
        """爬取过去24小时内发布的Agent相关论文"""
        try:
            logger.info("🕷️ 开始爬取过去24小时的Agent论文...")
            
            # 修改爬虫配置，爬取过去24小时的论文
            process = subprocess.Popen(
                ["scrapy", "crawl", "arxiv", "-s", "CLOSESPIDER_TIMEOUT=0"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=os.getcwd()
            )
            
            # 实时读取输出
            output_lines = []
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    line = output.strip()
                    output_lines.append(line)
                    # 显示重要信息
                    if any(keyword in line for keyword in ['Agent论文', '爬取', '论文已保存', 'Spider closed']):
                        logger.info(f"   {line}")
            
            # 等待进程完成
            return_code = process.poll()
            
            if return_code == 0:
                logger.info("✅ 爬虫运行成功")
                
                # 检查爬取结果 - 获取过去24小时的论文
                yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
                today = datetime.now().strftime('%Y-%m-%d')
                
                self.cursor.execute("""
                    SELECT COUNT(*) FROM papers 
                    WHERE added_at >= %s AND added_at <= %s;
                """, (yesterday, today))
                
                new_count = self.cursor.fetchone()[0]
                logger.info(f"📊 爬取到 {new_count} 篇Agent相关论文")
                
                return new_count > 0
            else:
                logger.error(f"❌ 爬虫运行失败，返回码: {return_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 爬取论文失败: {e}")
            return False

    def get_last_24h_papers(self):
        """获取过去24小时的Agent论文"""
        try:
            yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            today = datetime.now().strftime('%Y-%m-%d')
            
            self.cursor.execute("""
                SELECT id, category, title, authors, abstract, url, added_at
                FROM papers 
                WHERE added_at >= %s AND added_at <= %s
                AND (category = 'cs.CL' OR category = 'cs.AI')
                ORDER BY sn DESC;
            """, (yesterday, today))
            
            papers = self.cursor.fetchall()
            logger.info(f"📚 过去24小时有 {len(papers)} 篇Agent论文")
            return papers
        except Exception as e:
            logger.error(f"❌ 获取论文失败: {e}")
            return []

    def analyze_and_select_papers(self, papers, max_papers=10):
        """使用LLM分析并选出最相关的论文"""
        logger.info(f"🤖 使用LLM分析Agent论文相关性...")
        
        # 初始化AI分析器
        try:
            self.analyzer = PaperAnalyzer()
            logger.info("✅ AI分析器已启用")
        except Exception as e:
            logger.error(f"❌ AI分析器初始化失败: {e}")
            return []
        
        scored_papers = []
        
        for i, paper in enumerate(papers, 1):
            paper_id, category, title, authors, abstract, url, added_at = paper
            
            logger.info(f"  分析 {i}/{len(papers)}: {title[:50]}...")
            
            if not abstract or len(abstract.strip()) < 50:
                logger.info("    ⚠️ 摘要太短，跳过")
                continue
            
            # 检查是否为视觉相关论文（排除）
            vision_keywords = [
                'vision', 'visual', 'image', 'video', 'computer vision', 'cv', 
                'object detection', 'segmentation', 'recognition', 'vqa', 
                'multimodal', 'image generation', 'visual question answering'
            ]
            title_lower = title.lower()
            abstract_lower = abstract.lower()
            
            is_vision_related = any(keyword in title_lower or keyword in abstract_lower for keyword in vision_keywords)
            
            if is_vision_related:
                logger.info("    🚫 视觉相关论文，跳过")
                continue
            
            try:
                # 使用AI分析论文相关性
                analysis = self.analyzer.analyze_abstract(abstract, "Agent, Multi-Agent Systems, Agentic AI, LLM Agents")
                
                # 只保留高分论文（8分以上）- 更严格的Agent论文筛选
                if analysis['relevance_score'] < 8:
                    logger.info(f"    📊 评分过低: {analysis['relevance_score']}/10，跳过（需要≥8分）")
                    continue
                
                scored_papers.append({
                    'paper': paper,
                    'score': analysis['relevance_score'],
                    'analysis': analysis
                })
                logger.info(f"    ✅ 评分: {analysis['relevance_score']}/10")
                
            except Exception as e:
                logger.error(f"    ❌ 分析失败: {e}")
                continue
        
        # 按评分排序，取前N篇
        scored_papers.sort(key=lambda x: x['score'], reverse=True)
        top_papers = scored_papers[:max_papers]
        
        logger.info(f"✅ 选出前 {len(top_papers)} 篇最相关的Agent论文")
        for i, paper_data in enumerate(top_papers, 1):
            paper = paper_data['paper']
            score = paper_data['score']
            logger.info(f"  {i}. [{score}/10] {paper[2][:60]}...")
        
        return top_papers

    def post_papers_to_twitter(self, papers):
        """发布论文到Twitter - 单条推文格式，优先保证描述和链接完整"""
        if not papers:
            logger.info("📝 没有论文可发布")
            return
        
        logger.info(f"📱 准备发布 {len(papers)} 篇论文推文")
        
        try:
            successful_tweets = 0
            tweet_ids = []
            
            for i, paper_data in enumerate(papers, 1):
                paper = paper_data['paper']
                paper_id, category, title, authors, abstract, url, added_at = paper
                
                logger.info(f"\n📱 发布第 {i} 篇论文推文")
                logger.info(f"📄 {title[:50]}...")
                
                # 生成论文描述
                try:
                    description = self.analyzer.generate_description(title, abstract)
                    logger.info(f"    📝 生成描述 ({len(description)} 字符): {description}")
                except Exception as e:
                    logger.error(f"    ❌ 描述生成失败: {e}")
                    description = "Novel AI agent approach solving key challenges."
                
                # 清理标题，去掉"Title:"前缀节省字符
                clean_title = title.replace("Title:", "").strip()
                
                # 智能字符分配：优先保证描述和链接完整，动态分配标题空间
                # 计算固定部分：描述 + 链接 + 换行符（这些部分不能被截断）
                fixed_chars = len(description) + len(url) + 4  # 4个换行符
                
                # 计算标题可用的字符数
                available_for_title = 280 - fixed_chars
                
                # 如果标题需要截断
                if len(clean_title) > available_for_title:
                    if available_for_title >= 10:  # 确保标题至少有10个字符才显示
                        truncated_title = clean_title[:available_for_title-3] + "..."
                        tweet_content = f"""{truncated_title}

{description}

{url}"""
                        logger.info(f"⚠️ 标题截断至 {available_for_title-3} 字符以适应 {len(description)} 字符的描述")
                        logger.info(f"✅ 智能分配：描述 {len(description)} 字符，标题 {len(truncated_title)} 字符")
                    else:
                        # 极端情况：描述太长，不显示标题，只显示描述和链接
                        tweet_content = f"""{description}

{url}"""
                        logger.warning(f"⚠️ 描述很长 ({len(description)} 字符)，可用空间不足 ({available_for_title} 字符)，不显示标题")
                        logger.info(f"✅ 极简格式：仅显示描述和链接")
                else:
                    # 标题无需截断，显示完整标题
                    tweet_content = f"""{clean_title}

{description}

{url}"""
                    remaining_chars = available_for_title - len(clean_title)
                    logger.info(f"✅ 标题完整显示，剩余 {remaining_chars} 字符空间")
                
                final_length = len(tweet_content)
                if final_length > 280:
                    logger.error(f"❌ 推文仍超限 {final_length}/280 字符，需要进一步优化")
                else:
                    logger.info(f"✅ 推文长度符合要求 {final_length}/280 字符")
                
                logger.info(f"📝 推文内容 ({len(tweet_content)} 字符):")
                logger.info("=" * 40)
                logger.info(tweet_content)
                logger.info("=" * 40)
                
                try:
                    # 发布推文，最多重试3次
                    for attempt in range(3):
                        try:
                            response = self.twitter_client.create_tweet(text=tweet_content)
                            if response.data:
                                tweet_id = response.data['id']
                                tweet_ids.append(tweet_id)
                                successful_tweets += 1
                                logger.info(f"✅ 推文 {i} 发布成功！ID: {tweet_id}")
                                break
                            else:
                                logger.error(f"❌ 推文 {i} 发布失败 - 无响应数据")
                        except Exception as tweet_error:
                            logger.error(f"❌ 推文 {i} 发布失败 (尝试 {attempt + 1}/3): {tweet_error}")
                            if attempt < 2:
                                time.sleep(5)  # 等待5秒后重试
                            else:
                                break
                    
                    # 推文间隔10秒
                    if i < len(papers):
                        logger.info("⏳ 等待10秒...")
                        time.sleep(10)
                        
                except Exception as tweet_error:
                    logger.error(f"❌ 推文 {i} 发布失败: {tweet_error}")
                    continue
            
            logger.info(f"\n🎉 推文发布完成！")
            logger.info(f"📊 成功发布 {successful_tweets}/{len(papers)} 条推文")
            if tweet_ids:
                logger.info(f"🔗 推文IDs: {', '.join(tweet_ids)}")
                
        except Exception as e:
            logger.error(f"❌ 推文发布失败: {e}")

    def daily_task(self):
        """每日自动任务：爬取过去24小时的论文并发布"""
        logger.info("🌅 开始每日自动任务")
        logger.info("=" * 60)
        
        try:
            # 步骤1: 服务健康检查
            if not self.health_check():
                logger.error("❌ 服务检查失败，停止执行")
                return
            
            # 步骤2: 爬取过去24小时的Agent论文
            if not self.crawl_last_24h_papers():
                logger.error("❌ 爬取失败，今日无推文")
                return
            
            # 步骤3: 获取论文
            papers = self.get_last_24h_papers()
            if not papers:
                logger.info("📝 没有新的Agent论文，今日无推文")
                return
            
            # 步骤4: AI分析并选出最相关的论文
            top_papers = self.analyze_and_select_papers(papers, max_papers=10)
            if not top_papers:
                logger.info("📝 没有找到高质量Agent论文，今日无推文")
                return
            
            # 步骤5: 发布到Twitter
            self.post_papers_to_twitter(top_papers)
            
            logger.info("✅ 每日任务完成")
            
        except Exception as e:
            logger.error(f"❌ 每日任务失败: {e}")
            self._create_error_report(e)
        finally:
            self.close()

    def _create_error_report(self, error):
        """创建错误报告文件"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            error_file = f"error_report_{timestamp}.txt"
            
            with open(error_file, 'w', encoding='utf-8') as f:
                f.write(f"错误报告 - {datetime.now()}\n")
                f.write("=" * 50 + "\n")
                f.write(f"错误信息: {str(error)}\n")
                f.write(f"错误类型: {type(error).__name__}\n")
                f.write("=" * 50 + "\n")
            
            logger.info(f"📄 错误报告已保存: {error_file}")
        except Exception as e:
            logger.error(f"❌ 创建错误报告失败: {e}")



    def run_test_mode(self):
        """测试模式 - 立即执行一次完整流程"""
        logger.info("🧪 测试模式 - 立即执行")
        logger.info("=" * 60)
        
        # 执行每日任务
        self.daily_task()

    def run_analyze_mode(self):
        """分析模式 - 只分析论文，不发推文"""
        logger.info("🔍 分析模式 - 只分析论文，不发推文")
        logger.info("=" * 60)
        
        try:
            # 步骤1: 服务健康检查
            if not self.health_check():
                logger.error("❌ 服务检查失败，停止执行")
                return
            
            # 步骤2: 爬取过去24小时的Agent论文
            if not self.crawl_last_24h_papers():
                logger.error("❌ 爬取失败，无法分析")
                return
            
            # 步骤3: 获取论文
            papers = self.get_last_24h_papers()
            if not papers:
                logger.info("📝 没有新的Agent论文可分析")
                return
            
            # 步骤4: AI分析并选出最相关的论文
            top_papers = self.analyze_and_select_papers(papers, max_papers=10)
            if not top_papers:
                logger.info("📝 没有找到高质量Agent论文")
                return
            
            # 步骤5: 生成推文内容预览（不实际发布）
            logger.info("🎯 分析完成！生成推文内容预览：")
            logger.info("=" * 60)
            
            for i, paper_data in enumerate(top_papers, 1):
                paper = paper_data['paper']
                score = paper_data['score']
                analysis = paper_data['analysis']
                
                paper_id, category, title, authors, abstract, url, added_at = paper
                
                logger.info(f"\n📄 论文 {i}: 评分 {score}/10")
                logger.info(f"标题: {title}")
                logger.info(f"作者: {authors[:80]}...")
                logger.info(f"分类: {category}")
                logger.info(f"链接: {url}")
                logger.info(f"AI分析: {analysis.get('analysis', 'N/A')[:100]}...")
                
                # 生成推文内容
                try:
                    description = self.analyzer.generate_description(title, abstract)
                    logger.info(f"📝 生成描述 ({len(description)} 字符): {description}")
                except Exception as e:
                    logger.error(f"❌ 描述生成失败: {e}")
                    description = "Novel AI agent approach solving key challenges."
                
                # 清理标题，去掉"Title:"前缀节省字符
                clean_title = title.replace("Title:", "").strip()
                
                # 构建推文内容
                tweet_content = f"""{clean_title}

{description}

{url}"""
                
                # 智能字符分配：优先保证描述和链接完整，动态分配标题空间
                # 计算固定部分：描述 + 链接 + 换行符（这些部分不能被截断）
                fixed_chars = len(description) + len(url) + 4  # 4个换行符
                
                # 计算标题可用的字符数
                available_for_title = 280 - fixed_chars
                
                # 如果标题需要截断
                if len(clean_title) > available_for_title:
                    if available_for_title >= 10:  # 确保标题至少有10个字符才显示
                        truncated_title = clean_title[:available_for_title-3] + "..."
                        tweet_content = f"""{truncated_title}

{description}

{url}"""
                        logger.info(f"⚠️ 标题截断至 {available_for_title-3} 字符以适应 {len(description)} 字符的描述")
                        logger.info(f"✅ 智能分配：描述 {len(description)} 字符，标题 {len(truncated_title)} 字符")
                    else:
                        # 极端情况：描述太长，不显示标题，只显示描述和链接
                        tweet_content = f"""{description}

{url}"""
                        logger.warning(f"⚠️ 描述很长 ({len(description)} 字符)，可用空间不足 ({available_for_title} 字符)，不显示标题")
                        logger.info(f"✅ 极简格式：仅显示描述和链接")
                else:
                    # 标题无需截断，显示完整标题
                    tweet_content = f"""{clean_title}

{description}

{url}"""
                    remaining_chars = available_for_title - len(clean_title)
                    logger.info(f"✅ 标题完整显示，剩余 {remaining_chars} 字符空间")
                
                final_length = len(tweet_content)
                if final_length > 280:
                    logger.error(f"❌ 推文仍超限 {final_length}/280 字符，需要进一步优化")
                else:
                    logger.info(f"✅ 推文长度符合要求 {final_length}/280 字符")
                
                # 显示最终推文内容
                logger.info(f"\n📱 推文内容预览 ({len(tweet_content)}/280 字符):")
                logger.info("=" * 40)
                logger.info(tweet_content)
                logger.info("=" * 40)
                logger.info("-" * 60)
            
            logger.info(f"\n✅ 分析完成！共筛选出 {len(top_papers)} 篇高质量Agent论文，已生成推文内容预览")
            
        except Exception as e:
            logger.error(f"❌ 分析任务失败: {e}")
            self._create_error_report(e)
        finally:
            self.close()

    def close(self):
        """关闭连接"""
        try:
            if self.analyzer:
                self.analyzer.close()
            if self.cursor:
                self.cursor.close()
            if self.connection:
                self.connection.close()
            logger.info("🔒 连接已关闭")
        except Exception as e:
            logger.error(f"❌ 关闭连接失败: {e}")

def main():
    """主函数"""
    import sys
    
    try:
        bot = AutomatedPaperBot()
        
        if len(sys.argv) > 1:
            if sys.argv[1] == "test":
                # 测试模式 - 完整流程包括发推
                bot.run_test_mode()
            elif sys.argv[1] == "analyze":
                # 分析模式 - 只分析不发推
                bot.run_analyze_mode()
        else:
            # 默认：直接执行任务（用于Windows任务计划程序）
            bot.daily_task()
            
    except Exception as e:
        logger.error(f"❌ 机器人启动失败: {e}")
        logger.error("💡 请检查配置文件和网络连接")

if __name__ == "__main__":
    main()