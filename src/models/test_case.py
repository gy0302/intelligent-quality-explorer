from sqlalchemy import Column, Integer, String, Text, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
import enum
from src.models.base import BaseModel


class TestCaseStatus(enum.Enum):
    """测试用例状态枚举"""
    DRAFT = "draft"
    AI_REVIEWED = "ai_reviewed"
    MANUAL_REVIEWED = "manual_reviewed"
    APPROVED = "approved"
    REJECTED = "rejected"


class TestCasePriority(enum.Enum):
    """测试用例优先级枚举"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TestCase(BaseModel):
    """测试用例模型"""
    __tablename__ = "test_cases"
    
    test_point_id = Column(Integer, ForeignKey("test_points.id"), nullable=False, comment="测试点ID")
    case_name = Column(String(200), nullable=False, comment="测试用例名称")
    description = Column(Text, nullable=True, comment="测试用例描述")
    steps = Column(JSON, nullable=False, comment="测试步骤")
    input_data = Column(JSON, nullable=False, comment="输入数据")
    expected_result = Column(JSON, nullable=False, comment="预期结果")
    actual_result = Column(JSON, nullable=True, comment="实际结果")
    priority = Column(Enum(TestCasePriority), nullable=False, comment="测试优先级")
    status = Column(Enum(TestCaseStatus), default=TestCaseStatus.DRAFT, nullable=False, comment="测试用例状态")
    review_comments = Column(JSON, nullable=True, comment="评审意见")
    execution_status = Column(String(20), nullable=True, comment="执行状态")
    
    # 关系
    test_point = relationship("TestPoint", back_populates="test_cases")
    test_scripts = relationship("TestScript", back_populates="test_case", cascade="all, delete-orphan")
