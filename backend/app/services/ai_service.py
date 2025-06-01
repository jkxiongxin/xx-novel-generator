"""
AI模型调用服务
Author: AI Writer Team
Created: 2025-06-01
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List, Union
from abc import ABC, abstractmethod
import openai
from openai import AsyncOpenAI

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class AIModelAdapter(ABC):
    """AI模型适配器接口"""
    
    @abstractmethod
    async def generate_text(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> str:
        """生成文本内容"""
        pass
    
    @abstractmethod
    async def generate_structured_response(
        self,
        prompt: str,
        response_format: Dict[str, Any],
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """生成结构化响应"""
        pass


class OpenAIAdapter(AIModelAdapter):
    """OpenAI模型适配器"""
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        self.default_max_tokens = settings.OPENAI_MAX_TOKENS
        self.default_temperature = settings.OPENAI_TEMPERATURE
    
    async def generate_text(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> str:
        """生成文本内容"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens or self.default_max_tokens,
                temperature=temperature or self.default_temperature,
                **kwargs
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"OpenAI API调用失败: {str(e)}")
            raise AIServiceError(f"生成内容失败: {str(e)}")
    
    async def generate_structured_response(
        self,
        prompt: str,
        response_format: Dict[str, Any],
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """生成结构化响应"""
        try:
            # 添加响应格式说明到提示词
            format_instruction = f"\n\n请按照以下JSON格式返回结果：\n{response_format}"
            full_prompt = prompt + format_instruction
            
            response_text = await self.generate_text(
                full_prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
            
            # 尝试解析JSON响应
            import json
            try:
                return json.loads(response_text)
            except json.JSONDecodeError:
                # 如果解析失败，返回原始文本
                logger.warning(f"无法解析为JSON格式，返回原始文本: {response_text}")
                return {"content": response_text}
                
        except Exception as e:
            logger.error(f"生成结构化响应失败: {str(e)}")
            raise AIServiceError(f"生成结构化响应失败: {str(e)}")


class ClaudeAdapter(AIModelAdapter):
    """Claude模型适配器（预留接口）"""
    
    def __init__(self, api_key: str, model: str = "claude-3-sonnet"):
        self.api_key = api_key
        self.model = model
        # TODO: 实现Claude API客户端
    
    async def generate_text(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> str:
        """生成文本内容"""
        # TODO: 实现Claude API调用
        raise NotImplementedError("Claude适配器尚未实现")
    
    async def generate_structured_response(
        self,
        prompt: str,
        response_format: Dict[str, Any],
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """生成结构化响应"""
        # TODO: 实现Claude API调用
        raise NotImplementedError("Claude适配器尚未实现")


class AIServiceError(Exception):
    """AI服务异常"""
    pass


class AIService:
    """AI服务统一接口"""
    
    def __init__(self):
        self.adapters: Dict[str, AIModelAdapter] = {}
        self.default_adapter: Optional[str] = None
        self._init_adapters()
    
    def _init_adapters(self):
        """初始化AI模型适配器"""
        try:
            # 初始化OpenAI适配器
            if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "your-openai-api-key-here":
                openai_adapter = OpenAIAdapter(
                    api_key=settings.OPENAI_API_KEY,
                    model=settings.OPENAI_MODEL
                )
                self.adapters["openai"] = openai_adapter
                if self.default_adapter is None:
                    self.default_adapter = "openai"
                logger.info("OpenAI适配器初始化成功")
            else:
                logger.warning("OpenAI API Key未配置，跳过OpenAI适配器初始化")
            
            # TODO: 添加其他模型适配器
            
        except Exception as e:
            logger.error(f"AI适配器初始化失败: {str(e)}")
    
    def get_adapter(self, adapter_name: Optional[str] = None) -> AIModelAdapter:
        """获取AI模型适配器"""
        name = adapter_name or self.default_adapter
        
        if not name or name not in self.adapters:
            available = list(self.adapters.keys())
            raise AIServiceError(f"未找到适配器 {name}，可用适配器: {available}")
        
        return self.adapters[name]
    
    async def generate_text(
        self,
        prompt: str,
        adapter_name: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        retry_count: int = 3,
        **kwargs
    ) -> str:
        """生成文本内容（带重试机制）"""
        adapter = self.get_adapter(adapter_name)
        
        for attempt in range(retry_count):
            try:
                result = await adapter.generate_text(
                    prompt=prompt,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    **kwargs
                )
                return result
                
            except Exception as e:
                logger.warning(f"第{attempt + 1}次尝试失败: {str(e)}")
                if attempt == retry_count - 1:
                    raise AIServiceError(f"生成失败，已重试{retry_count}次: {str(e)}")
                
                # 等待后重试
                await asyncio.sleep(2 ** attempt)
    
    async def generate_structured_response(
        self,
        prompt: str,
        response_format: Dict[str, Any],
        adapter_name: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        retry_count: int = 3,
        **kwargs
    ) -> Dict[str, Any]:
        """生成结构化响应（带重试机制）"""
        adapter = self.get_adapter(adapter_name)
        
        for attempt in range(retry_count):
            try:
                result = await adapter.generate_structured_response(
                    prompt=prompt,
                    response_format=response_format,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    **kwargs
                )
                return result
                
            except Exception as e:
                logger.warning(f"第{attempt + 1}次尝试失败: {str(e)}")
                if attempt == retry_count - 1:
                    raise AIServiceError(f"生成失败，已重试{retry_count}次: {str(e)}")
                
                # 等待后重试
                await asyncio.sleep(2 ** attempt)
    
    def is_available(self, adapter_name: Optional[str] = None) -> bool:
        """检查AI服务是否可用"""
        try:
            self.get_adapter(adapter_name)
            return True
        except AIServiceError:
            return False
    
    def get_available_adapters(self) -> List[str]:
        """获取可用的适配器列表"""
        return list(self.adapters.keys())


# 创建全局AI服务实例
ai_service = AIService()


def get_ai_service() -> AIService:
    """获取AI服务实例"""
    return ai_service