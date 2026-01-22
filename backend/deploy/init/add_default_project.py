#!/usr/bin/env python3
"""
添加默认项目和默认分组的脚本
用于检查并添加默认项目和默认分组，不影响现有数据
"""

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from src.shared.database import engine
from src.shared.database import AsyncSessionLocal
from src.models.api import ApiProject, ApiGroup

async def main():
    """检查并添加默认项目和默认分组"""
    print("开始检查并添加默认项目...")
    try:
        # 使用AsyncSessionLocal获取会话
        async with AsyncSessionLocal() as db:
            # 检查默认项目是否已存在
            result = await db.execute(
                select(ApiProject)
                .where(or_(ApiProject.id == 1, ApiProject.name == "默认项目"))
            )
            existing_project = result.scalars().first()
            
            if existing_project:
                print("默认项目已存在，跳过添加")
                # 检查是否已有默认分组
                group_result = await db.execute(
                    select(ApiGroup)
                    .where(ApiGroup.project_id == existing_project.id)
                    .where(or_(ApiGroup.id == 1, ApiGroup.name == "默认分组"))
                )
                existing_group = group_result.scalars().first()
                if existing_group:
                    print("默认分组已存在，跳过添加")
                else:
                    # 为已有项目添加默认分组
                    default_group = ApiGroup(
                        id=1,
                        name="默认分组",
                        description="系统默认分组",
                        project_id=existing_project.id,
                        parent_id=None,
                        level=0
                    )
                    db.add(default_group)
                    await db.commit()
                    print("✅ 默认分组添加成功！")
                return
            
            # 创建默认项目
            default_project = ApiProject(
                id=1,  # 指定ID为1
                name="默认项目",
                description="系统默认项目",
                status="active",
                base_url="",
                project_type="REST"
            )
            
            db.add(default_project)
            await db.flush()  # 获取项目ID
            
            # 创建默认分组
            default_group = ApiGroup(
                id=1,
                name="默认分组",
                description="系统默认分组",
                project_id=default_project.id,
                parent_id=None,
                level=0
            )
            db.add(default_group)
            
            await db.commit()
            print("✅ 默认项目和默认分组添加成功！")
    except Exception as e:
        print(f"❌ 添加默认项目和分组失败: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())