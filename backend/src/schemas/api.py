from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict, Any
from datetime import datetime


class ApiProjectBase(BaseModel):
    """API项目基础模型 - 适合个人探索项目"""
    name: str = Field(..., min_length=1, max_length=100, description="项目名称")
    description: Optional[str] = Field(None, description="项目描述")
    base_url: Optional[str] = Field(None, description="API基础URL")
    project_type: Optional[str] = Field("REST", description="项目类型")
    tags: Optional[List[str]] = Field(None, description="项目标签")
    status: Optional[str] = Field("active", description="项目状态")
    
    # 以下字段对于个人探索项目来说可能不是必需的，保持可选
    openapi_spec: Optional[str] = Field(None, description="OpenAPI/Swagger规范")
    spec_version: Optional[str] = Field(None, description="规范版本")


class ApiProjectCreate(ApiProjectBase):
    """创建API项目请求模型"""
    # 对于个人探索项目，简化创建过程，仅保留核心字段
    name: str = Field(..., min_length=1, max_length=100, description="项目名称")
    description: Optional[str] = Field(None, description="项目描述")
    base_url: Optional[str] = Field(None, description="API基础URL")
    tags: Optional[List[str]] = Field(None, description="项目标签")
    
    # 可选字段
    openapi_spec: Optional[str] = Field(None, description="OpenAPI/Swagger规范")
    spec_version: Optional[str] = Field(None, description="规范版本")


class ApiProjectUpdate(BaseModel):
    """更新API项目请求模型"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="项目名称")
    description: Optional[str] = Field(None, description="项目描述")
    base_url: Optional[str] = Field(None, description="API基础URL")
    tags: Optional[List[str]] = Field(None, description="项目标签")
    status: Optional[str] = Field(None, description="项目状态")
    openapi_spec: Optional[str] = Field(None, description="OpenAPI/Swagger规范")
    spec_version: Optional[str] = Field(None, description="规范版本")


class ApiProjectResponse(ApiProjectBase):
    """API项目响应模型"""
    id: int = Field(..., description="项目ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    # 以下字段对于个人探索项目来说不是必需的，移除
    # created_by: str = Field(..., description="创建人")
    # updated_by: str = Field(..., description="更新人")

    model_config = {
        "from_attributes": True
    }


# -------------------- API分组相关Schema --------------------

class ApiGroupBase(BaseModel):
    """API分组基础模型"""
    name: str = Field(..., min_length=1, max_length=100, description="分组名称")
    parent_id: Optional[int] = Field(None, description="父分组ID")
    description: Optional[str] = Field(None, description="分组描述")


class ApiGroupCreate(ApiGroupBase):
    """创建API分组请求模型"""
    name: str = Field(..., min_length=1, max_length=100, description="分组名称")
    parent_id: Optional[int] = Field(None, description="父分组ID")
    description: Optional[str] = Field(None, description="分组描述")


class ApiGroupUpdate(ApiGroupBase):
    """更新API分组请求模型"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="分组名称")
    parent_id: Optional[int] = Field(None, description="父分组ID")
    description: Optional[str] = Field(None, description="分组描述")


