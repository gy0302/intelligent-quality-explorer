"""
断言智能服务
基于AI和规则的智能断言生成
"""

import asyncio
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

from config.settings import settings
from intelligent_testing.models.test_case import TestCase
from intelligent_testing.models.test_assertion import TestAssertion, AssertionType, AssertionLevel
from application.ports.llm_gateway import LLMGateway, LLMRequest


class AssertionPattern(str, Enum):
    """断言模式枚举"""
    STATUS_CODE = "status_code"
    RESPONSE_BODY = "response_body"
    RESPONSE_HEADER = "response_header"
    RESPONSE_TIME = "response_time"
    ERROR_HANDLING = "error_handling"
    DATA_VALIDATION = "data_validation"
    BUSINESS_RULE = "business_rule"
    SECURITY = "security"
    PERFORMANCE = "performance"


@dataclass
class AssertionContext:
    """断言生成上下文"""

    api_endpoint: str
    http_method: str
    request_data: Dict[str, Any]
    expected_response: Optional[Dict[str, Any]] = None
    response_schema: Optional[Dict[str, Any]] = None
    business_rules: List[Dict[str, Any]] = field(default_factory=list)
    historical_data: Optional[Dict[str, Any]] = None

    @property
    def has_schema(self) -> bool:
        """是否有响应模式"""
        return bool(self.response_schema)

    @property
    def has_business_rules(self) -> bool:
        """是否有业务规则"""
        return len(self.business_rules) > 0


