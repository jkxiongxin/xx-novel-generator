"""
角色管理API
Author: AI Assistant
Created: 2025-06-01
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import logging

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.character import Character, CharacterType, CharacterGender
from app.schemas.character import (
    CharacterCreate, CharacterUpdate, CharacterResponse,
    CharacterSummaryResponse, CharacterListResponse,
    CharacterGenerationRequest, CharacterGenerationResponse,
    CharacterFilterRequest, CharacterBatchAddRequest, CharacterBatchAddResponse
)
from app.services.generation_service import get_generation_service
from app.services.prompt_service import get_prompt_service
from app.models.novel import Novel
from app.models.worldview import Worldview

router = APIRouter(prefix="/characters", tags=["角色管理"])
logger = logging.getLogger(__name__)


@router.post("/", response_model=CharacterResponse, status_code=status.HTTP_201_CREATED)
async def create_character(
    character_data: CharacterCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建角色
    
    Args:
        character_data: 角色创建数据
        db: 数据库会话
        current_user: 当前用户
        
    Returns:
        CharacterResponse: 创建的角色信息
    """
    try:
        # 如果指定了小说ID，验证小说是否属于当前用户
        if character_data.novel_id:
            novel = db.query(Novel).filter(
                and_(Novel.id == character_data.novel_id, Novel.user_id == current_user.id)
            ).first()
            if not novel:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="小说不存在或无权访问"
                )
        
        # 创建角色
        character = Character(
            **character_data.model_dump(),
            user_id=current_user.id
        )
        
        db.add(character)
        db.commit()
        db.refresh(character)
        
        return CharacterResponse.model_validate(character)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建角色失败: {str(e)}"
        )


