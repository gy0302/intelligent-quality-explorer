#!/usr/bin/env python3
"""
验证默认项目的脚本
用于检查默认项目是否符合要求
"""

import asyncio
from src.shared.database import AsyncSessionLocal
from src.models.api import ApiProject

async def main():
    """验证默认项目"""
    print("开始验证默认项目...")
    try:
        # 使用AsyncSessionLocal获取会话
        async with AsyncSessionLocal() as db:
            # 查询ID为1的项目
            project = await db.get(ApiProject, 1)
            
            if not project:
                print("❌ 默认项目不存在")
                return
            
            # 验证项目信息
            print(f"✅ 默认项目存在，ID: {project.id}")
            print(f"   名称: {project.name}")
            print(f"   描述: {project.description}")
            print(f"   状态: {project.status}")
            print(f"   基础URL: {project.base_url}")
            print(f"   项目类型: {project.project_type}")
            
            # 检查是否符合要求
            if (project.name == "默认项目" and 
                project.description == "系统默认项目" and 
                project.status == "active"):
                print("\n✅ 默认项目符合要求！")
            else:
                print("\n❌ 默认项目不符合要求，需要更新")
                # 如果不符合要求，更新项目信息
                project.name = "默认项目"
                project.description = "系统默认项目"
                project.status = "active"
                await db.commit()
                print("✅ 默认项目已更新为符合要求")
                
    except Exception as e:
        print(f"❌ 验证默认项目失败: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())