"""
角色数据模型
Author: AI Assistant
Created: 2025-06-01
"""

import enum
from typing import Optional
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr

from app.models.base import Base, TimestampMixin, UserOwnedMixin


class CharacterType(str, enum.Enum):
    """角色类型枚举"""
    PROTAGONIST = "protagonist"  # 主角
    SUPPORTING = "supporting"    # 配角
    ANTAGONIST = "antagonist"    # 反派
    MINOR = "minor"             # 次要角色
    PASSERBY = "passerby"       # 路人


class CharacterGender(str, enum.Enum):
    """角色性别枚举"""
    MALE = "male"              # 男性
    FEMALE = "female"          # 女性
    UNKNOWN = "unknown"        # 未知
    OTHER = "other"            # 其他


class Character(Base, TimestampMixin, UserOwnedMixin):
    """角色表"""
    
    __tablename__ = "characters"
    
    # 基础信息
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="角色名")
    gender = Column(String(20), default=CharacterGender.UNKNOWN, comment="性别")
    personality = Column(Text, comment="性格描述")
    character_type = Column(String(50), default=CharacterType.SUPPORTING, comment="角色类型")
    
    # 关联信息
    novel_id = Column(Integer, ForeignKey("novels.id", ondelete="CASCADE"), nullable=True, comment="小说ID，模板角色可为空")
    worldview_id = Column(Integer, ForeignKey("worldviews.id", ondelete="SET NULL"), nullable=True, comment="世界观ID")
    faction_id = Column(Integer, ForeignKey("factions.id", ondelete="SET NULL"), nullable=True, comment="所属阵营ID")
    
    # 角色属性
    tags = Column(JSON, comment="角色标签", default=list)
    description = Column(Text, comment="角色描述")
    abilities = Column(Text, comment="角色能力")
    power_system = Column(String(100), comment="力量体系")
    original_world = Column(String(100), comment="原生世界名")
    
    # 模板标识
    is_template = Column(Boolean, default=False, comment="是否为模板角色")
    
    # 关系定义
    user = relationship("User", back_populates="characters")
    novel = relationship("Novel", back_populates="characters", foreign_keys=[novel_id])
    worldview = relationship("Worldview", back_populates="characters", foreign_keys=[worldview_id])
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "gender": self.gender,
            "personality": self.personality,
            "character_type": self.character_type,
            "novel_id": self.novel_id,
            "worldview_id": self.worldview_id,
            "faction_id": self.faction_id,
            "tags": self.tags or [],
            "description": self.description,
            "abilities": self.abilities,
            "power_system": self.power_system,
            "original_world": self.original_world,
            "is_template": self.is_template,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "user_id": self.user_id
        }
    
    def to_summary_dict(self) -> dict:
        """转换为摘要字典，用于API响应"""
        return {
            "id": self.id,
            "name": self.name,
            "gender": self.gender,
            "character_type": self.character_type,
            "tags": self.tags or [],
            "description": self.description[:100] + "..." if self.description and len(self.description) > 100 else self.description,
            "is_template": self.is_template
        }
    
    def update_from_dict(self, data: dict) -> None:
        """从字典更新数据"""
        updatable_fields = [
            "name", "gender", "personality", "character_type",
            "worldview_id", "faction_id", "tags", "description",
            "abilities", "power_system", "original_world", "is_template"
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(self, field, data[field])
    
    @property
    def tag_list(self) -> list:
        """获取标签列表"""
        return self.tags if self.tags else []
    
    def add_tag(self, tag: str) -> None:
        """添加标签"""
        if not self.tags:
            self.tags = []
        if tag not in self.tags:
            self.tags.append(tag)
    
    def remove_tag(self, tag: str) -> None:
        """移除标签"""
        if self.tags and tag in self.tags:
            self.tags.remove(tag)
    
    def __repr__(self):
        return f"<Character(id={self.id}, name='{self.name}', type='{self.character_type}')>"