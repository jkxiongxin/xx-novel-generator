"""
世界观数据模式
Author: AI Assistant
Created: 2025-06-01
Updated: 2025-06-03
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
    parent_region_id: Optional[int] = Field(None, description="父区域ID")
    level: int = Field(default=1, description="层级")
    climate: Optional[str] = Field(None, description="气候特征", max_length=200)
    terrain: Optional[str] = Field(None, description="地形特征", max_length=200)
    resources: Optional[str] = Field(None, description="主要资源")
    population: Optional[str] = Field(None, description="人口情况", max_length=100)
    culture: Optional[str] = Field(None, description="文化特色")


class WorldMapCreate(WorldMapBase):
    """创建世界地图请求模式"""
    pass


class WorldMapUpdate(BaseModel):
    """更新世界地图请求模式"""
    region_name: Optional[str] = Field(None, description="区域名称", max_length=100)
    description: Optional[str] = Field(None, description="区域描述")
    parent_region_id: Optional[int] = Field(None, description="父区域ID")
    level: Optional[int] = Field(None, description="层级")
    climate: Optional[str] = Field(None, description="气候特征", max_length=200)
    terrain: Optional[str] = Field(None, description="地形特征", max_length=200)
    resources: Optional[str] = Field(None, description="主要资源")
    population: Optional[str] = Field(None, description="人口情况", max_length=100)
    culture: Optional[str] = Field(None, description="文化特色")


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
    level_order: int = Field(..., description="等级顺序")
    cultivation_method: Optional[str] = Field(None, description="修炼方法")
    required_resources: Optional[str] = Field(None, description="所需资源")
    breakthrough_condition: Optional[str] = Field(None, description="突破条件")
    power_description: Optional[str] = Field(None, description="力量描述")


class CultivationSystemCreate(CultivationSystemBase):
    """创建修炼体系请求模式"""
    pass


class CultivationSystemUpdate(BaseModel):
    """更新修炼体系请求模式"""
    system_name: Optional[str] = Field(None, description="体系名称", max_length=100)
    level_name: Optional[str] = Field(None, description="等级名称", max_length=100)
    description: Optional[str] = Field(None, description="等级描述")
    level_order: Optional[int] = Field(None, description="等级顺序")
    cultivation_method: Optional[str] = Field(None, description="修炼方法")
    required_resources: Optional[str] = Field(None, description="所需资源")
    breakthrough_condition: Optional[str] = Field(None, description="突破条件")
    power_description: Optional[str] = Field(None, description="力量描述")


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
    time_period: Optional[str] = Field(None, description="时间段", max_length=100)
    time_order: int = Field(..., description="时间顺序")
    event_type: Optional[str] = Field(None, description="事件类型", max_length=50)
    description: str = Field(..., description="事件描述")
    participants: Optional[str] = Field(None, description="参与者")
    consequences: Optional[str] = Field(None, description="后果影响")
    related_locations: Optional[str] = Field(None, description="相关地点")


class HistoryCreate(HistoryBase):
    """创建历史事件请求模式"""
    pass


class HistoryUpdate(BaseModel):
    """更新历史事件请求模式"""
    event_name: Optional[str] = Field(None, description="事件名称", max_length=200)
    time_period: Optional[str] = Field(None, description="时间段", max_length=100)
    time_order: Optional[int] = Field(None, description="时间顺序")
    event_type: Optional[str] = Field(None, description="事件类型", max_length=50)
    description: Optional[str] = Field(None, description="事件描述")
    participants: Optional[str] = Field(None, description="参与者")
    consequences: Optional[str] = Field(None, description="后果影响")
    related_locations: Optional[str] = Field(None, description="相关地点")


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
    description: Optional[str] = Field(None, description="组织描述")
    leader: Optional[str] = Field(None, description="领导者", max_length=100)
    territory: Optional[str] = Field(None, description="控制区域")
    power_level: Optional[str] = Field(None, description="势力等级", max_length=50)
    ideology: Optional[str] = Field(None, description="理念目标")
    allies: Optional[List[str]] = Field(None, description="盟友列表")
    enemies: Optional[List[str]] = Field(None, description="敌对列表")
    member_count: Optional[str] = Field(None, description="成员数量", max_length=50)


class FactionCreate(FactionBase):
    """创建阵营势力请求模式"""
    pass


class FactionUpdate(BaseModel):
    """更新阵营势力请求模式"""
    name: Optional[str] = Field(None, description="阵营名称", max_length=100)
    faction_type: Optional[str] = Field(None, description="类型：阵营/势力/组织", max_length=50)
    description: Optional[str] = Field(None, description="组织描述")
    leader: Optional[str] = Field(None, description="领导者", max_length=100)
    territory: Optional[str] = Field(None, description="控制区域")
    power_level: Optional[str] = Field(None, description="势力等级", max_length=50)
    ideology: Optional[str] = Field(None, description="理念目标")
    allies: Optional[List[str]] = Field(None, description="盟友列表")
    enemies: Optional[List[str]] = Field(None, description="敌对列表")
    member_count: Optional[str] = Field(None, description="成员数量", max_length=50)


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
    generation_types: List[str] = Field(default_factory=list, description="生成类型：maps/cultivation/history/factions")
    user_suggestion: Optional[str] = Field(None, description="用户建议")
    include_novel_settings: bool = Field(default=True, description="是否包含小说设定")
    
    # 新增字段
    genre: Optional[str] = Field(None, description="小说类型")
    themes: Optional[List[str]] = Field(default_factory=list, description="小说主题列表")
    style: Optional[str] = Field(None, description="写作风格")
    
    class Config:
        schema_extra = {
            "example": {
                "novel_id": 1,
                "worldview_name": "玄幻大陆",
                "generation_types": ["maps", "cultivation", "history", "factions"],
                "genre": "玄幻",
                "themes": ["修炼", "争霸"],
                "style": "史诗",
                "user_suggestion": "希望包含特色的灵气体系",
                "include_novel_settings": True
            }
        }


class GeneratedWorldBase(BaseModel):
    """生成的世界基础信息"""
    name: str = Field(..., description="世界名称")
    description: str = Field(..., description="世界描述")
    background: str = Field(..., description="历史背景和基础设定")
    rules: List[str] = Field(default_factory=list, description="核心规则")
    characteristics: List[str] = Field(default_factory=list, description="世界特色")

class GeneratedLocation(BaseModel):
    """生成的特殊地点"""
    name: str = Field(..., description="地点名称")
    description: str = Field(..., description="地点描述")
    significance: str = Field(..., description="地点重要性")
    mysteries: List[str] = Field(default_factory=list, description="相关谜团")

class GeneratedPowerSystem(BaseModel):
    """生成的力量体系"""
    name: str = Field(..., description="体系名称")
    description: str = Field(..., description="体系描述")
    levels: List[dict] = Field(default_factory=list, description="等级体系")
    unique_features: List[str] = Field(default_factory=list, description="特色功能")
    cultivation_methods: List[str] = Field(default_factory=list, description="修炼方法")

class GeneratedArtifact(BaseModel):
    """生成的神器/遗物"""
    name: str = Field(..., description="神器名称")
    description: str = Field(..., description="描述")
    powers: List[str] = Field(default_factory=list, description="能力列表")
    history: str = Field(..., description="来历")

class GeneratedEra(BaseModel):
    """生成的历史时代"""
    name: str = Field(..., description="时代名称")
    description: str = Field(..., description="时代概述")
    major_events: List[dict] = Field(default_factory=list, description="重大事件")


class SimpleMapRegion(BaseModel):
    """简化的地图区域（用于生成响应）"""
    name: str = Field(..., description="区域名称")
    description: str = Field(..., description="区域描述")
    climate: Optional[str] = Field(None, description="气候特征")
    notable_features: Optional[List[str]] = Field(None, description="显著特征")


class SimpleFaction(BaseModel):
    """简化的阵营势力（用于生成响应）"""
    name: str = Field(..., description="阵营名称")
    description: str = Field(..., description="组织描述")
    ideology: Optional[str] = Field(None, description="理念目标")
    alliance: Optional[str] = Field(None, description="联盟关系")


class WorldviewGenerationResponse(BaseModel):
    """世界观生成响应模式"""
    success: bool = Field(..., description="生成是否成功")
    message: str = Field(..., description="响应消息")
    
    # 基础世界信息
    worldview: GeneratedWorldBase = Field(..., description="生成的世界基础信息")
    
    # 地理信息
    world_maps: List[SimpleMapRegion] = Field(default_factory=list, description="生成的地图区域")
    special_locations: List[GeneratedLocation] = Field(default_factory=list, description="生成的特殊地点")
    
    # 力量体系
    cultivation_system: GeneratedPowerSystem = Field(..., description="生成的力量体系")
    
    # 历史相关
    histories: List[GeneratedEra] = Field(default_factory=list, description="生成的历史时代")
    artifacts: List[GeneratedArtifact] = Field(default_factory=list, description="生成的神器/遗物")
    
    # 势力
    factions: List[SimpleFaction] = Field(default_factory=list, description="生成的阵营势力")
    
    # 统计
    total_generated: int = Field(default=0, description="成功生成的项目数量")