from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.config import (
    ConfigCategoryCreate, ConfigCategoryUpdate, ConfigCategoryResponse,
    ConfigItemCreate, ConfigItemUpdate, ConfigItemResponse, ConfigItemDetailResponse,
    ConfigQuery, ConfigListResponse, ConfigCategoryListResponse, ConfigBatchUpdate
)
from src.services.config.config_service import ConfigCategoryService, ConfigItemService
from src.shared.database import get_db_session


router = APIRouter(prefix="/api/v1/config", tags=["配置中心"])


# 配置分类相关路由
@router.post("/categories", response_model=ConfigCategoryResponse, summary="创建配置分类")
async def create_config_category(
    category_data: ConfigCategoryCreate,
    db: AsyncSession = Depends(get_db_session),
):
    """创建新的配置分类"""
    try:
        category = await ConfigCategoryService.create_category(db, category_data)
        return category
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/categories", response_model=ConfigCategoryListResponse, summary="获取配置分类列表")
async def get_config_categories(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    is_active: Optional[bool] = Query(None, description="是否启用"),
    db: AsyncSession = Depends(get_db_session),
):
    """获取配置分类列表"""
    result = await ConfigCategoryService.get_categories(db, page, page_size, is_active)
    return result


@router.get("/categories/{category_id}", response_model=ConfigCategoryResponse, summary="获取配置分类详情")
async def get_config_category(
    category_id: int,
    db: AsyncSession = Depends(get_db_session),
):
    """根据ID获取配置分类详情"""
    category = await ConfigCategoryService.get_category_by_id(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="配置分类不存在")
    return category


@router.put("/categories/{category_id}", response_model=ConfigCategoryResponse, summary="更新配置分类")
async def update_config_category(
    category_id: int,
    category_data: ConfigCategoryUpdate,
    db: AsyncSession = Depends(get_db_session),
):
    """更新配置分类信息"""
    category = await ConfigCategoryService.update_category(db, category_id, category_data)
    if not category:
        raise HTTPException(status_code=404, detail="配置分类不存在")
    return category


@router.delete("/categories/{category_id}", summary="删除配置分类")
async def delete_config_category(
    category_id: int,
    db: AsyncSession = Depends(get_db_session),
):
    """删除配置分类"""
    try:
        success = await ConfigCategoryService.delete_category(db, category_id)
        if not success:
            raise HTTPException(status_code=404, detail="配置分类不存在")
        return {"message": "配置分类删除成功"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# 配置项相关路由
@router.post("/items", response_model=ConfigItemResponse, summary="创建配置项")
async def create_config_item(
    config_data: ConfigItemCreate,
    db: AsyncSession = Depends(get_db_session),
):
    """创建新的配置项"""
    try:
        config_item = await ConfigItemService.create_config_item(db, config_data)
        return config_item
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/items", response_model=ConfigListResponse, summary="获取配置项列表")
async def get_config_items(
    category_id: Optional[int] = Query(None, description="分类ID"),
    key: Optional[str] = Query(None, description="配置键"),
    is_active: Optional[bool] = Query(None, description="是否启用"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db_session),
):
    """获取配置项列表"""
    result = await ConfigItemService.get_config_items(db, category_id, key, is_active, page, page_size)
    return result


@router.get("/items/{config_id}", response_model=ConfigItemResponse, summary="获取配置项详情")
async def get_config_item(
    config_id: int,
    db: AsyncSession = Depends(get_db_session),
):
    """根据ID获取配置项详情"""
    config_item = await ConfigItemService.get_config_item_by_id(db, config_id)
    if not config_item:
        raise HTTPException(status_code=404, detail="配置项不存在")
    return config_item


@router.get("/items/key/{key}", response_model=ConfigItemDetailResponse, summary="根据键获取配置项")
async def get_config_item_by_key(
    key: str,
    db: AsyncSession = Depends(get_db_session),
):
    """根据配置键获取配置项详情"""
    config_item = await ConfigItemService.get_config_item_by_key(db, key)
    if not config_item:
        raise HTTPException(status_code=404, detail=f"配置键 '{key}' 不存在")
    return config_item


@router.put("/items/{config_id}", response_model=ConfigItemResponse, summary="更新配置项")
async def update_config_item(
    config_id: int,
    config_data: ConfigItemUpdate,
    db: AsyncSession = Depends(get_db_session),
):
    """更新配置项信息"""
    try:
        config_item = await ConfigItemService.update_config_item(db, config_id, config_data)
        if not config_item:
            raise HTTPException(status_code=404, detail="配置项不存在")
        return config_item
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/items/{config_id}", summary="删除配置项")
async def delete_config_item(
    config_id: int,
    db: AsyncSession = Depends(get_db_session),
):
    """删除配置项"""
    success = await ConfigItemService.delete_config_item(db, config_id)
    if not success:
        raise HTTPException(status_code=404, detail="配置项不存在")
    return {"message": "配置项删除成功"}


@router.get("/active", response_model=dict, summary="获取所有活跃配置")
async def get_active_configs(
    db: AsyncSession = Depends(get_db_session),
):
    """获取所有活跃的配置项，以字典形式返回"""
    configs = await ConfigItemService.get_active_configs(db)
    return configs


@router.post("/batch-update", response_model=List[ConfigItemResponse], summary="批量更新配置项")
async def batch_update_configs(
    batch_data: ConfigBatchUpdate,
    db: AsyncSession = Depends(get_db_session),
):
    """批量更新配置项"""
    updated_configs = await ConfigItemService.batch_update_configs(db, batch_data.configs)
    return updated_configs