"""
数据库连接配置
Author: AI Writer Team
Created: 2025-06-01
"""

from typing import AsyncGenerator
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.core.config import settings


# 创建数据库引擎
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基础模型类
Base = declarative_base()

# 元数据
metadata = MetaData()


def get_db() -> Session:
    """
    获取数据库会话
    
    Yields:
        Session: 数据库会话实例
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables() -> None:
    """创建所有数据表"""
    Base.metadata.create_all(bind=engine)


def drop_tables() -> None:
    """删除所有数据表"""
    Base.metadata.drop_all(bind=engine)


def init_db() -> None:
    """初始化数据库"""
    # 创建表
    create_tables()
    
    # 这里可以添加初始数据的创建逻辑
    # 例如：创建默认用户、初始化提示词模板等
    pass


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self):
        self.engine = engine
        self.SessionLocal = SessionLocal
        self.Base = Base
    
    def get_session(self) -> Session:
        """获取新的数据库会话"""
        return self.SessionLocal()
    
    def create_all_tables(self) -> None:
        """创建所有表"""
        self.Base.metadata.create_all(bind=self.engine)
    
    def drop_all_tables(self) -> None:
        """删除所有表"""
        self.Base.metadata.drop_all(bind=self.engine)
    
    def reset_database(self) -> None:
        """重置数据库"""
        self.drop_all_tables()
        self.create_all_tables()


# 创建数据库管理器实例
db_manager = DatabaseManager()


# 数据库健康检查
def check_database_health() -> bool:
    """
    检查数据库连接健康状态
    
    Returns:
        bool: 连接是否正常
    """
    try:
        db = SessionLocal()
        # 执行简单查询测试连接
        db.execute("SELECT 1")
        db.close()
        return True
    except Exception:
        return False


# 数据库连接信息
def get_database_info() -> dict:
    """
    获取数据库连接信息
    
    Returns:
        dict: 数据库信息
    """
    return {
        "url": settings.DATABASE_URL,
        "echo": settings.DATABASE_ECHO,
        "driver": settings.DATABASE_URL.split("://")[0],
        "health": check_database_health(),
    }