"""
小说基础模型
Author: AI Writer Team
Created: 2025-06-01
"""

from typing import Optional, List
from sqlalchemy import Column, String, Integer, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum

from app.models.base import Base


class NovelStatus(str, enum.Enum):
    """小说状态枚举"""
    DRAFT = "draft"          # 草稿
    WRITING = "writing"      # 创作中
    COMPLETED = "completed"  # 已完成
    PUBLISHED = "published"  # 已发布
    ARCHIVED = "archived"    # 已归档


class NovelGenre(str, enum.Enum):
    """小说类型枚举"""
    FANTASY = "fantasy"           # 玄幻
    ROMANCE = "romance"           # 言情
    URBAN = "urban"               # 都市
    HISTORICAL = "historical"     # 历史
    SCIFI = "scifi"              # 科幻
    WUXIA = "wuxia"              # 武侠
    XIANXIA = "xianxia"          # 仙侠
    MILITARY = "military"         # 军事
    GAME = "game"                # 游戏
    SUSPENSE = "suspense"        # 悬疑
    OTHER = "other"              # 其他


class WritingStyle(str, enum.Enum):
    """写作风格枚举"""
    FIRST_PERSON = "first_person"    # 第一人称
    THIRD_PERSON = "third_person"    # 第三人称
    OMNISCIENT = "omniscient"        # 全知视角
    LIMITED = "limited"              # 限制视角


class TargetAudience(str, enum.Enum):
    """目标读者群体枚举"""
    GENERAL = "general"       # 大众
    MALE = "male"            # 男性向
    FEMALE = "female"        # 女性向
    YOUNG_ADULT = "young_adult"  # 青少年
    CHILDREN = "children"    # 儿童


class Novel(Base):
    """小说基础模型"""
    
    __tablename__ = "novels"
    
    # 基础信息
    title = Column(
        String(200), 
        nullable=False, 
        index=True,
        comment="小说标题"
    )
    genre = Column(
        SQLEnum(NovelGenre), 
        nullable=False,
        comment="小说类型"
    )
    author = Column(
        String(100), 
        nullable=False,
        comment="作者名"
    )
    description = Column(
        Text, 
        nullable=True,
        comment="小说简介"
    )
    
    # 创作设定
    target_words = Column(
        Integer, 
        default=100000, 
        nullable=False,
        comment="目标字数"
    )
    target_audience = Column(
        SQLEnum(TargetAudience), 
        default=TargetAudience.GENERAL,
        nullable=False,
        comment="目标读者群体"
    )
    writing_style = Column(
        SQLEnum(WritingStyle), 
        default=WritingStyle.THIRD_PERSON,
        nullable=False,
        comment="写作风格"
    )
    
    # 世界观设定
    worldview_count = Column(
        Integer, 
        default=1, 
        nullable=False,
        comment="世界观数量"
    )
    
    # 状态信息
    status = Column(
        SQLEnum(NovelStatus), 
        default=NovelStatus.DRAFT,
        nullable=False,
        comment="小说状态"
    )
    current_words = Column(
        Integer, 
        default=0, 
        nullable=False,
        comment="当前字数"
    )
    chapter_count = Column(
        Integer, 
        default=0, 
        nullable=False,
        comment="章节数量"
    )
    
    # 封面和标签
    cover_url = Column(
        String(255), 
        nullable=True,
        comment="封面URL"
    )
    tags = Column(
        Text, 
        nullable=True,
        comment="标签（JSON格式）"
    )
    
    # 外键关系
    user_id = Column(
        Integer, 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False,
        index=True,
        comment="用户ID"
    )
    
    # 关系映射
    user = relationship(
        "User",
        back_populates="novels"
    )
    
    # 新增关系映射
    characters = relationship(
        "Character",
        back_populates="novel",
        cascade="all, delete-orphan",
        foreign_keys="Character.novel_id"
    )
    
    worldviews = relationship(
        "Worldview",
        back_populates="novel",
        cascade="all, delete-orphan"
    )
    
    rough_outlines = relationship(
        "RoughOutline",
        back_populates="novel",
        cascade="all, delete-orphan"
    )
    
    detailed_outlines = relationship(
        "DetailedOutline",
        back_populates="novel",
        cascade="all, delete-orphan"
    )
    
    chapters = relationship(
        "Chapter",
        back_populates="novel",
        cascade="all, delete-orphan",
        order_by="Chapter.chapter_number"
    )
    
    def __repr__(self) -> str:
        """小说模型的字符串表示"""
        return f"<Novel(id={self.id}, title='{self.title}', author='{self.author}')>"
    
    def to_dict(self) -> dict:
        """
        转换为字典格式
        
        Returns:
            dict: 小说信息字典
        """
        return {
            "id": self.id,
            "title": self.title,
            "genre": self.genre.value if self.genre else None,
            "author": self.author,
            "description": self.description,
            "target_words": self.target_words,
            "target_audience": self.target_audience.value if self.target_audience else None,
            "writing_style": self.writing_style.value if self.writing_style else None,
            "worldview_count": self.worldview_count,
            "status": self.status.value if self.status else None,
            "current_words": self.current_words,
            "chapter_count": self.chapter_count,
            "cover_url": self.cover_url,
            "tags": self.tags,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def to_summary_dict(self) -> dict:
        """
        转换为摘要格式（用于列表显示）
        
        Returns:
            dict: 小说摘要信息
        """
        return {
            "id": self.id,
            "title": self.title,
            "genre": self.genre.value if self.genre else None,
            "author": self.author,
            "status": self.status.value if self.status else None,
            "current_words": self.current_words,
            "target_words": self.target_words,
            "chapter_count": self.chapter_count,
            "cover_url": self.cover_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    @property
    def progress_percentage(self) -> float:
        """写作进度百分比"""
        if self.target_words <= 0:
            return 0.0
        return min(100.0, (self.current_words / self.target_words) * 100)
    
    @property
    def is_completed(self) -> bool:
        """是否已完成"""
        return self.status == NovelStatus.COMPLETED
    
    @property
    def is_published(self) -> bool:
        """是否已发布"""
        return self.status == NovelStatus.PUBLISHED
    
    def update_word_count(self, word_count: int) -> None:
        """
        更新字数统计
        
        Args:
            word_count: 新的字数
        """
        self.current_words = word_count
    
    def increment_chapter_count(self) -> None:
        """增加章节数量"""
        self.chapter_count += 1
    
    def decrement_chapter_count(self) -> None:
        """减少章节数量"""
        if self.chapter_count > 0:
            self.chapter_count -= 1
    
    def set_status(self, status: NovelStatus) -> None:
        """
        设置小说状态
        
        Args:
            status: 新状态
        """
        self.status = status
    
    def mark_completed(self) -> None:
        """标记为已完成"""
        self.status = NovelStatus.COMPLETED
    
    def publish(self) -> None:
        """发布小说"""
        self.status = NovelStatus.PUBLISHED
    
    def archive(self) -> None:
        """归档小说"""
        self.status = NovelStatus.ARCHIVED
    
    def update_basic_info(self, **kwargs) -> None:
        """
        更新基础信息
        
        Args:
            **kwargs: 更新的字段
        """
        allowed_fields = {
            'title', 'genre', 'author', 'description', 
            'target_words', 'target_audience', 'writing_style',
            'cover_url', 'tags'
        }
        
        for field, value in kwargs.items():
            if field in allowed_fields and hasattr(self, field):
                setattr(self, field, value)