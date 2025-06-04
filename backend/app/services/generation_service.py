"""
内容生成服务
Author: AI Writer Team
Created: 2025-06-01
"""

import logging
import time
import json
from typing import Dict, Any, Optional, List

from app.services.ai_service import get_ai_service, AIServiceError
from app.services.prompt_service import PromptService
from app.services.worldview_converter import WorldviewConverter
from app.schemas.ai_worldview import AIWorldviewResponse
from app.models.prompt import PromptType
from app.schemas.prompt import (
    NovelNameRequest, NovelIdeaRequest, BrainStormRequest,
    GenerationResponse, StructuredGenerationResponse
)
from app.schemas.character import CharacterGenerationRequest, CharacterGenerationResponse
from app.schemas.outline import (
    RoughOutlineGenerationRequest, DetailedOutlineGenerationRequest,
    OutlineGenerationResponse
)
from app.schemas.chapter import (
    ChapterGenerationRequest, ChapterGenerationResponse
)
from app.schemas.worldview import (
    WorldviewGenerationRequest,
    WorldviewGenerationResponse,
    GeneratedWorldBase,
    GeneratedPowerSystem,
    GeneratedLocation,
    GeneratedEra,
    GeneratedArtifact
)

logger = logging.getLogger(__name__)


class GenerationService:
    """内容生成服务"""
    
    def __init__(self, prompt_service: PromptService):
        self.prompt_service = prompt_service
        self.ai_service = get_ai_service()
    
    def _normalize_levels(self, levels):
        """标准化等级数据：将字符串列表转换为字典列表"""
        if not levels:
            return []
        
        normalized = []
        for level in levels:
            if isinstance(level, str):
                # 如果是字符串，转换为字典格式
                normalized.append({
                    "name": level,
                    "description": f"{level}等级",
                    "requirements": "待定"
                })
            elif isinstance(level, dict):
                # 如果已经是字典，直接使用
                normalized.append(level)
            else:
                # 其他类型，转换为字符串后处理
                normalized.append({
                    "name": str(level),
                    "description": f"{str(level)}等级",
                    "requirements": "待定"
                })
        return normalized
    
    def _normalize_cultivation_methods(self, methods):
        """标准化修炼方法：将字典列表转换为字符串列表"""
        if not methods:
            return []
        
        normalized = []
        for method in methods:
            if isinstance(method, dict):
                # 如果是字典，提取名称或描述
                if "name" in method:
                    normalized.append(method["name"])
                elif "description" in method:
                    normalized.append(method["description"])
                else:
                    # 如果没有name或description，使用字典的字符串表示
                    normalized.append(str(method))
            elif isinstance(method, str):
                # 如果已经是字符串，直接使用
                normalized.append(method)
            else:
                # 其他类型，转换为字符串
                normalized.append(str(method))
        return normalized
    
    def _extract_unique_feature_names(self, features):
        """提取特色功能名称：将字典列表转换为字符串列表"""
        if not features:
            return []
        
        normalized = []
        for feature in features:
            if isinstance(feature, dict):
                # 如果是字典，提取名称
                if "name" in feature:
                    normalized.append(feature["name"])
                else:
                    # 如果没有name，使用字典的字符串表示
                    normalized.append(str(feature))
            elif isinstance(feature, str):
                # 如果已经是字符串，直接使用
                normalized.append(feature)
            else:
                # 其他类型，转换为字符串
                normalized.append(str(feature))
        return normalized

    async def generate_worldview(
        self,
        request: WorldviewGenerationRequest,
        user_id: Optional[int] = None,
        db = None
    ) -> WorldviewGenerationResponse:
        """生成世界观内容"""
        try:
            start_time = time.time()
            
            logger.info(f"开始生成世界观: {request.dict()}, 当前用户 {user_id}")
            
            # 检查AI服务是否可用
            if not self.ai_service.is_available(user_id=user_id):
                raise AIServiceError("AI服务当前不可用")
            
            # 获取小说基本设定信息
            novel_settings = {}
            if request.include_novel_settings and db is not None:
                novel_settings = await self._get_novel_settings(request.novel_id, db)
            
            # 提供默认值以防止模板格式化错误
            default_novel_settings = {
                "title": "未命名小说",
                "genre": "通用",
                "author": "佚名",
                "description": "暂无描述",
                "target_audience": "大众",
                "writing_style": "第三人称",
                "target_words": "100000",
                "current_words": "0"
            }
            
            # 合并设定信息，优先使用实际查询到的数据
            final_novel_settings = {**default_novel_settings, **novel_settings}
            
            # 构建上下文数据
            context_data = {
                "genre": request.genre or final_novel_settings.get("genre", "通用"),
                "themes": ", ".join(request.themes) if request.themes else "奇幻, 冒险",
                "style": request.style or final_novel_settings.get("writing_style", "史诗"),
                "worldview_name": request.worldview_name or "未命名世界观",
                "generation_types": ", ".join(request.generation_types) if request.generation_types else "完整世界观",
                "include_novel_settings": request.include_novel_settings,
                "novel_id": request.novel_id,
                "user_input": request.user_suggestion or "",
                # 添加小说基本设定信息（用于模板格式化）
                "novel_settings": final_novel_settings
            }
            
            # 构建提示词
            prompt = await self.prompt_service.build_prompt(
                prompt_type=PromptType.WORLD_VIEW,
                context_data=context_data,
                user_input=request.user_suggestion
            )

            # 获取提示词模板
            prompt_template = await self.prompt_service.get_default_prompt_by_type(
                PromptType.WORLD_VIEW
            )
            
            # 获取响应格式
            response_format = {}
            if prompt_template and prompt_template.response_format:
                try:
                    response_format = json.loads(prompt_template.response_format)
                except json.JSONDecodeError:
                    logger.warning("世界观生成提示词响应格式解析失败，使用默认格式")
            
            # 调用AI生成
            temperature = prompt_template.default_temperature / 100.0 if prompt_template else 0.7
            max_tokens = prompt_template.default_max_tokens if prompt_template else 30000

            result = await self.ai_service.generate_structured_response(
                prompt=prompt,
                response_format=response_format,
                temperature=temperature,
                max_tokens=max_tokens,
                user_id=user_id,
                db=db
            )
            
            generation_time = time.time() - start_time
            
            # 使用转换器处理AI响应
            try:
                converted_data = WorldviewConverter.convert_ai_response(
                    result, user_id or 0, request.novel_id
                )
                
                # 计算总生成项数
                total_items = (
                    1 +  # worldview
                    len(converted_data["world_maps"]) +
                    len(converted_data["special_locations"]) +
                    1 +  # cultivation_system
                    len(converted_data["histories"]) +
                    len(converted_data["artifacts"]) +
                    len(converted_data["factions"])
                )
                
                return WorldviewGenerationResponse(
                    success=True,
                    message=f"成功生成世界观及{total_items}个相关内容",
                    **converted_data,
                    total_generated=total_items
                )
                
            except ValueError as e:
                logger.error(f"世界观数据转换失败: {str(e)}")
                # 降级处理：使用原有逻辑
                return self._fallback_worldview_processing(result)
            
        except Exception as e:
            logger.error(f"世界观生成失败: {str(e)}")
            return WorldviewGenerationResponse(
                success=False,
                message=f"世界观生成失败: {str(e)}",
                worldview=GeneratedWorldBase(
                    name="",
                    description="",
                    background="",
                    rules=[],
                    characteristics=[]
                ),
                cultivation_system=GeneratedPowerSystem(
                    name="",
                    description="",
                    levels=[],
                    unique_features=[],
                    cultivation_methods=[]
                ),
                world_maps=[],
                special_locations=[],
                histories=[],
                artifacts=[],
                factions=[],
                total_generated=0
            )

    async def _get_novel_settings(self, novel_id: int, db) -> Dict[str, Any]:
        """获取小说的基本设定信息"""
        try:
            from app.models.novel import Novel
            from sqlalchemy.orm import Session
            
            # 查询小说信息
            novel = db.query(Novel).filter(Novel.id == novel_id).first()
            
            if not novel:
                logger.warning(f"未找到小说ID: {novel_id}")
                return {}
            
            # 构建小说设定信息
            novel_settings = {
                "title": novel.title,
                "genre": novel.genre.value if novel.genre else None,
                "author": novel.author,
                "description": novel.description or "",
                "target_audience": novel.target_audience.value if novel.target_audience else None,
                "writing_style": novel.writing_style.value if novel.writing_style else None,
                "target_words": novel.target_words,
                "tags": novel.tags,
                "current_words": novel.current_words,
                "chapter_count": novel.chapter_count,
                "status": novel.status.value if novel.status else None
            }
            
            logger.info(f"成功获取小说 {novel_id} 的设定信息")
            return novel_settings
            
        except Exception as e:
            logger.error(f"获取小说设定失败: {str(e)}")
            return {}

    def _fallback_worldview_processing(self, result: Dict[str, Any]) -> WorldviewGenerationResponse:
        """降级处理：使用原有逻辑处理世界观生成结果"""
        try:
            # 处理生成结果
            worldview_data = result.get("world_base", {})
            maps_data = result.get("geography", {}).get("map_regions", [])
            special_locations = result.get("geography", {}).get("special_locations", [])
            power_system = result.get("power_system", {})
            history_data = result.get("history", {}).get("eras", [])
            artifacts = result.get("history", {}).get("significant_artifacts", [])
            factions_data = result.get("factions", [])
            
            # 转换地图数据为简化格式
            simple_maps = []
            for region in maps_data:
                simple_maps.append({
                    "name": region.get("name", ""),
                    "description": region.get("description", ""),
                    "climate": region.get("climate", ""),
                    "notable_features": region.get("notable_features", [])
                })
            
            # 转换阵营数据为简化格式
            simple_factions = []
            for faction in factions_data:
                simple_factions.append({
                    "name": faction.get("name", ""),
                    "description": faction.get("description", ""),
                    "ideology": faction.get("ideology", ""),
                    "alliance": faction.get("alliance", faction.get("allies", ""))
                })
            
            # 计算总生成项数
            total_items = (
                (1 if worldview_data else 0) +
                len(simple_maps) +
                len(special_locations) +
                (1 if power_system else 0) +
                len(history_data) +
                len(artifacts) +
                len(simple_factions)
            )
            
            # 组织返回数据
            response_data = {
                "worldview": GeneratedWorldBase(
                    name=worldview_data.get("name", "未命名世界"),
                    description=worldview_data.get("description", ""),
                    background=worldview_data.get("background", ""),
                    rules=worldview_data.get("rules", []),
                    characteristics=worldview_data.get("characteristics", [])
                ),
                "world_maps": simple_maps,
                "special_locations": [
                    GeneratedLocation(
                        name=loc.get("name", ""),
                        description=loc.get("description", ""),
                        significance=loc.get("significance", ""),
                        mysteries=loc.get("mysteries", [])
                    ) for loc in special_locations
                ],
                "cultivation_system": GeneratedPowerSystem(
                    name=power_system.get("name", ""),
                    description=power_system.get("description", ""),
                    levels=self._normalize_levels(power_system.get("levels", [])),
                    unique_features=self._extract_unique_feature_names(power_system.get("unique_features", [])),
                    cultivation_methods=self._normalize_cultivation_methods(power_system.get("cultivation_methods", []))
                ),
                "histories": [
                    GeneratedEra(
                        name=era.get("name", ""),
                        description=era.get("description", ""),
                        major_events=era.get("key_events", [])
                    ) for era in history_data
                ],
                "artifacts": [
                    GeneratedArtifact(
                        name=art.get("name", ""),
                        description=art.get("description", ""),
                        powers=art.get("powers", []),
                        history=art.get("significance", "")
                    ) for art in artifacts
                ],
                "factions": simple_factions
            }

            return WorldviewGenerationResponse(
                success=True,
                message=f"成功生成世界观及{total_items}个相关内容（使用降级处理）",
                **response_data,
                total_generated=total_items
            )
            
        except Exception as e:
            logger.error(f"降级处理也失败: {str(e)}")
            # 返回默认的空结果
            return WorldviewGenerationResponse(
                success=False,
                message=f"世界观生成失败: {str(e)}",
                worldview=GeneratedWorldBase(
                    name="",
                    description="",
                    background="",
                    rules=[],
                    characteristics=[]
                ),
                cultivation_system=GeneratedPowerSystem(
                    name="",
                    description="",
                    levels=[],
                    unique_features=[],
                    cultivation_methods=[]
                ),
                world_maps=[],
                special_locations=[],
                histories=[],
                artifacts=[],
                factions=[],
                total_generated=0
            )

    async def generate_novel_name(
        self,
        request: NovelNameRequest,
        user_id: Optional[int] = None,
        db = None
    ) -> StructuredGenerationResponse:
        """生成小说名"""
        try:
            start_time = time.time()

            logger.info(f"小说名生成开始: {request.dict()}, 当前用户 {user_id}")
            
            # 检查AI服务是否可用
            if not self.ai_service.is_available(user_id=user_id):
                raise AIServiceError("AI服务当前不可用")
            
            # 构建上下文数据
            context_data = {
                "genre": request.genre or "通用",
                "keywords": request.keywords or "",
                "style": request.style or "吸引人的"
            }
            
            # 构建提示词
            prompt = await self.prompt_service.build_prompt(
                prompt_type=PromptType.NOVEL_NAME,
                context_data=context_data,
                user_input=request.user_input
            )
            
            # 获取响应格式
            prompt_template = await self.prompt_service.get_default_prompt_by_type(
                PromptType.NOVEL_NAME
            )
            response_format = {}
            if prompt_template and prompt_template.response_format:
                try:
                    response_format = json.loads(prompt_template.response_format)
                except json.JSONDecodeError:
                    logger.warning("提示词响应格式解析失败，使用默认格式")
            
            # 调用AI生成
            temperature = (request.temperature or prompt_template.default_temperature if prompt_template else 70) / 100.0
            max_tokens = request.max_tokens or (prompt_template.default_max_tokens if prompt_template else 30000)
            
            result = await self.ai_service.generate_structured_response(
                prompt=prompt,
                response_format=response_format,
                temperature=temperature,
                max_tokens=max_tokens,
                user_id=user_id,
                db=db
            )
            
            generation_time = time.time() - start_time
            
            return StructuredGenerationResponse(
                data=result,
                tokens_used=max_tokens,  # 实际应该从AI服务返回
                model_used=self.ai_service.default_adapter,
                generation_time=round(generation_time, 2)
            )
            
        except Exception as e:
            logger.error(f"小说名生成失败: {str(e)}")
            raise AIServiceError(f"小说名生成失败: {str(e)}")

    async def generate_world_maps(
        self,
        worldview_id: int,
        parent_region = None,
        request_params: Dict[str, Any] = None,
        user_id: Optional[int] = None,
        db = None
    ) -> Dict[str, Any]:
        """生成世界地图区域"""
        try:
            start_time = time.time()
            
            logger.info(f"开始生成地图区域: worldview_id={worldview_id}, parent_region={parent_region}")
            
            # 检查AI服务是否可用
            if not self.ai_service.is_available(user_id=user_id):
                raise AIServiceError("AI服务当前不可用")
            
            # 获取世界观信息
            worldview_info = await self._get_worldview_context(worldview_id, db)
            
            # 构建父区域上下文
            parent_context = ""
            if parent_region:
                parent_context = f"""
父区域信息：
- 名称：{parent_region.region_name}
- 描述：{parent_region.description}
- 气候：{parent_region.climate or '未知'}
- 地形：{parent_region.terrain or '未知'}
- 层级：{parent_region.level}

请生成这个父区域的子区域，确保与父区域的设定保持一致。
"""
            
            # 获取请求参数
            count = request_params.get("count", 3)
            include_features = request_params.get("include", [])
            user_suggestion = request_params.get("suggestion", "")
            
            # 构建上下文数据
            context_data = {
                "worldview_name": worldview_info.get("name", "未命名世界观"),
                "worldview_description": worldview_info.get("description", ""),
                "parent_context": parent_context,
                "generation_count": count,
                "include_climate": "climate" in include_features,
                "include_terrain": "terrain" in include_features,
                "include_resources": "resources" in include_features,
                "include_population": "population" in include_features,
                "include_culture": "culture" in include_features,
                "user_suggestion": user_suggestion
            }
            
            # 构建专门的地图生成提示词
            map_prompt = f"""
作为一个世界观设计师，请为"{worldview_info.get('name', '未命名世界观')}"生成{count}个地图区域。

世界观背景：
{worldview_info.get('description', '暂无描述')}

{parent_context}

生成要求：
1. 生成{count}个不同的地图区域
2. 每个区域都要有独特的特色和设定
3. 区域之间要有逻辑联系和层次关系
{'4. 包含气候特征描述' if 'climate' in include_features else ''}
{'5. 包含地形地貌描述' if 'terrain' in include_features else ''}
{'6. 包含自然资源描述' if 'resources' in include_features else ''}
{'7. 包含人口分布描述' if 'population' in include_features else ''}
{'8. 包含文化特色描述' if 'culture' in include_features else ''}

用户建议：{user_suggestion}

请按照以下JSON格式返回：
{{
    "generated_maps": [
        {{
            "name": "区域名称",
            "description": "详细的区域描述，包含历史背景和特色",
            "climate": "气候特征（如果需要）",
            "terrain": "地形地貌（如果需要）",
            "resources": "主要自然资源（如果需要）",
            "population": "人口分布情况（如果需要）",
            "culture": "文化特色（如果需要）"
        }}
    ]
}}
"""
            
            # 调用AI生成
            result = await self.ai_service.generate_structured_response(
                prompt=map_prompt,
                response_format={
                    "type": "object",
                    "properties": {
                        "generated_maps": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "description": {"type": "string"},
                                    "climate": {"type": "string"},
                                    "terrain": {"type": "string"},
                                    "resources": {"type": "string"},
                                    "population": {"type": "string"},
                                    "culture": {"type": "string"}
                                },
                                "required": ["name", "description"]
                            }
                        }
                    }
                }
                ,
                temperature=0.7,
                max_tokens=4000,
                user_id=user_id,
                db=db
            )
            
            generation_time = time.time() - start_time
            
            # 处理生成结果
            generated_maps = result.get("generated_maps", [])
            
            # 确保每个地图区域都有基本字段
            for map_data in generated_maps:
                if "climate" not in map_data:
                    map_data["climate"] = ""
                if "terrain" not in map_data:
                    map_data["terrain"] = ""
                if "resources" not in map_data:
                    map_data["resources"] = ""
                if "population" not in map_data:
                    map_data["population"] = ""
                if "culture" not in map_data:
                    map_data["culture"] = ""
            
            return {
                "generated_maps": generated_maps,
                "generation_time": round(generation_time, 2),
                "total_count": len(generated_maps),
                "parent_region_id": parent_region.id if parent_region else None,
                "worldview_id": worldview_id
            }
            
        except Exception as e:
            logger.error(f"地图生成失败: {str(e)}")
            raise AIServiceError(f"地图生成失败: {str(e)}")
    
    async def _get_worldview_context(self, worldview_id: int, db) -> Dict[str, Any]:
        """获取世界观上下文信息"""
        try:
            from app.models.worldview import Worldview
            
            worldview = db.query(Worldview).filter(Worldview.id == worldview_id).first()
            
            if not worldview:
                logger.warning(f"未找到世界观ID: {worldview_id}")
                return {}
            
            return {
                "name": worldview.name,
                "description": worldview.description or "",
                "is_primary": worldview.is_primary
            }
            
        except Exception as e:
            logger.error(f"获取世界观上下文失败: {str(e)}")
            return {}

    async def generate_cultivation_system(
        self,
        worldview_id: int,
        request_params: Dict[str, Any] = None,
        user_id: Optional[int] = None,
        db = None
    ) -> Dict[str, Any]:
        """生成修炼体系"""
        try:
            start_time = time.time()
            
            logger.info(f"开始生成修炼体系: worldview_id={worldview_id}")
            
            # 检查AI服务是否可用
            if not self.ai_service.is_available(user_id=user_id):
                raise AIServiceError("AI服务当前不可用")
            
            # 获取世界观信息
            worldview_info = await self._get_worldview_context(worldview_id, db)
            
            # 获取请求参数
            system_name = request_params.get("system_name", "")
            level_count = request_params.get("level_count", 9)
            include_features = request_params.get("include", [])
            user_suggestion = request_params.get("suggestion", "")
            
            # 构建上下文数据
            context_data = {
                "worldview_name": worldview_info.get("name", "未命名世界观"),
                "worldview_description": worldview_info.get("description", ""),
                "system_name": system_name,
                "level_count": level_count,
                "include_cultivation_method": "cultivation_method" in include_features,
                "include_required_resources": "required_resources" in include_features,
                "include_breakthrough_condition": "breakthrough_condition" in include_features,
                "include_power_description": "power_description" in include_features,
                "user_suggestion": user_suggestion
            }
            
            # 构建修炼体系生成提示词
            cultivation_prompt = f"""
作为一个修真世界设计师，请为"{worldview_info.get('name', '未命名世界观')}"设计一个完整的修炼体系。

世界观背景：
{worldview_info.get('description', '暂无描述')}

修炼体系要求：
1. 体系名称：{system_name or '请自动命名'}
2. 等级数量：{level_count}个等级
3. 每个等级都要有清晰的划分和特色
4. 等级间要有合理的递进关系
{'5. 包含详细的修炼方法描述' if 'cultivation_method' in include_features else ''}
{'6. 包含所需资源和材料说明' if 'required_resources' in include_features else ''}
{'7. 包含突破条件和要求' if 'breakthrough_condition' in include_features else ''}
{'8. 包含该等级的力量描述' if 'power_description' in include_features else ''}

用户建议：{user_suggestion}

请按照以下JSON格式返回：
{{
    "generated_systems": [
        {{
            "system_name": "修炼体系名称",
            "description": "体系整体描述",
            "levels": [
                {{
                    "name": "等级名称",
                    "description": "等级描述和特点",
                    "cultivation_method": "修炼方法（如果需要）",
                    "required_resources": "所需资源（如果需要）",
                    "breakthrough_condition": "突破条件（如果需要）",
                    "power_description": "力量描述（如果需要）"
                }}
            ]
        }}
    ]
}}
"""
            
            # 调用AI生成
            result = await self.ai_service.generate_structured_response(
                prompt=cultivation_prompt,
                response_format={
                    "type": "object",
                    "properties": {
                        "generated_systems": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "system_name": {"type": "string"},
                                    "description": {"type": "string"},
                                    "levels": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "name": {"type": "string"},
                                                "description": {"type": "string"},
                                                "cultivation_method": {"type": "string"},
                                                "required_resources": {"type": "string"},
                                                "breakthrough_condition": {"type": "string"},
                                                "power_description": {"type": "string"}
                                            },
                                            "required": ["name", "description"]
                                        }
                                    }
                                },
                                "required": ["system_name", "levels"]
                            }
                        }
                    }
                },
                temperature=0.7,
                max_tokens=6000,
                user_id=user_id,
                db=db
            )
            
            generation_time = time.time() - start_time
            
            # 处理生成结果
            generated_systems = result.get("generated_systems", [])
            
            # 确保每个等级都有基本字段
            for system_data in generated_systems:
                levels = system_data.get("levels", [])
                for level_data in levels:
                    if "cultivation_method" not in level_data:
                        level_data["cultivation_method"] = ""
                    if "required_resources" not in level_data:
                        level_data["required_resources"] = ""
                    if "breakthrough_condition" not in level_data:
                        level_data["breakthrough_condition"] = ""
                    if "power_description" not in level_data:
                        level_data["power_description"] = ""
            
            # 计算总生成的等级数量
            total_levels = sum(len(system.get("levels", [])) for system in generated_systems)
            
            return {
                "generated_systems": generated_systems,
                "generation_time": round(generation_time, 2),
                "total_systems": len(generated_systems),
                "total_levels": total_levels,
                "worldview_id": worldview_id
            }
            
        except Exception as e:
            logger.error(f"修炼体系生成失败: {str(e)}")
            raise AIServiceError(f"修炼体系生成失败: {str(e)}")

    async def validate_generation_request(self, request: Dict[str, Any]) -> bool:
        """验证生成请求"""
        try:
            # 检查基本参数
            max_tokens = request.get("max_tokens")
            if max_tokens is not None and max_tokens > 8000:
                raise ValueError("max_tokens不能超过8000")
            
            temperature = request.get("temperature")
            if temperature is not None and not (0 <= temperature <= 100):
                raise ValueError("temperature必须在0-100之间")
            
            # 检查用户输入长度
            user_input = request.get("user_input", "")
            if user_input and len(user_input) > 1000:
                raise ValueError("用户输入不能超过1000字符")
            
            return True
            
        except Exception as e:
            logger.error(f"生成请求验证失败: {str(e)}")
            return False

    async def filter_generated_content(self, content: str) -> str:
        """过滤生成的内容"""
        try:
            # 基础内容过滤
            filtered_content = content.strip()
            
            # 移除可能的敏感信息标记
            sensitive_markers = ["[FILTERED]", "[CENSORED]", "[BLOCKED]"]
            for marker in sensitive_markers:
                filtered_content = filtered_content.replace(marker, "")
            
            # 长度限制
            if len(filtered_content) > 10000:
                filtered_content = filtered_content[:10000] + "..."
                logger.warning("生成内容超长，已截断")
            
            return filtered_content
            
        except Exception as e:
            logger.error(f"内容过滤失败: {str(e)}")
            return content
    
    def get_service_status(self) -> Dict[str, Any]:
        """获取服务状态"""
        return {
            "ai_service_available": self.ai_service.is_available(),
            "available_adapters": self.ai_service.get_available_adapters(),
            "default_adapter": self.ai_service.default_adapter
        }


def get_generation_service(prompt_service: PromptService) -> GenerationService:
    """获取内容生成服务实例"""
    return GenerationService(prompt_service)