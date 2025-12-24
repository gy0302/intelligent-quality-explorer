# src/application/services/test_code_generator.py

class PytestCodeGenerator:
    """Pytest测试代码生成器"""

    def generate_test_class(self, endpoint: Endpoint, strategy: TestStrategy):
        """生成测试类"""
        template = """
import pytest
import requests

class Test{test_class_name}:
    \"\"\"{endpoint_summary}\"\"\"

    base_url = "{base_url}"

    {test_methods}
        """

        test_methods = []
        for scenario in strategy.scenarios:
            test_methods.append(self._generate_test_method(scenario))

        return template.format(
            test_class_name=self._camelize(endpoint.path),
            endpoint_summary=endpoint.summary or f"Test for {endpoint.path}",
            base_url=endpoint.base_url,
            test_methods="\n    ".join(test_methods)
        )