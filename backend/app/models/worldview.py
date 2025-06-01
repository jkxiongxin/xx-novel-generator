"""
世界观数据模型
Author: AI Assistant
Created: 2025-06-01
"""

import enum
from typing import Optional
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr

from app.models.base import Base, TimestampMixin, UserOwnedMixin


class Worldview(Base, TimestampMixin, UserOwnedMixin):
    """世界观主表"""
    
    __tablename__ = "worldviews"
    
    # 基础信息
    id = Column(Integer, primary_key=True, index=True)
    novel_id = Column(Integer, ForeignKey("novels.id", ondelete="CASCADE"), nullable=False, comment="小说ID")
    name = Column(String(100), nullable=False, comment="世界名称")
    description = Column(Text, comment="世界描述")
    is_primary = Column(Boolean, default=False, comment="是否主世界")
    
    # 关系定义
    user = relationship("User", back_populates="worldviews")
    novel = relationship("Novel", back_populates="worldviews")
    characters = relationship("Character", back_populates="worldview", foreign_keys="Character.worldview_id")
    world_maps = relationship("WorldMap", back_populates="worldview", cascade="all, delete-orphan")
    cultivation_systems = relationship("CultivationSystem", back_populates="worldview", cascade="all, delete-orphan")
    histories = relationship("History", back_populates="worldview", cascade="all, delete-orphan")
    factions = relationship("Faction", back_populates="worldview", cascade="all, delete-orphan")
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "novel_id": self.novel_id,
            "name": self.name,
            "description": self.description,
            "is_primary": self.is_primary,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "user_id": self.user_id
        }
    
    def update_from_dict(self, data: dict) -> None:
        """从字典更新数据"""
        updatable_fields = ["name", "description", "is_primary"]
        
        for field in updatable_fields:
            if field in data:
                setattr(self, field, data[field])
    
    def __repr__(self):
        return f"<Worldview(id={self.id}, name='{self.name}', primary={self.is_primary})>"


class WorldMap(Base, TimestampMixin, UserOwnedMixin):
    """世界地图"""
    
    __tablename__ = "world_maps"
    
    # 基础信息
    id = Column(Integer, primary_key=True, index=True)
    worldview_id = Column(Integer, ForeignKey("worldviews.id", ondelete="CASCADE"), nullable=False, comment="世界观ID")
    region_name = Column(String(100), nullable=False, comment="区域名称")
    description = Column(Text, nullable=False, comment="区域描述")
    parent_id = Column(Integer, ForeignKey("world_maps.id", ondelete="CASCADE"), nullable=True, comment="父区域ID")
    level = Column(Integer, default=1, comment="层级")
    
    # 关系定义
    user = relationship("User", back_populates="world_maps")
    worldview = relationship("Worldview", back_populates="world_maps")
    parent = relationship("WorldMap", remote_side=[id], back_populates="children")
    children = relationship("WorldMap", back_populates="parent", cascade="all, delete-orphan")
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "worldview_id": self.worldview_id,
            "region_name": self.region_name,
            "description": self.description,
            "parent_id": self.parent_id,
            "level": self.level,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "user_id": self.user_id
        }
    
    def update_from_dict(self, data: dict) -> None:
        """从字典更新数据"""
        updatable_fields = ["region_name", "description", "parent_id", "level"]
        
        for field in updatable_fields:
            if field in data:
                setattr(self, field, data[field])
    
    def __repr__(self):
        return f"<WorldMap(id={self.id}, name='{self.region_name}', level={self.level})>"


