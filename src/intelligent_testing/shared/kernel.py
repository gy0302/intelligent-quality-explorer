"""
依赖注入容器（Dependency Injection Container）
管理应用的所有依赖，实现控制反转
"""
import logging
from typing import Dict, Any, Type, Optional, Callable
from threading import Lock

from ...configs.settings import settings
from .shared.utils.logging_utils import setup_logging

logger = logging.getLogger(__name__)


class ServiceRegistry:
    """服务注册表"""

    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, Callable] = {}
        self._singletons: Dict[str, Any] = {}
        self._lock = Lock()

    def register(self, name: str, service: Any, singleton: bool = False):
        """注册服务"""
        with self._lock:
            self._services[name] = service
            if singleton:
                self._singletons[name] = service

    def register_factory(self, name: str, factory: Callable):
        """注册工厂函数"""
        with self._lock:
            self._factories[name] = factory

    def get(self, name: str) -> Any:
        """获取服务"""
        with self._lock:
            # 检查单例
            if name in self._singletons:
                return self._singletons[name]

            # 检查服务
            if name in self._services:
                return self._services[name]

            # 检查工厂
            if name in self._factories:
                service = self._factories[name]()
                self._services[name] = service
                return service

            raise KeyError(f"服务未找到: {name}")

    def has(self, name: str) -> bool:
        """检查服务是否存在"""
        with self._lock:
            return name in self._services or name in self._factories


