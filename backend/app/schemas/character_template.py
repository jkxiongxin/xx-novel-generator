"""
角色模板数据模式
Author: AI Assistant
Created: 2025-06-03
"""

from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field
from datetime import datetime

from app.schemas.character import CharacterResponse, CharacterSummaryResponse
from app.models.character import CharacterType, CharacterGender


class AppearanceDetail(BaseModel):
    """外貌描述模式"""
    height: Optional[str] = Field(None, description="身高")
    build: Optional[str] = Field(None, description="体型")
    hair: Optional[str] = Field(None, description="发型发色")
    eyes: Optional[str] = Field(None, description="眼睛")
    distinctive_features: Optional[str] = Field(None, description="特征")
    other: Optional[Dict[str, str]] = Field(default_factory=dict, description="其他外貌属性")


class TemplateDetailBase(BaseModel):
    """模板详情基础模式"""
    detailed_description: Optional[str] = Field(None, description="详细描述")
    background_story: Optional[str] = Field(None, description="背景故事")
    relationships: Optional[str] = Field(None, description="人际关系")
    strengths: List[str] = Field(default_factory=list, description="优势特点")
    weaknesses: List[str] = Field(default_factory=list, description="弱点缺陷")
    motivation: Optional[str] = Field(None, description="动机目标")
    character_arc: Optional[str] = Field(None, description="角色发展弧")
    dialogue_style: Optional[str] = Field(None, description="对话风格")
    appearance: Optional[AppearanceDetail] = Field(None, description="外貌描述")
    combat_style: Optional[str] = Field(None, description="战斗风格")
    equipment: List[str] = Field(default_factory=list, description="装备道具")
    special_abilities: List[str] = Field(default_factory=list, description="特殊能力")


class TemplateDetailCreate(TemplateDetailBase):
    """创建模板详情请求模式"""
    character_id: int = Field(..., description="关联角色ID")


class TemplateDetailUpdate(TemplateDetailBase):
    """更新模板详情请求模式"""
    pass


class TemplateDetailResponse(TemplateDetailBase):
    """模板详情响应模式"""
    id: int = Field(..., description="模板详情ID")
    character_id: int = Field(..., description="关联角色ID")
    usage_count: int = Field(..., description="使用次数")
    rating: float = Field(..., description="评分")
    is_popular: bool = Field(..., description="是否热门")
    is_new: bool = Field(..., description="是否新增")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    class Config:
        from_attributes = True


class UsageExampleBase(BaseModel):
    """使用示例基础模式"""
    novel_genre: str = Field(..., description="小说类型")
    usage_context: str = Field(..., description="使用场景")
    adaptation_notes: Optional[str] = Field(None, description="适配说明")


class UsageExampleCreate(UsageExampleBase):
    """创建使用示例请求模式"""
    template_detail_id: int = Field(..., description="模板详情ID")


class UsageExampleUpdate(UsageExampleBase):
    """更新使用示例请求模式"""
    pass


