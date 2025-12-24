"""
OpenAPI规范领域模型
作用：定义API规范的核心数据结构，业务逻辑的载体
"""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Union
from enum import Enum
from pydantic import BaseModel, Field


class HTTPMethod(str, Enum):
    """HTTP方法枚举"""
    GET = "get"
    POST = "post"
    PUT = "put"
    DELETE = "delete"
    PATCH = "patch"
    HEAD = "head"
    OPTIONS = "options"


@dataclass
class APIParameter:
    """API参数值对象"""
    name: str
    location: str  # query, path, header, cookie
    required: bool = False
    schema: Optional[Dict[str, Any]] = None
    description: Optional[str] = None

    def is_path_parameter(self) -> bool:
        """是否为路径参数"""
        return self.location == "path"

    def is_required_parameter(self) -> bool:
        """是否为必填参数"""
        return self.required


@dataclass
class APIResponse:
    """API响应值对象"""
    status_code: str
    description: str
    schema: Optional[Dict[str, Any]] = None
    headers: Optional[Dict[str, Any]] = None

    def is_success_response(self) -> bool:
        """是否为成功响应"""
        return self.status_code.startswith('2')

    def is_error_response(self) -> bool:
        """是否为错误响应"""
        return self.status_code.startswith('4') or self.status_code.startswith('5')


@dataclass
class APIOperation:
    """API操作实体"""
    path: str
    method: HTTPMethod
    operation_id: Optional[str] = None
    summary: Optional[str] = None
    description: Optional[str] = None
    parameters: List[APIParameter] = field(default_factory=list)
    request_body: Optional[Dict[str, Any]] = None
    responses: Dict[str, APIResponse] = field(default_factory=dict)
    security: Optional[List[Dict[str, Any]]] = None
    tags: List[str] = field(default_factory=list)

    def get_required_parameters(self) -> List[APIParameter]:
        """获取所有必填参数"""
        return [p for p in self.parameters if p.required]

    def get_path_parameters(self) -> List[APIParameter]:
        """获取路径参数"""
        return [p for p in self.parameters if p.location == "path"]

    def get_success_responses(self) -> Dict[str, APIResponse]:
        """获取成功响应"""
        return {k: v for k, v in self.responses.items() if v.is_success_response()}

    def get_error_responses(self) -> Dict[str, APIResponse]:
        """获取错误响应"""
        return {k: v for k, v in self.responses.items() if v.is_error_response()}

    def calculate_complexity_score(self) -> float:
        """计算接口复杂度分数（0-1）"""
        score = 0.0

        # 参数数量因素
        param_factor = min(len(self.parameters) * 0.05, 0.2)
        score += param_factor

        # 必填参数因素
        required_factor = min(len(self.get_required_parameters()) * 0.1, 0.2)
        score += required_factor

        # 请求体因素
        if self.request_body:
            score += 0.2

        # 响应数量因素
        response_factor = min(len(self.responses) * 0.03, 0.15)
        score += response_factor

        # 安全因素
        if self.security:
            score += 0.1

        return min(score, 1.0)


@dataclass
class OpenAPISpecification:
    """OpenAPI规范聚合根"""
    title: str
    version: str
    description: Optional[str] = None
    base_url: Optional[str] = None
    operations: List[APIOperation] = field(default_factory=list)

    def get_operation_by_id(self, operation_id: str) -> Optional[APIOperation]:
        """根据操作ID查找操作"""
        for op in self.operations:
            if op.operation_id == operation_id:
                return op
        return None

    def get_operations_by_tag(self, tag: str) -> List[APIOperation]:
        """根据标签查找操作"""
        return [op for op in self.operations if tag in op.tags]

    def get_operations_by_method(self, method: HTTPMethod) -> List[APIOperation]:
        """根据HTTP方法查找操作"""
        return [op for op in self.operations if op.method == method]

    def get_all_paths(self) -> List[str]:
        """获取所有路径"""
        return list({op.path for op in self.operations})

    def calculate_coverage_stats(self, test_points) -> Dict[str, float]:
        """计算测试覆盖率统计"""
        covered_operations = set()
        covered_paths = set()

        for test_point in test_points:
            if hasattr(test_point, 'operation_id'):
                for op in self.operations:
                    if op.operation_id == test_point.operation_id:
                        covered_operations.add(op)
                        covered_paths.add(op.path)

        total_operations = len(self.operations)
        total_paths = len(self.get_all_paths())

        return {
            "operation_coverage": len(covered_operations) / total_operations if total_operations > 0 else 0,
            "path_coverage": len(covered_paths) / total_paths if total_paths > 0 else 0,
            "covered_operations": len(covered_operations),
            "covered_paths": len(covered_paths),
            "total_operations": total_operations,
            "total_paths": total_paths,
        }