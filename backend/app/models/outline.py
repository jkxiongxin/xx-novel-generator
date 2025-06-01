"""
大纲数据模型
Author: AI Assistant
Created: 2025-06-01
"""

import enum
from typing import Optional
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr

from app.models.base import Base, TimestampMixin, UserOwnedMixin


class OutlineType(str, enum.Enum):
    """大纲类型枚举"""
    STORYLINE = "storyline"              # 故事线
    CHARACTER_GROWTH = "character_growth" # 角色成长路线
    MAJOR_EVENT = "major_event"          # 重大事件
    PLOT_POINT = "plot_point"            # 大情节点


class RoughOutline(Base, TimestampMixin, UserOwnedMixin):
    """粗略大纲表"""
    
    __tablename__ = "rough_outlines"
    
    # 基础信息
    id = Column(Integer, primary_key=True, index=True)
    novel_id = Column(Integer, ForeignKey("novels.id", ondelete="CASCADE"), nullable=False, comment="小说ID")
    outline_type = Column(String(50), nullable=False, comment="大纲类型")
    title = Column(String(200), nullable=False, comment="标题")
    content = Column(Text, nullable=False, comment="内容描述")
    order_index = Column(Integer, default=0, comment="排序索引")
    
    # 大情节点特有字段
    start_chapter = Column(Integer, comment="开始章节数")
    end_chapter = Column(Integer, comment="结束章节数")
    
    # 关系定义
    novel = relationship("Novel", back_populates="rough_outlines")
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "novel_id": self.novel_id,
            "outline_type": self.outline_type,
            "title": self.title,
            "content": self.content,
            "order_index": self.order_index,
            "start_chapter": self.start_chapter,
            "end_chapter": self.end_chapter,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "user_id": self.user_id
        }
    
    def update_from_dict(self, data: dict) -> None:
        """从字典更新数据"""
        updatable_fields = [
            "title", "content", "order_index", "start_chapter", "end_chapter"
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(self, field, data[field])
    
    def __repr__(self):
        return f"<RoughOutline(id={self.id}, type='{self.outline_type}', title='{self.title}')>"


class DetailedOutline(Base, TimestampMixin, UserOwnedMixin):
    """详细大纲表"""
    
    __tablename__ = "detailed_outlines"
    
    # 基础信息
    id = Column(Integer, primary_key=True, index=True)
    novel_id = Column(Integer, ForeignKey("novels.id", ondelete="CASCADE"), nullable=False, comment="小说ID")
    chapter_number = Column(Integer, nullable=False, comment="章节号")
    chapter_title = Column(String(200), comment="章节标题")
    
    # 章节内容描述
    plot_points = Column(Text, nullable=False, comment="章节情节点")
    participating_characters = Column(JSON, comment="参与角色ID列表", default=list)
    entering_characters = Column(JSON, comment="入场角色ID列表", default=list)
    exiting_characters = Column(JSON, comment="离场角色ID列表", default=list)
    chapter_summary = Column(Text, comment="章节简介")
    
    # 剧情标识
    is_plot_end = Column(Boolean, default=False, comment="是否剧情结束")
    is_new_plot = Column(Boolean, default=False, comment="是否新剧情开始")
    new_plot_summary = Column(Text, comment="新剧情简介")
    
    # 关系定义
    novel = relationship("Novel", back_populates="detailed_outlines")
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "novel_id": self.novel_id,
            "chapter_number": self.chapter_number,
            "chapter_title": self.chapter_title,
            "plot_points": self.plot_points,
            "participating_characters": self.participating_characters or [],
            "entering_characters": self.entering_characters or [],
            "exiting_characters": self.exiting_characters or [],
            "chapter_summary": self.chapter_summary,
            "is_plot_end": self.is_plot_end,
            "is_new_plot": self.is_new_plot,
            "new_plot_summary": self.new_plot_summary,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "user_id": self.user_id
        }
    
    def update_from_dict(self, data: dict) -> None:
        """从字典更新数据"""
        updatable_fields = [
            "chapter_title", "plot_points", "participating_characters",
            "entering_characters", "exiting_characters", "chapter_summary",
            "is_plot_end", "is_new_plot", "new_plot_summary"
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(self, field, data[field])
    
    @property
    def participating_character_ids(self) -> list:
        """获取参与角色ID列表"""
        return self.participating_characters if self.participating_characters else []
    
    @property
    def entering_character_ids(self) -> list:
        """获取入场角色ID列表"""
        return self.entering_characters if self.entering_characters else []
    
    @property
    def exiting_character_ids(self) -> list:
        """获取离场角色ID列表"""
        return self.exiting_characters if self.exiting_characters else []
    
    def add_participating_character(self, character_id: int) -> None:
        """添加参与角色"""
        if not self.participating_characters:
            self.participating_characters = []
        if character_id not in self.participating_characters:
            self.participating_characters.append(character_id)
    
    def add_entering_character(self, character_id: int) -> None:
        """添加入场角色"""
        if not self.entering_characters:
            self.entering_characters = []
        if character_id not in self.entering_characters:
            self.entering_characters.append(character_id)
    
    def add_exiting_character(self, character_id: int) -> None:
        """添加离场角色"""
        if not self.exiting_characters:
            self.exiting_characters = []
        if character_id not in self.exiting_characters:
            self.exiting_characters.append(character_id)
    
    def __repr__(self):
        return f"<DetailedOutline(id={self.id}, chapter={self.chapter_number}, title='{self.chapter_title}')>"