from abc import ABC, abstractmethod
from typing import Dict, Any
from ...models.specification import OpenAPISpecification


class SpecParser(ABC):
    """规范解析器抽象接口"""

    @abstractmethod
    def parse(self, spec_content: str) -> OpenAPISpecification:
        """解析规范内容"""
        pass

    @abstractmethod
    def validate(self, spec_content: str) -> bool:
        """验证规范有效性"""
        pass