"""
AI世界观生成响应专用数据模式
Author: AI Assistant
Created: 2025-06-03
"""

from typing import Optional, List, Union
from pydantic import BaseModel, Field


class AIWorldBase(BaseModel):
    """AI生成的世界基础信息"""
    name: str = Field(..., description="世界名称")
    description: str = Field(..., description="世界描述")
    background: str = Field(..., description="历史背景和基础设定")
    rules: List[str] = Field(default_factory=list, description="核心规则")
    characteristics: List[str] = Field(default_factory=list, description="世界特色")


class AIMapRegion(BaseModel):
    """AI生成的地图区域"""
    name: str = Field(..., description="区域名称")
    description: str = Field(..., description="区域描述")
    climate: Optional[str] = Field(None, description="气候特征")
    notable_features: Optional[List[str]] = Field(None, description="显著特征")


class AISpecialLocation(BaseModel):
    """AI生成的特殊地点"""
    name: str = Field(..., description="地点名称")
    description: str = Field(..., description="地点描述")
    significance: Optional[str] = Field(None, description="地点重要性")


class AIGeography(BaseModel):
    """AI生成的地理信息"""
    map_regions: List[AIMapRegion] = Field(default_factory=list, description="地图区域")
    special_locations: List[AISpecialLocation] = Field(default_factory=list, description="特殊地点")


class AIPowerLevel(BaseModel):
    """AI生成的力量等级"""
    name: str = Field(..., description="等级名称")
    description: str = Field(..., description="等级描述")


class AICultivationMethod(BaseModel):
    """AI生成的修炼方法"""
    name: str = Field(..., description="方法名称")
    description: str = Field(..., description="方法描述")
    attributes: Optional[List[str]] = Field(None, description="属性特征")


class AIUniqueFeature(BaseModel):
    """AI生成的特色功能"""
    name: str = Field(..., description="功能名称")
    description: str = Field(..., description="功能描述")
    abilities: Optional[List[str]] = Field(None, description="能力列表")


class AIPowerSystem(BaseModel):
    """AI生成的力量体系"""
    name: str = Field(..., description="体系名称")
    description: str = Field(..., description="体系描述")
    levels: List[AIPowerLevel] = Field(default_factory=list, description="等级体系")
    unique_features: List[Union[str, AIUniqueFeature]] = Field(default_factory=list, description="特色功能")
    cultivation_methods: List[AICultivationMethod] = Field(default_factory=list, description="修炼方法")


class AIHistoryEra(BaseModel):
    """AI生成的历史时代"""
    name: str = Field(..., description="时代名称")
    description: str = Field(..., description="时代概述")
    key_events: List[str] = Field(default_factory=list, description="关键事件")


class AIArtifact(BaseModel):
    """AI生成的神器/遗物"""
    name: str = Field(..., description="神器名称")
    description: str = Field(..., description="描述")
    significance: Optional[str] = Field(None, description="重要性")
    powers: Optional[List[str]] = Field(None, description="神器能力")


class AIHistory(BaseModel):
    """AI生成的历史信息"""
    eras: List[AIHistoryEra] = Field(default_factory=list, description="历史时代")
    significant_artifacts: List[AIArtifact] = Field(default_factory=list, description="重要神器")


class AIFaction(BaseModel):
    """AI生成的阵营势力"""
    name: str = Field(..., description="阵营名称")
    description: str = Field(..., description="组织描述")
    ideology: Optional[str] = Field(None, description="理念目标")
    powers_and_abilities: Optional[List[str]] = Field(None, description="能力列表")
    structure: Optional[str] = Field(None, description="组织结构")
    notable_members: Optional[List[str]] = Field(None, description="重要成员")


class AIWorldviewResponse(BaseModel):
    """AI世界观生成完整响应"""
    world_base: AIWorldBase = Field(..., description="世界基础信息")
    geography: AIGeography = Field(..., description="地理信息")
    power_system: AIPowerSystem = Field(..., description="力量体系")
    history: AIHistory = Field(..., description="历史信息")
    factions: List[AIFaction] = Field(default_factory=list, description="阵营势力")