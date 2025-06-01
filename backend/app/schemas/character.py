"""
角色数据模式
Author: AI Assistant
Created: 2025-06-01
"""

from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

from app.models.character import CharacterType, CharacterGender


class CharacterBase(BaseModel):
    """角色基础模式"""
    name: str = Field(..., description="角色名", max_length=100)
    gender: CharacterGender = Field(default=CharacterGender.UNKNOWN, description="性别")
    personality: Optional[str] = Field(None, description="性格描述")
    character_type: CharacterType = Field(default=CharacterType.SUPPORTING, description="角色类型")
    worldview_id: Optional[int] = Field(None, description="世界观ID")
    faction_id: Optional[int] = Field(None, description="所属阵营ID")
    tags: List[str] = Field(default_factory=list, description="角色标签")
    description: Optional[str] = Field(None, description="角色描述")
    abilities: Optional[str] = Field(None, description="角色能力")
    power_system: Optional[str] = Field(None, description="力量体系", max_length=100)
    original_world: Optional[str] = Field(None, description="原生世界名", max_length=100)
    is_template: bool = Field(default=False, description="是否为模板角色")


class CharacterCreate(CharacterBase):
    """创建角色请求模式"""
    novel_id: Optional[int] = Field(None, description="小说ID，模板角色可为空")


class CharacterUpdate(BaseModel):
    """更新角色请求模式"""
    name: Optional[str] = Field(None, description="角色名", max_length=100)
    gender: Optional[CharacterGender] = Field(None, description="性别")
    personality: Optional[str] = Field(None, description="性格描述")
    character_type: Optional[CharacterType] = Field(None, description="角色类型")
    worldview_id: Optional[int] = Field(None, description="世界观ID")
    faction_id: Optional[int] = Field(None, description="所属阵营ID")
    tags: Optional[List[str]] = Field(None, description="角色标签")
    description: Optional[str] = Field(None, description="角色描述")
    abilities: Optional[str] = Field(None, description="角色能力")
    power_system: Optional[str] = Field(None, description="力量体系", max_length=100)
    original_world: Optional[str] = Field(None, description="原生世界名", max_length=100)
    is_template: Optional[bool] = Field(None, description="是否为模板角色")


class CharacterResponse(CharacterBase):
    """角色响应模式"""
    id: int = Field(..., description="角色ID")
    novel_id: Optional[int] = Field(None, description="小说ID")
    user_id: int = Field(..., description="用户ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True


class CharacterSummaryResponse(BaseModel):
    """角色摘要响应模式"""
    id: int = Field(..., description="角色ID")
    name: str = Field(..., description="角色名")
    gender: CharacterGender = Field(..., description="性别")
    character_type: CharacterType = Field(..., description="角色类型")
    tags: List[str] = Field(..., description="角色标签")
    description: Optional[str] = Field(None, description="角色描述摘要")
    is_template: bool = Field(..., description="是否为模板角色")

    class Config:
        from_attributes = True


class CharacterListResponse(BaseModel):
    """角色列表响应模式"""
    items: List[CharacterSummaryResponse] = Field(..., description="角色列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")
    total_pages: int = Field(..., description="总页数")


class CharacterGenerationRequest(BaseModel):
    """角色生成请求模式"""
    novel_id: int = Field(..., description="小说ID")
    worldview_id: Optional[int] = Field(None, description="世界观ID")
    character_count: int = Field(default=1, description="生成角色数量", ge=1, le=10)
    character_types: List[CharacterType] = Field(default_factory=list, description="指定角色类型")
    user_suggestion: Optional[str] = Field(None, description="用户建议")
    include_worldview: bool = Field(default=True, description="是否包含世界观信息")


class CharacterGenerationResponse(BaseModel):
    """角色生成响应模式"""
    success: bool = Field(..., description="生成是否成功")
    message: str = Field(..., description="响应消息")
    characters: List[CharacterResponse] = Field(default_factory=list, description="生成的角色列表")
    total_generated: int = Field(default=0, description="成功生成的角色数量")
    generation_data: Optional[List[dict]] = Field(default=None, description="原始生成数据")


class CharacterFilterRequest(BaseModel):
    """角色筛选请求模式"""
    name: Optional[str] = Field(None, description="角色名模糊搜索")
    gender: Optional[CharacterGender] = Field(None, description="性别筛选")
    character_type: Optional[CharacterType] = Field(None, description="角色类型筛选")
    worldview_id: Optional[int] = Field(None, description="世界观ID筛选")
    faction_id: Optional[int] = Field(None, description="阵营ID筛选")
    power_system: Optional[str] = Field(None, description="力量体系筛选")
    original_world: Optional[str] = Field(None, description="原生世界筛选")
    tags: List[str] = Field(default_factory=list, description="标签筛选")
    is_template: Optional[bool] = Field(None, description="是否模板角色筛选")
    is_added: Optional[bool] = Field(None, description="是否已添加到当前小说")


class CharacterBatchAddRequest(BaseModel):
    """角色批量添加请求模式"""
    character_ids: List[int] = Field(..., description="角色ID列表")
    novel_id: int = Field(..., description="目标小说ID")


class CharacterBatchAddResponse(BaseModel):
    """角色批量添加响应模式"""
    success: bool = Field(..., description="添加是否成功")
    message: str = Field(..., description="响应消息")
    added_count: int = Field(default=0, description="成功添加的角色数量")
    failed_count: int = Field(default=0, description="添加失败的角色数量")
    added_characters: List[CharacterResponse] = Field(default_factory=list, description="成功添加的角色列表")