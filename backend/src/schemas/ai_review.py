from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class AIReviewRequest(BaseModel):
    """AI评审请求模型"""
    target_id: int = Field(..., description="评审对象ID")
    content: str = Field(..., description="评审内容")


class ReviewComment(BaseModel):
    """评审意见模型"""
    area: str = Field(..., description="关注领域")
    comment: str = Field(..., description="具体意见")
    severity: str = Field(..., description="严重程度", pattern="^(高|中|低)$")
    reviewer_role: Optional[str] = Field(None, description="评审专家角色")


class ReviewSuggestion(BaseModel):
    """改进建议模型"""
    area: str = Field(..., description="改进领域")
    suggestion: str = Field(..., description="具体建议")
    reviewer_role: Optional[str] = Field(None, description="评审专家角色")


class DetailedReviewResult(BaseModel):
    """详细评审结果模型"""
    result: str = Field(..., description="评审结果", pattern="^(PASSED|PARTIALLY_PASSED|FAILED)$")
    comments: List[ReviewComment] = Field(..., description="评审意见列表")
    suggestions: List[ReviewSuggestion] = Field(..., description="改进建议列表")


class AIReviewResponse(BaseModel):
    """AI评审响应模型"""
    success: bool = Field(..., description="评审是否成功")
    message: str = Field(..., description="评审结果消息")
    review_results: List[DetailedReviewResult] = Field(..., description="各专家评审结果列表")
    final_result: Dict[str, Any] = Field(..., description="合并后的最终评审结果")


class AIReviewHistoryItem(BaseModel):
    """评审历史记录项模型"""
    reviewer_role: str = Field(..., description="评审专家角色")
    review_result: str = Field(..., description="评审结果")
    review_comments: List[ReviewComment] = Field(..., description="评审意见列表")
    improvement_suggestions: List[ReviewSuggestion] = Field(..., description="改进建议列表")
    created_at: datetime = Field(..., description="评审时间")


class AIReviewHistoryResponse(BaseModel):
    """评审历史记录响应模型"""
    id: int = Field(..., description="评审记录ID")
    review_type: str = Field(..., description="评审类型")
    target_id: int = Field(..., description="评审对象ID")
    reviewer_role: str = Field(..., description="评审专家角色")
    review_result: str = Field(..., description="评审结果")
    review_comments: List[ReviewComment] = Field(..., description="评审意见列表")
    improvement_suggestions: List[ReviewSuggestion] = Field(..., description="改进建议列表")
    created_at: datetime = Field(..., description="评审时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True
