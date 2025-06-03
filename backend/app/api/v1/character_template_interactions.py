"""
角色模板交互API
Author: AI Assistant
Created: 2025-06-03
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.character import Character
from app.models.character_template import (
    CharacterTemplateDetail, CharacterTemplateFavorite, CharacterTemplateUsage
)
from app.schemas.character_template import (
    UseTemplateRequest, UseTemplateResponse, BatchUseTemplatesRequest,
    BatchUseTemplatesResponse, FavoriteResponse, GetFavoriteTemplatesResponse,
    GetRecommendationsResponse, RecommendedCharacter
)
from app.schemas.character import CharacterResponse, CharacterSummaryResponse
from app.models.novel import Novel

router = APIRouter(prefix="/character-templates", tags=["角色模板交互"])


@router.post("/{template_id}/use", response_model=UseTemplateResponse)
async def use_character_template(
    template_id: int = Path(..., description="角色模板ID"),
    request: UseTemplateRequest = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    使用角色模板创建新角色
    
    Args:
        template_id: 角色模板ID
        request: 使用模板请求
        db: 数据库会话
        current_user: 当前用户
        
    Returns:
        创建的角色信息
    """
    try:
        # 验证模板是否存在
        template = db.query(Character).filter(
            Character.id == template_id,
            Character.is_template == True
        ).first()
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="角色模板不存在"
            )
            
        # 验证小说是否存在且属于当前用户
        novel = db.query(Novel).filter(
            Novel.id == request.novel_id,
            Novel.user_id == current_user.id
        ).first()
        
        if not novel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="小说不存在或无权访问"
            )
            
        # 检查是否已经从这个模板创建过角色
        existing_character = db.query(Character).filter(
            Character.novel_id == request.novel_id,
            Character.from_template_id == template_id,
            Character.user_id == current_user.id
        ).first()
        
        if existing_character:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"已经从该模板创建过角色: {existing_character.name}"
            )
            
        # 创建新角色
        character_dict = template.to_dict()
        
        # 移除不需要的字段
        for field in ["id", "created_at", "updated_at"]:
            if field in character_dict:
                character_dict.pop(field)
                
        # 更新必要字段
        character_dict["is_template"] = False
        character_dict["novel_id"] = request.novel_id
        character_dict["user_id"] = current_user.id
        character_dict["from_template_id"] = template_id
        
        # 应用自定义修改
        if request.customizations:
            for field, value in request.customizations.items():
                if field in character_dict and field not in ["id", "user_id", "from_template_id"]:
                    character_dict[field] = value
        
        # 创建角色实例
        new_character = Character(**character_dict)
        db.add(new_character)
        db.flush()  # 获取ID但不提交
        
        # 记录使用记录
        usage_record = CharacterTemplateUsage(
            user_id=current_user.id,
            template_id=template_id,
            target_id=new_character.id,
            novel_id=request.novel_id,
            customizations=request.customizations or {},
            adaptation_notes=request.adaptation_notes
        )
        db.add(usage_record)
        
        # 更新模板使用次数
        template_detail = db.query(CharacterTemplateDetail).filter(
            CharacterTemplateDetail.character_id == template_id
        ).first()
        
        if template_detail:
            template_detail.usage_count += 1
        
        # 提交事务
        db.commit()
        db.refresh(new_character)
        
        # 确定是否应用了适配
        adaptation_applied = bool(
            request.customizations or request.adaptation_notes
        )
        
        return UseTemplateResponse(
            success=True,
            character=CharacterResponse.model_validate(new_character),
            template_used=CharacterSummaryResponse.model_validate(template.to_summary_dict()),
            adaptation_applied=adaptation_applied,
            message=f"成功从模板创建角色: {new_character.name}"
        )
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"使用角色模板失败: {str(e)}"
        )


