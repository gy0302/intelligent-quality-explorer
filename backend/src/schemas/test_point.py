from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class TestPointBase(BaseModel):
    """测试点基础模型"""
    module: str = Field(..., description="模块名称")
    name: str = Field(..., description="测试点名称")
    description: Optional[str] = Field(None, description="测试点描述")
    test_type: str = Field(..., description="测试类型", pattern="^(functional|performance|security|compatibility|reliability|usability)$")
    priority: str = Field(..., description="测试优先级", pattern="^(high|medium|low)$")
    check_points: List[str] = Field(..., description="测试检查点")
    input_data: Optional[Dict[str, Any]] = Field(None, description="输入数据")
    expected_result: Optional[Dict[str, Any]] = Field(None, description="预期结果")
    special_notes: Optional[str] = Field(None, description="特殊说明")


class TestPointCreate(TestPointBase):
    """创建测试点请求模型"""
    api_project_id: int = Field(..., description="API项目ID")
    api_interface_id: Optional[int] = Field(None, description="API接口ID")


class TestPointUpdate(BaseModel):
    """更新测试点请求模型"""
    module: Optional[str] = Field(None, description="模块名称")
    name: Optional[str] = Field(None, description="测试点名称")
    description: Optional[str] = Field(None, description="测试点描述")
    test_type: Optional[str] = Field(None, description="测试类型", pattern="^(functional|performance|security|compatibility|reliability|usability)$")
    priority: Optional[str] = Field(None, description="测试优先级", pattern="^(high|medium|low)$")
    check_points: Optional[List[str]] = Field(None, description="测试检查点")
    input_data: Optional[Dict[str, Any]] = Field(None, description="输入数据")
    expected_result: Optional[Dict[str, Any]] = Field(None, description="预期结果")
    status: Optional[str] = Field(None, description="测试点状态", pattern="^(draft|ai_reviewed|manual_reviewed|approved|rejected)$")
    review_comments: Optional[Dict[str, Any]] = Field(None, description="评审意见")
    special_notes: Optional[str] = Field(None, description="特殊说明")


class TestPointResponse(TestPointBase):
    """测试点响应模型"""
    id: int = Field(..., description="测试点ID")
    api_project_id: int = Field(..., description="API项目ID")
    api_interface_id: Optional[int] = Field(None, description="API接口ID")
    status: str = Field(..., description="测试点状态")
    review_comments: Optional[Dict[str, Any]] = Field(None, description="评审意见")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    created_by: str = Field(..., description="创建人")
    updated_by: str = Field(..., description="更新人")

    class Config:
        from_attributes = True


class TestPointGenerateRequest(BaseModel):
    """生成测试点请求模型"""
    api_project_id: int = Field(..., description="API项目ID")


class TestPointGenerateResponse(BaseModel):
    """生成测试点响应模型"""
    success: bool = Field(..., description="生成是否成功")
    message: str = Field(..., description="生成结果消息")
    project_id: int = Field(..., description="项目ID")
    generated_count: int = Field(..., description="生成的测试点数量")
    test_points: List[Dict[str, Any]] = Field(..., description="生成的测试点列表")


class TestPointStatusUpdateRequest(BaseModel):
    """更新测试点状态请求模型"""
    status: str = Field(..., description="新的测试点状态", pattern="^(draft|ai_reviewed|manual_reviewed|approved|rejected)$")
    review_comments: Optional[Dict[str, Any]] = Field(None, description="评审意见")
