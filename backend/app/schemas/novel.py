"""
小说数据模式
Author: AI Writer Team
Created: 2025-06-01
"""

from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class NovelStatus(str, Enum):
    """小说状态枚举"""
    DRAFT = "draft"          # 草稿
    WRITING = "writing"      # 写作中
    COMPLETED = "completed"  # 已完成
    PUBLISHED = "published"  # 已发布
    PAUSED = "paused"       # 暂停


class NovelGenre(str, Enum):
    """小说类型枚举"""
    FANTASY = "fantasy"        # 奇幻
    ROMANCE = "romance"        # 言情
    MYSTERY = "mystery"        # 悬疑
    SCIFI = "scifi"           # 科幻
    HISTORICAL = "historical"  # 历史
    MODERN = "modern"         # 现代
    MARTIAL_ARTS = "martial_arts"  # 武侠
    URBAN = "urban"           # 都市
    GAME = "game"             # 游戏
    OTHER = "other"           # 其他


class NovelBase(BaseModel):
    """小说基础模式"""
    title: str
    description: Optional[str] = None
    genre: NovelGenre
    tags: Optional[List[str]] = []
    target_word_count: Optional[int] = None
    
    @validator('title')
    def validate_title(cls, v):
        """验证标题"""
        if not v or not v.strip():
            raise ValueError('标题不能为空')
        if len(v.strip()) < 2:
            raise ValueError('标题至少需要2个字符')
        if len(v.strip()) > 100:
            raise ValueError('标题不能超过100个字符')
        return v.strip()
    
    @validator('description')
    def validate_description(cls, v):
        """验证描述"""
        if v is not None:
            if len(v.strip()) > 1000:
                raise ValueError('描述不能超过1000个字符')
            return v.strip() if v.strip() else None
        return v
    
    @validator('target_word_count')
    def validate_target_word_count(cls, v):
        """验证目标字数"""
        if v is not None:
            if v <= 0:
                raise ValueError('目标字数必须大于0')
            if v > 10000000:  # 1000万字
                raise ValueError('目标字数不能超过1000万字')
        return v


class NovelCreate(NovelBase):
    """小说创建模式"""
    pass


class NovelUpdate(BaseModel):
    """小说更新模式"""
    title: Optional[str] = None
    description: Optional[str] = None
    genre: Optional[NovelGenre] = None
    tags: Optional[List[str]] = None
    target_word_count: Optional[int] = None
    status: Optional[NovelStatus] = None
    
    @validator('title')
    def validate_title(cls, v):
        """验证标题"""
        if v is not None:
            if not v or not v.strip():
                raise ValueError('标题不能为空')
            if len(v.strip()) < 2:
                raise ValueError('标题至少需要2个字符')
            if len(v.strip()) > 100:
                raise ValueError('标题不能超过100个字符')
            return v.strip()
        return v
    
    @validator('description')
    def validate_description(cls, v):
        """验证描述"""
        if v is not None:
            if len(v.strip()) > 1000:
                raise ValueError('描述不能超过1000个字符')
            return v.strip() if v.strip() else None
        return v
    
    @validator('target_word_count')
    def validate_target_word_count(cls, v):
        """验证目标字数"""
        if v is not None:
            if v <= 0:
                raise ValueError('目标字数必须大于0')
            if v > 10000000:  # 1000万字
                raise ValueError('目标字数不能超过1000万字')
        return v


class NovelInDBBase(NovelBase):
    """数据库中的小说基础模式"""
    id: int
    user_id: int
    status: NovelStatus
    word_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Novel(NovelInDBBase):
    """小说响应模式"""
    pass


class NovelInDB(NovelInDBBase):
    """数据库中的小说模式"""
    pass


class NovelResponse(BaseModel):
    """小说响应模式"""
    id: int
    title: str
    description: Optional[str] = None
    genre: NovelGenre
    tags: List[str]
    status: NovelStatus
    target_word_count: Optional[int] = None
    word_count: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NovelListResponse(BaseModel):
    """小说列表响应模式"""
    novels: List[NovelResponse]
    total: int
    page: int
    size: int
    total_pages: int


class NovelStats(BaseModel):
    """小说统计模式"""
    total_novels: int
    total_word_count: int
    novels_by_status: dict
    novels_by_genre: dict
    average_word_count: float


class NovelSearchParams(BaseModel):
    """小说搜索参数"""
    keyword: Optional[str] = None
    genre: Optional[NovelGenre] = None
    status: Optional[NovelStatus] = None
    tags: Optional[List[str]] = None
    page: int = 1
    size: int = 20
    
    @validator('page')
    def validate_page(cls, v):
        """验证页码"""
        if v < 1:
            raise ValueError('页码必须大于0')
        return v
    
    @validator('size')
    def validate_size(cls, v):
        """验证每页大小"""
        if v < 1:
            raise ValueError('每页大小必须大于0')
        if v > 100:
            raise ValueError('每页大小不能超过100')
        return v