@router.get("/", response_model=CharacterListResponse)
async def get_characters(
    novel_id: Optional[int] = Query(None, description="小说ID筛选"),
    character_type: Optional[str] = Query(None, description="角色类型筛选"),
    gender: Optional[str] = Query(None, description="性别筛选"),
    is_template: Optional[bool] = Query(None, description="是否模板角色筛选"),
    search: Optional[str] = Query(None, description="角色名搜索"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取角色列表
    
    Args:
        novel_id: 小说ID筛选
        character_type: 角色类型筛选
        gender: 性别筛选
        is_template: 是否模板角色筛选
        search: 角色名搜索
        page: 页码
        page_size: 每页数量
        db: 数据库会话
        current_user: 当前用户
        
    Returns:
        CharacterListResponse: 角色列表响应
    """
    try:
        # 构建查询条件
        query = db.query(Character).filter(Character.user_id == current_user.id)
        
        if novel_id:
            query = query.filter(Character.novel_id == novel_id)
        
        if character_type:
            query = query.filter(Character.character_type == character_type)
            
        if gender:
            query = query.filter(Character.gender == gender)
            
        if is_template is not None:
            query = query.filter(Character.is_template == is_template)
            
        if search:
            query = query.filter(Character.name.contains(search))
        
        # 分页处理
        total = query.count()
        offset = (page - 1) * page_size
        characters = query.offset(offset).limit(page_size).all()
        
        # 转换为响应格式
        character_responses = [
            CharacterSummaryResponse(**character.to_summary_dict())
            for character in characters
        ]
        
        total_pages = (total + page_size - 1) // page_size
        
        return CharacterListResponse(
            items=character_responses,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取角色列表失败: {str(e)}"
        )


@router.get("/{character_id}", response_model=CharacterResponse)
async def get_character(
    character_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取单个角色详情"""
    character = db.query(Character).filter(
        and_(Character.id == character_id, Character.user_id == current_user.id)
    ).first()
    
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )
    
    return CharacterResponse.model_validate(character)


@router.put("/{character_id}", response_model=CharacterResponse)
async def update_character(
    character_id: int,
    character_data: CharacterUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新角色信息"""
    try:
        character = db.query(Character).filter(
            and_(Character.id == character_id, Character.user_id == current_user.id)
        ).first()
        
        if not character:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="角色不存在"
            )
        
        # 更新角色信息
        update_data = character_data.model_dump(exclude_unset=True)
        character.update_from_dict(update_data)
        
        db.commit()
        db.refresh(character)
        
        return CharacterResponse.model_validate(character)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新角色失败: {str(e)}"
        )


@router.delete("/{character_id}")
async def delete_character(
    character_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除角色"""
    try:
        character = db.query(Character).filter(
            and_(Character.id == character_id, Character.user_id == current_user.id)
        ).first()
        
        if not character:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="角色不存在"
            )
        
        db.delete(character)
        db.commit()
        
        return {"message": "角色删除成功"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除角色失败: {str(e)}"
        )


@router.get("/templates/", response_model=CharacterListResponse)
async def get_character_templates(
    character_type: Optional[str] = Query(None, description="角色类型筛选"),
    gender: Optional[str] = Query(None, description="性别筛选"),
    power_system: Optional[str] = Query(None, description="力量体系筛选"),
    original_world: Optional[str] = Query(None, description="原生世界筛选"),
    tags: List[str] = Query([], description="标签筛选"),
    search: Optional[str] = Query(None, description="角色名搜索"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取角色模板列表
    
    Args:
        character_type: 角色类型筛选
        gender: 性别筛选
        power_system: 力量体系筛选
        original_world: 原生世界筛选
        tags: 标签筛选
        search: 角色名搜索
        page: 页码
        page_size: 每页数量
        db: 数据库会话
        current_user: 当前用户
        
    Returns:
        CharacterListResponse: 角色模板列表响应
    """
    try:
        # 构建查询条件 - 只查询模板角色
        query = db.query(Character).filter(
            and_(Character.user_id == current_user.id, Character.is_template == True)
        )
        
        if character_type:
            query = query.filter(Character.character_type == character_type)
            
        if gender:
            query = query.filter(Character.gender == gender)
            
        if power_system:
            query = query.filter(Character.power_system.contains(power_system))
            
        if original_world:
            query = query.filter(Character.original_world.contains(original_world))
            
        if search:
            query = query.filter(Character.name.contains(search))
        
        # 分页处理
        total = query.count()
        offset = (page - 1) * page_size
        characters = query.offset(offset).limit(page_size).all()
        
        # 转换为响应格式
        character_responses = [
            CharacterSummaryResponse(**character.to_summary_dict())
            for character in characters
        ]
        
        total_pages = (total + page_size - 1) // page_size
        
        return CharacterListResponse(
            items=character_responses,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取角色模板列表失败: {str(e)}"
        )


@router.post("/batch-add", response_model=CharacterBatchAddResponse)
async def batch_add_characters(
    request: CharacterBatchAddRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    批量添加角色到小说
    
    Args:
        request: 批量添加请求
        db: 数据库会话
        current_user: 当前用户
        
    Returns:
        CharacterBatchAddResponse: 批量添加响应
    """
    try:
        # 验证小说是否属于当前用户
        novel = db.query(Novel).filter(
            and_(Novel.id == request.novel_id, Novel.user_id == current_user.id)
        ).first()
        if not novel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="小说不存在或无权访问"
            )
        
        added_characters = []
        failed_count = 0
        
        for character_id in request.character_ids:
            try:
                # 查找原角色
                original_character = db.query(Character).filter(
                    and_(Character.id == character_id, Character.user_id == current_user.id)
                ).first()
                
                if not original_character:
                    failed_count += 1
                    continue
                
                # 创建角色副本
                character_dict = original_character.to_dict()
                character_dict.pop('id')
                character_dict.pop('created_at')
                character_dict.pop('updated_at')
                character_dict['novel_id'] = request.novel_id
                character_dict['is_template'] = False
                
                new_character = Character(**character_dict)
                db.add(new_character)
                db.flush()  # 获取ID但不提交
                
                added_characters.append(CharacterResponse.model_validate(new_character))
                
            except Exception:
                failed_count += 1
                continue
        
        db.commit()
        
        return CharacterBatchAddResponse(
            success=True,
            message=f"成功添加 {len(added_characters)} 个角色，失败 {failed_count} 个",
            added_count=len(added_characters),
            failed_count=failed_count,
            added_characters=added_characters
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"批量添加角色失败: {str(e)}"
        )


@router.post("/generate", response_model=CharacterGenerationResponse)
async def generate_characters(
    request: CharacterGenerationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    AI生成角色
    
    Args:
        request: 角色生成请求
        db: 数据库会话
        current_user: 当前用户
        
    Returns:
        CharacterGenerationResponse: 角色生成响应
    """
    try:
        # 验证小说是否属于当前用户
        novel = db.query(Novel).filter(
            and_(Novel.id == request.novel_id, Novel.user_id == current_user.id)
        ).first()
        if not novel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="小说不存在或无权访问"
            )
        
        # 获取世界观信息（如果需要）
        worldview_info = ""
        if request.include_worldview and request.worldview_id:
            worldview = db.query(Worldview).filter(
                and_(Worldview.id == request.worldview_id, Worldview.user_id == current_user.id)
            ).first()
            if worldview:
                worldview_info = f"世界名称: {worldview.name}\n世界描述: {worldview.description or '无'}"
        
        # 准备小说信息
        novel_info = {
            "title": novel.title,
            "genre": novel.genre.value if novel.genre else "通用",
            "description": novel.description or ""
        }
        
        # 调用生成服务
        prompt_service = get_prompt_service(db)
        generation_service = get_generation_service(prompt_service)
        
        generation_result = await generation_service.generate_characters(
            request=request,
            novel_info=novel_info,
            worldview_info=worldview_info
        )
        
        if not generation_result.success:
            return generation_result
        
        # 将生成的数据转换为角色对象并保存到数据库
        created_characters = []
        for character_data in generation_result.generation_data or []:
            try:
                # 映射AI生成的字段到数据库模型
                character_type_mapping = {
                    "protagonist": CharacterType.PROTAGONIST,
                    "major_supporting": CharacterType.SUPPORTING,
                    "supporting": CharacterType.SUPPORTING,
                    "antagonist": CharacterType.ANTAGONIST,
                    "minor": CharacterType.MINOR
                }
                
                gender_mapping = {
                    "male": CharacterGender.MALE,
                    "female": CharacterGender.FEMALE,
                    "unknown": CharacterGender.UNKNOWN,
                    "other": CharacterGender.OTHER
                }
                
                character = Character(
                    name=character_data.get("name", "未命名角色"),
                    gender=gender_mapping.get(character_data.get("gender", "unknown"), CharacterGender.UNKNOWN),
                    personality=character_data.get("personality", ""),
                    character_type=character_type_mapping.get(character_data.get("character_type", "supporting"), CharacterType.SUPPORTING),
                    tags=character_data.get("tags", []),
                    description=character_data.get("description", ""),
                    abilities=character_data.get("abilities", ""),
                    novel_id=request.novel_id,
                    worldview_id=request.worldview_id,
                    user_id=current_user.id,
                    is_template=False
                )
                
                db.add(character)
                db.flush()  # 获取ID但不提交
                created_characters.append(CharacterResponse.model_validate(character))
                
            except Exception as e:
                logger.error(f"创建角色失败: {str(e)}")
                continue
        
        db.commit()
        
        return CharacterGenerationResponse(
            success=True,
            message=f"成功生成并保存 {len(created_characters)} 个角色",
            characters=created_characters,
            total_generated=len(created_characters),
            generation_data=generation_result.generation_data
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"角色生成失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"角色生成失败: {str(e)}"
        )