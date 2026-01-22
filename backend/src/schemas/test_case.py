from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class TestCaseBase(BaseModel):
    """测试用例基础模型"""
    case_name: str = Field(..., description="测试用例名称")
    description: Optional[str] = Field(None, description="测试用例描述")
    steps: List[str] = Field(..., description="测试步骤")
    input_data: Dict[str, Any] = Field(..., description="输入数据")
    expected_result: Dict[str, Any] = Field(..., description="预期结果")
    priority: str = Field(..., description="测试优先级", pattern="^(high|medium|low)$")


class TestCaseCreate(TestCaseBase):
    """创建测试用例请求模型"""
    test_point_id: int = Field(..., description="测试点ID")


class TestCaseUpdate(BaseModel):
    """更新测试用例请求模型"""
    case_name: Optional[str] = Field(None, description="测试用例名称")
    description: Optional[str] = Field(None, description="测试用例描述")
    steps: Optional[List[str]] = Field(None, description="测试步骤")
    input_data: Optional[Dict[str, Any]] = Field(None, description="输入数据")
    expected_result: Optional[Dict[str, Any]] = Field(None, description="预期结果")
    actual_result: Optional[Dict[str, Any]] = Field(None, description="实际结果")
    priority: Optional[str] = Field(None, description="测试优先级", pattern="^(high|medium|low)$")
    status: Optional[str] = Field(None, description="测试用例状态", pattern="^(draft|ai_reviewed|manual_reviewed|approved|rejected)$")
    execution_status: Optional[str] = Field(None, description="执行状态")
    review_comments: Optional[Dict[str, Any]] = Field(None, description="评审意见")


class TestCaseResponse(TestCaseBase):
    """测试用例响应模型"""
    id: int = Field(..., description="测试用例ID")
    test_point_id: int = Field(..., description="测试点ID")
    actual_result: Optional[Dict[str, Any]] = Field(None, description="实际结果")
    status: str = Field(..., description="测试用例状态")
    execution_status: Optional[str] = Field(None, description="执行状态")
    review_comments: Optional[Dict[str, Any]] = Field(None, description="评审意见")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    created_by: str = Field(..., description="创建人")
    updated_by: str = Field(..., description="更新人")

    class Config:
        from_attributes = True


class TestCaseGenerateRequest(BaseModel):
    """生成测试用例请求模型"""
    test_point_ids: List[int] = Field(..., description="测试点ID列表")


class TestCaseGenerateResponse(BaseModel):
    """生成测试用例响应模型"""
    success: bool = Field(..., description="生成是否成功")
    message: str = Field(..., description="生成结果消息")
    generated_count: int = Field(..., description="生成的测试用例数量")
    test_cases: List[Dict[str, Any]] = Field(..., description="生成的测试用例列表")


class TestCaseStatusUpdateRequest(BaseModel):
    """更新测试用例状态请求模型"""
    status: str = Field(..., description="新的测试用例状态", pattern="^(draft|ai_reviewed|manual_reviewed|approved|rejected)$")
    review_comments: Optional[Dict[str, Any]] = Field(None, description="评审意见")
    execution_status: Optional[str] = Field(None, description="执行状态")
