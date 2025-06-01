"""
章节数据模型
Author: AI Assistant  
Created: 2025-06-01
"""

import enum
from typing import Optional
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr

from app.models.base import Base, TimestampMixin, UserOwnedMixin


class ChapterStatus(str, enum.Enum):
    """章节状态枚举"""
    DRAFT = "draft"           # 草稿
    COMPLETED = "completed"   # 已完成
    PUBLISHED = "published"   # 已发布


class Chapter(Base, TimestampMixin, UserOwnedMixin):
    """章节表"""
    
    __tablename__ = "chapters"
    
    # 基础信息
    id = Column(Integer, primary_key=True, index=True)
    novel_id = Column(Integer, ForeignKey("novels.id", ondelete="CASCADE"), nullable=False, comment="小说ID")
    title = Column(String(200), nullable=False, comment="章节标题")
    content = Column(Text, comment="章节内容")
    chapter_number = Column(Integer, nullable=False, comment="章节序号")
    word_count = Column(Integer, default=0, comment="字数统计")
    status = Column(String(20), default=ChapterStatus.DRAFT, comment="状态")
    
    # 关联信息
    outline_id = Column(Integer, ForeignKey("detailed_outlines.id", ondelete="SET NULL"), nullable=True, comment="关联大纲ID")
    character_ids = Column(JSON, comment="关联角色ID列表", default=list)
    
    # 版本控制
    version = Column(Integer, default=1, comment="版本号")
    notes = Column(Text, comment="作者备注")
    
    # 关系定义
    user = relationship("User", back_populates="chapters")
    novel = relationship("Novel", back_populates="chapters", foreign_keys=[novel_id])
    outline = relationship("DetailedOutline", foreign_keys=[outline_id])
    
    # 添加数据库索引
    __table_args__ = (
        Index('idx_chapter_novel_number', 'novel_id', 'chapter_number', unique=True),
        Index('idx_chapter_novel_status', 'novel_id', 'status'),
        Index('idx_chapter_user_novel', 'user_id', 'novel_id'),
        Index('idx_chapter_outline', 'outline_id'),
    )
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "novel_id": self.novel_id,
            "title": self.title,
            "content": self.content,
            "chapter_number": self.chapter_number,
            "word_count": self.word_count,
            "status": self.status,
            "outline_id": self.outline_id,
            "character_ids": self.character_ids or [],
            "version": self.version,
            "notes": self.notes,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "user_id": self.user_id
        }
    
    def to_summary_dict(self) -> dict:
        """转换为摘要字典，用于列表显示"""
        return {
            "id": self.id,
            "novel_id": self.novel_id,
            "title": self.title,
            "chapter_number": self.chapter_number,
            "word_count": self.word_count,
            "status": self.status,
            "version": self.version,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    def update_from_dict(self, data: dict) -> None:
        """从字典更新数据"""
        updatable_fields = [
            "title", "content", "chapter_number", "status", 
            "outline_id", "character_ids", "notes"
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(self, field, data[field])
        
        # 更新字数统计
        if "content" in data and data["content"]:
            self.update_word_count()
    
    def update_word_count(self) -> None:
        """更新字数统计"""
        if self.content:
            # 简单的字数统计，去除空白字符
            self.word_count = len(self.content.replace(' ', '').replace('\n', '').replace('\t', ''))
        else:
            self.word_count = 0
    
    @property
    def character_id_list(self) -> list:
        """获取关联角色ID列表"""
        return self.character_ids if self.character_ids else []
    
    def add_character(self, character_id: int) -> None:
        """添加关联角色"""
        if not self.character_ids:
            self.character_ids = []
        if character_id not in self.character_ids:
            self.character_ids.append(character_id)
    
    def remove_character(self, character_id: int) -> None:
        """移除关联角色"""
        if self.character_ids and character_id in self.character_ids:
            self.character_ids.remove(character_id)
    
    def increment_version(self) -> None:
        """增加版本号"""
        self.version += 1
    
    def is_draft(self) -> bool:
        """是否为草稿状态"""
        return self.status == ChapterStatus.DRAFT
    
    def is_completed(self) -> bool:
        """是否已完成"""
        return self.status == ChapterStatus.COMPLETED
    
    def is_published(self) -> bool:
        """是否已发布"""
        return self.status == ChapterStatus.PUBLISHED
    
    def mark_completed(self) -> None:
        """标记为已完成"""
        self.status = ChapterStatus.COMPLETED
    
    def mark_published(self) -> None:
        """标记为已发布"""
        self.status = ChapterStatus.PUBLISHED
    
    def mark_draft(self) -> None:
        """标记为草稿"""
        self.status = ChapterStatus.DRAFT
    
    def get_content_preview(self, length: int = 200) -> str:
        """获取内容预览"""
        if not self.content:
            return ""
        if len(self.content) <= length:
            return self.content
        return self.content[:length] + "..."
    
    def __repr__(self):
        return f"<Chapter(id={self.id}, novel_id={self.novel_id}, number={self.chapter_number}, title='{self.title}')>"