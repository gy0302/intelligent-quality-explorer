"""
应用配置管理
使用Pydantic v2进行配置管理
"""
from typing import Optional, List, Dict, Any
from pydantic import Field, field_validator, ConfigDict
from pydantic_settings import BaseSettings
import os
from pathlib import Path


class DatabaseSettings(BaseSettings):
    """数据库配置"""
    url: str = Field(..., alias="DATABASE_URL")
    pool_size: int = Field(10, alias="DATABASE_POOL_SIZE")
    max_overflow: int = Field(20, alias="DATABASE_MAX_OVERFLOW")
    echo: bool = Field(False, alias="DATABASE_ECHO")

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


class OpenAISettings(BaseSettings):
    """OpenAI配置"""
    api_key: str = Field(..., alias="OPENAI_API_KEY")
    model: str = Field("gpt-4-1106-preview", alias="OPENAI_MODEL")
    temperature: float = Field(0.7, alias="OPENAI_TEMPERATURE")
    max_tokens: int = Field(4000, alias="OPENAI_MAX_TOKENS")

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @field_validator('api_key')
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        # 直接从环境变量获取APP_ENV
        import os
        app_env = os.getenv("APP_ENV", "development")
        
        # 在开发环境下允许使用默认值
        if app_env != 'development':
            if not v or v == "your-openai-api-key":
                raise ValueError("OpenAI API key must be set")
        return v


class OllamaSettings(BaseSettings):
    """Ollama配置"""
    base_url: str = Field("http://localhost:11434", alias="OLLAMA_BASE_URL")
    model: str = Field("qwen3:8b", alias="OLLAMA_MODEL")
    temperature: float = Field(0.7, alias="OLLAMA_TEMPERATURE")

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


class AppSettings(BaseSettings):
    """应用配置"""
    env: str = Field("development", alias="APP_ENV")
    secret_key: str = Field(..., alias="APP_SECRET_KEY")
    debug: bool = Field(True, alias="APP_DEBUG")

    # 文件上传
    upload_folder: str = Field("./uploads", alias="UPLOAD_FOLDER")
    max_content_length: int = Field(16777216, alias="MAX_CONTENT_LENGTH")

    # CORS
    cors_origins: List[str] = Field(["http://localhost:8501"], alias="CORS_ORIGINS")

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @field_validator('secret_key')
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        # 直接从环境变量获取APP_ENV
        import os
        app_env = os.getenv("APP_ENV", "development")
        
        # 在开发环境下允许使用默认值
        if app_env != 'development':
            if not v or v == "your-secret-key-change-in-production":
                raise ValueError("App secret key must be set and secure")
        return v

    @field_validator('upload_folder')
    @classmethod
    def create_upload_folder(cls, v: str) -> str:
        """创建上传文件夹"""
        path = Path(v)
        path.mkdir(parents=True, exist_ok=True)
        return str(path)


class LogSettings(BaseSettings):
    """日志配置"""
    level: str = Field("INFO", alias="LOG_LEVEL")
    file: str = Field("logs/app.log", alias="LOG_FILE")

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @field_validator('file')
    @classmethod
    def create_log_folder(cls, v: str) -> str:
        """创建日志文件夹"""
        path = Path(v)
        path.parent.mkdir(parents=True, exist_ok=True)
        return v


class Settings(BaseSettings):
    """全局设置"""
    database: DatabaseSettings = DatabaseSettings()
    openai: OpenAISettings = OpenAISettings()
    ollama: OllamaSettings = OllamaSettings()
    app: AppSettings = AppSettings()
    log: LogSettings = LogSettings()

    # 项目路径
    project_root: Path = Path(__file__).parent.parent.parent
    data_dir: Path = project_root / "data"
    outputs_dir: Path = project_root / "outputs"

    # AI评审配置
    ai_reviewers: List[Dict[str, Any]] = [
        {
            "role": "资深质量架构师",
            "focus_areas": ["测试覆盖率", "边界条件", "错误处理", "性能测试"]
        },
        {
            "role": "资深开发专家",
            "focus_areas": ["代码规范", "接口设计", "数据结构", "算法复杂度"]
        },
        {
            "role": "资深需求专家",
            "focus_areas": ["业务逻辑", "用户场景", "需求完整性", "用户体验"]
        }
    ]

    # 工作流配置
    workflow_steps: List[Dict[str, Any]] = [
        {"id": "import", "name": "API导入", "description": "导入OpenAPI/Swagger规范"},
        {"id": "api_review", "name": "API评审", "description": "AI专家评审API规范"},
        {"id": "test_points", "name": "测试点生成", "description": "生成测试点并形成思维导图"},
        {"id": "points_review", "name": "测试点评审", "description": "评审测试点"},
        {"id": "test_cases", "name": "测试用例生成", "description": "生成测试用例列表"},
        {"id": "cases_review", "name": "测试用例评审", "description": "评审测试用例"},
        {"id": "scripts", "name": "脚本生成", "description": "生成测试脚本和数据"},
        {"id": "scripts_review", "name": "脚本评审", "description": "评审测试脚本"},
        {"id": "execution", "name": "测试执行", "description": "执行测试用例"},
        {"id": "report", "name": "测试报告", "description": "生成测试报告"},
    ]

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore"
    )


# 全局设置实例
settings = Settings()