class AssertionIntelligence:
    """断言智能服务"""

    def __init__(self, llm_gateway: Optional[LLMGateway] = None):
        self.llm_gateway = llm_gateway
        self.assertion_patterns = self._load_assertion_patterns()
        self.rule_based_generator = RuleBasedAssertionGenerator()
        self.ai_based_generator = AIBasedAssertionGenerator(llm_gateway)

    def _load_assertion_patterns(self) -> Dict[AssertionPattern, Dict[str, Any]]:
        """加载断言模式"""
        return {
            AssertionPattern.STATUS_CODE: {
                "description": "状态码验证",
                "priority": 1,
                "applicable_methods": ["GET", "POST", "PUT", "DELETE", "PATCH"],
                "template": "验证响应状态码为{expected_code}"
            },
            AssertionPattern.RESPONSE_BODY: {
                "description": "响应体验证",
                "priority": 2,
                "applicable_methods": ["GET", "POST", "PUT", "PATCH"],
                "template": "验证响应体包含预期字段和数据"
            },
            AssertionPattern.ERROR_HANDLING: {
                "description": "错误处理验证",
                "priority": 3,
                "applicable_methods": ["GET", "POST", "PUT", "DELETE", "PATCH"],
                "template": "验证错误场景的处理"
            },
            AssertionPattern.DATA_VALIDATION: {
                "description": "数据验证",
                "priority": 4,
                "applicable_methods": ["POST", "PUT", "PATCH"],
                "template": "验证数据的完整性和正确性"
            },
            AssertionPattern.BUSINESS_RULE: {
                "description": "业务规则验证",
                "priority": 5,
                "applicable_methods": ["POST", "PUT", "PATCH", "DELETE"],
                "template": "验证业务规则的执行"
            },
            AssertionPattern.SECURITY: {
                "description": "安全验证",
                "priority": 6,
                "applicable_methods": ["GET", "POST", "PUT", "DELETE", "PATCH"],
                "template": "验证安全要求和约束"
            },
            AssertionPattern.PERFORMANCE: {
                "description": "性能验证",
                "priority": 7,
                "applicable_methods": ["GET", "POST", "PUT", "DELETE", "PATCH"],
                "template": "验证性能指标"
            }
        }

    async def enhance_test_case(
            self,
            test_case: TestCase,
            api_schema: Any,
            context: Dict[str, Any] = None
    ) -> TestCase:
        """增强测试用例的断言"""

        # 提取断言上下文
        assertion_context = self._extract_assertion_context(test_case, api_schema, context)

        # 确定适用的断言模式
        applicable_patterns = self._get_applicable_patterns(assertion_context)

        # 生成断言
        assertions = []

        # 规则基础的断言
        rule_based_assertions = self.rule_based_generator.generate_assertions(
            assertion_context, applicable_patterns
        )
        assertions.extend(rule_based_assertions)

        # AI基础的断言（如果配置启用）
        if context and context.get("enable_ai_assertions", True):
            ai_assertions = await self.ai_based_generator.generate_assertions(
                assertion_context, applicable_patterns
            )
            assertions.extend(ai_assertions)

        # 去重和排序
        unique_assertions = self._deduplicate_assertions(assertions)
        sorted_assertions = self._sort_assertions(unique_assertions)

        # 添加到测试用例
        test_case.assertions = sorted_assertions

        # 计算断言质量分数
        test_case.assertion_quality_score = self._calculate_assertion_quality(sorted_assertions)

        return test_case

    def _extract_assertion_context(
            self,
            test_case: TestCase,
            api_schema: Any,
            context: Dict[str, Any]
    ) -> AssertionContext:
        """提取断言上下文"""

        # 从测试用例中提取信息
        api_endpoint = test_case.api_endpoint or ""
        http_method = self._extract_http_method(api_endpoint)

        # 提取请求数据
        request_data = test_case.test_data or {}

        # 提取响应模式
        response_schema = self._extract_response_schema(api_endpoint, api_schema)

        # 提取业务规则
        business_rules = self._extract_business_rules(test_case, context)

        return AssertionContext(
            api_endpoint=api_endpoint,
            http_method=http_method,
            request_data=request_data,
            response_schema=response_schema,
            business_rules=business_rules
        )

    def _extract_http_method(self, api_endpoint: str) -> str:
        """从端点提取HTTP方法"""
        if not api_endpoint:
            return "GET"

        # 假设端点格式为 "METHOD /path"
        parts = api_endpoint.split()
        if len(parts) >= 1:
            return parts[0].upper()

        return "GET"

    def _extract_response_schema(self, api_endpoint: str, api_schema: Any) -> Optional[Dict[str, Any]]:
        """提取响应模式"""
        # 这里应该根据端点找到对应的响应模式
        # 简化实现
        if hasattr(api_schema, 'properties'):
            return {
                "type": "object",
                "properties": api_schema.properties
            }
        return None

    def _extract_business_rules(self, test_case: TestCase, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """提取业务规则"""
        business_rules = []

        # 从测试用例描述中提取
        description = test_case.description or ""
        if "业务规则" in description or "business rule" in description.lower():
            business_rules.append({
                "source": "test_case_description",
                "rule": description
            })

        # 从上下文中提取
        if context and "business_rules" in context:
            business_rules.extend(context["business_rules"])

        return business_rules

    def _get_applicable_patterns(self, context: AssertionContext) -> List[AssertionPattern]:
        """获取适用的断言模式"""
        applicable_patterns = []

        for pattern, config in self.assertion_patterns.items():
            # 检查HTTP方法是否适用
            applicable_methods = config.get("applicable_methods", [])
            if context.http_method not in applicable_methods:
                continue

            # 根据上下文决定是否添加
            if self._should_include_pattern(pattern, context):
                applicable_patterns.append(pattern)

        # 按优先级排序
        applicable_patterns.sort(
            key=lambda p: self.assertion_patterns[p].get("priority", 99)
        )

        return applicable_patterns

    def _should_include_pattern(self, pattern: AssertionPattern, context: AssertionContext) -> bool:
        """判断是否应该包含某个模式"""

        if pattern == AssertionPattern.STATUS_CODE:
            # 总是包含状态码验证
            return True

        elif pattern == AssertionPattern.RESPONSE_BODY:
            # 如果有响应模式，则包含响应体验证
            return context.has_schema

        elif pattern == AssertionPattern.ERROR_HANDLING:
            # 对于错误场景测试，包含错误处理验证
            return "error" in (context.request_data.get("scenario", "") or "").lower()

        elif pattern == AssertionPattern.BUSINESS_RULE:
            # 如果有业务规则，则包含业务规则验证
            return context.has_business_rules

        elif pattern == AssertionPattern.SECURITY:
            # 对于安全相关的端点，包含安全验证
            security_keywords = ["auth", "token", "password", "secret", "admin"]
            endpoint_lower = context.api_endpoint.lower()
            return any(keyword in endpoint_lower for keyword in security_keywords)

        elif pattern == AssertionPattern.PERFORMANCE:
            # 对于性能测试，包含性能验证
            return context.request_data.get("performance_test", False)

        return False

    def _deduplicate_assertions(self, assertions: List[TestAssertion]) -> List[TestAssertion]:
        """去重断言"""
        unique_assertions = []
        seen_content = set()

        for assertion in assertions:
            content_key = f"{assertion.assertion_type}:{assertion.expected_value}"
            if content_key not in seen_content:
                seen_content.add(content_key)
                unique_assertions.append(assertion)

        return unique_assertions

    def _sort_assertions(self, assertions: List[TestAssertion]) -> List[TestAssertion]:
        """排序断言"""
        # 按优先级和类型排序
        priority_order = {
            AssertionType.STATUS_CODE: 1,
            AssertionType.RESPONSE_BODY: 2,
            AssertionType.RESPONSE_HEADER: 3,
            AssertionType.RESPONSE_TIME: 4,
            AssertionType.BUSINESS_RULE: 5,
            AssertionType.SECURITY: 6
        }

        return sorted(
            assertions,
            key=lambda a: (
                priority_order.get(a.assertion_type, 99),
                a.priority if hasattr(a, 'priority') else 1
            )
        )

    def _calculate_assertion_quality(self, assertions: List[TestAssertion]) -> float:
        """计算断言质量分数"""
        if not assertions:
            return 0.0

        # 计算各种指标
        total_assertions = len(assertions)
        diverse_types = len(set(a.assertion_type for a in assertions))

        # 计算覆盖率
        type_coverage = diverse_types / len(AssertionType) if AssertionType else 0

        # 计算详细度
        detailed_assertions = sum(
            1 for a in assertions
            if a.description and len(a.description) > 10
        )
        detail_score = detailed_assertions / total_assertions if total_assertions > 0 else 0

        # 综合分数
        quality_score = (
                type_coverage * 0.4 +  # 类型多样性
                detail_score * 0.3 +  # 详细度
                (total_assertions / 10) * 0.3  # 数量适当性（归一化）
        )

        return min(quality_score, 1.0)


class RuleBasedAssertionGenerator:
    """规则基础断言生成器"""

    def generate_assertions(
            self,
            context: AssertionContext,
            patterns: List[AssertionPattern]
    ) -> List[TestAssertion]:
        """基于规则生成断言"""

        assertions = []

        for pattern in patterns:
            pattern_assertions = self._generate_for_pattern(pattern, context)
            assertions.extend(pattern_assertions)

        return assertions

    def _generate_for_pattern(
            self,
            pattern: AssertionPattern,
            context: AssertionContext
    ) -> List[TestAssertion]:
        """为特定模式生成断言"""

        if pattern == AssertionPattern.STATUS_CODE:
            return self._generate_status_code_assertions(context)

        elif pattern == AssertionPattern.RESPONSE_BODY:
            return self._generate_response_body_assertions(context)

        elif pattern == AssertionPattern.ERROR_HANDLING:
            return self._generate_error_handling_assertions(context)

        elif pattern == AssertionPattern.BUSINESS_RULE:
            return self._generate_business_rule_assertions(context)

        elif pattern == AssertionPattern.SECURITY:
            return self._generate_security_assertions(context)

        elif pattern == AssertionPattern.PERFORMANCE:
            return self._generate_performance_assertions(context)

        return []

    def _generate_status_code_assertions(self, context: AssertionContext) -> List[TestAssertion]:
        """生成状态码断言"""
        assertions = []

        # 根据HTTP方法确定预期状态码
        expected_codes = {
            "GET": 200,
            "POST": 201,  # 创建成功
            "PUT": 200,
            "DELETE": 204,  # 无内容
            "PATCH": 200
        }

        expected_code = expected_codes.get(context.http_method, 200)

        # 创建断言
        assertion = TestAssertion(
            id=f"assert_status_{context.http_method}",
            name=f"验证{context.http_method}请求状态码",
            description=f"验证API返回正确的状态码: {expected_code}",
            assertion_type=AssertionType.STATUS_CODE,
            expected_value=expected_code,
            assertion_level=AssertionLevel.REQUIRED,
            priority=1
        )

        assertions.append(assertion)

        # 对于错误场景，添加错误状态码断言
        if "error" in str(context.request_data).lower():
            error_assertion = TestAssertion(
                id=f"assert_error_status_{context.http_method}",
                name=f"验证错误场景状态码",
                description="验证错误场景返回4xx或5xx状态码",
                assertion_type=AssertionType.STATUS_CODE,
                expected_value={"range": "4xx-5xx"},
                assertion_level=AssertionType.OPTIONAL,
                priority=2
            )
            assertions.append(error_assertion)

        return assertions

    def _generate_response_body_assertions(self, context: AssertionContext) -> List[TestAssertion]:
        """生成响应体断言"""
        assertions = []

        if not context.response_schema:
            return assertions

        # 提取模式中的关键字段
        schema_properties = context.response_schema.get("properties", {})

        for field_name, field_schema in list(schema_properties.items())[:5]:  # 限制前5个字段
            field_type = field_schema.get("type", "unknown")

            # 创建字段存在性断言
            existence_assertion = TestAssertion(
                id=f"assert_field_exists_{field_name}",
                name=f"验证响应包含字段: {field_name}",
                description=f"验证响应体包含 {field_name} 字段",
                assertion_type=AssertionType.RESPONSE_BODY,
                expected_value={"field_exists": field_name},
                assertion_level=AssertionLevel.RECOMMENDED,
                priority=2
            )
            assertions.append(existence_assertion)

            # 根据字段类型创建类型断言
            if field_type != "unknown":
                type_assertion = TestAssertion(
                    id=f"assert_field_type_{field_name}",
                    name=f"验证字段类型: {field_name}",
                    description=f"验证 {field_name} 字段类型为 {field_type}",
                    assertion_type=AssertionType.RESPONSE_BODY,
                    expected_value={"field_type": {field_name: field_type}},
                    assertion_level=AssertionType.OPTIONAL,
                    priority=3
                )
                assertions.append(type_assertion)

        return assertions

    def _generate_error_handling_assertions(self, context: AssertionContext) -> List[TestAssertion]:
        """生成错误处理断言"""
        assertions = []

        # 错误消息格式断言
        error_message_assertion = TestAssertion(
            id="assert_error_message_format",
            name="验证错误消息格式",
            description="验证错误响应包含标准化的错误消息格式",
            assertion_type=AssertionType.RESPONSE_BODY,
            expected_value={
                "error_format": {
                    "required_fields": ["code", "message"],
                    "optional_fields": ["details", "trace_id"]
                }
            },
            assertion_level=AssertionLevel.RECOMMENDED,
            priority=2
        )
        assertions.append(error_message_assertion)

        return assertions

    def _generate_business_rule_assertions(self, context: AssertionContext) -> List[TestAssertion]:
        """生成业务规则断言"""
        assertions = []

        for i, rule in enumerate(context.business_rules[:3]):  # 限制前3个规则
            rule_description = rule.get("rule", "").split("。")[0]  # 取第一句

            assertion = TestAssertion(
                id=f"assert_business_rule_{i + 1}",
                name=f"验证业务规则: {rule_description[:30]}...",
                description=f"验证业务规则: {rule_description}",
                assertion_type=AssertionType.BUSINESS_RULE,
                expected_value={"rule_description": rule_description},
                assertion_level=AssertionLevel.REQUIRED,
                priority=1
            )
            assertions.append(assertion)

        return assertions

    def _generate_security_assertions(self, context: AssertionContext) -> List[TestAssertion]:
        """生成安全断言"""
        assertions = []

        # 认证检查
        auth_assertion = TestAssertion(
            id="assert_authentication",
            name="验证认证要求",
            description="验证接口需要有效的认证",
            assertion_type=AssertionType.SECURITY,
            expected_value={"requires_auth": True},
            assertion_level=AssertionLevel.REQUIRED,
            priority=1
        )
        assertions.append(auth_assertion)

        # 敏感数据屏蔽
        sensitive_data_assertion = TestAssertion(
            id="assert_sensitive_data_masking",
            name="验证敏感数据屏蔽",
            description="验证响应中敏感数据被适当屏蔽",
            assertion_type=AssertionType.SECURITY,
            expected_value={"masks_sensitive_data": True},
            assertion_level=AssertionLevel.RECOMMENDED,
            priority=2
        )
        assertions.append(sensitive_data_assertion)

        return assertions

    def _generate_performance_assertions(self, context: AssertionContext) -> List[TestAssertion]:
        """生成性能断言"""
        assertions = []

        # 响应时间断言
        response_time_assertion = TestAssertion(
            id="assert_response_time",
            name="验证响应时间",
            description="验证API响应时间在可接受范围内",
            assertion_type=AssertionType.RESPONSE_TIME,
            expected_value={"max_response_time_ms": 1000},
            assertion_level=AssertionLevel.OPTIONAL,
            priority=3
        )
        assertions.append(response_time_assertion)

        return assertions


class AIBasedAssertionGenerator:
    """AI基础断言生成器"""

    def __init__(self, llm_gateway: Optional[LLMGateway] = None):
        self.llm_gateway = llm_gateway

    async def generate_assertions(
            self,
            context: AssertionContext,
            patterns: List[AssertionPattern]
    ) -> List[TestAssertion]:
        """使用AI生成断言"""

        if not self.llm_gateway:
            return []

        try:
            # 构建AI提示
            prompt = self._build_ai_prompt(context, patterns)

            # 调用AI服务
            request = LLMRequest(
                prompt=prompt,
                system_prompt="你是一个资深的API测试专家，专门生成高质量的测试断言。",
                temperature=0.3,
                max_tokens=1000
            )

            response = await self.llm_gateway.generate_text(request)

            # 解析AI响应
            assertions = self._parse_ai_response(response.content, context)

            return assertions

        except Exception as e:
            # 记录错误但继续
            print(f"AI断言生成失败: {str(e)}")
            return []

    def _build_ai_prompt(self, context: AssertionContext, patterns: List[AssertionPattern]) -> str:
        """构建AI提示"""

        prompt = f"""
        请为以下API端点生成高质量的测试断言：

        API端点：{context.api_endpoint}
        HTTP方法：{context.http_method}
        请求数据：{json.dumps(context.request_data, ensure_ascii=False, indent=2)}

        """

        if context.response_schema:
            prompt += f"响应模式：{json.dumps(context.response_schema, ensure_ascii=False, indent=2)}\n\n"

        if context.business_rules:
            prompt += f"业务规则：{json.dumps(context.business_rules, ensure_ascii=False, indent=2)}\n\n"

        prompt += f"需要关注的断言模式：{', '.join(p.value for p in patterns)}\n\n"

        prompt += """
        请生成以下格式的断言：
        1. 断言名称
        2. 断言描述
        3. 预期值
        4. 断言类型（状态码、响应体、业务规则等）
        5. 优先级（1-5，1最高）

        每个断言请用"---"分隔。
        """

        return prompt

    def _parse_ai_response(self, ai_response: str, context: AssertionContext) -> List[TestAssertion]:
        """解析AI响应"""

        assertions = []
        sections = ai_response.split("---")

        for i, section in enumerate(sections):
            if not section.strip():
                continue

            # 解析断言信息
            lines = section.strip().split('\n')
            assertion_info = {}

            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    assertion_info[key.strip()] = value.strip()

            # 创建断言对象
            if assertion_info:
                assertion = TestAssertion(
                    id=f"ai_assertion_{i + 1}",
                    name=assertion_info.get("断言名称", f"AI生成的断言 {i + 1}"),
                    description=assertion_info.get("断言描述", ""),
                    assertion_type=self._map_assertion_type(assertion_info.get("断言类型", "")),
                    expected_value=assertion_info.get("预期值", ""),
                    assertion_level=AssertionLevel.RECOMMENDED,
                    priority=int(assertion_info.get("优先级", 3))
                )
                assertions.append(assertion)

        return assertions

    def _map_assertion_type(self, type_str: str) -> AssertionType:
        """映射断言类型"""
        type_mapping = {
            "状态码": AssertionType.STATUS_CODE,
            "响应体": AssertionType.RESPONSE_BODY,
            "响应头": AssertionType.RESPONSE_HEADER,
            "响应时间": AssertionType.RESPONSE_TIME,
            "业务规则": AssertionType.BUSINESS_RULE,
            "安全": AssertionType.SECURITY,
            "性能": AssertionType.PERFORMANCE
        }

        return type_mapping.get(type_str, AssertionType.CUSTOM)