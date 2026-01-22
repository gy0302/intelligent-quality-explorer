from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class TestExecutionRequest(BaseModel):
    """测试执行请求模型"""
    script_ids: List[int] = Field(..., description="测试脚本ID列表")
    test_data_ids: Optional[List[int]] = Field(None, description="测试数据ID列表")
    

class SingleExecutionResult(BaseModel):
    """单个测试执行结果模型"""
    script_id: int = Field(..., description="测试脚本ID")
    test_case_id: int = Field(..., description="测试用例ID")
    case_name: str = Field(..., description="测试用例名称")
    script_type: str = Field(..., description="脚本类型")
    execution_status: str = Field(..., description="执行状态")
    actual_result: Optional[str] = Field(None, description="实际执行结果")
    executed_at: datetime = Field(..., description="执行时间")


class TestExecutionResult(BaseModel):
    """单个测试脚本执行结果模型"""
    script_id: int = Field(..., description="测试脚本ID")
    test_case_id: int = Field(..., description="测试用例ID")
    success: bool = Field(..., description="执行是否成功")
    output: str = Field(..., description="执行输出")
    error: Optional[str] = Field(None, description="执行错误")
    return_code: int = Field(..., description="返回码")
    executed_at: datetime = Field(..., description="执行时间")


class TestExecutionResponse(BaseModel):
    """测试执行响应模型"""
    success: bool = Field(..., description="执行是否成功")
    message: str = Field(..., description="执行结果消息")
    execution_results: List[TestExecutionResult] = Field(..., description="测试执行结果列表")


class TestExecutionResultResponse(BaseModel):
    """测试执行结果响应模型"""
    success: bool = Field(..., description="查询是否成功")
    message: str = Field(..., description="查询结果消息")
    execution_results: List[SingleExecutionResult] = Field(..., description="测试执行结果列表")


class InterfaceDimensionReport(BaseModel):
    """接口维度报告模型"""
    interface_id: int = Field(..., description="接口ID")
    path: str = Field(..., description="接口路径")
    method: str = Field(..., description="接口方法")
    description: Optional[str] = Field(None, description="接口描述")
    total_test_points: int = Field(..., description="总测试点数")
    total_test_cases: int = Field(..., description="总测试用例数")
    total_test_scripts: int = Field(..., description="总测试脚本数")
    execution_results: List[SingleExecutionResult] = Field(..., description="执行结果列表")
    passed_count: int = Field(..., description="通过数量")
    failed_count: int = Field(..., description="失败数量")


class CaseDimensionReport(BaseModel):
    """测试用例维度报告模型"""
    test_case_id: int = Field(..., description="测试用例ID")
    case_name: str = Field(..., description="测试用例名称")
    priority: str = Field(..., description="优先级")
    status: str = Field(..., description="状态")
    total_test_scripts: int = Field(..., description="总测试脚本数")
    execution_results: List[SingleExecutionResult] = Field(..., description="执行结果列表")
    execution_status: Optional[str] = Field(None, description="执行状态")
    passed_count: int = Field(..., description="通过数量")
    failed_count: int = Field(..., description="失败数量")


class ScriptDimensionReport(BaseModel):
    """测试脚本维度报告模型"""
    script_id: int = Field(..., description="测试脚本ID")
    script_type: str = Field(..., description="脚本类型")
    status: str = Field(..., description="状态")
    execution_results: List[SingleExecutionResult] = Field(..., description="执行结果列表")
    passed_count: int = Field(..., description="通过数量")
    failed_count: int = Field(..., description="失败数量")


class TestReportDetail(BaseModel):
    """测试报告详细内容模型"""
    project_id: int = Field(..., description="项目ID")
    project_name: str = Field(..., description="项目名称")
    report_date: datetime = Field(..., description="报告生成日期")
    summary: Dict[str, Any] = Field(..., description="测试摘要")
    execution_results: List[SingleExecutionResult] = Field(..., description="执行结果列表")
    total_scripts: int = Field(..., description="总脚本数")
    passed_count: int = Field(..., description="通过数量")
    failed_count: int = Field(..., description="失败数量")
    success_rate: float = Field(..., description="成功率")
    api_interfaces: List[Dict[str, Any]] = Field(..., description="API接口列表")
    test_points: List[Dict[str, Any]] = Field(..., description="测试点列表")
    test_cases: List[Dict[str, Any]] = Field(..., description="测试用例列表")
    test_scripts: List[Dict[str, Any]] = Field(..., description="测试脚本列表")
    interface_dimension: List[InterfaceDimensionReport] = Field(..., description="接口维度报告")
    case_dimension: List[CaseDimensionReport] = Field(..., description="测试用例维度报告")
    script_dimension: List[ScriptDimensionReport] = Field(..., description="测试脚本维度报告")


class TestReportResponse(BaseModel):
    """测试报告响应模型"""
    success: bool = Field(..., description="报告生成是否成功")
    message: str = Field(..., description="生成结果消息")
    report: TestReportDetail = Field(..., description="测试报告内容")


class TestReportExportRequest(BaseModel):
    """测试报告导出请求模型"""
    project_id: int = Field(..., description="项目ID")
    format: str = Field(..., description="报告格式", pattern="^(json|text)$")
