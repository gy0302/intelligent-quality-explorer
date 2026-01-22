#!/usr/bin/env python3
"""
初始化产品项目数据的脚本
"""

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from src.shared.database import engine
from src.shared.database import AsyncSessionLocal
from src.models.base import Base
from src.models.api import ApiProject

async def main():
    """初始化产品项目数据"""
    print("开始初始化产品项目数据...")
    try:
        # 创建所有表
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        # 使用AsyncSessionLocal直接获取会话
        async with AsyncSessionLocal() as db:
            # 检查是否已有数据
            result = await db.execute(ApiProject.__table__.select().limit(1))
            if result.scalar():
                print("数据库中已有产品项目数据，跳过初始化")
                return
            
            # 创建示例产品项目，包含默认项目
            sample_projects = [
                {
                    "name": "默认项目",
                    "description": "系统默认项目",
                    "status": "active",
                    "base_url": "",
                    "project_type": "REST"
                },
                {
                    "name": "用户管理系统",
                    "description": "用户管理系统是一个用于管理用户信息的系统",
                    "status": "active",
                    "base_url": "https://api.example.com/users",
                    "project_type": "REST"
                },
                {
                    "name": "订单管理系统",
                    "description": "订单管理系统是一个用于管理订单信息的系统",
                    "status": "active",
                    "base_url": "https://api.example.com/orders",
                    "project_type": "REST"
                },
                {
                    "name": "产品管理系统",
                    "description": "产品管理系统是一个用于管理产品信息的系统",
                    "status": "inactive",
                    "base_url": "https://api.example.com/products",
                    "project_type": "REST"
                }
            ]
            
            # 插入数据
            for project_data in sample_projects:
                project = ApiProject(**project_data)
                db.add(project)
            
            await db.commit()
            print("✅ 产品项目数据初始化成功！")
    except Exception as e:
        print(f"❌ 产品项目数据初始化失败: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
