"""
角色模板扩展数据模型
Author: AI Assistant
Created: 2025-06-03
"""

from typing import Optional, List
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, Float, JSON, Table
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin
from app.models.character import Character


class CharacterTemplateDetail(Base, TimestampMixin):
    """角色模板详细信息表"""
    
    __tablename__ = "character_template_details"
    
    id = Column(Integer, primary_key=True, index=True)
    character_id = Column(Integer, ForeignKey("characters.id", ondelete="CASCADE"), unique=True, nullable=False, comment="关联角色ID")
    
    # 详细描述信息
    detailed_description = Column(Text, comment="详细描述")
    background_story = Column(Text, comment="背景故事")
    relationships = Column(Text, comment="人际关系")
    strengths = Column(JSON, comment="优势特点", default=list)
    weaknesses = Column(JSON, comment="弱点缺陷", default=list)
    motivation = Column(Text, comment="动机目标")
    character_arc = Column(Text, comment="角色发展弧")
    dialogue_style = Column(Text, comment="对话风格")
    
    # 外观描述
    appearance = Column(JSON, comment="外貌描述", default=dict)
    
    # 战斗相关
    combat_style = Column(Text, comment="战斗风格")
    equipment = Column(JSON, comment="装备道具", default=list)
    special_abilities = Column(JSON, comment="特殊能力", default=list)
    
    # 统计信息
    usage_count = Column(Integer, default=0, comment="使用次数")
    rating = Column(Float, default=0.0, comment="评分")
    is_popular = Column(Boolean, default=False, comment="是否热门")
    is_new = Column(Boolean, default=False, comment="是否新增")
    
    # 关系定义
    character = relationship("Character", back_populates="template_detail")
    usage_examples = relationship("UsageExample", back_populates="template_detail", cascade="all, delete-orphan")
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "character_id": self.character_id,
            "detailed_description": self.detailed_description,
            "background_story": self.background_story,
            "relationships": self.relationships,
            "strengths": self.strengths or [],
            "weaknesses": self.weaknesses or [],
            "motivation": self.motivation,
            "character_arc": self.character_arc,
            "dialogue_style": self.dialogue_style,
            "appearance": self.appearance or {},
            "combat_style": self.combat_style,
            "equipment": self.equipment or [],
            "special_abilities": self.special_abilities or [],
            "usage_count": self.usage_count,
            "rating": self.rating,
            "is_popular": self.is_popular,
            "is_new": self.is_new
        }
    
    def update_from_dict(self, data: dict) -> None:
        """从字典更新数据"""
        updatable_fields = [
            "detailed_description", "background_story", "relationships", "strengths",
            "weaknesses", "motivation", "character_arc", "dialogue_style", 
            "appearance", "combat_style", "equipment", "special_abilities",
            "usage_count", "rating", "is_popular", "is_new"
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(self, field, data[field])


class UsageExample(Base, TimestampMixin):
    """角色模板使用示例表"""
    
    __tablename__ = "character_usage_examples"
    
    id = Column(Integer, primary_key=True, index=True)
    template_detail_id = Column(Integer, ForeignKey("character_template_details.id", ondelete="CASCADE"), nullable=False, comment="关联模板详情ID")
    
    novel_genre = Column(String(100), comment="小说类型")
    usage_context = Column(Text, comment="使用场景")
    adaptation_notes = Column(Text, comment="适配说明")
    
    # 关系定义
    template_detail = relationship("CharacterTemplateDetail", back_populates="usage_examples")
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "template_detail_id": self.template_detail_id,
            "novel_genre": self.novel_genre,
            "usage_context": self.usage_context,
            "adaptation_notes": self.adaptation_notes
        }


class CharacterTemplateFavorite(Base, TimestampMixin):
    """角色模板收藏表"""
    
    __tablename__ = "character_template_favorites"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, comment="用户ID")
    character_id = Column(Integer, ForeignKey("characters.id", ondelete="CASCADE"), nullable=False, comment="角色模板ID")
    
    # 关系定义
    user = relationship("User", back_populates="character_favorites")
    character_template = relationship("Character")
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "character_id": self.character_id
        }


class CharacterTemplateUsage(Base, TimestampMixin):
    """角色模板使用记录表"""
    
    __tablename__ = "character_template_usages"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, comment="用户ID")
    template_id = Column(Integer, ForeignKey("characters.id", ondelete="CASCADE"), nullable=False, comment="模板角色ID")
    target_id = Column(Integer, ForeignKey("characters.id", ondelete="SET NULL"), nullable=True, comment="生成的目标角色ID")
    novel_id = Column(Integer, ForeignKey("novels.id", ondelete="CASCADE"), nullable=False, comment="使用的小说ID")
    
    customizations = Column(JSON, comment="自定义修改", default=dict)
    adaptation_notes = Column(Text, comment="适配说明")
    
    # 关系定义
    user = relationship("User", back_populates="template_usages")
    template = relationship("Character", foreign_keys=[template_id])
    target = relationship("Character", foreign_keys=[target_id])
    novel = relationship("Novel")
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "template_id": self.template_id,
            "target_id": self.target_id,
            "novel_id": self.novel_id,
            "customizations": self.customizations or {},
            "adaptation_notes": self.adaptation_notes,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }