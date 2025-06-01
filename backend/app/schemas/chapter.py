"""
章节数据模式
Author: AI Assistant
Created: 2025-06-01
"""

from typing import Optional, List
from pydantic import BaseModel, Field, validator
from datetime import datetime

from app.models.chapter import ChapterStatus


class ChapterBase(BaseModel):
    """章节基础模式"""
    title: str = Field(..., description="章节标题", max_length=200)
    content: Optional[str] = Field(None, description="章节内容")
    chapter_number: int = Field(..., description="章节序号", ge=1)
    status: ChapterStatus = Field(default=ChapterStatus.DRAFT, description="章节状态")
    outline_id: Optional[int] = Field(None, description="关联大纲ID")
    character_ids: List[int] = Field(default_factory=list, description="关联角色ID列表")
    notes: Optional[str] = Field(None, description="作者备注")

    @validator('character_ids')
    def validate_character_ids(cls, v):
        """验证角色ID列表"""
        if v is None:
            return []
        if not isinstance(v, list):
            raise ValueError("character_ids must be a list")
        if len(v) > 50:  # 限制最多关联50个角色
            raise ValueError("Too many characters (max 50)")
        return v

    @validator('title')
    def validate_title(cls, v):
        """验证章节标题"""
        if not v or not v.strip():
            raise ValueError("Title cannot be empty")
        if len(v.strip()) < 2:
            raise ValueError("Title must be at least 2 characters")
        return v.strip()


class ChapterCreate(ChapterBase):
    """创建章节请求模式"""
    novel_id: int = Field(..., description="小说ID")

    @validator('chapter_number')
    def validate_chapter_number(cls, v):
        """验证章节序号"""
        if v < 1:
            raise ValueError("Chapter number must be positive")
        if v > 10000:  # 限制最大章节数
            raise ValueError("Chapter number too large (max 10000)")
        return v


class ChapterUpdate(BaseModel):
    """更新章节请求模式"""
    title: Optional[str] = Field(None, description="章节标题", max_length=200)
    content: Optional[str] = Field(None, description="章节内容")
    chapter_number: Optional[int] = Field(None, description="章节序号", ge=1)
    status: Optional[ChapterStatus] = Field(None, description="章节状态")
    outline_id: Optional[int] = Field(None, description="关联大纲ID")
    character_ids: Optional[List[int]] = Field(None, description="关联角色ID列表")
    notes: Optional[str] = Field(None, description="作者备注")

    @validator('character_ids')
    def validate_character_ids(cls, v):
        """验证角色ID列表"""
        if v is None:
            return v
        if not isinstance(v, list):
            raise ValueError("character_ids must be a list")
        if len(v) > 50:
            raise ValueError("Too many characters (max 50)")
        return v

    @validator('title')
    def validate_title(cls, v):
        """验证章节标题"""
        if v is not None:
            if not v or not v.strip():
                raise ValueError("Title cannot be empty")
            if len(v.strip()) < 2:
                raise ValueError("Title must be at least 2 characters")
            return v.strip()
        return v

    @validator('chapter_number')
    def validate_chapter_number(cls, v):
        """验证章节序号"""
        if v is not None:
            if v < 1:
                raise ValueError("Chapter number must be positive")
            if v > 10000:
                raise ValueError("Chapter number too large (max 10000)")
        return v


class ChapterResponse(ChapterBase):
    """章节响应模式"""
    id: int = Field(..., description="章节ID")
    novel_id: int = Field(..., description="小说ID")
    user_id: int = Field(..., description="用户ID")
    word_count: int = Field(default=0, description="字数统计")
    version: int = Field(default=1, description="版本号")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True


class ChapterSummaryResponse(BaseModel):
    """章节摘要响应模式"""
    id: int = Field(..., description="章节ID")
    novel_id: int = Field(..., description="小说ID")
    title: str = Field(..., description="章节标题")
    chapter_number: int = Field(..., description="章节序号")
    word_count: int = Field(..., description="字数统计")
    status: ChapterStatus = Field(..., description="章节状态")
    version: int = Field(..., description="版本号")
    outline_id: Optional[int] = Field(None, description="关联大纲ID")
    character_count: int = Field(default=0, description="关联角色数量")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True


class ChapterListResponse(BaseModel):
    """章节列表响应模式"""
    items: List[ChapterSummaryResponse] = Field(..., description="章节列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")
    total_pages: int = Field(..., description="总页数")
    total_words: int = Field(default=0, description="总字数")


