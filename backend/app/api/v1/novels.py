"""
小说管理API路由
Author: AI Writer Team
Created: 2025-06-01
"""

import logging
import json
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
    NovelSearchParams, NovelStats, NovelStatus, NovelGenre,
    NovelDetailResponse, NovelDetailStats, NovelContentOverview,
    NovelStatsDetailResponse, Activity, RecentActivitiesResponse
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED)
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
        # 添加调试日志
        logger.info(f"创建小说数据: title={novel_create.title}, target_word_count={novel_create.target_word_count}")
        logger.info(f"Novel模型字段: {[attr for attr in dir(Novel) if not attr.startswith('_')]}")
        
        # 创建新小说 - 修正字段名匹配
        db_novel = Novel(
            title=novel_create.title,
            description=novel_create.description,
            genre=novel_create.genre,
            author=current_user.username or "未知作者",  # 添加必需的author字段
            tags=json.dumps(novel_create.tags or [], ensure_ascii=False),  # 修正：将列表转换为JSON字符串
            target_words=novel_create.target_word_count,  # 修正：target_word_count -> target_words
            status=NovelStatus.DRAFT,  # 默认状态为草稿
            current_words=0,  # 修正：word_count -> current_words
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
            "tags": json.loads(db_novel.tags) if db_novel.tags else [],  # 修正：将JSON字符串转换为列表
            "status": db_novel.status,
            "target_word_count": db_novel.target_words,  # 修正：使用正确的Model字段
            "word_count": db_novel.current_words,  # 修正：使用正确的Model字段
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
        
    except IntegrityError as e:
        db.rollback()
        logger.error(f"小说创建数据完整性错误: 用户{current_user.id}, 错误详情: {str(e)}")
        logger.error(f"创建数据: title={novel_create.title}, genre={novel_create.genre}, user_id={current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"小说创建失败，数据完整性错误: {str(e)}"
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
            author=current_user.username or "未知作者",  # 添加必需的author字段
            tags=json.dumps(novel_create.tags or [], ensure_ascii=False),  # 修正：将列表转换为JSON字符串
            target_words=novel_create.target_word_count,  # 修正：target_word_count -> target_words
            status=NovelStatus.DRAFT,  # 默认状态为草稿
            current_words=0,  # 修正：word_count -> current_words
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
            tags=json.loads(db_novel.tags) if db_novel.tags else [],  # 修正：将JSON字符串转换为列表
            status=db_novel.status,
            target_word_count=db_novel.target_words,  # 修正：使用正确的Model字段
            word_count=db_novel.current_words,  # 修正：使用正确的Model字段
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


@router.get("")
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
            if novel.target_words and novel.target_words > 0:
                progress_percentage = min(100, (novel.current_words / novel.target_words) * 100)
            else:
                progress_percentage = 0
            
            novel_data = {
                "id": novel.id,
                "title": novel.title,
                "description": novel.description,
                "genre": novel.genre,
                "status": novel.status,
                "cover_image": None,  # 可以后续添加封面功能
                "word_count": novel.current_words,  # 修正：使用正确的Model字段
                "chapter_count": chapter_count,
                "target_words": novel.target_words,  # 修正：使用正确的Model字段
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
                "word_count": novel.current_words,  # 修正：使用正确的Model字段
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


@router.get("/{novel_id}", response_model=NovelDetailResponse)
async def get_novel(
    novel_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取指定小说详情 - 扩展版本，包含统计信息和内容概览
    
    Args:
        novel_id: 小说ID
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        NovelDetailResponse: 扩展的小说详情
        
    Raises:
        HTTPException: 小说不存在或无权限时抛出异常
    """
    try:
        novel = db.query(Novel).filter(
            Novel.id == novel_id,
            Novel.user_id == current_user.id
        ).first()
        
        if not novel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="小说不存在或您没有权限访问"
            )
        
        # 获取最新章节信息
        from app.models.chapter import Chapter
        latest_chapter = db.query(Chapter)\
            .filter(Chapter.novel_id == novel.id)\
            .order_by(desc(Chapter.updated_at))\
            .first()
        
        # 计算统计信息
        stats = calculate_novel_stats(novel, db)
        
        # 计算内容概览
        content_overview = calculate_content_overview(novel, db)
        
        # 解析标签
        import json
        tags = []
        if novel.tags:
            try:
                tags = json.loads(novel.tags) if isinstance(novel.tags, str) else novel.tags
            except:
                tags = []
        
        return NovelDetailResponse(
            id=novel.id,
            title=novel.title,
            description=novel.description,
            genre=novel.genre,
            author=novel.author,
            tags=tags,
            status=novel.status,
            target_word_count=novel.target_words,
            word_count=novel.current_words,
            user_id=novel.user_id,
            created_at=novel.created_at,
            updated_at=novel.updated_at,
            cover_image=novel.cover_url,
            target_audience=novel.target_audience.value if novel.target_audience else None,
            writing_style=novel.writing_style.value if novel.writing_style else None,
            progress_percentage=round(novel.progress_percentage, 1),
            last_edit_date=latest_chapter.updated_at.isoformat() if latest_chapter else novel.updated_at.isoformat(),
            last_chapter_id=latest_chapter.id if latest_chapter else None,
            last_chapter_title=latest_chapter.title if latest_chapter else None,
            stats=stats,
            content_overview=content_overview
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取小说详情失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取小说详情失败"
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
            target_word_count=novel.target_words,  # 修正：使用正确的Model字段
            word_count=novel.current_words,  # 修正：使用正确的Model字段
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
        total_words = sum(novel.current_words for novel in novels if novel.current_words)  # 修正：使用正确的Model字段
        
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
    total_word_count = sum(novel.current_words for novel in novels)  # 修正：使用正确的Model字段
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


def calculate_novel_stats(novel: Novel, db: Session) -> NovelDetailStats:
    """
    计算小说的详细统计信息
    
    Args:
        novel: 小说对象
        db: 数据库会话
        
    Returns:
        NovelDetailStats: 详细统计信息
    """
    from app.models.chapter import Chapter
    from datetime import datetime, timedelta
    
    # 获取章节统计
    chapters = db.query(Chapter).filter(Chapter.novel_id == novel.id).all()
    total_chapters = len(chapters)
    completed_chapters = len([c for c in chapters if c.status == "completed"])
    draft_chapters = len([c for c in chapters if c.status == "draft"])
    
    # 计算字数统计
    total_words = sum(c.word_count for c in chapters if c.word_count)
    average_words_per_chapter = total_words / total_chapters if total_chapters > 0 else 0
    
    # 计算写作天数（从创建到现在）
    writing_days = (datetime.now() - novel.created_at).days + 1
    average_daily_words = total_words / writing_days if writing_days > 0 else 0
    
    # 估算完成时间
    estimated_completion_time = None
    if novel.target_words and novel.target_words > total_words and average_daily_words > 0:
        remaining_words = novel.target_words - total_words
        remaining_days = remaining_words / average_daily_words
        estimated_date = datetime.now() + timedelta(days=remaining_days)
        estimated_completion_time = estimated_date.strftime("%Y-%m-%d")
    
    return NovelDetailStats(
        total_chapters=total_chapters,
        completed_chapters=completed_chapters,
        draft_chapters=draft_chapters,
        total_words=total_words,
        average_words_per_chapter=round(average_words_per_chapter, 1),
        estimated_completion_time=estimated_completion_time,
        writing_days=writing_days,
        average_daily_words=round(average_daily_words, 1)
    )


def calculate_content_overview(novel: Novel, db: Session) -> NovelContentOverview:
    """
    计算小说的内容概览信息
    
    Args:
        novel: 小说对象
        db: 数据库会话
        
    Returns:
        NovelContentOverview: 内容概览信息
    """
    from app.models.worldview import Worldview
    from app.models.character import Character
    from app.models.outline import RoughOutline, DetailedOutline
    from app.models.chapter import Chapter
    
    # 世界观统计
    worldview_count = db.query(Worldview).filter(Worldview.novel_id == novel.id).count()
    has_worldview = worldview_count > 0
    
    # 角色统计
    character_count = db.query(Character).filter(Character.novel_id == novel.id).count()
    
    # 大纲统计
    rough_outline_count = db.query(RoughOutline).filter(RoughOutline.novel_id == novel.id).count()
    detailed_outline_count = db.query(DetailedOutline).filter(DetailedOutline.novel_id == novel.id).count()
    
    # 最近活动时间
    latest_chapter = db.query(Chapter)\
        .filter(Chapter.novel_id == novel.id)\
        .order_by(desc(Chapter.updated_at))\
        .first()
    
    last_activity_date = None
    if latest_chapter:
        last_activity_date = latest_chapter.updated_at.isoformat()
    elif novel.updated_at:
        last_activity_date = novel.updated_at.isoformat()
    
    return NovelContentOverview(
        has_worldview=has_worldview,
        worldview_count=worldview_count,
        character_count=character_count,
        rough_outline_count=rough_outline_count,
        detailed_outline_count=detailed_outline_count,
        last_activity_date=last_activity_date
    )


@router.get("/{novel_id}/stats", response_model=NovelStatsDetailResponse)
async def get_novel_stats(
    novel_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
    ):
    """
    获取小说详细统计数据

    Args:
        novel_id: 小说ID
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        NovelStatsDetailResponse: 详细统计数据
        
    Raises:
        HTTPException: 小说不存在或无权限时抛出异常
    """
    try:
        novel = db.query(Novel).filter(
            Novel.id == novel_id,
            Novel.user_id == current_user.id
        ).first()
        
        if not novel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="小说不存在或您没有权限访问"
            )
        
        from app.models.chapter import Chapter
        from app.models.character import Character
        from app.models.worldview import Worldview
        from app.models.outline import RoughOutline, DetailedOutline
        from datetime import datetime, timedelta
        
        # 获取章节数据
        chapters = db.query(Chapter).filter(Chapter.novel_id == novel.id).all()
        total_chapters = len(chapters)
        completed_chapters = len([c for c in chapters if c.status == "completed"])
        total_words = sum(c.word_count for c in chapters if c.word_count)
        average_chapter_length = total_words / total_chapters if total_chapters > 0 else 0
        
        # 基础统计
        basic_stats = {
            "total_words": total_words,
            "total_chapters": total_chapters,
            "completed_chapters": completed_chapters,
            "average_chapter_length": round(average_chapter_length, 1)
        }
        
        # 进度统计
        completion_percentage = novel.progress_percentage
        target_words = novel.target_words or 0
        remaining_words = max(0, target_words - total_words)
        
        # 计算写作统计
        writing_days = (datetime.now() - novel.created_at).days + 1
        average_daily_words = total_words / writing_days if writing_days > 0 else 0
        
        # 估算完成时间
        estimated_days_to_completion = 0
        if remaining_words > 0 and average_daily_words > 0:
            estimated_days_to_completion = int(remaining_words / average_daily_words)
        
        daily_target_words = 0
        if estimated_days_to_completion > 0:
            daily_target_words = int(remaining_words / estimated_days_to_completion)
        
        progress_stats = {
            "completion_percentage": round(completion_percentage, 1),
            "estimated_days_to_completion": estimated_days_to_completion,
            "target_words": target_words,
            "daily_target_words": daily_target_words
        }
        
        # 写作统计
        # 找到最高产的一天（模拟数据）
        most_productive_day = "Monday"  # 可以后续实现真实的统计
        writing_streak = min(writing_days, 7)  # 模拟连续写作天数
        
        writing_stats = {
            "writing_days": writing_days,
            "total_writing_hours": None,  # 可以后续添加
            "average_daily_words": round(average_daily_words, 1),
            "most_productive_day": most_productive_day,
            "writing_streak": writing_streak
        }
        
        # 内容统计
        character_count = db.query(Character).filter(Character.novel_id == novel.id).count()
        worldview_count = db.query(Worldview).filter(Worldview.novel_id == novel.id).count()
        rough_outline_count = db.query(RoughOutline).filter(RoughOutline.novel_id == novel.id).count()
        detailed_outline_count = db.query(DetailedOutline).filter(DetailedOutline.novel_id == novel.id).count()
        
        # 大纲完成度
        outline_completion = 0
        if detailed_outline_count > 0:
            outline_completion = min(100, (completed_chapters / detailed_outline_count) * 100)
        
        content_stats = {
            "character_count": character_count,
            "worldview_count": worldview_count,
            "outline_completion": round(outline_completion, 1),
            "plot_point_count": rough_outline_count + detailed_outline_count
        }
        
        # 质量统计（模拟数据，可以后续实现真实的AI评分）
        quality_stats = {
            "ai_review_score": None,
            "consistency_score": None,
            "readability_score": None
        }
        
        return NovelStatsDetailResponse(
            basic_stats=basic_stats,
            progress_stats=progress_stats,
            writing_stats=writing_stats,
            content_stats=content_stats,
            quality_stats=quality_stats
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取小说统计数据失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取统计数据失败"
        )


@router.get("/{novel_id}/activities", response_model=RecentActivitiesResponse)
async def get_recent_activities(
    novel_id: int,
    limit: int = Query(10, ge=1, le=50, description="返回数量限制"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
    ):
    """
    获取小说最近活动记录

    Args:
        novel_id: 小说ID
        limit: 返回数量限制
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        RecentActivitiesResponse: 最近活动记录
        
    Raises:
        HTTPException: 小说不存在或无权限时抛出异常
    """
    try:
        novel = db.query(Novel).filter(
            Novel.id == novel_id,
            Novel.user_id == current_user.id
        ).first()
        
        if not novel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="小说不存在或您没有权限访问"
            )
        
        # 生成活动记录
        activities = generate_recent_activities(novel, db, limit)
        
        return RecentActivitiesResponse(
            activities=activities,
            total=len(activities)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取活动记录失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取活动记录失败"
        )


def generate_recent_activities(novel: Novel, db: Session, limit: int = 10) -> List[Activity]:
    """
    生成最近活动记录
    
    Args:
        novel: 小说对象
        db: 数据库会话
        limit: 返回数量限制
        
    Returns:
        List[Activity]: 活动记录列表
    """
    from app.models.chapter import Chapter
    from app.models.character import Character
    from app.models.worldview import Worldview
    import uuid
    
    activities = []
    
    # 章节活动
    recent_chapters = db.query(Chapter)\
        .filter(Chapter.novel_id == novel.id)\
        .order_by(desc(Chapter.updated_at))\
        .limit(5)\
        .all()
    
    for chapter in recent_chapters:
        activities.append(Activity(
            id=str(uuid.uuid4()),
            type="chapter_updated",
            title=f"更新章节：{chapter.title}",
            description=f"字数：{chapter.word_count}字",
            timestamp=chapter.updated_at.isoformat(),
            metadata={
                "chapter_id": chapter.id,
                "words_added": chapter.word_count
            }
        ))
    
    # 角色活动
    recent_characters = db.query(Character)\
        .filter(Character.novel_id == novel.id)\
        .order_by(desc(Character.updated_at))\
        .limit(3)\
        .all()
    
    for character in recent_characters:
        activities.append(Activity(
            id=str(uuid.uuid4()),
            type="character_added",
            title=f"添加角色：{character.name}",
            description=f"类型：{character.character_type}",
            timestamp=character.updated_at.isoformat(),
            metadata={
                "character_id": character.id
            }
        ))
    
    # 世界观活动
    recent_worldviews = db.query(Worldview)\
        .filter(Worldview.novel_id == novel.id)\
        .order_by(desc(Worldview.updated_at))\
        .limit(2)\
        .all()
    
    for worldview in recent_worldviews:
        activities.append(Activity(
            id=str(uuid.uuid4()),
            type="worldview_updated",
            title=f"更新世界观：{worldview.name}",
            description=worldview.description or "世界观设定",
            timestamp=worldview.updated_at.isoformat(),
            metadata={
                "worldview_id": worldview.id
            }
        ))
    
    # 按时间排序并限制数量
    activities.sort(key=lambda x: x.timestamp, reverse=True)
    return activities[:limit]
    
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
            target_word_count=novel.target_words,  # 修正：使用正确的Model字段
            word_count=novel.current_words,  # 修正：使用正确的Model字段
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