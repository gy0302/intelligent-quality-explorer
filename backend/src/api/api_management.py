from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_, and_, desc, select, func
from typing import List, Dict, Any, Optional
import httpx

from src.shared.database import get_db_session
from src.services.api_parser.api_importer import ApiImporter
from src.models.api import ApiProject, ApiInterface, ApiGroup
from src.schemas.api import (
    ApiInterfaceResponse, ApiImportResponse, ApiGroupResponse, ApiGroupCreate,
    ApiInterfaceUpdate, ApiInterfaceCreate
)


router = APIRouter(prefix="/api/v1", tags=["API管理"])

# API导入服务实例
api_importer = ApiImporter()


# -------------------- API分组管理 --------------------

@router.get("/projects/{project_id}/groups", response_model=List[ApiGroupResponse], summary="获取项目API分组列表")
async def get_project_groups(
    project_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """获取指定产品项目的API分组列表"""
    # 检查项目是否存在且已启动
    project = await db.get(ApiProject, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="产品项目不存在")
    if project.status != "active":
        raise HTTPException(status_code=400, detail="仅允许获取已启动项目的API分组列表")

    # 获取项目的所有API分组
    result = await db.execute(
        select(ApiGroup).where(ApiGroup.project_id == project_id)
    )
    groups = result.scalars().all()
    
    # 将扁平列表转换为树形结构
    def build_tree(groups, parent_id=None):
        tree = []
        for group in groups:
            if group.parent_id == parent_id:
                children = build_tree(groups, group.id)
                group_dict = group.__dict__.copy()
                if '_sa_instance_state' in group_dict:
                    del group_dict['_sa_instance_state']
                group_dict['children'] = children
                tree.append(group_dict)
        return tree
    
    tree_groups = build_tree(groups)
    return tree_groups


@router.post("/projects/{project_id}/groups", response_model=ApiGroupResponse, summary="创建API分组")
async def create_api_group(
    project_id: int,
    group: ApiGroupCreate,
    db: AsyncSession = Depends(get_db_session)
):
    """创建新的API分组"""
    # 检查项目是否存在且已启动
    project = await db.get(ApiProject, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="产品项目不存在")
    if project.status != "active":
        raise HTTPException(status_code=400, detail="仅允许为已启动项目创建API分组")

    # 检查分组名称是否已存在
    existing_group = await db.execute(
        select(ApiGroup)
        .where(ApiGroup.project_id == project_id)
        .where(ApiGroup.name == group.name)
    )
    if existing_group.scalar():
        raise HTTPException(status_code=400, detail="API分组名称已存在")

    # 检查层级深度，最多支持8级
    if group.parent_id:
        # 获取父分组
        parent_group = await db.get(ApiGroup, group.parent_id)
        if not parent_group:
            raise HTTPException(status_code=404, detail="父分组不存在")
        
        # 计算层级深度
        current_level = 1
        temp_group = parent_group
        while temp_group.parent_id is not None and current_level < 8:
            temp_group = await db.get(ApiGroup, temp_group.parent_id)
            if not temp_group:
                break
            current_level += 1
        
        if current_level >= 8:
            raise HTTPException(status_code=400, detail="分组层级不能超过8级")

    # 创建新的API分组
    new_group = ApiGroup(
        name=group.name,
        project_id=project_id,
        parent_id=group.parent_id,
        description=group.description
    )
    db.add(new_group)
    await db.commit()
    await db.refresh(new_group)
    return new_group


@router.put("/groups/{group_id}", response_model=ApiGroupResponse, summary="更新API分组")
async def update_api_group(
    group_id: int,
    group: ApiGroupCreate,
    db: AsyncSession = Depends(get_db_session)
):
    """更新指定ID的API分组"""
    existing_group = await db.get(ApiGroup, group_id)
    if not existing_group:
        raise HTTPException(status_code=404, detail="API分组不存在")

    # 检查分组名称是否已存在（排除当前分组）
    existing = await db.execute(
        select(ApiGroup)
        .where(ApiGroup.project_id == existing_group.project_id)
        .where(ApiGroup.name == group.name)
        .where(ApiGroup.id != group_id)
    )
    if existing.scalar():
        raise HTTPException(status_code=400, detail="API分组名称已存在")

    # 更新分组信息
    existing_group.name = group.name
    existing_group.parent_id = group.parent_id
    await db.commit()
    await db.refresh(existing_group)
    return existing_group


@router.delete("/groups/{group_id}", summary="删除API分组")
async def delete_api_group(
    group_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """删除指定ID的API分组"""
    group = await db.get(ApiGroup, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="API分组不存在")

    # 检查分组是否包含接口
    interfaces = await db.execute(
        select(ApiInterface)
        .where(ApiInterface.group_id == group_id)
    )
    if interfaces.scalar():
        raise HTTPException(status_code=400, detail="该分组下包含接口，无法删除")

    await db.delete(group)
    await db.commit()
    return {"message": "API分组删除成功"}


# -------------------- API接口管理 --------------------

@router.get("/projects/{project_id}/interfaces", summary="获取接口列表")
async def get_project_interfaces(
    project_id: int,
    skip: int = 0,
    limit: int = 10,
    keyword: Optional[str] = Query(None, description="搜索关键词，匹配接口名称或路径"),
    group_id: Optional[int] = Query(None, description="API分组ID"),
    status: Optional[str] = Query(None, description="接口状态: active/inactive"),
    method: Optional[str] = Query(None, description="HTTP请求方法"),
    order_by: Optional[str] = Query(None, description="排序字段"),
    db: AsyncSession = Depends(get_db_session)
):
    """获取指定产品项目的接口列表，支持搜索、过滤、排序"""
    # 检查项目是否存在且已启动
    project = await db.get(ApiProject, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="产品项目不存在")
    if project.status != "active":
        raise HTTPException(status_code=400, detail="仅允许获取已启动项目的接口列表")

    # 构建查询条件
    stmt = select(ApiInterface).where(ApiInterface.project_id == project_id)
    
    # 添加搜索条件
    if keyword:
        stmt = stmt.where(
            or_(
                ApiInterface.name.like(f"%{keyword}%"),
                ApiInterface.path.like(f"%{keyword}%")
            )
        )
    
    # 添加分组过滤
    if group_id:
        stmt = stmt.where(ApiInterface.group_id == group_id)
    
    # 添加状态过滤
    if status:
        stmt = stmt.where(ApiInterface.status == status)
    
    # 添加方法过滤
    if method:
        stmt = stmt.where(ApiInterface.method == method.upper())
    
    # 计算总数
    count_query = select(func.count(ApiInterface.id)).where(ApiInterface.project_id == project_id)
    if keyword:
        count_query = count_query.where(
            or_(
                ApiInterface.name.like(f"%{keyword}%"),
                ApiInterface.path.like(f"%{keyword}%")
            )
        )
    if group_id:
        count_query = count_query.where(ApiInterface.group_id == group_id)
    if status:
        count_query = count_query.where(ApiInterface.status == status)
    if method:
        count_query = count_query.where(ApiInterface.method == method.upper())
    
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0
    
    # 添加排序
    if order_by:
        if order_by == "updated_at":
            stmt = stmt.order_by(desc(ApiInterface.updated_at))
        elif order_by == "created_at":
            stmt = stmt.order_by(desc(ApiInterface.created_at))
        elif order_by == "name":
            stmt = stmt.order_by(ApiInterface.name)
        elif order_by == "method":
            stmt = stmt.order_by(ApiInterface.method)
        elif order_by == "path":
            stmt = stmt.order_by(ApiInterface.path)
    else:
        # 默认按更新时间降序
        stmt = stmt.order_by(desc(ApiInterface.updated_at))
    
    # 添加分页
    stmt = stmt.offset(skip).limit(limit)
    
    result = await db.execute(stmt)
    interfaces = result.scalars().all()
    
    return {
        "total": total,
        "items": interfaces
    }


@router.get("/interfaces/{interface_id}", response_model=ApiInterfaceResponse, summary="获取接口详情")
async def get_interface_detail(
    interface_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """获取指定ID的接口详情"""
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


@router.post("/projects/{project_id}/interfaces", response_model=ApiInterfaceResponse, summary="创建接口")
async def create_interface(
    project_id: int,
    interface: ApiInterfaceCreate,
    db: AsyncSession = Depends(get_db_session)
):
    """创建新的接口"""
    # 检查项目是否存在且已启动
    project = await db.get(ApiProject, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="产品项目不存在")
    if project.status != "active":
        raise HTTPException(status_code=400, detail="仅允许为已启动项目创建接口")
    
    # 检查接口名称和路径是否已存在
    existing = await db.execute(
        ApiInterface.__table__.select()
        .where(ApiInterface.project_id == project_id)
        .where(
            or_(
                ApiInterface.name == interface.name,
                and_(ApiInterface.path == interface.path, ApiInterface.method == interface.method)
            )
        )
    )
    if existing.scalar():
        raise HTTPException(status_code=400, detail="接口名称或路径+方法组合已存在")
    
    # 创建新接口
    new_interface = ApiInterface(
        project_id=project_id,
        name=interface.name,
        method=interface.method,
        path=interface.path,
        group_id=interface.group_id,
        protocol=interface.protocol,
        status=interface.status,
        description=interface.description,
        operation_id=interface.operation_id,
        tags=interface.tags,
        response_schema=interface.response_schema,
        request_schema=interface.request_schema,
        auth_type=interface.auth_type,
        auth_token=interface.auth_token
    )
    db.add(new_interface)
    await db.commit()
    await db.refresh(new_interface)
    return new_interface


@router.put("/interfaces/{interface_id}", response_model=ApiInterfaceResponse, summary="更新接口")
async def update_interface(
    interface_id: int,
    interface: ApiInterfaceUpdate,
    db: AsyncSession = Depends(get_db_session)
):
    """更新指定ID的接口"""
    existing_interface = await db.get(ApiInterface, interface_id)
    if not existing_interface:
        raise HTTPException(status_code=404, detail="接口不存在")
    
    # 更新接口信息
    update_data = interface.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(existing_interface, field, value)
    
    await db.commit()
    await db.refresh(existing_interface)
    return existing_interface


@router.delete("/interfaces/{interface_id}", summary="删除接口")
async def delete_interface(
    interface_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """删除指定ID的接口"""
    interface = await db.get(ApiInterface, interface_id)
    if not interface:
        raise HTTPException(status_code=404, detail="接口不存在")
    
    # 检查接口是否已启用
    if interface.status == "active":
        raise HTTPException(status_code=400, detail="已启用的接口不可删除")
    
    await db.delete(interface)
    await db.commit()
    return {"message": "接口删除成功"}


@router.put("/interfaces/{interface_id}/status", response_model=ApiInterfaceResponse, summary="更新接口状态")
async def update_interface_status(
    interface_id: int,
    status: str = Query(..., description="接口状态: active/inactive"),
    db: AsyncSession = Depends(get_db_session)
):
    """更新指定ID的接口状态"""
    interface = await db.get(ApiInterface, interface_id)
    if not interface:
        raise HTTPException(status_code=404, detail="接口不存在")
    
    # 验证状态值
    if status not in ["active", "inactive"]:
        raise HTTPException(status_code=400, detail="无效的状态值")
    
    # 更新状态
    interface.status = status
    await db.commit()
    await db.refresh(interface)
    return interface


@router.delete("/interfaces/batch", summary="批量删除接口")
async def batch_delete_interfaces(
    interface_ids: List[int] = Query(..., description="接口ID列表"),
    db: AsyncSession = Depends(get_db_session)
):
    """批量删除接口"""
    # 检查所有接口是否存在且未启用
    for interface_id in interface_ids:
        interface = await db.get(ApiInterface, interface_id)
        if not interface:
            raise HTTPException(status_code=404, detail=f"接口ID {interface_id} 不存在")
        if interface.status == "active":
            raise HTTPException(status_code=400, detail=f"接口ID {interface_id} 已启用，不可删除")
    
    # 执行批量删除
    await db.execute(
        ApiInterface.__table__.delete().where(ApiInterface.id.in_(interface_ids))
    )
    await db.commit()
    return {"message": f"成功删除 {len(interface_ids)} 个接口"}


@router.put("/interfaces/batch/status", summary="批量更新接口状态")
async def batch_update_interface_status(
    interface_ids: List[int] = Query(..., description="接口ID列表"),
    status: str = Query(..., description="接口状态: active/inactive"),
    db: AsyncSession = Depends(get_db_session)
):
    """批量更新接口状态"""
    # 验证状态值
    if status not in ["active", "inactive"]:
        raise HTTPException(status_code=400, detail="无效的状态值")
    
    # 检查所有接口是否存在
    for interface_id in interface_ids:
        interface = await db.get(ApiInterface, interface_id)
        if not interface:
            raise HTTPException(status_code=404, detail=f"接口ID {interface_id} 不存在")
    
    # 执行批量更新
    await db.execute(
        ApiInterface.__table__.update()
        .where(ApiInterface.id.in_(interface_ids))
        .values(status=status)
    )
    await db.commit()
    return {"message": f"成功更新 {len(interface_ids)} 个接口状态"}


# -------------------- API导入管理 --------------------

@router.post("/projects/{project_id}/import-spec", response_model=ApiImportResponse, summary="导入API规范")
async def import_api_spec(
    project_id: int,
    file: UploadFile = File(...),
    group_id: Optional[int] = Query(None, description="API分组ID，未指定则使用默认分组"),
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
            tags=project.tags,
            group_id=group_id,
            project_id=project_id
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
    url: str = Query(..., description="API规范URL"),
    group_id: Optional[int] = Query(None, description="API分组ID，未指定则使用默认分组"),
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
            tags=project.tags,
            group_id=group_id,
            project_id=project_id
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
