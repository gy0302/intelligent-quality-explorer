from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_, select
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
        select(ApiProject).where(ApiProject.name == project.name)
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
    limit: int = 10,
    name: Optional[str] = Query(None, description="项目名称"),
    description: Optional[str] = Query(None, description="项目描述"),
    status: Optional[str] = Query(None, description="项目状态"),
    db: AsyncSession = Depends(get_db_session)
):
    """获取产品项目列表，支持按名称、描述、状态查询"""
    stmt = select(ApiProject)
    
    # 添加查询条件
    if name:
        stmt = stmt.where(ApiProject.name.like(f"%{name}%"))
    if description:
        stmt = stmt.where(ApiProject.description.like(f"%{description}%"))
    if status:
        stmt = stmt.where(ApiProject.status == status)
    
    stmt = select(ApiProject).offset(skip).limit(limit)
    result = await db.execute(stmt)
    projects = result.scalars().all()
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
    
    # 默认项目不可删除
    if project_id == 1:
        raise HTTPException(status_code=400, detail="默认项目不可删除")
    
    # 已启用的项目不可删除
    if project.status == "active":
        raise HTTPException(status_code=400, detail="已启用的项目不可删除")

    await db.delete(project)
    await db.commit()
    return {"message": "产品项目删除成功"}


@router.delete("/projects/batch", summary="批量删除产品项目")
async def batch_delete_projects(
    project_ids: List[int],
    db: AsyncSession = Depends(get_db_session)
):
    """批量删除产品项目"""
    # 检查是否包含默认项目
    if 1 in project_ids:
        raise HTTPException(status_code=400, detail="默认项目不可删除")
    
    # 获取所有要删除的项目
    projects = await db.execute(
        select(ApiProject).where(ApiProject.id.in_(project_ids))
    )
    projects_to_delete = projects.scalars().all()
    
    # 检查是否有已启用的项目
    for project in projects_to_delete:
        if project.status == "active":
            raise HTTPException(status_code=400, detail=f"项目{project.name}已启用，不可删除")
    
    # 执行删除
    from sqlalchemy import delete
    await db.execute(
        delete(ApiProject).where(ApiProject.id.in_(project_ids))
    )
    await db.commit()
    return {"message": "产品项目批量删除成功"}


@router.put("/projects/{project_id}/status", response_model=ApiProjectResponse, summary="更新产品项目状态")
async def update_project_status(
    project_id: int,
    status: str = Query(..., description="项目状态，可选值：active, inactive"),
    db: AsyncSession = Depends(get_db_session)
):
    """更新指定ID的产品项目状态"""
    # 验证状态值
    if status not in ["active", "inactive"]:
        raise HTTPException(status_code=400, detail="无效的状态值")
    
    project = await db.get(ApiProject, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="产品项目不存在")
    
    # 默认项目不可禁用
    if project_id == 1 and status == "inactive":
        raise HTTPException(status_code=400, detail="默认项目不可禁用")
    
    # 更新状态
    project.status = status
    await db.commit()
    await db.refresh(project)
    return project


@router.put("/projects/batch/status", summary="批量更新产品项目状态")
async def batch_update_project_status(
    project_ids: List[int],
    status: str = Query(..., description="项目状态，可选值：active, inactive"),
    db: AsyncSession = Depends(get_db_session)
):
    """批量更新产品项目状态"""
    # 验证状态值
    if status not in ["active", "inactive"]:
        raise HTTPException(status_code=400, detail="无效的状态值")
    
    # 检查是否包含默认项目且要禁用
    if 1 in project_ids and status == "inactive":
        raise HTTPException(status_code=400, detail="默认项目不可禁用")
    
    # 执行状态更新
    from sqlalchemy import update
    await db.execute(
        update(ApiProject)
        .where(ApiProject.id.in_(project_ids))
        .values(status=status)
    )
    await db.commit()
    return {"message": "产品项目状态批量更新成功"}
