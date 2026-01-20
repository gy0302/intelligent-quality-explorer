from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional

from src.shared.database import get_db_session
from src.models.api import ApiProject
from src.schemas.api import (
    ApiProjectCreate, ApiProjectUpdate, ApiProjectResponse
)

router = APIRouter(prefix="/api/v1", tags=["产品项目管理"])


@router.post("/projects", response_model=ApiProjectResponse, summary="创建产品项目")
async def create_project(
    project: ApiProjectCreate,
    db: AsyncSession = Depends(get_db_session)
):
    """创建新的产品项目"""
    # 检查项目名称是否已存在
    existing_project = await db.execute(
        ApiProject.__table__.select().where(ApiProject.name == project.name)
    )
    if existing_project.scalar():
        raise HTTPException(status_code=400, detail="产品项目名称已存在")

    # 创建新的产品项目
    new_project = ApiProject(
        name=project.name,
        description=project.description,
        openapi_spec=project.openapi_spec,
        spec_version=project.spec_version,
        status=project.status or "active",
        base_url=project.base_url,
        project_type=project.project_type or "REST",
        tags=project.tags
    )
    db.add(new_project)
    await db.commit()
    await db.refresh(new_project)
    return new_project


@router.get("/projects", response_model=List[ApiProjectResponse], summary="获取产品项目列表")
async def get_projects(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db_session)
):
    """获取产品项目列表"""
    stmt = ApiProject.__table__.select().offset(skip).limit(limit)
    result = await db.execute(stmt)
    projects = result.mappings().all()
    return projects


@router.get("/projects/{project_id}", response_model=ApiProjectResponse, summary="获取产品项目详情")
async def get_project(
    project_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """获取指定ID的产品项目详情"""
    project = await db.get(ApiProject, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="产品项目不存在")
    return project


@router.put("/projects/{project_id}", response_model=ApiProjectResponse, summary="更新产品项目")
async def update_project(
    project_id: int,
    project: ApiProjectUpdate,
    db: AsyncSession = Depends(get_db_session)
):
    """更新指定ID的产品项目"""
    existing_project = await db.get(ApiProject, project_id)
    if not existing_project:
        raise HTTPException(status_code=404, detail="产品项目不存在")

    # 更新项目信息
    update_data = project.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(existing_project, field, value)

    await db.commit()
    await db.refresh(existing_project)
    return existing_project


@router.delete("/projects/{project_id}", summary="删除产品项目")
async def delete_project(
    project_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """删除指定ID的产品项目"""
    project = await db.get(ApiProject, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="产品项目不存在")

    await db.delete(project)
    await db.commit()
    return {"message": "产品项目删除成功"}
