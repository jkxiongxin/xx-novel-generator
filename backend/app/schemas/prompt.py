"""
提示词数据模式
Author: AI Writer Team
Created: 2025-06-01
"""

from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator

from app.models.prompt import PromptType


class PromptBase(BaseModel):
    """提示词基础模式"""
    name: str = Field(..., description="提示词名称", max_length=200)
    type: PromptType = Field(..., description="提示词类型")
    template: str = Field(..., description="提示词模板内容")
    description: Optional[str] = Field(None, description="提示词描述")
    default_max_tokens: int = Field(2000, description="默认最大token数", ge=1, le=8000)
    default_temperature: int = Field(70, description="默认温度值(0-100)", ge=0, le=100)
    response_format: Optional[str] = Field(None, description="期望的响应格式(JSON)")
    is_active: bool = Field(True, description="是否启用")
    version: str = Field("1.0", description="版本号", max_length=20)


class PromptCreate(PromptBase):
    """创建提示词模式"""
    pass


class PromptUpdate(BaseModel):
    """更新提示词模式"""
    name: Optional[str] = Field(None, description="提示词名称", max_length=200)
    template: Optional[str] = Field(None, description="提示词模板内容")
    description: Optional[str] = Field(None, description="提示词描述")
    default_max_tokens: Optional[int] = Field(None, description="默认最大token数", ge=1, le=8000)
    default_temperature: Optional[int] = Field(None, description="默认温度值(0-100)", ge=0, le=100)
    response_format: Optional[str] = Field(None, description="期望的响应格式(JSON)")
    is_active: Optional[bool] = Field(None, description="是否启用")
    version: Optional[str] = Field(None, description="版本号", max_length=20)


class PromptResponse(PromptBase):
    """提示词响应模式"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class GenerationRequest(BaseModel):
    """生成请求基础模式"""
    user_input: Optional[str] = Field(None, description="用户输入", max_length=1000)
    max_tokens: Optional[int] = Field(None, description="最大token数", ge=1, le=8000)
    temperature: Optional[int] = Field(None, description="温度值(0-100)", ge=0, le=100)
    
    @validator('temperature')
    def validate_temperature(cls, v):
        if v is not None and (v < 0 or v > 100):
            raise ValueError('温度值必须在0-100之间')
        return v


class NovelNameRequest(GenerationRequest):
    """小说名生成请求"""
    genre: Optional[str] = Field(None, description="小说类型", max_length=100)
    keywords: Optional[str] = Field(None, description="关键词", max_length=200)
    style: Optional[str] = Field(None, description="风格偏好", max_length=100)


class NovelIdeaRequest(GenerationRequest):
    """小说创意生成请求"""
    genre: Optional[str] = Field(None, description="小说类型", max_length=100)
    themes: Optional[str] = Field(None, description="主题", max_length=200)
    length: Optional[str] = Field(None, description="篇幅长度", max_length=50)


class BrainStormRequest(GenerationRequest):
    """脑洞生成器请求"""
    topic: Optional[str] = Field(None, description="主题", max_length=200)
    elements: Optional[str] = Field(None, description="要素", max_length=300)
    creativity_level: Optional[int] = Field(80, description="创意程度(0-100)", ge=0, le=100)


class GenerationResponse(BaseModel):
    """生成响应模式"""
    content: str = Field(..., description="生成的内容")
    tokens_used: Optional[int] = Field(None, description="使用的token数")
    model_used: Optional[str] = Field(None, description="使用的模型")
    generation_time: Optional[float] = Field(None, description="生成耗时(秒)")
    
    class Config:
        from_attributes = True


class StructuredGenerationResponse(BaseModel):
    """结构化生成响应模式"""
    data: Dict[str, Any] = Field(..., description="结构化数据")
    tokens_used: Optional[int] = Field(None, description="使用的token数")
    model_used: Optional[str] = Field(None, description="使用的模型")
    generation_time: Optional[float] = Field(None, description="生成耗时(秒)")
    
    class Config:
        from_attributes = True