class UsageExampleResponse(UsageExampleBase):
    """使用示例响应模式"""
    id: int = Field(..., description="使用示例ID")
    template_detail_id: int = Field(..., description="模板详情ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    class Config:
        from_attributes = True


class CharacterTemplateResponse(CharacterResponse):
    """角色模板响应模式"""
    template_detail: Optional[TemplateDetailResponse] = Field(None, description="模板详情")
    usage_examples: List[UsageExampleResponse] = Field(default_factory=list, description="使用示例")
    is_favorited: Optional[bool] = Field(None, description="当前用户是否已收藏")


class CharacterTemplateSummaryResponse(CharacterSummaryResponse):
    """角色模板摘要响应模式"""
    usage_count: int = Field(default=0, description="使用次数")
    rating: float = Field(default=0.0, description="评分")
    is_popular: bool = Field(default=False, description="是否热门")
    is_new: bool = Field(default=False, description="是否新增")
    is_favorited: Optional[bool] = Field(None, description="当前用户是否已收藏")


class TemplateFilterOption(BaseModel):
    """筛选选项模式"""
    value: str = Field(..., description="选项值")
    label: str = Field(..., description="选项标签")
    count: int = Field(default=0, description="选项计数")


class CharacterTemplateListResponse(BaseModel):
    """角色模板列表响应模式"""
    characters: List[CharacterTemplateSummaryResponse] = Field(..., description="角色模板列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")
    total_pages: int = Field(..., description="总页数")
    filters_available: Optional[Dict[str, List[TemplateFilterOption]]] = Field(None, description="可用的筛选选项")


class UseTemplateRequest(BaseModel):
    """使用角色模板请求模式"""
    novel_id: int = Field(..., description="目标小说ID")
    customizations: Optional[Dict[str, Any]] = Field(None, description="自定义修改")
    adaptation_notes: Optional[str] = Field(None, description="适配说明")


class UseTemplateResponse(BaseModel):
    """使用角色模板响应模式"""
    success: bool = Field(..., description="是否成功")
    character: CharacterResponse = Field(..., description="创建的角色")
    template_used: CharacterSummaryResponse = Field(..., description="使用的模板")
    adaptation_applied: bool = Field(..., description="是否应用了适配")
    message: str = Field(..., description="响应消息")


class BatchUseTemplateItem(BaseModel):
    """批量使用模板项模式"""
    template_id: int = Field(..., description="模板ID")
    customizations: Optional[Dict[str, Any]] = Field(None, description="自定义修改")


class BatchUseTemplatesRequest(BaseModel):
    """批量使用模板请求模式"""
    novel_id: int = Field(..., description="目标小说ID")
    templates: List[BatchUseTemplateItem] = Field(..., description="模板列表")


class BatchUseFailedItem(BaseModel):
    """批量失败项模式"""
    template_id: int = Field(..., description="模板ID")
    reason: str = Field(..., description="失败原因")


class BatchUseTemplatesResponse(BaseModel):
    """批量使用模板响应模式"""
    success_count: int = Field(..., description="成功数量")
    failed_count: int = Field(..., description="失败数量")
    created_characters: List[CharacterSummaryResponse] = Field(..., description="创建的角色")
    failed_items: List[BatchUseFailedItem] = Field(..., description="失败项")
    message: str = Field(..., description="响应消息")


class FavoriteResponse(BaseModel):
    """收藏响应模式"""
    success: bool = Field(..., description="是否成功")
    is_favorited: bool = Field(..., description="是否已收藏")
    message: str = Field(..., description="响应消息")


class GetFavoriteTemplatesResponse(BaseModel):
    """获取收藏模板响应模式"""
    characters: List[CharacterTemplateSummaryResponse] = Field(..., description="角色模板列表")
    total: int = Field(..., description="总数量")


class RecommendedCharacter(CharacterTemplateSummaryResponse):
    """推荐角色模式"""
    recommendation_score: float = Field(..., description="推荐分数")
    recommendation_reasons: List[str] = Field(..., description="推荐理由")
    fit_score: float = Field(..., description="适配度评分")


class GetRecommendationsResponse(BaseModel):
    """获取推荐响应模式"""
    recommendations: List[RecommendedCharacter] = Field(..., description="推荐列表")
    recommendation_reason: str = Field(..., description="推荐原因")


class GenreUsageStat(BaseModel):
    """类型使用统计模式"""
    genre: str = Field(..., description="类型")
    usage_count: int = Field(..., description="使用次数")


class UserTemplateStat(BaseModel):
    """用户模板统计模式"""
    templates_used: int = Field(..., description="使用的模板数量")
    favorite_count: int = Field(..., description="收藏数量")
    most_used_tags: List[str] = Field(..., description="最常用标签")


class GetTemplateStatsResponse(BaseModel):
    """获取模板统计响应模式"""
    total_templates: int = Field(..., description="模板总数")
    total_usages: int = Field(..., description="总使用次数")
    popular_templates: List[CharacterTemplateSummaryResponse] = Field(..., description="热门模板")
    trending_tags: List[str] = Field(..., description="流行标签")
    usage_by_genre: List[GenreUsageStat] = Field(..., description="按类型使用统计")
    user_stats: Optional[UserTemplateStat] = Field(None, description="用户统计")


class SearchSuggestion(BaseModel):
    """搜索建议模式"""
    text: str = Field(..., description="建议文本")
    type: str = Field(..., description="建议类型")
    match_count: int = Field(..., description="匹配数量")


class SearchMetadata(BaseModel):
    """搜索元数据模式"""
    keyword: str = Field(..., description="关键词")
    total_matches: int = Field(..., description="总匹配数")
    search_time: float = Field(..., description="搜索时间(ms)")
    suggestions: Optional[List[str]] = Field(None, description="搜索建议")


class HighlightedField(BaseModel):
    """高亮字段模式"""
    field: str = Field(..., description="字段名")
    content: str = Field(..., description="高亮内容")


class HighlightedResult(BaseModel):
    """高亮结果模式"""
    character_id: int = Field(..., description="角色ID")
    highlighted_fields: List[HighlightedField] = Field(..., description="高亮字段")


class SearchTemplatesResponse(CharacterTemplateListResponse):
    """搜索模板响应模式"""
    search_metadata: SearchMetadata = Field(..., description="搜索元数据")
    highlighted_results: Optional[List[HighlightedResult]] = Field(None, description="高亮结果")


class SearchTemplatesRequest(BaseModel):
    """搜索模板请求模式"""
    keyword: str = Field(..., description="搜索关键词")
    filters: Optional[Dict[str, Any]] = Field(None, description="额外筛选条件")
    search_fields: Optional[List[str]] = Field(None, description="搜索字段")
    fuzzy_search: bool = Field(default=True, description="是否模糊搜索")
    highlight: bool = Field(default=False, description="是否高亮匹配内容")


# === 管理员角色模板管理相关Schema ===

class CharacterTemplateCreateRequest(BaseModel):
    """创建角色模板请求模式"""
    # 基础角色信息
    name: str = Field(..., min_length=1, max_length=100, description="角色名")
    gender: str = Field(..., description="性别")
    personality: Optional[str] = Field(None, description="性格描述")
    character_type: str = Field(..., description="角色类型")
    tags: List[str] = Field(default_factory=list, description="角色标签")
    description: Optional[str] = Field(None, description="角色描述")
    abilities: Optional[str] = Field(None, description="角色能力")
    power_system: Optional[str] = Field(None, description="力量体系")
    original_world: Optional[str] = Field(None, description="原生世界名")
    
    # 模板详情信息
    template_detail: Optional[TemplateDetailBase] = Field(None, description="模板详情")


class CharacterTemplateUpdateRequest(BaseModel):
    """更新角色模板请求模式"""
    # 基础角色信息
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="角色名")
    gender: Optional[str] = Field(None, description="性别")
    personality: Optional[str] = Field(None, description="性格描述")
    character_type: Optional[str] = Field(None, description="角色类型")
    tags: Optional[List[str]] = Field(None, description="角色标签")
    description: Optional[str] = Field(None, description="角色描述")
    abilities: Optional[str] = Field(None, description="角色能力")
    power_system: Optional[str] = Field(None, description="力量体系")
    original_world: Optional[str] = Field(None, description="原生世界名")
    
    # 模板详情信息
    template_detail: Optional[TemplateDetailBase] = Field(None, description="模板详情")


