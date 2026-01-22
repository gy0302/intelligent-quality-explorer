from sqlalchemy import Column, Integer, String, Text, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
import enum
from src.models.base import BaseModel


class TestScriptType(enum.Enum):
    """测试脚本类型枚举"""
    PYTHON = "python"
    JAVA = "java"
    JS = "javascript"
    OTHER = "other"


class TestScriptStatus(enum.Enum):
    """测试脚本状态枚举"""
    DRAFT = "draft"
    AI_REVIEWED = "ai_reviewed"
    MANUAL_REVIEWED = "manual_reviewed"
    APPROVED = "approved"
    REJECTED = "rejected"


class TestScript(BaseModel):
    """测试脚本模型"""
    __tablename__ = "test_scripts"
    
    test_case_id = Column(Integer, ForeignKey("test_cases.id"), nullable=False, comment="测试用例ID")
    script_type = Column(Enum(TestScriptType), default=TestScriptType.PYTHON, nullable=False, comment="脚本类型")
    script_content = Column(Text, nullable=False, comment="脚本内容")
    status = Column(Enum(TestScriptStatus), default=TestScriptStatus.DRAFT, nullable=False, comment="脚本状态")
    review_comments = Column(JSON, nullable=True, comment="评审意见")
    
    # 关系
    test_case = relationship("TestCase", back_populates="test_scripts")
    test_data = relationship("TestData", back_populates="test_script", cascade="all, delete-orphan")


class TestData(BaseModel):
    """测试数据模型"""
    __tablename__ = "test_data"
    
    test_script_id = Column(Integer, ForeignKey("test_scripts.id"), nullable=False, comment="测试脚本ID")
    data_name = Column(String(100), nullable=False, comment="数据名称")
    data_type = Column(String(50), nullable=False, comment="数据类型")
    data_content = Column(JSON, nullable=False, comment="数据内容")
    description = Column(Text, nullable=True, comment="数据描述")
    
    # 关系
    test_script = relationship("TestScript", back_populates="test_data")
