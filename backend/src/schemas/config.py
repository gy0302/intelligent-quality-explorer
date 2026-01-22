from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Any, List
from datetime import datetime


# 配置分类相关模型
class ConfigCategoryBase(BaseModel):
    """配置分类基础模型"""
    name: str = Field(..., description="分类名称", max_length=100)
    description: Optional[str] = Field(None, description="分类描述", max_length=500)
    is_active: bool = Field(True, description="是否启用")


class ConfigCategoryCreate(ConfigCategoryBase):
    """创建配置分类请求模型"""
    pass


class ConfigCategoryUpdate(ConfigCategoryBase):
    """更新配置分类请求模型"""
    name: Optional[str] = Field(None, description="分类名称", max_length=100)


class ConfigCategoryResponse(ConfigCategoryBase):
    """配置分类响应模型"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: str
    updated_by: str


# 配置项相关模型
class ConfigItemBase(BaseModel):
    """配置项基础模型"""
    key: str = Field(..., description="配置键", max_length=100)
    value: Any = Field(..., description="配置值")
    description: Optional[str] = Field(None, description="配置描述", max_length=500)
    category_id: int = Field(..., description="所属分类ID")
    is_active: bool = Field(True, description="是否启用")
    is_secret: bool = Field(False, description="是否为敏感信息")
    data_type: str = Field("string", description="数据类型", pattern="^(string|number|boolean|array|object)$")
    default_value: Optional[Any] = Field(None, description="默认值")


class ConfigItemCreate(ConfigItemBase):
    """创建配置项请求模型"""
    pass


class ConfigItemUpdate(ConfigItemBase):
    """更新配置项请求模型"""
    key: Optional[str] = Field(None, description="配置键", max_length=100)
    value: Optional[Any] = Field(None, description="配置值")
    category_id: Optional[int] = Field(None, description="所属分类ID")


class ConfigItemResponse(ConfigItemBase):
    """配置项响应模型"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: str
    updated_by: str
    
    # 敏感信息处理
    def model_dump(self, **kwargs):
        data = super().model_dump(**kwargs)
        if data.get("is_secret"):
            data["value"] = "******"
        return data


class ConfigItemDetailResponse(ConfigItemResponse):
    """配置项详细响应模型（包含实际值，用于内部使用）"""
    def model_dump(self, **kwargs):
        return super().model_dump(**kwargs)


# 配置查询相关模型
class ConfigQuery(BaseModel):
    """配置查询模型"""
    category_id: Optional[int] = Field(None, description="分类ID")
    key: Optional[str] = Field(None, description="配置键")
    is_active: Optional[bool] = Field(None, description="是否启用")
    page: int = Field(1, description="页码", ge=1)
    page_size: int = Field(20, description="每页数量", ge=1, le=100)


class ConfigListResponse(BaseModel):
    """配置列表响应模型"""
    items: List[ConfigItemResponse]
    total: int
    page: int
    page_size: int
    

# 配置批量操作模型
class ConfigBatchUpdate(BaseModel):
    """批量更新配置请求模型"""
    configs: List[dict] = Field(..., description="配置列表")


class ConfigCategoryListResponse(BaseModel):
    """配置分类列表响应模型"""
    items: List[ConfigCategoryResponse]
    total: int
    page: int
    page_size: int
