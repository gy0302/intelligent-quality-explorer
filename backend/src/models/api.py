from sqlalchemy import Column, Integer, String, Text, ForeignKey, JSON, event
from sqlalchemy.orm import relationship
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from src.models.base import BaseModel


class ApiProject(BaseModel):
    """API项目模型"""
    __tablename__ = "api_projects"
    
    name = Column(String(100), nullable=False, comment="项目名称")
    description = Column(Text, nullable=True, comment="项目描述")
    openapi_spec = Column(Text, nullable=True, comment="OpenAPI/Swagger规范")
    spec_version = Column(String(20), nullable=True, comment="OpenAPI版本")
    status = Column(String(20), default="active", nullable=False, comment="项目状态")
    base_url = Column(String(200), nullable=True, comment="API基础URL")
    project_type = Column(String(20), default="REST", nullable=False, comment="项目类型")
    tags = Column(JSON, nullable=True, comment="项目标签")
    
    # 关系
    interfaces = relationship("ApiInterface", back_populates="project", cascade="all, delete-orphan")
    test_points = relationship("TestPoint", back_populates="api_project", cascade="all, delete-orphan")
    groups = relationship("ApiGroup", back_populates="project", cascade="all, delete-orphan")


class ApiInterface(BaseModel):
    """API接口模型"""
    __tablename__ = "api_interfaces"
    
    project_id = Column(Integer, ForeignKey("api_projects.id"), nullable=False, comment="项目ID")
    group_id = Column(Integer, ForeignKey("api_groups.id"), nullable=True, comment="API分组ID")
    path = Column(String(200), nullable=False, comment="接口路径")
    method = Column(String(10), nullable=False, comment="HTTP方法")
    name = Column(String(100), nullable=False, comment="接口名称")
    summary = Column(String(200), nullable=True, comment="接口摘要")
    description = Column(Text, nullable=True, comment="接口描述")
    operation_id = Column(String(100), nullable=True, comment="操作ID")
    tags = Column(JSON, nullable=True, comment="标签")
    response_schema = Column(JSON, nullable=True, comment="响应模式")
    request_schema = Column(JSON, nullable=True, comment="请求模式")
    status = Column(String(20), default="active", nullable=False, comment="接口状态")
    protocol = Column(String(20), default="HTTP", nullable=False, comment="协议")
    
    auth_type = Column(String(50), nullable=True, comment="认证类型")
    auth_token = Column(String(200), nullable=True, comment="认证令牌")
    
    # 关系
    project = relationship("ApiProject", back_populates="interfaces")
    group = relationship("ApiGroup")
    parameters = relationship("ApiParameter", back_populates="interface", cascade="all, delete-orphan")
    test_points = relationship("TestPoint", back_populates="api_interface", cascade="all, delete-orphan")


class ApiParameter(BaseModel):
    """API参数模型"""
    __tablename__ = "api_parameters"
    
    interface_id = Column(Integer, ForeignKey("api_interfaces.id"), nullable=False, comment="接口ID")
    name = Column(String(100), nullable=False, comment="参数名称")
    in_ = Column(String(20), nullable=False, comment="参数位置(in)")
    description = Column(Text, nullable=True, comment="参数描述")
    required = Column(Integer, default=0, nullable=False, comment="是否必填")
    param_type = Column(String(50), nullable=False, comment="参数类型")
    schema = Column(JSON, nullable=True, comment="参数模式")
    example = Column(JSON, nullable=True, comment="参数示例")
    
    # 参数验证信息
    min_length = Column(Integer, nullable=True, comment="最小长度")
    max_length = Column(Integer, nullable=True, comment="最大长度")
    pattern = Column(String(200), nullable=True, comment="正则表达式")
    
    # 关系
    interface = relationship("ApiInterface", back_populates="parameters")


class ApiGroup(BaseModel):
    """API分组模型"""
    __tablename__ = "api_groups"
    
    name = Column(String(100), nullable=False, comment="分组名称")
    project_id = Column(Integer, ForeignKey("api_projects.id"), nullable=False, comment="项目ID")
    parent_id = Column(Integer, ForeignKey("api_groups.id"), nullable=True, comment="父分组ID")
    description = Column(Text, nullable=True, comment="分组描述")
    
    # 关系
    project = relationship("ApiProject", back_populates="groups")
    
    # 移除自引用关系，简化模型
    # 分组的层级关系将通过前端处理，后端只存储parent_id
    # 这样可以避免复杂的SQLAlchemy自引用关系配置问题