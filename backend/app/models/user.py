"""
用户模型
Author: AI Writer Team
Created: 2025-06-01
"""

from typing import Optional, List
from sqlalchemy import Column, String, Boolean, Text
from sqlalchemy.orm import relationship

from app.models.base import Base


class User(Base):
    """用户模型"""
    
    __tablename__ = "users"
    
    # 基础信息
    username = Column(
        String(50), 
        unique=True, 
        index=True, 
        nullable=False,
        comment="用户名"
    )
    email = Column(
        String(100), 
        unique=True, 
        index=True, 
        nullable=False,
        comment="邮箱"
    )
    password_hash = Column(
        String(128), 
        nullable=False,
        comment="密码哈希"
    )
    
    # 个人信息
    avatar_url = Column(
        String(255), 
        nullable=True,
        comment="头像URL"
    )
    nickname = Column(
        String(100), 
        nullable=True,
        comment="昵称"
    )
    bio = Column(
        Text, 
        nullable=True,
        comment="个人简介"
    )
    
    # 状态信息
    is_active = Column(
        Boolean, 
        default=True, 
        nullable=False,
        comment="是否激活"
    )
    is_verified = Column(
        Boolean, 
        default=False, 
        nullable=False,
        comment="是否已验证邮箱"
    )
    is_admin = Column(
        Boolean, 
        default=False, 
        nullable=False,
        comment="是否管理员"
    )
    
    # 偏好设置
    preferred_language = Column(
        String(10), 
        default="zh-CN", 
        nullable=False,
        comment="首选语言"
    )
    timezone = Column(
        String(50), 
        default="Asia/Shanghai", 
        nullable=False,
        comment="时区"
    )
    
    # 关系映射
    novels = relationship(
        "Novel",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select"
    )
    characters = relationship(
        "Character",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select"
    )
    rough_outlines = relationship(
        "RoughOutline",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select"
    )
    detailed_outlines = relationship(
        "DetailedOutline",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select"
    )
    worldviews = relationship(
        "Worldview",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select"
    )
    chapters = relationship(
        "Chapter",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select"
    )
    world_maps = relationship(
        "WorldMap",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select"
    )
    cultivation_systems = relationship(
        "CultivationSystem",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select"
    )
    histories = relationship(
        "History",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select"
    )
    factions = relationship(
        "Faction",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select"
    )
    ai_model_configs = relationship(
        "AIModelConfig",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select"
    )
    
    def __repr__(self) -> str:
        """用户模型的字符串表示"""
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"
    
    def to_dict(self, include_sensitive: bool = False) -> dict:
        """
        转换为字典格式
        
        Args:
            include_sensitive: 是否包含敏感信息
            
        Returns:
            dict: 用户信息字典
        """
        data = {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "nickname": self.nickname,
            "bio": self.bio,
            "avatar_url": self.avatar_url,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "preferred_language": self.preferred_language,
            "timezone": self.timezone,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_sensitive:
            data.update({
                "is_admin": self.is_admin,
            })
        
        return data
    
    def to_public_dict(self) -> dict:
        """
        转换为公开信息字典
        
        Returns:
            dict: 公开用户信息
        """
        return {
            "id": self.id,
            "username": self.username,
            "nickname": self.nickname or self.username,
            "bio": self.bio,
            "avatar_url": self.avatar_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
    
    @property
    def display_name(self) -> str:
        """显示名称"""
        return self.nickname or self.username
    
    @property
    def novel_count(self) -> int:
        """小说数量"""
        return len(self.novels) if self.novels else 0
    
    def activate(self) -> None:
        """激活用户"""
        self.is_active = True
    
    def deactivate(self) -> None:
        """停用用户"""
        self.is_active = False
    
    def verify_email(self) -> None:
        """验证邮箱"""
        self.is_verified = True
    
    def set_admin(self, is_admin: bool = True) -> None:
        """设置管理员权限"""
        self.is_admin = is_admin
    
    def update_profile(self, **kwargs) -> None:
        """
        更新用户资料
        
        Args:
            **kwargs: 更新的字段
        """
        allowed_fields = {
            'nickname', 'bio', 'avatar_url', 
            'preferred_language', 'timezone'
        }
        
        for field, value in kwargs.items():
            if field in allowed_fields and hasattr(self, field):
                setattr(self, field, value)