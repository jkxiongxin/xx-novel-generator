"""
基础模型类
Author: AI Writer Team
Created: 2025-06-01
"""

from datetime import datetime
from typing import Any
from sqlalchemy import Column, Integer, DateTime, Boolean, String, func
from sqlalchemy.ext.declarative import declarative_base, declared_attr


class BaseModel:
    """基础模型类，包含通用字段和方法"""
    
    @declared_attr
    def __tablename__(cls) -> str:
        """自动生成表名"""
        # 将类名转换为小写下划线格式
        import re
        name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', cls.__name__)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower() + 's'
    
    # 主键
    id = Column(Integer, primary_key=True, index=True, comment="主键ID")
    
    # 时间戳字段
    created_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False,
        comment="创建时间"
    )
    updated_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now(),
        nullable=False,
        comment="更新时间"
    )
    
    def to_dict(self) -> dict:
        """
        将模型实例转换为字典
        
        Returns:
            dict: 模型数据字典
        """
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                value = value.isoformat()
            result[column.name] = value
        return result
    
    def update_from_dict(self, data: dict) -> None:
        """
        从字典更新模型实例
        
        Args:
            data: 更新数据字典
        """
        for key, value in data.items():
            if hasattr(self, key) and key not in ['id', 'created_at']:
                setattr(self, key, value)
    
    def __repr__(self) -> str:
        """模型实例的字符串表示"""
        return f"<{self.__class__.__name__}(id={self.id})>"


# 创建基础类
Base = declarative_base(cls=BaseModel)


class TimestampMixin:
    """时间戳混入类"""
    
    created_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False,
        comment="创建时间"
    )
    updated_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now(),
        nullable=False,
        comment="更新时间"
    )


class SoftDeleteMixin:
    """软删除混入类"""
    
    deleted_at = Column(
        DateTime(timezone=True), 
        nullable=True,
        comment="删除时间"
    )
    is_deleted = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="是否已删除"
    )
    
    def soft_delete(self) -> None:
        """软删除"""
        self.deleted_at = datetime.utcnow()
        self.is_deleted = True
    
    def restore(self) -> None:
        """恢复删除"""
        self.deleted_at = None
        self.is_deleted = False


class UserOwnedMixin:
    """用户所有权混入类"""
    
    @declared_attr
    def user_id(cls):
        """用户ID外键"""
        from sqlalchemy import Column, Integer, ForeignKey
        return Column(
            Integer, 
            ForeignKey("users.id", ondelete="CASCADE"), 
            nullable=False,
            index=True,
            comment="用户ID"
        )
    
    @declared_attr
    def user(cls):
        """用户关系"""
        from sqlalchemy.orm import relationship
        return relationship("User", back_populates=cls.__tablename__)


class StatusMixin:
    """状态混入类"""
    
    status = Column(
        String(50),
        nullable=False,
        default="active",
        comment="状态"
    )
    
    def is_active(self) -> bool:
        """是否活跃状态"""
        return self.status == "active"
    
    def activate(self) -> None:
        """激活"""
        self.status = "active"
    
    def deactivate(self) -> None:
        """停用"""
        self.status = "inactive"


# 导出所有基础类和混入类
__all__ = [
    "Base",
    "BaseModel", 
    "TimestampMixin",
    "SoftDeleteMixin", 
    "UserOwnedMixin",
    "StatusMixin"
]