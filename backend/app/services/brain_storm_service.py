"""
脑洞生成器服务
Author: AI Writer Team
Created: 2025-06-03
"""

import logging
import time
import json
import uuid
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from app.services.ai_service import get_ai_service, AIServiceError
from app.services.prompt_service import PromptService
from app.models.prompt import PromptType
from app.models.brain_storm import (
    BrainStormHistory, BrainStormIdea, BrainStormPreferences,
    BrainStormElements, BrainStormTopicSuggestion
)
from app.schemas.brain_storm import (
    BrainStormRequest, BrainStormResponse, GeneratedIdea,
    BrainStormHistoryResponse, BrainStormHistoryItem, BrainStormHistoryDetail,
    ElementSuggestionsResponse, ElementCategory, ElementItem,
    TopicSuggestionsResponse, TopicSuggestion,
    UserPreferences, SavePreferencesRequest,
    GenerationStats, RateGenerationRequest
)

logger = logging.getLogger(__name__)


class BrainStormService:
    """脑洞生成器服务"""
    
    def __init__(self, prompt_service: PromptService, db: Session):
        self.prompt_service = prompt_service
        self.db = db
        self.ai_service = get_ai_service()
    
    async def generate_brain_storm(
        self,
        request: BrainStormRequest,
        user_id: int
    ) -> BrainStormResponse:
        """生成脑洞创意"""
        try:
            start_time = time.time()
            generation_id = str(uuid.uuid4())
            
            logger.info(f"用户 {user_id} 开始脑洞生成: {request.topic}")
            
            # 检查AI服务是否可用
            if not self.ai_service.is_available(user_id=user_id):
                raise AIServiceError("AI服务当前不可用")
            
            # 构建上下文数据
            context_data = {
                "topic": request.topic,
                "creativity_level": request.creativity_level or 7,
                "idea_count": request.idea_count or 10,
                "idea_types": request.idea_type or ["mixed"],
                "elements": request.elements or [],
                "style": request.style or "富有创意",
                "language": request.language or "zh-CN",
                "avoid_keywords": request.avoid_keywords or [],
                "reference_works": request.reference_works or []
            }
            
            # 构建提示词
            prompt = await self._build_brain_storm_prompt(context_data, request.user_input)
            
            # 获取响应格式
            response_format = await self._get_response_format()
            
            # 调用AI生成
            temperature = (request.temperature or 70) / 100.0
            max_tokens = request.max_tokens or 4000
            
            result = await self.ai_service.generate_structured_response(
                prompt=prompt,
                response_format=response_format,
                temperature=temperature,
                max_tokens=max_tokens,
                user_id=user_id,
                db=self.db
            )
            
            generation_time = time.time() - start_time
            
            # 处理生成结果
            ideas_data = result.get("ideas", [])
            generated_ideas = []
            
            for i, idea_data in enumerate(ideas_data):
                idea = GeneratedIdea(
                    id=f"{generation_id}_{i}",
                    content=idea_data.get("content", ""),
                    type=idea_data.get("type", "mixed"),
                    tags=idea_data.get("tags", []),
                    creativity_score=idea_data.get("creativity_score"),
                    practical_score=idea_data.get("practical_score"),
                    summary=idea_data.get("summary"),
                    potential_development=idea_data.get("potential_development"),
                    related_elements=idea_data.get("related_elements", [])
                )
                generated_ideas.append(idea)
            
            # 保存历史记录
            await self._save_generation_history(
                generation_id=generation_id,
                user_id=user_id,
                request=request,
                ideas=generated_ideas,
                generation_time=generation_time,
                model_used=self.ai_service.default_adapter
            )
            
            # 更新要素使用统计
            if request.elements:
                await self._update_elements_stats(request.elements)
            
            # 构建响应
            metadata = {
                "topic": request.topic,
                "parameters": request.dict(),
                "generation_time": round(generation_time, 2),
                "model_used": self.ai_service.default_adapter,
                "prompt_tokens": max_tokens,  # 实际应该从AI服务返回
                "completion_tokens": len(str(result))  # 简化计算
            }
            
            response = BrainStormResponse(
                success=True,
                ideas=generated_ideas,
                generation_id=generation_id,
                metadata=metadata
            )
            
            logger.info(f"用户 {user_id} 脑洞生成成功，生成 {len(generated_ideas)} 个创意")
            return response
            
        except Exception as e:
            logger.error(f"脑洞生成失败: {str(e)}")
            raise AIServiceError(f"脑洞生成失败: {str(e)}")
    
    async def get_generation_history(
        self,
        user_id: int,
        limit: int = 20,
        offset: int = 0
    ) -> BrainStormHistoryResponse:
        """获取生成历史"""
        try:
            # 查询历史记录
            query = self.db.query(BrainStormHistory).filter(
                BrainStormHistory.user_id == user_id
            ).order_by(desc(BrainStormHistory.created_at))
            
            total = query.count()
            history_records = query.offset(offset).limit(limit).all()
            
            # 转换为响应格式
            history_items = []
            for record in history_records:
                item = BrainStormHistoryItem(
                    id=record.id,
                    generation_id=record.generation_id,
                    topic=record.topic,
                    creativity_level=record.creativity_level,
                    idea_count=record.idea_count,
                    ideas_generated=record.ideas_generated,
                    generation_time=record.generation_time,
                    rating=record.rating,
                    created_at=record.created_at
                )
                history_items.append(item)
            
            return BrainStormHistoryResponse(
                history=history_items,
                total=total,
                limit=limit,
                offset=offset
            )
            
        except Exception as e:
            logger.error(f"获取生成历史失败: {str(e)}")
            raise
    
    async def get_history_detail(
        self,
        history_id: int,
        user_id: int
    ) -> BrainStormHistoryDetail:
        """获取历史详情"""
        try:
            # 查询历史记录
            history_record = self.db.query(BrainStormHistory).filter(
                BrainStormHistory.id == history_id,
                BrainStormHistory.user_id == user_id
            ).first()
            
            if not history_record:
                raise ValueError("历史记录不存在")
            
            # 获取创意列表
            ideas = []
            for idea_record in history_record.ideas:
                idea = GeneratedIdea(
                    id=idea_record.idea_id,
                    content=idea_record.content,
                    type=idea_record.idea_type or "mixed",
                    tags=idea_record.tags or [],
                    creativity_score=idea_record.creativity_score,
                    practical_score=idea_record.practical_score,
                    summary=idea_record.summary,
                    potential_development=idea_record.potential_development,
                    related_elements=idea_record.related_elements or []
                )
                ideas.append(idea)
            
            # 构建历史项
            history_item = BrainStormHistoryItem(
                id=history_record.id,
                generation_id=history_record.generation_id,
                topic=history_record.topic,
                creativity_level=history_record.creativity_level,
                idea_count=history_record.idea_count,
                ideas_generated=history_record.ideas_generated,
                generation_time=history_record.generation_time,
                rating=history_record.rating,
                created_at=history_record.created_at
            )
            
            # 使用统计
            usage_stats = {
                "copied_count": history_record.copied_count,
                "exported_count": history_record.exported_count,
                "applied_count": history_record.applied_count
            }
            
            return BrainStormHistoryDetail(
                history=history_item,
                ideas=ideas,
                usage_stats=usage_stats
            )
            
        except Exception as e:
            logger.error(f"获取历史详情失败: {str(e)}")
            raise
    
    async def get_element_suggestions(
        self,
        category: Optional[str] = None
    ) -> ElementSuggestionsResponse:
        """获取要素建议"""
        try:
            query = self.db.query(BrainStormElements).filter(
                BrainStormElements.is_active == True
            )
            
            if category:
                query = query.filter(BrainStormElements.category == category)
            
            elements = query.order_by(
                desc(BrainStormElements.is_featured),
                desc(BrainStormElements.effectiveness_score)
            ).all()
            
            # 按分类组织
            categories_dict = {}
            for element in elements:
                if element.category not in categories_dict:
                    categories_dict[element.category] = []
                
                element_item = ElementItem(
                    name=element.name,
                    description=element.description or "",
                    usage_count=element.usage_count,
                    effectiveness_score=element.effectiveness_score,
                    related_elements=element.related_elements or []
                )
                categories_dict[element.category].append(element_item)
            
            # 转换为响应格式
            categories = []
            for cat_name, cat_elements in categories_dict.items():
                category_item = ElementCategory(
                    category=cat_name,
                    display_name=self._get_category_display_name(cat_name),
                    elements=cat_elements
                )
                categories.append(category_item)
            
            return ElementSuggestionsResponse(categories=categories)
            
        except Exception as e:
            logger.error(f"获取要素建议失败: {str(e)}")
            raise
    
    async def get_topic_suggestions(
        self,
        query: Optional[str] = None,
        limit: int = 10
    ) -> TopicSuggestionsResponse:
        """获取主题建议"""
        try:
            db_query = self.db.query(BrainStormTopicSuggestion).filter(
                BrainStormTopicSuggestion.is_active == True
            )
            
            if query:
                db_query = db_query.filter(
                    BrainStormTopicSuggestion.topic.contains(query)
                )
            
            topics = db_query.order_by(
                desc(BrainStormTopicSuggestion.is_trending),
                desc(BrainStormTopicSuggestion.popularity)
            ).limit(limit).all()
            
            suggestions = []
            for topic in topics:
                suggestion = TopicSuggestion(
                    topic=topic.topic,
                    description=topic.description or "",
                    popularity=topic.popularity,
                    expected_ideas=topic.expected_ideas,
                    related_topics=topic.related_topics or [],
                    sample_ideas=topic.sample_ideas or []
                )
                suggestions.append(suggestion)
            
            return TopicSuggestionsResponse(suggestions=suggestions)
            
        except Exception as e:
            logger.error(f"获取主题建议失败: {str(e)}")
            raise
    
    async def get_user_preferences(self, user_id: int) -> UserPreferences:
        """获取用户偏好"""
        try:
            preferences = self.db.query(BrainStormPreferences).filter(
                BrainStormPreferences.user_id == user_id
            ).first()
            
            if not preferences:
                # 创建默认偏好
                preferences = BrainStormPreferences(user_id=user_id)
                self.db.add(preferences)
                self.db.commit()
                self.db.refresh(preferences)
            
            return UserPreferences(
                default_creativity_level=preferences.default_creativity_level,
                default_idea_count=preferences.default_idea_count,
                preferred_types=preferences.preferred_types or [],
                favorite_elements=preferences.favorite_elements or [],
                default_style=preferences.default_style,
                auto_save_history=preferences.auto_save_history,
                enable_notifications=preferences.enable_notifications,
                show_creativity_scores=preferences.show_creativity_scores,
                enable_auto_suggestions=preferences.enable_auto_suggestions,
                preferred_layout=preferences.preferred_layout,
                items_per_page=preferences.items_per_page,
                enable_dark_mode=preferences.enable_dark_mode,
                updated_at=preferences.updated_at
            )
            
        except Exception as e:
            logger.error(f"获取用户偏好失败: {str(e)}")
            raise
    
    async def save_user_preferences(
        self,
        user_id: int,
        request: SavePreferencesRequest
    ) -> UserPreferences:
        """保存用户偏好"""
        try:
            preferences = self.db.query(BrainStormPreferences).filter(
                BrainStormPreferences.user_id == user_id
            ).first()
            
            if not preferences:
                preferences = BrainStormPreferences(user_id=user_id)
                self.db.add(preferences)
            
            # 更新偏好设置
            update_data = request.dict(exclude_unset=True)
            for field, value in update_data.items():
                if hasattr(preferences, field):
                    setattr(preferences, field, value)
            
            self.db.commit()
            self.db.refresh(preferences)
            
            return await self.get_user_preferences(user_id)
            
        except Exception as e:
            logger.error(f"保存用户偏好失败: {str(e)}")
            raise
    
    async def rate_generation(
        self,
        generation_id: str,
        user_id: int,
        request: RateGenerationRequest
    ) -> Dict[str, Any]:
        """评价生成结果"""
        try:
            # 查找历史记录
            history = self.db.query(BrainStormHistory).filter(
                BrainStormHistory.generation_id == generation_id,
                BrainStormHistory.user_id == user_id
            ).first()
            
            if not history:
                raise ValueError("生成记录不存在")
            
            # 更新评分和反馈
            history.rating = request.rating
            history.user_feedback = request.feedback
            history.useful_ideas = request.useful_ideas or []
            
            # 更新有用创意的用户评分
            if request.useful_ideas:
                for idea in history.ideas:
                    if idea.idea_id in request.useful_ideas:
                        idea.user_rating = 5  # 标记为有用
                        idea.is_favorite = True
            
            self.db.commit()
            
            # 计算平均评分
            avg_rating = self.db.query(func.avg(BrainStormHistory.rating)).filter(
                BrainStormHistory.user_id == user_id,
                BrainStormHistory.rating.isnot(None)
            ).scalar() or 0.0
            
            return {
                "success": True,
                "average_rating": float(avg_rating),
                "feedback_received": bool(request.feedback)
            }
            
        except Exception as e:
            logger.error(f"评价生成结果失败: {str(e)}")
            raise
    
    async def get_generation_stats(self, user_id: int) -> GenerationStats:
        """获取生成统计"""
        try:
            # 基础统计
            total_generations = self.db.query(BrainStormHistory).filter(
                BrainStormHistory.user_id == user_id
            ).count()
            
            total_ideas = self.db.query(func.sum(BrainStormHistory.ideas_generated)).filter(
                BrainStormHistory.user_id == user_id
            ).scalar() or 0
            
            avg_ideas = total_ideas / total_generations if total_generations > 0 else 0
            
            # 创意程度分布
            creativity_dist = self.db.query(
                BrainStormHistory.creativity_level,
                func.count(BrainStormHistory.id)
            ).filter(
                BrainStormHistory.user_id == user_id
            ).group_by(BrainStormHistory.creativity_level).all()
            
            creativity_distribution = [
                {"level": level, "count": count}
                for level, count in creativity_dist
            ]
            
            # 最受欢迎要素（简化实现）
            most_popular_elements = ["玄幻", "科幻", "爱情", "冒险", "悬疑"]
            
            # 使用趋势（简化实现）
            usage_trends = [
                {"date": "2025-06-01", "generations": 5},
                {"date": "2025-06-02", "generations": 8},
                {"date": "2025-06-03", "generations": 12}
            ]
            
            return GenerationStats(
                total_generations=total_generations,
                total_ideas=total_ideas,
                average_ideas_per_generation=round(avg_ideas, 2),
                most_popular_elements=most_popular_elements,
                creativity_distribution=creativity_distribution,
                usage_trends=usage_trends
            )
            
        except Exception as e:
            logger.error(f"获取生成统计失败: {str(e)}")
            raise
    
    async def _build_brain_storm_prompt(
        self,
        context_data: Dict[str, Any],
        user_input: Optional[str] = None
    ) -> str:
        """构建脑洞生成提示词"""
        try:
            # 尝试从数据库获取提示词模板
            prompt = await self.prompt_service.build_prompt(
                prompt_type=PromptType.BRAIN_STORM,
                context_data=context_data,
                user_input=user_input
            )
            return prompt
        except Exception:
            # 如果模板不存在，使用默认提示词
            return self._build_default_brain_storm_prompt(context_data, user_input)
    
    def _build_default_brain_storm_prompt(
        self,
        context_data: Dict[str, Any],
        user_input: Optional[str] = None
    ) -> str:
        """构建默认脑洞生成提示词"""
        prompt = f"""
你是一个专业的创意生成助手，请根据以下要求生成脑洞创意：

主题：{context_data['topic']}
创意程度：{context_data['creativity_level']}/10 (1=保守，10=极具创意)
生成数量：{context_data['idea_count']}个
创意类型：{', '.join(context_data['idea_types'])}
相关要素：{', '.join(context_data['elements'])}
生成风格：{context_data['style']}

{f"用户补充：{user_input}" if user_input else ""}

请生成{context_data['idea_count']}个富有创意的想法，每个想法都要：
1. 内容新颖有趣，符合主题
2. 具有一定的可行性和发展潜力
3. 包含简要的发展方向建议

请以JSON格式返回结果：
{{
  "ideas": [
    {{
      "content": "创意内容描述",
      "type": "创意类型",
      "tags": ["标签1", "标签2"],
      "creativity_score": 创意评分(0-10),
      "practical_score": 实用性评分(0-10),
      "summary": "一句话总结",
      "potential_development": "发展潜力描述",
      "related_elements": ["相关要素"]
    }}
  ]
}}
"""
        return prompt
    
    async def _get_response_format(self) -> Dict[str, Any]:
        """获取响应格式"""
        return {
            "type": "object",
            "properties": {
                "ideas": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "content": {"type": "string"},
                            "type": {"type": "string"},
                            "tags": {"type": "array", "items": {"type": "string"}},
                            "creativity_score": {"type": "number"},
                            "practical_score": {"type": "number"},
                            "summary": {"type": "string"},
                            "potential_development": {"type": "string"},
                            "related_elements": {"type": "array", "items": {"type": "string"}}
                        }
                    }
                }
            }
        }
    
    async def _save_generation_history(
        self,
        generation_id: str,
        user_id: int,
        request: BrainStormRequest,
        ideas: List[GeneratedIdea],
        generation_time: float,
        model_used: str
    ):
        """保存生成历史"""
        try:
            # 创建历史记录
            history = BrainStormHistory(
                user_id=user_id,
                generation_id=generation_id,
                topic=request.topic,
                creativity_level=request.creativity_level or 7,
                idea_count=request.idea_count or 10,
                idea_types=request.idea_type,
                elements=request.elements,
                style=request.style,
                language=request.language or "zh-CN",
                avoid_keywords=request.avoid_keywords,
                reference_works=request.reference_works,
                ideas_generated=len(ideas),
                generation_time=generation_time,
                model_used=model_used
            )
            
            self.db.add(history)
            self.db.flush()  # 获取ID
            
            # 保存创意
            for idea in ideas:
                idea_record = BrainStormIdea(
                    history_id=history.id,
                    idea_id=idea.id,
                    content=idea.content,
                    idea_type=idea.type,
                    summary=idea.summary,
                    potential_development=idea.potential_development,
                    creativity_score=idea.creativity_score,
                    practical_score=idea.practical_score,
                    tags=idea.tags,
                    related_elements=idea.related_elements
                )
                self.db.add(idea_record)
            
            self.db.commit()
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"保存生成历史失败: {str(e)}")
            raise
    
    async def _update_elements_stats(self, elements: List[str]):
        """更新要素使用统计"""
        try:
            for element_name in elements:
                element = self.db.query(BrainStormElements).filter(
                    BrainStormElements.name == element_name
                ).first()
                
                if element:
                    element.usage_count += 1
                    # 简化的效果评分更新
                    element.effectiveness_score = min(
                        element.effectiveness_score + 0.1,
                        10.0
                    )
                else:
                    # 创建新要素
                    new_element = BrainStormElements(
                        name=element_name,
                        display_name=element_name,
                        category="custom",
                        usage_count=1,
                        effectiveness_score=5.0
                    )
                    self.db.add(new_element)
            
            self.db.commit()
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"更新要素统计失败: {str(e)}")
    
    def _get_category_display_name(self, category: str) -> str:
        """获取分类显示名称"""
        category_names = {
            "genre": "类型",
            "element": "要素",
            "theme": "主题",
            "style": "风格",
            "custom": "自定义"
        }
        return category_names.get(category, category)


def get_brain_storm_service(prompt_service: PromptService, db: Session) -> BrainStormService:
    """获取脑洞生成器服务实例"""
    return BrainStormService(prompt_service, db)