"""
管理员角色模板管理API
Author: AI Assistant
Created: 2025-06-03
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc

from app.core.database import get_db
from app.core.dependencies import require_admin_user
from app.models.user import User
from app.models.character import Character, CharacterType, CharacterGender
from app.models.character_template import (
    CharacterTemplateDetail, UsageExample
)
from app.schemas.character_template import (
    CharacterTemplateCreateRequest, CharacterTemplateCreateResponse,
    CharacterTemplateUpdateRequest, CharacterTemplateUpdateResponse,
    CharacterTemplateDeleteResponse, AdminTemplateListResponse,
    CharacterTemplateResponse, TemplateDetailCreate, TemplateDetailResponse,
    TemplateStatusUpdateRequest, BatchTemplateStatusUpdateRequest,
    BatchTemplateStatusUpdateResponse, UsageExampleCreate, UsageExampleResponse
)

router = APIRouter(prefix="/admin/character-templates", tags=["管理员-角色模板管理"])


@router.post("", response_model=CharacterTemplateCreateResponse)
async def create_character_template(
    request: CharacterTemplateCreateRequest,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin_user)
):
    """
    创建角色模板
    
    Args:
        request: 创建请求
        db: 数据库会话
        admin_user: 管理员用户
        
    Returns:
        创建结果
    """
    try:
        # 创建角色基础信息
        character_data = {
            "name": request.name,
            "gender": request.gender,
            "personality": request.personality,
            "character_type": request.character_type,
            "tags": request.tags,
            "description": request.description,
            "abilities": request.abilities,
            "power_system": request.power_system,
            "original_world": request.original_world,
            "is_template": True,  # 标记为模板
            "user_id": admin_user.id  # 设置创建者为管理员
        }
        
        # 创建角色记录
        character = Character(**character_data)
        db.add(character)
        db.flush()  # 获取角色ID
        
        # 如果有模板详情，创建详情记录
        template_detail = None
        if request.template_detail:
            detail_data = request.template_detail.model_dump()
            detail_data["character_id"] = character.id
            detail_data["is_new"] = True  # 新创建的模板标记为新增
            
            template_detail = CharacterTemplateDetail(**detail_data)
            db.add(template_detail)
            db.flush()
        
        db.commit()
        
        # 构建响应数据
        template_dict = character.to_dict()
        if template_detail:
            template_dict["template_detail"] = TemplateDetailResponse.model_validate(template_detail)
        template_dict["usage_examples"] = []
        template_dict["is_favorited"] = False
        
        return CharacterTemplateCreateResponse(
            success=True,
            template=CharacterTemplateResponse.model_validate(template_dict),
            message="角色模板创建成功"
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建角色模板失败: {str(e)}"
        )


@router.put("/{template_id}", response_model=CharacterTemplateUpdateResponse)
async def update_character_template(
    template_id: int = Path(..., description="模板ID"),
    request: CharacterTemplateUpdateRequest = ...,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin_user)
):
    """
    更新角色模板
    
    Args:
        template_id: 模板ID
        request: 更新请求
        db: 数据库会话
        admin_user: 管理员用户
        
    Returns:
        更新结果
    """
    try:
        # 查询角色模板
        character = db.query(Character).filter(
            Character.id == template_id,
            Character.is_template == True
        ).first()
        
        if not character:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="角色模板不存在"
            )
        
        # 更新角色基础信息
        update_data = request.model_dump(exclude_unset=True, exclude={"template_detail"})
        character.update_from_dict(update_data)
        
        # 查询或创建模板详情
        template_detail = db.query(CharacterTemplateDetail).filter(
            CharacterTemplateDetail.character_id == template_id
        ).first()
        
        if request.template_detail:
            detail_data = request.template_detail.model_dump()
            
            if template_detail:
                # 更新现有详情
                template_detail.update_from_dict(detail_data)
            else:
                # 创建新详情
                detail_data["character_id"] = template_id
                template_detail = CharacterTemplateDetail(**detail_data)
                db.add(template_detail)
        
        db.commit()
        
        # 构建响应数据
        template_dict = character.to_dict()
        if template_detail:
            template_dict["template_detail"] = TemplateDetailResponse.model_validate(template_detail)
        
        # 获取使用示例
        usage_examples = db.query(UsageExample).filter(
            UsageExample.template_detail_id == template_detail.id if template_detail else None
        ).all()
        template_dict["usage_examples"] = [
            UsageExampleResponse.model_validate(example) for example in usage_examples
        ]
        template_dict["is_favorited"] = False
        
        return CharacterTemplateUpdateResponse(
            success=True,
            template=CharacterTemplateResponse.model_validate(template_dict),
            message="角色模板更新成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新角色模板失败: {str(e)}"
        )


@router.delete("/{template_id}", response_model=CharacterTemplateDeleteResponse)
async def delete_character_template(
    template_id: int = Path(..., description="模板ID"),
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin_user)
):
    """
    删除角色模板
    
    Args:
        template_id: 模板ID
        db: 数据库会话
        admin_user: 管理员用户
        
    Returns:
        删除结果
    """
    try:
        # 查询角色模板
        character = db.query(Character).filter(
            Character.id == template_id,
            Character.is_template == True
        ).first()
        
        if not character:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="角色模板不存在"
            )
        
        # 检查是否有使用记录
        from app.models.character_template import CharacterTemplateUsage
        usage_count = db.query(func.count(CharacterTemplateUsage.id)).filter(
            CharacterTemplateUsage.template_id == template_id
        ).scalar()
        
        if usage_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"该模板已被使用 {usage_count} 次，无法删除"
            )
        
        # 删除角色（会级联删除相关数据）
        db.delete(character)
        db.commit()
        
        return CharacterTemplateDeleteResponse(
            success=True,
            template_id=template_id,
            message="角色模板删除成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除角色模板失败: {str(e)}"
        )


@router.get("", response_model=AdminTemplateListResponse)
async def get_admin_template_list(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    gender: Optional[str] = Query(None, description="性别筛选"),
    character_type: Optional[str] = Query(None, description="角色类型筛选"),
    is_popular: Optional[bool] = Query(None, description="是否热门"),
    is_new: Optional[bool] = Query(None, description="是否新增"),
    sort_by: str = Query("created_at", description="排序字段"),
    sort_order: str = Query("desc", description="排序方向"),
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin_user)
):
    """
    获取管理员模板列表（包含更多管理信息）
    
    Args:
        page: 页码
        page_size: 每页数量
        search: 搜索关键词
        gender: 性别筛选
        character_type: 角色类型筛选
        is_popular: 是否热门
        is_new: 是否新增
        sort_by: 排序字段
        sort_order: 排序方向
        db: 数据库会话
        admin_user: 管理员用户
        
    Returns:
        管理员模板列表
    """
    try:
        # 构建查询
        query = db.query(Character).join(
            CharacterTemplateDetail,
            Character.id == CharacterTemplateDetail.character_id,
            isouter=True
        ).filter(Character.is_template == True)
        
        # 应用搜索
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    Character.name.like(search_pattern),
                    Character.description.like(search_pattern),
                    Character.personality.like(search_pattern)
                )
            )
        
        # 应用筛选
        if gender:
            query = query.filter(Character.gender == gender)
        
        if character_type:
            query = query.filter(Character.character_type == character_type)
        
        if is_popular is not None:
            query = query.filter(CharacterTemplateDetail.is_popular == is_popular)
        
        if is_new is not None:
            query = query.filter(CharacterTemplateDetail.is_new == is_new)
        
        # 应用排序
        if sort_by in ["usage_count", "rating", "is_popular", "is_new"]:
            sort_column = getattr(CharacterTemplateDetail, sort_by)
        else:
            sort_column = getattr(Character, sort_by if hasattr(Character, sort_by) else "created_at")
        
        if sort_order.lower() == "asc":
            query = query.order_by(sort_column)
        else:
            query = query.order_by(desc(sort_column))
        
        # 获取总数并应用分页
        total = query.count()
        offset = (page - 1) * page_size
        templates = query.offset(offset).limit(page_size).all()
        
        # 构建响应数据
        template_responses = []
        for template in templates:
            template_dict = template.to_dict()
            
            # 添加模板详情
            if template.template_detail:
                template_dict["template_detail"] = TemplateDetailResponse.model_validate(template.template_detail)
            
            # 获取使用示例
            if template.template_detail:
                usage_examples = db.query(UsageExample).filter(
                    UsageExample.template_detail_id == template.template_detail.id
                ).all()
                template_dict["usage_examples"] = [
                    UsageExampleResponse.model_validate(example) for example in usage_examples
                ]
            else:
                template_dict["usage_examples"] = []
            
            template_dict["is_favorited"] = False
            template_responses.append(CharacterTemplateResponse.model_validate(template_dict))
        
        # 计算总页数
        total_pages = (total + page_size - 1) // page_size
        
        return AdminTemplateListResponse(
            templates=template_responses,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取管理员模板列表失败: {str(e)}"
        )


@router.patch("/{template_id}/status", response_model=CharacterTemplateUpdateResponse)
async def update_template_status(
    template_id: int = Path(..., description="模板ID"),
    request: TemplateStatusUpdateRequest = ...,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin_user)
):
    """
    更新模板状态
    
    Args:
        template_id: 模板ID
        request: 状态更新请求
        db: 数据库会话
        admin_user: 管理员用户
        
    Returns:
        更新结果
    """
    try:
        # 查询模板详情
        template_detail = db.query(CharacterTemplateDetail).filter(
            CharacterTemplateDetail.character_id == template_id
        ).first()
        
        if not template_detail:
            # 如果没有详情，创建一个
            character = db.query(Character).filter(
                Character.id == template_id,
                Character.is_template == True
            ).first()
            
            if not character:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="角色模板不存在"
                )
            
            template_detail = CharacterTemplateDetail(character_id=template_id)
            db.add(template_detail)
            db.flush()
        
        # 更新状态
        update_data = request.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(template_detail, field):
                setattr(template_detail, field, value)
        
        db.commit()
        
        # 获取完整模板信息
        character = db.query(Character).filter(Character.id == template_id).first()
        template_dict = character.to_dict()
        template_dict["template_detail"] = TemplateDetailResponse.model_validate(template_detail)
        template_dict["usage_examples"] = []
        template_dict["is_favorited"] = False
        
        return CharacterTemplateUpdateResponse(
            success=True,
            template=CharacterTemplateResponse.model_validate(template_dict),
            message="模板状态更新成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新模板状态失败: {str(e)}"
        )


@router.patch("/batch/status", response_model=BatchTemplateStatusUpdateResponse)
async def batch_update_template_status(
    request: BatchTemplateStatusUpdateRequest,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin_user)
):
    """
    批量更新模板状态
    
    Args:
        request: 批量更新请求
        db: 数据库会话
        admin_user: 管理员用户
        
    Returns:
        批量更新结果
    """
    try:
        success_count = 0
        failed_count = 0
        failed_items = []
        
        for template_id in request.template_ids:
            try:
                # 查询模板详情
                template_detail = db.query(CharacterTemplateDetail).filter(
                    CharacterTemplateDetail.character_id == template_id
                ).first()
                
                if not template_detail:
                    # 检查角色是否存在
                    character = db.query(Character).filter(
                        Character.id == template_id,
                        Character.is_template == True
                    ).first()
                    
                    if not character:
                        failed_items.append({
                            "template_id": template_id,
                            "reason": "角色模板不存在"
                        })
                        failed_count += 1
                        continue
                    
                    # 创建模板详情
                    template_detail = CharacterTemplateDetail(character_id=template_id)
                    db.add(template_detail)
                    db.flush()
                
                # 更新状态
                update_data = request.status_updates.model_dump(exclude_unset=True)
                for field, value in update_data.items():
                    if hasattr(template_detail, field):
                        setattr(template_detail, field, value)
                
                success_count += 1
                
            except Exception as e:
                failed_items.append({
                    "template_id": template_id,
                    "reason": str(e)
                })
                failed_count += 1
        
        db.commit()
        
        return BatchTemplateStatusUpdateResponse(
            success_count=success_count,
            failed_count=failed_count,
            failed_items=failed_items,
            message=f"批量更新完成，成功 {success_count} 个，失败 {failed_count} 个"
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"批量更新模板状态失败: {str(e)}"
        )


@router.post("/{template_id}/usage-examples", response_model=UsageExampleResponse)
async def create_usage_example(
    template_id: int = Path(..., description="模板ID"),
    request: UsageExampleCreate = ...,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin_user)
):
    """
    为模板添加使用示例
    
    Args:
        template_id: 模板ID
        request: 使用示例创建请求
        db: 数据库会话
        admin_user: 管理员用户
        
    Returns:
        创建的使用示例
    """
    try:
        # 查询模板详情
        template_detail = db.query(CharacterTemplateDetail).filter(
            CharacterTemplateDetail.character_id == template_id
        ).first()
        
        if not template_detail:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="模板详情不存在"
            )
        
        # 创建使用示例
        example_data = request.model_dump()
        example_data["template_detail_id"] = template_detail.id
        
        usage_example = UsageExample(**example_data)
        db.add(usage_example)
        db.commit()
        
        return UsageExampleResponse.model_validate(usage_example)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建使用示例失败: {str(e)}"
        )