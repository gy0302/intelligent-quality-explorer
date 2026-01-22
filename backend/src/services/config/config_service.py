from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from src.models.config import ConfigCategory, ConfigItem
from src.schemas.config import (
    ConfigCategoryCreate, ConfigCategoryUpdate,
    ConfigItemCreate, ConfigItemUpdate
)


class ConfigCategoryService:
    """配置分类服务"""
    
    @staticmethod
    async def create_category(
        db: AsyncSession, 
        category_data: ConfigCategoryCreate,
        user_id: str = "system"
    ) -> ConfigCategory:
        """创建配置分类"""
        category = ConfigCategory(
            name=category_data.name,
            description=category_data.description,
            is_active=category_data.is_active,
            created_by=user_id,
            updated_by=user_id
        )
        db.add(category)
        await db.commit()
        await db.refresh(category)
        return category
    
    @staticmethod
    async def get_categories(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        is_active: Optional[bool] = None
    ) -> Dict[str, Any]:
        """获取配置分类列表"""
        query = select(ConfigCategory).where(ConfigCategory.is_active == True)
        
        if is_active is not None:
            query = query.where(ConfigCategory.is_active == is_active)
        
        # 计算总数
        total_query = select(func.count(ConfigCategory.id)).where(ConfigCategory.is_active == True)
        if is_active is not None:
            total_query = total_query.where(ConfigCategory.is_active == is_active)
        total = await db.scalar(total_query)
        
        # 分页查询
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        categories = await db.scalars(query)
        
        return {
            "items": categories.all(),
            "total": total,
            "page": page,
            "page_size": page_size
        }
    
    @staticmethod
    async def get_category_by_id(db: AsyncSession, category_id: int) -> Optional[ConfigCategory]:
        """根据ID获取配置分类"""
        query = select(ConfigCategory).where(ConfigCategory.id == category_id, ConfigCategory.is_active == True)
        return await db.scalar(query)
    
    @staticmethod
    async def update_category(
        db: AsyncSession,
        category_id: int,
        category_data: ConfigCategoryUpdate,
        user_id: str = "system"
    ) -> Optional[ConfigCategory]:
        """更新配置分类"""
        category = await ConfigCategoryService.get_category_by_id(db, category_id)
        if not category:
            return None
        
        update_data = category_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(category, field, value)
        
        category.updated_by = user_id
        await db.commit()
        await db.refresh(category)
        return category
    
    @staticmethod
    async def delete_category(db: AsyncSession, category_id: int) -> bool:
        """删除配置分类"""
        # 检查是否有配置项关联
        config_count_query = select(func.count(ConfigItem.id)).where(ConfigItem.category_id == category_id, ConfigItem.is_active == True)
        config_count = await db.scalar(config_count_query)
        
        if config_count > 0:
            raise ValueError("配置分类: 该分类下存在配置项，无法删除")
        
        result = await db.execute(update(ConfigCategory).where(ConfigCategory.id == category_id).values(is_active=False))
        await db.commit()
        return result.rowcount > 0


