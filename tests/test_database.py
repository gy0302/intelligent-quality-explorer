#!/usr/bin/env python3
"""
数据库连接测试脚本
"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

# 导入项目的数据库配置和会话管理
from src.shared.database import get_db_session
from src.config.settings import settings

async def test_db_connection():
    """测试数据库连接"""
    print(f"测试数据库连接: {settings.database.url}")
    print(f"数据库池大小: {settings.database.pool_size}")
    print(f"最大连接数: {settings.database.max_overflow}")
    print("=" * 50)
    
    try:
        # 获取数据库会话
        async for db in get_db_session():
            # 执行简单的SQL查询
            result = await db.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✓ 数据库连接成功!")
            print(f"  PostgreSQL版本: {version}")
            
            # 测试表是否存在
            result = await db.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
            tables = result.scalars().all()
            print(f"\n✓ 数据库表查询成功!")
            print(f"  公共模式下的表数量: {len(tables)}")
            if tables:
                print(f"  表列表: {', '.join(tables[:10])}{'...' if len(tables) > 10 else ''}")
            
            # 测试插入和查询
            await db.execute(text("CREATE TABLE IF NOT EXISTS test_connection (id SERIAL PRIMARY KEY, message VARCHAR(100))"))
            await db.execute(text("INSERT INTO test_connection (message) VALUES ('数据库连接测试成功!')"))
            await db.commit()
            
            result = await db.execute(text("SELECT message FROM test_connection ORDER BY id DESC LIMIT 1"))
            test_message = result.scalar()
            print(f"\n✓ 数据库CRUD操作成功!")
            print(f"  测试消息: {test_message}")
            
            # 清理测试数据
            await db.execute(text("DROP TABLE IF EXISTS test_connection"))
            await db.commit()
            
            break
            
    except Exception as e:
        print(f"✗ 数据库连接失败!")
        print(f"  错误信息: {str(e)}")
        print("\n提示:")
        print("  1. 请确保PostgreSQL服务已启动")
        print("  2. 检查.env文件中的数据库连接参数")
        print("  3. 确保PostgreSQL已创建qadatabase数据库")
        print("  4. 检查数据库用户postgres的密码是否正确")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 所有数据库测试通过!")
    return True

if __name__ == "__main__":
    asyncio.run(test_db_connection())