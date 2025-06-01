"""
AI生成接口
Author: AI Writer Team
Created: 2025-06-01
"""

import logging
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.prompt_service import get_prompt_service
from app.services.generation_service import get_generation_service
from app.services.ai_service import AIServiceError
from app.schemas.prompt import (
    NovelNameRequest, NovelIdeaRequest, BrainStormRequest,
    StructuredGenerationResponse
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/novel-name", response_model=StructuredGenerationResponse)
async def generate_novel_name(
    request: NovelNameRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    生成小说名
    
    - **genre**: 小说类型（可选）
    - **keywords**: 关键词（可选）
    - **style**: 风格偏好（可选）
    - **user_input**: 用户需求描述（可选）
    - **max_tokens**: 最大token数（可选）
    - **temperature**: 温度值0-100（可选）
    """
    try:
        # 获取服务实例
        prompt_service = get_prompt_service(db)
        generation_service = get_generation_service(prompt_service)
        
        # 验证请求
        request_dict = request.dict()
        is_valid = await generation_service.validate_generation_request(request_dict)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="请求参数验证失败"
            )
        
        # 生成小说名
        result = await generation_service.generate_novel_name(request)
        
        logger.info(f"用户 {current_user.username} 生成小说名成功")
        return result
        
    except AIServiceError as e:
        logger.error(f"小说名生成失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI服务暂时不可用: {str(e)}"
        )
    except Exception as e:
        logger.error(f"小说名生成异常: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="生成小说名时发生内部错误"
        )


@router.post("/novel-idea", response_model=StructuredGenerationResponse)
async def generate_novel_idea(
    request: NovelIdeaRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    生成小说创意
    
    - **genre**: 小说类型（可选）
    - **themes**: 主题（可选）
    - **length**: 篇幅长度（可选）
    - **user_input**: 用户需求描述（可选）
    - **max_tokens**: 最大token数（可选）
    - **temperature**: 温度值0-100（可选）
    """
    try:
        # 获取服务实例
        prompt_service = get_prompt_service(db)
        generation_service = get_generation_service(prompt_service)
        
        # 验证请求
        request_dict = request.dict()
        is_valid = await generation_service.validate_generation_request(request_dict)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="请求参数验证失败"
            )
        
        # 生成小说创意
        result = await generation_service.generate_novel_idea(request)
        
        logger.info(f"用户 {current_user.username} 生成小说创意成功")
        return result
        
    except AIServiceError as e:
        logger.error(f"小说创意生成失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI服务暂时不可用: {str(e)}"
        )
    except Exception as e:
        logger.error(f"小说创意生成异常: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="生成小说创意时发生内部错误"
        )


@router.post("/brain-storm", response_model=StructuredGenerationResponse)
async def generate_brain_storm(
    request: BrainStormRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    脑洞生成器
    
    - **topic**: 主题（可选）
    - **elements**: 要素（可选）
    - **creativity_level**: 创意程度0-100（可选，默认80）
    - **user_input**: 用户想法描述（可选）
    - **max_tokens**: 最大token数（可选）
    - **temperature**: 温度值0-100（可选）
    """
    try:
        # 获取服务实例
        prompt_service = get_prompt_service(db)
        generation_service = get_generation_service(prompt_service)
        
        # 验证请求
        request_dict = request.dict()
        is_valid = await generation_service.validate_generation_request(request_dict)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="请求参数验证失败"
            )
        
        # 生成脑洞创意
        result = await generation_service.generate_brain_storm(request)
        
        logger.info(f"用户 {current_user.username} 生成脑洞创意成功")
        return result
        
    except AIServiceError as e:
        logger.error(f"脑洞生成失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI服务暂时不可用: {str(e)}"
        )
    except Exception as e:
        logger.error(f"脑洞生成异常: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="生成脑洞创意时发生内部错误"
        )


@router.get("/status")
async def get_generation_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取AI生成服务状态
    """
    try:
        # 获取服务实例
        prompt_service = get_prompt_service(db)
        generation_service = get_generation_service(prompt_service)
        
        # 获取服务状态
        status_info = generation_service.get_service_status()
        
        return {
            "status": "success",
            "data": status_info,
            "message": "服务状态获取成功"
        }
        
    except Exception as e:
        logger.error(f"获取生成服务状态异常: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取服务状态时发生内部错误"
        )


@router.get("/prompt-types")
async def get_prompt_types(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取可用的提示词类型
    """
    try:
        from app.models.prompt import PromptType
        
        prompt_types = [
            {
                "value": PromptType.NOVEL_NAME,
                "label": "小说名生成",
                "description": "生成吸引人的小说标题"
            },
            {
                "value": PromptType.NOVEL_IDEA,
                "label": "小说创意生成",
                "description": "生成完整的小说创意设定"
            },
            {
                "value": PromptType.BRAIN_STORM,
                "label": "脑洞生成器",
                "description": "发挥创意，生成有趣的脑洞想法"
            }
        ]
        
        return {
            "status": "success",
            "data": prompt_types,
            "message": "提示词类型获取成功"
        }
        
    except Exception as e:
        logger.error(f"获取提示词类型异常: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取提示词类型时发生内部错误"
        )