class ConfigItemService:
    """配置项服务"""
    
    # 内存缓存，存储活跃配置项
    _active_configs_cache: Dict[str, Any] = {}
    
    @classmethod
    async def init_config_cache(cls, db: AsyncSession) -> None:
        """
        初始化配置缓存，平台启动时调用
        
        Args:
            db: 数据库会话
        """
        cls._active_configs_cache = await cls.get_active_configs_from_db(db)
    
    @staticmethod
    async def get_active_configs_from_db(db: AsyncSession) -> Dict[str, Any]:
        """
        从数据库获取所有活跃的配置项
        
        Args:
            db: 数据库会话
            
        Returns:
            Dict[str, Any]: 配置项字典
        """
        query = select(ConfigItem).where(ConfigItem.is_active == True)
        config_items = await db.scalars(query)
        
        config_dict = {}
        for item in config_items.all():
            config_dict[item.key] = item.value
        
        return config_dict
    
    @classmethod
    async def get_active_configs(cls, db: AsyncSession) -> Dict[str, Any]:
        """
        获取所有活跃的配置项，优先从内存缓存读取
        
        Args:
            db: 数据库会话（仅当缓存为空时使用）
            
        Returns:
            Dict[str, Any]: 配置项字典
        """
        # 如果缓存为空，从数据库加载
        if not cls._active_configs_cache:
            await cls.init_config_cache(db)
        
        return cls._active_configs_cache.copy()
    
    @classmethod
    def refresh_config_cache(cls, new_configs: Dict[str, Any]) -> None:
        """
        刷新配置缓存
        
        Args:
            new_configs: 新的配置项字典
        """
        cls._active_configs_cache = new_configs.copy()
    
    @classmethod
    def clear_config_cache(cls) -> None:
        """
        清空配置缓存
        """
        cls._active_configs_cache.clear()
    
    @staticmethod
    async def create_config_item(
        db: AsyncSession,
        config_data: ConfigItemCreate,
        user_id: str = "system"
    ) -> ConfigItem:
        """创建配置项"""
        # 检查配置键是否已存在
        existing_config = await db.scalar(
            select(ConfigItem).where(ConfigItem.key == config_data.key, ConfigItem.is_active == True)
        )
        if existing_config:
            raise ValueError(f"配置项: 配置键 '{config_data.key}' 已存在")
        
        config_item = ConfigItem(
            key=config_data.key,
            value=config_data.value,
            description=config_data.description,
            category_id=config_data.category_id,
            is_active=config_data.is_active,
            is_secret=config_data.is_secret,
            data_type=config_data.data_type,
            default_value=config_data.default_value,
            created_by=user_id,
            updated_by=user_id
        )
        
        db.add(config_item)
        await db.commit()
        await db.refresh(config_item)
        
        # 刷新缓存
        new_configs = await self.get_active_configs_from_db(db)
        self.refresh_config_cache(new_configs)
        
        return config_item
    
    @staticmethod
    async def get_config_items(
        db: AsyncSession,
        category_id: Optional[int] = None,
        key: Optional[str] = None,
        is_active: Optional[bool] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """获取配置项列表"""
        query = select(ConfigItem).where(ConfigItem.is_active == True)
        
        if category_id is not None:
            query = query.where(ConfigItem.category_id == category_id)
        
        if key is not None:
            query = query.where(ConfigItem.key.ilike(f"%{key}%"))
        
        if is_active is not None:
            query = query.where(ConfigItem.is_active == is_active)
        
        # 计算总数
        total_query = select(func.count(ConfigItem.id)).where(ConfigItem.is_active == True)
        if category_id is not None:
            total_query = total_query.where(ConfigItem.category_id == category_id)
        if key is not None:
            total_query = total_query.where(ConfigItem.key.ilike(f"%{key}%"))
        if is_active is not None:
            total_query = total_query.where(ConfigItem.is_active == is_active)
        
        total = await db.scalar(total_query)
        
        # 分页查询
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        config_items = await db.scalars(query)
        
        return {
            "items": config_items.all(),
            "total": total,
            "page": page,
            "page_size": page_size
        }
    
    @staticmethod
    async def get_config_item_by_id(db: AsyncSession, config_id: int) -> Optional[ConfigItem]:
        """根据ID获取配置项"""
        query = select(ConfigItem).where(ConfigItem.id == config_id, ConfigItem.is_active == True)
        return await db.scalar(query)
    
    @staticmethod
    async def get_config_item_by_key(db: AsyncSession, key: str) -> Optional[ConfigItem]:
        """根据键获取配置项"""
        query = select(ConfigItem).where(ConfigItem.key == key, ConfigItem.is_active == True)
        return await db.scalar(query)
    
    @staticmethod
    async def update_config_item(
        db: AsyncSession,
        config_id: int,
        config_data: ConfigItemUpdate,
        user_id: str = "system"
    ) -> Optional[ConfigItem]:
        """更新配置项"""
        config_item = await ConfigItemService.get_config_item_by_id(db, config_id)
        if not config_item:
            return None
        
        # 检查配置键是否与其他配置项冲突
        if config_data.key and config_data.key != config_item.key:
            existing_config = await db.scalar(
                select(ConfigItem).where(ConfigItem.key == config_data.key, ConfigItem.id != config_id, ConfigItem.is_active == True)
            )
            if existing_config:
                raise ValueError(f"配置项: 配置键 '{config_data.key}' 已存在")
        
        update_data = config_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(config_item, field, value)
        
        config_item.updated_by = user_id
        await db.commit()
        await db.refresh(config_item)
        
        # 刷新缓存
        new_configs = await self.get_active_configs_from_db(db)
        self.refresh_config_cache(new_configs)
        
        return config_item
    
    @staticmethod
    async def delete_config_item(db: AsyncSession, config_id: int) -> bool:
        """删除配置项"""
        result = await db.execute(update(ConfigItem).where(ConfigItem.id == config_id).values(is_active=False))
        await db.commit()
        
        # 刷新缓存
        new_configs = await self.get_active_configs_from_db(db)
        self.refresh_config_cache(new_configs)
        
        return result.rowcount > 0
    
    @staticmethod
    async def get_active_configs(db: AsyncSession) -> Dict[str, Any]:
        """获取所有活跃的配置项，以字典形式返回"""
        query = select(ConfigItem).where(ConfigItem.is_active == True)
        config_items = await db.scalars(query)
        
        config_dict = {}
        for item in config_items.all():
            config_dict[item.key] = item.value
        
        return config_dict
    
    @staticmethod
    async def batch_update_configs(
        db: AsyncSession,
        configs: List[Dict[str, Any]],
        user_id: str = "system"
    ) -> List[ConfigItem]:
        """批量更新配置项"""
        updated_configs = []
        
        try:
            # 开始事务
            for config_data in configs:
                config_id = config_data.get("id")
                if not config_id:
                    continue
                
                config_item = await ConfigItemService.get_config_item_by_id(db, config_id)
                if config_item:
                    for field, value in config_data.items():
                        if field != "id" and hasattr(config_item, field):
                            setattr(config_item, field, value)
                    
                    config_item.updated_by = user_id
                    updated_configs.append(config_item)
            
            # 提交事务
            await db.commit()
            
            # 刷新所有更新的配置项
            for config_item in updated_configs:
                await db.refresh(config_item)
            
            # 刷新缓存
            new_configs = await ConfigItemService.get_active_configs_from_db(db)
            ConfigItemService.refresh_config_cache(new_configs)
            
            return updated_configs
        except Exception as e:
            # 回滚事务
            await db.rollback()
            # 重新抛出异常，让调用者处理
            raise e