class ApiGroupResponse(ApiGroupBase):
    """API分组响应模型"""
    id: int = Field(..., description="分组ID")
    project_id: int = Field(..., description="项目ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    children: Optional[List['ApiGroupResponse']] = Field(None, description="子分组")

    model_config = {
        "from_attributes": True
    }


# -------------------- API接口相关Schema --------------------

class ApiInterfaceBase(BaseModel):
    """API接口基础模型"""
    name: str = Field(..., min_length=1, max_length=100, description="接口名称")
    path: str = Field(..., description="接口路径")
    method: str = Field(..., description="HTTP方法")
    summary: Optional[str] = Field(None, description="接口摘要")
    description: Optional[str] = Field(None, description="接口描述")
    operation_id: Optional[str] = Field(None, description="操作ID")
    tags: Optional[List[str]] = Field(None, description="标签")
    request_schema: Optional[Dict[str, Any]] = Field(None, description="请求模式")
    response_schema: Optional[Dict[str, Any]] = Field(None, description="响应模式")
    group_id: Optional[int] = Field(None, description="API分组ID")
    status: Optional[str] = Field("active", description="接口状态")
    protocol: Optional[str] = Field("HTTP", description="协议")
    
    # 添加缺失的字段：认证信息（对于个人探索项目可能需要）
    auth_type: Optional[str] = Field(None, description="认证类型")
    auth_token: Optional[str] = Field(None, description="认证令牌")


class ApiInterfaceCreate(ApiInterfaceBase):
    """创建API接口请求模型"""
    name: str = Field(..., min_length=1, max_length=100, description="接口名称")
    group_id: Optional[int] = Field(None, description="API分组ID")
    
    # 简化创建过程，移除不必要的字段
    operation_id: Optional[str] = Field(None, description="操作ID")
    request_schema: Optional[Dict[str, Any]] = Field(None, description="请求模式")
    response_schema: Optional[Dict[str, Any]] = Field(None, description="响应模式")


class ApiInterfaceUpdate(BaseModel):
    """更新API接口请求模型"""
    path: Optional[str] = Field(None, description="接口路径")
    method: Optional[str] = Field(None, description="HTTP方法")
    summary: Optional[str] = Field(None, description="接口摘要")
    description: Optional[str] = Field(None, description="接口描述")
    operation_id: Optional[str] = Field(None, description="操作ID")
    tags: Optional[List[str]] = Field(None, description="标签")
    request_schema: Optional[Dict[str, Any]] = Field(None, description="请求模式")
    response_schema: Optional[Dict[str, Any]] = Field(None, description="响应模式")
    group_id: Optional[int] = Field(None, description="API分组ID")
    status: Optional[str] = Field(None, description="接口状态")
    auth_type: Optional[str] = Field(None, description="认证类型")
    auth_token: Optional[str] = Field(None, description="认证令牌")


class ApiInterfaceResponse(ApiInterfaceBase):
    """API接口响应模型"""
    id: int = Field(..., description="接口ID")
    project_id: int = Field(..., description="项目ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    # 以下字段对于个人探索项目来说不是必需的，移除
    # created_by: str = Field(..., description="创建人")
    # updated_by: str = Field(..., description="更新人")

    model_config = {
        "from_attributes": True
    }


class ApiParameterBase(BaseModel):
    """API参数基础模型"""
    name: str = Field(..., description="参数名称")
    in_: str = Field(..., description="参数位置")
    description: Optional[str] = Field(None, description="参数描述")
    required: bool = Field(False, description="是否必填")
    param_type: str = Field(..., description="参数类型")
    schema: Optional[Dict[str, Any]] = Field(None, description="参数模式")
    example: Optional[Any] = Field(None, description="参数示例")
    
    # 添加缺失的字段：参数验证信息
    min_length: Optional[int] = Field(None, description="最小长度")
    max_length: Optional[int] = Field(None, description="最大长度")
    pattern: Optional[str] = Field(None, description="正则表达式")


class ApiParameterResponse(ApiParameterBase):
    """API参数响应模型"""
    id: int = Field(..., description="参数ID")
    interface_id: int = Field(..., description="接口ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    # 以下字段对于个人探索项目来说不是必需的，移除
    # created_by: str = Field(..., description="创建人")
    # updated_by: str = Field(..., description="更新人")

    model_config = {
        "from_attributes": True
    }


class ApiImportRequestBase(BaseModel):
    """API导入基础请求模型"""
    project_name: str = Field(..., min_length=1, max_length=100, description="项目名称")
    description: Optional[str] = Field(None, description="项目描述")
    base_url: Optional[str] = Field(None, description="API基础URL")
    tags: Optional[List[str]] = Field(None, description="项目标签")
    
    # 以下字段对于个人探索项目来说不是必需的，移除
    # contact_info: Optional[Dict[str, Any]] = Field(None, description="联系信息")
    
    # 添加缺失的字段：导入选项
    overwrite: Optional[bool] = Field(False, description="是否覆盖现有项目")
    validate_spec: Optional[bool] = Field(True, description="是否验证规范")


class ApiImportFileRequest(ApiImportRequestBase):
    """通过文件导入API请求模型"""
    # 注意：文件导入时，文件本身通过FastAPI的File对象传递，不包含在这个模型中
    pass


class ApiImportUrlRequest(ApiImportRequestBase):
    """通过URL导入API规范"""
    url: HttpUrl = Field(..., description="OpenAPI/Swagger规范URL")


class ApiImportResponse(BaseModel):
    """API导入响应模型"""
    success: bool = Field(..., description="导入是否成功")
    message: str = Field(..., description="导入结果消息")
    project_id: Optional[int] = Field(None, description="项目ID")
    project_name: Optional[str] = Field(None, description="项目名称")
    interface_count: Optional[int] = Field(None, description="导入的接口数量")
    parameter_count: Optional[int] = Field(None, description="导入的参数数量")
    error_details: Optional[Dict[str, Any]] = Field(None, description="错误详情")
    spec_info: Optional[Dict[str, Any]] = Field(None, description="规范信息")
    execution_time: Optional[float] = Field(None, description="导入执行时间（秒）")
    
    # 简化响应，移除不必要的字段
    # 对于个人探索项目，以下字段可能不需要：
    # - error_details（可以简化为message）
    # - spec_info（可以根据需要保留）
    # - execution_time（对于个人项目可能不需要精确的执行时间）
