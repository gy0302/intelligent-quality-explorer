"""测试用例生成服务"""
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from langchain_classic.chains import LLMChain
from langchain_classic.prompts import PromptTemplate
from langchain_community.llms import Ollama
from langchain_openai import OpenAI
from src.config.settings import settings
from src.models.test_point import TestPoint
from src.models.test_case import TestCase, TestCaseStatus, TestCasePriority


class TestCaseGenerator:
    """测试用例生成服务"""
    
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
    
    async def generate_test_cases(self, db: AsyncSession, test_point_ids: List[int]) -> Dict[str, Any]:
        """
        根据测试点生成测试用例
        
        Args:
            db: 数据库会话
            test_point_ids: 测试点ID列表
            
        Returns:
            Dict: 测试用例生成结果信息
        """
        try:
            # 获取测试点列表
            result = await db.execute(
                select(TestPoint).where(TestPoint.id.in_(test_point_ids))
            )
            test_points = result.scalars().all()
            
            if not test_points:
                return {
                    "success": False,
                    "message": "No test points found with the provided IDs"
                }
            
            generated_cases = []
            
            # 为每个测试点生成测试用例
            for test_point in test_points:
                # 构建测试点信息
                point_info = {
                    "id": test_point.id,
                    "module": test_point.module,
                    "name": test_point.name,
                    "description": test_point.description,
                    "test_type": test_point.test_type.value,
                    "priority": test_point.priority.value,
                    "check_points": test_point.check_points,
                    "input_data": test_point.input_data,
                    "expected_result": test_point.expected_result,
                    "special_notes": test_point.special_notes
                }
                
                # 生成测试用例
                cases = await self._generate_cases_for_point(point_info)
                
                # 保存测试用例到数据库
                for case in cases:
                    # 确定优先级
                    priority = TestCasePriority.MEDIUM
                    if case.get("priority") == "high":
                        priority = TestCasePriority.HIGH
                    elif case.get("priority") == "low":
                        priority = TestCasePriority.LOW
                    
                    # 创建测试用例
                    test_case = TestCase(
                        test_point_id=test_point.id,
                        case_name=case.get("case_name"),
                        description=case.get("description"),
                        steps=case.get("steps"),
                        input_data=case.get("input_data"),
                        expected_result=case.get("expected_result"),
                        priority=priority,
                        status=TestCaseStatus.DRAFT
                    )
                    
                    db.add(test_case)
                    generated_cases.append({
                        "test_point_id": test_point.id,
                        "test_case": case
                    })
            
            # 提交事务
            await db.commit()
            
            return {
                "success": True,
                "message": "Test cases generated successfully",
                "generated_count": len(generated_cases),
                "test_cases": generated_cases
            }
        except Exception as e:
            await db.rollback()
            return {
                "success": False,
                "message": f"Failed to generate test cases: {str(e)}"
            }
    
    async def _generate_cases_for_point(self, test_point: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        根据单个测试点生成测试用例
        
        Args:
            test_point: 测试点信息
            
        Returns:
            List[Dict]: 生成的测试用例列表
        """
        # 创建测试用例生成提示词
        prompt_template = PromptTemplate(
            input_variables=["test_point"],
            template="""
            你是一位资深的质量测试专家，请根据以下测试点生成详细的测试用例：
            
            {test_point}
            
            测试用例生成要求：
            1. 每个测试用例需要包含：
               - case_name: 测试用例名称（清晰描述测试场景）
               - description: 测试用例详细描述
               - steps: 测试步骤（详细的操作步骤，按顺序）
               - input_data: 输入数据（详细的测试数据）
               - expected_result: 预期结果（详细的验证结果）
               - priority: 优先级（high/medium/low，与测试点一致）
            2. 测试步骤需要具体、可执行，包含每个操作的详细说明
            3. 输入数据需要具体、完整，包含所有必要的参数
            4. 预期结果需要明确、可验证，包含具体的响应内容和状态
            5. 生成的测试用例需要覆盖测试点的所有检查点
            6. 考虑边界条件和异常情况
            
            请按照以下JSON格式返回测试用例列表：
            [
                {{
                    "case_name": "创建用户-正常流程",
                    "description": "测试创建用户的正常流程，验证用户信息是否正确保存",
                    "steps": [
                        "1. 准备测试数据：username=testuser, email=test@example.com, password=Test123!",
                        "2. 调用API接口：POST /api/users",
                        "3. 传递参数：{{\"username\": \"testuser\", \"email\": \"test@example.com\", \"password\": \"Test123!\"}}",
                        "4. 检查响应状态码是否为201",
                        "5. 检查返回的用户信息是否正确"
                    ],
                    "input_data": {{
                        "username": "testuser",
                        "email": "test@example.com",
                        "password": "Test123!"
                    }},
                    "expected_result": {{
                        "status_code": 201,
                        "response_body": {{
                            "id": 1,
                            "username": "testuser",
                            "email": "test@example.com",
                            "created_at": "2023-01-01T00:00:00Z"
                        }}
                    }},
                    "priority": "high"
                }}
            ]
            """
        )
        
        # 创建LLM Chain
        chain = LLMChain(llm=self.llm, prompt=prompt_template)
        
        # 执行测试用例生成
        result = chain.run(test_point=str(test_point))
        
        # 解析测试用例结果
        return self._parse_test_cases(result)
    
    def _parse_test_cases(self, result: str) -> List[Dict[str, Any]]:
        """
        解析生成的测试用例
        
        Args:
            result: LLM返回的测试用例结果
            
        Returns:
            List[Dict]: 解析后的测试用例列表
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
            print(f"Failed to parse test cases: {str(e)}")
            return []
    
    async def get_test_cases(self, db: AsyncSession, project_id: int) -> List[Dict[str, Any]]:
        """
        获取项目的测试用例列表
        
        Args:
            db: 数据库会话
            project_id: API项目ID
            
        Returns:
            List[Dict]: 测试用例列表
        """
        try:
            # 先获取项目的测试点ID
            test_points_result = await db.execute(
                select(TestPoint.id).where(TestPoint.api_project_id == project_id)
            )
            test_point_ids = [point_id for point_id, in test_points_result.all()]
            
            if not test_point_ids:
                return []
            
            # 获取测试用例
            result = await db.execute(
                select(TestCase)
                .where(TestCase.test_point_id.in_(test_point_ids))
                .order_by(TestCase.priority.desc(), TestCase.created_at)
            )
            
            test_cases = result.scalars().all()
            
            return [{
                "id": case.id,
                "test_point_id": case.test_point_id,
                "case_name": case.case_name,
                "description": case.description,
                "steps": case.steps,
                "input_data": case.input_data,
                "expected_result": case.expected_result,
                "actual_result": case.actual_result,
                "priority": case.priority.value,
                "status": case.status.value,
                "execution_status": case.execution_status,
                "created_at": case.created_at
            } for case in test_cases]
        except Exception as e:
            print(f"Failed to get test cases: {str(e)}")
            return []
    
    async def update_test_case_status(self, db: AsyncSession, test_case_id: int, status: TestCaseStatus) -> Dict[str, Any]:
        """
        更新测试用例状态
        
        Args:
            db: 数据库会话
            test_case_id: 测试用例ID
            status: 新的状态
            
        Returns:
            Dict: 更新结果信息
        """
        try:
            test_case = await db.get(TestCase, test_case_id)
            if not test_case:
                return {
                    "success": False,
                    "message": f"Test case with ID {test_case_id} not found"
                }
            
            test_case.status = status
            await db.commit()
            
            return {
                "success": True,
                "message": "Test case status updated successfully"
            }
        except Exception as e:
            await db.rollback()
            return {
                "success": False,
                "message": f"Failed to update test case status: {str(e)}"
            }
