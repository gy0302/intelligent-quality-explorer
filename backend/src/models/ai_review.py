from sqlalchemy import Column, Integer, String, Text, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
import enum
from src.models.base import BaseModel


class ReviewType(enum.Enum):
    """评审类型枚举"""
    API_REVIEW = "api_review"
    TEST_POINT_REVIEW = "test_point_review"
    TEST_CASE_REVIEW = "test_case_review"
    TEST_SCRIPT_REVIEW = "test_script_review"


class ReviewResult(enum.Enum):
    """评审结果枚举"""
    PASSED = "passed"
    PARTIALLY_PASSED = "partially_passed"
    FAILED = "failed"


class AIReview(BaseModel):
    """AI评审模型"""
    __tablename__ = "ai_reviews"
    
    review_type = Column(Enum(ReviewType), nullable=False, comment="评审类型")
    target_id = Column(Integer, nullable=False, comment="评审对象ID")
    reviewer_role = Column(String(50), nullable=False, comment="评审专家角色")
    reviewer_focus = Column(JSON, nullable=False, comment="评审关注领域")
    review_content = Column(Text, nullable=False, comment="评审内容")
    review_result = Column(Enum(ReviewResult), nullable=False, comment="评审结果")
    review_comments = Column(JSON, nullable=False, comment="评审意见")
    improvement_suggestions = Column(JSON, nullable=True, comment="改进建议")