class ChapterGenerationRequest(BaseModel):
    """AI生成章节请求模式"""
    novel_id: int = Field(..., description="小说ID")
    chapter_number: int = Field(..., description="目标章节号", ge=1)
    outline_id: Optional[int] = Field(None, description="基于的大纲ID")
    character_ids: List[int] = Field(default_factory=list, description="参与角色ID列表")
    prompt_template: Optional[str] = Field(None, description="提示词模板类型")
    generation_params: dict = Field(default_factory=dict, description="生成参数配置")
    user_suggestion: Optional[str] = Field(None, description="用户建议和要求")
    include_worldview: bool = Field(default=True, description="是否包含世界观信息")
    include_characters: bool = Field(default=True, description="是否包含角色信息")
    include_outline: bool = Field(default=True, description="是否包含大纲信息")
    target_word_count: Optional[int] = Field(None, description="目标字数", ge=100, le=50000)

    @validator('generation_params')
    def validate_generation_params(cls, v):
        """验证生成参数"""
        if not isinstance(v, dict):
            return {}
        
        # 验证常用参数
        allowed_params = {
            'temperature', 'max_tokens', 'top_p', 'frequency_penalty', 
            'presence_penalty', 'style', 'tone', 'perspective'
        }
        
        return {k: v[k] for k in v if k in allowed_params}

    @validator('character_ids')
    def validate_character_ids(cls, v):
        """验证角色ID列表"""
        if len(v) > 20:  # 单章节最多20个角色
            raise ValueError("Too many characters for single chapter (max 20)")
        return v


class ChapterGenerationResponse(BaseModel):
    """AI生成章节响应模式"""
    success: bool = Field(..., description="生成是否成功")
    message: str = Field(..., description="响应消息")
    chapter: Optional[ChapterResponse] = Field(None, description="生成的章节")
    generated_content: Optional[str] = Field(None, description="生成的内容")
    word_count: int = Field(default=0, description="生成内容字数")
    generation_data: Optional[dict] = Field(None, description="原始生成数据")
    used_prompt_template: Optional[str] = Field(None, description="使用的提示词模板")


class ChapterFilterRequest(BaseModel):
    """章节筛选请求模式"""
    title: Optional[str] = Field(None, description="标题模糊搜索")
    status: Optional[ChapterStatus] = Field(None, description="状态筛选")
    chapter_number_start: Optional[int] = Field(None, description="章节号范围开始", ge=1)
    chapter_number_end: Optional[int] = Field(None, description="章节号范围结束", ge=1)
    word_count_min: Optional[int] = Field(None, description="最小字数", ge=0)
    word_count_max: Optional[int] = Field(None, description="最大字数", ge=0)
    has_outline: Optional[bool] = Field(None, description="是否关联大纲")
    character_ids: List[int] = Field(default_factory=list, description="包含指定角色")
    created_after: Optional[datetime] = Field(None, description="创建时间之后")
    created_before: Optional[datetime] = Field(None, description="创建时间之前")

    @validator('chapter_number_end')
    def validate_chapter_range(cls, v, values):
        """验证章节号范围"""
        if v is not None and 'chapter_number_start' in values:
            start = values['chapter_number_start']
            if start is not None and v < start:
                raise ValueError("End chapter must be >= start chapter")
        return v

    @validator('word_count_max')
    def validate_word_count_range(cls, v, values):
        """验证字数范围"""
        if v is not None and 'word_count_min' in values:
            min_count = values['word_count_min']
            if min_count is not None and v < min_count:
                raise ValueError("Max word count must be >= min word count")
        return v


class ChapterBatchRequest(BaseModel):
    """章节批量操作请求模式"""
    chapter_ids: List[int] = Field(..., description="章节ID列表")
    operation: str = Field(..., description="操作类型")
    operation_data: dict = Field(default_factory=dict, description="操作数据")

    @validator('chapter_ids')
    def validate_chapter_ids(cls, v):
        """验证章节ID列表"""
        if not v:
            raise ValueError("Chapter IDs list cannot be empty")
        if len(v) > 100:  # 批量操作最多100个章节
            raise ValueError("Too many chapters for batch operation (max 100)")
        return v

    @validator('operation')
    def validate_operation(cls, v):
        """验证操作类型"""
        allowed_operations = {
            'update_status', 'delete', 'update_outline', 
            'add_characters', 'remove_characters', 'export'
        }
        if v not in allowed_operations:
            raise ValueError(f"Invalid operation. Allowed: {allowed_operations}")
        return v


class ChapterBatchResponse(BaseModel):
    """章节批量操作响应模式"""
    success: bool = Field(..., description="操作是否成功")
    message: str = Field(..., description="响应消息")
    processed_count: int = Field(default=0, description="处理成功的章节数量")
    failed_count: int = Field(default=0, description="处理失败的章节数量")
    failed_ids: List[int] = Field(default_factory=list, description="处理失败的章节ID列表")
    results: List[dict] = Field(default_factory=list, description="详细结果信息")


class ChapterStatsResponse(BaseModel):
    """章节统计响应模式"""
    total_chapters: int = Field(..., description="总章节数")
    draft_count: int = Field(..., description="草稿章节数")
    completed_count: int = Field(..., description="已完成章节数")
    published_count: int = Field(..., description="已发布章节数")
    total_words: int = Field(..., description="总字数")
    average_words: float = Field(..., description="平均字数")
    latest_chapter: Optional[ChapterSummaryResponse] = Field(None, description="最新章节")
    chapter_distribution: dict = Field(default_factory=dict, description="章节分布统计")