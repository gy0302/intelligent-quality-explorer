"""
智能测试领域包初始化
作用：定义领域层公共接口，支持领域模型导入
"""
from .models.specification import (
    HTTPMethod,
    APIParameter,
    APIResponse,
    APIOperation,
    OpenAPISpecification
)

from .models.test_asset import (
    TestPriority,
    TestType,
    TestPoint,
    TestCase,
    TestScript
)

from .models.intelligent_strategy import (
    AIGenerationMode,
    TestIntelligenceLevel,
    AIGenerationConfig,
    IntelligentTestStrategy
)

__all__ = [
    "HTTPMethod",
    "APIParameter",
    "APIResponse",
    "APIOperation",
    "OpenAPISpecification",
    "TestPriority",
    "TestType",
    "TestPoint",
    "TestCase",
    "TestScript",
    "AIGenerationMode",
    "TestIntelligenceLevel",
    "AIGenerationConfig",
    "IntelligentTestStrategy",
]