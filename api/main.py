"""
FastAPI主应用入口
采用现代化API设计，支持OpenAPI文档、中间件、依赖注入等
"""
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html
from contextlib import asynccontextmanager
import logging
from typing import Dict, Any, List

from config.settings import settings
from src.shared.kernel import kernel
from api.dependencies import get_kernel, get_current_user
from api.middleware import RequestLoggingMiddleware, ExceptionHandlerMiddleware
from api.routers import (
    spec,
    mindmap,
    testcase,
    script,
    review,
    workflow,
    assistant,
    strategy
)

# 配置日志
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(settings.LOG_DIR / "api.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    - 启动时初始化
    - 运行时提供服务
    - 关闭时清理资源
    """
    # 启动时
    logger.info(f"启动{settings.APP_NAME} - API服务")
    logger.info(f"环境: {settings.ENVIRONMENT}")
    logger.info(f"版本: {settings.APP_VERSION}")

    # 初始化依赖注入容器
    kernel.init_dependencies()
    logger.info("依赖注入容器初始化完成")

    # 存储到app状态
    app.state.kernel = kernel
    app.state.settings = settings

    yield  # 应用运行中

    # 关闭时
    logger.info(f"关闭{settings.APP_NAME} - API服务")
    # 这里可以添加清理资源的逻辑


def create_app() -> FastAPI:
    """创建FastAPI应用实例"""
    # 创建应用
    app = FastAPI(
        title=settings.APP_NAME,
        description=settings.APP_DESCRIPTION,
        version=settings.APP_VERSION,
        docs_url=None if settings.ENVIRONMENT == "production" else "/docs",
        redoc_url=None if settings.ENVIRONMENT == "production" else "/redoc",
        openapi_url="/openapi.json" if settings.ENVIRONMENT != "production" else None,
        lifespan=lifespan,
        contact={
            "name": "智能测试团队",
            "url": "https://gitee.com/aiqa-explore/intelligent-quality-explorer",
            "email": "contact@smart-test-pilot-pro.com"
        },
        license_info={
            "name": "MIT License",
            "url": "https://opensource.org/licenses/MIT"
        },
        servers=[
            {
                "url": "http://localhost:8000",
                "description": "开发服务器"
            },
            {
                "url": "https://api.test-intelligent-pro.com",
                "description": "生产服务器"
            }
        ]
    )

    # 添加中间件
    _add_middlewares(app)

    # 挂载静态文件
    _mount_static_files(app)

    # 添加异常处理器
    _add_exception_handlers(app)

    # 添加路由
    _add_routers(app)

    # 添加健康检查
    _add_health_endpoints(app)

    # 自定义文档
    _customize_docs(app)

    return app


def _add_middlewares(app: FastAPI):
    """添加中间件"""
    # CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.DEBUG else [
            "http://localhost:8501",
            "https://smart-test-pilot-pro.com"
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # GZIP压缩中间件
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # 可信主机中间件（生产环境）
    if not settings.DEBUG:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["smart-test-pilot-pro.com", "api.smart-test-pilot-pro.com"]
        )

    # 请求日志中间件
    app.add_middleware(RequestLoggingMiddleware)

    # 异常处理中间件
    app.add_middleware(ExceptionHandlerMiddleware)


def _mount_static_files(app: FastAPI):
    """挂载静态文件"""
    # 确保静态文件目录存在
    static_dir = settings.BASE_DIR / "static"
    static_dir.mkdir(exist_ok=True)

    app.mount("/static", StaticFiles(directory=static_dir), name="static")


def _add_exception_handlers(app: FastAPI):
    """添加异常处理器"""

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """HTTP异常处理器"""
        logger.warning(f"HTTP异常: {exc.status_code} - {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.status_code,
                    "message": exc.detail,
                    "type": "HTTPException"
                },
                "request_id": request.state.request_id if hasattr(request.state, "request_id") else None
            }
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """全局异常处理器"""
        logger.error(f"未处理的异常: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": 500,
                    "message": "内部服务器错误",
                    "type": "InternalServerError",
                    "detail": str(exc) if settings.DEBUG else "请联系管理员"
                },
                "request_id": request.state.request_id if hasattr(request.state, "request_id") else None
            }
        )


def _add_routers(app: FastAPI):
    """添加路由"""
    # API v1 路由
    api_v1_prefix = "/api/v1"

    app.include_router(
        spec.router,
        prefix=f"{api_v1_prefix}/specs",
        tags=["API规范"],
        dependencies=[Depends(get_current_user)] if not settings.DEBUG else []
    )

    app.include_router(
        mindmap.router,
        prefix=f"{api_v1_prefix}/mindmaps",
        tags=["思维导图"],
        dependencies=[Depends(get_current_user)] if not settings.DEBUG else []
    )

    app.include_router(
        testcase.router,
        prefix=f"{api_v1_prefix}/testcases",
        tags=["测试用例"],
        dependencies=[Depends(get_current_user)] if not settings.DEBUG else []
    )

    app.include_router(
        script.router,
        prefix=f"{api_v1_prefix}/scripts",
        tags=["测试脚本"],
        dependencies=[Depends(get_current_user)] if not settings.DEBUG else []
    )

    app.include_router(
        review.router,
        prefix=f"{api_v1_prefix}/reviews",
        tags=["评审管理"],
        dependencies=[Depends(get_current_user)] if not settings.DEBUG else []
    )

    app.include_router(
        workflow.router,
        prefix=f"{api_v1_prefix}/workflows",
        tags=["工作流"],
        dependencies=[Depends(get_current_user)] if not settings.DEBUG else []
    )

    app.include_router(
        assistant.router,
        prefix=f"{api_v1_prefix}/assistant",
        tags=["AI助手"],
        dependencies=[Depends(get_current_user)] if not settings.DEBUG else []
    )

    app.include_router(
        strategy.router,
        prefix=f"{api_v1_prefix}/strategies",
        tags=["策略管理"],
        dependencies=[Depends(get_current_user)] if not settings.DEBUG else []
    )


def _add_health_endpoints(app: FastAPI):
    """添加健康检查端点"""

    @app.get("/health", tags=["健康检查"])
    async def health_check():
        """健康检查端点"""
        return {
            "status": "healthy",
            "service": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT
        }

    @app.get("/ready", tags=["健康检查"])
    async def readiness_check():
        """就绪检查端点"""
        # 检查关键依赖（数据库、Redis、