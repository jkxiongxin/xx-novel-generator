"""
章节管理API路由
Author: AI Writer Team
Created: 2025-06-01
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import desc, asc, and_, or_, func

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.novel import Novel
from app.models.chapter import Chapter, ChapterStatus
from app.models.character import Character
from app.models.outline import DetailedOutline
from app.models.worldview import Worldview
from app.schemas.chapter import (
    ChapterCreate, ChapterUpdate, ChapterResponse, ChapterSummaryResponse,
    ChapterListResponse, ChapterGenerationRequest, ChapterGenerationResponse,
    ChapterFilterRequest, ChapterBatchRequest, ChapterBatchResponse,
    ChapterStatsResponse
)
from app.services.generation_service import get_generation_service
from app.services.prompt_service import get_prompt_service

router = APIRouter()


@router.post("/", response_model=ChapterResponse, status_code=status.HTTP_201_CREATED)
async def create_chapter(
    chapter_create: ChapterCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建新章节
    
    Args:
        chapter_create: 章节创建数据
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        ChapterResponse: 创建的章节信息
        
    Raises:
        HTTPException: 创建失败时抛出异常
    """
    try:
        # 验证小说是否属于当前用户
        novel = db.query(Novel).filter(
            Novel.id == chapter_create.novel_id,
            Novel.user_id == current_user.id
        ).first()
        
        if not novel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="小说不存在或您没有权限访问"
            )
        
        # 检查章节序号是否已存在
        existing_chapter = db.query(Chapter).filter(
            Chapter.novel_id == chapter_create.novel_id,
            Chapter.chapter_number == chapter_create.chapter_number
        ).first()
        
        if existing_chapter:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"第{chapter_create.chapter_number}章已存在"
            )
        
        # 创建新章节
        db_chapter = Chapter(
            novel_id=chapter_create.novel_id,
            title=chapter_create.title,
            content=chapter_create.content or "",
            chapter_number=chapter_create.chapter_number,
            status=chapter_create.status,
            outline_id=chapter_create.outline_id,
            character_ids=chapter_create.character_ids or [],
            notes=chapter_create.notes,
            user_id=current_user.id
        )
        
        # 更新字数统计
        db_chapter.update_word_count()
        
        db.add(db_chapter)
        db.commit()
        db.refresh(db_chapter)
        
        return ChapterResponse.from_orm(db_chapter)
        
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="章节创建失败，请检查输入数据"
        )
    except Exception as e:
        db.rollback()
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="服务器内部错误"
        )


