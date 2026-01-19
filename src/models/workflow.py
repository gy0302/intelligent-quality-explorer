from sqlalchemy import Column, Integer, String, Text, ForeignKey, JSON, Enum, DateTime
from sqlalchemy.orm import relationship
import enum
from src.models.base import BaseModel


class WorkflowStep(enum.Enum):
    """工作流步骤枚举"""
    API_IMPORT = "import"
    API_AI_REVIEW = "api_review"
    TEST_POINT_GENERATION = "test_points"
    TEST_POINT_AI_REVIEW = "points_review"
    TEST_POINT_MANUAL_REVIEW = "points_manual_review"
    TEST_CASE_GENERATION = "test_cases"
    TEST_CASE_AI_REVIEW = "cases_review"
    TEST_CASE_MANUAL_REVIEW = "cases_manual_review"
    TEST_SCRIPT_GENERATION = "scripts"
    TEST_SCRIPT_AI_REVIEW = "scripts_review"
    TEST_SCRIPT_MANUAL_REVIEW = "scripts_manual_review"
    TEST_EXECUTION = "execution"
    TEST_REPORT = "report"


class WorkflowStatus(enum.Enum):
    """工作流状态枚举"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    REJECTED = "rejected"


class Workflow(BaseModel):
    """工作流模型"""
    __tablename__ = "workflows"
    
    api_project_id = Column(Integer, ForeignKey("api_projects.id"), nullable=False, comment="API项目ID")
    name = Column(String(100), nullable=False, comment="工作流名称")
    current_step = Column(Enum(WorkflowStep), default=WorkflowStep.API_IMPORT, nullable=False, comment="当前步骤")
    status = Column(Enum(WorkflowStatus), default=WorkflowStatus.PENDING, nullable=False, comment="工作流状态")
    progress = Column(Integer, default=0, nullable=False, comment="工作流进度(%)")
    execution_log = Column(JSON, nullable=True, comment="执行日志")
    
    # 关系
    project = relationship("ApiProject")
    step_records = relationship("WorkflowStepRecord", back_populates="workflow", cascade="all, delete-orphan")


class WorkflowStepRecord(BaseModel):
    """工作流步骤记录模型"""
    __tablename__ = "workflow_step_records"
    
    workflow_id = Column(Integer, ForeignKey("workflows.id"), nullable=False, comment="工作流ID")
    step = Column(Enum(WorkflowStep), nullable=False, comment="步骤")
    status = Column(Enum(WorkflowStatus), nullable=False, comment="步骤状态")
    start_time = Column(DateTime, nullable=True, comment="开始时间")
    end_time = Column(DateTime, nullable=True, comment="结束时间")
    duration = Column(Integer, nullable=True, comment="持续时间(秒)")
    result = Column(JSON, nullable=True, comment="步骤结果")
    comments = Column(Text, nullable=True, comment="步骤备注")
    
    # 关系
    workflow = relationship("Workflow", back_populates="step_records")
