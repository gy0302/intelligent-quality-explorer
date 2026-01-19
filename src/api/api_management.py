from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional
import httpx

from src.shared.database import get_db_session
from src.services.api_parser.api_importer import ApiImporter
from src.models.api import ApiProject, ApiInterface
from src.schemas.api import (
    ApiProjectCreate, ApiProjectUpdate, ApiProjectResponse,
    ApiInterfaceResponse, ApiImportResponse, ApiImportRequestBase
)


router = APIRouter(prefix="/api/v1", tags=["API管理"])

# API导入服务实例
api_importer = ApiImporter()


@router.post("/api-projects", response_model=ApiProjectResponse, summary="创建API项目")
async def create_api_project(
    project: ApiProjectCreate,
    db: AsyncSession = Depends(get_db_session)
):
    """创建新的API项目"""
    # 检查项目名称是否已存在
    existing_project = await db.execute(
        ApiProject.__table__.select().where(ApiProject.name == project.name)
    )
    if existing_project.scalar():
        raise HTTPException(status_code=400, detail="API项目名称已存在")

    # 创建新的API项目
    new_project = ApiProject(
        name=project.name,
        description=project.description,
        openapi_spec=project.openapi_spec,
        spec_version=project.spec_version,
        status=project.status or "active",
        base_url=project.base_url,
        project_type=project.project_type or "REST",
        tags=project.tags,
        contact_info=project.contact_info,
        terms_of_service=project.terms_of_service,
        license_info=project.license_info
    )
    db.add(new_project)
    await db.commit()
    await db.refresh(new_project)
    return new_project


@router.get("/api-projects", response_model=List[ApiProjectResponse], summary="获取API项目列表")
async def get_api_projects(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db_session)
):
    """获取API项目列表"""
    result = await db.execute(
        ApiProject.__table__.select().offset(skip).limit(limit)
    )
    projects = result.scalars().all()
    return projects


@router.get("/api-projects/{project_id}", response_model=ApiProjectResponse, summary="获取API项目详情")
async def get_api_project(
    project_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """获取指定ID的API项目详情"""
    project = await db.get(ApiProject, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="API项目不存在")
    return project


@router.put("/api-projects/{project_id}", response_model=ApiProjectResponse, summary="更新API项目")
async def update_api_project(
    project_id: int,
    project: ApiProjectUpdate,
    db: AsyncSession = Depends(get_db_session)
):
    """更新指定ID的API项目"""
    existing_project = await db.get(ApiProject, project_id)
    if not existing_project:
        raise HTTPException(status_code=404, detail="API项目不存在")

    # 更新项目信息
    update_data = project.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(existing_project, field, value)

    await db.commit()
    await db.refresh(existing_project)
    return existing_project


@router.delete("/api-projects/{project_id}", summary="删除API项目")
async def delete_api_project(
    project_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """删除指定ID的API项目"""
    project = await db.get(ApiProject, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="API项目不存在")

    await db.delete(project)
    await db.commit()
    return {"message": "API项目删除成功"}


@router.post("/api-projects/import", response_model=ApiImportResponse, summary="导入API规范")
async def import_api(
    project_name: str,
    description: Optional[str] = None,
    base_url: Optional[str] = None,
    tags: Optional[List[str]] = None,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db_session)
):
    """通过上传文件导入OpenAPI/Swagger规范"""
    try:
        # 读取文件内容
        content = await file.read()
        spec_content = content.decode("utf-8")

        # 调用API导入服务
        result = await api_importer.import_api(
            db,
            project_name,
            spec_content,
            description=description,
            base_url=base_url,
            tags=tags
        )

        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导入API规范失败: {str(e)}")


@router.post("/api-projects/import-url", response_model=ApiImportResponse, summary="通过URL导入API规范")
async def import_api_from_url(
    project_name: str,
    url: str,
    description: Optional[str] = None,
    base_url: Optional[str] = None,
    tags: Optional[List[str]] = None,
    db: AsyncSession = Depends(get_db_session)
):
    """通过URL导入OpenAPI/Swagger规范"""
    try:
        # 从URL获取规范内容
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            spec_content = response.text

        # 调用API导入服务
        result = await api_importer.import_api(
            db,
            project_name,
            spec_content,
            description=description,
            base_url=base_url,
            tags=tags
        )

        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])

        return result
    except httpx.HTTPError as e:
        raise HTTPException(status_code=400, detail=f"获取URL内容失败: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导入API规范失败: {str(e)}")


@router.get("/api-projects/{project_id}/interfaces", response_model=List[ApiInterfaceResponse], summary="获取API接口列表")
async def get_api_interfaces(
    project_id: int,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db_session)
):
    """获取指定API项目的接口列表"""
    # 检查项目是否存在
    project = await db.get(ApiProject, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="API项目不存在")

    result = await db.execute(
        ApiInterface.__table__.select()
        .where(ApiInterface.project_id == project_id)
        .offset(skip)
        .limit(limit)
    )
    interfaces = result.scalars().all()
    return interfaces


@router.get("/api-interfaces/{interface_id}", response_model=ApiInterfaceResponse, summary="获取API接口详情")
async def get_api_interface(
    interface_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """获取指定ID的API接口详情"""
    interface = await db.get(ApiInterface, interface_id)
    if not interface:
        raise HTTPException(status_code=404, detail="API接口不存在")
    return interface
