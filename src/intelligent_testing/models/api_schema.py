"""
API模式模型
提供细粒度的API模式分析和建模能力
"""

from typing import Dict, List, Any, Optional, Set, Union
from enum import Enum
from dataclasses import dataclass, field
from pydantic import BaseModel, Field
from datetime import datetime


class SchemaType(str, Enum):
    """Schema类型枚举"""
    STRING = "string"
    INTEGER = "integer"
    NUMBER = "number"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"
    NULL = "null"
    ANY = "any"


class ValidationRule(str, Enum):
    """验证规则枚举"""
    REQUIRED = "required"
    MIN_LENGTH = "minLength"
    MAX_LENGTH = "maxLength"
    PATTERN = "pattern"
    MINIMUM = "minimum"
    MAXIMUM = "maximum"
    ENUM = "enum"
    FORMAT = "format"
    ITEMS = "items"
    PROPERTIES = "properties"
    ADDITIONAL_PROPERTIES = "additionalProperties"


@dataclass
class SchemaValidation:
    """Schema验证规则"""

    rule_type: ValidationRule
    value: Any
    message: Optional[str] = None
    severity: str = "error"  # error, warning, info

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "rule_type": self.rule_type.value,
            "value": self.value,
            "message": self.message,
            "severity": self.severity
        }


@dataclass
class SchemaProperty:
    """Schema属性定义"""

    name: str
    schema_type: SchemaType
    description: Optional[str] = None
    default_value: Optional[Any] = None
    is_required: bool = False
    validations: List[SchemaValidation] = field(default_factory=list)
    example_values: List[Any] = field(default_factory=list)

    # 嵌套属性
    properties: Dict[str, "SchemaProperty"] = field(default_factory=dict)
    item_schema: Optional["SchemaProperty"] = None

    # 元数据
    source: str = "openapi"  # openapi, inference, user_defined
    confidence: float = 1.0  # 置信度 0-1

    def get_all_validation_rules(self) -> List[SchemaValidation]:
        """获取所有验证规则"""
        rules = self.validations.copy()

        # 递归获取嵌套属性的规则
        for prop in self.properties.values():
            rules.extend(prop.get_all_validation_rules())

        if self.item_schema:
            rules.extend(self.item_schema.get_all_validation_rules())

        return rules

    def get_boundary_values(self) -> Dict[str, Any]:
        """获取边界值"""
        boundaries = {}

        for validation in self.validations:
            if validation.rule_type == ValidationRule.MINIMUM:
                boundaries["minimum"] = validation.value
            elif validation.rule_type == ValidationRule.MAXIMUM:
                boundaries["maximum"] = validation.value
            elif validation.rule_type == ValidationRule.MIN_LENGTH:
                boundaries["min_length"] = validation.value
            elif validation.rule_type == ValidationRule.MAX_LENGTH:
                boundaries["max_length"] = validation.value

        return boundaries

    def generate_test_values(self, count: int = 5) -> List[Any]:
        """生成测试值"""
        values = []

        # 如果有示例值，优先使用
        if self.example_values:
            values.extend(self.example_values[:count])

        # 根据类型生成测试值
        if self.schema_type == SchemaType.STRING:
            values.extend(self._generate_string_values(count))
        elif self.schema_type == SchemaType.INTEGER:
            values.extend(self._generate_integer_values(count))
        elif self.schema_type == SchemaType.NUMBER:
            values.extend(self._generate_number_values(count))
        elif self.schema_type == SchemaType.BOOLEAN:
            values.extend([True, False])
        elif self.schema_type == SchemaType.ARRAY:
            values.extend(self._generate_array_values(count))

        return values[:count]

    def _generate_string_values(self, count: int) -> List[str]:
        """生成字符串测试值"""
        values = []

        # 边界值
        boundaries = self.get_boundary_values()

        # 正常值
        values.append("test")
        values.append("example")

        # 边界值
        if "min_length" in boundaries:
            values.append("a" * boundaries["min_length"])
        if "max_length" in boundaries:
            values.append("a" * min(boundaries["max_length"], 1000))

        # 特殊字符
        values.append("")
        values.append("null")
        values.append("undefined")

        return values[:count]

    def _generate_integer_values(self, count: int) -> List[int]:
        """生成整数测试值"""
        values = []
        boundaries = self.get_boundary_values()

        # 边界值
        if "minimum" in boundaries:
            values.append(boundaries["minimum"])
            values.append(boundaries["minimum"] - 1)  # 边界外

        if "maximum" in boundaries:
            values.append(boundaries["maximum"])
            values.append(boundaries["maximum"] + 1)  # 边界外

        # 正常值
        values.append(0)
        values.append(1)
        values.append(-1)
        values.append(100)

        return values[:count]

    def _generate_number_values(self, count: int) -> List[Union[int, float]]:
        """生成数字测试值"""
        values = []
        boundaries = self.get_boundary_values()

        # 边界值
        if "minimum" in boundaries:
            values.append(float(boundaries["minimum"]))
            values.append(float(boundaries["minimum"]) - 0.1)

        if "maximum" in boundaries:
            values.append(float(boundaries["maximum"]))
            values.append(float(boundaries["maximum"]) + 0.1)

        # 特殊值
        values.append(0.0)
        values.append(-0.0)
        values.append(3.14159)
        values.append(-1.5)

        return values[:count]

    def _generate_array_values(self, count: int) -> List[List[Any]]:
        """生成数组测试值"""
        values = []

        # 空数组
        values.append([])

        # 单元素数组
        if self.item_schema:
            item_values = self.item_schema.generate_test_values(3)
            for val in item_values:
                values.append([val])

        # 多元素数组
        values.append([1, 2, 3])
        values.append(["a", "b", "c"])

        return values[:count]


