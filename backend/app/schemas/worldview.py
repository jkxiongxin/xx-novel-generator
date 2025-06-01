"""
世界观数据模式
Author: AI Assistant
Created: 2025-06-01
"""

from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class WorldviewBase(BaseModel):
    """世界观基础模式"""
    name: str = Field(..., description="世界名称", max_length=100)
    description: Optional[str] = Field(None, description="世界描述")
    is_primary: bool = Field(default=False, description="是否主世界")


class WorldviewCreate(WorldviewBase):
    """创建世界观请求模式"""
    novel_id: int = Field(..., description="小说ID")


class WorldviewUpdate(BaseModel):
    """更新世界观请求模式"""
    name: Optional[str] = Field(None, description="世界名称", max_length=100)
    description: Optional[str] = Field(None, description="世界描述")
    is_primary: Optional[bool] = Field(None, description="是否主世界")


class WorldviewResponse(WorldviewBase):
    """世界观响应模式"""
    id: int = Field(..., description="世界观ID")
    novel_id: int = Field(..., description="小说ID")
    user_id: int = Field(..., description="用户ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True


class WorldMapBase(BaseModel):
    """世界地图基础模式"""
    region_name: str = Field(..., description="区域名称", max_length=100)
    description: str = Field(..., description="区域描述")
    parent_id: Optional[int] = Field(None, description="父区域ID")
    level: int = Field(default=1, description="层级")


class WorldMapCreate(WorldMapBase):
    """创建世界地图请求模式"""
    worldview_id: int = Field(..., description="世界观ID")


class WorldMapUpdate(BaseModel):
    """更新世界地图请求模式"""
    region_name: Optional[str] = Field(None, description="区域名称", max_length=100)
    description: Optional[str] = Field(None, description="区域描述")
    parent_id: Optional[int] = Field(None, description="父区域ID")
    level: Optional[int] = Field(None, description="层级")


class WorldMapResponse(WorldMapBase):
    """世界地图响应模式"""
    id: int = Field(..., description="地图ID")
    worldview_id: int = Field(..., description="世界观ID")
    user_id: int = Field(..., description="用户ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True


class CultivationSystemBase(BaseModel):
    """修炼体系基础模式"""
    system_name: str = Field(..., description="体系名称", max_length=100)
    level_name: str = Field(..., description="等级名称", max_length=100)
    description: str = Field(..., description="等级描述")
    cultivation_method: Optional[str] = Field(None, description="修炼方法")
    required_resources: Optional[str] = Field(None, description="所需资源")
    level_order: int = Field(..., description="等级顺序")


class CultivationSystemCreate(CultivationSystemBase):
    """创建修炼体系请求模式"""
    worldview_id: int = Field(..., description="世界观ID")


class CultivationSystemUpdate(BaseModel):
    """更新修炼体系请求模式"""
    system_name: Optional[str] = Field(None, description="体系名称", max_length=100)
    level_name: Optional[str] = Field(None, description="等级名称", max_length=100)
    description: Optional[str] = Field(None, description="等级描述")
    cultivation_method: Optional[str] = Field(None, description="修炼方法")
    required_resources: Optional[str] = Field(None, description="所需资源")
    level_order: Optional[int] = Field(None, description="等级顺序")


class CultivationSystemResponse(CultivationSystemBase):
    """修炼体系响应模式"""
    id: int = Field(..., description="体系ID")
    worldview_id: int = Field(..., description="世界观ID")
    user_id: int = Field(..., description="用户ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True


class HistoryBase(BaseModel):
    """历史事件基础模式"""
    event_name: str = Field(..., description="事件名称", max_length=200)
    dynasty_name: Optional[str] = Field(None, description="朝代名称", max_length=100)
    background: str = Field(..., description="历史背景")
    important_events: Optional[str] = Field(None, description="重要事件")
    impact_description: Optional[str] = Field(None, description="影响描述")
    time_order: int = Field(..., description="时间顺序")


class HistoryCreate(HistoryBase):
    """创建历史事件请求模式"""
    worldview_id: int = Field(..., description="世界观ID")


class HistoryUpdate(BaseModel):
    """更新历史事件请求模式"""
    event_name: Optional[str] = Field(None, description="事件名称", max_length=200)
    dynasty_name: Optional[str] = Field(None, description="朝代名称", max_length=100)
    background: Optional[str] = Field(None, description="历史背景")
    important_events: Optional[str] = Field(None, description="重要事件")
    impact_description: Optional[str] = Field(None, description="影响描述")
    time_order: Optional[int] = Field(None, description="时间顺序")


class HistoryResponse(HistoryBase):
    """历史事件响应模式"""
    id: int = Field(..., description="历史ID")
    worldview_id: int = Field(..., description="世界观ID")
    user_id: int = Field(..., description="用户ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True


class FactionBase(BaseModel):
    """阵营势力基础模式"""
    name: str = Field(..., description="阵营名称", max_length=100)
    faction_type: str = Field(..., description="类型：阵营/势力/组织", max_length=50)
    organization_structure: Optional[str] = Field(None, description="组织架构")
    territory: Optional[str] = Field(None, description="势力范围")
    ideology: Optional[str] = Field(None, description="理念目标")
    important_figures: Optional[str] = Field(None, description="重要人物")


class FactionCreate(FactionBase):
    """创建阵营势力请求模式"""
    worldview_id: int = Field(..., description="世界观ID")


class FactionUpdate(BaseModel):
    """更新阵营势力请求模式"""
    name: Optional[str] = Field(None, description="阵营名称", max_length=100)
    faction_type: Optional[str] = Field(None, description="类型：阵营/势力/组织", max_length=50)
    organization_structure: Optional[str] = Field(None, description="组织架构")
    territory: Optional[str] = Field(None, description="势力范围")
    ideology: Optional[str] = Field(None, description="理念目标")
    important_figures: Optional[str] = Field(None, description="重要人物")


class FactionResponse(FactionBase):
    """阵营势力响应模式"""
    id: int = Field(..., description="阵营ID")
    worldview_id: int = Field(..., description="世界观ID")
    user_id: int = Field(..., description="用户ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True


class WorldviewListResponse(BaseModel):
    """世界观列表响应模式"""
    items: List[WorldviewResponse] = Field(..., description="世界观列表")
    total: int = Field(..., description="总数量")


class WorldMapListResponse(BaseModel):
    """世界地图列表响应模式"""
    items: List[WorldMapResponse] = Field(..., description="世界地图列表")
    total: int = Field(..., description="总数量")


class CultivationSystemListResponse(BaseModel):
    """修炼体系列表响应模式"""
    items: List[CultivationSystemResponse] = Field(..., description="修炼体系列表")
    total: int = Field(..., description="总数量")


class HistoryListResponse(BaseModel):
    """历史事件列表响应模式"""
    items: List[HistoryResponse] = Field(..., description="历史事件列表")
    total: int = Field(..., description="总数量")


class FactionListResponse(BaseModel):
    """阵营势力列表响应模式"""
    items: List[FactionResponse] = Field(..., description="阵营势力列表")
    total: int = Field(..., description="总数量")


class WorldviewGenerationRequest(BaseModel):
    """世界观生成请求模式"""
    novel_id: int = Field(..., description="小说ID")
    worldview_name: Optional[str] = Field(None, description="世界观名称")
    generation_types: List[str] = Field(default_factory=list, description="生成类型：map/cultivation/history/faction")
    user_suggestion: Optional[str] = Field(None, description="用户建议")
    include_novel_idea: bool = Field(default=True, description="是否包含小说创意")
    include_novel_settings: bool = Field(default=True, description="是否包含小说设定")


class WorldviewGenerationResponse(BaseModel):
    """世界观生成响应模式"""
    success: bool = Field(..., description="生成是否成功")
    message: str = Field(..., description="响应消息")
    worldview: Optional[WorldviewResponse] = Field(None, description="生成的世界观")
    world_maps: List[WorldMapResponse] = Field(default_factory=list, description="生成的世界地图")
    cultivation_systems: List[CultivationSystemResponse] = Field(default_factory=list, description="生成的修炼体系")
    histories: List[HistoryResponse] = Field(default_factory=list, description="生成的历史事件")
    factions: List[FactionResponse] = Field(default_factory=list, description="生成的阵营势力")
    total_generated: int = Field(default=0, description="成功生成的项目数量")