"""测试点生成服务"""
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from langchain_classic.chains import LLMChain
from langchain_classic.prompts import PromptTemplate
from langchain_community.llms import Ollama
from langchain_openai import OpenAI
from src.config.settings import settings
from src.models.api import ApiProject, ApiInterface
from src.models.test_point import TestPoint, TestPointStatus, TestPointType, TestPointPriority


class TestPointGenerator:
    """测试点生成服务"""
    
    def __init__(self):
        # 根据配置选择AI模型
        if settings.openai.api_key and settings.openai.api_key != "your-openai-api-key":
            self.llm = OpenAI(
                api_key=settings.openai.api_key,
                model=settings.openai.model,
                temperature=settings.openai.temperature,
                max_tokens=settings.openai.max_tokens
            )
        else:
            self.llm = Ollama(
                base_url=settings.ollama.base_url,
                model=settings.ollama.model,
                temperature=settings.ollama.temperature
            )
    
    async def generate_test_points(self, db: AsyncSession, api_project_id: int) -> Dict[str, Any]:
        """
        根据API项目生成测试点
        
        Args:
            db: 数据库会话
            api_project_id: API项目ID
            
        Returns:
            Dict: 测试点生成结果信息
        """
        try:
            # 获取API项目信息
            project = await db.get(ApiProject, api_project_id)
            if not project:
                return {
                    "success": False,
                    "message": f"API project with ID {api_project_id} not found"
                }
            
            # 获取API接口列表
            interfaces_result = await db.execute(
                select(ApiInterface).where(ApiInterface.project_id == api_project_id)
            )
            interfaces = interfaces_result.scalars().all()
            
            if not interfaces:
                return {
                    "success": False,
                    "message": f"No API interfaces found for project ID {api_project_id}"
                }
            
            generated_points = []
            
            # 为每个接口生成测试点
            for interface in interfaces:
                # 构建接口信息
                interface_info = {
                    "path": interface.path,
                    "method": interface.method,
                    "summary": interface.summary,
                    "description": interface.description,
                    "operation_id": interface.operation_id,
                    "tags": interface.tags,
                    "request_schema": interface.request_schema,
                    "response_schema": interface.response_schema
                }
                
                # 生成测试点
                points = await self._generate_points_for_interface(interface_info)
                
                # 保存测试点到数据库
                for point in points:
                    # 确定测试类型
                    test_type = TestPointType.FUNCTIONAL
                    if point.get("type") == "performance":
                        test_type = TestPointType.PERFORMANCE
                    elif point.get("type") == "security":
                        test_type = TestPointType.SECURITY
                    elif point.get("type") == "compatibility":
                        test_type = TestPointType.COMPATIBILITY
                    elif point.get("type") == "reliability":
                        test_type = TestPointType.RELIABILITY
                    elif point.get("type") == "usability":
                        test_type = TestPointType.USABILITY
                    
                    # 确定优先级
                    priority = TestPointPriority.MEDIUM
                    if point.get("priority") == "high":
                        priority = TestPointPriority.HIGH
                    elif point.get("priority") == "low":
                        priority = TestPointPriority.LOW
                    
                    # 创建测试点
                    test_point = TestPoint(
                        api_project_id=api_project_id,
                        api_interface_id=interface.id,
                        module=point.get("module", "Default"),
                        name=point.get("name"),
                        description=point.get("description"),
                        test_type=test_type,
                        priority=priority,
                        check_points=point.get("check_points", []),
                        input_data=point.get("input_data", {}),
                        expected_result=point.get("expected_result", {}),
                        status=TestPointStatus.DRAFT,
                        special_notes=point.get("special_notes", "")
                    )
                    
                    db.add(test_point)
                    generated_points.append({
                        "interface_id": interface.id,
                        "interface_path": interface.path,
                        "test_point": point
                    })
            
            # 提交事务
            await db.commit()
            
            return {
                "success": True,
                "message": "Test points generated successfully",
                "project_id": api_project_id,
                "generated_count": len(generated_points),
                "test_points": generated_points
            }
        except Exception as e:
            await db.rollback()
            return {
                "success": False,
                "message": f"Failed to generate test points: {str(e)}"
            }
    
    async def _generate_points_for_interface(self, interface_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        为单个API接口生成测试点
        
        Args:
            interface_info: API接口信息
            
        Returns:
            List[Dict]: 生成的测试点列表
        """
        # 创建测试点生成提示词
        prompt_template = PromptTemplate(
            input_variables=["interface_info"],
            template="""
            你是一位资深的质量测试专家，请根据以下API接口信息生成全面的测试点：
            
            {interface_info}
            
            测试点生成要求：
            1. 从功能测试、性能测试、安全测试等多个维度生成测试点
            2. 每个测试点需要包含：
               - module: 模块名称（从接口path或tags中提取）
               - name: 测试点名称（清晰描述测试场景）
               - description: 测试点详细描述
               - type: 测试类型（functional/performance/security/compatibility/reliability/usability）
               - priority: 优先级（high/medium/low）
               - check_points: 测试检查点（详细的验证项）
               - input_data: 输入数据示例
               - expected_result: 预期结果
               - special_notes: 特殊说明（可选）
            3. 考虑边界条件、错误场景、异常输入等
            4. 针对不同的HTTP方法设计合适的测试场景
            5. 生成的测试点需要覆盖接口的所有功能点
            
            请按照以下JSON格式返回测试点列表：
            [
                {{
                    "module": "用户管理",
                    "name": "创建用户-正常流程",
                    "description": "测试创建用户的正常流程",
                    "type": "functional",
                    "priority": "high",
                    "check_points": ["检查响应状态码为200", "检查返回用户ID", "检查用户信息正确"],
                    "input_data": {{"username": "testuser", "email": "test@example.com"}},
                    "expected_result": {{"status": "success", "data": {{"id": 1, "username": "testuser"}}}},
                    "special_notes": "需要确保数据库中不存在同名用户"
                }}
            ]
            """
        )
        
        # 创建LLM Chain
        chain = LLMChain(llm=self.llm, prompt=prompt_template)
        
        # 执行测试点生成
        result = chain.run(interface_info=str(interface_info))
        
        # 解析测试点结果
        return self._parse_test_points(result)
    
    def _parse_test_points(self, result: str) -> List[Dict[str, Any]]:
        """
        解析生成的测试点
        
        Args:
            result: LLM返回的测试点结果
            
        Returns:
            List[Dict]: 解析后的测试点列表
        """
        import json
        
        try:
            # 提取JSON部分
            if "[" in result:
                json_start = result.index("[")
                json_end = result.rindex("]") + 1
                json_str = result[json_start:json_end]
                return json.loads(json_str)
            else:
                return []
        except Exception as e:
            print(f"Failed to parse test points: {str(e)}")
            return []
    
    async def get_test_points(self, db: AsyncSession, project_id: int) -> List[Dict[str, Any]]:
        """
        获取项目的测试点列表
        
        Args:
            db: 数据库会话
            project_id: API项目ID
            
        Returns:
            List[Dict]: 测试点列表
        """
        try:
            result = await db.execute(
                select(TestPoint)
                .where(TestPoint.api_project_id == project_id)
                .order_by(TestPoint.module, TestPoint.priority.desc())
            )
            
            test_points = result.scalars().all()
            
            return [{
                "id": point.id,
                "module": point.module,
                "name": point.name,
                "description": point.description,
                "test_type": point.test_type.value,
                "priority": point.priority.value,
                "check_points": point.check_points,
                "input_data": point.input_data,
                "expected_result": point.expected_result,
                "status": point.status.value,
                "review_comments": point.review_comments,
                "special_notes": point.special_notes,
                "created_at": point.created_at
            } for point in test_points]
        except Exception as e:
            print(f"Failed to get test points: {str(e)}")
            return []
    
    async def update_test_point_status(self, db: AsyncSession, test_point_id: int, status: TestPointStatus) -> Dict[str, Any]:
        """
        更新测试点状态
        
        Args:
            db: 数据库会话
            test_point_id: 测试点ID
            status: 新的状态
            
        Returns:
            Dict: 更新结果信息
        """
        try:
            test_point = await db.get(TestPoint, test_point_id)
            if not test_point:
                return {
                    "success": False,
                    "message": f"Test point with ID {test_point_id} not found"
                }
            
            test_point.status = status
            await db.commit()
            
            return {
                "success": True,
                "message": "Test point status updated successfully"
            }
        except Exception as e:
            await db.rollback()
            return {
                "success": False,
                "message": f"Failed to update test point status: {str(e)}"
            }
