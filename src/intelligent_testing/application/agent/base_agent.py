from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from pydantic import BaseModel

TInput = TypeVar('TInput', bound=BaseModel)
TOutput = TypeVar('TOutput', bound=BaseModel)


class BaseAgent(ABC, Generic[TInput, TOutput]):
    """智能体抽象基类，所有用例智能体应继承此类"""

    agent_name: str
    agent_version: str = "1.0.0"

    @abstractmethod
    async def execute(self, input_data: TInput, context: dict = None) -> TOutput:
        """
        执行智能体的核心任务

        Args:
            input_data: 输入数据，符合Pydantic模型
            context: 执行上下文（如工作流ID、用户信息等）

        Returns:
            输出数据，符合Pydantic模型

        Raises:
            AgentExecutionError: 智能体执行失败时抛出
        """
        pass

    def get_metadata(self) -> dict:
        """获取智能体元数据"""
        return {
            "name": self.agent_name,
            "version": self.agent_version,
            "description": self.__doc__
        }