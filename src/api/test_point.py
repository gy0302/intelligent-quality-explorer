from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any

from src.shared.database import get_db_session
from src.services.test_point.generator import TestPointGenerator
from src.models.test_point import TestPoint, TestPointStatus, TestPointType, TestPointPriority
from src.schemas.test_point import (
    TestPointCreate, TestPointUpdate, TestPointResponse,
    TestPointGenerateRequest, TestPointGenerateResponse,
    TestPointStatusUpdateRequest
)

router = APIRouter(prefix="/api/v1/test-points", tags=["测试点管理"])

# 测试点生成服务实例
test_point_generator = TestPointGenerator()

@router.post("/generate", response_model=TestPointGenerateResponse, summary="生成测试点", description="根据API项目生成测试点")
async def generate_test_points(
    request: TestPointGenerateRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """根据API项目生成测试点"""
    try:
        result = await test_point_generator.generate_test_points(
            db=db,
            api_project_id=request.api_project_id
        )
        
        if not result["success"]:
            raise HTTPException(status_code=404, detail=result["message"])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成测试点失败: {str(e)}")

@router.get("/", response_model=List[TestPointResponse], summary="获取测试点列表", description="获取测试点列表")
async def get_test_points(
    project_id: int,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db_session)
):
    """获取指定项目的测试点列表"""
    try:
        result = await db.execute(
            select(TestPoint)
            .where(TestPoint.api_project_id == project_id)
            .offset(skip)
            .limit(limit)
        )
        test_points = result.scalars().all()
        return test_points
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取测试点列表失败: {str(e)}")

@router.get("/{test_point_id}", response_model=TestPointResponse, summary="获取测试点详情", description="获取指定测试点的详细信息")
async def get_test_point(
    test_point_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """获取指定测试点的详细信息"""
    test_point = await db.get(TestPoint, test_point_id)
    if not test_point:
        raise HTTPException(status_code=404, detail="测试点不存在")
    return test_point

@router.post("/", response_model=TestPointResponse, summary="创建测试点", description="手动创建测试点")
async def create_test_point(
    request: TestPointCreate,
    db: AsyncSession = Depends(get_db_session)
):
    """手动创建测试点"""
    try:
        # 转换测试类型和优先级枚举
        try:
            test_type = TestPointType(request.test_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"测试类型参数非法，可选值: {[e.value for e in TestPointType]}")
        try:
            priority = TestPointPriority(request.priority)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"优先级参数非法，可选值: {[e.value for e in TestPointPriority]}")
        
        # 创建测试点
        test_point = TestPoint(
            api_project_id=request.api_project_id,
            api_interface_id=request.api_interface_id,
            module=request.module,
            name=request.name,
            description=request.description,
            test_type=test_type,
            priority=priority,
            check_points=request.check_points,
            input_data=request.input_data,
            expected_result=request.expected_result,
            special_notes=request.special_notes,
            status=TestPointStatus.DRAFT
        )
        
        db.add(test_point)
        await db.commit()
        await db.refresh(test_point)
        
        return test_point
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建测试点失败: {str(e)}")

@router.put("/{test_point_id}", response_model=TestPointResponse, summary="更新测试点", description="更新测试点信息")
async def update_test_point(
    test_point_id: int,
    request: TestPointUpdate,
    db: AsyncSession = Depends(get_db_session)
):
    """更新测试点信息"""
    try:
        test_point = await db.get(TestPoint, test_point_id)
        if not test_point:
            raise HTTPException(status_code=404, detail="测试点不存在")
        
        # 更新测试点信息
        update_data = request.dict(exclude_unset=True)
        
        # 处理枚举类型
        if "test_type" in update_data:
            try:
                update_data["test_type"] = TestPointType(update_data["test_type"])
            except ValueError:
                raise HTTPException(status_code=400, detail=f"测试类型参数非法，可选值: {[e.value for e in TestPointType]}")
        
        if "priority" in update_data:
            try:
                update_data["priority"] = TestPointPriority(update_data["priority"])
            except ValueError:
                raise HTTPException(status_code=400, detail=f"优先级参数非法，可选值: {[e.value for e in TestPointPriority]}")
        
        if "status" in update_data:
            try:
                update_data["status"] = TestPointStatus(update_data["status"])
            except ValueError:
                raise HTTPException(status_code=400, detail=f"状态参数非法，可选值: {[e.value for e in TestPointStatus]}")
        
        # 更新字段
        for field, value in update_data.items():
            setattr(test_point, field, value)
        
        await db.commit()
        await db.refresh(test_point)
        
        return test_point
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新测试点失败: {str(e)}")

@router.delete("/{test_point_id}", summary="删除测试点", description="删除指定的测试点")
async def delete_test_point(
    test_point_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """删除指定的测试点"""
    try:
        test_point = await db.get(TestPoint, test_point_id)
        if not test_point:
            raise HTTPException(status_code=404, detail="测试点不存在")
        
        await db.delete(test_point)
        await db.commit()
        
        return {"message": "测试点删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除测试点失败: {str(e)}")

@router.put("/{test_point_id}/status", response_model=TestPointResponse, summary="更新测试点状态", description="更新测试点的状态")
async def update_test_point_status(
    test_point_id: int,
    request: TestPointStatusUpdateRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """更新测试点的状态"""
    try:
        test_point = await db.get(TestPoint, test_point_id)
        if not test_point:
            raise HTTPException(status_code=404, detail="测试点不存在")
        
        # 更新状态
        try:
            test_point.status = TestPointStatus(request.status)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"状态参数非法，可选值: {[e.value for e in TestPointStatus]}")
        
        # 更新评审意见
        if request.review_comments:
            if test_point.review_comments:
                # 如果已有评审意见，合并
                test_point.review_comments.update(request.review_comments)
            else:
                test_point.review_comments = request.review_comments
        
        await db.commit()
        await db.refresh(test_point)
        
        return test_point
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新测试点状态失败: {str(e)}")

@router.get("/project/{project_id}", response_model=List[TestPointResponse], summary="获取项目测试点", description="获取指定项目的所有测试点")
async def get_project_test_points(
    project_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """获取指定项目的所有测试点"""
    try:
        result = await db.execute(
            select(TestPoint)
            .where(TestPoint.api_project_id == project_id)
            .order_by(TestPoint.module, TestPoint.priority.desc())
        )
        test_points = result.scalars().all()
        return test_points
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取项目测试点失败: {str(e)}")

@router.get("/interface/{interface_id}", response_model=List[TestPointResponse], summary="获取接口测试点", description="获取指定接口的所有测试点")
async def get_interface_test_points(
    interface_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """获取指定接口的所有测试点"""
    try:
        result = await db.execute(
            select(TestPoint)
            .where(TestPoint.api_interface_id == interface_id)
            .order_by(TestPoint.module, TestPoint.priority.desc())
        )
        test_points = result.scalars().all()
        return test_points
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取接口测试点失败: {str(e)}")