@dataclass
class ApiSchema:
    """API模式定义"""

    id: str
    name: str
    description: Optional[str] = None

    # Schema定义
    root_property: Optional[SchemaProperty] = None
    properties: Dict[str, SchemaProperty] = field(default_factory=dict)

    # 源信息
    source_type: str = "openapi"  # openapi, json_schema, inferred
    source_reference: Optional[str] = None

    # 版本控制
    version: str = "1.0.0"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    # 元数据
    metadata: Dict[str, Any] = field(default_factory=dict)

    def find_property(self, property_path: str) -> Optional[SchemaProperty]:
        """查找属性"""
        if not property_path:
            return self.root_property

        path_parts = property_path.split(".")
        current = self.root_property

        for part in path_parts:
            if not current or part not in current.properties:
                return None
            current = current.properties[part]

        return current

    def get_all_properties(self) -> List[SchemaProperty]:
        """获取所有属性"""
        properties = []

        def collect_properties(prop: SchemaProperty):
            properties.append(prop)
            for child_prop in prop.properties.values():
                collect_properties(child_prop)
            if prop.item_schema:
                collect_properties(prop.item_schema)

        if self.root_property:
            collect_properties(self.root_property)

        return properties

    def get_validation_rules(self) -> Dict[str, List[SchemaValidation]]:
        """获取所有验证规则"""
        rules = {}

        for prop in self.get_all_properties():
            if prop.validations:
                rules[prop.name] = prop.validations

        return rules

    def generate_test_data_template(self) -> Dict[str, Any]:
        """生成测试数据模板"""
        if not self.root_property:
            return {}

        return self._generate_property_template(self.root_property)

    def _generate_property_template(self, prop: SchemaProperty) -> Any:
        """生成属性模板"""
        if prop.schema_type == SchemaType.OBJECT:
            template = {}
            for name, child_prop in prop.properties.items():
                template[name] = self._generate_property_template(child_prop)
            return template

        elif prop.schema_type == SchemaType.ARRAY:
            if prop.item_schema:
                return [self._generate_property_template(prop.item_schema)]
            else:
                return []

        else:
            # 返回默认值或示例值
            if prop.default_value is not None:
                return prop.default_value
            elif prop.example_values:
                return prop.example_values[0]
            else:
                # 根据类型返回默认值
                defaults = {
                    SchemaType.STRING: "string_value",
                    SchemaType.INTEGER: 0,
                    SchemaType.NUMBER: 0.0,
                    SchemaType.BOOLEAN: True,
                    SchemaType.NULL: None,
                    SchemaType.ANY: "any_value"
                }
                return defaults.get(prop.schema_type, None)

    def analyze_complexity(self) -> Dict[str, Any]:
        """分析模式复杂度"""
        all_props = self.get_all_properties()

        # 计算各种指标
        total_props = len(all_props)
        nested_levels = self._calculate_nested_levels()
        validation_rules = sum(len(prop.validations) for prop in all_props)

        # 计算复杂度分数
        complexity_score = (
                                   total_props * 0.3 +
                                   nested_levels * 0.3 +
                                   validation_rules * 0.4
                           ) / 10  # 归一化到0-1

        return {
            "total_properties": total_props,
            "nested_levels": nested_levels,
            "validation_rules": validation_rules,
            "complexity_score": min(complexity_score, 1.0),
            "complexity_level": self._get_complexity_level(complexity_score)
        }

    def _calculate_nested_levels(self) -> int:
        """计算嵌套层数"""

        def max_depth(prop: SchemaProperty, current_depth: int) -> int:
            max_child_depth = current_depth

            # 检查子属性
            for child_prop in prop.properties.values():
                child_depth = max_depth(child_prop, current_depth + 1)
                max_child_depth = max(max_child_depth, child_depth)

            # 检查数组元素
            if prop.item_schema:
                child_depth = max_depth(prop.item_schema, current_depth + 1)
                max_child_depth = max(max_child_depth, child_depth)

            return max_child_depth

        if self.root_property:
            return max_depth(self.root_property, 1)
        return 0

    def _get_complexity_level(self, score: float) -> str:
        """获取复杂度等级"""
        if score < 0.3:
            return "low"
        elif score < 0.6:
            return "medium"
        else:
            return "high"