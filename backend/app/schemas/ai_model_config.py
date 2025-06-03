"""
AI模型配置数据模式
Author: AI Writer Team
Created: 2025-06-01
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel, validator, Field

from app.models.ai_model_config import ModelType, RequestFormat


class AIModelConfigBase(BaseModel):
    """AI模型配置基础模式"""
    
    name: str = Field(..., min_length=1, max_length=200, description="模型显示名称")
    description: Optional[str] = Field(None, max_length=1000, description="模型描述")
    model_type: ModelType = Field(..., description="模型类型")
    is_active: bool = Field(True, description="是否启用")
    is_default: bool = Field(False, description="是否为默认模型")
    
    # 分组配置
    group_name: Optional[str] = Field(None, max_length=100, description="配置分组名称")
    group_description: Optional[str] = Field(None, max_length=1000, description="分组描述")
    is_group_default: bool = Field(False, description="是否为分组内默认模型")
    
    # API配置
    api_endpoint: str = Field(..., max_length=500, description="API端点URL")
    api_key: Optional[str] = Field(None, max_length=500, description="API密钥")
    model_name: str = Field(..., min_length=1, max_length=200, description="模型名称/ID")
    request_format: RequestFormat = Field(..., description="请求格式")
    
    # 请求配置
    max_tokens: int = Field(2000, ge=1, le=100000, description="最大token数")
    temperature: str = Field("0.7", description="温度参数")
    timeout: int = Field(60, ge=1, le=300, description="请求超时时间(秒)")
    retry_count: int = Field(3, ge=0, le=10, description="重试次数")
    
    # 高级配置
    request_headers: Optional[Dict[str, str]] = Field(None, description="自定义请求头")
    request_params: Optional[Dict[str, Any]] = Field(None, description="请求参数映射")
    response_mapping: Optional[Dict[str, str]] = Field(None, description="响应数据映射")
    
    # 模板和预设
    prompt_template: Optional[str] = Field(None, max_length=5000, description="提示词模板")
    system_message: Optional[str] = Field(None, max_length=2000, description="系统消息模板")
    
    # 限制和配额
    daily_limit: Optional[int] = Field(None, ge=1, description="每日调用限制")
    monthly_limit: Optional[int] = Field(None, ge=1, description="每月调用限制")
    priority: int = Field(1, ge=1, le=10, description="优先级(1-10)")
    
    @validator('api_endpoint')
    def validate_api_endpoint(cls, v):
        """验证API端点URL格式"""
        if not v.startswith(('http://', 'https://')):
            raise ValueError('API端点必须是有效的HTTP(S) URL')
        return v
    
    @validator('temperature')
    def validate_temperature(cls, v):
        """验证温度参数"""
        try:
            temp = float(v)
            if temp < 0 or temp > 2:
                raise ValueError('温度参数必须在0-2之间')
        except ValueError:
            raise ValueError('温度参数必须是有效数字')
        return v
    
    @validator('request_headers')
    def validate_request_headers(cls, v):
        """验证请求头"""
        if v is not None:
            # 检查请求头数量限制
            if len(v) > 20:
                raise ValueError('自定义请求头不能超过20个')
            
            # 检查键值长度
            for key, value in v.items():
                if len(key) > 100 or len(str(value)) > 500:
                    raise ValueError('请求头键值长度过长')
        return v
    
    @validator('request_params')
    def validate_request_params(cls, v):
        """验证请求参数"""
        if v is not None:
            # 检查参数数量限制
            if len(v) > 50:
                raise ValueError('请求参数不能超过50个')
        return v


class AIModelConfigCreate(AIModelConfigBase):
    """创建AI模型配置请求模式"""
    pass


class AIModelConfigUpdate(BaseModel):
    """更新AI模型配置请求模式"""
    
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    model_type: Optional[ModelType] = None
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None
    
    api_endpoint: Optional[str] = Field(None, max_length=500)
    api_key: Optional[str] = Field(None, max_length=500)
    model_name: Optional[str] = Field(None, min_length=1, max_length=200)
    request_format: Optional[RequestFormat] = None
    
    max_tokens: Optional[int] = Field(None, ge=1, le=100000)
    temperature: Optional[str] = None
    timeout: Optional[int] = Field(None, ge=1, le=300)
    retry_count: Optional[int] = Field(None, ge=0, le=10)
    
    request_headers: Optional[Dict[str, str]] = None
    request_params: Optional[Dict[str, Any]] = None
    response_mapping: Optional[Dict[str, str]] = None
    
    prompt_template: Optional[str] = Field(None, max_length=5000)
    system_message: Optional[str] = Field(None, max_length=2000)
    
    daily_limit: Optional[int] = Field(None, ge=1)
    monthly_limit: Optional[int] = Field(None, ge=1)
    priority: Optional[int] = Field(None, ge=1, le=10)
    
    @validator('api_endpoint')
    def validate_api_endpoint(cls, v):
        if v is not None and not v.startswith(('http://', 'https://')):
            raise ValueError('API端点必须是有效的HTTP(S) URL')
        return v
    
    @validator('temperature')
    def validate_temperature(cls, v):
        if v is not None:
            try:
                temp = float(v)
                if temp < 0 or temp > 2:
                    raise ValueError('温度参数必须在0-2之间')
            except ValueError:
                raise ValueError('温度参数必须是有效数字')
        return v


class AIModelConfigResponse(AIModelConfigBase):
    """AI模型配置响应模式"""
    
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    # 隐藏敏感信息的API密钥
    api_key: Optional[str] = None
    
    class Config:
        from_attributes = True
    
    @validator('api_key', pre=True)
    def mask_api_key(cls, v):
        """掩码API密钥"""
        if v and len(v) > 4:
            return f"***{v[-4:]}"
        elif v:
            return "***"
        return None


class AIModelConfigFullResponse(AIModelConfigBase):
    """AI模型配置完整响应模式（包含敏感信息，仅限管理员）"""
    
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AIModelConfigListResponse(BaseModel):
    """AI模型配置列表响应模式"""
    
    items: List[AIModelConfigResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class AIModelConfigTestRequest(BaseModel):
    """AI模型配置测试请求模式"""
    
    prompt: str = Field(..., min_length=1, max_length=1000, description="测试提示词")
    max_tokens: Optional[int] = Field(None, ge=1, le=1000, description="测试用最大token数")
    temperature: Optional[str] = Field(None, description="测试用温度参数")


class AIModelConfigTestResponse(BaseModel):
    """AI模型配置测试响应模式"""
    
    success: bool
    response_time: float
    content: Optional[str] = None
    error: Optional[str] = None
    usage: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True


class AIModelConfigBatchRequest(BaseModel):
    """AI模型配置批量操作请求模式"""
    
    config_ids: List[int] = Field(..., min_items=1, max_items=50, description="配置ID列表")
    action: str = Field(..., description="操作类型：activate, deactivate, delete")
    
    @validator('action')
    def validate_action(cls, v):
        """验证操作类型"""
        allowed_actions = ['activate', 'deactivate', 'delete']
        if v not in allowed_actions:
            raise ValueError(f'操作类型必须是: {", ".join(allowed_actions)}')
        return v


class AIModelConfigStatsResponse(BaseModel):
    """AI模型配置统计响应模式"""
    
    total_configs: int
    active_configs: int
    inactive_configs: int
    model_types: Dict[str, int]
    request_formats: Dict[str, int]
    default_config_id: Optional[int] = None
    
    class Config:
        from_attributes = True


class AIModelConfigTemplateResponse(BaseModel):
    """AI模型配置模板响应模式"""
    
    name: str
    description: str
    model_type: ModelType
    request_format: RequestFormat
    default_config: AIModelConfigBase
    
    class Config:
        from_attributes = True


class AIModelGroupResponse(BaseModel):
    """AI模型分组响应模式"""
    
    group_name: str
    group_description: Optional[str] = None
    model_count: int
    active_count: int
    default_config_id: Optional[int] = None
    configs: List[AIModelConfigResponse]
    
    class Config:
        from_attributes = True


class AIModelGroupListResponse(BaseModel):
    """AI模型分组列表响应模式"""
    
    groups: List[AIModelGroupResponse]
    total_groups: int
    total_configs: int
    
    class Config:
        from_attributes = True


class AIModelGroupStatsResponse(BaseModel):
    """AI模型分组统计响应模式"""
    
    group_name: str
    group_description: Optional[str] = None
    total_configs: int
    active_configs: int
    model_types: Dict[str, int]
    default_config: Optional[AIModelConfigResponse] = None
    
    class Config:
        from_attributes = True


# 预设模板配置
AI_MODEL_TEMPLATES = [
    {
        "name": "OpenAI GPT-3.5",
        "description": "OpenAI GPT-3.5 Turbo模型，适合大多数文本生成任务",
        "model_type": ModelType.OPENAI_COMPATIBLE,
        "request_format": RequestFormat.OPENAI_CHAT,
        "default_config": {
            "name": "OpenAI GPT-3.5",
            "description": "OpenAI GPT-3.5 Turbo模型",
            "model_type": ModelType.OPENAI_COMPATIBLE,
            "api_endpoint": "https://api.openai.com/v1/chat/completions",
            "model_name": "gpt-3.5-turbo",
            "request_format": RequestFormat.OPENAI_CHAT,
            "max_tokens": 2000,
            "temperature": "0.7",
            "timeout": 60,
            "retry_count": 3,
            "priority": 5
        }
    },
    {
        "name": "OpenAI GPT-4",
        "description": "OpenAI GPT-4模型，更强的推理能力",
        "model_type": ModelType.OPENAI_COMPATIBLE,
        "request_format": RequestFormat.OPENAI_CHAT,
        "default_config": {
            "name": "OpenAI GPT-4",
            "description": "OpenAI GPT-4模型",
            "model_type": ModelType.OPENAI_COMPATIBLE,
            "api_endpoint": "https://api.openai.com/v1/chat/completions",
            "model_name": "gpt-4",
            "request_format": RequestFormat.OPENAI_CHAT,
            "max_tokens": 2000,
            "temperature": "0.7",
            "timeout": 120,
            "retry_count": 3,
            "priority": 8
        }
    },
    {
        "name": "Claude 3 Sonnet",
        "description": "Anthropic Claude 3 Sonnet模型",
        "model_type": ModelType.CLAUDE_COMPATIBLE,
        "request_format": RequestFormat.CLAUDE_MESSAGES,
        "default_config": {
            "name": "Claude 3 Sonnet",
            "description": "Anthropic Claude 3 Sonnet模型",
            "model_type": ModelType.CLAUDE_COMPATIBLE,
            "api_endpoint": "https://api.anthropic.com/v1/messages",
            "model_name": "claude-3-sonnet-20240229",
            "request_format": RequestFormat.CLAUDE_MESSAGES,
            "max_tokens": 2000,
            "temperature": "0.7",
            "timeout": 60,
            "retry_count": 3,
            "priority": 7
        }
    },
    {
        "name": "Ollama Llama2",
        "description": "本地部署的Llama2模型（通过Ollama）",
        "model_type": ModelType.OLLAMA,
        "request_format": RequestFormat.OPENAI_CHAT,
        "default_config": {
            "name": "Ollama Llama2",
            "description": "本地部署的Llama2模型",
            "model_type": ModelType.OLLAMA,
            "api_endpoint": "http://localhost:11434/v1/chat/completions",
            "model_name": "llama2",
            "request_format": RequestFormat.OPENAI_CHAT,
            "max_tokens": 2000,
            "temperature": "0.7",
            "timeout": 60,
            "retry_count": 3,
            "priority": 6,
            "group_name": "本地模型",
            "group_description": "本地部署的开源模型"
        }
    },
    {
        "name": "Ollama Mistral",
        "description": "本地部署的Mistral模型（通过Ollama）",
        "model_type": ModelType.OLLAMA,
        "request_format": RequestFormat.OPENAI_CHAT,
        "default_config": {
            "name": "Ollama Mistral",
            "description": "本地部署的Mistral模型",
            "model_type": ModelType.OLLAMA,
            "api_endpoint": "http://localhost:11434/v1/chat/completions",
            "model_name": "mistral",
            "request_format": RequestFormat.OPENAI_CHAT,
            "max_tokens": 2000,
            "temperature": "0.7",
            "timeout": 60,
            "retry_count": 3,
            "priority": 6,
            "group_name": "本地模型",
            "group_description": "本地部署的开源模型"
        }
    },
    {
        "name": "自定义HTTP API",
        "description": "自定义HTTP API接口配置模板",
        "model_type": ModelType.CUSTOM_HTTP,
        "request_format": RequestFormat.CUSTOM_JSON,
        "default_config": {
            "name": "自定义API模型",
            "description": "自定义HTTP API接口",
            "model_type": ModelType.CUSTOM_HTTP,
            "api_endpoint": "http://your-api-endpoint.com/v1/chat",
            "model_name": "custom-model",
            "request_format": RequestFormat.CUSTOM_JSON,
            "max_tokens": 2000,
            "temperature": "0.7",
            "timeout": 60,
            "retry_count": 3,
            "priority": 4,
            "group_name": "自定义模型",
            "group_description": "用户自定义配置的模型"
        }
    }
]


# 预设分组配置
DEFAULT_MODEL_GROUPS = {
    "OpenAI官方": {
        "description": "OpenAI官方提供的模型",
        "priority": 10,
        "models": ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"]
    },
    "Claude系列": {
        "description": "Anthropic Claude系列模型",
        "priority": 9,
        "models": ["claude-3-sonnet", "claude-3-opus", "claude-3-haiku"]
    },
    "本地模型": {
        "description": "本地部署的开源模型",
        "priority": 7,
        "models": ["llama2", "mistral", "codellama"]
    },
    "自定义模型": {
        "description": "用户自定义配置的模型",
        "priority": 5,
        "models": []
    },
    "国产大模型": {
        "description": "国产大语言模型",
        "priority": 8,
        "models": ["文心一言", "通义千问", "ChatGLM"]
    }
}