class Kernel:
    """
    依赖注入内核
    管理整个应用的依赖关系
    """

    def __init__(self):
        self._registry = ServiceRegistry()
        self._initialized = False
        self._lock = Lock()

    def init_dependencies(self):
        """初始化所有依赖"""
        if self._initialized:
            return

        with self._lock:
            logger.info("开始初始化依赖注入容器...")

            # 设置日志
            setup_logging()

            # 初始化各层组件
            self._init_shared_components()
            self._init_domain_components()
            self._init_application_components()
            self._init_adapter_components()
            self._init_api_components()

            self._initialized = True
            logger.info("依赖注入容器初始化完成")

    def _init_shared_components(self):
        """初始化共享组件"""
        logger.info("初始化共享组件...")

        # 配置
        self._registry.register("settings", settings, singleton=True)

        # 工具类
        from src.shared.utils.file_utils import FileUtils
        self._registry.register("utils.file_utils", FileUtils())

        from src.shared.utils.excel_utils import ExcelUtils
        self._registry.register("utils.excel_utils", ExcelUtils())

        from src.shared.utils.json_utils import JSONUtils
        self._registry.register("utils.json_utils", JSONUtils())

        from src.shared.utils.yaml_utils import YAMLUtils
        self._registry.register("utils.yaml_utils", YAMLUtils())

        logger.info("共享组件初始化完成")

    def _init_domain_components(self):
        """初始化领域组件"""
        logger.info("初始化领域组件...")

        # 领域模型（类引用）
        from src.intelligent_testing.models.specification import APISpecification
        self._registry.register("models.APISpecification", APISpecification)

        from src.intelligent_testing.models.mind_map import MindMap
        self._registry.register("models.MindMap", MindMap)

        from src.intelligent_testing.models.test_case import TestCase
        self._registry.register("models.TestCase", TestCase)

        # 核心服务
        from src.intelligent_testing.services.core.test_generation_engine import TestGenerationEngine
        self._registry.register("services.TestGenerationEngine", TestGenerationEngine(), singleton=True)

        from src.intelligent_testing.services.core.mindmap_builder import MindMapBuilder
        self._registry.register("services.MindMapBuilder", MindMapBuilder(), singleton=True)

        # 智能服务
        from src.intelligent_testing.services.intelligence.test_code_generator import TestCodeGenerator
        self._registry.register("services.TestCodeGenerator", TestCodeGenerator(), singleton=True)

        # AI助手服务
        from src.intelligent_testing.services.assistant.conversation_service import ConversationService
        self._registry.register_factory("services.ConversationService",
                                        lambda: ConversationService(self.get("adapters.LLMAdapter")))

        logger.info("领域组件初始化完成")

    def _init_application_components(self):
        """初始化应用组件"""
        logger.info("初始化应用组件...")

        # 智能体
        from src.application.agent.spec_analysis_agent import SpecAnalysisAgent
        self._registry.register("agents.SpecAnalysisAgent", SpecAnalysisAgent(), singleton=True)

        from src.application.agent.ai_review_agent import AIReviewAgent
        self._registry.register("agents.AIReviewAgent", AIReviewAgent(), singleton=True)

        from src.application.agent.test_case_generation_agent import TestCaseGenerationAgent
        self._registry.register("agents.TestCaseGenerationAgent", TestCaseGenerationAgent(), singleton=True)

        from src.application.agent.ai_assistant_agent import AIAssistantAgent
        self._registry.register("agents.AIAssistantAgent", AIAssistantAgent(), singleton=True)

        # 编排器
        from src.application.orchestrators.complete_test_orchestrator import CompleteTestOrchestrator
        self._registry.register("orchestrators.CompleteTestOrchestrator", CompleteTestOrchestrator(), singleton=True)

        logger.info("应用组件初始化完成")

    def _init_adapter_components(self):
        """初始化适配器组件"""
        logger.info("初始化适配器组件...")

        # LLM适配器（根据配置选择）
        llm_provider = settings.LLM_PROVIDER

        if llm_provider == "openai":
            from src.adapters.secondary.llm.openai_adapter import OpenAIAdapter
            llm_adapter = OpenAIAdapter()
        elif llm_provider == "anthropic":
            from src.adapters.secondary.llm.anthropic_adapter import AnthropicAdapter
            llm_adapter = AnthropicAdapter()
        elif llm_provider == "ollama":
            from src.adapters.secondary.llm.ollama_adapter import OllamaAdapter
            llm_adapter = OllamaAdapter()
        else:
            from src.adapters.secondary.llm.local_llm_adapter import LocalLLMAdapter
            llm_adapter = LocalLLMAdapter()

        self._registry.register("adapters.LLMAdapter", llm_adapter, singleton=True)

        # 解析器适配器
        from src.adapters.secondary.parsers.openapi_parser_adapter import OpenAPIParserAdapter
        self._registry.register("adapters.OpenAPIParserAdapter", OpenAPIParserAdapter(), singleton=True)

        # 导出器适配器
        from src.adapters.secondary.exporters.excel_exporter import ExcelExporter
        self._registry.register("adapters.ExcelExporter", ExcelExporter(), singleton=True)

        from src.adapters.secondary.exporters.csv_exporter import CSVExporter
        self._registry.register("adapters.CSVExporter", CSVExporter(), singleton=True)

        # 存储库适配器
        from src.adapters.secondary.repositories.sqlite_repo import SQLiteRepository
        self._registry.register("adapters.SQLiteRepository", SQLiteRepository(), singleton=True)

        logger.info("适配器组件初始化完成")

    def _init_api_components(self):
        """初始化API组件"""
        logger.info("初始化API组件...")

        # API工厂
        from src.adapters.primary.fastapi.app_factory import create_app
        self._registry.register("api.app_factory", create_app, singleton=True)

        logger.info("API组件初始化完成")

    def get(self, name: str) -> Any:
        """获取服务"""
        if not self._initialized:
            self.init_dependencies()

        return self._registry.get(name)

    def get_by_type(self, cls: Type) -> Any:
        """通过类型获取服务"""
        # 遍历所有服务，找到匹配类型的
        # 注意：这里简化实现，实际应该维护类型映射
        for key in self._registry._services:
            service = self._registry._services[key]
            if isinstance(service, cls):
                return service

        raise KeyError(f"服务类型未找到: {cls.__name__}")

    def register_service(self, name: str, service: Any, singleton: bool = False):
        """注册服务（用于扩展）"""
        self._registry.register(name, service, singleton)

    def register_factory(self, name: str, factory: Callable):
        """注册工厂函数（用于扩展）"""
        self._registry.register_factory(name, factory)


# 创建全局内核实例
kernel = Kernel()