@router.post("/batch-use", response_model=BatchUseTemplatesResponse)
async def batch_use_templates(
    request: BatchUseTemplatesRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    批量使用角色模板创建角色
    
    Args:
        request: 批量使用模板请求
        db: 数据库会话
        current_user: 当前用户
        
    Returns:
        批量创建的结果信息
    """
    try:
        # 验证小说是否存在且属于当前用户
        novel = db.query(Novel).filter(
            Novel.id == request.novel_id,
            Novel.user_id == current_user.id
        ).first()
        
        if not novel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="小说不存在或无权访问"
            )
            
        created_characters = []
        failed_items = []
        
        # 处理每个模板
        for item in request.templates:
            try:
                # 验证模板是否存在
                template = db.query(Character).filter(
                    Character.id == item.template_id,
                    Character.is_template == True
                ).first()
                
                if not template:
                    failed_items.append({
                        "template_id": item.template_id,
                        "reason": "模板不存在"
                    })
                    continue
                    
                # 检查是否已经从这个模板创建过角色
                existing_character = db.query(Character).filter(
                    Character.novel_id == request.novel_id,
                    Character.from_template_id == item.template_id,
                    Character.user_id == current_user.id
                ).first()
                
                if existing_character:
                    failed_items.append({
                        "template_id": item.template_id,
                        "reason": f"已经从该模板创建过角色: {existing_character.name}"
                    })
                    continue
                    
                # 创建新角色
                character_dict = template.to_dict()
                
                # 移除不需要的字段
                for field in ["id", "created_at", "updated_at"]:
                    if field in character_dict:
                        character_dict.pop(field)
                        
                # 更新必要字段
                character_dict["is_template"] = False
                character_dict["novel_id"] = request.novel_id
                character_dict["user_id"] = current_user.id
                character_dict["from_template_id"] = item.template_id
                
                # 应用自定义修改
                if item.customizations:
                    for field, value in item.customizations.items():
                        if field in character_dict and field not in ["id", "user_id", "from_template_id"]:
                            character_dict[field] = value
                
                # 创建角色实例
                new_character = Character(**character_dict)
                db.add(new_character)
                db.flush()  # 获取ID但不提交
                
                # 记录使用记录
                usage_record = CharacterTemplateUsage(
                    user_id=current_user.id,
                    template_id=item.template_id,
                    target_id=new_character.id,
                    novel_id=request.novel_id,
                    customizations=item.customizations or {}
                )
                db.add(usage_record)
                
                # 更新模板使用次数
                template_detail = db.query(CharacterTemplateDetail).filter(
                    CharacterTemplateDetail.character_id == item.template_id
                ).first()
                
                if template_detail:
                    template_detail.usage_count += 1
                    
                # 添加到成功列表
                created_characters.append(
                    CharacterSummaryResponse.model_validate(new_character.to_summary_dict())
                )
                
            except Exception as e:
                failed_items.append({
                    "template_id": item.template_id,
                    "reason": str(e)
                })
        
        # 如果全部失败，回滚事务
        if not created_characters:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="所有角色模板添加失败"
            )
            
        # 提交事务
        db.commit()
        
        return BatchUseTemplatesResponse(
            success_count=len(created_characters),
            failed_count=len(failed_items),
            created_characters=created_characters,
            failed_items=failed_items,
            message=f"成功添加{len(created_characters)}个角色，失败{len(failed_items)}个"
        )
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"批量使用角色模板失败: {str(e)}"
        )


@router.post("/{template_id}/favorite", response_model=FavoriteResponse)
async def toggle_favorite_template(
    template_id: int = Path(..., description="角色模板ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    收藏或取消收藏角色模板
    
    Args:
        template_id: 角色模板ID
        db: 数据库会话
        current_user: 当前用户
        
    Returns:
        收藏状态
    """
    try:
        # 验证模板是否存在
        template = db.query(Character).filter(
            Character.id == template_id,
            Character.is_template == True
        ).first()
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="角色模板不存在"
            )
            
        # 检查是否已收藏
        favorite = db.query(CharacterTemplateFavorite).filter(
            CharacterTemplateFavorite.character_id == template_id,
            CharacterTemplateFavorite.user_id == current_user.id
        ).first()
        
        if favorite:
            # 取消收藏
            db.delete(favorite)
            db.commit()
            return FavoriteResponse(
                success=True,
                is_favorited=False,
                message=f"已取消收藏角色模板: {template.name}"
            )
        else:
            # 添加收藏
            new_favorite = CharacterTemplateFavorite(
                user_id=current_user.id,
                character_id=template_id
            )
            db.add(new_favorite)
            db.commit()
            return FavoriteResponse(
                success=True,
                is_favorited=True,
                message=f"已收藏角色模板: {template.name}"
            )
            
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"收藏操作失败: {str(e)}"
        )


