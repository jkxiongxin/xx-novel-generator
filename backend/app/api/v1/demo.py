"""
演示API接口 - 无需认证
Author: AI Writer Team
Created: 2025-06-01
"""

import logging
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
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
async def demo_generate_novel_name(
    request: NovelNameRequest,
    db: Session = Depends(get_db)
):
    """
    演示：生成小说名（无需认证）
    
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
        
        logger.info(f"演示用户生成小说名成功")
        return result
        
    except AIServiceError as e:
        logger.error(f"小说名生成失败: {str(e)}")
        # 返回模拟数据而不是错误
        return _get_mock_novel_names()
    except Exception as e:
        logger.error(f"小说名生成异常: {str(e)}")
        # 返回模拟数据而不是错误
        return _get_mock_novel_names()


@router.post("/novel-idea", response_model=StructuredGenerationResponse)
async def demo_generate_novel_idea(
    request: NovelIdeaRequest,
    db: Session = Depends(get_db)
):
    """
    演示：生成小说创意（无需认证）
    
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
        
        logger.info(f"演示用户生成小说创意成功")
        return result
        
    except AIServiceError as e:
        logger.error(f"小说创意生成失败: {str(e)}")
        # 返回模拟数据而不是错误
        return _get_mock_novel_idea(request)
    except Exception as e:
        logger.error(f"小说创意生成异常: {str(e)}")
        # 返回模拟数据而不是错误
        return _get_mock_novel_idea(request)


@router.post("/brain-storm", response_model=StructuredGenerationResponse)
async def demo_generate_brain_storm(
    request: BrainStormRequest,
    db: Session = Depends(get_db)
):
    """
    演示：脑洞生成器（无需认证）
    
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
        
        logger.info(f"演示用户生成脑洞创意成功")
        return result
        
    except AIServiceError as e:
        logger.error(f"脑洞生成失败: {str(e)}")
        # 返回模拟数据而不是错误
        return _get_mock_brain_storm(request)
    except Exception as e:
        logger.error(f"脑洞生成异常: {str(e)}")
        # 返回模拟数据而不是错误
        return _get_mock_brain_storm(request)


@router.get("/status")
async def demo_get_generation_status():
    """
    演示：获取AI生成服务状态（无需认证）
    """
    return {
        "status": "success",
        "data": {
            "ai_service_available": False,  # 演示模式
            "available_adapters": ["demo"],
            "default_adapter": "demo"
        },
        "message": "演示模式：服务状态获取成功"
    }


# 模拟数据生成函数
def _get_mock_novel_names() -> StructuredGenerationResponse:
    """返回模拟的小说名生成结果"""
    return StructuredGenerationResponse(
        data={
            "titles": [
                {"title": "星辰大海的征途", "reason": "体现了宏大的宇宙背景和冒险精神"},
                {"title": "时光倒流的秘密", "reason": "充满神秘色彩，暗示时间穿越的奇幻元素"},
                {"title": "最后的守护者", "reason": "突出主角的责任感和英雄气概"},
                {"title": "消失的文明密码", "reason": "结合了考古元素和解谜悬疑"},
                {"title": "重生之商业帝国", "reason": "都市题材，主角重新崛起的励志故事"}
            ]
        },
        tokens_used=500,
        model_used="演示模式",
        generation_time=1.2
    )


def _get_mock_novel_idea(request: NovelIdeaRequest) -> StructuredGenerationResponse:
    """返回模拟的小说创意生成结果"""
    genre = request.genre or "科幻"
    return StructuredGenerationResponse(
        data={
            "idea": {
                "title": f"《{genre}纪元：新世界的曙光》",
                "setting": f"2185年，地球因环境恶化不再适宜居住，人类被迫迁移到太空殖民地。在名为'新伊甸'的巨型太空站上，三个不同社会阶层形成了严格的等级制度。",
                "main_character": "艾莉娅·陈，25岁，底层区的维修工程师，意外发现了太空站核心系统的致命缺陷，同时拥有罕见的'量子感知'能力，能够感应到其他维度的信息。",
                "conflict": "太空站的能源系统即将崩溃，而统治阶层为了维护自己的利益选择隐瞒真相。艾莉娅必须在有限的时间内，团结各个阶层的人民，寻找拯救所有人的方法。",
                "plot": "从发现危机到揭露真相，再到团结民众、寻找解决方案，最终通过跨维度合作找到新的家园，是一个关于成长、团结和希望的故事。",
                "unique_selling_point": "结合了太空歌剧的宏大背景、社会层级的深刻反思、以及跨维度科幻元素，展现了人性在极端环境下的光辉。",
                "target_audience": "喜欢科幻小说、关注社会议题、年龄在18-35岁的读者群体"
            }
        },
        tokens_used=800,
        model_used="演示模式",
        generation_time=2.1
    )


def _get_mock_brain_storm(request: BrainStormRequest) -> StructuredGenerationResponse:
    """返回模拟的脑洞生成结果"""
    topic = request.topic or "创意写作"
    return StructuredGenerationResponse(
        data={
            "brainstorms": [
                {
                    "style": "现实向",
                    "concept": f"基于{topic}的社区互助平台",
                    "implementation": "通过移动APP连接同城有相同兴趣的人，建立线下活动和线上交流的社区生态",
                    "development": "可以扩展为技能分享、知识付费、本地化服务等多元化平台"
                },
                {
                    "style": "想象向",
                    "concept": f"能够感知{topic}灵感的AI伙伴",
                    "implementation": "开发一个具有情感认知能力的AI，能够理解创作者的情绪状态并提供个性化的创作建议",
                    "development": "进化为能够与人类进行深度创作协作的智能体，共同创造出人机结合的艺术作品"
                },
                {
                    "style": "颠覆向",
                    "concept": f"反向{topic}：从结果逆推过程",
                    "implementation": "从理想的结果开始，运用逆向思维分析实现路径，打破传统的线性思考模式",
                    "development": "建立全新的思维训练体系，培养人们从多个维度和角度思考问题的能力"
                }
            ]
        },
        tokens_used=600,
        model_used="演示模式",
        generation_time=1.8
    )