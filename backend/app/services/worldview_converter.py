"""
世界观数据转换服务
将AI生成的数据转换为数据库Schema格式
Author: AI Assistant
Created: 2025-06-03
"""

import logging
from typing import List, Dict, Any, Optional
from app.schemas.ai_worldview import AIWorldviewResponse
from app.schemas.worldview import (
    WorldMapResponse, CultivationSystemResponse, 
    HistoryResponse, FactionResponse,
    GeneratedWorldBase, GeneratedPowerSystem,
    GeneratedLocation, GeneratedEra, GeneratedArtifact
)

logger = logging.getLogger(__name__)


class WorldviewConverter:
    """世界观数据转换器"""
    
    @staticmethod
    def convert_ai_response(ai_response: Dict[str, Any], user_id: int, novel_id: int) -> Dict[str, Any]:
        """
        将AI原始响应转换为适合前端的格式
        
        Args:
            ai_response: AI返回的原始数据
            user_id: 用户ID
            novel_id: 小说ID
            
        Returns:
            转换后的数据
        """
        try:
            # 解析AI响应
            parsed_response = AIWorldviewResponse(**ai_response)
            
            # 转换基础世界信息
            worldview = GeneratedWorldBase(
                name=parsed_response.world_base.name,
                description=parsed_response.world_base.description,
                background=parsed_response.world_base.background,
                rules=parsed_response.world_base.rules,
                characteristics=parsed_response.world_base.characteristics
            )
            
            # 转换地理信息 - 保持原始格式用于前端显示
            world_maps = []
            for region in parsed_response.geography.map_regions:
                world_maps.append({
                    "name": region.name,
                    "description": region.description,
                    "climate": region.climate or "",
                    "notable_features": region.notable_features or []
                })
            
            # 转换特殊地点
            special_locations = [
                GeneratedLocation(
                    name=loc.name,
                    description=loc.description,
                    significance=loc.significance or "",  # 处理可能缺失的significance字段
                    mysteries=[]  # AI响应中没有mysteries字段
                ) for loc in parsed_response.geography.special_locations
            ]
            
            # 转换力量体系
            cultivation_system = GeneratedPowerSystem(
                name=parsed_response.power_system.name,
                description=parsed_response.power_system.description,
                levels=[
                    {
                        "name": level.name,
                        "description": level.description
                    } for level in parsed_response.power_system.levels
                ],
                unique_features=[
                    feature.name if hasattr(feature, 'name') else str(feature)
                    for feature in parsed_response.power_system.unique_features
                ],
                cultivation_methods=[
                    method.name for method in parsed_response.power_system.cultivation_methods
                ]
            )
            
            # 转换历史信息
            histories = [
                GeneratedEra(
                    name=era.name,
                    description=era.description,
                    major_events=[
                        {"name": event, "description": event} for event in era.key_events
                    ]
                ) for era in parsed_response.history.eras
            ]
            
            # 转换神器
            artifacts = [
                GeneratedArtifact(
                    name=artifact.name,
                    description=artifact.description,
                    powers=artifact.powers or [],  # 使用AI返回的powers字段
                    history=artifact.significance or ""  # 使用significance字段作为历史
                ) for artifact in parsed_response.history.significant_artifacts
            ]
            
            # 转换阵营 - 保持原始格式用于前端显示
            factions = []
            for faction in parsed_response.factions:
                factions.append({
                    "name": faction.name,
                    "description": faction.description,
                    "ideology": faction.ideology or "",
                    "powers_and_abilities": faction.powers_and_abilities or [],
                    "structure": faction.structure or "",
                    "notable_members": faction.notable_members or []
                })
            
            return {
                "worldview": worldview,
                "world_maps": world_maps,
                "special_locations": special_locations,
                "cultivation_system": cultivation_system,
                "histories": histories,
                "artifacts": artifacts,
                "factions": factions
            }
            
        except Exception as e:
            logger.error(f"世界观数据转换失败: {str(e)}")
            raise ValueError(f"数据转换失败: {str(e)}")
    
    @staticmethod
    def convert_to_database_format(ai_response: Dict[str, Any], worldview_id: int, user_id: int) -> Dict[str, List]:
        """
        将AI响应转换为数据库格式（用于保存到数据库）
        
        Args:
            ai_response: AI返回的原始数据
            worldview_id: 世界观ID
            user_id: 用户ID
            
        Returns:
            数据库格式的数据
        """
        try:
            parsed_response = AIWorldviewResponse(**ai_response)
            
            # 转换地图区域为数据库格式
            world_maps = []
            for i, region in enumerate(parsed_response.geography.map_regions):
                world_maps.append({
                    "region_name": region.name,
                    "description": region.description,
                    "level": 1,
                    "climate": region.climate or "",
                    "terrain": ", ".join(region.notable_features or []),
                    "resources": "",  # AI响应中没有resources信息
                    "population": "",  # AI响应中没有population信息
                    "culture": ""  # AI响应中没有culture信息
                })
            
            # 转换修炼体系为数据库格式
            cultivation_systems = []
            for i, level in enumerate(parsed_response.power_system.levels):
                cultivation_systems.append({
                    "system_name": parsed_response.power_system.name,
                    "level_name": level.name,
                    "description": level.description,
                    "level_order": i + 1,
                    "cultivation_method": "",  # 后续可以从cultivation_methods中提取
                    "required_resources": "",
                    "breakthrough_condition": "",
                    "power_description": level.description
                })
            
            # 转换历史事件为数据库格式
            histories = []
            for era_idx, era in enumerate(parsed_response.history.eras):
                for event_idx, event in enumerate(era.key_events):
                    histories.append({
                        "event_name": event,
                        "time_period": era.name,
                        "time_order": era_idx * 100 + event_idx,
                        "event_type": "时代事件",
                        "description": f"{era.description} - {event}",
                        "participants": "",
                        "consequences": "",
                        "related_locations": ""
                    })
            
            # 转换阵营为数据库格式
            factions = []
            for faction in parsed_response.factions:
                factions.append({
                    "name": faction.name,
                    "faction_type": "组织",
                    "description": faction.description,
                    "leader": "",  # AI响应中可能在notable_members中
                    "territory": "",
                    "power_level": "",
                    "ideology": faction.ideology or "",
                    "allies": [],
                    "enemies": [],
                    "member_count": ""
                })
            
            return {
                "world_maps": world_maps,
                "cultivation_systems": cultivation_systems,
                "histories": histories,
                "factions": factions
            }
            
        except Exception as e:
            logger.error(f"数据库格式转换失败: {str(e)}")
            raise ValueError(f"数据库格式转换失败: {str(e)}")