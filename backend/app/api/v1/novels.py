"""
小说管理API路由
Author: AI Writer Team
Created: 2025-06-01
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import desc, asc, and_, or_

from app.core.database import get_db
from app.core.dependencies import get_current_user, validate_pagination_params
from app.models.user import User
from app.models.novel import Novel
from app.schemas.novel import (
    NovelCreate, NovelUpdate, NovelResponse, NovelListResponse,
    NovelSearchParams, NovelStats, NovelStatus, NovelGenre
)

router = APIRouter()


@router.post("/", response_model=NovelResponse, status_code=status.HTTP_201_CREATED)
async def create_novel(
    novel_create: NovelCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建新小说
    
    Args:
        novel_create: 小说创建数据
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        NovelResponse: 创建的小说信息
        
    Raises:
        HTTPException: 创建失败时抛出异常
    """
    try:
        # 创建新小说
        db_novel = Novel(
            title=novel_create.title,
            description=novel_create.description,
            genre=novel_create.genre,
            tags=novel_create.tags or [],
            target_word_count=novel_create.target_word_count,
            status=NovelStatus.DRAFT,  # 默认状态为草稿
            word_count=0,  # 初始字数为0
            user_id=current_user.id
        )
        
        db.add(db_novel)
        db.commit()
        db.refresh(db_novel)
        
        return NovelResponse(
            id=db_novel.id,
            title=db_novel.title,
            description=db_novel.description,
            genre=db_novel.genre,
            tags=db_novel.tags,
            status=db_novel.status,
            target_word_count=db_novel.target_word_count,
            word_count=db_novel.word_count,
            user_id=db_novel.user_id,
            created_at=db_novel.created_at,
            updated_at=db_novel.updated_at
        )
        
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="小说创建失败，请检查输入数据"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="服务器内部错误"
        )


