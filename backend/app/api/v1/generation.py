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
    db: Session = Depends(get_db)
):
    """
    获取系统状态 - 首页专用，无需登录
    
    返回系统各项服务的状态信息，用于首页展示
    """
    try:
        # 获取服务实例并检查AI服务状态
        ai_service_status = "available"
        database_status = "connected"
        
        try:
            prompt_service = get_prompt_service(db)
            generation_service = get_generation_service(prompt_service)
            
            # 测试AI服务连接
            service_status = generation_service.get_service_status()
            
            # 根据服务状态确定AI服务可用性
            if service_status.get("ai_service", {}).get("available", False):
                ai_service_status = "available"
            else:
                ai_service_status = "limited"
                
        except Exception as ai_error:
            logger.warning(f"AI服务检查失败: {str(ai_error)}")
            ai_service_status = "unavailable"
        
        # 检查数据库连接
        try:
            db.execute(text("SELECT 1"))
            database_status = "connected"
        except Exception as db_error:
            logger.error(f"数据库连接检查失败: {str(db_error)}")
            database_status = "disconnected"
        
        # 功能特性开关
        feature_flags = {
            "brain_generator": ai_service_status == "available",
            "character_templates": True,  # 这个功能不依赖AI服务
            "ai_generation": ai_service_status in ["available", "limited"]
        }
        
        return {
            "status": "success",
            "data": {
                "ai_service": ai_service_status,
                "database": database_status,
                "feature_flags": feature_flags
            },
            "message": "系统状态获取成功"
        }
        
    except Exception as e:
        logger.error(f"获取系统状态异常: {str(e)}")
        # 即使出错也要返回基本状态信息
        return {
            "status": "success",
            "data": {
                "ai_service": "unavailable",
                "database": "disconnected",
                "feature_flags": {
                    "brain_generator": False,
                    "character_templates": True,
                    "ai_generation": False
                }
            },
            "message": "系统状态获取成功（部分服务不可用）"
        }


@router.get("/status/detailed")
async def get_detailed_generation_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取详细的AI生成服务状态 - 需要登录
    """
    try:
        # 获取服务实例
        prompt_service = get_prompt_service(db)
        generation_service = get_generation_service(prompt_service)
        
        # 获取详细服务状态
        status_info = generation_service.get_service_status()
        
        return {
            "status": "success",
            "data": status_info,
            "message": "详细服务状态获取成功"
        }
        
    except Exception as e:
        logger.error(f"获取详细生成服务状态异常: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取详细服务状态时发生内部错误"
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


# 新的脑洞生成器接口

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