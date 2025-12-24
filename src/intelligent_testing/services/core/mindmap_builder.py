"""
MVP核心：思维导图构建器
从API规范构建测试思维导图
"""

import uuid
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from intelligent_testing.models.mind_map import MindMap, MindMapNode, NodeType
from intelligent_testing.models.specification import APISpecification


@dataclass
class MindmapGenerationConfig:
    """思维导图生成配置"""
    include_categories: List[str] = None  # 包含的测试类别
    max_depth: int = 4  # 最大深度
    enable_ai_assistance: bool = True  # 是否启用AI辅助


class MindmapBuilder:
    """思维导图构建器（MVP版本）"""

    def __init__(self):
        self.default_categories = [
            "功能测试",
            "安全测试",
            "边界值测试",
            "异常场景测试",
            "性能测试",
            "兼容性测试"
        ]

    def build_from_specification(
            self,
            api_spec: APISpecification,
            config: Dict[str, Any] = None
    ) -> MindMap:
        """从API规范构建思维导图"""

        # 解析配置
        mindmap_config = self._parse_config(config)

        # 创建根节点
        api_name = api_spec.info.title if hasattr(api_spec, 'info') else "API"
        root_node = MindMapNode(
            id=str(uuid.uuid4()),
            name=f"API测试思维导图 - {api_name}",
            node_type=NodeType.ROOT,
            level=0,
            description=f"基于{api_name}生成的测试思维导图"
        )

        # 添加主要测试类别
        for category in self._get_categories_to_include(mindmap_config):
            category_node = self._create_category_node(category, api_spec)
            root_node.add_child(category_node)

            # 为每个类别添加测试点
            test_points = self._generate_test_points_for_category(category, api_spec)
            for test_point in test_points:
                test_point_node = self._create_test_point_node(test_point)
                category_node.add_child(test_point_node)

        # 创建思维导图
        mind_map = MindMap(
            id=str(uuid.uuid4()),
            name=f"测试思维导图_{api_name}",
            api_spec_id=getattr(api_spec, 'id', ''),
            root_node=root_node
        )

        return mind_map

    def _parse_config(self, config: Dict[str, Any]) -> MindmapGenerationConfig:
        """解析配置"""
        if not config:
            return MindmapGenerationConfig()

        return MindmapGenerationConfig(
            include_categories=config.get('include_categories'),
            max_depth=config.get('max_depth', 4),
            enable_ai_assistance=config.get('enable_ai_assistance', True)
        )

    def _get_categories_to_include(self, config: MindmapGenerationConfig) -> List[str]:
        """获取要包含的类别"""
        if config.include_categories:
            return [cat for cat in config.include_categories if cat in self.default_categories]
        return self.default_categories

    def _create_category_node(self, category: str, api_spec: APISpecification) -> MindMapNode:
        """创建分类节点"""
        descriptions = {
            "功能测试": "验证API功能是否符合需求规格",
            "安全测试": "验证API安全性和访问控制",
            "边界值测试": "验证边界条件下的API行为",
            "异常场景测试": "验证异常输入和错误处理",
            "性能测试": "验证API性能指标",
            "兼容性测试": "验证API兼容性"
        }

        return MindMapNode(
            id=str(uuid.uuid4()),
            name=category,
            node_type=NodeType.CATEGORY,
            level=1,
            description=descriptions.get(category, "")
        )

    def _generate_test_points_for_category(
            self,
            category: str,
            api_spec: APISpecification
    ) -> List[Dict[str, Any]]:
        """为分类生成测试点"""
        if category == "功能测试":
            return self._generate_functional_test_points(api_spec)
        elif category == "安全测试":
            return self._generate_security_test_points(api_spec)
        elif category == "边界值测试":
            return self._generate_boundary_test_points(api_spec)
        elif category == "异常场景测试":
            return self._generate_negative_test_points(api_spec)
        elif category == "性能测试":
            return self._generate_performance_test_points(api_spec)
        elif category == "兼容性测试":
            return self._generate_compatibility_test_points(api_spec)
        else:
            return []

    def _generate_functional_test_points(self, api_spec: APISpecification) -> List[Dict[str, Any]]:
        """生成功能测试点"""
        test_points = []

        if hasattr(api_spec, 'paths') and api_spec.paths:
            for path, methods in api_spec.paths.items():
                for method in methods.keys():
                    test_points.append({
                        "id": str(uuid.uuid4()),
                        "name": f"{method.upper()} {path} - 正常功能",
                        "description": f"验证{method.upper()} {path}接口的正常功能",
                        "priority": 1,
                        "metadata": {"path": path, "method": method}
                    })

        return test_points[:10]  # MVP阶段限制数量

    def _generate_security_test_points(self, api_spec: APISpecification) -> List[Dict[str, Any]]:
        """生成安全测试点"""
        test_points = []

        # 基本安全测试点
        security_points = [
            {
                "name": "认证测试",
                "description": "验证API认证机制",
                "priority": 1
            },
            {
                "name": "授权测试",
                "description": "验证API授权和权限控制",
                "priority": 1
            },
            {
                "name": "输入验证测试",
                "description": "验证输入数据的安全验证",
                "priority": 2
            }
        ]

        for point in security_points:
            test_points.append({
                "id": str(uuid.uuid4()),
                "name": point["name"],
                "description": point["description"],
                "priority": point["priority"]
            })

        return test_points

    def _generate_boundary_test_points(self, api_spec: APISpecification) -> List[Dict[str, Any]]:
        """生成边界值测试点"""
        test_points = []

        boundary_points = [
            {
                "name": "数值边界测试",
                "description": "测试数值参数的边界值",
                "priority": 2
            },
            {
                "name": "字符串长度边界测试",
                "description": "测试字符串参数的边界长度",
                "priority": 2
            },
            {
                "name": "数组边界测试",
                "description": "测试数组参数的边界情况",
                "priority": 3
            }
        ]

        for point in boundary_points:
            test_points.append({
                "id": str(uuid.uuid4()),
                "name": point["name"],
                "description": point["description"],
                "priority": point["priority"]
            })

        return test_points

    def _generate_negative_test_points(self, api_spec: APISpecification) -> List[Dict[str, Any]]:
        """生成异常场景测试点"""
        test_points = []

        negative_points = [
            {
                "name": "无效输入测试",
                "description": "测试无效的输入数据",
                "priority": 2
            },
            {
                "name": "错误处理测试",
                "description": "测试API的错误处理机制",
                "priority": 2
            },
            {
                "name": "异常流程测试",
                "description": "测试异常的业务流程",
                "priority": 3
            }
        ]

        for point in negative_points:
            test_points.append({
                "id": str(uuid.uuid4()),
                "name": point["name"],
                "description": point["description"],
                "priority": point["priority"]
            })

        return test_points

    def _generate_performance_test_points(self, api_spec: APISpecification) -> List[Dict[str, Any]]:
        """生成性能测试点"""
        test_points = []

        performance_points = [
            {
                "name": "响应时间测试",
                "description": "测试API响应时间",
                "priority": 3
            },
            {
                "name": "并发测试",
                "description": "测试API的并发处理能力",
                "priority": 3
            }
        ]

        for point in performance_points:
            test_points.append({
                "id": str(uuid.uuid4()),
                "name": point["name"],
                "description": point["description"],
                "priority": point["priority"]
            })

        return test_points

    def _generate_compatibility_test_points(self, api_spec: APISpecification) -> List[Dict[str, Any]]:
        """生成兼容性测试点"""
        test_points = []

        compatibility_points = [
            {
                "name": "版本兼容性测试",
                "description": "测试不同版本的兼容性",
                "priority": 3
            },
            {
                "name": "数据格式兼容性测试",
                "description": "测试不同数据格式的兼容性",
                "priority": 3
            }
        ]

        for point in compatibility_points:
            test_points.append({
                "id": str(uuid.uuid4()),
                "name": point["name"],
                "description": point["description"],
                "priority": point["priority"]
            })

        return test_points

    def _create_test_point_node(self, test_point: Dict[str, Any]) -> MindMapNode:
        """创建测试点节点"""
        return MindMapNode(
            id=test_point["id"],
            name=test_point["name"],
            node_type=NodeType.TEST_POINT,
            level=2,
            description=test_point["description"],
            priority=test_point["priority"],
            metadata=test_point.get("metadata", {})
        )