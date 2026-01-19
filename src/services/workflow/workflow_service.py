"""工作流管理服务"""
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime
from src.models.workflow import Workflow, WorkflowStep, WorkflowStatus, WorkflowStepRecord
from src.models.test_point import TestPointStatus
from src.models.test_case import TestCaseStatus
from src.models.test_script import TestScriptStatus
from src.config.settings import settings


class WorkflowService:
    """工作流管理服务"""
    
    def __init__(self):
        # 工作流步骤配置
        self.workflow_steps = settings.workflow_steps
    
    async def create_workflow(self, db: AsyncSession, api_project_id: int, name: str) -> Dict[str, Any]:
        """
        创建新的工作流
        
        Args:
            db: 数据库会话
            api_project_id: API项目ID
            name: 工作流名称
            
        Returns:
            Dict: 创建的工作流信息
        """
        try:
            # 创建工作流
            workflow = Workflow(
                api_project_id=api_project_id,
                name=name,
                current_step=WorkflowStep.API_IMPORT,
                status=WorkflowStatus.IN_PROGRESS,
                progress=0,
                execution_log=[]
            )
            
            db.add(workflow)
            await db.flush()
            
            # 创建初始步骤记录
            step_record = WorkflowStepRecord(
                workflow_id=workflow.id,
                step=WorkflowStep.API_IMPORT,
                status=WorkflowStatus.IN_PROGRESS,
                start_time=datetime.utcnow(),
                result={}
            )
            
            db.add(step_record)
            await db.commit()
            await db.refresh(workflow)
            
            return {
                "success": True,
                "message": "工作流创建成功",
                "workflow": {
                    "id": workflow.id,
                    "name": workflow.name,
                    "current_step": workflow.current_step.value,
                    "status": workflow.status.value,
                    "progress": workflow.progress,
                    "created_at": workflow.created_at
                }
            }
        except Exception as e:
            await db.rollback()
            return {
                "success": False,
                "message": f"创建工作流失败: {str(e)}"
            }
    
    async def update_workflow_step(self, db: AsyncSession, workflow_id: int, step: WorkflowStep, status: WorkflowStatus, result: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        更新工作流步骤
        
        Args:
            db: 数据库会话
            workflow_id: 工作流ID
            step: 步骤
            status: 状态
            result: 步骤结果
            
        Returns:
            Dict: 更新结果
        """
        try:
            # 获取工作流
            workflow = await db.get(Workflow, workflow_id)
            if not workflow:
                return {
                    "success": False,
                    "message": f"工作流ID {workflow_id} 不存在"
                }
            
            # 获取当前步骤记录
            current_step_record = await db.execute(
                select(WorkflowStepRecord)
                .where(WorkflowStepRecord.workflow_id == workflow_id)
                .where(WorkflowStepRecord.step == workflow.current_step)
                .where(WorkflowStepRecord.status == WorkflowStatus.IN_PROGRESS)
            )
            current_step_record = current_step_record.scalar_one_or_none()
            
            if current_step_record:
                # 更新当前步骤记录
                current_step_record.status = status
                current_step_record.end_time = datetime.utcnow()
                if current_step_record.start_time:
                    current_step_record.duration = int((current_step_record.end_time - current_step_record.start_time).total_seconds())
                if result:
                    current_step_record.result = result
                
                # 更新执行日志
                if workflow.execution_log:
                    workflow.execution_log.append({
                        "step": workflow.current_step.value,
                        "status": status.value,
                        "time": datetime.utcnow().isoformat(),
                        "result": result
                    })
                else:
                    workflow.execution_log = [{
                        "step": workflow.current_step.value,
                        "status": status.value,
                        "time": datetime.utcnow().isoformat(),
                        "result": result
                    }]
            
            # 更新工作流状态和进度
            if status in [WorkflowStatus.COMPLETED, WorkflowStatus.REJECTED]:
                # 计算进度
                total_steps = len(WorkflowStep.__members__)
                completed_steps = len(
                    await (await db.execute(
                        select(WorkflowStepRecord)
                        .where(WorkflowStepRecord.workflow_id == workflow_id)
                        .where(WorkflowStepRecord.status == WorkflowStatus.COMPLETED)
                    )).scalars().all()
                ) + 1  # 加上当前步骤
                workflow.progress = int((completed_steps / total_steps) * 100)
                
                # 更新当前步骤
                if status == WorkflowStatus.COMPLETED:
                    # 找到下一个步骤
                    steps = list(WorkflowStep.__members__.values())
                    current_index = steps.index(workflow.current_step)
                    if current_index < len(steps) - 1:
                        next_step = steps[current_index + 1]
                        workflow.current_step = next_step
                        workflow.status = WorkflowStatus.IN_PROGRESS
                        
                        # 创建下一个步骤记录
                        next_step_record = WorkflowStepRecord(
                            workflow_id=workflow.id,
                            step=next_step,
                            status=WorkflowStatus.IN_PROGRESS,
                            start_time=datetime.utcnow(),
                            result={}
                        )
                        db.add(next_step_record)
                    else:
                        # 工作流完成
                        workflow.status = WorkflowStatus.COMPLETED
                        workflow.progress = 100
                elif status == WorkflowStatus.REJECTED:
                    # 工作流失败
                    workflow.status = WorkflowStatus.FAILED
                    workflow.progress = 0
            
            await db.commit()
            await db.refresh(workflow)
            
            return {
                "success": True,
                "message": "工作流步骤更新成功",
                "workflow": {
                    "id": workflow.id,
                    "name": workflow.name,
                    "current_step": workflow.current_step.value,
                    "status": workflow.status.value,
                    "progress": workflow.progress
                }
            }
        except Exception as e:
            await db.rollback()
            return {
                "success": False,
                "message": f"更新工作流步骤失败: {str(e)}"
            }
    
    async def get_workflow(self, db: AsyncSession, workflow_id: int) -> Dict[str, Any]:
        """
        获取工作流详情
        
        Args:
            db: 数据库会话
            workflow_id: 工作流ID
            
        Returns:
            Dict: 工作流详情
        """
        try:
            # 获取工作流
            workflow = await db.get(Workflow, workflow_id)
            if not workflow:
                return {
                    "success": False,
                    "message": f"工作流ID {workflow_id} 不存在"
                }
            
            # 获取步骤记录
            step_records_result = await db.execute(
                select(WorkflowStepRecord)
                .where(WorkflowStepRecord.workflow_id == workflow_id)
                .order_by(WorkflowStepRecord.created_at)
            )
            step_records = step_records_result.scalars().all()
            
            # 格式化步骤记录
            formatted_steps = []
            for record in step_records:
                formatted_steps.append({
                    "step": record.step.value,
                    "status": record.status.value,
                    "start_time": record.start_time.isoformat() if record.start_time else None,
                    "end_time": record.end_time.isoformat() if record.end_time else None,
                    "duration": record.duration,
                    "result": record.result,
                    "comments": record.comments
                })
            
            return {
                "success": True,
                "message": "获取工作流详情成功",
                "workflow": {
                    "id": workflow.id,
                    "name": workflow.name,
                    "api_project_id": workflow.api_project_id,
                    "current_step": workflow.current_step.value,
                    "status": workflow.status.value,
                    "progress": workflow.progress,
                    "execution_log": workflow.execution_log,
                    "step_records": formatted_steps,
                    "created_at": workflow.created_at,
                    "updated_at": workflow.updated_at
                }
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"获取工作流详情失败: {str(e)}"
            }
    
    async def get_workflow_list(self, db: AsyncSession, project_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> Dict[str, Any]:
        """
        获取工作流列表
        
        Args:
            db: 数据库会话
            project_id: API项目ID，可选
            skip: 跳过的记录数
            limit: 返回的记录数
            
        Returns:
            Dict: 工作流列表
        """
        try:
            from sqlalchemy import select
            
            query = select(Workflow)
            if project_id:
                query = query.where(Workflow.api_project_id == project_id)
            
            result = await db.execute(
                query.order_by(Workflow.created_at.desc()).offset(skip).limit(limit)
            )
            workflows = result.scalars().all()
            
            # 格式化工作流列表
            formatted_workflows = []
            for workflow in workflows:
                formatted_workflows.append({
                    "id": workflow.id,
                    "name": workflow.name,
                    "api_project_id": workflow.api_project_id,
                    "current_step": workflow.current_step.value,
                    "status": workflow.status.value,
                    "progress": workflow.progress,
                    "created_at": workflow.created_at,
                    "updated_at": workflow.updated_at
                })
            
            # 获取总记录数
            count_result = await db.execute(
                select(func.count(Workflow.id)).where(query.whereclause)
            )
            total_count = count_result.scalar_one()
            
            return {
                "success": True,
                "message": "获取工作流列表成功",
                "workflows": formatted_workflows,
                "total_count": total_count,
                "skip": skip,
                "limit": limit
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"获取工作流列表失败: {str(e)}"
            }
    
    async def get_workflow_metrics(self, db: AsyncSession, project_id: Optional[int] = None) -> Dict[str, Any]:
        """
        获取工作流度量指标
        
        Args:
            db: 数据库会话
            project_id: API项目ID，可选
            
        Returns:
            Dict: 工作流度量指标
        """
        try:
            from sqlalchemy import select, func
            from src.models.api import ApiProject, ApiInterface
            from src.models.test_point import TestPoint
            from src.models.test_case import TestCase
            from src.models.test_script import TestScript
            
            metrics = {
                "api_projects_count": 0,
                "api_interfaces_count": 0,
                "test_points_count": 0,
                "test_cases_count": 0,
                "test_scripts_count": 0,
                "workflows_count": 0,
                "completed_workflows_count": 0,
                "failed_workflows_count": 0,
                "average_completion_time": 0,
                "adoption_rate": {
                    "test_points": 0,
                    "test_cases": 0,
                    "test_scripts": 0
                }
            }
            
            # API项目数量
            api_projects_query = select(func.count(ApiProject.id))
            if project_id:
                api_projects_query = api_projects_query.where(ApiProject.id == project_id)
            api_projects_count = await db.execute(api_projects_query)
            metrics["api_projects_count"] = api_projects_count.scalar_one()
            
            # API接口数量
            api_interfaces_query = select(func.count(ApiInterface.id))
            if project_id:
                api_interfaces_query = api_interfaces_query.where(ApiInterface.api_project_id == project_id)
            api_interfaces_count = await db.execute(api_interfaces_query)
            metrics["api_interfaces_count"] = api_interfaces_count.scalar_one()
            
            # 测试点数量
            test_points_query = select(func.count(TestPoint.id))
            if project_id:
                test_points_query = test_points_query.where(TestPoint.api_project_id == project_id)
            test_points_count = await db.execute(test_points_query)
            metrics["test_points_count"] = test_points_count.scalar_one()
            
            # 测试用例数量
            test_cases_query = select(func.count(TestCase.id))
            if project_id:
                from sqlalchemy import join
                test_cases_query = test_cases_query.join(TestPoint).where(TestPoint.api_project_id == project_id)
            test_cases_count = await db.execute(test_cases_query)
            metrics["test_cases_count"] = test_cases_count.scalar_one()
            
            # 测试脚本数量
            test_scripts_query = select(func.count(TestScript.id))
            if project_id:
                from sqlalchemy import join
                test_scripts_query = test_scripts_query.join(TestCase).join(TestPoint).where(TestPoint.api_project_id == project_id)
            test_scripts_count = await db.execute(test_scripts_query)
            metrics["test_scripts_count"] = test_scripts_count.scalar_one()
            
            # 工作流数量
            workflows_query = select(func.count(Workflow.id))
            if project_id:
                workflows_query = workflows_query.where(Workflow.api_project_id == project_id)
            workflows_count = await db.execute(workflows_query)
            metrics["workflows_count"] = workflows_count.scalar_one()
            
            # 已完成工作流数量
            completed_workflows_query = select(func.count(Workflow.id))
            completed_workflows_query = completed_workflows_query.where(Workflow.status == WorkflowStatus.COMPLETED)
            if project_id:
                completed_workflows_query = completed_workflows_query.where(Workflow.api_project_id == project_id)
            completed_workflows_count = await db.execute(completed_workflows_query)
            metrics["completed_workflows_count"] = completed_workflows_count.scalar_one()
            
            # 失败工作流数量
            failed_workflows_query = select(func.count(Workflow.id))
            failed_workflows_query = failed_workflows_query.where(Workflow.status == WorkflowStatus.FAILED)
            if project_id:
                failed_workflows_query = failed_workflows_query.where(Workflow.api_project_id == project_id)
            failed_workflows_count = await db.execute(failed_workflows_query)
            metrics["failed_workflows_count"] = failed_workflows_count.scalar_one()
            
            # 计算采纳率
            # 测试点采纳率 = 通过评审的测试点数量 / 总测试点数量
            approved_test_points_query = select(func.count(TestPoint.id))
            approved_test_points_query = approved_test_points_query.where(TestPoint.status == TestPointStatus.APPROVED)
            if project_id:
                approved_test_points_query = approved_test_points_query.where(TestPoint.api_project_id == project_id)
            approved_test_points_count = await db.execute(approved_test_points_query)
            approved_test_points_count = approved_test_points_count.scalar_one()
            
            if metrics["test_points_count"] > 0:
                metrics["adoption_rate"]["test_points"] = round((approved_test_points_count / metrics["test_points_count"]) * 100, 2)
            
            # 测试用例采纳率 = 通过评审的测试用例数量 / 总测试用例数量
            approved_test_cases_query = select(func.count(TestCase.id))
            approved_test_cases_query = approved_test_cases_query.where(TestCase.status == TestCaseStatus.APPROVED)
            if project_id:
                approved_test_cases_query = approved_test_cases_query.join(TestPoint).where(TestPoint.api_project_id == project_id)
            approved_test_cases_count = await db.execute(approved_test_cases_query)
            approved_test_cases_count = approved_test_cases_count.scalar_one()
            
            if metrics["test_cases_count"] > 0:
                metrics["adoption_rate"]["test_cases"] = round((approved_test_cases_count / metrics["test_cases_count"]) * 100, 2)
            
            # 测试脚本采纳率 = 通过评审的测试脚本数量 / 总测试脚本数量
            approved_test_scripts_query = select(func.count(TestScript.id))
            approved_test_scripts_query = approved_test_scripts_query.where(TestScript.status == TestScriptStatus.APPROVED)
            if project_id:
                approved_test_scripts_query = approved_test_scripts_query.join(TestCase).join(TestPoint).where(TestPoint.api_project_id == project_id)
            approved_test_scripts_count = await db.execute(approved_test_scripts_query)
            approved_test_scripts_count = approved_test_scripts_count.scalar_one()
            
            if metrics["test_scripts_count"] > 0:
                metrics["adoption_rate"]["test_scripts"] = round((approved_test_scripts_count / metrics["test_scripts_count"]) * 100, 2)
            
            return {
                "success": True,
                "message": "获取工作流度量指标成功",
                "metrics": metrics
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"获取工作流度量指标失败: {str(e)}"
            }
