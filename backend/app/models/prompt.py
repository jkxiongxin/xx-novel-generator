"""
提示词模板数据模型
Author: AI Writer Team
Created: 2025-06-01
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Enum
from sqlalchemy.sql import func
import enum

from app.models.base import Base


class PromptType(str, enum.Enum):
    """提示词类型枚举"""
    NOVEL_NAME = "novel_name"          # 小说名生成
    NOVEL_IDEA = "novel_idea"          # 小说创意生成
    BRAIN_STORM = "brain_storm"        # 脑洞生成器
    WORLD_VIEW = "world_view"          # 世界观生成
    ROUGH_OUTLINE = "rough_outline"    # 粗略大纲生成
    DETAIL_OUTLINE = "detail_outline"  # 细致大纲生成
    CHARACTER = "character"            # 角色生成
    CHAPTER = "chapter"                # 章节内容生成


class Prompt(Base):
    """提示词模板模型"""
    
    __tablename__ = "prompts"
    
    name = Column(String(200), nullable=False, comment="提示词名称")
    type = Column(Enum(PromptType), nullable=False, comment="提示词类型")
    template = Column(Text, nullable=False, comment="提示词模板内容")
    description = Column(Text, comment="提示词描述")
    
    # 配置参数
    default_max_tokens = Column(Integer, default=2000, comment="默认最大token数")
    default_temperature = Column(Integer, default=70, comment="默认温度值(0-100)")
    
    # 响应格式配置
    response_format = Column(Text, comment="期望的响应格式(JSON)")
    
    # 状态和版本
    is_active = Column(Boolean, default=True, comment="是否启用")
    version = Column(String(20), default="1.0", comment="版本号")
    
    def __repr__(self):
        return f"<Prompt(id={self.id}, name='{self.name}', type='{self.type}')>"