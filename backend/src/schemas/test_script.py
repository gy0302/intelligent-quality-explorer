from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class TestDataBase(BaseModel):
    """测试数据基础模型"""
    data_name: str = Field(..., description="数据名称")
    data_type: str = Field(..., description="数据类型")
    data_content: Dict[str, Any] = Field(..., description="数据内容")
    description: Optional[str] = Field(None, description="数据描述")


class TestDataCreate(TestDataBase):
    """创建测试数据请求模型"""
    test_script_id: int = Field(..., description="测试脚本ID")


class TestDataResponse(TestDataBase):
    """测试数据响应模型"""
    id: int = Field(..., description="测试数据ID")
    test_script_id: int = Field(..., description="测试脚本ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    created_by: str = Field(..., description="创建人")
    updated_by: str = Field(..., description="更新人")

    class Config:
        from_attributes = True


class TestScriptBase(BaseModel):
    """测试脚本基础模型"""
    script_type: str = Field(..., description="脚本类型", pattern="^(python|java|javascript|other)$")
    script_content: str = Field(..., description="脚本内容")


class TestScriptCreate(TestScriptBase):
    """创建测试脚本请求模型"""
    test_case_id: int = Field(..., description="测试用例ID")


class TestScriptUpdate(BaseModel):
    """更新测试脚本请求模型"""
    script_type: Optional[str] = Field(None, description="脚本类型", pattern="^(python|java|javascript|other)$")
    script_content: Optional[str] = Field(None, description="脚本内容")
    status: Optional[str] = Field(None, description="脚本状态", pattern="^(draft|ai_reviewed|manual_reviewed|approved|rejected)$")
    review_comments: Optional[Dict[str, Any]] = Field(None, description="评审意见")


class TestScriptResponse(TestScriptBase):
    """测试脚本响应模型"""
    id: int = Field(..., description="测试脚本ID")
    test_case_id: int = Field(..., description="测试用例ID")
    status: str = Field(..., description="脚本状态")
    review_comments: Optional[Dict[str, Any]] = Field(None, description="评审意见")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    created_by: str = Field(..., description="创建人")
    updated_by: str = Field(..., description="更新人")
    test_data: List[TestDataResponse] = Field([], description="关联的测试数据列表")

    class Config:
        from_attributes = True


class TestScriptGenerateRequest(BaseModel):
    """生成测试脚本请求模型"""
    test_case_ids: List[int] = Field(..., description="测试用例ID列表")


class TestScriptGenerateResponse(BaseModel):
    """生成测试脚本响应模型"""
    success: bool = Field(..., description="生成是否成功")
    message: str = Field(..., description="生成结果消息")
    generated_count: int = Field(..., description="生成的测试脚本数量")
    test_scripts: List[Dict[str, Any]] = Field(..., description="生成的测试脚本列表")


class TestScriptStatusUpdateRequest(BaseModel):
    """更新测试脚本状态请求模型"""
    status: str = Field(..., description="新的脚本状态", pattern="^(draft|ai_reviewed|manual_reviewed|approved|rejected)$")
    review_comments: Optional[Dict[str, Any]] = Field(None, description="评审意见")
