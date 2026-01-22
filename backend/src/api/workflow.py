from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional

from src.shared.database import get_db_session
from src.services.workflow.workflow_service import WorkflowService
from src.models.workflow import WorkflowStep, WorkflowStatus
from src.schemas.workflow import (
    WorkflowCreate, WorkflowStepUpdate, WorkflowResponse,
    WorkflowDetailResponse, WorkflowListResponse, WorkflowMetricsResponse
)

router = APIRouter(prefix="/api/v1/workflows", tags=["工作流管理"])

# 工作流服务实例
workflow_service = WorkflowService()

@router.post("/", response_model=WorkflowResponse, summary="创建工作流", description="创建新的工作流")
async def create_workflow(
    request: WorkflowCreate,
    db: AsyncSession = Depends(get_db_session)
):
    """创建新的工作流，关联到指定的API项目"""
    try:
        result = await workflow_service.create_workflow(
            db=db,
            api_project_id=request.api_project_id,
            name=request.name
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["message"])
        
        return result["workflow"]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建工作流失败: {str(e)}")

@router.get("/", response_model=WorkflowListResponse, summary="获取工作流列表", description="获取工作流列表，支持分页")
async def get_workflows(
    project_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db_session)
):
    """获取工作流列表，可通过项目ID过滤，支持分页"""
    try:
        result = await workflow_service.get_workflow_list(
            db=db,
            project_id=project_id,
            skip=skip,
            limit=limit
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["message"])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取工作流列表失败: {str(e)}")

@router.get("/{workflow_id}", response_model=WorkflowDetailResponse, summary="获取工作流详情", description="获取指定工作流的详细信息，包括执行日志和步骤记录")
async def get_workflow(
    workflow_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """获取指定工作流的详细信息，包括执行日志和步骤记录"""
    try:
        result = await workflow_service.get_workflow(
            db=db,
            workflow_id=workflow_id
        )
        
        if not result["success"]:
            raise HTTPException(status_code=404, detail=result["message"])
        
        return result["workflow"]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取工作流详情失败: {str(e)}")

@router.put("/{workflow_id}/step", response_model=WorkflowResponse, summary="更新工作流步骤", description="更新工作流的当前步骤状态")
async def update_workflow_step(
    workflow_id: int,
    request: WorkflowStepUpdate,
    db: AsyncSession = Depends(get_db_session)
):
    """更新工作流的当前步骤状态，包括完成、拒绝等操作"""
    try:
        # 转换步骤和状态为枚举类型
        step = WorkflowStep(request.step)
        status = WorkflowStatus(request.status)
        
        result = await workflow_service.update_workflow_step(
            db=db,
            workflow_id=workflow_id,
            step=step,
            status=status,
            result=request.result
        )
        
        if not result["success"]:
            raise HTTPException(status_code=404, detail=result["message"])
        
        return result["workflow"]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"无效的步骤或状态值: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新工作流步骤失败: {str(e)}")

@router.get("/metrics", response_model=WorkflowMetricsResponse, summary="获取工作流度量指标", description="获取工作流的度量指标，包括API项目、接口、测试点、测试用例、测试脚本的数量和采纳率等")
async def get_workflow_metrics(
    project_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db_session)
):
    """获取工作流的度量指标，包括API项目、接口、测试点、测试用例、测试脚本的数量和采纳率等"""
    try:
        result = await workflow_service.get_workflow_metrics(
            db=db,
            project_id=project_id
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["message"])
        
        return result["metrics"]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取工作流度量指标失败: {str(e)}")
