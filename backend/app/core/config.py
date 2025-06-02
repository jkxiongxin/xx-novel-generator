"""
应用配置管理
Author: AI Writer Team
Created: 2025-06-01
"""

import os
from typing import Any, Dict, Optional, List
from pydantic_settings import BaseSettings
from pydantic import validator


class Settings(BaseSettings):
    """应用配置类"""
    
    # 基础配置
    APP_NAME: str = "AI智能小说创作平台"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = False
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./ai_writer.db"
    DATABASE_ECHO: bool = False
    
    # 安全配置
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"
    
    # CORS配置
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1", "*"]
    
    # 开发环境CORS配置
    DEV_CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173,http://localhost:8080,http://localhost:4173"
    
    # 生产环境CORS配置
    PROD_CORS_ORIGINS: str = ""
    
    # CORS通配符支持 (仅开发环境)
    CORS_ALLOW_ALL_ORIGINS: bool = False
    
    # 传统CORS配置 (保持兼容性)
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]
    
    # AI配置
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    OPENAI_MAX_TOKENS: int = 2000
    OPENAI_TEMPERATURE: float = 0.7
    
    # 文件上传配置
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: List[str] = [".txt", ".md", ".docx"]
    
    # 分页配置
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    
    @validator("SECRET_KEY")
    def validate_secret_key(cls, v: str) -> str:
        """验证密钥长度"""
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v
    
    @validator("DATABASE_URL")
    def validate_database_url(cls, v: str) -> str:
        """验证数据库URL格式"""
        if not v.startswith(("sqlite://", "postgresql://", "mysql://")):
            raise ValueError("DATABASE_URL must start with sqlite://, postgresql://, or mysql://")
        return v
    
    @property
    def database_config(self) -> Dict[str, Any]:
        """获取数据库配置"""
        return {
            "url": self.DATABASE_URL,
            "echo": self.DATABASE_ECHO,
        }
    @property
    def cors_config(self) -> Dict[str, Any]:
        """获取CORS配置"""
        # 根据环境选择CORS源
        if self.DEBUG:
            if self.CORS_ALLOW_ALL_ORIGINS:
                origins = ["*"]
            else:
                # 将字符串转换为列表
                origins = [url.strip() for url in self.DEV_CORS_ORIGINS.split(",") if url.strip()]
        else:
            if self.PROD_CORS_ORIGINS:
                origins = [url.strip() for url in self.PROD_CORS_ORIGINS.split(",") if url.strip()]
            else:
                origins = self.CORS_ORIGINS
        
        return {
            "allow_origins": origins,
            "allow_credentials": True,
            "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
            "allow_headers": [
                "Accept",
                "Accept-Language",
                "Content-Language",
                "Content-Type",
                "Authorization",
                "X-Requested-With",
                "X-CSRF-Token",
                "X-Process-Time",
            ],
            "expose_headers": ["X-Process-Time", "X-Total-Count"],
            "max_age": 86400,  # 24小时预检缓存
        }
    
    @property
    def jwt_config(self) -> Dict[str, Any]:
        """获取JWT配置"""
        return {
            "secret_key": self.SECRET_KEY,
            "algorithm": self.ALGORITHM,
            "access_token_expire_minutes": self.ACCESS_TOKEN_EXPIRE_MINUTES,
        }
    
    class Config:
        """Pydantic配置"""
        env_file = ".env"
        case_sensitive = True


# 创建全局配置实例
settings = Settings()


def get_settings() -> Settings:
    """获取配置实例"""
    return settings