class CultivationSystem(Base, TimestampMixin, UserOwnedMixin):
    """修炼体系"""
    
    __tablename__ = "cultivation_systems"
    
    # 基础信息
    id = Column(Integer, primary_key=True, index=True)
    worldview_id = Column(Integer, ForeignKey("worldviews.id", ondelete="CASCADE"), nullable=False, comment="世界观ID")
    system_name = Column(String(100), nullable=False, comment="体系名称")
    level_name = Column(String(100), nullable=False, comment="等级名称")
    description = Column(Text, nullable=False, comment="等级描述")
    cultivation_method = Column(Text, comment="修炼方法")
    required_resources = Column(Text, comment="所需资源")
    level_order = Column(Integer, nullable=False, comment="等级顺序")
    
    # 关系定义
    user = relationship("User", back_populates="cultivation_systems")
    worldview = relationship("Worldview", back_populates="cultivation_systems")
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "worldview_id": self.worldview_id,
            "system_name": self.system_name,
            "level_name": self.level_name,
            "description": self.description,
            "cultivation_method": self.cultivation_method,
            "required_resources": self.required_resources,
            "level_order": self.level_order,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "user_id": self.user_id
        }
    
    def update_from_dict(self, data: dict) -> None:
        """从字典更新数据"""
        updatable_fields = [
            "system_name", "level_name", "description", "cultivation_method",
            "required_resources", "level_order"
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(self, field, data[field])
    
    def __repr__(self):
        return f"<CultivationSystem(id={self.id}, system='{self.system_name}', level='{self.level_name}')>"


class History(Base, TimestampMixin, UserOwnedMixin):
    """历史事件"""
    
    __tablename__ = "histories"
    
    # 基础信息
    id = Column(Integer, primary_key=True, index=True)
    worldview_id = Column(Integer, ForeignKey("worldviews.id", ondelete="CASCADE"), nullable=False, comment="世界观ID")
    event_name = Column(String(200), nullable=False, comment="事件名称")
    dynasty_name = Column(String(100), comment="朝代名称")
    background = Column(Text, nullable=False, comment="历史背景")
    important_events = Column(Text, comment="重要事件")
    impact_description = Column(Text, comment="影响描述")
    time_order = Column(Integer, nullable=False, comment="时间顺序")
    
    # 关系定义
    user = relationship("User", back_populates="histories")
    worldview = relationship("Worldview", back_populates="histories")
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "worldview_id": self.worldview_id,
            "event_name": self.event_name,
            "dynasty_name": self.dynasty_name,
            "background": self.background,
            "important_events": self.important_events,
            "impact_description": self.impact_description,
            "time_order": self.time_order,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "user_id": self.user_id
        }
    
    def update_from_dict(self, data: dict) -> None:
        """从字典更新数据"""
        updatable_fields = [
            "event_name", "dynasty_name", "background", "important_events",
            "impact_description", "time_order"
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(self, field, data[field])
    
    def __repr__(self):
        return f"<History(id={self.id}, event='{self.event_name}', order={self.time_order})>"


class Faction(Base, TimestampMixin, UserOwnedMixin):
    """阵营势力"""
    
    __tablename__ = "factions"
    
    # 基础信息
    id = Column(Integer, primary_key=True, index=True)
    worldview_id = Column(Integer, ForeignKey("worldviews.id", ondelete="CASCADE"), nullable=False, comment="世界观ID")
    name = Column(String(100), nullable=False, comment="阵营名称")
    faction_type = Column(String(50), nullable=False, comment="类型：阵营/势力/组织")
    organization_structure = Column(Text, comment="组织架构")
    territory = Column(Text, comment="势力范围")
    ideology = Column(Text, comment="理念目标")
    important_figures = Column(Text, comment="重要人物")
    
    # 关系定义
    user = relationship("User", back_populates="factions")
    worldview = relationship("Worldview", back_populates="factions")
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "worldview_id": self.worldview_id,
            "name": self.name,
            "faction_type": self.faction_type,
            "organization_structure": self.organization_structure,
            "territory": self.territory,
            "ideology": self.ideology,
            "important_figures": self.important_figures,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "user_id": self.user_id
        }
    
    def update_from_dict(self, data: dict) -> None:
        """从字典更新数据"""
        updatable_fields = [
            "name", "faction_type", "organization_structure", "territory",
            "ideology", "important_figures"
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(self, field, data[field])
    
    def __repr__(self):
        return f"<Faction(id={self.id}, name='{self.name}', type='{self.faction_type}')>"