class CharacterTemplateCreateResponse(BaseModel):
    """创建角色模板响应模式"""
    success: bool = Field(..., description="是否成功")
    template: CharacterTemplateResponse = Field(..., description="创建的模板")
    message: str = Field(..., description="响应消息")


class CharacterTemplateUpdateResponse(BaseModel):
    """更新角色模板响应模式"""
    success: bool = Field(..., description="是否成功")
    template: CharacterTemplateResponse = Field(..., description="更新的模板")
    message: str = Field(..., description="响应消息")


class CharacterTemplateDeleteResponse(BaseModel):
    """删除角色模板响应模式"""
    success: bool = Field(..., description="是否成功")
    template_id: int = Field(..., description="删除的模板ID")
    message: str = Field(..., description="响应消息")


class AdminTemplateListResponse(BaseModel):
    """管理员模板列表响应模式"""
    templates: List[CharacterTemplateResponse] = Field(..., description="模板列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")
    total_pages: int = Field(..., description="总页数")


class TemplateStatusUpdateRequest(BaseModel):
    """模板状态更新请求模式"""
    is_popular: Optional[bool] = Field(None, description="是否热门")
    is_new: Optional[bool] = Field(None, description="是否新增")
    rating: Optional[float] = Field(None, ge=0.0, le=5.0, description="评分")


class BatchTemplateStatusUpdateRequest(BaseModel):
    """批量模板状态更新请求模式"""
    template_ids: List[int] = Field(..., description="模板ID列表")
    status_updates: TemplateStatusUpdateRequest = Field(..., description="状态更新")


class BatchTemplateStatusUpdateResponse(BaseModel):
    """批量模板状态更新响应模式"""
    success_count: int = Field(..., description="成功数量")
    failed_count: int = Field(..., description="失败数量")
    failed_items: List[Dict[str, Any]] = Field(..., description="失败项")
    message: str = Field(..., description="响应消息")