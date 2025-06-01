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

logger = logging.getLogger(__name__)


class GenerationService:
    """内容生成服务"""
    
    def __init__(self, prompt_service: PromptService):
        self.prompt_service = prompt_service
        self.ai_service = get_ai_service()
    
    async def generate_novel_name(
        self,
        request: NovelNameRequest,
        user_id: Optional[int] = None,
        db = None
    ) -> StructuredGenerationResponse:
        """生成小说名"""
        try:
            start_time = time.time()
            
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
            temperature = (request.temperature or prompt_template.default_temperature) / 100.0
            max_tokens = request.max_tokens or prompt_template.default_max_tokens
            
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
    
    async def generate_novel_idea(
        self,
        request: NovelIdeaRequest,
        user_id: Optional[int] = None,
        db = None
    ) -> StructuredGenerationResponse:
        """生成小说创意"""
        try:
            start_time = time.time()
            
            # 检查AI服务是否可用
            if not self.ai_service.is_available(user_id=user_id):
                raise AIServiceError("AI服务当前不可用")
            
            # 构建上下文数据
            context_data = {
                "genre": request.genre or "通用",
                "themes": request.themes or "",
                "length": request.length or "中篇"
            }
            
            # 构建提示词
            prompt = await self.prompt_service.build_prompt(
                prompt_type=PromptType.NOVEL_IDEA,
                context_data=context_data,
                user_input=request.user_input
            )
            
            # 获取响应格式
            prompt_template = await self.prompt_service.get_default_prompt_by_type(
                PromptType.NOVEL_IDEA
            )
            response_format = {}
            if prompt_template and prompt_template.response_format:
                try:
                    response_format = json.loads(prompt_template.response_format)
                except json.JSONDecodeError:
                    logger.warning("提示词响应格式解析失败，使用默认格式")
            
            # 调用AI生成
            temperature = (request.temperature or prompt_template.default_temperature) / 100.0
            max_tokens = request.max_tokens or prompt_template.default_max_tokens
            
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
            logger.error(f"小说创意生成失败: {str(e)}")
            raise AIServiceError(f"小说创意生成失败: {str(e)}")
    
    async def generate_brain_storm(
        self, 
        request: BrainStormRequest
    ) -> StructuredGenerationResponse:
        """生成脑洞创意"""
        try:
            start_time = time.time()
            
            # 检查AI服务是否可用
            if not self.ai_service.is_available():
                raise AIServiceError("AI服务当前不可用")
            
            # 构建上下文数据
            context_data = {
                "topic": request.topic or "创意写作",
                "elements": request.elements or "",
                "creativity_level": request.creativity_level or 80
            }
            
            # 构建提示词
            prompt = await self.prompt_service.build_prompt(
                prompt_type=PromptType.BRAIN_STORM,
                context_data=context_data,
                user_input=request.user_input
            )
            
            # 获取响应格式
            prompt_template = await self.prompt_service.get_default_prompt_by_type(
                PromptType.BRAIN_STORM
            )
            response_format = {}
            if prompt_template and prompt_template.response_format:
                try:
                    response_format = json.loads(prompt_template.response_format)
                except json.JSONDecodeError:
                    logger.warning("提示词响应格式解析失败，使用默认格式")
            
            # 调用AI生成
            temperature = (request.temperature or prompt_template.default_temperature) / 100.0
            max_tokens = request.max_tokens or prompt_template.default_max_tokens
            
            result = await self.ai_service.generate_structured_response(
                prompt=prompt,
                response_format=response_format,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            generation_time = time.time() - start_time
            
            return StructuredGenerationResponse(
                data=result,
                tokens_used=max_tokens,  # 实际应该从AI服务返回
                model_used=self.ai_service.default_adapter,
                generation_time=round(generation_time, 2)
            )
            
        except Exception as e:
            logger.error(f"脑洞生成失败: {str(e)}")
            raise AIServiceError(f"脑洞生成失败: {str(e)}")
    
    async def validate_generation_request(self, request: Dict[str, Any]) -> bool:
        """验证生成请求"""
        try:
            # 检查基本参数
            if request.get("max_tokens", 0) > 8000:
                raise ValueError("max_tokens不能超过8000")
            
            if not (0 <= request.get("temperature", 50) <= 100):
                raise ValueError("temperature必须在0-100之间")
            
            # 检查用户输入长度
            user_input = request.get("user_input", "")
            if len(user_input) > 1000:
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


    async def generate_characters(
        self,
        request: CharacterGenerationRequest,
        novel_info: dict,
        worldview_info: str = ""
    ) -> CharacterGenerationResponse:
        """生成角色"""
        try:
            start_time = time.time()
            
            # 检查AI服务是否可用
            if not self.ai_service.is_available():
                raise AIServiceError("AI服务当前不可用")
            
            # 构建上下文数据
            character_types_str = ", ".join([ct.value for ct in request.character_types]) if request.character_types else "配角"
            
            context_data = {
                "character_count": request.character_count,
                "novel_title": novel_info.get("title", ""),
                "novel_genre": novel_info.get("genre", ""),
                "worldview_info": worldview_info or "无特殊世界观设定",
                "character_types": character_types_str,
                "user_suggestion": request.user_suggestion or ""
            }
            
            # 构建提示词
            prompt = await self.prompt_service.build_prompt(
                prompt_type=PromptType.CHARACTER,
                context_data=context_data,
                user_input=request.user_suggestion
            )
            
            # 获取响应格式
            prompt_template = await self.prompt_service.get_default_prompt_by_type(
                PromptType.CHARACTER
            )
            response_format = {}
            if prompt_template and prompt_template.response_format:
                try:
                    response_format = json.loads(prompt_template.response_format)
                except json.JSONDecodeError:
                    logger.warning("角色生成提示词响应格式解析失败，使用默认格式")
            
            # 调用AI生成
            temperature = prompt_template.default_temperature / 100.0 if prompt_template else 0.8
            max_tokens = prompt_template.default_max_tokens if prompt_template else 2000
            
            result = await self.ai_service.generate_structured_response(
                prompt=prompt,
                response_format=response_format,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            generation_time = time.time() - start_time
            
            # 处理生成结果
            characters_data = result.get("characters", [])
            
            return CharacterGenerationResponse(
                success=True,
                message=f"成功生成 {len(characters_data)} 个角色",
                characters=[],  # 这里会在API层转换为实际的Character对象
                total_generated=len(characters_data),
                generation_data=characters_data  # 添加原始生成数据
            )
            
        except Exception as e:
            logger.error(f"角色生成失败: {str(e)}")
            return CharacterGenerationResponse(
                success=False,
                message=f"角色生成失败: {str(e)}",
                characters=[],
                total_generated=0
            )
    
    async def generate_rough_outline(
        self,
        request: RoughOutlineGenerationRequest,
        novel_info: dict,
        worldview_info: str = "",
        character_info: str = ""
    ) -> OutlineGenerationResponse:
        """生成粗略大纲"""
        try:
            start_time = time.time()
            
            # 检查AI服务是否可用
            if not self.ai_service.is_available():
                raise AIServiceError("AI服务当前不可用")
            
            # 构建上下文数据
            outline_types_str = ", ".join([ot.value for ot in request.outline_types]) if request.outline_types else "故事线, 角色成长路线, 重大事件, 大情节点"
            
            context_data = {
                "novel_title": novel_info.get("title", ""),
                "novel_genre": novel_info.get("genre", ""),
                "worldview_info": worldview_info or "无特殊世界观设定",
                "character_info": character_info or "角色信息待定",
                "target_chapters": request.target_chapters or 100,
                "outline_types": outline_types_str,
                "user_suggestion": request.user_suggestion or ""
            }
            
            # 构建提示词
            prompt = await self.prompt_service.build_prompt(
                prompt_type=PromptType.ROUGH_OUTLINE,
                context_data=context_data,
                user_input=request.user_suggestion
            )
            
            # 获取响应格式
            prompt_template = await self.prompt_service.get_default_prompt_by_type(
                PromptType.ROUGH_OUTLINE
            )
            response_format = {}
            if prompt_template and prompt_template.response_format:
                try:
                    response_format = json.loads(prompt_template.response_format)
                except json.JSONDecodeError:
                    logger.warning("粗略大纲提示词响应格式解析失败，使用默认格式")
            
            # 调用AI生成
            temperature = prompt_template.default_temperature / 100.0 if prompt_template else 0.75
            max_tokens = prompt_template.default_max_tokens if prompt_template else 3000
            
            result = await self.ai_service.generate_structured_response(
                prompt=prompt,
                response_format=response_format,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            generation_time = time.time() - start_time
            
            # 处理生成结果
            rough_outlines_data = result.get("rough_outlines", [])
            
            return OutlineGenerationResponse(
                success=True,
                message=f"成功生成 {len(rough_outlines_data)} 个粗略大纲",
                rough_outlines=[],  # 这里会在API层转换为实际的RoughOutline对象
                detailed_outlines=[],
                total_generated=len(rough_outlines_data),
                generation_data=rough_outlines_data  # 添加原始生成数据
            )
            
        except Exception as e:
            logger.error(f"粗略大纲生成失败: {str(e)}")
            return OutlineGenerationResponse(
                success=False,
                message=f"粗略大纲生成失败: {str(e)}",
                rough_outlines=[],
                detailed_outlines=[],
                total_generated=0
            )
    
    async def generate_detailed_outline(
        self,
        request: DetailedOutlineGenerationRequest,
        novel_info: dict,
        worldview_info: str = "",
        rough_outline_info: str = "",
        character_info: str = ""
    ) -> OutlineGenerationResponse:
        """生成详细大纲"""
        try:
            start_time = time.time()
            
            # 检查AI服务是否可用
            if not self.ai_service.is_available():
                raise AIServiceError("AI服务当前不可用")
            
            # 构建上下文数据
            context_data = {
                "novel_title": novel_info.get("title", ""),
                "novel_genre": novel_info.get("genre", ""),
                "worldview_info": worldview_info or "无特殊世界观设定",
                "rough_outline_info": rough_outline_info or "粗略大纲待定",
                "character_info": character_info or "角色信息待定",
                "start_chapter": request.start_chapter,
                "end_chapter": request.end_chapter,
                "user_suggestion": request.user_suggestion or ""
            }
            
            # 构建提示词
            prompt = await self.prompt_service.build_prompt(
                prompt_type=PromptType.DETAIL_OUTLINE,
                context_data=context_data,
                user_input=request.user_suggestion
            )
            
            # 获取响应格式
            prompt_template = await self.prompt_service.get_default_prompt_by_type(
                PromptType.DETAIL_OUTLINE
            )
            response_format = {}
            if prompt_template and prompt_template.response_format:
                try:
                    response_format = json.loads(prompt_template.response_format)
                except json.JSONDecodeError:
                    logger.warning("详细大纲提示词响应格式解析失败，使用默认格式")
            
            # 调用AI生成
            temperature = prompt_template.default_temperature / 100.0 if prompt_template else 0.75
            max_tokens = prompt_template.default_max_tokens if prompt_template else 4000
            
            result = await self.ai_service.generate_structured_response(
                prompt=prompt,
                response_format=response_format,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            generation_time = time.time() - start_time
            
            # 处理生成结果
            detailed_outlines_data = result.get("detailed_outlines", [])
            
            return OutlineGenerationResponse(
                success=True,
                message=f"成功生成 {len(detailed_outlines_data)} 个详细大纲",
                rough_outlines=[],
                detailed_outlines=[],  # 这里会在API层转换为实际的DetailedOutline对象
                total_generated=len(detailed_outlines_data),
                generation_data=detailed_outlines_data  # 添加原始生成数据
            )
            
        except Exception as e:
            logger.error(f"详细大纲生成失败: {str(e)}")
            return OutlineGenerationResponse(
                success=False,
                message=f"详细大纲生成失败: {str(e)}",
                rough_outlines=[],
                detailed_outlines=[],
                total_generated=0
            )

    async def generate_chapter(
        self,
        request: ChapterGenerationRequest,
        novel_info: dict,
        outline_info: str = "",
        character_info: str = "",
        worldview_info: str = "",
        previous_chapters: str = ""
    ) -> ChapterGenerationResponse:
        """生成章节内容"""
        try:
            start_time = time.time()
            
            # 检查AI服务是否可用
            if not self.ai_service.is_available():
                raise AIServiceError("AI服务当前不可用")
            
            # 构建上下文数据
            context_data = {
                "novel_title": novel_info.get("title", ""),
                "novel_genre": novel_info.get("genre", ""),
                "novel_description": novel_info.get("description", ""),
                "chapter_number": request.chapter_number,
                "target_word_count": request.target_word_count or 2000,
                "worldview_info": worldview_info if request.include_worldview else "",
                "character_info": character_info if request.include_characters else "",
                "outline_info": outline_info if request.include_outline else "",
                "previous_chapters": previous_chapters,
                "user_suggestion": request.user_suggestion or "",
                "generation_params": request.generation_params
            }
            
            # 构建提示词
            prompt = await self.prompt_service.build_prompt(
                prompt_type=PromptType.CHAPTER,
                context_data=context_data,
                user_input=request.user_suggestion
            )
            
            # 获取响应格式
            prompt_template = await self.prompt_service.get_default_prompt_by_type(
                PromptType.CHAPTER
            )
            response_format = {}
            if prompt_template and prompt_template.response_format:
                try:
                    response_format = json.loads(prompt_template.response_format)
                except json.JSONDecodeError:
                    logger.warning("章节生成提示词响应格式解析失败，使用默认格式")
            
            # 调用AI生成
            generation_params = request.generation_params or {}
            temperature = generation_params.get('temperature',
                prompt_template.default_temperature if prompt_template else 75) / 100.0
            max_tokens = generation_params.get('max_tokens',
                prompt_template.default_max_tokens if prompt_template else 4000)
            
            result = await self.ai_service.generate_structured_response(
                prompt=prompt,
                response_format=response_format,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            generation_time = time.time() - start_time
            
            # 处理生成结果
            generated_content = result.get("content", "")
            chapter_title = result.get("title", f"第{request.chapter_number}章")
            
            # 过滤生成的内容
            filtered_content = await self.filter_generated_content(generated_content)
            
            # 计算字数
            word_count = len(filtered_content.replace(" ", "").replace("\n", ""))
            
            return ChapterGenerationResponse(
                success=True,
                message=f"成功生成第{request.chapter_number}章内容，共{word_count}字",
                chapter=None,  # 这里会在API层转换为实际的Chapter对象
                generated_content=filtered_content,
                word_count=word_count,
                generation_data={
                    "title": chapter_title,
                    "content": filtered_content,
                    "word_count": word_count,
                    "generation_time": generation_time,
                    "used_template": prompt_template.name if prompt_template else "default"
                },
                used_prompt_template=prompt_template.name if prompt_template else "default"
            )
            
        except Exception as e:
            logger.error(f"章节生成失败: {str(e)}")
            return ChapterGenerationResponse(
                success=False,
                message=f"章节生成失败: {str(e)}",
                chapter=None,
                generated_content="",
                word_count=0
            )

    async def generate_chapter_continuation(
        self,
        request: ChapterGenerationRequest,
        novel_info: dict,
        current_content: str,
        outline_info: str = "",
        character_info: str = "",
        worldview_info: str = ""
    ) -> ChapterGenerationResponse:
        """生成章节续写内容"""
        try:
            start_time = time.time()
            
            # 检查AI服务是否可用
            if not self.ai_service.is_available():
                raise AIServiceError("AI服务当前不可用")
            
            # 分析当前内容，提取最后几段作为上下文
            content_lines = current_content.strip().split('\n')
            context_lines = content_lines[-3:] if len(content_lines) > 3 else content_lines
            context_preview = '\n'.join(context_lines)
            
            # 构建上下文数据
            context_data = {
                "novel_title": novel_info.get("title", ""),
                "novel_genre": novel_info.get("genre", ""),
                "chapter_number": request.chapter_number,
                "current_content_preview": context_preview,
                "current_word_count": len(current_content.replace(" ", "").replace("\n", "")),
                "target_additional_words": request.target_word_count or 1000,
                "worldview_info": worldview_info if request.include_worldview else "",
                "character_info": character_info if request.include_characters else "",
                "outline_info": outline_info if request.include_outline else "",
                "user_suggestion": request.user_suggestion or "",
                "continuation_mode": True
            }
            
            # 构建续写专用提示词
            continuation_prompt = f"""
基于以下信息，为小说《{novel_info.get('title', '')}》的第{request.chapter_number}章续写内容：

【当前章节末尾内容】
{context_preview}

【续写要求】
- 保持与前文的连贯性和风格一致性
- 目标新增字数：{request.target_word_count or 1000}字
- 推进情节发展，避免原地踏步
- 确保角色行为符合设定

【小说信息】
类型：{novel_info.get('genre', '')}
{f'世界观：{worldview_info}' if worldview_info else ''}
{f'角色信息：{character_info}' if character_info else ''}
{f'大纲要求：{outline_info}' if outline_info else ''}

【用户建议】
{request.user_suggestion or '无特殊要求'}

请直接生成续写内容，不要重复已有内容：
"""
            
            # 调用AI生成
            generation_params = request.generation_params or {}
            temperature = generation_params.get('temperature', 75) / 100.0
            max_tokens = generation_params.get('max_tokens', 3000)
            
            result = await self.ai_service.generate_text(
                prompt=continuation_prompt,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            generation_time = time.time() - start_time
            
            # 过滤生成的内容
            filtered_content = await self.filter_generated_content(result)
            
            # 计算字数
            word_count = len(filtered_content.replace(" ", "").replace("\n", ""))
            
            return ChapterGenerationResponse(
                success=True,
                message=f"成功为第{request.chapter_number}章续写{word_count}字内容",
                chapter=None,
                generated_content=filtered_content,
                word_count=word_count,
                generation_data={
                    "content": filtered_content,
                    "word_count": word_count,
                    "generation_time": generation_time,
                    "continuation_mode": True
                },
                used_prompt_template="chapter_continuation"
            )
            
        except Exception as e:
            logger.error(f"章节续写失败: {str(e)}")
            return ChapterGenerationResponse(
                success=False,
                message=f"章节续写失败: {str(e)}",
                chapter=None,
                generated_content="",
                word_count=0
            )

    async def generate_chapter_rewrite(
        self,
        request: ChapterGenerationRequest,
        novel_info: dict,
        original_content: str,
        outline_info: str = "",
        character_info: str = "",
        worldview_info: str = "",
        rewrite_suggestions: str = ""
    ) -> ChapterGenerationResponse:
        """生成章节重写内容"""
        try:
            start_time = time.time()
            
            # 检查AI服务是否可用
            if not self.ai_service.is_available():
                raise AIServiceError("AI服务当前不可用")
            
            # 分析原始内容结构
            original_word_count = len(original_content.replace(" ", "").replace("\n", ""))
            
            # 构建上下文数据
            context_data = {
                "novel_title": novel_info.get("title", ""),
                "novel_genre": novel_info.get("genre", ""),
                "chapter_number": request.chapter_number,
                "original_content": original_content,
                "original_word_count": original_word_count,
                "target_word_count": request.target_word_count or original_word_count,
                "worldview_info": worldview_info if request.include_worldview else "",
                "character_info": character_info if request.include_characters else "",
                "outline_info": outline_info if request.include_outline else "",
                "rewrite_suggestions": rewrite_suggestions,
                "user_suggestion": request.user_suggestion or "",
                "rewrite_mode": True
            }
            
            # 构建重写专用提示词
            rewrite_prompt = f"""
请为小说《{novel_info.get('title', '')}》的第{request.chapter_number}章进行重写：

【原始章节内容】
{original_content}

【重写要求】
- 保持核心情节不变，优化表达方式
- 目标字数：{request.target_word_count or original_word_count}字
- 提升文笔质量和阅读体验
- 确保角色性格和世界观一致性

【小说信息】
类型：{novel_info.get('genre', '')}
{f'世界观：{worldview_info}' if worldview_info else ''}
{f'角色信息：{character_info}' if character_info else ''}
{f'大纲要求：{outline_info}' if outline_info else ''}

【重写建议】
{rewrite_suggestions or '优化文笔，增强可读性'}

【用户建议】
{request.user_suggestion or '无特殊要求'}

请生成重写后的完整章节内容：
"""
            
            # 调用AI生成
            generation_params = request.generation_params or {}
            temperature = generation_params.get('temperature', 70) / 100.0
            max_tokens = generation_params.get('max_tokens', 5000)
            
            result = await self.ai_service.generate_text(
                prompt=rewrite_prompt,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            generation_time = time.time() - start_time
            
            # 过滤生成的内容
            filtered_content = await self.filter_generated_content(result)
            
            # 计算字数
            word_count = len(filtered_content.replace(" ", "").replace("\n", ""))
            
            return ChapterGenerationResponse(
                success=True,
                message=f"成功重写第{request.chapter_number}章，共{word_count}字",
                chapter=None,
                generated_content=filtered_content,
                word_count=word_count,
                generation_data={
                    "content": filtered_content,
                    "word_count": word_count,
                    "original_word_count": original_word_count,
                    "generation_time": generation_time,
                    "rewrite_mode": True,
                    "improvement_suggestions": rewrite_suggestions
                },
                used_prompt_template="chapter_rewrite"
            )
            
        except Exception as e:
            logger.error(f"章节重写失败: {str(e)}")
            return ChapterGenerationResponse(
                success=False,
                message=f"章节重写失败: {str(e)}",
                chapter=None,
                generated_content="",
                word_count=0
            )

    async def build_chapter_context(
        self,
        novel_info: dict,
        chapter_number: int,
        include_worldview: bool = True,
        include_characters: bool = True,
        include_outline: bool = True,
        character_ids: List[int] = None
    ) -> dict:
        """构建章节生成的上下文信息"""
        try:
            context = {
                "novel_info": novel_info,
                "chapter_number": chapter_number,
                "worldview_info": "",
                "character_info": "",
                "outline_info": "",
                "previous_chapters": ""
            }
            
            # 这里应该从数据库获取相关信息
            # 由于当前没有数据库操作层，这里提供接口预留
            # 实际实现会在API层调用时提供这些信息
            
            return context
            
        except Exception as e:
            logger.error(f"构建章节上下文失败: {str(e)}")
            return {}

    def _determine_chapter_type(self, chapter_number: int, total_chapters: int = None) -> str:
        """判断章节类型（开头、发展、高潮、结尾）"""
        if chapter_number == 1:
            return "opening"
        elif total_chapters and chapter_number >= total_chapters * 0.8:
            return "climax_ending"
        elif total_chapters and chapter_number >= total_chapters * 0.6:
            return "climax"
        else:
            return "development"

    def _analyze_chapter_position(self, chapter_number: int, outline_info: str = "") -> dict:
        """分析章节在故事中的位置和作用"""
        return {
            "position": "middle",  # 开头、中间、结尾
            "narrative_function": "development",  # 发展、转折、高潮等
            "pacing_suggestion": "steady",  # 节奏建议
            "focus_elements": ["plot", "character"]  # 重点元素
        }


def get_generation_service(prompt_service: PromptService) -> GenerationService:
    """获取内容生成服务实例"""
    return GenerationService(prompt_service)