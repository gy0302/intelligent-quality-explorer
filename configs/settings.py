"""
全局配置管理
采用分层配置，支持环境变量覆盖
"""
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from pydantic import BaseSettings, Field, validator
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class Settings(BaseSettings):
    """应用主配置"""

    # 应用信息
    APP_NAME: str = Field("智能测试探索架构", description="应用名称")
    APP_VERSION: str = Field("0.1.0", description="应用版本")
    APP_DESCRIPTION: str = Field("基于AI的智能接口测试自动生成平台", description="应用描述")

    # 环境配置
    ENVIRONMENT: str = Field("development", description="运行环境")
    DEBUG: bool = Field(True, description="调试模式")
    LOG_LEVEL: str = Field("INFO", description="日志级别")

    # 路径配置
    BASE_DIR: Path = Path(__file__).parent.parent
    CONFIG_DIR: Path = BASE_DIR / "config"
    DATA_DIR: Path = BASE_DIR / "data"
    OUTPUT_DIR: Path = BASE_DIR / "outputs"
    LOG_DIR: Path = BASE_DIR / "logs"
    UPLOAD_DIR: Path = BASE_DIR / "uploads"

    # API配置
    API_HOST: str = Field("0.0.0.0", description="API主机")
    API_PORT: int = Field(8000, description="API端口")
    API_RELOAD: bool = Field(True, description="API热重载")
    API_WORKERS: int = Field(1, description="API工作进程数")

    # Web配置
    WEB_HOST: str = Field("0.0.0.0", description="Web主机")
    WEB_PORT: int = Field(8501, description="Web端口")
    WEB_BROWSER: bool = Field(True, description="自动打开浏览器")

    # LLM配置
    LLM_PROVIDER: str = Field("openai", description="LLM提供商")
    OPENAI_API_KEY: Optional[str] = Field(None, description="OpenAI API密钥")
    OPENAI_MODEL: str = Field("gpt-4-turbo-preview", description="OpenAI模型")
    OPENAI_BASE_URL: Optional[str] = Field(None, description="OpenAI基础URL")

    ANTHROPIC_API_KEY: Optional[str] = Field(None, description="Anthropic API密钥")
    ANTHROPIC_MODEL: str = Field("claude-3-opus", description="Anthropic模型")

    OLLAMA_BASE_URL: str = Field("http://localhost:11434", description="Ollama基础URL")
    OLLAMA_MODEL: str = Field("llama2", description="Ollama模型")

    # 本地LLM配置
    LOCAL_LLM_ENABLED: bool = Field(False, description="启用本地LLM")
    LOCAL_LLM_MODEL_PATH: Optional[str] = Field(None, description="本地模型路径")

    # LangChain配置
    LANGCHAIN_TRACING: bool = Field(False, description="LangChain追踪")
    LANGCHAIN_PROJECT: Optional[str] = Field(None, description="LangChain项目")

    # 数据库配置
    DATABASE_URL: str = Field("sqlite:///./data/test_pilot.db", description="数据库URL")
    DATABASE_ECHO: bool = Field(False, description="数据库回显")

    # Redis配置
    REDIS_ENABLED: bool = Field(False, description="启用Redis")
    REDIS_URL: str = Field("redis://localhost:6379/0", description="Redis URL")
    REDIS_PASSWORD: Optional[str] = Field(None, description="Redis密码")

    # 向量数据库配置
    VECTOR_DB_TYPE: str = Field("chromadb", description="向量数据库类型")
    CHROMA_PERSIST_DIR: str = Field("./data/chroma_db", description="Chroma持久化目录")

    # 安全配置
    SECRET_KEY: str = Field("your-secret-key-change-in-production", description="密钥")
    JWT_ALGORITHM: str = Field("HS256", description="JWT算法")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(30, description="访问令牌过期时间")

    # 文件配置
    MAX_UPLOAD_SIZE: int = Field(10 * 1024 * 1024, description="最大上传大小")
    ALLOWED_EXTENSIONS: List[str] = Field([".json", ".yaml", ".yml"], description="允许的文件扩展名")

    # 测试配置
    DEFAULT_TEST_CASE_FORMAT: str = Field("excel", description="默认测试用例格式")
    DEFAULT_TEST_RUNNER: str = Field("pytest", description="默认测试运行器")

    # 缓存配置
    CACHE_ENABLED: bool = Field(True, description="启用缓存")
    CACHE_TTL: int = Field(3600, description="缓存TTL（秒）")

    # 性能配置
    MAX_RETRIES: int = Field(3, description="最大重试次数")
    TIMEOUT_SECONDS: int = Field(30, description="超时秒数")
    RATE_LIMIT: int = Field(100, description="速率限制")

    # AI助手配置
    AI_ASSISTANT_ENABLED: bool = Field(True, description="启用AI助手")
    AI_ASSISTANT_DEFAULT_EXPERT: str = Field("api_testing_expert", description="默认专家")
    AI_ASSISTANT_HISTORY_SIZE: int = Field(50, description="历史记录大小")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @validator("ENVIRONMENT")
    def validate_environment(cls, v):
        """验证环境"""
        valid_environments = ["development", "testing", "staging", "production"]
        if v not in valid_environments:
            raise ValueError(f"环境必须是: {', '.join(valid_environments)}")
        return v

    @validator("LLM_PROVIDER")
    def validate_llm_provider(cls, v):
        """验证LLM提供商"""
        valid_providers = ["openai", "anthropic", "ollama", "local"]
        if v not in valid_providers:
            raise ValueError(f"LLM提供商必须是: {', '.join(valid_providers)}")
        return v

    def get_database_config(self) -> Dict[str, Any]:
        """获取数据库配置"""
        return {
            "url": self.DATABASE_URL,
            "echo": self.DATABASE_ECHO,
            "pool_size": 5,
            "max_overflow": 10,
            "pool_timeout": 30,
        }

    def get_redis_config(self) -> Dict[str, Any]:
        """获取Redis配置"""
        return {
            "url": self.REDIS_URL,
            "password": self.REDIS_PASSWORD,
            "decode_responses": True,
        }

    def ensure_directories(self):
        """确保必要的目录存在"""
        directories = [
            self.DATA_DIR,
            self.OUTPUT_DIR,
            self.LOG_DIR,
            self.UPLOAD_DIR,
            self.OUTPUT_DIR / "mindmaps",
            self.OUTPUT_DIR / "test_cases" / "csv",
            self.OUTPUT_DIR / "test_cases" / "excel",
            self.OUTPUT_DIR / "scripts",
            self.OUTPUT_DIR / "reports",
            self.OUTPUT_DIR / "reviews" / "ai_reviews",
            self.OUTPUT_DIR / "reviews" / "human_reviews",
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)


# 创建全局配置实例
settings = Settings()
settings.ensure_directories()