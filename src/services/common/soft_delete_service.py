from typing import Type, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from src.models.base import BaseModel


class SoftDeleteService:
    """统一的软删除服务"""
    
    @staticmethod
    async def soft_delete(
        db: AsyncSession,
        model: Type[BaseModel],
        ids: List[int]
    ) -> bool:
        """
        软删除指定ID的记录
        
        Args:
            db: 数据库会话
            model: 模型类
            ids: 要删除的记录ID列表
            
        Returns:
            bool: 删除是否成功
        """
        if not ids:
            return False
            
        result = await db.execute(
            update(model)
            .where(model.id.in_(ids))
            .values(is_active=False)
        )
        await db.commit()
        return result.rowcount > 0
    
    @staticmethod
    async def restore(
        db: AsyncSession,
        model: Type[BaseModel],
        ids: List[int]
    ) -> bool:
        """
        恢复已删除的记录
        
        Args:
            db: 数据库会话
            model: 模型类
            ids: 要恢复的记录ID列表
            
        Returns:
            bool: 恢复是否成功
        """
        if not ids:
            return False
            
        result = await db.execute(
            update(model)
            .where(model.id.in_(ids))
            .values(is_active=True)
        )
        await db.commit()
        return result.rowcount > 0
    
    @staticmethod
    def get_active_query(model: Type[BaseModel]):
        """
        获取只包含激活记录的查询
        
        Args:
            model: 模型类
            
        Returns:
            查询对象: 包含is_active=True条件的查询
        """
        return select(model).where(model.is_active == True)
    
    @staticmethod
    async def get_by_id(
        db: AsyncSession,
        model: Type[BaseModel],
        id: int
    ) -> Optional[BaseModel]:
        """
        根据ID获取激活状态的记录
        
        Args:
            db: 数据库会话
            model: 模型类
            id: 记录ID
            
        Returns:
            Optional[BaseModel]: 激活状态的记录，不存在则返回None
        """
        return await db.scalar(
            select(model)
            .where(model.id == id, model.is_active == True)
        )
    
    @staticmethod
    async def get_all_active(
        db: AsyncSession,
        model: Type[BaseModel]
    ) -> List[BaseModel]:
        """
        获取所有激活状态的记录
        
        Args:
            db: 数据库会话
            model: 模型类
            
        Returns:
            List[BaseModel]: 激活状态的记录列表
        """
        result = await db.scalars(
            select(model).where(model.is_active == True)
        )
        return result.all()
