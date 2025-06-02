"""
小说管理API路由
Author: AI Writer Team
Created: 2025-06-01
"""

import logging
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

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_novel(
    novel_create: NovelCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    快速创建小说 - 首页专用
    
    Args:
        novel_create: 小说创建数据
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        dict: 创建结果，包含小说信息和工作台链接
        
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
        
        # 构建响应数据
        novel_data = {
            "id": db_novel.id,
            "title": db_novel.title,
            "description": db_novel.description,
            "genre": db_novel.genre,
            "tags": db_novel.tags,
            "status": db_novel.status,
            "target_word_count": db_novel.target_word_count,
            "word_count": db_novel.word_count,
            "user_id": db_novel.user_id,
            "created_at": db_novel.created_at.isoformat(),
            "updated_at": db_novel.updated_at.isoformat()
        }
        
        # 生成工作台链接
        redirect_url = f"/workspace/{db_novel.id}/chapters"
        
        return {
            "status": "success",
            "data": {
                "novel": novel_data,
                "redirect_url": redirect_url
            },
            "message": "小说创建成功"
        }
        
    except IntegrityError:
        db.rollback()
        logger.error(f"小说创建数据完整性错误: 用户{current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="小说创建失败，请检查输入数据"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"小说创建异常: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="服务器内部错误"
        )


@router.post("/detailed", response_model=NovelResponse, status_code=status.HTTP_201_CREATED)
async def create_novel_detailed(
    novel_create: NovelCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建新小说 - 详细版本，返回完整模型
    
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


@router.get("/")
async def get_novels(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页大小"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    status: Optional[str] = Query(None, description="状态筛选"),
    genre: Optional[str] = Query(None, description="类型筛选"),
    sort_by: str = Query("updated_at", description="排序字段"),
    sort_order: str = Query("desc", description="排序方向"),
    date_from: Optional[str] = Query(None, description="创建时间起始"),
    date_to: Optional[str] = Query(None, description="创建时间结束"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取小说列表 - 支持设计文档中的所有筛选和排序参数
    
    Args:
        page: 页码
        page_size: 每页数量
        search: 搜索关键词
        status: 状态筛选
        genre: 类型筛选
        sort_by: 排序字段
        sort_order: 排序方向
        date_from: 创建时间起始
        date_to: 创建时间结束
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        dict: 小说列表响应
    """
    try:
        # 构建查询
        query = db.query(Novel).filter(Novel.user_id == current_user.id)
        
        # 添加搜索条件
        if search:
            query = query.filter(
                or_(
                    Novel.title.contains(search),
                    Novel.description.contains(search)
                )
            )
        
        if status:
            query = query.filter(Novel.status == status)
        
        if genre:
            query = query.filter(Novel.genre == genre)
        
        # 时间范围筛选
        if date_from:
            query = query.filter(Novel.created_at >= date_from)
        if date_to:
            query = query.filter(Novel.created_at <= date_to)
        
        # 添加排序
        sort_column = getattr(Novel, sort_by, Novel.updated_at)
        if sort_order.lower() == "asc":
            query = query.order_by(asc(sort_column))
        else:
            query = query.order_by(desc(sort_column))
        
        # 计算总数
        total = query.count()
        
        # 应用分页
        offset = (page - 1) * page_size
        novels = query.offset(offset).limit(page_size).all()
        
        # 获取章节统计
        from app.models.chapter import Chapter
        novels_data = []
        for novel in novels:
            chapter_count = db.query(Chapter).filter(Chapter.novel_id == novel.id).count()
            
            # 获取最新章节信息
            latest_chapter = db.query(Chapter)\
                .filter(Chapter.novel_id == novel.id)\
                .order_by(desc(Chapter.updated_at))\
                .first()
            
            # 计算进度百分比
            if novel.target_word_count and novel.target_word_count > 0:
                progress_percentage = min(100, (novel.word_count / novel.target_word_count) * 100)
            else:
                progress_percentage = 0
            
            novel_data = {
                "id": novel.id,
                "title": novel.title,
                "description": novel.description,
                "genre": novel.genre,
                "status": novel.status,
                "cover_image": None,  # 可以后续添加封面功能
                "word_count": novel.word_count,
                "chapter_count": chapter_count,
                "target_words": novel.target_word_count,
                "progress_percentage": round(progress_percentage, 1),
                "created_at": novel.created_at.isoformat(),
                "updated_at": novel.updated_at.isoformat(),
                "last_chapter_title": latest_chapter.title if latest_chapter else None,
                "last_edit_date": latest_chapter.updated_at.isoformat() if latest_chapter else novel.updated_at.isoformat()
            }
            novels_data.append(novel_data)
        
        # 计算分页信息
        total_pages = (total + page_size - 1) // page_size
        
        return {
            "status": "success",
            "data": {
                "novels": novels_data,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages
            },
            "message": "小说列表获取成功"
        }
        
    except Exception as e:
        logger.error(f"获取小说列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取小说列表失败"
        )


@router.get("/recent", description="获取最近编辑的小说 - 首页专用")
async def get_recent_novels(
    limit: int = Query(6, ge=1, le=20, description="返回数量限制"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取最近编辑的小说 - 专为首页设计
    
    Args:
        limit: 返回数量限制，默认6个
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        dict: 包含最近小说列表的响应
    """
    try:
        # 导入章节模型以获取最新章节信息
        from app.models.chapter import Chapter
        
        # 获取用户最近编辑的小说
        recent_novels = db.query(Novel)\
            .filter(Novel.user_id == current_user.id)\
            .order_by(desc(Novel.updated_at))\
            .limit(limit)\
            .all()
        
        # 构建响应数据
        novels_data = []
        for novel in recent_novels:
            # 获取最新章节标题
            latest_chapter = db.query(Chapter)\
                .filter(Chapter.novel_id == novel.id)\
                .order_by(desc(Chapter.updated_at))\
                .first()
            
            novel_data = {
                "id": novel.id,
                "title": novel.title,
                "description": novel.description,
                "genre": novel.genre,
                "status": novel.status,
                "cover_image": None,  # 可以后续添加封面功能
                "word_count": novel.word_count,
                "chapter_count": db.query(Chapter).filter(Chapter.novel_id == novel.id).count(),
                "created_at": novel.created_at.isoformat(),
                "updated_at": novel.updated_at.isoformat(),
                "last_chapter_title": latest_chapter.title if latest_chapter else None
            }
            novels_data.append(novel_data)
        
        return {
            "status": "success",
            "data": {
                "novels": novels_data,
                "total": len(novels_data)
            },
            "message": "最近小说获取成功"
        }
        
    except Exception as e:
        logger.error(f"获取最近小说失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取最近小说失败"
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
        novel_title = novel.title
        db.delete(novel)
        db.commit()
        
        return {
            "status": "success",
            "data": {
                "deleted_novel_id": novel_id
            },
            "message": f"小说《{novel_title}》删除成功"
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"删除小说失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="小说删除失败"
        )


@router.post("/batch/delete")
async def batch_delete_novels(
    novel_ids: List[int],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    批量删除小说
    
    Args:
        novel_ids: 要删除的小说ID列表
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        dict: 批量删除结果
    """
    try:
        # 查找用户拥有的小说
        novels = db.query(Novel).filter(
            Novel.id.in_(novel_ids),
            Novel.user_id == current_user.id
        ).all()
        
        success_count = 0
        failed_count = 0
        failed_items = []
        
        for novel in novels:
            try:
                db.delete(novel)
                success_count += 1
            except Exception as e:
                failed_count += 1
                failed_items.append({
                    "novel_id": novel.id,
                    "reason": str(e)
                })
        
        db.commit()
        
        return {
            "status": "success",
            "data": {
                "success_count": success_count,
                "failed_count": failed_count,
                "failed_items": failed_items
            },
            "message": f"批量删除完成，成功 {success_count} 个，失败 {failed_count} 个"
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"批量删除小说失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="批量删除失败"
        )


@router.post("/batch/status")
async def batch_update_status(
    novel_ids: List[int],
    new_status: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    批量修改小说状态
    
    Args:
        novel_ids: 要修改的小说ID列表
        new_status: 新状态
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        dict: 批量修改结果
    """
    try:
        # 查找用户拥有的小说
        novels = db.query(Novel).filter(
            Novel.id.in_(novel_ids),
            Novel.user_id == current_user.id
        ).all()
        
        success_count = 0
        failed_count = 0
        updated_novels = []
        
        for novel in novels:
            try:
                novel.status = new_status
                success_count += 1
                updated_novels.append({
                    "id": novel.id,
                    "title": novel.title,
                    "status": novel.status
                })
            except Exception as e:
                failed_count += 1
        
        db.commit()
        
        return {
            "status": "success",
            "data": {
                "success_count": success_count,
                "failed_count": failed_count,
                "updated_novels": updated_novels
            },
            "message": f"批量状态修改完成，成功 {success_count} 个，失败 {failed_count} 个"
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"批量修改状态失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="批量状态修改失败"
        )


@router.post("/{novel_id}/export")
async def export_novel(
    novel_id: int,
    export_format: str = Query(..., description="导出格式：txt, docx, pdf"),
    include_outline: bool = Query(False, description="是否包含大纲"),
    include_worldview: bool = Query(False, description="是否包含世界观"),
    include_characters: bool = Query(False, description="是否包含角色信息"),
    only_completed: bool = Query(False, description="仅包含已完成章节"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    生成小说导出链接
    
    Args:
        novel_id: 小说ID
        export_format: 导出格式
        include_outline: 是否包含大纲
        include_worldview: 是否包含世界观
        include_characters: 是否包含角色信息
        only_completed: 仅包含已完成章节
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        dict: 导出信息
    """
    try:
        # 验证小说权限
        novel = db.query(Novel).filter(
            Novel.id == novel_id,
            Novel.user_id == current_user.id
        ).first()
        
        if not novel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="小说不存在或您没有权限访问"
            )
        
        # 生成导出ID（实际项目中应该是真实的导出任务）
        import uuid
        export_id = str(uuid.uuid4())
        
        # 模拟导出处理
        download_url = f"/api/v1/novels/download/{export_id}"
        
        return {
            "status": "success",
            "data": {
                "export_id": export_id,
                "download_url": download_url,
                "expires_at": "2025-06-02T21:32:00Z",
                "file_size": 102400,  # 模拟文件大小
                "estimated_time": 5   # 预计生成时间(秒)
            },
            "message": "导出任务已创建"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建导出任务失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建导出任务失败"
        )


@router.get("/export/{export_id}/status")
async def get_export_status(export_id: str):
    """
    获取导出状态
    
    Args:
        export_id: 导出任务ID
        
    Returns:
        dict: 导出状态信息
    """
    # 模拟导出状态查询
    return {
        "status": "success",
        "data": {
            "export_id": export_id,
            "status": "completed",
            "progress_percentage": 100,
            "download_url": f"/api/v1/novels/download/{export_id}",
            "file_info": {
                "filename": f"novel_{export_id}.txt",
                "size": 102400,
                "format": "txt"
            }
        },
        "message": "导出已完成"
    }


@router.get("/stats/overview")
async def get_novel_stats_overview(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取用户统计数据概览 - 专为首页设计
    
    Args:
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        dict: 首页所需的统计数据
    """
    try:
        # 导入章节模型
        from app.models.chapter import Chapter
        
        # 获取用户的所有小说
        novels = db.query(Novel).filter(Novel.user_id == current_user.id).all()
        
        # 计算基础统计
        total_novels = len(novels)
        total_words = sum(novel.word_count for novel in novels if novel.word_count)
        
        # 计算章节统计
        if total_novels > 0:
            novel_ids = [novel.id for novel in novels]
            total_chapters = db.query(Chapter).filter(Chapter.novel_id.in_(novel_ids)).count()
        else:
            total_chapters = 0
        
        # 按状态统计
        active_novels = len([n for n in novels if n.status in [NovelStatus.WRITING, NovelStatus.DRAFT]])
        completed_novels = len([n for n in novels if n.status == NovelStatus.COMPLETED])
        
        # 获取最近活动信息
        recent_activity = {}
        if novels:
            # 获取最近更新的小说
            latest_novel = max(novels, key=lambda x: x.updated_at)
            recent_activity = {
                "last_edit_date": latest_novel.updated_at.isoformat(),
                "daily_words": 0  # 可以后续实现每日字数统计
            }
        else:
            recent_activity = {
                "last_edit_date": None,
                "daily_words": 0
            }
        
        return {
            "status": "success",
            "data": {
                "total_novels": total_novels,
                "total_chapters": total_chapters,
                "total_words": total_words,
                "active_novels": active_novels,
                "completed_novels": completed_novels,
                "recent_activity": recent_activity
            },
            "message": "统计数据获取成功"
        }
        
    except Exception as e:
        logger.error(f"获取用户统计数据失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取统计数据失败"
        )


@router.get("/stats/detailed", response_model=NovelStats)
async def get_detailed_novel_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取用户的详细小说统计信息
    
    Args:
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        NovelStats: 详细小说统计信息
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