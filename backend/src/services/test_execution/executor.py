"""测试执行服务"""
import asyncio
import subprocess
import sys
import tempfile
import os
import json
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models.test_script import TestScript, TestData
from src.models.test_case import TestCase
from src.models.test_point import TestPoint


class TestExecutor:
    """测试执行服务"""
    
    async def execute_test_scripts(self, db: AsyncSession, script_ids: List[int]) -> Dict[str, Any]:
        """
        执行测试脚本
        
        Args:
            db: 数据库会话
            script_ids: 测试脚本ID列表
            
        Returns:
            Dict: 测试执行结果信息
        """
        try:
            # 获取测试脚本列表（过滤已删除数据）
            result = await db.execute(
                select(TestScript).where(TestScript.id.in_(script_ids), TestScript.is_active == True)
            )
            test_scripts = result.scalars().all()
            
            if not test_scripts:
                return {
                    "success": False,
                    "message": "No test scripts found with the provided IDs"
                }
            
            execution_results = []
            
            # 执行每个测试脚本
            for test_script in test_scripts:
                # 获取测试数据（过滤已删除数据）
                data_result = await db.execute(
                    select(TestData).where(TestData.test_script_id == test_script.id, TestData.is_active == True)
                )
                test_data = data_result.scalars().all()
                
                # 执行脚本
                result = await self._execute_script(
                    script_content=test_script.script_content,
                    script_type=test_script.script_type.value,
                    test_data=[{
                        "name": data.data_name,
                        "type": data.data_type,
                        "content": data.data_content,
                        "description": data.description
                    } for data in test_data]
                )
                
                # 获取测试用例的执行状态（过滤已删除数据）
                test_case_result = await db.execute(
                    select(TestCase).where(TestCase.id == test_script.test_case_id, TestCase.is_active == True)
                )
                test_case = test_case_result.scalars().first()
                if test_case:
                    test_case.execution_status = "completed" if result["success"] else "failed"
                    test_case.actual_result = result["output"]
                    await db.flush()
                
                execution_results.append({
                    "script_id": test_script.id,
                    "test_case_id": test_script.test_case_id,
                    "result": result
                })
            
            # 提交事务
            await db.commit()
            
            return {
                "success": True,
                "message": "Test scripts executed successfully",
                "execution_results": execution_results
            }
        except Exception as e:
            await db.rollback()
            return {
                "success": False,
                "message": f"Failed to execute test scripts: {str(e)}"
            }
    
    async def _execute_script(self, script_content: str, script_type: str, test_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        执行单个测试脚本
        
        Args:
            script_content: 测试脚本内容
            script_type: 脚本类型
            test_data: 测试数据列表
            
        Returns:
            Dict: 测试脚本执行结果
        """
        if script_type == "python":
            return await self._execute_python_script(script_content, test_data)
        elif script_type == "javascript":
            return await self._execute_js_script(script_content, test_data)
        elif script_type == "java":
            return await self._execute_java_script(script_content, test_data)
        else:
            return {
                "success": False,
                "output": f"Unsupported script type: {script_type}",
                "error": f"Script type {script_type} is not supported"
            }
    
    async def _execute_python_script(self, script_content: str, test_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        执行Python测试脚本
        
        Args:
            script_content: Python脚本内容
            test_data: 测试数据列表
            
        Returns:
            Dict: 脚本执行结果
        """
        try:
            # 创建临时Python文件
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
                f.write(script_content)
                temp_file_path = f.name
            
            # 创建临时测试数据文件
            data_file_path = None
            if test_data:
                data_file_path = temp_file_path.replace('.py', '_data.json')
                with open(data_file_path, 'w', encoding='utf-8') as f:
                    json.dump(test_data, f, ensure_ascii=False, indent=2)
            
            try:
                # 执行Python脚本
                process = await asyncio.create_subprocess_exec(
                    sys.executable,
                    temp_file_path,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    env={**os.environ, 'TEST_DATA_FILE': data_file_path}
                )
                
                stdout, stderr = await process.communicate()
                output = stdout.decode('utf-8')
                error = stderr.decode('utf-8')
                
                return {
                    "success": process.returncode == 0,
                    "output": output,
                    "error": error,
                    "return_code": process.returncode
                }
            finally:
                # 清理临时文件
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                if data_file_path and os.path.exists(data_file_path):
                    os.unlink(data_file_path)
                    
        except Exception as e:
            return {
                "success": False,
                "output": str(e),
                "error": f"Failed to execute Python script: {str(e)}"
            }
    
    async def _execute_js_script(self, script_content: str, test_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        执行JavaScript测试脚本
        
        Args:
            script_content: JavaScript脚本内容
            test_data: 测试数据列表
            
        Returns:
            Dict: 脚本执行结果
        """
        try:
            # 检查Node.js是否可用
            try:
                process = await asyncio.create_subprocess_exec(
                    'node', '--version',
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                await process.communicate()
                if process.returncode != 0:
                    return {
                        "success": False,
                        "output": "Node.js is not available",
                        "error": "Node.js is not installed or not in PATH"
                    }
            except FileNotFoundError:
                return {
                    "success": False,
                    "output": "Node.js is not available",
                    "error": "Node.js is not installed or not in PATH"
                }
            
            # 创建临时JS文件
            with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False, encoding='utf-8') as f:
                f.write(script_content)
                temp_file_path = f.name
            
            try:
                # 执行JS脚本
                process = await asyncio.create_subprocess_exec(
                    'node', temp_file_path,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await process.communicate()
                output = stdout.decode('utf-8')
                error = stderr.decode('utf-8')
                
                return {
                    "success": process.returncode == 0,
                    "output": output,
                    "error": error,
                    "return_code": process.returncode
                }
            finally:
                # 清理临时文件
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            return {
                "success": False,
                "output": str(e),
                "error": f"Failed to execute JavaScript script: {str(e)}"
            }
    
    async def _execute_java_script(self, script_content: str, test_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        执行Java测试脚本
        
        Args:
            script_content: Java脚本内容
            test_data: 测试数据列表
            
        Returns:
            Dict: 脚本执行结果
        """
        return {
            "success": False,
            "output": "Java script execution not fully implemented in MVP",
            "error": "Java script execution is not fully implemented yet"
        }
    
    async def get_execution_results(self, db: AsyncSession, project_id: int) -> List[Dict[str, Any]]:
        """
        获取项目的测试执行结果
        
        Args:
            db: 数据库会话
            project_id: API项目ID
            
        Returns:
            List[Dict]: 测试执行结果列表
        """
        try:
            # 先获取项目的测试点ID（过滤已删除数据）
            test_points_result = await db.execute(
                select(TestPoint.id).where(TestPoint.api_project_id == project_id, TestPoint.is_active == True)
            )
            test_point_ids = [point_id for point_id, in test_points_result.all()]
            
            if not test_point_ids:
                return []
            
            # 获取测试用例（过滤已删除数据）
            test_cases_result = await db.execute(
                select(TestCase).where(TestCase.test_point_id.in_(test_point_ids), TestCase.is_active == True)
            )
            test_cases = test_cases_result.scalars().all()
            
            if not test_cases:
                return []
            
            # 获取测试脚本（过滤已删除数据）
            test_scripts_result = await db.execute(
                select(TestScript)
                .where(
                    TestScript.test_case_id.in_([case.id for case in test_cases]),
                    TestScript.is_active == True
                )
            )
            test_scripts = test_scripts_result.scalars().all()
            
            results = []
            for script in test_scripts:
                # 获取对应的测试用例
                test_case = next((case for case in test_cases if case.id == script.test_case_id), None)
                if test_case:
                    results.append({
                        "script_id": script.id,
                        "test_case_id": script.test_case_id,
                        "case_name": test_case.case_name,
                        "script_type": script.script_type.value,
                        "execution_status": test_case.execution_status,
                        "actual_result": test_case.actual_result,
                        "executed_at": test_case.updated_at
                    })
            
            return results
        except Exception as e:
            print(f"Failed to get execution results: {str(e)}")
            return []
