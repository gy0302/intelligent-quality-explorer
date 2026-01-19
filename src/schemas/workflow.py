from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class WorkflowCreate(BaseModel):
    """创建工作流请求模型"""
    api_project_id: int = Field(..., description="API项目ID")
    name: str = Field(..., description="工作流名称")


class WorkflowStepUpdate(BaseModel):
    """更新工作流步骤请求模型"""
    step: str = Field(..., description="工作流步骤")
    status: str = Field(..., description="步骤状态")
    result: Optional[Dict[str, Any]] = Field(None, description="步骤结果")


class WorkflowResponse(BaseModel):
    """工作流响应模型"""
    id: int = Field(..., description="工作流ID")
    api_project_id: int = Field(..., description="API项目ID")
    name: str = Field(..., description="工作流名称")
    current_step: str = Field(..., description="当前步骤")
    status: str = Field(..., description="工作流状态")
    progress: int = Field(..., description="工作流进度(%)")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True


class WorkflowDetailResponse(WorkflowResponse):
    """工作流详情响应模型"""
    execution_log: Optional[List[Dict[str, Any]]] = Field(None, description="执行日志")
    step_records: Optional[List[Dict[str, Any]]] = Field(None, description="步骤记录")


class WorkflowListResponse(BaseModel):
    """工作流列表响应模型"""
    workflows: List[WorkflowResponse] = Field(..., description="工作流列表")
    total_count: int = Field(..., description="总记录数")
    skip: int = Field(..., description="跳过的记录数")
    limit: int = Field(..., description="返回的记录数")


class WorkflowMetricsResponse(BaseModel):
    """工作流度量指标响应模型"""
    api_projects_count: int = Field(..., description="API项目数量")
    api_interfaces_count: int = Field(..., description="API接口数量")
    test_points_count: int = Field(..., description="测试点数量")
    test_cases_count: int = Field(..., description="测试用例数量")
    test_scripts_count: int = Field(..., description="测试脚本数量")
    workflows_count: int = Field(..., description="工作流数量")
    completed_workflows_count: int = Field(..., description="已完成工作流数量")
    failed_workflows_count: int = Field(..., description="失败工作流数量")
    average_completion_time: float = Field(..., description="平均完成时间")
    adoption_rate: Dict[str, float] = Field(..., description="采纳率")


class WorkflowStepRecordResponse(BaseModel):
    """工作流步骤记录响应模型"""
    step: str = Field(..., description="步骤")
    status: str = Field(..., description="状态")
    start_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    duration: Optional[int] = Field(None, description="持续时间(秒)")
    result: Optional[Dict[str, Any]] = Field(None, description="步骤结果")
    comments: Optional[str] = Field(None, description="步骤备注")
