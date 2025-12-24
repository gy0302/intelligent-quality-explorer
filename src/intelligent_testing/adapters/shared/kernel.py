# src/shared/kernel.py
"""
应用内核 - 依赖注入容器
"""
from typing import Dict, Any
from loguru import logger


class Kernel:
    """IoC容器"""

    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._initialized = False

    def register(self, name: str, service: Any):
        """注册服务"""
        self._services[name] = service
        return self

    def get(self, name: str) -> Any:
        """获取服务"""
        if name not in self._services:
            raise KeyError(f"Service '{name}' not registered")
        return self._services[name]

    def init(self):
        """初始化所有服务"""
        if self._initialized:
            return

        logger.info("Initializing application kernel...")

        # 这里会初始化所有服务
        self._initialized = True
        logger.success("Application kernel initialized")


kernel = Kernel()