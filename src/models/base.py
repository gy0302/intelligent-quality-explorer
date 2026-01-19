from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, String, Boolean
from sqlalchemy.sql import expression
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class BaseModel(Base):
    """所有模型的基类"""
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(String(50), default="system", nullable=False)
    updated_by = Column(String(50), default="system", nullable=False)
    is_active = Column(Boolean, default=True, server_default=expression.true(), nullable=False, comment="是否激活，False为删除，True为激活")
    