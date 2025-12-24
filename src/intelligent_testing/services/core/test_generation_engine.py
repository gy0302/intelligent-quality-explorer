"""
MVP核心：测试生成引擎
协调整个测试生成流程的基础版本
"""

import uuid
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

from config.settings import settings
from intelligent_testing.models.specification import APISpecification
from intelligent_testing.models.mind_map import MindMap
from intelligent_testing.models.test_case import TestCase, TestCaseStatus
from intelligent_testing.models.test_script import TestScript
from intelligent_testing.services.core.mindmap_builder import MindmapBuilder
from intelligent_testing.services.quality.test_case_validator import TestCaseValidator
from intelligent_testing.services.quality.review_analyzer import ReviewAnalyzer
from intelligent_testing.services.export.excel_generator import ExcelGenerator
from intelligent_testing.services.export.csv_generator import CSVGenerator


@dataclass
class MVPGenerationResult:
    """MVP生成结果"""

    success: bool
    workflow_id: str
    mindmap: Optional[MindMap] = None
    test_cases: List[TestCase] = field(default_factory=list)
    review_results: List[Dict[str, Any]] = field(default_factory=list)
    export_files: List[Dict[str, Any]] = field(default_factory=list)
    error_message: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


class MVPTestGenerationEngine:
    """MVP测试生成引擎（简化版本）"""

    def __init__(self):
        self.workflow_id = str(uuid.uuid4())
        self.mindmap_builder = MindmapBuilder()
        self.test_case_validator = TestCaseValidator()
        self.review_analyzer = ReviewAnalyzer()
        self.excel_generator = ExcelGenerator()
        self.csv_generator = CSVGenerator()
        self.log = []

    def generate_from_specification(
            self,
            api_spec: APISpecification,
            config: Dict[str, Any] = None
    ) -> MVPGenerationResult:
        """从API规范生成测试用例（MVP核心流程）"""

        try:
            self._log("开始MVP测试生成流程")

            # 1. 生成思维导图
            self._log("步骤1: 生成思维导图")
            mindmap = self._generate_mindmap(api_spec, config)

            # 2. AI评审思维导图
            self._log("步骤2: AI评审思维导图")
            ai_review_mindmap = self._review_mindmap(mindmap)

            # 3. 生成测试用例
            self._log("步骤3: 生成测试用例")
            test_cases = self._generate_test_cases(mindmap, api_spec, config)

            # 4. AI评审测试用例
            self._log("步骤4: AI评审测试用例")
            ai_review_test_cases = self._review_test_cases(test_cases)

            # 5. 验证测试用例
            self._log("步骤5: 验证测试用例")
            validation_results = self._validate_test_cases(test_cases)

            # 6. 导出测试用例
            self._log("步骤6: 导出测试用例")
            export_files = self._export_test_cases(test_cases, config)

            return MVPGenerationResult(
                success=True,
                workflow_id=self.workflow_id,
                mindmap=mindmap,
                test_cases=test_cases,
                review_results=[
                    ai_review_mindmap,
                    ai_review_test_cases,
                    validation_results
                ],
                export_files=export_files
            )

        except Exception as e:
            self._log(f"生成流程失败: {str(e)}", "ERROR")
            return MVPGenerationResult(
                success=False,
                workflow_id=self.workflow_id,
                error_message=str(e)
            )

    def _generate_mindmap(
            self,
            api_spec: APISpecification,
            config: Dict[str, Any]
    ) -> MindMap:
        """生成思维导图"""
        try:
            mindmap = self.mindmap_builder.build_from_specification(api_spec, config)
            self._log(f"思维导图生成成功: {mindmap.name}")
            return mindmap
        except Exception as e:
            self._log(f"思维导图生成失败: {str(e)}", "ERROR")
            raise

    def _review_mindmap(self, mindmap: MindMap) -> Dict[str, Any]:
        """评审思维导图"""
        try:
            review_result = self.review_analyzer.analyze_mindmap(mindmap)
            self._log(f"思维导图评审完成: 得分{review_result.get('score', 0)}")
            return review_result
        except Exception as e:
            self._log(f"思维导图评审失败: {str(e)}", "WARNING")
            return {"error": str(e), "score": 0.5}

    def _generate_test_cases(
            self,
            mindmap: MindMap,
            api_spec: APISpecification,
            config: Dict[str, Any]
    ) -> List[TestCase]:
        """生成测试用例（MVP简化版）"""
        test_cases = []

        # 从思维导图节点生成测试用例
        for node in mindmap.flatten_nodes():
            if node.level >= 2:  # 只处理测试点级别的节点
                test_case = self._create_test_case_from_node(node, api_spec)
                test_cases.append(test_case)

        self._log(f"生成了 {len(test_cases)} 个测试用例")
        return test_cases

    def _create_test_case_from_node(
            self,
            node: Any,
            api_spec: APISpecification
    ) -> TestCase:
        """从思维导图节点创建测试用例"""

        # 提取API端点信息（简化版）
        api_endpoint = self._extract_endpoint_from_node(node, api_spec)

        return TestCase(
            id=f"TC-{uuid.uuid4().hex[:8]}",
            name=f"测试: {node.name}",
            description=node.description or f"基于节点'{node.name}'生成的测试用例",
            priority=self._calculate_priority(node),
            category=self._determine_category(node),
            api_endpoint=api_endpoint,
            test_steps=self._generate_test_steps(node, api_endpoint),
            expected_results=self._generate_expected_results(node),
            test_data=self._generate_test_data(node),
            status=TestCaseStatus.DRAFT,
            created_by="MVP_Engine"
        )

    def _extract_endpoint_from_node(
            self,
            node: Any,
            api_spec: APISpecification
    ) -> Optional[str]:
        """从节点提取API端点（简化版）"""
        # MVP阶段：简单匹配节点名中的路径关键词
        if hasattr(api_spec, 'paths') and api_spec.paths:
            for path in api_spec.paths.keys():
                if node.name and path.lower() in node.name.lower():
                    return f"GET {path}"  # 简化：默认GET方法

        return None

    def _calculate_priority(self, node: Any) -> int:
        """计算测试用例优先级"""
        # 根据节点层级和类型确定优先级
        if node.level <= 1:
            return 1  # 高优先级
        elif node.level <= 3:
            return 3  # 中优先级
        else:
            return 5  # 低优先级

    def _determine_category(self, node: Any) -> str:
        """确定测试用例分类"""
        node_name = node.name.lower() if node.name else ""

        if "安全" in node_name or "auth" in node_name:
            return "security"
        elif "边界" in node_name or "boundary" in node_name:
            return "boundary"
        elif "异常" in node_name or "error" in node_name:
            return "negative"
        else:
            return "functional"

    def _generate_test_steps(self, node: Any, api_endpoint: Optional[str]) -> List[str]:
        """生成测试步骤"""
        steps = []

        if api_endpoint:
            steps.append(f"准备测试数据")
            steps.append(f"调用API: {api_endpoint}")
        else:
            steps.append(f"执行测试: {node.name}")

        steps.append(f"验证响应结果")
        steps.append(f"检查业务逻辑")

        return steps

    def _generate_expected_results(self, node: Any) -> List[str]:
        """生成预期结果"""
        results = []

        if "成功" in node.name or "正常" in node.name:
            results.append("操作成功完成")
            results.append("返回正确的状态码")
            results.append("响应数据符合预期")
        elif "失败" in node.name or "错误" in node.name:
            results.append("返回适当的错误码")
            results.append("错误信息清晰明确")

        return results

    def _generate_test_data(self, node: Any) -> Dict[str, Any]:
        """生成测试数据"""
        return {
            "scenario": node.name,
            "description": node.description or "",
            "node_id": node.id
        }

    def _review_test_cases(self, test_cases: List[TestCase]) -> Dict[str, Any]:
        """评审测试用例"""
        try:
            review_results = []
            for test_case in test_cases:
                review = self.review_analyzer.analyze_test_case(test_case)
                review_results.append(review)

            avg_score = sum(r.get('score', 0) for r in review_results) / len(review_results)

            self._log(f"测试用例评审完成: 平均得分{avg_score:.2f}")

            return {
                "total_reviewed": len(review_results),
                "average_score": avg_score,
                "review_details": review_results[:10]  # 只返回前10个详情
            }

        except Exception as e:
            self._log(f"测试用例评审失败: {str(e)}", "WARNING")
            return {"error": str(e)}

    def _validate_test_cases(self, test_cases: List[TestCase]) -> Dict[str, Any]:
        """验证测试用例"""
        try:
            validation_results = []
            for test_case in test_cases:
                validation = self.test_case_validator.validate(test_case)
                validation_results.append(validation)

            valid_count = sum(1 for r in validation_results if r.get('is_valid', False))
            valid_ratio = valid_count / len(validation_results) if validation_results else 0

            self._log(f"测试用例验证完成: 有效比例{valid_ratio:.1%}")

            return {
                "total_validated": len(validation_results),
                "valid_count": valid_count,
                "valid_ratio": valid_ratio,
                "validation_details": validation_results[:10]
            }

        except Exception as e:
            self._log(f"测试用例验证失败: {str(e)}", "WARNING")
            return {"error": str(e)}

    def _export_test_cases(
            self,
            test_cases: List[TestCase],
            config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """导出测试用例"""
        export_files = []

        try:
            # 导出Excel
            output_dir = settings.OUTPUT_DIR / "test_cases" / "excel"
            output_dir.mkdir(parents=True, exist_ok=True)

            excel_file = output_dir / f"test_cases_{self.workflow_id[:8]}.xlsx"
            self.excel_generator.generate_test_case_sheet(test_cases, excel_file)

            export_files.append({
                "type": "excel",
                "path": str(excel_file),
                "count": len(test_cases)
            })

            self._log(f"Excel导出成功: {excel_file}")

            # 导出CSV
            csv_dir = settings.OUTPUT_DIR / "test_cases" / "csv"
            csv_dir.mkdir(parents=True, exist_ok=True)

            csv_file = csv_dir / f"test_cases_{self.workflow_id[:8]}.csv"
            self.csv_generator.generate_test_case_csv(test_cases, csv_file)

            export_files.append({
                "type": "csv",
                "path": str(csv_file),
                "count": len(test_cases)
            })

            self._log(f"CSV导出成功: {csv_file}")

        except Exception as e:
            self._log(f"测试用例导出失败: {str(e)}", "ERROR")
            # 不抛出异常，继续流程

        return export_files

    def _log(self, message: str, level: str = "INFO"):
        """记录日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        self.log.append(log_entry)

        if level == "ERROR":
            print(f"❌ {log_entry}")
        elif level == "WARNING":
            print(f"⚠️ {log_entry}")
        else:
            print(f"ℹ️ {log_entry}")

    def get_execution_log(self) -> List[str]:
        """获取执行日志"""
        return self.log