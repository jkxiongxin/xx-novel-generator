"""
AI生成接口
Author: AI Writer Team
Created: 2025-06-01
"""

import logging
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text

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
from app.schemas.worldview import (
    WorldviewGenerationRequest,
    WorldviewGenerationResponse
)
from app.schemas.brain_storm import (
    BrainStormRequest as NewBrainStormRequest,
    BrainStormResponse, BrainStormHistoryResponse, BrainStormHistoryDetail,
    ElementSuggestionsResponse, TopicSuggestionsResponse,
    UserPreferences, SavePreferencesRequest, SavePreferencesResponse,
    GenerationStats, RateGenerationRequest, RateGenerationResponse
)
from app.services.brain_storm_service import get_brain_storm_service

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
        logger.info(f"用户 {current_user.username} 请求生成小说名")
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
        result = await generation_service.generate_novel_name(request, user_id=current_user.id)
        
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


@router.post("/worldview/generate", response_model=WorldviewGenerationResponse)
async def generate_worldview(
    request: WorldviewGenerationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    生成世界观
    
    - **novel_id**: 小说ID（必需）
    - **worldview_name**: 世界观名称（可选）
    - **generation_types**: 生成类型列表，可选：maps/cultivation/history/factions
    - **user_suggestion**: 用户建议（可选）
    - **include_novel_idea**: 是否包含小说创意（默认True）
    - **include_novel_settings**: 是否包含小说设定（默认True）
    """
    try:
        logger.info(f"用户 {current_user.username} 请求生成世界观")
        
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
        
        # 生成世界观
        result = await generation_service.generate_worldview(
            request,
            user_id=current_user.id
        )
        
        logger.info(f"用户 {current_user.username} 生成世界观成功")
        return result
        
    except AIServiceError as e:
        logger.error(f"世界观生成失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI服务暂时不可用: {str(e)}"
        )
    except Exception as e:
        logger.error(f"世界观生成异常: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="生成世界观时发生内部错误"
        )


@router.post("/brain-storm", response_model=BrainStormResponse)
async def generate_brain_storm_new(
    request: NewBrainStormRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    脑洞生成器 - 新版本
    
    根据设计文档实现的完整脑洞生成器功能
    """
    try:
        logger.info(f"用户 {current_user.username} 请求脑洞生成: {request.topic}")
        
        # 获取服务实例
        prompt_service = get_prompt_service(db)
        brain_storm_service = get_brain_storm_service(prompt_service, db)
        
        # 生成脑洞创意
        result = await brain_storm_service.generate_brain_storm(request, current_user.id)
        
        logger.info(f"用户 {current_user.username} 脑洞生成成功")
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


@router.get("/brain-storm/history", response_model=BrainStormHistoryResponse)
async def get_brain_storm_history(
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取脑洞生成历史
    """
    try:
        # 获取服务实例
        prompt_service = get_prompt_service(db)
        brain_storm_service = get_brain_storm_service(prompt_service, db)
        
        # 获取历史记录
        result = await brain_storm_service.get_generation_history(
            user_id=current_user.id,
            limit=limit,
            offset=offset
        )
        
        return result
        
    except Exception as e:
        logger.error(f"获取脑洞生成历史异常: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取生成历史时发生内部错误"
        )


@router.get("/brain-storm/history/{history_id}", response_model=BrainStormHistoryDetail)
async def get_brain_storm_history_detail(
    history_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取脑洞生成历史详情
    """
    try:
        # 获取服务实例
        prompt_service = get_prompt_service(db)
        brain_storm_service = get_brain_storm_service(prompt_service, db)
        
        # 获取历史详情
        result = await brain_storm_service.get_history_detail(
            history_id=history_id,
            user_id=current_user.id
        )
        
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"获取脑洞生成历史详情异常: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取历史详情时发生内部错误"
        )


@router.get("/brain-storm/elements", response_model=ElementSuggestionsResponse)
async def get_brain_storm_elements(
    category: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取脑洞生成要素建议
    """
    try:
        # 获取服务实例
        prompt_service = get_prompt_service(db)
        brain_storm_service = get_brain_storm_service(prompt_service, db)
        
        # 获取要素建议
        result = await brain_storm_service.get_element_suggestions(category=category)
        
        return result
        
    except Exception as e:
        logger.error(f"获取要素建议异常: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取要素建议时发生内部错误"
        )


@router.get("/brain-storm/topic-suggestions", response_model=TopicSuggestionsResponse)
async def get_brain_storm_topic_suggestions(
    q: str = None,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取主题建议
    """
    try:
        # 获取服务实例
        prompt_service = get_prompt_service(db)
        brain_storm_service = get_brain_storm_service(prompt_service, db)
        
        # 获取主题建议
        result = await brain_storm_service.get_topic_suggestions(
            query=q,
            limit=limit
        )
        
        return result
        
    except Exception as e:
        logger.error(f"获取主题建议异常: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取主题建议时发生内部错误"
        )


@router.get("/brain-storm/preferences", response_model=UserPreferences)
async def get_brain_storm_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取用户脑洞生成偏好设置
    """
    try:
        # 获取服务实例
        prompt_service = get_prompt_service(db)
        brain_storm_service = get_brain_storm_service(prompt_service, db)
        
        # 获取用户偏好
        result = await brain_storm_service.get_user_preferences(current_user.id)
        
        return result
        
    except Exception as e:
        logger.error(f"获取用户偏好异常: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取用户偏好时发生内部错误"
        )


@router.post("/brain-storm/preferences", response_model=SavePreferencesResponse)
async def save_brain_storm_preferences(
    request: SavePreferencesRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    保存用户脑洞生成偏好设置
    """
    try:
        # 获取服务实例
        prompt_service = get_prompt_service(db)
        brain_storm_service = get_brain_storm_service(prompt_service, db)
        
        # 保存用户偏好
        preferences = await brain_storm_service.save_user_preferences(
            user_id=current_user.id,
            request=request
        )
        
        return SavePreferencesResponse(
            success=True,
            preferences=preferences
        )
        
    except Exception as e:
        logger.error(f"保存用户偏好异常: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="保存用户偏好时发生内部错误"
        )


@router.post("/brain-storm/{generation_id}/rating", response_model=RateGenerationResponse)
async def rate_brain_storm_generation(
    generation_id: str,
    request: RateGenerationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    评价脑洞生成结果
    """
    try:
        # 获取服务实例
        prompt_service = get_prompt_service(db)
        brain_storm_service = get_brain_storm_service(prompt_service, db)
        
        # 评价生成结果
        result = await brain_storm_service.rate_generation(
            generation_id=generation_id,
            user_id=current_user.id,
            request=request
        )
        
        return RateGenerationResponse(**result)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"评价生成结果异常: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="评价生成结果时发生内部错误"
        )


@router.get("/brain-storm/stats", response_model=GenerationStats)
async def get_brain_storm_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取脑洞生成统计信息
    """
    try:
        # 获取服务实例
        prompt_service = get_prompt_service(db)
        brain_storm_service = get_brain_storm_service(prompt_service, db)
        
        # 获取统计信息
        result = await brain_storm_service.get_generation_stats(current_user.id)
        
        return result
        
    except Exception as e:
        logger.error(f"获取生成统计异常: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取生成统计时发生内部错误"
        )