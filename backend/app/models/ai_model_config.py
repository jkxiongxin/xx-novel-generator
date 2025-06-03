"""
AI模型配置数据模型
Author: AI Writer Team
Created: 2025-06-01
"""

import json
from typing import Dict, Any, Optional, List
from enum import Enum
from sqlalchemy import Column, String, Text, JSON, Boolean, Integer, Enum as SQLEnum
from sqlalchemy.orm import relationship

from app.models.base import Base, UserOwnedMixin


class ModelType(str, Enum):
    """AI模型类型枚举"""
    OPENAI_COMPATIBLE = "openai_compatible"  # OpenAI兼容格式
    CUSTOM_HTTP = "custom_http"              # 自定义HTTP API
    CLAUDE_COMPATIBLE = "claude_compatible"   # Claude兼容格式
    HUGGING_FACE = "hugging_face"            # HuggingFace格式
    OLLAMA = "ollama"                        # Ollama本地模型
    OPENROUTER = "openrouter"                # OpenRouter代理


class RequestFormat(str, Enum):
    """请求格式枚举"""
    OPENAI_CHAT = "openai_chat"              # OpenAI Chat Completions格式
    OPENAI_COMPLETION = "openai_completion"   # OpenAI Completions格式
    CLAUDE_MESSAGES = "claude_messages"       # Claude Messages格式
    CUSTOM_JSON = "custom_json"              # 自定义JSON格式
    REST_API = "rest_api"                    # 标准REST API


class AIModelConfig(Base, UserOwnedMixin):
    """AI模型配置模型"""
    
    # 基础信息
    name = Column(String(200), nullable=False, comment="模型显示名称")
    description = Column(Text, nullable=True, comment="模型描述")
    model_type = Column(SQLEnum(ModelType), nullable=False, comment="模型类型")
    is_active = Column(Boolean, default=True, nullable=False, comment="是否启用")
    is_default = Column(Boolean, default=False, nullable=False, comment="是否为默认模型")
    
    # 分组配置
    group_name = Column(String(100), nullable=True, comment="配置分组名称")
    group_description = Column(Text, nullable=True, comment="分组描述")
    is_group_default = Column(Boolean, default=False, nullable=False, comment="是否为分组内默认模型")
    
    # API配置
    api_endpoint = Column(String(500), nullable=False, comment="API端点URL")
    api_key = Column(String(500), nullable=True, comment="API密钥")
    model_name = Column(String(200), nullable=False, comment="模型名称/ID")
    request_format = Column(SQLEnum(RequestFormat), nullable=False, comment="请求格式")
    
    # 请求配置
    max_tokens = Column(Integer, default=2000, nullable=False, comment="最大token数")
    temperature = Column(String(10), default="0.7", nullable=False, comment="温度参数")
    timeout = Column(Integer, default=60, nullable=False, comment="请求超时时间(秒)")
    retry_count = Column(Integer, default=3, nullable=False, comment="重试次数")
    
    # 高级配置
    request_headers = Column(JSON, nullable=True, comment="自定义请求头")
    request_params = Column(JSON, nullable=True, comment="请求参数映射")
    response_mapping = Column(JSON, nullable=True, comment="响应数据映射")
    
    # 模板和预设
    prompt_template = Column(Text, nullable=True, comment="提示词模板")
    system_message = Column(Text, nullable=True, comment="系统消息模板")
    
    # 限制和配额
    daily_limit = Column(Integer, nullable=True, comment="每日调用限制")
    monthly_limit = Column(Integer, nullable=True, comment="每月调用限制")
    priority = Column(Integer, default=1, nullable=False, comment="优先级(1-10)")
    
    def get_request_headers(self) -> Dict[str, str]:
        """获取请求头配置"""
        headers = {"Content-Type": "application/json"}
        
        # 添加API密钥到请求头
        if self.api_key:
            if self.model_type == ModelType.OPENAI_COMPATIBLE:
                headers["Authorization"] = f"Bearer {self.api_key}"
            elif self.model_type == ModelType.CLAUDE_COMPATIBLE:
                headers["x-api-key"] = self.api_key
            else:
                headers["Authorization"] = f"Bearer {self.api_key}"
        
        # 合并自定义请求头
        if self.request_headers:
            headers.update(self.request_headers)
            
        return headers
    
    def get_request_params(self) -> Dict[str, Any]:
        """获取请求参数配置"""
        params = {
            "model": self.model_name,
            "max_tokens": self.max_tokens,
            "temperature": float(self.temperature)
        }
        
        # 合并自定义参数
        if self.request_params:
            params.update(self.request_params)
            
        return params
    
    def get_response_mapping(self) -> Dict[str, str]:
        """获取响应映射配置"""
        # 默认响应映射
        default_mapping = {
            "content": "choices.0.message.content",  # OpenAI格式
            "usage": "usage",
            "finish_reason": "choices.0.finish_reason"
        }
        
        if self.response_mapping:
            default_mapping.update(self.response_mapping)
            
        return default_mapping
    
    def format_prompt(self, prompt: str, **kwargs) -> str:
        """格式化提示词"""
        if self.prompt_template:
            try:
                return self.prompt_template.format(prompt=prompt, **kwargs)
            except KeyError:
                pass
        return prompt
    
    def get_system_message(self, **kwargs) -> Optional[str]:
        """获取系统消息"""
        if self.system_message:
            try:
                return self.system_message.format(**kwargs)
            except KeyError:
                pass
        return self.system_message
    
    def is_openai_compatible(self) -> bool:
        """是否为OpenAI兼容格式"""
        return self.model_type == ModelType.OPENAI_COMPATIBLE
    
    def is_claude_compatible(self) -> bool:
        """是否为Claude兼容格式"""
        return self.model_type == ModelType.CLAUDE_COMPATIBLE
    
    def is_custom_format(self) -> bool:
        """是否为自定义格式"""
        return self.model_type == ModelType.CUSTOM_HTTP
    
    def validate_config(self) -> List[str]:
        """验证配置有效性"""
        errors = []
        
        # 检查必填字段
        if not self.api_endpoint:
            errors.append("API端点不能为空")
        
        if not self.model_name:
            errors.append("模型名称不能为空")
        
        # 检查URL格式
        if self.api_endpoint and not self.api_endpoint.startswith(('http://', 'https://')):
            errors.append("API端点必须是有效的HTTP(S) URL")
        
        # 检查参数范围
        if self.max_tokens <= 0 or self.max_tokens > 100000:
            errors.append("最大token数必须在1-100000之间")
        
        try:
            temp = float(self.temperature)
            if temp < 0 or temp > 2:
                errors.append("温度参数必须在0-2之间")
        except ValueError:
            errors.append("温度参数必须是有效数字")
        
        if self.timeout <= 0 or self.timeout > 300:
            errors.append("超时时间必须在1-300秒之间")
        
        if self.retry_count < 0 or self.retry_count > 10:
            errors.append("重试次数必须在0-10之间")
        
        return errors
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典，隐藏敏感信息"""
        data = super().to_dict()
        
        # 隐藏API密钥
        if data.get('api_key'):
            data['api_key'] = f"***{data['api_key'][-4:]}" if len(data['api_key']) > 4 else "***"
        
        return data
    
    def to_full_dict(self) -> Dict[str, Any]:
        """转换为完整字典，包含敏感信息（仅限管理员）"""
        return super().to_dict()
    
    def __repr__(self) -> str:
        return f"<AIModelConfig(id={self.id}, name='{self.name}', type='{self.model_type}')>"