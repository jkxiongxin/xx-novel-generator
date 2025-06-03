"""
脑洞生成器数据模型
Author: AI Writer Team
Created: 2025-06-03
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.base import Base


class BrainStormHistory(Base):
    """脑洞生成历史记录"""
    __tablename__ = "brain_storm_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    generation_id = Column(String(50), nullable=False, unique=True, index=True)
    
    # 生成参数
    topic = Column(String(200), nullable=False)
    creativity_level = Column(Integer, default=7)
    idea_count = Column(Integer, default=10)
    idea_types = Column(JSON, nullable=True)  # 存储选择的创意类型列表
    elements = Column(JSON, nullable=True)    # 存储选择的要素标签列表
    style = Column(String(100), nullable=True)
    language = Column(String(20), default="zh-CN")
    avoid_keywords = Column(JSON, nullable=True)
    reference_works = Column(JSON, nullable=True)
    
    # 生成结果统计
    ideas_generated = Column(Integer, default=0)
    generation_time = Column(Float, nullable=True)  # 生成耗时(秒)
    model_used = Column(String(100), nullable=True)
    prompt_tokens = Column(Integer, nullable=True)
    completion_tokens = Column(Integer, nullable=True)
    
    # 用户反馈
    rating = Column(Integer, nullable=True)  # 1-5星评分
    user_feedback = Column(Text, nullable=True)
    useful_ideas = Column(JSON, nullable=True)  # 用户标记的有用创意ID列表
    
    # 使用统计
    copied_count = Column(Integer, default=0)    # 复制次数
    exported_count = Column(Integer, default=0)  # 导出次数
    applied_count = Column(Integer, default=0)   # 应用次数
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = relationship("User", back_populates="brain_storm_history")
    ideas = relationship("BrainStormIdea", back_populates="history", cascade="all, delete-orphan")


class BrainStormIdea(Base):
    """脑洞创意"""
    __tablename__ = "brain_storm_ideas"
    
    id = Column(Integer, primary_key=True, index=True)
    history_id = Column(Integer, ForeignKey("brain_storm_history.id"), nullable=False, index=True)
    idea_id = Column(String(50), nullable=False)  # 在一次生成中的唯一ID
    
    # 创意内容
    content = Column(Text, nullable=False)
    idea_type = Column(String(50), nullable=True)  # plot, character, worldview, mixed
    summary = Column(String(500), nullable=True)
    potential_development = Column(Text, nullable=True)
    
    # 评分和标签
    creativity_score = Column(Float, nullable=True)   # AI评估的创意评分
    practical_score = Column(Float, nullable=True)    # AI评估的实用性评分
    tags = Column(JSON, nullable=True)                # 相关标签
    related_elements = Column(JSON, nullable=True)    # 相关要素
    
    # 用户操作记录
    copied_times = Column(Integer, default=0)      # 被复制次数
    user_rating = Column(Integer, nullable=True)   # 用户评分 1-5
    is_favorite = Column(Boolean, default=False)   # 是否收藏
    user_notes = Column(Text, nullable=True)       # 用户备注
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    history = relationship("BrainStormHistory", back_populates="ideas")


class BrainStormPreferences(Base):
    """用户脑洞生成偏好设置"""
    __tablename__ = "brain_storm_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    
    # 默认参数设置
    default_creativity_level = Column(Integer, default=7)
    default_idea_count = Column(Integer, default=10)
    preferred_types = Column(JSON, nullable=True)      # 偏好的创意类型
    favorite_elements = Column(JSON, nullable=True)    # 常用要素标签
    default_style = Column(String(100), nullable=True)
    
    # 功能偏好
    auto_save_history = Column(Boolean, default=True)
    enable_notifications = Column(Boolean, default=True)
    show_creativity_scores = Column(Boolean, default=True)
    enable_auto_suggestions = Column(Boolean, default=True)
    
    # 界面偏好
    preferred_layout = Column(String(50), default="grid")  # grid, list
    items_per_page = Column(Integer, default=20)
    enable_dark_mode = Column(Boolean, default=False)
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = relationship("User", back_populates="brain_storm_preferences")


class BrainStormElements(Base):
    """脑洞生成要素库"""
    __tablename__ = "brain_storm_elements"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 要素信息
    name = Column(String(100), nullable=False, unique=True)
    display_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=False, index=True)  # 要素分类
    
    # 统计信息
    usage_count = Column(Integer, default=0)           # 使用次数
    effectiveness_score = Column(Float, default=0.0)   # 效果评分
    success_rate = Column(Float, default=0.0)          # 成功率
    
    # 关联信息
    related_elements = Column(JSON, nullable=True)     # 相关要素
    compatible_types = Column(JSON, nullable=True)     # 兼容的创意类型
    example_usage = Column(Text, nullable=True)        # 使用示例
    
    # 状态
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)       # 是否推荐要素
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class BrainStormTopicSuggestion(Base):
    """主题建议"""
    __tablename__ = "brain_storm_topic_suggestions"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 主题信息
    topic = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=False, index=True)
    
    # 统计信息
    popularity = Column(Integer, default=0)            # 热度评分
    usage_count = Column(Integer, default=0)           # 使用次数
    success_rate = Column(Float, default=0.0)          # 成功率
    expected_ideas = Column(Integer, default=10)       # 预期生成创意数
    
    # 关联信息
    related_topics = Column(JSON, nullable=True)       # 相关主题
    sample_ideas = Column(JSON, nullable=True)         # 示例创意
    recommended_elements = Column(JSON, nullable=True) # 推荐要素
    
    # 状态
    is_active = Column(Boolean, default=True)
    is_trending = Column(Boolean, default=False)       # 是否热门
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)