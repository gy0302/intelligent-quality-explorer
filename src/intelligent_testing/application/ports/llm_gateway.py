"""
LLM网关端口接口
定义与LLM交互的抽象接口
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class LLMRequest:
    """LLM请求数据"""
    prompt: str
    system_prompt: Optional[str] = None
    temperature: float = 0.1
    max_tokens: int = 2000
    model: Optional[str] = None
    metadata: Dict[str, Any] = None


@dataclass
class LLMResponse:
    """LLM响应数据"""
    content: str
    model: str
    usage: Dict[str, int]
    metadata: Dict[str, Any] = None


class LLMGateway(ABC):
    """LLM网关抽象接口"""

    @abstractmethod
    async def generate_text(self, request: LLMRequest) -> LLMResponse:
        """生成文本"""
        pass

    @abstractmethod
    async def generate_with_chat(self, messages: List[Dict[str, str]],
                                 temperature: float = 0.1) -> str:
        """使用聊天模式生成"""
        pass

    @abstractmethod
    def supports_model(self, model_name: str) -> bool:
        """检查是否支持特定模型"""
        pass

    @abstractmethod
    def get_available_models(self) -> List[str]:
        """获取可用模型列表"""
        pass