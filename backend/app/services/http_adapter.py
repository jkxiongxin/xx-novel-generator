"""
通用HTTP适配器，支持任意API端点调用
Author: AI Writer Team
Created: 2025-06-01
"""

import logging
import json
import asyncio
from typing import Dict, Any, Optional, List, Union
import aiohttp
from aiohttp import ClientTimeout, ClientError

from app.models.ai_model_config import AIModelConfig, ModelType, RequestFormat
from app.services.ai_service import AIModelAdapter, AIServiceError

logger = logging.getLogger(__name__)


class HTTPAdapter(AIModelAdapter):
    """通用HTTP适配器，支持自定义API端点"""
    
    def __init__(self, config: AIModelConfig):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def _get_session(self) -> aiohttp.ClientSession:
        """获取HTTP会话"""
        if self.session is None or self.session.closed:
            timeout = ClientTimeout(total=self.config.timeout)
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                headers=self.config.get_request_headers()
            )
        return self.session
    
    async def _close_session(self):
        """关闭HTTP会话"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    def _build_openai_request(
        self, 
        prompt: str, 
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """构建OpenAI格式请求"""
        messages = []
        
        # 添加系统消息
        system_msg = self.config.get_system_message()
        if system_msg:
            messages.append({"role": "system", "content": system_msg})
        
        # 添加用户消息
        formatted_prompt = self.config.format_prompt(prompt)
        messages.append({"role": "user", "content": formatted_prompt})
        
        # 构建请求参数
        params = self.config.get_request_params()
        params.update({
            "messages": messages,
            "max_tokens": max_tokens or self.config.max_tokens,
            "temperature": temperature or float(self.config.temperature)
        })
        
        # 合并额外参数
        params.update(kwargs)
        
        return params
    
    def _build_claude_request(
        self, 
        prompt: str, 
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """构建Claude格式请求"""
        messages = []
        
        # Claude格式的消息
        formatted_prompt = self.config.format_prompt(prompt)
        messages.append({"role": "user", "content": formatted_prompt})
        
        # 构建请求参数
        params = {
            "model": self.config.model_name,
            "max_tokens": max_tokens or self.config.max_tokens,
            "temperature": temperature or float(self.config.temperature),
            "messages": messages
        }
        
        # 添加系统消息
        system_msg = self.config.get_system_message()
        if system_msg:
            params["system"] = system_msg
        
        # 合并自定义参数和额外参数
        if self.config.request_params:
            params.update(self.config.request_params)
        params.update(kwargs)
        
        return params
    
    def _build_custom_request(
        self, 
        prompt: str, 
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """构建自定义格式请求"""
        formatted_prompt = self.config.format_prompt(prompt)
        
        # 基础参数
        params = {
            "prompt": formatted_prompt,
            "max_tokens": max_tokens or self.config.max_tokens,
            "temperature": temperature or float(self.config.temperature)
        }
        
        # 添加模型名称
        if self.config.model_name:
            params["model"] = self.config.model_name
        
        # 添加系统消息
        system_msg = self.config.get_system_message()
        if system_msg:
            params["system_message"] = system_msg
        
        # 合并自定义参数和额外参数
        if self.config.request_params:
            params.update(self.config.request_params)
        params.update(kwargs)
        
        return params
    
    def _build_request(
        self, 
        prompt: str, 
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """根据请求格式构建请求"""
        if self.config.request_format == RequestFormat.OPENAI_CHAT:
            return self._build_openai_request(prompt, max_tokens, temperature, **kwargs)
        elif self.config.request_format == RequestFormat.CLAUDE_MESSAGES:
            return self._build_claude_request(prompt, max_tokens, temperature, **kwargs)
        else:
            return self._build_custom_request(prompt, max_tokens, temperature, **kwargs)
    
    def _extract_content_from_response(self, response_data: Dict[str, Any]) -> str:
        """从响应中提取内容"""
        mapping = self.config.get_response_mapping()
        content_path = mapping.get("content", "choices.0.message.content")
        
        try:
            # 解析路径并提取内容
            return self._extract_by_path(response_data, content_path)
        except (KeyError, IndexError, TypeError) as e:
            logger.warning(f"无法按路径 {content_path} 提取内容: {e}")
            
            # 尝试常见的响应格式
            common_paths = [
                "choices.0.message.content",  # OpenAI
                "content.0.text",             # Claude
                "text",                       # 简单格式
                "response",                   # 通用格式
                "output",                     # 输出格式
                "result"                      # 结果格式
            ]
            
            for path in common_paths:
                try:
                    return self._extract_by_path(response_data, path)
                except:
                    continue
            
            # 如果都失败了，返回原始响应的字符串表示
            return str(response_data)
    
    def _extract_by_path(self, data: Dict[str, Any], path: str) -> str:
        """按路径提取数据"""
        parts = path.split('.')
        current = data
        
        for part in parts:
            if part.isdigit():
                # 数组索引
                current = current[int(part)]
            else:
                # 对象属性
                current = current[part]
        
        return str(current) if current is not None else ""
    
    async def generate_text(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> str:
        """生成文本内容"""
        session = await self._get_session()
        
        try:
            # 构建请求
            request_data = self._build_request(prompt, max_tokens, temperature, **kwargs)
            
            logger.info(f"调用AI API: {self.config.api_endpoint}")
            logger.debug(f"请求数据: {json.dumps(request_data, ensure_ascii=False, indent=2)}")
            
            # 发送请求
            async with session.post(
                self.config.api_endpoint,
                json=request_data
            ) as response:
                
                # 检查响应状态
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"API请求失败: {response.status} - {error_text}")
                    raise AIServiceError(f"API请求失败: {response.status} - {error_text}")
                
                # 解析响应
                response_data = await response.json()
                logger.debug(f"API响应: {json.dumps(response_data, ensure_ascii=False, indent=2)}")
                
                # 提取内容
                content = self._extract_content_from_response(response_data)
                
                if not content:
                    raise AIServiceError("API响应中未找到有效内容")
                
                return content.strip()
                
        except ClientError as e:
            logger.error(f"HTTP请求失败: {str(e)}")
            raise AIServiceError(f"网络请求失败: {str(e)}")
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {str(e)}")
            raise AIServiceError(f"响应格式错误: {str(e)}")
        except Exception as e:
            logger.error(f"生成文本失败: {str(e)}")
            raise AIServiceError(f"生成文本失败: {str(e)}")
    
    async def generate_structured_response(
        self,
        prompt: str,
        response_format: Dict[str, Any],
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """生成结构化响应"""
        # 在提示词中添加格式说明
        format_instruction = f"\n\n请严格按照以下JSON格式返回结果，不要添加任何额外的文字说明：\n{json.dumps(response_format, ensure_ascii=False, indent=2)}"
        full_prompt = prompt + format_instruction

        import re
        # 生成文本
        response_text = await self.generate_text(
            full_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs
        )

        logger.info(f"生成的响应文本: {response_text}")

        # 过滤掉<think>...</think>内容
        response_text = re.sub(r"<think>.*?</think>", "", response_text, flags=re.DOTALL | re.IGNORECASE)

        # 提取被```json ... ```包裹的内容
        match = re.search(r"```json\s*(.*?)\s*```", response_text, re.DOTALL | re.IGNORECASE)
        if match:
            json_str = match.group(1)
        else:
            json_str = response_text

        # 尝试解析JSON
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            logger.warning(f"无法解析为JSON格式，返回原始文本: {response_text}")
            return {"content": response_text, "raw_response": response_text}
    
    async def test_connection(self, test_prompt: str = "你好") -> Dict[str, Any]:
        """测试连接"""
        import time
        import re
        
        start_time = time.time()
        
        try:
            # 测试生成
            content = await self.generate_text(
                test_prompt,
                max_tokens=50,
                temperature=0.1
            )
            
            response_time = time.time() - start_time
            
            return {
                "success": True,
                "response_time": response_time,
                "content": content,
                "error": None
            }
            
        except Exception as e:
            response_time = time.time() - start_time
            
            return {
                "success": False,
                "response_time": response_time,
                "content": None,
                "error": str(e)
            }
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self._close_session()


class AdapterFactory:
    """适配器工厂"""
    
    @staticmethod
    def create_adapter(config: AIModelConfig) -> AIModelAdapter:
        """根据配置创建适配器"""
        if config.model_type in [
            ModelType.OPENAI_COMPATIBLE,
            ModelType.CLAUDE_COMPATIBLE,
            ModelType.CUSTOM_HTTP,
            ModelType.HUGGING_FACE,
            ModelType.OLLAMA,
            ModelType.OPENROUTER
        ]:
            return HTTPAdapter(config)
        else:
            raise AIServiceError(f"不支持的模型类型: {config.model_type}")
    
    @staticmethod
    def get_supported_types() -> List[ModelType]:
        """获取支持的模型类型"""
        return [
            ModelType.OPENAI_COMPATIBLE,
            ModelType.CLAUDE_COMPATIBLE,
            ModelType.CUSTOM_HTTP,
            ModelType.HUGGING_FACE,
            ModelType.OLLAMA,
            ModelType.OPENROUTER
        ]