from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional
import httpx

from src.shared.database import get_db_session
from src.services.api_parser.api_importer import ApiImporter
from src.models.api import ApiProject, ApiInterface
from src.schemas.api import (
    ApiInterfaceResponse, ApiImportResponse
)


router = APIRouter(prefix="/api/v1", tags=["API管理"])

# API导入服务实例
api_importer = ApiImporter()


@router.get("/projects/{project_id}/interfaces", response_model=List[ApiInterfaceResponse], summary="获取接口列表")
async def get_project_interfaces(
    project_id: int,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db_session)
):
    """获取指定产品项目的接口列表，仅关联已启动的项目"""
    # 检查项目是否存在且已启动
    project = await db.get(ApiProject, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="产品项目不存在")
    if project.status != "active":
        raise HTTPException(status_code=400, detail="仅允许获取已启动项目的接口列表")

    result = await db.execute(
        ApiInterface.__table__.select()
        .where(ApiInterface.project_id == project_id)
        .offset(skip)
        .limit(limit)
    )
    interfaces = result.scalars().all()
    return interfaces


@router.get("/interfaces/{interface_id}", response_model=ApiInterfaceResponse, summary="获取接口详情")
async def get_interface_detail(
    interface_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """获取指定ID的接口详情，仅关联已启动的项目"""
    interface = await db.get(ApiInterface, interface_id)
    if not interface:
        raise HTTPException(status_code=404, detail="接口不存在")
    
    # 检查接口所属项目是否已启动
    project = await db.get(ApiProject, interface.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="产品项目不存在")
    if project.status != "active":
        raise HTTPException(status_code=400, detail="仅允许获取已启动项目的接口详情")
    
    return interface


@router.post("/projects/{project_id}/import-spec", response_model=ApiImportResponse, summary="导入API规范")
async def import_api_spec(
    project_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db_session)
):
    """通过上传文件导入OpenAPI/Swagger规范，仅关联已启动的项目"""
    try:
        # 检查项目是否存在且已启动
        project = await db.get(ApiProject, project_id)
        if not project:
            raise HTTPException(status_code=404, detail="产品项目不存在")
        if project.status != "active":
            raise HTTPException(status_code=400, detail="仅允许为已启动项目导入API规范")
            
        # 读取文件内容
        content = await file.read()
        spec_content = content.decode("utf-8")

        # 调用API导入服务
        result = await api_importer.import_api(
            db,
            project.name,
            spec_content,
            description=project.description,
            base_url=project.base_url,
            tags=project.tags
        )

        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导入API规范失败: {str(e)}")


@router.post("/projects/{project_id}/import-spec-url", response_model=ApiImportResponse, summary="通过URL导入API规范")
async def import_api_spec_from_url(
    project_id: int,
    url: str,
    db: AsyncSession = Depends(get_db_session)
):
    """通过URL导入OpenAPI/Swagger规范，仅关联已启动的项目"""
    try:
        # 检查项目是否存在且已启动
        project = await db.get(ApiProject, project_id)
        if not project:
            raise HTTPException(status_code=404, detail="产品项目不存在")
        if project.status != "active":
            raise HTTPException(status_code=400, detail="仅允许为已启动项目导入API规范")
            
        # 从URL获取规范内容
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            spec_content = response.text

        # 调用API导入服务
        result = await api_importer.import_api(
            db,
            project.name,
            spec_content,
            description=project.description,
            base_url=project.base_url,
            tags=project.tags
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
