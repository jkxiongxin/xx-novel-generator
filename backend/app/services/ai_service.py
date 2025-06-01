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
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db

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
        self.user_adapters: Dict[int, Dict[str, AIModelAdapter]] = {}  # 用户自定义适配器
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
            
        except Exception as e:
            logger.error(f"AI适配器初始化失败: {str(e)}")
    
    def load_user_adapters(self, user_id: int, db: Session):
        """加载用户自定义适配器"""
        try:
            from app.models.ai_model_config import AIModelConfig
            from app.services.http_adapter import AdapterFactory
            
            # 查询用户的AI配置
            configs = db.query(AIModelConfig).filter(
                AIModelConfig.user_id == user_id,
                AIModelConfig.is_active == True
            ).all()
            
            if user_id not in self.user_adapters:
                self.user_adapters[user_id] = {}
            
            # 清除旧的适配器
            self.user_adapters[user_id].clear()
            
            # 创建新的适配器
            for config in configs:
                try:
                    adapter = AdapterFactory.create_adapter(config)
                    adapter_key = f"user_{user_id}_{config.id}"
                    self.user_adapters[user_id][adapter_key] = adapter
                    
                    # 如果是默认配置，设置为默认适配器
                    if config.is_default:
                        self.user_adapters[user_id]["default"] = adapter
                    
                    logger.info(f"用户 {user_id} 的适配器 {config.name} 加载成功")
                    
                except Exception as e:
                    logger.error(f"加载用户 {user_id} 的适配器 {config.name} 失败: {str(e)}")
            
            logger.info(f"用户 {user_id} 共加载 {len(self.user_adapters[user_id])} 个适配器")
            
        except Exception as e:
            logger.error(f"加载用户 {user_id} 适配器失败: {str(e)}")
    
    def get_adapter(self, adapter_name: Optional[str] = None, user_id: Optional[int] = None) -> AIModelAdapter:
        """获取AI模型适配器"""
        # 优先使用用户自定义适配器
        if user_id and user_id in self.user_adapters:
            user_adapters = self.user_adapters[user_id]
            
            if adapter_name:
                # 查找指定的用户适配器
                if adapter_name in user_adapters:
                    return user_adapters[adapter_name]
                # 查找用户适配器中匹配的名称
                for key, adapter in user_adapters.items():
                    if key.endswith(f"_{adapter_name}") or adapter_name in key:
                        return adapter
            else:
                # 使用用户默认适配器
                if "default" in user_adapters:
                    return user_adapters["default"]
                # 使用第一个可用的用户适配器
                if user_adapters:
                    return next(iter(user_adapters.values()))
        
        # 使用系统默认适配器
        name = adapter_name or self.default_adapter
        
        if not name or name not in self.adapters:
            available = list(self.adapters.keys())
            if user_id and user_id in self.user_adapters:
                available.extend(list(self.user_adapters[user_id].keys()))
            raise AIServiceError(f"未找到适配器 {name}，可用适配器: {available}")
        
        return self.adapters[name]
    
    async def generate_text(
        self,
        prompt: str,
        adapter_name: Optional[str] = None,
        user_id: Optional[int] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        retry_count: int = 3,
        db: Optional[Session] = None,
        **kwargs
    ) -> str:
        """生成文本内容（带重试机制）"""
        # 如果有用户ID和数据库连接，加载用户适配器
        if user_id and db:
            self.load_user_adapters(user_id, db)
        
        adapter = self.get_adapter(adapter_name, user_id)
        
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
        user_id: Optional[int] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        retry_count: int = 3,
        db: Optional[Session] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """生成结构化响应（带重试机制）"""
        # 如果有用户ID和数据库连接，加载用户适配器
        if user_id and db:
            self.load_user_adapters(user_id, db)
        
        adapter = self.get_adapter(adapter_name, user_id)
        
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
    
    def is_available(self, adapter_name: Optional[str] = None, user_id: Optional[int] = None) -> bool:
        """检查AI服务是否可用"""
        try:
            self.get_adapter(adapter_name, user_id)
            return True
        except AIServiceError:
            return False
    
    def get_available_adapters(self, user_id: Optional[int] = None) -> List[str]:
        """获取可用的适配器列表"""
        adapters = list(self.adapters.keys())
        if user_id and user_id in self.user_adapters:
            adapters.extend(list(self.user_adapters[user_id].keys()))
        return adapters
    
    def get_user_configs(self, user_id: int, db: Session) -> List[Dict[str, Any]]:
        """获取用户的AI配置信息"""
        try:
            from app.models.ai_model_config import AIModelConfig
            
            configs = db.query(AIModelConfig).filter(
                AIModelConfig.user_id == user_id,
                AIModelConfig.is_active == True
            ).all()
            
            return [config.to_dict() for config in configs]
            
        except Exception as e:
            logger.error(f"获取用户 {user_id} 配置失败: {str(e)}")
            return []
    
    async def test_user_config(self, config_id: int, user_id: int, db: Session, test_prompt: str = "你好") -> Dict[str, Any]:
        """测试用户配置"""
        try:
            from app.models.ai_model_config import AIModelConfig
            from app.services.http_adapter import AdapterFactory
            
            # 查询配置
            config = db.query(AIModelConfig).filter(
                AIModelConfig.id == config_id,
                AIModelConfig.user_id == user_id
            ).first()
            
            if not config:
                return {
                    "success": False,
                    "error": "配置不存在",
                    "response_time": 0,
                    "content": None
                }
            
            # 创建临时适配器
            adapter = AdapterFactory.create_adapter(config)
            
            # 测试连接
            result = await adapter.test_connection(test_prompt)
            
            return result
            
        except Exception as e:
            logger.error(f"测试配置 {config_id} 失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "response_time": 0,
                "content": None
            }


# 创建全局AI服务实例
ai_service = AIService()


def get_ai_service() -> AIService:
    """获取AI服务实例"""
    return ai_service