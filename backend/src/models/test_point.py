from sqlalchemy import Column, Integer, String, Text, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
import enum
from src.models.base import BaseModel


class TestPointStatus(enum.Enum):
    """测试点状态枚举"""
    DRAFT = "draft"
    AI_REVIEWED = "ai_reviewed"
    MANUAL_REVIEWED = "manual_reviewed"
    APPROVED = "approved"
    REJECTED = "rejected"


class TestPointType(enum.Enum):
    """测试点类型枚举"""
    FUNCTIONAL = "functional"
    PERFORMANCE = "performance"
    SECURITY = "security"
    COMPATIBILITY = "compatibility"
    RELIABILITY = "reliability"
    USABILITY = "usability"


class TestPointPriority(enum.Enum):
    """测试点优先级枚举"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TestPoint(BaseModel):
    """测试点模型"""
    __tablename__ = "test_points"
    
    api_project_id = Column(Integer, ForeignKey("api_projects.id"), nullable=False, comment="API项目ID")
    api_interface_id = Column(Integer, ForeignKey("api_interfaces.id"), nullable=True, comment="API接口ID")
    module = Column(String(100), nullable=False, comment="模块名称")
    name = Column(String(200), nullable=False, comment="测试点名称")
    description = Column(Text, nullable=True, comment="测试点描述")
    test_type = Column(Enum(TestPointType), nullable=False, comment="测试类型")
    priority = Column(Enum(TestPointPriority), nullable=False, comment="测试优先级")
    check_points = Column(JSON, nullable=False, comment="测试检查点")
    input_data = Column(JSON, nullable=True, comment="输入数据")
    expected_result = Column(JSON, nullable=True, comment="预期结果")
    status = Column(Enum(TestPointStatus), default=TestPointStatus.DRAFT, nullable=False, comment="测试点状态")
    review_comments = Column(JSON, nullable=True, comment="评审意见")
    special_notes = Column(Text, nullable=True, comment="特殊说明")
    
    # 关系
    api_project = relationship("ApiProject", back_populates="test_points")
    api_interface = relationship("ApiInterface", back_populates="test_points")
    test_cases = relationship("TestCase", back_populates="test_point", cascade="all, delete-orphan")
