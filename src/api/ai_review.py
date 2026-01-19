from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any

from src.shared.database import get_db_session
from src.services.ai_review.review_service import AIReviewService
from src.models.ai_review import ReviewType
from src.schemas.ai_review import (
    AIReviewRequest, AIReviewResponse, AIReviewHistoryResponse
)

router = APIRouter(prefix="/api/v1/ai-review", tags=["AI评审"])

# AI评审服务实例
ai_review_service = AIReviewService()

@router.post("/api", response_model=AIReviewResponse, summary="执行API评审", description="对API设计和规范进行AI评审")
async def review_api(
    request: AIReviewRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """对API设计和规范进行AI评审"""
    try:
        result = await ai_review_service.perform_review(
            db=db,
            review_type=ReviewType.API_REVIEW,
            target_id=request.target_id,
            content=request.content
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["message"])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI评审失败: {str(e)}")

@router.post("/test-points", response_model=AIReviewResponse, summary="执行测试点评审", description="对测试点进行AI评审")
async def review_test_points(
    request: AIReviewRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """对测试点进行AI评审"""
    try:
        result = await ai_review_service.perform_review(
            db=db,
            review_type=ReviewType.TEST_POINT_REVIEW,
            target_id=request.target_id,
            content=request.content
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["message"])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI评审失败: {str(e)}")

@router.post("/test-cases", response_model=AIReviewResponse, summary="执行测试用例评审", description="对测试用例进行AI评审")
async def review_test_cases(
    request: AIReviewRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """对测试用例进行AI评审"""
    try:
        result = await ai_review_service.perform_review(
            db=db,
            review_type=ReviewType.TEST_CASE_REVIEW,
            target_id=request.target_id,
            content=request.content
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["message"])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI评审失败: {str(e)}")

@router.post("/test-scripts", response_model=AIReviewResponse, summary="执行测试脚本评审", description="对测试脚本进行AI评审")
async def review_test_scripts(
    request: AIReviewRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """对测试脚本进行AI评审"""
    try:
        result = await ai_review_service.perform_review(
            db=db,
            review_type=ReviewType.TEST_SCRIPT_REVIEW,
            target_id=request.target_id,
            content=request.content
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["message"])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI评审失败: {str(e)}")

@router.get("/history/api/{target_id}", response_model=List[AIReviewHistoryResponse], summary="获取API评审历史", description="获取指定API的评审历史记录")
async def get_api_review_history(
    target_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """获取指定API的评审历史记录"""
    try:
        return await ai_review_service.get_review_history(
            db=db,
            review_type=ReviewType.API_REVIEW,
            target_id=target_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取评审历史失败: {str(e)}")

@router.get("/history/test-points/{target_id}", response_model=List[AIReviewHistoryResponse], summary="获取测试点评审历史", description="获取指定测试点的评审历史记录")
async def get_test_point_review_history(
    target_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """获取指定测试点的评审历史记录"""
    try:
        return await ai_review_service.get_review_history(
            db=db,
            review_type=ReviewType.TEST_POINT_REVIEW,
            target_id=target_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取评审历史失败: {str(e)}")

@router.get("/history/test-cases/{target_id}", response_model=List[AIReviewHistoryResponse], summary="获取测试用例评审历史", description="获取指定测试用例的评审历史记录")
async def get_test_case_review_history(
    target_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """获取指定测试用例的评审历史记录"""
    try:
        return await ai_review_service.get_review_history(
            db=db,
            review_type=ReviewType.TEST_CASE_REVIEW,
            target_id=target_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取评审历史失败: {str(e)}")

@router.get("/history/test-scripts/{target_id}", response_model=List[AIReviewHistoryResponse], summary="获取测试脚本评审历史", description="获取指定测试脚本的评审历史记录")
async def get_test_script_review_history(
    target_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """获取指定测试脚本的评审历史记录"""
    try:
        return await ai_review_service.get_review_history(
            db=db,
            review_type=ReviewType.TEST_SCRIPT_REVIEW,
            target_id=target_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取评审历史失败: {str(e)}")
