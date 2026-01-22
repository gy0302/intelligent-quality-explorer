"""测试脚本和测试数据生成服务"""
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from langchain_classic.chains import LLMChain
from langchain_classic.prompts import PromptTemplate
from langchain_community.llms import Ollama
from langchain_openai import OpenAI
from src.config.settings import settings
from src.models.test_case import TestCase
from src.models.test_script import TestScript, TestData, TestScriptType, TestScriptStatus


class TestScriptGenerator:
    """测试脚本生成服务"""
    
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
    
    async def generate_test_scripts(self, db: AsyncSession, test_case_ids: List[int]) -> Dict[str, Any]:
        """
        根据测试用例生成测试脚本和测试数据
        
        Args:
            db: 数据库会话
            test_case_ids: 测试用例ID列表
            
        Returns:
            Dict: 测试脚本生成结果信息
        """
        try:
            # 获取测试用例列表
            result = await db.execute(
                select(TestCase).where(TestCase.id.in_(test_case_ids))
            )
            test_cases = result.scalars().all()
            
            if not test_cases:
                return {
                    "success": False,
                    "message": "No test cases found with the provided IDs"
                }
            
            generated_scripts = []
            
            # 为每个测试用例生成测试脚本
            for test_case in test_cases:
                # 构建测试用例信息
                case_info = {
                    "id": test_case.id,
                    "case_name": test_case.case_name,
                    "description": test_case.description,
                    "steps": test_case.steps,
                    "input_data": test_case.input_data,
                    "expected_result": test_case.expected_result,
                    "priority": test_case.priority.value,
                    "status": test_case.status.value
                }
                
                # 生成测试脚本
                script = await self._generate_script_for_case(case_info)
                
                # 生成测试数据
                test_data = await self._generate_test_data_for_script(script)
                
                # 保存测试脚本到数据库
                test_script = TestScript(
                    test_case_id=test_case.id,
                    script_type=TestScriptType.PYTHON,
                    script_content=script,
                    status=TestScriptStatus.DRAFT
                )
                db.add(test_script)
                await db.flush()  # 获取脚本ID
                
                # 保存测试数据到数据库
                data_records = []
                for data in test_data:
                    data_record = TestData(
                        test_script_id=test_script.id,
                        data_name=data.get("name"),
                        data_type=data.get("type"),
                        data_content=data.get("content"),
                        description=data.get("description")
                    )
                    db.add(data_record)
                    data_records.append(data)
                
                generated_scripts.append({
                    "test_case_id": test_case.id,
                    "test_script": script,
                    "test_data": data_records
                })
            
            # 提交事务
            await db.commit()
            
            return {
                "success": True,
                "message": "Test scripts and data generated successfully",
                "generated_count": len(generated_scripts),
                "test_scripts": generated_scripts
            }
        except Exception as e:
            await db.rollback()
            return {
                "success": False,
                "message": f"Failed to generate test scripts: {str(e)}"
            }
    
    async def _generate_script_for_case(self, test_case: Dict[str, Any]) -> str:
        """
        根据单个测试用例生成测试脚本
        
        Args:
            test_case: 测试用例信息
            
        Returns:
            str: 生成的测试脚本内容
        """
        # 创建测试脚本生成提示词
        prompt_template = PromptTemplate(
            input_variables=["test_case"],
            template="""
            你是一位资深的测试开发工程师，请根据以下测试用例生成详细的Python测试脚本：
            
            {test_case}
            
            测试脚本生成要求：
            1. 使用Python语言和requests库编写
            2. 脚本需要包含：
               - 必要的导入语句
               - 测试用例类（继承unittest.TestCase）
               - 测试方法（以test_开头）
               - 清晰的注释说明
               - 完整的测试步骤实现
               - 输入数据处理
               - 预期结果验证
               - 异常处理
            3. 测试脚本需要可直接执行，不需要额外修改
            4. 使用断言验证预期结果
            5. 包含日志记录功能
            6. 遵循Python PEP 8编码规范
            
            请只返回测试脚本内容，不要添加任何解释或说明。
            """
        )
        
        # 创建LLM Chain
        chain = LLMChain(llm=self.llm, prompt=prompt_template)
        
        # 执行测试脚本生成
        result = chain.run(test_case=str(test_case))
        
        return result
    
    async def _generate_test_data_for_script(self, script: str) -> List[Dict[str, Any]]:
        """
        根据测试脚本生成测试数据
        
        Args:
            script: 测试脚本内容
            
        Returns:
            List[Dict]: 测试数据列表
        """
        # 创建测试数据生成提示词
        prompt_template = PromptTemplate(
            input_variables=["script"],
            template="""
            你是一位资深的测试数据工程师，请根据以下测试脚本生成详细的测试数据：
            
            {script}
            
            测试数据生成要求：
            1. 识别脚本中需要的所有测试数据
            2. 生成多种类型的测试数据：正常数据、边界数据、异常数据
            3. 测试数据需要结构化，包含：
               - name: 数据名称
               - type: 数据类型
               - content: 数据内容（JSON格式）
               - description: 数据描述
            4. 考虑数据的多样性和覆盖性
            5. 遵循行业数据规范
            6. 考虑数据的可维护性
            
            请按照以下JSON格式返回测试数据列表：
            [
                {{
                    "name": "正常用户数据",
                    "type": "json",
                    "content": {{
                        "username": "testuser",
                        "email": "test@example.com",
                        "password": "Test123!"
                    }},
                    "description": "用于测试正常流程的用户数据"
                }}
            ]
            """
        )
        
        # 创建LLM Chain
        chain = LLMChain(llm=self.llm, prompt=prompt_template)
        
        # 执行测试数据生成
        result = chain.run(script=script)
        
        # 解析测试数据结果
        return self._parse_test_data(result)
    
    def _parse_test_data(self, result: str) -> List[Dict[str, Any]]:
        """
        解析生成的测试数据
        
        Args:
            result: LLM返回的测试数据结果
            
        Returns:
            List[Dict]: 解析后的测试数据列表
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
            print(f"Failed to parse test data: {str(e)}")
            return []
    
    async def get_test_scripts(self, db: AsyncSession, project_id: int) -> List[Dict[str, Any]]:
        """
        获取项目的测试脚本列表
        
        Args:
            db: 数据库会话
            project_id: API项目ID
            
        Returns:
            List[Dict]: 测试脚本列表
        """
        try:
            # 先获取项目的测试用例ID
            result = await db.execute(
                select(TestCase.id)
                .join(TestPoint)
                .where(TestPoint.api_project_id == project_id)
            )
            test_case_ids = [case_id for case_id, in result.all()]
            
            if not test_case_ids:
                return []
            
            # 获取测试脚本
            result = await db.execute(
                select(TestScript)
                .where(TestScript.test_case_id.in_(test_case_ids))
                .order_by(TestScript.created_at)
            )
            
            test_scripts = result.scalars().all()
            
            return [{
                "id": script.id,
                "test_case_id": script.test_case_id,
                "script_type": script.script_type.value,
                "script_content": script.script_content,
                "status": script.status.value,
                "created_at": script.created_at,
                "updated_at": script.updated_at
            } for script in test_scripts]
        except Exception as e:
            print(f"Failed to get test scripts: {str(e)}")
            return []
    
    async def update_test_script_status(self, db: AsyncSession, test_script_id: int, status: TestScriptStatus) -> Dict[str, Any]:
        """
        更新测试脚本状态
        
        Args:
            db: 数据库会话
            test_script_id: 测试脚本ID
            status: 新的状态
            
        Returns:
            Dict: 更新结果信息
        """
        try:
            test_script = await db.get(TestScript, test_script_id)
            if not test_script:
                return {
                    "success": False,
                    "message": f"Test script with ID {test_script_id} not found"
                }
            
            test_script.status = status
            await db.commit()
            
            return {
                "success": True,
                "message": "Test script status updated successfully"
            }
        except Exception as e:
            await db.rollback()
            return {
                "success": False,
                "message": f"Failed to update test script status: {str(e)}"
            }
