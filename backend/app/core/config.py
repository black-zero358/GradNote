import os
import sys
from typing import Optional, Dict, Any, List
from pydantic import PostgresDsn, field_validator, ValidationInfo
from pydantic_settings import BaseSettings

def validate_required_env_vars() -> None:
    """
    验证必需的环境变量是否存在
    如果缺少关键的环境变量，应用将无法启动
    """
    required_vars = {
        "SECRET_KEY": "JWT密钥，用于令牌签名",
        "POSTGRES_PASSWORD": "PostgreSQL数据库密码",
        "FIRST_SUPERUSER": "初始管理员用户名",
        "FIRST_SUPERUSER_PASSWORD": "初始管理员密码",
        "FIRST_SUPERUSER_EMAIL": "初始管理员邮箱"
    }
    
    missing_vars = []
    for var_name, description in required_vars.items():
        if not os.getenv(var_name):
            missing_vars.append(f"  - {var_name}: {description}")
    
    if missing_vars:
        error_msg = (
            "❌ 安全错误：缺少必需的环境变量\n\n"
            "以下环境变量是必需的，但未设置：\n"
            + "\n".join(missing_vars) + "\n\n"
            "请设置这些环境变量后重新启动应用。\n"
            "参考 .env.example 文件了解如何配置。\n"
        )
        print(error_msg, file=sys.stderr)
        sys.exit(1)


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    
    # JWT相关配置
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24小时
    
    # 数据库配置
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "GradNote")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    DATABASE_URI: Optional[str] = None
    
    @field_validator("DATABASE_URI", mode="before")
    def assemble_db_connection(cls, v: Optional[str], info: ValidationInfo) -> Any:
        if isinstance(v, str):
            return v
        
        # 获取当前值
        data = info.data
        
        # 确保所有必要的数据库配置都存在
        required_keys = ["POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_SERVER", "POSTGRES_PORT", "POSTGRES_DB"]
        for key in required_keys:
            if key not in data or not data.get(key):
                raise ValueError(f"数据库配置不完整：缺少 {key} 环境变量")
        
        # 使用字符串拼接而不是PostgresDsn.build，避免编码问题
        return f"postgresql://{data.get('POSTGRES_USER')}:{data.get('POSTGRES_PASSWORD')}@{data.get('POSTGRES_SERVER')}:{data.get('POSTGRES_PORT')}/{data.get('POSTGRES_DB')}"
    
    # Redis配置
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    
    # LLM服务配置
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "deepseek-v3-250324")
    VLM_MODEL: str = os.getenv("VLM_MODEL", "doubao-1-5-vision-pro-32k-250115")
    
    # LANGFUSE配置
    LANGFUSE_PUBLIC_KEY: str = os.getenv("LANGFUSE_PUBLIC_KEY", "")
    LANGFUSE_SECRET_KEY: str = os.getenv("LANGFUSE_SECRET_KEY", "")
    
    # OpenAI格式配置
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_API_BASE: str = os.getenv("OPENAI_API_BASE", "")
    OPENAI_LLM_MODEL: str = os.getenv("OPENAI_LLM_MODEL", "")
    OPENAI_EMBEDDING_MODEL: str = os.getenv("OPENAI_EMBEDDING_MODEL", "")
    OPENAI_VLM_MODEL: str = os.getenv("OPENAI_VLM_MODEL", "")
    
    # 服务设置
    DEBUG: str = os.getenv("DEBUG", "false")
    WORKERS: str = os.getenv("WORKERS", "4")
    API_PORT: str = os.getenv("API_PORT", "8000")
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")
    
    # CORS配置
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
    ]

    # 日志配置
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "info")
    LOG_REQUEST_BODY: str = os.getenv("LOG_REQUEST_BODY", "false")
    LOG_ENCODING: str = os.getenv("LOG_ENCODING", "utf-8")

    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "ignore"  # 允许额外的字段，忽略不在模型中定义的字段

# 在创建settings实例前验证必需的环境变量
validate_required_env_vars()

settings = Settings() 