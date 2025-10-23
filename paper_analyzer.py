#!/usr/bin/env python3
"""
论文分析工具 - 使用Groq LLM分析数据库中的论文
"""
import psycopg2
from langchain_groq import ChatGroq
from config import DB_CONFIG, GROQ_CONFIG
import json

class PaperAnalyzer:
    def __init__(self):
        # 检查API密钥
        if not GROQ_CONFIG['api_key']:
            raise ValueError("❌ Groq API密钥未配置！请在.env文件中设置GROQ_API_KEY")
        
        # 初始化LLM - 对Qwen模型关闭推理过程
        if 'qwen' in GROQ_CONFIG['model'].lower():
            self.llm = ChatGroq(
                model=GROQ_CONFIG['model'],
                temperature=0,
                max_tokens=1000,
                timeout=60,
                max_retries=3,
                api_key=GROQ_CONFIG['api_key'],
                extra_body={"reasoning_effort": "none"}
            )
        else:
            self.llm = ChatGroq(
                model=GROQ_CONFIG['model'],
                temperature=0,
                max_tokens=1000,
                timeout=60,
                max_retries=3,
                api_key=GROQ_CONFIG['api_key']
            )
        
        # 数据库连接
        self.connection = psycopg2.connect(
            host=DB_CONFIG['host'],
            database=DB_CONFIG['database'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            port=DB_CONFIG['port']
        )
        self.cursor = self.connection.cursor()

    def generate_description(self, title: str, abstract: str) -> str:
        """为论文生成非常简短的一句话概括，严格限制在150字符内"""
        prompt = f"""Write ONE very short sentence summarizing this paper in 150 characters or less.

REQUIREMENTS:
- ONE simple sentence ending with period
- Maximum 150 characters total
- Very concise - just the key method and main contribution
- No unnecessary details

EXAMPLES:
"Uses multi-agent RL for task allocation."
"Proposes BERT variant for sentiment analysis."
"Introduces GNN for protein folding prediction."

Title: {title}
Abstract: {abstract}

Short summary (≤150 chars):"""

        try:
            response = self.llm.invoke(prompt)
            description = response.content.strip()
            # 清理引号和多余字符，包括字符计数信息
            description = description.replace('"', '').replace("'", "").strip()
            # 移除可能的字符计数信息
            if "chars)" in description:
                description = description.split("(")[0].strip()
            if description.endswith("."):
                description = description[:-1].strip() + "."
            # 严格控制描述长度，确保推文不会超限
            # 最大安全描述长度：280 - 32(链接) - 4(换行) - 20(最小标题) - 3(省略号) = 221字符
            # 为了更安全，限制在200字符以内
            max_safe_length = 200
            
            if len(description) > max_safe_length:
                # 截断到安全长度，确保以句号结尾
                print(f"Warning: Description too long ({len(description)} chars), truncating to {max_safe_length}: {description}")
                description = description[:max_safe_length-1] + "."
                
            return description
        except Exception as e:
            # 如果API调用失败，返回默认描述（也要控制长度）
            return "Novel AI agent approach solving key challenges."

    def generate_detailed_analysis(self, title: str, abstract: str) -> str:
        """为论文生成详细分析（用于Twitter线程第二条推文）"""
        prompt = f"""Analyze this AI agent research paper and provide a detailed technical analysis in bullet points. Focus on:
- What specific methods/techniques are used
- What problems it solves
- Key contributions or innovations
- Performance improvements or results

Keep it concise but informative, max 250 characters total. Use bullet points with • symbol.

Title: {title}
Abstract: {abstract}

Analysis:"""

        try:
            response = self.llm.invoke(prompt)
            analysis = response.content.strip()
            # 清理引号和多余字符
            analysis = analysis.replace('"', '').replace("'", "").strip()
            # 限制长度
            if len(analysis) > 250:
                analysis = analysis[:247] + "..."
            return analysis
        except Exception as e:
            # 如果API调用失败，返回默认分析
            return "• Novel agent architecture\n• Solves key challenges in multi-agent coordination\n• Achieves improved performance over baselines"

    def analyze_abstract(self, abstract: str, topic: str = "Agent Systems") -> dict:
        """分析论文摘要与Agent系统的相关性"""
        prompt = f"""You are an expert AI researcher specializing in Agent systems. Analyze if this research paper is SPECIFICALLY about AI Agents, Multi-Agent Systems, or Agentic AI.

IMPORTANT: Only papers that are DIRECTLY about AI agents should get high scores. Papers that merely mention "agent" in passing or use it in non-AI contexts should get low scores.

TRUE Agent papers include:
- Multi-agent systems and coordination
- LLM agents and agentic AI
- Autonomous agents and planning
- Agent-based reasoning and decision making
- Agent frameworks and architectures
- Conversational agents and chatbots
- Agent learning and adaptation

NOT Agent papers (should get low scores):
- Papers that only mention "agent" in citations or related work
- RAG systems (unless specifically about agentic RAG)
- General LLM research without agent focus
- Role-playing or persona research
- Benchmarking that's not agent-specific
- Fine-tuning or training methods
- User agents, web agents, or software agents

Abstract: {abstract}

Please provide a structured analysis in the following JSON format:
{{
    "relevant": true/false,
    "confidence": "High/Medium/Low",
    "relevance_score": 0-10,
    "analysis": "Brief explanation of why it is or isn't a true Agent paper",
    "keywords": ["key", "agent", "words", "found"]
}}

Be STRICT in your evaluation. Only give scores 8+ for papers that are clearly and primarily about AI agents."""

        try:
            response = self.llm.invoke(prompt)
            # 尝试解析JSON响应
            try:
                # 提取JSON部分
                content = response.content.strip()
                if content.startswith('```json'):
                    content = content[7:-3]
                elif content.startswith('```'):
                    content = content[3:-3]
                
                result = json.loads(content)
                return result
            except json.JSONDecodeError:
                # 如果JSON解析失败，返回基本结构
                return {
                    "relevant": "yes" in response.content.lower() or "true" in response.content.lower(),
                    "confidence": "Medium",
                    "relevance_score": 5,
                    "analysis": response.content[:200] + "...",
                    "keywords": []
                }
        except Exception as e:
            return {
                "relevant": False,
                "confidence": "Low",
                "relevance_score": 0,
                "analysis": f"Error analyzing: {str(e)}",
                "keywords": []
            }

    def analyze_recent_papers(self, limit: int = 10, topic: str = "Carbon Emission"):
        """分析最近的论文"""
        print(f"🔍 分析最近的 {limit} 篇论文，主题: {topic}")
        print("=" * 80)
        
        # 获取最近的论文
        self.cursor.execute("""
            SELECT id, title, abstract, category, authors, url
            FROM papers 
            ORDER BY sn DESC 
            LIMIT %s;
        """, (limit,))
        
        papers = self.cursor.fetchall()
        relevant_papers = []
        
        for i, (paper_id, title, abstract, category, authors, url) in enumerate(papers, 1):
            print(f"\n📄 [{i}/{limit}] 分析论文: {title[:60]}...")
            
            if not abstract or len(abstract.strip()) < 50:
                print("   ⚠️  摘要太短，跳过分析")
                continue
            
            # 分析论文
            analysis = self.analyze_abstract(abstract, topic)
            
            print(f"   🎯 相关性: {'✅ 相关' if analysis['relevant'] else '❌ 不相关'}")
            print(f"   📊 置信度: {analysis['confidence']}")
            print(f"   🔢 相关性评分: {analysis['relevance_score']}/10")
            print(f"   💭 分析: {analysis['analysis'][:100]}...")
            
            if analysis['relevant'] and analysis['relevance_score'] >= 6:
                relevant_papers.append({
                    'id': paper_id,
                    'title': title,
                    'category': category,
                    'authors': authors,
                    'url': url,
                    'analysis': analysis
                })
        
        # 总结相关论文
        if relevant_papers:
            print(f"\n🎉 找到 {len(relevant_papers)} 篇与 '{topic}' 相关的论文:")
            print("=" * 80)
            for paper in relevant_papers:
                print(f"📋 {paper['title']}")
                print(f"   👥 作者: {paper['authors'][:80]}...")
                print(f"   🏷️  分类: {paper['category']}")
                print(f"   🔗 链接: {paper['url']}")
                print(f"   📊 评分: {paper['analysis']['relevance_score']}/10")
                print()
        else:
            print(f"\n😔 没有找到与 '{topic}' 高度相关的论文")

    def analyze_by_category(self, category: str, topic: str = "Carbon Emission"):
        """按分类分析论文"""
        print(f"🔍 分析 '{category}' 分类中与 '{topic}' 相关的论文")
        print("=" * 80)
        
        self.cursor.execute("""
            SELECT id, title, abstract, authors, url
            FROM papers 
            WHERE category = %s
            ORDER BY sn DESC;
        """, (category,))
        
        papers = self.cursor.fetchall()
        
        if not papers:
            print(f"❌ 没有找到 '{category}' 分类的论文")
            return
        
        print(f"📊 找到 {len(papers)} 篇 '{category}' 分类的论文")
        
        relevant_count = 0
        for paper_id, title, abstract, authors, url in papers:
            if not abstract or len(abstract.strip()) < 50:
                continue
                
            analysis = self.analyze_abstract(abstract, topic)
            
            if analysis['relevant'] and analysis['relevance_score'] >= 7:
                relevant_count += 1
                print(f"\n✅ 相关论文 #{relevant_count}:")
                print(f"   📋 标题: {title}")
                print(f"   👥 作者: {authors[:80]}...")
                print(f"   📊 评分: {analysis['relevance_score']}/10")
                print(f"   💭 分析: {analysis['analysis'][:150]}...")
                print(f"   🔗 链接: {url}")
        
        print(f"\n📈 总结: 在 {len(papers)} 篇 '{category}' 论文中，找到 {relevant_count} 篇与 '{topic}' 相关")

    def close(self):
        """关闭数据库连接"""
        self.cursor.close()
        self.connection.close()

def main():
    """主函数"""
    try:
        analyzer = PaperAnalyzer()
        
        print("🤖 论文分析工具")
        print("选择分析模式:")
        print("1. 分析最近的论文")
        print("2. 按分类分析论文")
        print("3. 退出")
        
        choice = input("\n请选择 (1-3): ").strip()
        
        if choice == "1":
            limit = int(input("分析多少篇最近的论文? (默认10): ") or "10")
            topic = input("分析主题 (默认: Carbon Emission): ").strip() or "Carbon Emission"
            analyzer.analyze_recent_papers(limit, topic)
            
        elif choice == "2":
            # 显示可用分类
            analyzer.cursor.execute("SELECT DISTINCT category FROM papers ORDER BY category;")
            categories = [row[0] for row in analyzer.cursor.fetchall()]
            print(f"可用分类: {', '.join(categories)}")
            
            category = input("选择分类: ").strip()
            topic = input("分析主题 (默认: Carbon Emission): ").strip() or "Carbon Emission"
            analyzer.analyze_by_category(category, topic)
            
        elif choice == "3":
            print("👋 再见!")
        else:
            print("❌ 无效选择")
        
        analyzer.close()
        
    except ValueError as e:
        print(str(e))
    except Exception as e:
        print(f"❌ 发生错误: {e}")

if __name__ == "__main__":
    main()