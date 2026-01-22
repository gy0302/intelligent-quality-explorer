from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, join
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional

from src.models.test_case import TestCase
from src.models.test_point import TestPoint
from src.shared.database import get_db_session
from src.services.test_script.generator import TestScriptGenerator
from src.models.test_script import TestScript, TestData, TestScriptType, TestScriptStatus
from src.schemas.test_script import (
    TestScriptCreate, TestScriptUpdate, TestScriptResponse,
    TestScriptGenerateRequest, TestScriptGenerateResponse,
    TestScriptStatusUpdateRequest,
    TestDataCreate, TestDataResponse
)

router = APIRouter(prefix="/api/v1/test-scripts", tags=["测试脚本管理"])

# 测试脚本生成服务实例
test_script_generator = TestScriptGenerator()

@router.post("/generate", response_model=TestScriptGenerateResponse, summary="生成测试脚本和测试数据", description="根据测试用例生成测试脚本和测试数据")
async def generate_test_scripts(
    request: TestScriptGenerateRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """根据测试用例生成测试脚本和测试数据"""
    try:
        result = await test_script_generator.generate_test_scripts(
            db=db,
            test_case_ids=request.test_case_ids
        )
        
        if not result["success"]:
            raise HTTPException(status_code=404, detail=result["message"])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成测试脚本失败: {str(e)}")

@router.get("/", response_model=List[TestScriptResponse], summary="获取测试脚本列表", description="获取测试脚本列表，可通过测试用例ID、项目ID或接口ID过滤")
async def get_test_scripts(
    test_case_id: Optional[int] = None,
    project_id: Optional[int] = None,
    interface_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db_session)
):
    """获取测试脚本列表，可通过测试用例ID、项目ID或接口ID过滤"""
    try:
        # 构建查询条件
        query = select(TestScript)
        
        if test_case_id:
            query = query.where(TestScript.test_case_id == test_case_id)
        elif project_id:
            # 通过项目ID查询，需要关联测试用例和测试点表
            query = query.join(TestCase).join(TestPoint).where(TestPoint.api_project_id == project_id)
        elif interface_id:
            # 通过接口ID查询，需要关联测试用例和测试点表
            query = query.join(TestCase).join(TestPoint).where(TestPoint.api_interface_id == interface_id)
        
        result = await db.execute(
            query.offset(skip).limit(limit)
        )
        test_scripts = result.scalars().all()
        return test_scripts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取测试脚本列表失败: {str(e)}")

