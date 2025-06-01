"""
内容生成服务
Author: AI Writer Team
Created: 2025-06-01
"""

import logging
import time
import json
from typing import Dict, Any, Optional

from app.services.ai_service import get_ai_service, AIServiceError
from app.services.prompt_service import PromptService
from app.models.prompt import PromptType
from app.schemas.prompt import (
    NovelNameRequest, NovelIdeaRequest, BrainStormRequest,
    GenerationResponse, StructuredGenerationResponse
)

logger = logging.getLogger(__name__)


class GenerationService:
    """内容生成服务"""
    
    def __init__(self, prompt_service: PromptService):
        self.prompt_service = prompt_service
        self.ai_service = get_ai_service()
    
    async def generate_novel_name(
        self, 
        request: NovelNameRequest
    ) -> StructuredGenerationResponse:
        """生成小说名"""
        try:
            start_time = time.time()
            
            # 检查AI服务是否可用
            if not self.ai_service.is_available():
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
            logger.error(f"小说名生成失败: {str(e)}")
            raise AIServiceError(f"小说名生成失败: {str(e)}")
    
    async def generate_novel_idea(
        self, 
        request: NovelIdeaRequest
    ) -> StructuredGenerationResponse:
        """生成小说创意"""
        try:
            start_time = time.time()
            
            # 检查AI服务是否可用
            if not self.ai_service.is_available():
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


def get_generation_service(prompt_service: PromptService) -> GenerationService:
    """获取内容生成服务实例"""
    return GenerationService(prompt_service)