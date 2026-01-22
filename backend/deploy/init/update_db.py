#!/usr/bin/env python3
"""
数据库更新脚本
用于更新数据库表结构，添加缺失的name字段
"""

import asyncio
from src.shared.database import engine, Base
from src.models.api import ApiInterface

async def main():
    """更新数据库表结构"""
    print("开始更新数据库表结构...")
    try:
        # 检查并更新表结构
        async with engine.begin() as conn:
            # 打印当前表结构
            print("正在检查ApiInterface表结构...")
            
            # 使用SQLAlchemy的alter方法添加name字段
            from sqlalchemy import text
            
            # 执行SQL语句添加name字段
            await conn.execute(text("""
                ALTER TABLE api_interfaces 
                ADD COLUMN IF NOT EXISTS name VARCHAR(100) NOT NULL DEFAULT '未命名接口'
            """))
            
            print("✅ 成功添加name字段到api_interfaces表")
            
    except Exception as e:
        print(f"❌ 数据库表更新失败: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())