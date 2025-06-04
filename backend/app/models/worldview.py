"""
世界观数据模型
Author: AI Assistant
Created: 2025-06-01
Updated: 2025-06-03
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
    parent_region_id = Column(Integer, ForeignKey("world_maps.id", ondelete="CASCADE"), nullable=True, comment="父区域ID")
    level = Column(Integer, default=1, comment="层级")
    
    # 扩展字段（根据设计文档）
    climate = Column(String(200), comment="气候特征")
    terrain = Column(String(200), comment="地形特征")
    resources = Column(Text, comment="主要资源")
    population = Column(String(100), comment="人口情况")
    culture = Column(Text, comment="文化特色")
    
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
            "parent_region_id": self.parent_region_id,
            "level": self.level,
            "climate": self.climate,
            "terrain": self.terrain,
            "resources": self.resources,
            "population": self.population,
            "culture": self.culture,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "user_id": self.user_id
        }
    
    def update_from_dict(self, data: dict) -> None:
        """从字典更新数据"""
        updatable_fields = [
            "region_name", "description", "parent_region_id", "level",
            "climate", "terrain", "resources", "population", "culture"
        ]
        
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
    level_order = Column(Integer, nullable=False, comment="等级顺序")
    
    # 扩展字段（根据设计文档）
    cultivation_method = Column(Text, comment="修炼方法")
    required_resources = Column(Text, comment="所需资源")
    breakthrough_condition = Column(Text, comment="突破条件")
    power_description = Column(Text, comment="力量描述")
    
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
            "level_order": self.level_order,
            "cultivation_method": self.cultivation_method,
            "required_resources": self.required_resources,
            "breakthrough_condition": self.breakthrough_condition,
            "power_description": self.power_description,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "user_id": self.user_id
        }
    
    def update_from_dict(self, data: dict) -> None:
        """从字典更新数据"""
        updatable_fields = [
            "system_name", "level_name", "description", "level_order",
            "cultivation_method", "required_resources", "breakthrough_condition", "power_description"
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
    time_period = Column(String(100), comment="时间段")
    time_order = Column(Integer, nullable=False, comment="时间顺序")
    event_type = Column(String(50), comment="事件类型")
    description = Column(Text, nullable=False, comment="事件描述")
    
    # 扩展字段（根据设计文档）
    participants = Column(Text, comment="参与者")
    consequences = Column(Text, comment="后果影响")
    related_locations = Column(Text, comment="相关地点")
    
    # 关系定义
    user = relationship("User", back_populates="histories")
    worldview = relationship("Worldview", back_populates="histories")
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "worldview_id": self.worldview_id,
            "event_name": self.event_name,
            "time_period": self.time_period,
            "time_order": self.time_order,
            "event_type": self.event_type,
            "description": self.description,
            "participants": self.participants,
            "consequences": self.consequences,
            "related_locations": self.related_locations,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "user_id": self.user_id
        }
    
    def update_from_dict(self, data: dict) -> None:
        """从字典更新数据"""
        updatable_fields = [
            "event_name", "time_period", "time_order", "event_type", "description",
            "participants", "consequences", "related_locations"
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
    description = Column(Text, comment="组织描述")
    
    # 扩展字段（根据设计文档）
    leader = Column(String(100), comment="领导者")
    territory = Column(Text, comment="控制区域")
    power_level = Column(String(50), comment="势力等级")
    ideology = Column(Text, comment="理念目标")
    allies = Column(JSON, comment="盟友列表")
    enemies = Column(JSON, comment="敌对列表")
    member_count = Column(String(50), comment="成员数量")
    
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
            "description": self.description,
            "leader": self.leader,
            "territory": self.territory,
            "power_level": self.power_level,
            "ideology": self.ideology,
            "allies": self.allies,
            "enemies": self.enemies,
            "member_count": self.member_count,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "user_id": self.user_id
        }
    
    def update_from_dict(self, data: dict) -> None:
        """从字典更新数据"""
        updatable_fields = [
            "name", "faction_type", "description", "leader", "territory",
            "power_level", "ideology", "allies", "enemies", "member_count"
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(self, field, data[field])
    
    def __repr__(self):
        return f"<Faction(id={self.id}, name='{self.name}', type='{self.faction_type}')>"