@router.get("/{test_script_id}", response_model=TestScriptResponse, summary="获取测试脚本详情", description="获取指定测试脚本的详细信息，包括关联的测试数据")
async def get_test_script(
    test_script_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """获取指定测试脚本的详细信息，包括关联的测试数据"""
    test_script = await db.get(TestScript, test_script_id)
    if not test_script:
        raise HTTPException(status_code=404, detail="测试脚本不存在")
    return test_script

@router.post("/", response_model=TestScriptResponse, summary="创建测试脚本", description="手动创建测试脚本")
async def create_test_script(
    request: TestScriptCreate,
    db: AsyncSession = Depends(get_db_session)
):
    """手动创建测试脚本"""
    try:
        # 检查测试用例是否存在
        test_case = await db.get(TestCase, request.test_case_id)
        if not test_case:
            raise HTTPException(status_code=404, detail="测试用例不存在")
        
        # 转换脚本类型枚举
        try:
            script_type = TestScriptType(request.script_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"脚本类型参数非法，可选值: {[e.value for e in TestScriptType]}")
        
        # 创建测试脚本
        test_script = TestScript(
            test_case_id=request.test_case_id,
            script_type=script_type,
            script_content=request.script_content,
            status=TestScriptStatus.DRAFT
        )
        
        db.add(test_script)
        await db.commit()
        await db.refresh(test_script)
        
        return test_script
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建测试脚本失败: {str(e)}")

@router.put("/{test_script_id}", response_model=TestScriptResponse, summary="更新测试脚本", description="更新测试脚本信息")
async def update_test_script(
    test_script_id: int,
    request: TestScriptUpdate,
    db: AsyncSession = Depends(get_db_session)
):
    """更新测试脚本信息"""
    try:
        test_script = await db.get(TestScript, test_script_id)
        if not test_script:
            raise HTTPException(status_code=404, detail="测试脚本不存在")
        
        # 更新测试脚本信息
        update_data = request.dict(exclude_unset=True)
        
        # 处理枚举类型
        if "script_type" in update_data:
            try:
                update_data["script_type"] = TestScriptType(update_data["script_type"])
            except ValueError:
                raise HTTPException(status_code=400, detail=f"脚本类型参数非法，可选值: {[e.value for e in TestScriptType]}")
        
        if "status" in update_data:
            try:
                update_data["status"] = TestScriptStatus(update_data["status"])
            except ValueError:
                raise HTTPException(status_code=400, detail=f"状态参数非法，可选值: {[e.value for e in TestScriptStatus]}")
        
        # 更新字段
        for field, value in update_data.items():
            setattr(test_script, field, value)
        
        await db.commit()
        await db.refresh(test_script)
        
        return test_script
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新测试脚本失败: {str(e)}")

@router.delete("/{test_script_id}", summary="删除测试脚本", description="删除指定的测试脚本及其关联的测试数据")
async def delete_test_script(
    test_script_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """删除指定的测试脚本及其关联的测试数据"""
    try:
        test_script = await db.get(TestScript, test_script_id)
        if not test_script:
            raise HTTPException(status_code=404, detail="测试脚本不存在")
        
        await db.delete(test_script)
        await db.commit()
        
        return {"message": "测试脚本删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除测试脚本失败: {str(e)}")

@router.put("/{test_script_id}/status", response_model=TestScriptResponse, summary="更新测试脚本状态", description="更新测试脚本的状态")
async def update_test_script_status(
    test_script_id: int,
    request: TestScriptStatusUpdateRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """更新测试脚本的状态，包括评审状态"""
    try:
        test_script = await db.get(TestScript, test_script_id)
        if not test_script:
            raise HTTPException(status_code=404, detail="测试脚本不存在")
        
        # 更新状态
        try:
            test_script.status = TestScriptStatus(request.status)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"状态参数非法，可选值: {[e.value for e in TestScriptStatus]}")
        
        # 更新评审意见
        if request.review_comments:
            if test_script.review_comments:
                # 如果已有评审意见，合并
                test_script.review_comments.update(request.review_comments)
            else:
                test_script.review_comments = request.review_comments
        
        await db.commit()
        await db.refresh(test_script)
        
        return test_script
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新测试脚本状态失败: {str(e)}")

# 测试数据相关接口
@router.get("/{test_script_id}/test-data", response_model=List[TestDataResponse], summary="获取测试数据列表", description="获取指定测试脚本的测试数据列表")
async def get_test_data_list(
    test_script_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """获取指定测试脚本的测试数据列表"""
    try:                                                                
        result = await db.execute(
            select(TestData).where(TestData.test_script_id == test_script_id)
        )
        test_data_list = result.scalars().all()
        return test_data_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取测试数据列表失败: {str(e)}")

@router.post("/test-data", response_model=TestDataResponse, summary="创建测试数据", description="手动创建测试数据")
async def create_test_data(
    request: TestDataCreate,
    db: AsyncSession = Depends(get_db_session)
):
    """手动创建测试数据"""
    try:
        # 检查测试脚本是否存在
        test_script = await db.get(TestScript, request.test_script_id)
        if not test_script:
            raise HTTPException(status_code=404, detail="测试脚本不存在")
        
        # 创建测试数据
        test_data = TestData(
            test_script_id=request.test_script_id,
            data_name=request.data_name,
            data_type=request.data_type,
            data_content=request.data_content,
            description=request.description
        )
        
        db.add(test_data)
        await db.commit()
        await db.refresh(test_data)
        
        return test_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建测试数据失败: {str(e)}")

@router.get("/test-data", response_model=List[TestDataResponse], summary="获取测试数据列表", description="获取测试数据列表，可通过接口ID过滤")
async def get_test_data_list_by_filter(
    interface_id: Optional[int] = None,
    test_script_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db_session)
):
    """获取测试数据列表，可通过接口ID或测试脚本ID过滤"""
    try:
        # 构建查询条件
        query = select(TestData)
        
        if test_script_id:
            # 通过测试脚本ID查询
            query = query.where(TestData.test_script_id == test_script_id)
        elif interface_id:
            # 通过接口ID查询，需要关联测试脚本、测试用例和测试点表
            query = query.join(TestScript).join(TestCase).join(TestPoint).where(TestPoint.api_interface_id == interface_id)
        
        result = await db.execute(
            query.offset(skip).limit(limit)
        )
        test_data_list = result.scalars().all()
        return test_data_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取测试数据列表失败: {str(e)}")

@router.get("/test-data/{test_data_id}", response_model=TestDataResponse, summary="获取测试数据详情", description="获取指定测试数据的详细信息")
async def get_test_data(
    test_data_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """获取指定测试数据的详细信息"""
    test_data = await db.get(TestData, test_data_id)
    if not test_data:
        raise HTTPException(status_code=404, detail="测试数据不存在")
    return test_data

@router.delete("/test-data/{test_data_id}", summary="删除测试数据", description="删除指定的测试数据")
async def delete_test_data(
    test_data_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """删除指定的测试数据"""
    try:
        test_data = await db.get(TestData, test_data_id)
        if not test_data:
            raise HTTPException(status_code=404, detail="测试数据不存在")
        
        await db.delete(test_data)
        await db.commit()
        
        return {"message": "测试数据删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除测试数据失败: {str(e)}")