@router.get("/", response_model=NovelListResponse)
async def get_novels(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页大小"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    genre: Optional[NovelGenre] = Query(None, description="小说类型"),
    status: Optional[NovelStatus] = Query(None, description="小说状态"),
    sort_by: str = Query("updated_at", description="排序字段"),
    sort_order: str = Query("desc", description="排序方向"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取用户的小说列表
    
    Args:
        page: 页码
        size: 每页大小
        keyword: 搜索关键词
        genre: 小说类型
        status: 小说状态
        sort_by: 排序字段
        sort_order: 排序方向
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        NovelListResponse: 小说列表响应
    """
    # 构建查询
    query = db.query(Novel).filter(Novel.user_id == current_user.id)
    
    # 添加搜索条件
    if keyword:
        query = query.filter(
            or_(
                Novel.title.contains(keyword),
                Novel.description.contains(keyword)
            )
        )
    
    if genre:
        query = query.filter(Novel.genre == genre)
    
    if status:
        query = query.filter(Novel.status == status)
    
    # 添加排序
    sort_column = getattr(Novel, sort_by, Novel.updated_at)
    if sort_order.lower() == "asc":
        query = query.order_by(asc(sort_column))
    else:
        query = query.order_by(desc(sort_column))
    
    # 计算总数
    total = query.count()
    
    # 应用分页
    offset = (page - 1) * size
    novels = query.offset(offset).limit(size).all()
    
    # 转换为响应格式
    novel_responses = [
        NovelResponse(
            id=novel.id,
            title=novel.title,
            description=novel.description,
            genre=novel.genre,
            tags=novel.tags,
            status=novel.status,
            target_word_count=novel.target_word_count,
            word_count=novel.word_count,
            user_id=novel.user_id,
            created_at=novel.created_at,
            updated_at=novel.updated_at
        )
        for novel in novels
    ]
    
    # 计算分页信息
    total_pages = (total + size - 1) // size
    
    return NovelListResponse(
        novels=novel_responses,
        total=total,
        page=page,
        size=size,
        total_pages=total_pages
    )


@router.get("/{novel_id}", response_model=NovelResponse)
async def get_novel(
    novel_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取指定小说详情
    
    Args:
        novel_id: 小说ID
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        NovelResponse: 小说详情
        
    Raises:
        HTTPException: 小说不存在或无权限时抛出异常
    """
    novel = db.query(Novel).filter(
        Novel.id == novel_id,
        Novel.user_id == current_user.id
    ).first()
    
    if not novel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="小说不存在或您没有权限访问"
        )
    
    return NovelResponse(
        id=novel.id,
        title=novel.title,
        description=novel.description,
        genre=novel.genre,
        tags=novel.tags,
        status=novel.status,
        target_word_count=novel.target_word_count,
        word_count=novel.word_count,
        user_id=novel.user_id,
        created_at=novel.created_at,
        updated_at=novel.updated_at
    )


@router.put("/{novel_id}", response_model=NovelResponse)
async def update_novel(
    novel_id: int,
    novel_update: NovelUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新小说信息
    
    Args:
        novel_id: 小说ID
        novel_update: 小说更新数据
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        NovelResponse: 更新后的小说信息
        
    Raises:
        HTTPException: 小说不存在、无权限或更新失败时抛出异常
    """
    novel = db.query(Novel).filter(
        Novel.id == novel_id,
        Novel.user_id == current_user.id
    ).first()
    
    if not novel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="小说不存在或您没有权限访问"
        )
    
    try:
        # 更新小说信息
        update_data = novel_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(novel, field, value)
        
        db.commit()
        db.refresh(novel)
        
        return NovelResponse(
            id=novel.id,
            title=novel.title,
            description=novel.description,
            genre=novel.genre,
            tags=novel.tags,
            status=novel.status,
            target_word_count=novel.target_word_count,
            word_count=novel.word_count,
            user_id=novel.user_id,
            created_at=novel.created_at,
            updated_at=novel.updated_at
        )
        
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="小说信息更新失败，请检查输入数据"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="服务器内部错误"
        )


@router.delete("/{novel_id}")
async def delete_novel(
    novel_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除小说
    
    Args:
        novel_id: 小说ID
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        dict: 删除结果
        
    Raises:
        HTTPException: 小说不存在、无权限或删除失败时抛出异常
    """
    novel = db.query(Novel).filter(
        Novel.id == novel_id,
        Novel.user_id == current_user.id
    ).first()
    
    if not novel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="小说不存在或您没有权限访问"
        )
    
    try:
        db.delete(novel)
        db.commit()
        
        return {"message": "小说删除成功"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="小说删除失败"
        )


@router.get("/stats/overview", response_model=NovelStats)
async def get_novel_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取用户的小说统计信息
    
    Args:
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        NovelStats: 小说统计信息
    """
    # 获取用户的所有小说
    novels = db.query(Novel).filter(Novel.user_id == current_user.id).all()
    
    # 计算统计信息
    total_novels = len(novels)
    total_word_count = sum(novel.word_count for novel in novels)
    average_word_count = total_word_count / total_novels if total_novels > 0 else 0
    
    # 按状态统计
    novels_by_status = {}
    for status in NovelStatus:
        novels_by_status[status.value] = len([n for n in novels if n.status == status])
    
    # 按类型统计
    novels_by_genre = {}
    for genre in NovelGenre:
        novels_by_genre[genre.value] = len([n for n in novels if n.genre == genre])
    
    return NovelStats(
        total_novels=total_novels,
        total_word_count=total_word_count,
        novels_by_status=novels_by_status,
        novels_by_genre=novels_by_genre,
        average_word_count=average_word_count
    )


@router.patch("/{novel_id}/status", response_model=NovelResponse)
async def update_novel_status(
    novel_id: int,
    new_status: NovelStatus,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新小说状态
    
    Args:
        novel_id: 小说ID
        new_status: 新状态
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        NovelResponse: 更新后的小说信息
        
    Raises:
        HTTPException: 小说不存在、无权限或更新失败时抛出异常
    """
    novel = db.query(Novel).filter(
        Novel.id == novel_id,
        Novel.user_id == current_user.id
    ).first()
    
    if not novel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="小说不存在或您没有权限访问"
        )
    
    try:
        novel.status = new_status
        db.commit()
        db.refresh(novel)
        
        return NovelResponse(
            id=novel.id,
            title=novel.title,
            description=novel.description,
            genre=novel.genre,
            tags=novel.tags,
            status=novel.status,
            target_word_count=novel.target_word_count,
            word_count=novel.word_count,
            user_id=novel.user_id,
            created_at=novel.created_at,
            updated_at=novel.updated_at
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="状态更新失败"
        )