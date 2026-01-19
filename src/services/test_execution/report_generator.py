"""测试报告生成服务"""
import json
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime
from src.models.test_case import TestCase
from src.models.test_script import TestScript
from src.models.test_point import TestPoint
from src.models.api import ApiProject, ApiInterface
from src.services.test_execution.executor import TestExecutor


class TestReportGenerator:
    """测试报告生成服务"""
    
    def _calculate_summary(self, execution_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        计算测试结果统计信息
        
        Args:
            execution_results: 测试执行结果列表
            
        Returns:
            Dict: 统计信息
        """
        total = len(execution_results)
        passed = 0
        failed = 0
        
        for result in execution_results:
            if result["execution_status"] == "completed":
                passed += 1
            else:
                failed += 1
        
        success_rate = 0.0
        if total > 0:
            success_rate = round((passed / total) * 100, 2)
        
        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "success_rate": success_rate
        }
    
    async def generate_test_report(self, db: AsyncSession, project_id: int) -> Dict[str, Any]:
        """
        生成项目的测试报告
        
        Args:
            db: 数据库会话
            project_id: API项目ID
            
        Returns:
            Dict: 测试报告
        """
        try:
            # 获取项目信息
            project = await db.get(ApiProject, project_id)
            if not project:
                return {
                    "success": False,
                    "message": f"测试报告生成: 项目 {project_id} 不存在"
                }
            
            # 获取执行结果
            executor = TestExecutor()
            execution_results = await executor.get_execution_results(db, project_id)
            
            # 计算统计信息
            summary = self._calculate_summary(execution_results)
            
            # 生成基础报告
            report = {
                "project_id": project_id,
                "project_name": project.name,
                "report_date": datetime.utcnow().isoformat(),
                "summary": summary,
                "execution_results": execution_results,
                "total_scripts": summary["total"],
                "passed_count": summary["passed"],
                "failed_count": summary["failed"],
                "success_rate": summary["success_rate"]
            }
            
            return {
                "success": True,
                "message": "测试报告生成: 报告生成成功",
                "report": report
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"测试报告生成: 生成基础报告失败 - {str(e)}"
            }

    async def generate_detailed_report(self, db: AsyncSession, project_id: int) -> Dict[str, Any]:
        """
        生成详细的测试报告
        
        Args:
            db: 数据库会话
            project_id: API项目ID
            
        Returns:
            Dict: 详细测试报告
        """
        try:
            # 获取项目信息
            project = await db.get(ApiProject, project_id)
            if not project:
                return {
                    "success": False,
                    "message": f"测试报告生成: 项目 {project_id} 不存在"
                }
            
            # 获取执行结果
            executor = TestExecutor()
            execution_results = await executor.get_execution_results(db, project_id)
            
            # 计算统计信息
            summary = self._calculate_summary(execution_results)
            
            # 获取API接口信息
            interfaces_result = await db.execute(
                select(ApiInterface)
                .where(ApiInterface.api_project_id == project_id)
            )
            interfaces = interfaces_result.scalars().all()
            
            # 获取测试点信息（过滤已删除数据）
            test_points_result = await db.execute(
                select(TestPoint)
                .where(TestPoint.api_project_id == project_id, TestPoint.is_active == True)
            )
            test_points = test_points_result.scalars().all()
            
            # 获取测试用例信息（过滤已删除数据）
            test_cases_result = await db.execute(
                select(TestCase)
                .where(
                    TestCase.test_point_id.in_([point.id for point in test_points]),
                    TestCase.is_active == True
                )
            )
            test_cases = test_cases_result.scalars().all()
            
            # 获取测试脚本信息（过滤已删除数据）
            test_scripts_result = await db.execute(
                select(TestScript)
                .where(
                    TestScript.test_case_id.in_([case.id for case in test_cases]),
                    TestScript.is_active == True
                )
            )
            test_scripts = test_scripts_result.scalars().all()
            
            # 构建详细报告
            detailed_report = {
                "project_id": project_id,
                "project_name": project.name,
                "report_date": datetime.utcnow().isoformat(),
                "summary": summary,
                "execution_results": execution_results,
                "total_scripts": summary["total"],
                "passed_count": summary["passed"],
                "failed_count": summary["failed"],
                "success_rate": summary["success_rate"],
                "api_interfaces": [{"id": interface.id,
                    "path": interface.path,
                    "method": interface.method,
                    "description": interface.description
                } for interface in interfaces],
                "test_points": [{"id": point.id,
                    "name": point.name,
                    "module": point.module,
                    "test_type": point.test_type.value,
                    "priority": point.priority.value,
                    "status": point.status.value
                } for point in test_points],
                "test_cases": [{"id": case.id,
                    "case_name": case.case_name,
                    "priority": case.priority.value,
                    "status": case.status.value,
                    "execution_status": case.execution_status
                } for case in test_cases],
                "test_scripts": [{"id": script.id,
                    "script_type": script.script_type.value,
                    "status": script.status.value
                } for script in test_scripts]
            }
            
            return {
                "success": True,
                "message": "测试报告生成: 生成详细报告成功",
                "report": detailed_report
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"测试报告生成: 生成详细报告失败 - {str(e)}"
            }
    

    
    def export_report_to_json(self, report: Dict[str, Any]) -> str:
        """
        将报告导出为JSON格式
        
        Args:
            report: 测试报告
            
        Returns:
            str: JSON格式的报告
        """
        return json.dumps(report, ensure_ascii=False, indent=2)
    
    def export_report_to_text(self, report: Dict[str, Any]) -> str:
        """
        将报告导出为文本格式
        
        Args:
            report: 测试报告
            
        Returns:
            str: 文本格式的报告
        """
        text = []
        text.append("=" * 60)
        text.append(f"测试报告 - {report['project_name']}")
        text.append(f"报告日期: {report['report_date']}")
        text.append("=" * 60)
        text.append("")
        text.append("测试概览:")
        text.append(f"总脚本数: {report['total_scripts']}")
        text.append(f"通过数: {report['passed_count']}")
        text.append(f"失败数: {report['failed_count']}")
        text.append(f"成功率: {report['success_rate']}%")
        text.append("")
        text.append("=" * 60)
        text.append("详细执行结果:")
        text.append("")
        
        for i, result in enumerate(report['execution_results'], 1):
            text.append(f"{i}. 测试用例: {result['case_name']}")
            text.append(f"   脚本ID: {result['script_id']}")
            text.append(f"   脚本类型: {result['script_type']}")
            text.append(f"   执行状态: {'通过' if result['execution_status'] == 'completed' else '失败'}")
            text.append("   " + "-" * 40)
        
        return "\n".join(text)