@router.get("/favorites", response_model=GetFavoriteTemplatesResponse)
async def get_favorite_templates(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取用户收藏的角色模板列表
    
    Args:
        db: 数据库会话
        current_user: 当前用户
        
    Returns:
        收藏的角色模板列表
    """
    try:
        # 查询用户收藏的模板ID
        favorites = db.query(CharacterTemplateFavorite).filter(
            CharacterTemplateFavorite.user_id == current_user.id
        ).all()
        
        favorited_ids = [f.character_id for f in favorites]
        
        if not favorited_ids:
            return GetFavoriteTemplatesResponse(
                characters=[],
                total=0
            )
            
        # 查询收藏的模板角色
        templates = db.query(Character).outerjoin(
            CharacterTemplateDetail,
            Character.id == CharacterTemplateDetail.character_id
        ).filter(
            Character.id.in_(favorited_ids)
        ).all()
        
        # 构建响应数据
        template_responses = []
        for template in templates:
            template_dict = template.to_summary_dict()
            
            if hasattr(template, "template_detail") and template.template_detail:
                template_dict.update({
                    "usage_count": template.template_detail.usage_count,
                    "rating": template.template_detail.rating,
                    "is_popular": template.template_detail.is_popular,
                    "is_new": template.template_detail.is_new
                })
            else:
                template_dict.update({
                    "usage_count": 0,
                    "rating": 0.0,
                    "is_popular": False,
                    "is_new": False
                })
                
            template_dict["is_favorited"] = True
            template_responses.append(
                template_dict
            )
        
        return GetFavoriteTemplatesResponse(
            characters=template_responses,
            total=len(template_responses)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取收藏模板失败: {str(e)}"
        )


@router.get("/recommendations", response_model=GetRecommendationsResponse)
async def get_template_recommendations(
    based_on: str = "popular",
    novel_id: int = None,
    limit: int = 10,
    exclude_used: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取推荐的角色模板
    
    Args:
        based_on: 推荐依据 (popular, usage_history, current_novel, similar)
        novel_id: 小说ID (用于基于小说的推荐)
        limit: 推荐数量
        exclude_used: 是否排除已使用的
        db: 数据库会话
        current_user: 当前用户
        
    Returns:
        推荐的角色模板列表
    """
    try:
        # 基础查询
        query = db.query(Character).join(
            CharacterTemplateDetail,
            Character.id == CharacterTemplateDetail.character_id
        ).filter(
            Character.is_template == True
        )
        
        # 如果需要排除已使用的
        if exclude_used and novel_id:
            # 获取已使用的模板ID
            used_templates = db.query(CharacterTemplateUsage.template_id).filter(
                CharacterTemplateUsage.user_id == current_user.id,
                CharacterTemplateUsage.novel_id == novel_id
            ).distinct().all()
            
            used_ids = [item[0] for item in used_templates]
            
            if used_ids:
                query = query.filter(Character.id.notin_(used_ids))
                
        # 根据推荐依据应用不同的排序和筛选
        recommendation_reason = ""
        
        if based_on == "popular":
            query = query.order_by(desc(CharacterTemplateDetail.usage_count))
            recommendation_reason = "基于热门角色推荐"
            
        elif based_on == "usage_history" and current_user:
            # 获取用户历史使用的角色类型和标签
            user_usages = db.query(CharacterTemplateUsage).filter(
                CharacterTemplateUsage.user_id == current_user.id
            ).all()
            
            if user_usages:
                # 获取历史使用的模板ID
                used_template_ids = [usage.template_id for usage in user_usages]
                
                # 获取历史使用的模板
                used_templates = db.query(Character).filter(
                    Character.id.in_(used_template_ids)
                ).all()
                
                # 提取使用历史中的标签和角色类型
                used_tags = []
                used_character_types = []
                
                for template in used_templates:
                    if template.tags:
                        used_tags.extend(template.tags)
                    if template.character_type:
                        used_character_types.append(template.character_type)
                        
                # 移除重复项
                used_tags = list(set(used_tags))
                used_character_types = list(set(used_character_types))
                
                # 构建基于使用历史的推荐
                if used_tags or used_character_types:
                    conditions = []
                    
                    # 基于标签
                    for tag in used_tags[:3]:  # 只使用前3个标签
                        conditions.append(Character.tags.contains([tag]))
                        
                    # 基于角色类型
                    for char_type in used_character_types:
                        conditions.append(Character.character_type == char_type)
                        
                    if conditions:
                        query = query.filter(or_(*conditions))
                        recommendation_reason = "基于您的使用历史推荐"
            else:
                # 没有使用历史，回退到流行推荐
                query = query.order_by(desc(CharacterTemplateDetail.usage_count))
                recommendation_reason = "热门角色推荐"
                
        elif based_on == "current_novel" and novel_id:
            # 获取小说信息
            novel = db.query(Novel).filter(
                Novel.id == novel_id
            ).first()
            
            if novel:
                # 获取小说中的现有角色
                existing_characters = db.query(Character).filter(
                    Character.novel_id == novel_id,
                    Character.user_id == current_user.id
                ).all()
                
                # 提取现有角色的标签和类型
                novel_tags = []
                novel_character_types = []
                
                for character in existing_characters:
                    if character.tags:
                        novel_tags.extend(character.tags)
                    if character.character_type:
                        novel_character_types.append(character.character_type)
                        
                # 移除重复项
                novel_tags = list(set(novel_tags))
                novel_character_types = list(set(novel_character_types))
                
                # 构建基于小说的推荐
                if novel_tags or novel_character_types:
                    conditions = []
                    
                    # 基于标签
                    for tag in novel_tags[:3]:  # 只使用前3个标签
                        conditions.append(Character.tags.contains([tag]))
                        
                    # 基于角色类型
                    # 推荐与现有角色互补的类型
                    complementary_types = []
                    if "protagonist" not in novel_character_types:
                        complementary_types.append("protagonist")
                    if "antagonist" not in novel_character_types:
                        complementary_types.append("antagonist")
                    if "supporting" not in novel_character_types:
                        complementary_types.append("supporting")
                        
                    for char_type in complementary_types:
                        conditions.append(Character.character_type == char_type)
                        
                    if conditions:
                        query = query.filter(or_(*conditions))
                        recommendation_reason = f"基于《{novel.title}》小说推荐"
                else:
                    # 没有足够信息，回退到基于小说类型的推荐
                    if novel.genre:
                        recommendation_reason = f"适合{novel.genre}类型小说的角色"
            else:
                # 小说不存在，回退到流行推荐
                query = query.order_by(desc(CharacterTemplateDetail.usage_count))
                recommendation_reason = "热门角色推荐"
        
        # 限制结果数量
        templates = query.limit(limit).all()
        
        # 获取用户收藏记录
        favorited_template_ids = db.query(CharacterTemplateFavorite.character_id).filter(
            CharacterTemplateFavorite.user_id == current_user.id
        ).all()
        favorited_ids = [item[0] for item in favorited_template_ids]
        
        # 构建响应数据
        recommended_characters = []
        for template in templates:
            # 构建基本信息
            template_dict = template.to_summary_dict()
            
            if template.template_detail:
                template_dict.update({
                    "usage_count": template.template_detail.usage_count,
                    "rating": template.template_detail.rating,
                    "is_popular": template.template_detail.is_popular,
                    "is_new": template.template_detail.is_new
                })
            else:
                template_dict.update({
                    "usage_count": 0,
                    "rating": 0.0,
                    "is_popular": False,
                    "is_new": False
                })
                
            # 设置收藏状态
            template_dict["is_favorited"] = template.id in favorited_ids
            
            # 添加推荐信息
            template_dict["recommendation_score"] = 0.8 + (0.2 * (template_dict.get("usage_count", 0) / 100))
            template_dict["fit_score"] = 0.7 + (0.3 * (template_dict.get("rating", 0) / 5))
            
            # 简单的推荐理由
            recommendation_reasons = []
            if template_dict.get("is_popular", False):
                recommendation_reasons.append("热门角色")
            if template_dict.get("is_new", False):
                recommendation_reasons.append("新添加的角色")
            if template.character_type == "protagonist":
                recommendation_reasons.append("优秀的主角选择")
            elif template.character_type == "antagonist":
                recommendation_reasons.append("出色的反派角色")
            elif template.character_type == "supporting":
                recommendation_reasons.append("精彩的配角")
            
            if not recommendation_reasons:
                recommendation_reasons.append("可能适合您的故事")
                
            template_dict["recommendation_reasons"] = recommendation_reasons
            
            recommended_characters.append(RecommendedCharacter.model_validate(template_dict))
        
        return GetRecommendationsResponse(
            recommendations=recommended_characters,
            recommendation_reason=recommendation_reason
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取角色推荐失败: {str(e)}"
        )