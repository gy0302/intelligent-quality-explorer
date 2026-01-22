#!/usr/bin/env python3
"""
简化版本的添加默认分组脚本
直接使用SQLAlchemy Core操作，不依赖ORM关系
"""

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from src.shared.database import AsyncSessionLocal

async def main():
    """检查并添加默认分组"""
    print("开始检查并添加默认分组...")
    try:
        # 使用AsyncSessionLocal获取会话
        async with AsyncSessionLocal() as db:
            # 先检查是否有默认项目
            project_result = await db.execute(
                text("SELECT id FROM api_projects WHERE id = 1 OR name = '默认项目'")
            )
            project = project_result.fetchone()
            
            if not project:
                print("未找到默认项目，跳过添加默认分组")
                return
            
            project_id = project.id
            print(f"找到默认项目，ID: {project_id}")
            
            # 检查是否已有默认分组
            group_result = await db.execute(
                text("SELECT id FROM api_groups WHERE project_id = :project_id AND (id = 1 OR name = '默认分组')")
                .bindparams(project_id=project_id)
            )
            group = group_result.fetchone()
            
            if group:
                print("默认分组已存在，跳过添加")
                return
            
            # 添加默认分组
            await db.execute(
                text("INSERT INTO api_groups (id, name, project_id, parent_id, description, created_at, updated_at, created_by, updated_by, is_active) VALUES (:id, :name, :project_id, :parent_id, :description, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, :created_by, :updated_by, true)")
                .bindparams(
                    id=1,
                    name="默认分组",
                    project_id=project_id,
                    parent_id=None,
                    description="系统默认分组",
                    created_by="system",
                    updated_by="system"
                )
            )
            await db.commit()
            print("✅ 默认分组添加成功！")
            
    except Exception as e:
        print(f"❌ 添加默认分组失败: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
