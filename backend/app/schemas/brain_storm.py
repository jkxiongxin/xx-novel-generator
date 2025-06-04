"""
脑洞生成器数据模式
Author: AI Writer Team
Created: 2025-06-03
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator


class BrainStormRequest(BaseModel):
    """脑洞生成请求"""
    topic: str = Field(..., description="主题关键词", max_length=200)
    creativity_level: Optional[int] = Field(7, description="创意程度 1-10", ge=1, le=10)
    idea_count: Optional[int] = Field(10, description="生成数量", ge=1, le=20)
    idea_type: Optional[List[str]] = Field(None, description="创意类型", example=["plot", "character", "worldview"])
    elements: Optional[List[str]] = Field(None, description="要素标签", example=["玄幻", "科幻", "爱情"])
    style: Optional[str] = Field(None, description="生成风格", max_length=100)
    language: Optional[str] = Field("zh-CN", description="语言")
    avoid_keywords: Optional[List[str]] = Field(None, description="避免的关键词")
    reference_works: Optional[List[str]] = Field(None, description="参考作品")
    user_input: Optional[str] = Field(None, description="用户想法描述", max_length=1000)
    max_tokens: Optional[int] = Field(None, description="最大token数", ge=1, le=30000)
    temperature: Optional[int] = Field(None, description="温度值(0-100)", ge=0, le=100)

    @validator('idea_type')
    def validate_idea_type(cls, v):
        if v is not None:
            valid_types = ['plot', 'character', 'worldview', 'mixed']
            for t in v:
                if t not in valid_types:
                    raise ValueError(f'无效的创意类型: {t}')
        return v


class GeneratedIdea(BaseModel):
    """生成的创意"""
    id: str = Field(..., description="创意ID")
    content: str = Field(..., description="创意内容")
    type: str = Field(..., description="创意类型")
    tags: List[str] = Field(default=[], description="相关标签")
    creativity_score: Optional[float] = Field(None, description="创意评分")
    practical_score: Optional[float] = Field(None, description="实用性评分")
    summary: Optional[str] = Field(None, description="简要总结")
    potential_development: Optional[str] = Field(None, description="发展潜力描述")
    related_elements: List[str] = Field(default=[], description="相关要素")


class BrainStormResponse(BaseModel):
    """脑洞生成响应"""
    success: bool = Field(..., description="是否成功")
    ideas: List[GeneratedIdea] = Field(..., description="生成的创意列表")
    generation_id: str = Field(..., description="生成ID")
    metadata: Dict[str, Any] = Field(..., description="生成元数据")


class BrainStormHistoryItem(BaseModel):
    """历史记录项"""
    id: int = Field(..., description="记录ID")
    generation_id: str = Field(..., description="生成ID")
    topic: str = Field(..., description="主题")
    creativity_level: int = Field(..., description="创意程度")
    idea_count: int = Field(..., description="生成数量")
    ideas_generated: int = Field(..., description="实际生成数量")
    generation_time: Optional[float] = Field(None, description="生成耗时")
    rating: Optional[int] = Field(None, description="用户评分")
    created_at: datetime = Field(..., description="创建时间")

    class Config:
        from_attributes = True


class BrainStormHistoryResponse(BaseModel):
    """历史记录响应"""
    history: List[BrainStormHistoryItem] = Field(..., description="历史记录列表")
    total: int = Field(..., description="总数")
    limit: int = Field(..., description="限制数量")
    offset: int = Field(..., description="偏移量")


class BrainStormHistoryDetail(BaseModel):
    """历史记录详情"""
    history: BrainStormHistoryItem = Field(..., description="历史记录")
    ideas: List[GeneratedIdea] = Field(..., description="创意列表")
    usage_stats: Dict[str, int] = Field(..., description="使用统计")


class ElementItem(BaseModel):
    """要素项"""
    name: str = Field(..., description="要素名称")
    description: str = Field(..., description="要素描述")
    usage_count: int = Field(..., description="使用次数")
    effectiveness_score: float = Field(..., description="效果评分")
    related_elements: List[str] = Field(default=[], description="相关要素")


class ElementCategory(BaseModel):
    """要素分类"""
    category: str = Field(..., description="分类名称")
    display_name: str = Field(..., description="显示名称")
    elements: List[ElementItem] = Field(..., description="要素列表")


class ElementSuggestionsResponse(BaseModel):
    """要素建议响应"""
    categories: List[ElementCategory] = Field(..., description="分类列表")


class TopicSuggestion(BaseModel):
    """主题建议"""
    topic: str = Field(..., description="主题")
    description: str = Field(..., description="描述")
    popularity: int = Field(..., description="热度")
    expected_ideas: int = Field(..., description="预期生成创意数")
    related_topics: List[str] = Field(default=[], description="相关主题")
    sample_ideas: List[str] = Field(default=[], description="示例创意")


class TopicSuggestionsResponse(BaseModel):
    """主题建议响应"""
    suggestions: List[TopicSuggestion] = Field(..., description="建议列表")


class GenerationStats(BaseModel):
    """生成统计"""
    total_generations: int = Field(..., description="总生成次数")
    total_ideas: int = Field(..., description="总创意数")
    average_ideas_per_generation: float = Field(..., description="平均每次生成创意数")
    most_popular_elements: List[str] = Field(..., description="最受欢迎要素")
    creativity_distribution: List[Dict[str, int]] = Field(..., description="创意程度分布")
    usage_trends: List[Dict[str, Any]] = Field(..., description="使用趋势")


class UserPreferences(BaseModel):
    """用户偏好"""
    default_creativity_level: int = Field(7, description="默认创意程度")
    default_idea_count: int = Field(10, description="默认生成数量")
    preferred_types: List[str] = Field(default=[], description="偏好类型")
    favorite_elements: List[str] = Field(default=[], description="常用要素")
    default_style: Optional[str] = Field(None, description="默认风格")
    auto_save_history: bool = Field(True, description="自动保存历史")
    enable_notifications: bool = Field(True, description="启用通知")
    show_creativity_scores: bool = Field(True, description="显示创意评分")
    enable_auto_suggestions: bool = Field(True, description="启用自动建议")
    preferred_layout: str = Field("grid", description="偏好布局")
    items_per_page: int = Field(20, description="每页项目数")
    enable_dark_mode: bool = Field(False, description="启用暗色模式")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    class Config:
        from_attributes = True


class SavePreferencesRequest(BaseModel):
    """保存偏好请求"""
    default_creativity_level: Optional[int] = Field(None, ge=1, le=10)
    default_idea_count: Optional[int] = Field(None, ge=1, le=20)
    preferred_types: Optional[List[str]] = Field(None)
    favorite_elements: Optional[List[str]] = Field(None)
    default_style: Optional[str] = Field(None, max_length=100)
    auto_save_history: Optional[bool] = Field(None)
    enable_notifications: Optional[bool] = Field(None)
    show_creativity_scores: Optional[bool] = Field(None)
    enable_auto_suggestions: Optional[bool] = Field(None)
    preferred_layout: Optional[str] = Field(None)
    items_per_page: Optional[int] = Field(None, ge=5, le=100)
    enable_dark_mode: Optional[bool] = Field(None)


class SavePreferencesResponse(BaseModel):
    """保存偏好响应"""
    success: bool = Field(..., description="是否成功")
    preferences: UserPreferences = Field(..., description="偏好设置")


class RateGenerationRequest(BaseModel):
    """评价生成请求"""
    rating: int = Field(..., description="评分 1-5", ge=1, le=5)
    feedback: Optional[str] = Field(None, description="文字反馈", max_length=1000)
    useful_ideas: Optional[List[str]] = Field(None, description="有用的创意ID")
    improvement_suggestions: Optional[str] = Field(None, description="改进建议", max_length=500)


class RateGenerationResponse(BaseModel):
    """评价生成响应"""
    success: bool = Field(..., description="是否成功")
    average_rating: float = Field(..., description="平均评分")
    feedback_received: bool = Field(..., description="是否收到反馈")