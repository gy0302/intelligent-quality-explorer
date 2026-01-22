from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional

from src.models.test_point import TestPoint
from src.shared.database import get_db_session
from src.services.test_case.generator import TestCaseGenerator
from src.models.test_case import TestCase, TestCaseStatus, TestCasePriority
from src.schemas.test_case import (
    TestCaseCreate, TestCaseUpdate, TestCaseResponse,
    TestCaseGenerateRequest, TestCaseGenerateResponse,
    TestCaseStatusUpdateRequest
)

router = APIRouter(prefix="/api/v1/test-cases", tags=["测试用例管理"])

# 测试用例生成服务实例
test_case_generator = TestCaseGenerator()

@router.post("/generate", response_model=TestCaseGenerateResponse, summary="生成测试用例", description="根据测试点生成测试用例")
async def generate_test_cases(
    request: TestCaseGenerateRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """根据测试点生成测试用例"""
    try:
        result = await test_case_generator.generate_test_cases(
            db=db,
            test_point_ids=request.test_point_ids
        )
        
        if not result["success"]:
            raise HTTPException(status_code=404, detail=result["message"])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成测试用例失败: {str(e)}")

@router.get("/", response_model=List[TestCaseResponse], summary="获取测试用例列表", description="获取测试用例列表，可通过测试点ID、项目ID或接口ID过滤")
async def get_test_cases(
    test_point_id: Optional[int] = None,
    project_id: Optional[int] = None,
    interface_id: Optional[int] = None,
    status: Optional[str] = None, 
    priority: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db_session)
):
    """获取测试用例列表，可通过测试点ID、项目ID或接口ID过滤"""
    try:
        # 构建查询条件
        query = select(TestCase).where(TestCase.is_active == True)
        
        if status:
            query = query.where(TestCase.status == TestCaseStatus(status))
        if priority:
            query = query.where(TestCase.priority == TestCasePriority(priority))
        
        if test_point_id:
            query = query.where(TestCase.test_point_id == test_point_id)
        elif project_id:
            # 通过项目ID查询，需要关联测试点表
            query = query.join(TestPoint).where(TestPoint.api_project_id == project_id)
        elif interface_id:
            # 通过接口ID查询，需要关联测试点表
            query = query.join(TestPoint).where(TestPoint.api_interface_id == interface_id)
        
        result = await db.execute(
            query.offset(skip).limit(limit)
        )
        test_cases = result.scalars().all()
        return test_cases
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取测试用例列表失败: {str(e)}")

@router.get("/{test_case_id}", response_model=TestCaseResponse, summary="获取测试用例详情", description="获取指定测试用例的详细信息")
async def get_test_case(
    test_case_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """获取指定测试用例的详细信息"""
    test_case = await db.get(TestCase, test_case_id)
    if not test_case:
        raise HTTPException(status_code=404, detail="测试用例不存在")
    return test_case

@router.post("/", response_model=TestCaseResponse, summary="创建测试用例", description="手动创建测试用例")
async def create_test_case(
    request: TestCaseCreate,
    db: AsyncSession = Depends(get_db_session)
):
    """手动创建测试用例"""
    try:
        # 检查测试点是否存在
        test_point = await db.get(TestPoint, request.test_point_id)
        if not test_point:
            raise HTTPException(status_code=404, detail="测试点不存在")
        
        # 转换优先级枚举
        try:
            priority = TestCasePriority(request.priority)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"优先级参数非法，可选值: {[e.value for e in TestCasePriority]}")
        
        # 创建测试用例
        test_case = TestCase(
            test_point_id=request.test_point_id,
            case_name=request.case_name,
            description=request.description,
            steps=request.steps,
            input_data=request.input_data,
            expected_result=request.expected_result,
            priority=priority,
            status=TestCaseStatus.DRAFT
        )
        
        db.add(test_case)
        await db.commit()
        await db.refresh(test_case)
        
        return test_case
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建测试用例失败: {str(e)}")

@router.put("/{test_case_id}", response_model=TestCaseResponse, summary="更新测试用例", description="更新测试用例信息")
async def update_test_case(
    test_case_id: int,
    request: TestCaseUpdate,
    db: AsyncSession = Depends(get_db_session)
):
    """更新测试用例信息"""
    try:
        test_case = await db.get(TestCase, test_case_id)
        if not test_case:
            raise HTTPException(status_code=404, detail="测试用例不存在")
        
        # 更新测试用例信息
        update_data = request.dict(exclude_unset=True)
        
        # 处理枚举类型
        if "priority" in update_data:
            try:
                update_data["priority"] = TestCasePriority(update_data["priority"])
            except ValueError:
                raise HTTPException(status_code=400, detail=f"优先级参数非法，可选值: {[e.value for e in TestCasePriority]}")
        
        if "status" in update_data:
            try:
                update_data["status"] = TestCaseStatus(update_data["status"])
            except ValueError:
                raise HTTPException(status_code=400, detail=f"状态参数非法，可选值: {[e.value for e in TestCaseStatus]}")
        
        # 更新字段
        for field, value in update_data.items():
            setattr(test_case, field, value)
        
        await db.commit()
        await db.refresh(test_case)
        
        return test_case
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新测试用例失败: {str(e)}")

@router.delete("/{test_case_id}", summary="删除测试用例", description="删除指定的测试用例")
async def delete_test_case(
    test_case_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """删除指定的测试用例"""
    try:
        test_case = await db.get(TestCase, test_case_id)
        if not test_case:
            raise HTTPException(status_code=404, detail="测试用例不存在")
        
        test_case.is_active = False
        await db.commit()
        await db.refresh(test_case)

        
        return {"message": "测试用例删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除测试用例失败: {str(e)}")

@router.put("/{test_case_id}/status", response_model=TestCaseResponse, summary="更新测试用例状态", description="更新测试用例的状态")
async def update_test_case_status(
    test_case_id: int,
    request: TestCaseStatusUpdateRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """更新测试用例的状态，包括评审状态和执行状态"""
    try:
        test_case = await db.get(TestCase, test_case_id)
        if not test_case:
            raise HTTPException(status_code=404, detail="测试用例不存在")
        
        # 更新状态
        try:
            test_case.status = TestCaseStatus(request.status)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"状态参数非法，可选值: {[e.value for e in TestCaseStatus]}")
        
        # 更新执行状态
        if request.execution_status:
            test_case.execution_status = request.execution_status
        
        # 更新评审意见
        if request.review_comments:
            if test_case.review_comments:
                # 如果已有评审意见，合并
                test_case.review_comments.update(request.review_comments)
            else:
                test_case.review_comments = request.review_comments
        
        await db.commit()
        await db.refresh(test_case)
        
        return test_case
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新测试用例状态失败: {str(e)}")

@router.delete("/batch", summary="批量删除测试用例", description="批量软删除测试用例")
async def batch_delete_test_cases(
    case_ids: List[int],
    db: AsyncSession = Depends(get_db_session)
):
    try:
        await db.execute(update(TestCase).where(TestCase.id.in_(case_ids)).values(is_active=False))
        await db.commit()
        return {"message": f"成功删除{len(case_ids)}条测试用例"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量删除测试用例失败: {str(e)}")