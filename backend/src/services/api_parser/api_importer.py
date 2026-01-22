"""API导入服务"""
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from src.models.api import ApiProject, ApiInterface, ApiParameter
from src.services.api_parser.openapi_parser import OpenAPIParser


class ApiImporter:
    """API导入服务"""
    
    def __init__(self):
        self.parser = OpenAPIParser()
    
    async def import_api(
        self, 
        db: AsyncSession, 
        project_name: str, 
        spec_content: str,
        description: Optional[str] = None,
        base_url: Optional[str] = None,
        tags: Optional[List[str]] = None,
        contact_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        导入API规范到数据库
        
        Args:
            db: 数据库会话
            project_name: 项目名称
            spec_content: OpenAPI/Swagger规范内容
            description: 项目描述
            base_url: API基础URL
            tags: 项目标签
            contact_info: 联系信息
            
        Returns:
            Dict: 导入结果信息
        """
        try:
            import time
            start_time = time.time()
            
            # 解析API规范
            if not self.parser.load_spec(spec_content):
                return {
                    "success": False,
                    "message": "Failed to parse API specification"
                }
            
            # 获取API基本信息
            api_info = self.parser.get_api_info()
            
            # 优先使用传入参数，否则使用规范中的信息
            final_description = description or api_info.get("description", "")
            final_base_url = base_url or api_info.get("base_url", "")
            final_contact = contact_info or api_info.get("contact_info", {})
            final_tags = tags or []
            
            # 创建API项目
            api_project = ApiProject(
                name=project_name,
                description=final_description,
                openapi_spec=spec_content,
                spec_version=api_info.get("spec_version"),
                status="active",
                base_url=final_base_url,
                project_type="REST",
                tags=final_tags,
                contact_info=final_contact,
                terms_of_service=api_info.get("terms_of_service"),
                license_info=api_info.get("license_info")
            )
            db.add(api_project)
            await db.flush()  # 获取项目ID
            
            # 导入API接口
            paths = self.parser.get_paths()
            interface_count = 0
            parameter_count = 0
            
            for api_path in paths:
                # 解析请求体
                request_body = self.parser.parse_request_body(api_path)
                
                # 创建API接口
                api_interface = ApiInterface(
                    project_id=api_project.id,
                    path=api_path["path"],
                    method=api_path["method"],
                    summary=api_path.get("summary", ""),
                    description=api_path.get("description", ""),
                    operation_id=api_path.get("operation_id"),
                    tags=api_path.get("tags", []),
                    request_schema=request_body,
                    response_schema=self.parser.parse_responses(api_path)
                )
                db.add(api_interface)
                await db.flush()  # 获取接口ID
                interface_count += 1
                
                # 解析并导入参数
                parameters = self.parser.parse_parameters(api_path)
                for param in parameters:
                    api_parameter = ApiParameter(
                        interface_id=api_interface.id,
                        name=param["name"],
                        in_=param["in"],
                        description=param.get("description", ""),
                        required=1 if param.get("required", False) else 0,
                        param_type=param.get("type", "string"),
                        schema=param.get("schema", {}),
                        example=param.get("example")
                    )
                    db.add(api_parameter)
                    parameter_count += 1
            
            # 提交事务
            await db.commit()
            
            execution_time = time.time() - start_time
            
            return {
                "success": True,
                "message": "API imported successfully",
                "project_id": api_project.id,
                "project_name": api_project.name,
                "interface_count": interface_count,
                "parameter_count": parameter_count,
                "spec_version": api_info.get("spec_version"),
                "spec_info": {
                    "title": api_info.get("title"),
                    "version": api_info.get("version"),
                    "base_url": api_project.base_url,
                    "contact_info": api_project.contact_info,
                    "license_info": api_project.license_info
                },
                "execution_time": round(execution_time, 2)
            }
        except Exception as e:
            import traceback
            await db.rollback()
            return {
                "success": False,
                "message": f"Failed to import API: {str(e)}",
                "error_details": {
                    "type": type(e).__name__,
                    "message": str(e),
                    "traceback": traceback.format_exc().splitlines()
                }
            }
    
    async def update_api_project(self, db: AsyncSession, project_id: int, spec_content: str) -> Dict[str, Any]:
        """
        更新API项目规范
        
        Args:
            db: 数据库会话
            project_id: 项目ID
            spec_content: 新的OpenAPI/Swagger规范内容
            
        Returns:
            Dict: 更新结果信息
        """
        try:
            # 查找项目
            project = await db.get(ApiProject, project_id)
            if not project:
                return {
                    "success": False,
                    "message": f"API project with ID {project_id} not found"
                }
            
            # 解析新的API规范
            if not self.parser.load_spec(spec_content):
                return {
                    "success": False,
                    "message": "Failed to parse new API specification"
                }
            
            # 删除现有的接口和参数
            interfaces = await db.execute(
                select(ApiInterface).where(ApiInterface.project_id == project_id)
            )
            for interface in interfaces.scalars():
                # 删除接口的参数
                await db.execute(
                    delete(ApiParameter).where(ApiParameter.interface_id == interface.id)
                )
                # 删除接口
                await db.delete(interface)
            
            # 更新项目规范
            project.openapi_spec = spec_content
            project.spec_version = self.parser.get_api_info().get("spec_version")
            
            # 导入新的API接口
            paths = self.parser.get_paths()
            interface_count = 0
            parameter_count = 0
            
            for api_path in paths:
                # 解析请求体
                request_body = self.parser.parse_request_body(api_path)
                
                # 创建API接口
                api_interface = ApiInterface(
                    project_id=project.id,
                    path=api_path["path"],
                    method=api_path["method"],
                    summary=api_path.get("summary", ""),
                    description=api_path.get("description", ""),
                    operation_id=api_path.get("operation_id"),
                    tags=api_path.get("tags", []),
                    request_schema=request_body,
                    response_schema=self.parser.parse_responses(api_path)
                )
                db.add(api_interface)
                await db.flush()  # 获取接口ID
                interface_count += 1
                
                # 解析并导入参数
                parameters = self.parser.parse_parameters(api_path)
                for param in parameters:
                    api_parameter = ApiParameter(
                        interface_id=api_interface.id,
                        name=param["name"],
                        in_=param["in"],
                        description=param.get("description", ""),
                        required=1 if param.get("required", False) else 0,
                        param_type=param.get("type", "string"),
                        schema=param.get("schema", {}),
                        example=param.get("example")
                    )
                    db.add(api_parameter)
                    parameter_count += 1
            
            # 提交事务
            await db.commit()
            
            return {
                "success": True,
                "message": "API project updated successfully",
                "project_id": project.id,
                "project_name": project.name,
                "interface_count": interface_count,
                "parameter_count": parameter_count
            }
        except Exception as e:
            await db.rollback()
            return {
                "success": False,
                "message": f"Failed to update API project: {str(e)}"
            }
