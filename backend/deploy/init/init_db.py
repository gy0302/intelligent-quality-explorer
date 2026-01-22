#!/usr/bin/env python3
"""
数据库初始化脚本
用于创建所有数据库表
"""

import asyncio
from src.shared.database import create_tables

async def main():
    """初始化数据库"""
    print("开始初始化数据库...")
    try:
        await create_tables()
        print("✅ 数据库表创建成功！")
    except Exception as e:
        print(f"❌ 数据库表创建失败: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
