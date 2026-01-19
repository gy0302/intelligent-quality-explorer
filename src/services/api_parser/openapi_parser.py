"""OpenAPI/Swagger规范解析器"""
import json
import yaml
from typing import Dict, Any, List
from prance import ResolvingParser
from openapi_spec_validator import validate_spec
from openapi_spec_validator.readers import read_from_filename


class OpenAPIParser:
    """OpenAPI/Swagger规范解析器"""
    
    def __init__(self):
        self.parser = None
        self.spec = None
        self.spec_version = None
    
    def load_spec(self, spec_content: str) -> bool:
        """
        加载并验证OpenAPI/Swagger规范
        
        Args:
            spec_content: OpenAPI/Swagger规范内容
            
        Returns:
            bool: 加载成功返回True，否则返回False
        """
        try:
            # 尝试解析JSON格式
            try:
                self.spec = json.loads(spec_content)
            except json.JSONDecodeError:
                # 尝试解析YAML格式
                self.spec = yaml.safe_load(spec_content)
            
            # 验证规范版本
            if "swagger" in self.spec:
                self.spec_version = "swagger"  # Swagger 2.0
                validate_spec(self.spec)
            elif "openapi" in self.spec:
                self.spec_version = "openapi"
                version = self.spec["openapi"]
                if version.startswith("3."):
                    validate_spec(self.spec)
                else:
                    raise ValueError(f"Unsupported OpenAPI version: {version}")
            else:
                raise ValueError("Unknown API specification format")
            
            # 使用prance解析器进行进一步解析和引用解析
            self.parser = ResolvingParser(spec_content=spec_content)
            self.parser.parse()
            
            return True
        except Exception as e:
            print(f"Error loading spec: {e}")
            return False
    
    def get_api_info(self) -> Dict[str, Any]:
        """
        获取API基本信息
        
        Returns:
            Dict: API基本信息
        """
        if not self.spec:
            return {}
        
        info = self.spec.get("info", {})
        servers = self.spec.get("servers", [])
        
        # 提取base_url（从第一个server中获取）
        base_url = ""
        if servers:
            base_url = servers[0].get("url", "")
        
        return {
            "title": info.get("title", ""),
            "description": info.get("description", ""),
            "version": info.get("version", ""),
            "spec_version": self.spec_version,
            "base_url": base_url,
            "contact_info": info.get("contact", {}),
            "license_info": info.get("license", {}),
            "terms_of_service": info.get("termsOfService")
        }
    
    def get_paths(self) -> List[Dict[str, Any]]:
        """
        获取所有API路径和操作
        
        Returns:
            List[Dict]: API路径和操作列表
        """
        if not self.parser:
            return []
        
        paths = self.parser.specification.get("paths", {})
        api_list = []
        
        for path, methods in paths.items():
            for method, operation in methods.items():
                if method in ["get", "post", "put", "delete", "patch", "head", "options", "trace"]:
                    api_list.append({
                        "path": path,
                        "method": method.upper(),
                        "operation_id": operation.get("operationId"),
                        "summary": operation.get("summary"),
                        "description": operation.get("description"),
                        "tags": operation.get("tags", []),
                        "parameters": operation.get("parameters", []),
                        "requestBody": operation.get("requestBody"),
                        "responses": operation.get("responses", {})
                    })
        
        return api_list
    
    def get_components(self) -> Dict[str, Any]:
        """
        获取API组件定义
        
        Returns:
            Dict: 组件定义
        """
        if not self.parser:
            return {}
        
        return self.parser.specification.get("components", {})
    
    def parse_parameters(self, api_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        解析API参数
        
        Args:
            api_info: API信息
            
        Returns:
            List[Dict]: 参数列表
        """
        parameters = api_info.get("parameters", [])
        parsed_params = []
        
        for param in parameters:
            parsed_param = {
                "name": param.get("name"),
                "in": param.get("in"),
                "description": param.get("description"),
                "required": param.get("required", False),
                "type": param.get("type"),
                "schema": param.get("schema", {}),
                "example": param.get("example")
            }
            parsed_params.append(parsed_param)
        
        return parsed_params
    
    def parse_request_body(self, api_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        解析API请求体
        
        Args:
            api_info: API信息
            
        Returns:
            Dict: 请求体信息
        """
        request_body = api_info.get("requestBody", {})
        if not request_body:
            return {}
        
        # 处理OpenAPI 3.0的requestBody格式
        content = request_body.get("content", {})
        # 取第一个媒体类型的schema
        for media_type, media_info in content.items():
            return {
                "content_type": media_type,
                "schema": media_info.get("schema", {}),
                "example": media_info.get("example") or media_info.get("examples", {})
            }
        
        return {}
    
    def parse_responses(self, api_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        解析API响应
        
        Args:
            api_info: API信息
            
        Returns:
            Dict: 响应信息
        """
        responses = api_info.get("responses", {})
        parsed_responses = {}
        
        for status_code, response in responses.items():
            parsed_responses[status_code] = {
                "description": response.get("description"),
                "content": {}
            }
            
            # 处理响应内容
            content = response.get("content", {})
            for media_type, media_info in content.items():
                parsed_responses[status_code]["content"][media_type] = {
                    "schema": media_info.get("schema", {}),
                    "example": media_info.get("example") or media_info.get("examples", {})
                }
        
        return parsed_responses
