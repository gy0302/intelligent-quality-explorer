from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
import json

from src.shared.database import get_db_session
from src.services.test_execution.executor import TestExecutor
from src.services.test_execution.report_generator import TestReportGenerator
from src.schemas.test_execution import (
    TestExecutionRequest, TestExecutionResponse,
    TestReportResponse, TestReportExportRequest
)

router = APIRouter(prefix="/api/v1/test-execution", tags=["测试执行"])

# 测试执行服务实例
test_executor = TestExecutor()
# 测试报告生成服务实例
test_report_generator = TestReportGenerator()

@router.post("/execute", response_model=TestExecutionResponse, summary="执行测试脚本", description="执行指定的测试脚本列表")
async def execute_test_scripts(
    request: TestExecutionRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """执行指定的测试脚本列表，返回执行结果"""
    try:
        result = await test_executor.execute_test_scripts(
            db=db,
            script_ids=request.script_ids
        )
        
        if not result["success"]:
            raise HTTPException(status_code=404, detail=result["message"])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"执行测试脚本失败: {str(e)}")

@router.get("/results", response_model=List[Dict[str, Any]], summary="获取测试执行结果", description="获取指定项目的测试执行结果")
async def get_execution_results(
    project_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """获取指定项目的测试执行结果"""
    try:
        results = await test_executor.get_execution_results(db=db, project_id=project_id)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取测试执行结果失败: {str(e)}")

@router.get("/report", response_model=TestReportResponse, summary="生成测试报告", description="生成指定项目的测试报告")
async def generate_test_report(
    project_id: int,
    detailed: bool = False,
    db: AsyncSession = Depends(get_db_session)
):
    """生成指定项目的测试报告，可选择是否生成详细报告"""
    try:
        if detailed:
            result = await test_report_generator.generate_detailed_report(db=db, project_id=project_id)
        else:
            result = await test_report_generator.generate_test_report(db=db, project_id=project_id)
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["message"])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成测试报告失败: {str(e)}")

@router.post("/report/export", summary="导出测试报告", description="导出指定项目的测试报告，支持JSON和文本格式")
async def export_test_report(
    request: TestReportExportRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """导出指定项目的测试报告，支持JSON和文本格式"""
    try:
        # 生成测试报告
        result = await test_report_generator.generate_test_report(db=db, project_id=request.project_id)
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["message"])
        
        report = result["report"]
        
        # 根据格式导出报告
        if request.format == "json":
            report_content = test_report_generator.export_report_to_json(report)
            media_type = "application/json"
            filename = f"test_report_{request.project_id}.json"
        elif request.format == "text":
            report_content = test_report_generator.export_report_to_text(report)
            media_type = "text/plain"
            filename = f"test_report_{request.project_id}.txt"
        else:
            raise HTTPException(status_code=400, detail="不支持的报告格式")
        
        # 返回文件下载响应
        return Response(
            content=report_content,
            media_type=media_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出测试报告失败: {str(e)}")
