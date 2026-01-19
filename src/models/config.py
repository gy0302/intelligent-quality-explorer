from enum import unique
from sqlalchemy import Column, String, Text, Boolean, Integer, JSON, ForeignKey
from sqlalchemy.sql import expression
from .base import BaseModel


class ConfigCategory(BaseModel):
    """配置分类"""
    __tablename__ = "config_categories"
    
    name = Column(String(100), nullable=False,unique=True, comment="分类名称")
    description = Column(String(500), nullable=True, comment="分类描述")
    is_active = Column(Boolean, default=True, server_default=expression.true(), comment="是否启用")


class ConfigItem(BaseModel):
    """配置项"""
    __tablename__ = "config_items"
    
    key = Column(String(100), nullable=False, index=True, comment="配置键")
    value = Column(JSON, nullable=False, comment="配置值")
    description = Column(String(500), nullable=True, comment="配置描述")
    category_id = Column(Integer, ForeignKey("config_categories.id", ondelete="CASCADE"), nullable=False, comment="所属分类ID")
    is_active = Column(Boolean, default=True, server_default=expression.true(), comment="是否启用")
    is_secret = Column(Boolean, default=False, server_default=expression.false(), comment="是否为敏感信息")
    data_type = Column(String(20), nullable=False, default="string", comment="数据类型")
    default_value = Column(JSON, nullable=True, comment="默认值")
    
    # 外键关系在__init__.py中定义，避免循环导入
