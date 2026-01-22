#!/usr/bin/env python3
"""
测试数据库连接 - 同时测试同步和异步连接方式
用于排查为什么DBWeaver可以连接但项目代码不能连接的问题
"""
import os
import asyncio
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
os.chdir(project_root)
os.environ["PYTHONPATH"] = str(project_root)

# 测试1: 直接使用psycopg2测试同步连接
try:
    import psycopg2
    from psycopg2 import OperationalError
    
    print("=== 测试1: 使用psycopg2的同步连接 ===")
    # 从环境变量获取数据库URL
    db_url = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@10.211.55.3:5432/qadatabase")
    
    # 转换为psycopg2格式（移除+asyncpg）
    psycopg2_url = db_url.replace("+asyncpg", "")
    print(f"连接URL: {psycopg2_url}")
    
    # 解析连接参数
    from urllib.parse import urlparse
    parsed = urlparse(psycopg2_url)
    
    conn_params = {
        "host": parsed.hostname,
        "port": parsed.port,
        "database": parsed.path[1:],  # 移除开头的'/'
        "user": parsed.username,
        "password": parsed.password,
    }
    
    try:
        conn = psycopg2.connect(**conn_params)
        cursor = conn.cursor()
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        cursor.execute("SELECT current_database()")
        dbname = cursor.fetchone()[0]
        cursor.execute("SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public'")
        table_count = cursor.fetchone()[0]
        
        print(f"✓ 同步连接成功!")
        print(f"  PostgreSQL版本: {version.split()[1]}")
        print(f"  当前数据库: {dbname}")
        print(f"  public模式下的表数量: {table_count}")
        
        cursor.close()
        conn.close()
    except OperationalError as e:
        print(f"✗ 同步连接失败!")
        print(f"  错误信息: {e}")
    
except ImportError:
    print("=== 测试1: 使用psycopg2的同步连接 ===")
    print("✗ psycopg2未安装，跳过此测试")

print("\n" + "="*50 + "\n")

# 测试2: 使用SQLAlchemy的同步连接
try:
    from sqlalchemy import create_engine, text
    
    print("=== 测试2: 使用SQLAlchemy的同步连接 ===")
    db_url = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@10.211.55.3:5432/qadatabase")
    sync_url = db_url.replace("+asyncpg", "")  # 使用默认的psycopg2驱动
    
    engine = create_engine(sync_url)
    
    try:
        with engine.connect() as conn:
            version = conn.execute(text("SELECT version()")).scalar()
            dbname = conn.execute(text("SELECT current_database()")).scalar()
            table_count = conn.execute(text("SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public'")).scalar()
            
            print(f"✓ SQLAlchemy同步连接成功!")
            print(f"  PostgreSQL版本: {version.split()[1]}")
            print(f"  当前数据库: {dbname}")
            print(f"  public模式下的表数量: {table_count}")
    except Exception as e:
        print(f"✗ SQLAlchemy同步连接失败!")
        print(f"  错误信息: {e}")
    
except ImportError:
    print("=== 测试2: 使用SQLAlchemy的同步连接 ===")
    print("✗ SQLAlchemy未安装，跳过此测试")

print("\n" + "="*50 + "\n")

# 测试3: 使用SQLAlchemy的异步连接（项目当前使用的方式）
async def test_async_connection():
    print("=== 测试3: 使用SQLAlchemy的异步连接 ===")
    
    try:
        from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
        from sqlalchemy.orm import sessionmaker
        from sqlalchemy import text
        
        # 导入项目的settings
        from src.config.settings import settings
        print(f"连接URL: {settings.database.url}")
        
        # 使用项目配置的URL（包含+asyncpg）
        async_engine = create_async_engine(
            settings.database.url,
            pool_size=settings.database.pool_size,
            max_overflow=settings.database.max_overflow,
            echo=False
        )
        
        AsyncSessionLocal = sessionmaker(
            async_engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
        
        try:
            async with AsyncSessionLocal() as session:
                async with session.begin():
                    version = await session.execute(text("SELECT version()"))
                    version = version.scalar()
                    
                    dbname = await session.execute(text("SELECT current_database()"))
                    dbname = dbname.scalar()
                    
                    table_count = await session.execute(text("SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public'")
                    )
                    table_count = table_count.scalar()
                    
                    print(f"✓ SQLAlchemy异步连接成功!")
                    print(f"  PostgreSQL版本: {version.split()[1]}")
                    print(f"  当前数据库: {dbname}")
                    print(f"  public模式下的表数量: {table_count}")
                    
        except Exception as e:
            print(f"✗ SQLAlchemy异步连接失败!")
            print(f"  错误信息: {e}")
            import traceback
            traceback.print_exc()
        
        await async_engine.dispose()
        
    except ImportError as e:
        print(f"✗ 导入模块失败: {e}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"✗ 测试过程中发生意外错误: {e}")
        import traceback
        traceback.print_exc()

# 运行异步测试
asyncio.run(test_async_connection())

print("\n" + "="*50 + "\n")

# 测试4: 直接使用asyncpg测试异步连接
async def test_direct_asyncpg():
    print("=== 测试4: 直接使用asyncpg的异步连接 ===")
    
    try:
        import asyncpg
        
        # 从环境变量获取数据库URL
        db_url = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@10.211.55.3:5432/qadatabase")
        print(f"连接URL: {db_url}")
        
        # 解析连接参数
        from urllib.parse import urlparse
        parsed = urlparse(db_url)
        
        conn_params = {
            "host": parsed.hostname,
            "port": parsed.port,
            "database": parsed.path[1:],  # 移除开头的'/'
            "user": parsed.username,
            "password": parsed.password,
        }
        
        try:
            conn = await asyncpg.connect(**conn_params)
            version = await conn.fetchval("SELECT version()")
            dbname = await conn.fetchval("SELECT current_database()")
            table_count = await conn.fetchval("SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public'")
            
            print(f"✓ asyncpg直接连接成功!")
            print(f"  PostgreSQL版本: {version.split()[1]}")
            print(f"  当前数据库: {dbname}")
            print(f"  public模式下的表数量: {table_count}")
            
            await conn.close()
        except Exception as e:
            print(f"✗ asyncpg直接连接失败!")
            print(f"  错误信息: {e}")
            import traceback
            traceback.print_exc()
            
    except ImportError:
        print(f"✗ asyncpg未安装，跳过此测试")
    except Exception as e:
        print(f"✗ 测试过程中发生意外错误: {e}")
        import traceback
        traceback.print_exc()

# 运行asyncpg测试
asyncio.run(test_direct_asyncpg())

print("\n=== 测试总结 ===\n")
print("如果同步连接成功但异步连接失败，可能是:")
print("1. asyncpg驱动的兼容性问题")
print("2. 异步连接的网络限制")
print("3. 防火墙/安全组对异步连接的限制")
print("\n如果所有连接都失败，可能是:")
print("1. 网络连接问题")
print("2. 数据库服务器配置问题")
print("3. 连接参数错误")
