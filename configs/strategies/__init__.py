"""
策略模块 - Domain层策略定义
包含各种测试生成、评审、优化策略
"""
from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, List, Any, Optional, Type
from dataclasses import dataclass
from pydantic import BaseModel, Field
import yaml


class TestGenerationStrategyType(str, Enum):
    """测试生成策略类型"""
    FUNCTIONAL = "functional"
    BOUNDARY = "boundary"
    ERROR = "error"
    SECURITY = "security"
    PERFORMANCE = "performance"
    INTEGRATION = "integration"
    REGRESSION = "regression"


class ReviewStrategyType(str, Enum):
    """评审策略类型"""
    AI_REVIEW = "ai_review"
    HUMAN_REVIEW = "human_review"
    PEER_REVIEW = "peer_review"
    AUTOMATED_REVIEW = "automated_review"


class OptimizationStrategyType(str, Enum):
    """优化策略类型"""
    TEST_SUITE_MINIMIZATION = "test_suite_minimization"
    TEST_CASE_PRIORITIZATION = "test_case_prioritization"
    TEST_DATA_OPTIMIZATION = "test_data_optimization"
    TEST_EXECUTION_OPTIMIZATION = "test_execution_optimization"


@dataclass
class StrategyResult:
    """策略执行结果"""
    success: bool
    data: Any
    metrics: Dict[str, Any]
    recommendations: List[str]
    execution_time: float


class BaseStrategy(ABC):
    """策略基类"""

    def __init__(self, name: str, description: str, config: Optional[Dict] = None):
        self.name = name
        self.description = description
        self.config = config or {}
        self.metrics: Dict[str, Any] = {}

    @abstractmethod
    async def execute(self, *args, **kwargs) -> StrategyResult:
        """执行策略"""
        pass

    def update_config(self, config: Dict[str, Any]):
        """更新配置"""
        self.config.update(config)

    def get_metrics(self) -> Dict[str, Any]:
        """获取指标"""
        return self.metrics.copy()


class TestGenerationStrategy(BaseStrategy):
    """测试生成策略"""

    def __init__(self, strategy_type: TestGenerationStrategyType, **kwargs):
        super().__init__(**kwargs)
        self.strategy_type = strategy_type
        self.coverage_targets = kwargs.get('coverage_targets', {})
        self.rules = kwargs.get('rules', [])

    async def execute(self, api_spec, context=None) -> StrategyResult:
        """执行测试生成策略"""
        raise NotImplementedError


class ReviewStrategy(BaseStrategy):
    """评审策略"""

    def __init__(self, strategy_type: ReviewStrategyType, **kwargs):
        super().__init__(**kwargs)
        self.strategy_type = strategy_type
        self.review_criteria = kwargs.get('review_criteria', [])
        self.scoring_system = kwargs.get('scoring_system', {})

    async def execute(self, content, reviewer=None) -> StrategyResult:
        """执行评审策略"""
        raise NotImplementedError


class OptimizationStrategy(BaseStrategy):
    """优化策略"""

    def __init__(self, strategy_type: OptimizationStrategyType, **kwargs):
        super().__init__(**kwargs)
        self.strategy_type = strategy_type
        self.optimization_goals = kwargs.get('optimization_goals', [])
        self.constraints = kwargs.get('constraints', {})

    async def execute(self, test_suite, context=None) -> StrategyResult:
        """执行优化策略"""
        raise NotImplementedError


class StrategyRegistry:
    """策略注册表"""

    def __init__(self):
        self._strategies: Dict[str, Type[BaseStrategy]] = {}
        self._instances: Dict[str, BaseStrategy] = {}

    def register(self, strategy_class: Type[BaseStrategy], name: Optional[str] = None):
        """注册策略类"""
        strategy_name = name or strategy_class.__name__
        self._strategies[strategy_name] = strategy_class

    def create_strategy(self, name: str, **kwargs) -> BaseStrategy:
        """创建策略实例"""
        if name not in self._strategies:
            raise ValueError(f"策略未注册: {name}")

        strategy_class = self._strategies[name]
        instance = strategy_class(**kwargs)
        self._instances[name] = instance
        return instance

    def get_strategy(self, name: str) -> Optional[BaseStrategy]:
        """获取策略实例"""
        return self._instances.get(name)

    def list_strategies(self) -> List[str]:
        """列出所有已注册策略"""
        return list(self._strategies.keys())


# 创建全局策略注册表
strategy_registry = StrategyRegistry()


def load_strategies_from_config(config_path: str) -> Dict[str, Any]:
    """从配置文件加载策略"""
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config