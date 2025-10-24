#!/usr/bin/env python3
"""
完整的数据库设置脚本
"""
import os
import psycopg2
from dotenv import load_dotenv

def setup_database():
    print("🔧 正在设置PostgreSQL数据库...")
    
    load_dotenv(override=True)
    
    # 基本连接配置（连接到默认的postgres数据库）
    BASE_CONFIG = {
        "host": os.getenv("DB_HOST", "localhost"),
        "database": "postgres",
        "user": os.getenv("DB_USER", "postgres"),
        "password": os.getenv("DB_PASSWORD", ""),
        "port": int(os.getenv("DB_PORT", 5432))
    }
    
    TARGET_DATABASE = os.getenv("DB_DATABASE", "arxiv")
    
    print(f"目标数据库: {TARGET_DATABASE}")
    print(f"PostgreSQL服务器: {BASE_CONFIG['host']}:{BASE_CONFIG['port']}")
    print()
    
    # 1. 测试PostgreSQL连接
    print("1. 测试PostgreSQL服务器连接...")
    try:
        connection = psycopg2.connect(**BASE_CONFIG)
        cursor = connection.cursor()
        
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"✅ PostgreSQL连接成功")
        print(f"   版本: {version}")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"❌ PostgreSQL连接失败: {e}")
        print("💡 请确保PostgreSQL服务已启动，用户名密码正确")
        return False
    
    # 2. 创建数据库
    print(f"\n2. 创建数据库 '{TARGET_DATABASE}'...")
    try:
        connection = psycopg2.connect(**BASE_CONFIG)
        connection.autocommit = True
        cursor = connection.cursor()
        
        # 检查数据库是否已存在
        cursor.execute("""
            SELECT EXISTS(
                SELECT datname FROM pg_catalog.pg_database 
                WHERE datname = %s
            );
        """, (TARGET_DATABASE,))
        
        database_exists = cursor.fetchone()[0]
        
        if database_exists:
            print(f"⚠️ 数据库 '{TARGET_DATABASE}' 已存在")
        else:
            # 创建数据库
            cursor.execute(f"CREATE DATABASE {TARGET_DATABASE} WITH ENCODING 'UTF8';")
            print(f"✅ 数据库 '{TARGET_DATABASE}' 创建成功")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"❌ 创建数据库失败: {e}")
        return False
    
    # 3. 创建表结构
    print(f"\n3. 创建表结构...")
    try:
        # 连接到目标数据库
        target_config = BASE_CONFIG.copy()
        target_config['database'] = TARGET_DATABASE
        
        connection = psycopg2.connect(**target_config)
        cursor = connection.cursor()
        
        # 读取并执行init.sql
        with open('init.sql', 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # 分割SQL语句并执行
        sql_statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
        
        for sql in sql_statements:
            if sql:
                cursor.execute(sql)
                print(f"   执行: {sql[:50]}...")
        
        connection.commit()
        print("✅ 表结构创建成功")
        
        # 验证表创建
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public';
        """)
        
        tables = cursor.fetchall()
        print("   已创建的表:")
        for table in tables:
            print(f"     - {table[0]}")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"❌ 创建表结构失败: {e}")
        return False
    
    # 4. 最终验证
    print(f"\n4. 验证数据库设置...")
    try:
        target_config = BASE_CONFIG.copy()
        target_config['database'] = TARGET_DATABASE
        
        connection = psycopg2.connect(**target_config)
        cursor = connection.cursor()
        
        # 测试papers表
        cursor.execute("SELECT COUNT(*) FROM papers;")
        count = cursor.fetchone()[0]
        print(f"✅ papers表验证成功，当前记录数: {count}")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"❌ 数据库验证失败: {e}")
        return False
    
    print(f"\n🎉 数据库设置完成！")
    print(f"现在可以运行: python automated_paper_bot.py analyze")
    return True

if __name__ == "__main__":
    setup_database()
