"""数据库模型"""

# 基础模型
from src.models.base import Base, BaseModel

# API相关模型
from src.models.api import ApiProject, ApiInterface, ApiParameter

# 测试点相关模型
from src.models.test_point import TestPoint, TestPointStatus, TestPointType, TestPointPriority

# 测试用例相关模型
from src.models.test_case import TestCase, TestCaseStatus, TestCasePriority

# 测试脚本相关模型
from src.models.test_script import TestScript, TestScriptType, TestScriptStatus, TestData

# AI评审相关模型
from src.models.ai_review import AIReview, ReviewType, ReviewResult

# 工作流相关模型
from src.models.workflow import Workflow, WorkflowStep, WorkflowStatus, WorkflowStepRecord

# 配置相关模型
from src.models.config import ConfigCategory, ConfigItem

__all__ = [
    # 基础模型
    "Base",
    "BaseModel",
    
    # API相关模型
    "ApiProject",
    "ApiInterface",
    "ApiParameter",
    
    # 测试点相关模型
    "TestPoint",
    "TestPointStatus",
    "TestPointType",
    "TestPointPriority",
    
    # 测试用例相关模型
    "TestCase",
    "TestCaseStatus",
    "TestCasePriority",
    
    # 测试脚本相关模型
    "TestScript",
    "TestScriptType",
    "TestScriptStatus",
    "TestData",
    
    # AI评审相关模型
    "AIReview",
    "ReviewType",
    "ReviewResult",
    
    # 工作流相关模型
    "Workflow",
    "WorkflowStep",
    "WorkflowStatus",
    "WorkflowStepRecord",
    
    # 配置相关模型
    "ConfigCategory",
    "ConfigItem",
]