@router.get("/", response_model=ChapterListResponse)
async def get_chapters(
    novel_id: Optional[int] = Query(None, description="小说ID过滤"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页大小"),
    status: Optional[ChapterStatus] = Query(None, description="章节状态过滤"),
    chapter_number_start: Optional[int] = Query(None, description="章节序号范围开始"),
    chapter_number_end: Optional[int] = Query(None, description="章节序号范围结束"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    sort_by: str = Query("chapter_number", description="排序字段"),
    sort_order: str = Query("asc", description="排序方向"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取用户的章节列表
    
    Args:
        novel_id: 小说ID过滤
        page: 页码
        size: 每页大小
        status: 章节状态过滤
        chapter_number_start: 章节序号范围开始
        chapter_number_end: 章节序号范围结束
        keyword: 搜索关键词
        sort_by: 排序字段
        sort_order: 排序方向
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        ChapterListResponse: 章节列表响应
    """
    # 构建基础查询
    query = db.query(Chapter).filter(Chapter.user_id == current_user.id)
    
    # 添加小说过滤
    if novel_id:
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
        query = query.filter(Chapter.novel_id == novel_id)
    
    # 添加搜索条件
    if keyword:
        query = query.filter(
            or_(
                Chapter.title.contains(keyword),
                Chapter.content.contains(keyword),
                Chapter.notes.contains(keyword)
            )
        )
    
    if status:
        query = query.filter(Chapter.status == status)
    
    if chapter_number_start:
        query = query.filter(Chapter.chapter_number >= chapter_number_start)
    
    if chapter_number_end:
        query = query.filter(Chapter.chapter_number <= chapter_number_end)
    
    # 添加排序
    sort_column = getattr(Chapter, sort_by, Chapter.chapter_number)
    if sort_order.lower() == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(asc(sort_column))
    
    # 计算总数和总字数
    total = query.count()
    total_words = db.query(func.sum(Chapter.word_count)).filter(
        Chapter.user_id == current_user.id
    ).scalar() or 0
    
    # 应用分页
    offset = (page - 1) * size
    chapters = query.offset(offset).limit(size).all()
    
    # 转换为响应格式
    chapter_responses = []
    for chapter in chapters:
        character_count = len(chapter.character_id_list)
        chapter_responses.append(
            ChapterSummaryResponse(
                id=chapter.id,
                novel_id=chapter.novel_id,
                title=chapter.title,
                chapter_number=chapter.chapter_number,
                word_count=chapter.word_count,
                status=chapter.status,
                version=chapter.version,
                outline_id=chapter.outline_id,
                character_count=character_count,
                created_at=chapter.created_at,
                updated_at=chapter.updated_at
            )
        )
    
    # 计算分页信息
    total_pages = (total + size - 1) // size
    
    return ChapterListResponse(
        items=chapter_responses,
        total=total,
        page=page,
        page_size=size,
        total_pages=total_pages,
        total_words=total_words
    )


@router.get("/{chapter_id}", response_model=ChapterResponse)
async def get_chapter(
    chapter_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取指定章节详情
    
    Args:
        chapter_id: 章节ID
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        ChapterResponse: 章节详情
        
    Raises:
        HTTPException: 章节不存在或无权限时抛出异常
    """
    chapter = db.query(Chapter).filter(
        Chapter.id == chapter_id,
        Chapter.user_id == current_user.id
    ).first()
    
    if not chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="章节不存在或您没有权限访问"
        )
    
    return ChapterResponse.from_orm(chapter)


@router.put("/{chapter_id}", response_model=ChapterResponse)
async def update_chapter(
    chapter_id: int,
    chapter_update: ChapterUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新章节信息
    
    Args:
        chapter_id: 章节ID
        chapter_update: 章节更新数据
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        ChapterResponse: 更新后的章节信息
        
    Raises:
        HTTPException: 章节不存在、无权限或更新失败时抛出异常
    """
    chapter = db.query(Chapter).filter(
        Chapter.id == chapter_id,
        Chapter.user_id == current_user.id
    ).first()
    
    if not chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="章节不存在或您没有权限访问"
        )
    
    try:
        # 检查章节序号是否冲突（如果更新了序号）
        if chapter_update.chapter_number and chapter_update.chapter_number != chapter.chapter_number:
            existing_chapter = db.query(Chapter).filter(
                Chapter.novel_id == chapter.novel_id,
                Chapter.chapter_number == chapter_update.chapter_number,
                Chapter.id != chapter_id
            ).first()
            
            if existing_chapter:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"第{chapter_update.chapter_number}章已存在"
                )
        
        # 更新章节信息
        update_data = chapter_update.dict(exclude_unset=True)
        chapter.update_from_dict(update_data)
        
        # 如果内容有更新，增加版本号
        if "content" in update_data:
            chapter.increment_version()
        
        db.commit()
        db.refresh(chapter)
        
        return ChapterResponse.from_orm(chapter)
        
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="章节信息更新失败，请检查输入数据"
        )
    except Exception as e:
        db.rollback()
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="服务器内部错误"
        )


@router.delete("/{chapter_id}")
async def delete_chapter(
    chapter_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除章节
    
    Args:
        chapter_id: 章节ID
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        dict: 删除结果
        
    Raises:
        HTTPException: 章节不存在、无权限或删除失败时抛出异常
    """
    chapter = db.query(Chapter).filter(
        Chapter.id == chapter_id,
        Chapter.user_id == current_user.id
    ).first()
    
    if not chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="章节不存在或您没有权限访问"
        )
    
    try:
        db.delete(chapter)
        db.commit()
        
        return {"message": f"第{chapter.chapter_number}章删除成功"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="章节删除失败"
        )


@router.patch("/{chapter_id}/status", response_model=ChapterResponse)
async def update_chapter_status(
    chapter_id: int,
    new_status: ChapterStatus,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新章节状态
    
    Args:
        chapter_id: 章节ID
        new_status: 新状态
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        ChapterResponse: 更新后的章节信息
        
    Raises:
        HTTPException: 章节不存在、无权限或更新失败时抛出异常
    """
    chapter = db.query(Chapter).filter(
        Chapter.id == chapter_id,
        Chapter.user_id == current_user.id
    ).first()
    
    if not chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="章节不存在或您没有权限访问"
        )
    
    try:
        chapter.status = new_status
        db.commit()
        db.refresh(chapter)
        
        return ChapterResponse.from_orm(chapter)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="状态更新失败"
        )


@router.post("/generate", response_model=ChapterGenerationResponse)
async def generate_chapter(
    request: ChapterGenerationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    AI生成章节内容
    
    Args:
        request: 章节生成请求
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        ChapterGenerationResponse: 章节生成响应
        
    Raises:
        HTTPException: 生成失败时抛出异常
    """
    try:
        # 验证小说权限
        novel = db.query(Novel).filter(
            Novel.id == request.novel_id,
            Novel.user_id == current_user.id
        ).first()
        
        if not novel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="小说不存在或您没有权限访问"
            )
        
        # 检查章节是否已存在
        existing_chapter = db.query(Chapter).filter(
            Chapter.novel_id == request.novel_id,
            Chapter.chapter_number == request.chapter_number
        ).first()
        
        if existing_chapter:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"第{request.chapter_number}章已存在，请选择其他章节号"
            )
        
        # 收集生成上下文信息
        novel_info = {
            "title": novel.title,
            "description": novel.description,
            "genre": novel.genre,
            "tags": novel.tags
        }
        
        # 获取世界观信息
        worldview_info = ""
        if request.include_worldview:
            worldviews = db.query(Worldview).filter(
                Worldview.novel_id == request.novel_id
            ).all()
            if worldviews:
                worldview_info = "\n".join([
                    f"世界观设定: {wv.name}\n描述: {wv.description}"
                    for wv in worldviews
                ])
        
        # 获取角色信息
        character_info = ""
        if request.include_characters and request.character_ids:
            characters = db.query(Character).filter(
                Character.id.in_(request.character_ids),
                Character.user_id == current_user.id
            ).all()
            if characters:
                character_info = "\n".join([
                    f"角色: {char.name}\n性格: {char.personality}\n能力: {char.abilities}"
                    for char in characters
                ])
        
        # 获取大纲信息
        outline_info = ""
        if request.include_outline and request.outline_id:
            outline = db.query(DetailedOutline).filter(
                DetailedOutline.id == request.outline_id,
                DetailedOutline.user_id == current_user.id
            ).first()
            if outline:
                outline_info = f"章节大纲: {outline.chapter_title}\n情节点: {outline.plot_points}"
        
        # 获取前面章节内容作为上下文
        previous_chapters = ""
        if request.chapter_number > 1:
            prev_chapters = db.query(Chapter).filter(
                Chapter.novel_id == request.novel_id,
                Chapter.chapter_number < request.chapter_number,
                Chapter.status != ChapterStatus.DRAFT
            ).order_by(desc(Chapter.chapter_number)).limit(2).all()
            
            if prev_chapters:
                previous_chapters = "\n\n".join([
                    f"第{ch.chapter_number}章: {ch.title}\n{ch.get_content_preview(300)}"
                    for ch in reversed(prev_chapters)
                ])
        
        # 调用生成服务
        prompt_service = get_prompt_service(db)
        generation_service = get_generation_service(prompt_service)
        
        generation_result = await generation_service.generate_chapter(
            request=request,
            novel_info=novel_info,
            outline_info=outline_info,
            character_info=character_info,
            worldview_info=worldview_info,
            previous_chapters=previous_chapters
        )
        
        if not generation_result.success:
            return generation_result
        
        # 自动保存生成的章节
        generated_data = generation_result.generation_data or {}
        chapter_title = generated_data.get("title", f"第{request.chapter_number}章")
        
        new_chapter = Chapter(
            novel_id=request.novel_id,
            title=chapter_title,
            content=generation_result.generated_content,
            chapter_number=request.chapter_number,
            status=ChapterStatus.DRAFT,
            outline_id=request.outline_id,
            character_ids=request.character_ids,
            notes=f"AI生成于{generation_result.used_prompt_template}模板",
            user_id=current_user.id
        )
        
        new_chapter.update_word_count()
        
        db.add(new_chapter)
        db.commit()
        db.refresh(new_chapter)
        
        # 更新响应
        generation_result.chapter = ChapterResponse.from_orm(new_chapter)
        
        return generation_result
        
    except Exception as e:
        db.rollback()
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"章节生成失败: {str(e)}"
        )


@router.post("/batch", response_model=ChapterBatchResponse)
async def batch_operate_chapters(
    request: ChapterBatchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    批量操作章节
    
    Args:
        request: 批量操作请求
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        ChapterBatchResponse: 批量操作响应
        
    Raises:
        HTTPException: 操作失败时抛出异常
    """
    try:
        # 验证章节权限
        chapters = db.query(Chapter).filter(
            Chapter.id.in_(request.chapter_ids),
            Chapter.user_id == current_user.id
        ).all()
        
        if len(chapters) != len(request.chapter_ids):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="部分章节不存在或您没有权限访问"
            )
        
        processed_count = 0
        failed_count = 0
        failed_ids = []
        results = []
        
        for chapter in chapters:
            try:
                if request.operation == "update_status":
                    new_status = request.operation_data.get("status")
                    if new_status:
                        chapter.status = ChapterStatus(new_status)
                        results.append({
                            "chapter_id": chapter.id,
                            "operation": "update_status",
                            "success": True,
                            "message": f"状态更新为{new_status}"
                        })
                    
                elif request.operation == "delete":
                    db.delete(chapter)
                    results.append({
                        "chapter_id": chapter.id,
                        "operation": "delete",
                        "success": True,
                        "message": "删除成功"
                    })
                    
                elif request.operation == "update_outline":
                    outline_id = request.operation_data.get("outline_id")
                    chapter.outline_id = outline_id
                    results.append({
                        "chapter_id": chapter.id,
                        "operation": "update_outline",
                        "success": True,
                        "message": f"大纲ID更新为{outline_id}"
                    })
                    
                elif request.operation == "add_characters":
                    character_ids = request.operation_data.get("character_ids", [])
                    for char_id in character_ids:
                        chapter.add_character(char_id)
                    results.append({
                        "chapter_id": chapter.id,
                        "operation": "add_characters",
                        "success": True,
                        "message": f"添加{len(character_ids)}个角色"
                    })
                    
                elif request.operation == "remove_characters":
                    character_ids = request.operation_data.get("character_ids", [])
                    for char_id in character_ids:
                        chapter.remove_character(char_id)
                    results.append({
                        "chapter_id": chapter.id,
                        "operation": "remove_characters",
                        "success": True,
                        "message": f"移除{len(character_ids)}个角色"
                    })
                
                processed_count += 1
                
            except Exception as e:
                failed_count += 1
                failed_ids.append(chapter.id)
                results.append({
                    "chapter_id": chapter.id,
                    "operation": request.operation,
                    "success": False,
                    "message": str(e)
                })
        
        db.commit()
        
        return ChapterBatchResponse(
            success=failed_count == 0,
            message=f"批量操作完成，成功{processed_count}个，失败{failed_count}个",
            processed_count=processed_count,
            failed_count=failed_count,
            failed_ids=failed_ids,
            results=results
        )
        
    except Exception as e:
        db.rollback()
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"批量操作失败: {str(e)}"
        )


@router.get("/stats/{novel_id}", response_model=ChapterStatsResponse)
async def get_chapter_stats(
    novel_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取章节统计信息
    
    Args:
        novel_id: 小说ID
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        ChapterStatsResponse: 章节统计信息
        
    Raises:
        HTTPException: 小说不存在或无权限时抛出异常
    """
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
    
    # 获取所有章节
    chapters = db.query(Chapter).filter(
        Chapter.novel_id == novel_id
    ).all()
    
    # 计算统计信息
    total_chapters = len(chapters)
    draft_count = len([c for c in chapters if c.status == ChapterStatus.DRAFT])
    completed_count = len([c for c in chapters if c.status == ChapterStatus.COMPLETED])
    published_count = len([c for c in chapters if c.status == ChapterStatus.PUBLISHED])
    
    total_words = sum(c.word_count for c in chapters)
    average_words = total_words / total_chapters if total_chapters > 0 else 0
    
    # 获取最新章节
    latest_chapter = None
    if chapters:
        latest = max(chapters, key=lambda c: c.chapter_number)
        character_count = len(latest.character_id_list)
        latest_chapter = ChapterSummaryResponse(
            id=latest.id,
            novel_id=latest.novel_id,
            title=latest.title,
            chapter_number=latest.chapter_number,
            word_count=latest.word_count,
            status=latest.status,
            version=latest.version,
            outline_id=latest.outline_id,
            character_count=character_count,
            created_at=latest.created_at,
            updated_at=latest.updated_at
        )
    
    # 章节分布统计
    chapter_distribution = {
        "by_status": {
            "draft": draft_count,
            "completed": completed_count,
            "published": published_count
        },
        "by_word_count": {
            "0-1000": len([c for c in chapters if 0 <= c.word_count < 1000]),
            "1000-3000": len([c for c in chapters if 1000 <= c.word_count < 3000]),
            "3000-5000": len([c for c in chapters if 3000 <= c.word_count < 5000]),
            "5000+": len([c for c in chapters if c.word_count >= 5000])
        }
    }
    
    return ChapterStatsResponse(
        total_chapters=total_chapters,
        draft_count=draft_count,
        completed_count=completed_count,
        published_count=published_count,
        total_words=total_words,
        average_words=round(average_words, 1),
        latest_chapter=latest_chapter,
        chapter_distribution=chapter_distribution
    )