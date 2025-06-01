"""
大纲管理API
Author: AI Assistant
Created: 2025-06-01
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.novel import Novel
from app.models.outline import RoughOutline, DetailedOutline, OutlineType
from app.schemas.outline import (
    RoughOutlineCreate, RoughOutlineUpdate, RoughOutlineResponse,
    DetailedOutlineCreate, DetailedOutlineUpdate, DetailedOutlineResponse,
    RoughOutlineListResponse, DetailedOutlineListResponse,
    RoughOutlineGenerationRequest, DetailedOutlineGenerationRequest,
    OutlineGenerationResponse, OutlineFilterRequest,
    OutlineSummaryRequest, OutlineSummaryResponse
)

router = APIRouter(prefix="/outline", tags=["大纲管理"])


# ============ 粗略大纲 API ============

@router.post("/rough", response_model=RoughOutlineResponse, status_code=status.HTTP_201_CREATED)
async def create_rough_outline(
    outline_data: RoughOutlineCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建粗略大纲
    
    Args:
        outline_data: 粗略大纲创建数据
        db: 数据库会话
        current_user: 当前用户
        
    Returns:
        RoughOutlineResponse: 创建的粗略大纲信息
    """
    try:
        # 验证小说是否属于当前用户
        novel = db.query(Novel).filter(
            and_(Novel.id == outline_data.novel_id, Novel.user_id == current_user.id)
        ).first()
        if not novel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="小说不存在或无权访问"
            )
        
        # 创建粗略大纲
        outline = RoughOutline(
            **outline_data.model_dump(),
            user_id=current_user.id
        )
        
        db.add(outline)
        db.commit()
        db.refresh(outline)
        
        return RoughOutlineResponse.model_validate(outline)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建粗略大纲失败: {str(e)}"
        )


@router.get("/rough/novel/{novel_id}", response_model=RoughOutlineListResponse)
async def get_rough_outlines_by_novel(
    novel_id: int,
    outline_type: Optional[OutlineType] = Query(None, description="大纲类型筛选"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取小说的粗略大纲列表
    
    Args:
        novel_id: 小说ID
        outline_type: 大纲类型筛选
        db: 数据库会话
        current_user: 当前用户
        
    Returns:
        RoughOutlineListResponse: 粗略大纲列表响应
    """
    try:
        # 验证小说是否属于当前用户
        novel = db.query(Novel).filter(
            and_(Novel.id == novel_id, Novel.user_id == current_user.id)
        ).first()
        if not novel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="小说不存在或无权访问"
            )
        
        # 构建查询条件
        query = db.query(RoughOutline).filter(
            and_(RoughOutline.novel_id == novel_id, RoughOutline.user_id == current_user.id)
        )
        
        if outline_type:
            query = query.filter(RoughOutline.outline_type == outline_type)
        
        # 按排序索引排序
        outlines = query.order_by(RoughOutline.outline_type, RoughOutline.order_index).all()
        
        # 转换为响应格式
        outline_responses = [
            RoughOutlineResponse.model_validate(outline)
            for outline in outlines
        ]
        
        return RoughOutlineListResponse(
            items=outline_responses,
            total=len(outline_responses)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取粗略大纲列表失败: {str(e)}"
        )


@router.get("/rough/{outline_id}", response_model=RoughOutlineResponse)
async def get_rough_outline(
    outline_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取单个粗略大纲详情"""
    outline = db.query(RoughOutline).filter(
        and_(RoughOutline.id == outline_id, RoughOutline.user_id == current_user.id)
    ).first()
    
    if not outline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="粗略大纲不存在"
        )
    
    return RoughOutlineResponse.model_validate(outline)


@router.put("/rough/{outline_id}", response_model=RoughOutlineResponse)
async def update_rough_outline(
    outline_id: int,
    outline_data: RoughOutlineUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新粗略大纲信息"""
    try:
        outline = db.query(RoughOutline).filter(
            and_(RoughOutline.id == outline_id, RoughOutline.user_id == current_user.id)
        ).first()
        
        if not outline:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="粗略大纲不存在"
            )
        
        # 更新大纲信息
        update_data = outline_data.model_dump(exclude_unset=True)
        outline.update_from_dict(update_data)
        
        db.commit()
        db.refresh(outline)
        
        return RoughOutlineResponse.model_validate(outline)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新粗略大纲失败: {str(e)}"
        )


@router.delete("/rough/{outline_id}")
async def delete_rough_outline(
    outline_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除粗略大纲"""
    try:
        outline = db.query(RoughOutline).filter(
            and_(RoughOutline.id == outline_id, RoughOutline.user_id == current_user.id)
        ).first()
        
        if not outline:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="粗略大纲不存在"
            )
        
        db.delete(outline)
        db.commit()
        
        return {"message": "粗略大纲删除成功"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除粗略大纲失败: {str(e)}"
        )


# ============ 详细大纲 API ============

@router.post("/detailed", response_model=DetailedOutlineResponse, status_code=status.HTTP_201_CREATED)
async def create_detailed_outline(
    outline_data: DetailedOutlineCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建详细大纲
    
    Args:
        outline_data: 详细大纲创建数据
        db: 数据库会话
        current_user: 当前用户
        
    Returns:
        DetailedOutlineResponse: 创建的详细大纲信息
    """
    try:
        # 验证小说是否属于当前用户
        novel = db.query(Novel).filter(
            and_(Novel.id == outline_data.novel_id, Novel.user_id == current_user.id)
        ).first()
        if not novel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="小说不存在或无权访问"
            )
        
        # 检查章节号是否已存在
        existing_outline = db.query(DetailedOutline).filter(
            and_(
                DetailedOutline.novel_id == outline_data.novel_id,
                DetailedOutline.chapter_number == outline_data.chapter_number,
                DetailedOutline.user_id == current_user.id
            )
        ).first()
        
        if existing_outline:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"章节 {outline_data.chapter_number} 的详细大纲已存在"
            )
        
        # 创建详细大纲
        outline = DetailedOutline(
            **outline_data.model_dump(),
            user_id=current_user.id
        )
        
        db.add(outline)
        db.commit()
        db.refresh(outline)
        
        return DetailedOutlineResponse.model_validate(outline)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建详细大纲失败: {str(e)}"
        )


@router.get("/detailed/novel/{novel_id}", response_model=DetailedOutlineListResponse)
async def get_detailed_outlines_by_novel(
    novel_id: int,
    chapter_start: Optional[int] = Query(None, description="起始章节号"),
    chapter_end: Optional[int] = Query(None, description="结束章节号"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取小说的详细大纲列表
    
    Args:
        novel_id: 小说ID
        chapter_start: 起始章节号
        chapter_end: 结束章节号
        db: 数据库会话
        current_user: 当前用户
        
    Returns:
        DetailedOutlineListResponse: 详细大纲列表响应
    """
    try:
        # 验证小说是否属于当前用户
        novel = db.query(Novel).filter(
            and_(Novel.id == novel_id, Novel.user_id == current_user.id)
        ).first()
        if not novel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="小说不存在或无权访问"
            )
        
        # 构建查询条件
        query = db.query(DetailedOutline).filter(
            and_(DetailedOutline.novel_id == novel_id, DetailedOutline.user_id == current_user.id)
        )
        
        if chapter_start:
            query = query.filter(DetailedOutline.chapter_number >= chapter_start)
            
        if chapter_end:
            query = query.filter(DetailedOutline.chapter_number <= chapter_end)
        
        # 按章节号排序
        outlines = query.order_by(DetailedOutline.chapter_number).all()
        
        # 转换为响应格式
        outline_responses = [
            DetailedOutlineResponse.model_validate(outline)
            for outline in outlines
        ]
        
        return DetailedOutlineListResponse(
            items=outline_responses,
            total=len(outline_responses)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取详细大纲列表失败: {str(e)}"
        )


@router.get("/detailed/{outline_id}", response_model=DetailedOutlineResponse)
async def get_detailed_outline(
    outline_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取单个详细大纲详情"""
    outline = db.query(DetailedOutline).filter(
        and_(DetailedOutline.id == outline_id, DetailedOutline.user_id == current_user.id)
    ).first()
    
    if not outline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="详细大纲不存在"
        )
    
    return DetailedOutlineResponse.model_validate(outline)


@router.put("/detailed/{outline_id}", response_model=DetailedOutlineResponse)
async def update_detailed_outline(
    outline_id: int,
    outline_data: DetailedOutlineUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新详细大纲信息"""
    try:
        outline = db.query(DetailedOutline).filter(
            and_(DetailedOutline.id == outline_id, DetailedOutline.user_id == current_user.id)
        ).first()
        
        if not outline:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="详细大纲不存在"
            )
        
        # 更新大纲信息
        update_data = outline_data.model_dump(exclude_unset=True)
        outline.update_from_dict(update_data)
        
        db.commit()
        db.refresh(outline)
        
        return DetailedOutlineResponse.model_validate(outline)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新详细大纲失败: {str(e)}"
        )


@router.delete("/detailed/{outline_id}")
async def delete_detailed_outline(
    outline_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除详细大纲"""
    try:
        outline = db.query(DetailedOutline).filter(
            and_(DetailedOutline.id == outline_id, DetailedOutline.user_id == current_user.id)
        ).first()
        
        if not outline:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="详细大纲不存在"
            )
        
        db.delete(outline)
        db.commit()
        
        return {"message": "详细大纲删除成功"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除详细大纲失败: {str(e)}"
        )


# ============ 大纲生成 API ============

@router.post("/generate/rough", response_model=OutlineGenerationResponse)
async def generate_rough_outline(
    request: RoughOutlineGenerationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    生成粗略大纲
    
    Args:
        request: 粗略大纲生成请求
        db: 数据库会话
        current_user: 当前用户
        
    Returns:
        OutlineGenerationResponse: 大纲生成响应
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
        
        # TODO: 这里应该调用AI生成服务
        # 暂时返回模拟数据
        return OutlineGenerationResponse(
            success=False,
            message="AI生成功能暂未实现，请手动创建大纲",
            rough_outlines=[],
            detailed_outlines=[],
            total_generated=0
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成粗略大纲失败: {str(e)}"
        )


@router.post("/generate/detailed", response_model=OutlineGenerationResponse)
async def generate_detailed_outline(
    request: DetailedOutlineGenerationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    生成详细大纲
    
    Args:
        request: 详细大纲生成请求
        db: 数据库会话
        current_user: 当前用户
        
    Returns:
        OutlineGenerationResponse: 大纲生成响应
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
        
        # TODO: 这里应该调用AI生成服务
        # 暂时返回模拟数据
        return OutlineGenerationResponse(
            success=False,
            message="AI生成功能暂未实现，请手动创建大纲",
            rough_outlines=[],
            detailed_outlines=[],
            total_generated=0
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成详细大纲失败: {str(e)}"
        )


# ============ 大纲总结 API ============

@router.post("/summary", response_model=OutlineSummaryResponse)
async def generate_outline_summary(
    request: OutlineSummaryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    生成大纲总结
    
    Args:
        request: 大纲总结请求
        db: 数据库会话
        current_user: 当前用户
        
    Returns:
        OutlineSummaryResponse: 大纲总结响应
    """
    try:
        # 根据大纲类型查找大纲
        if request.outline_type == "rough":
            outline = db.query(RoughOutline).filter(
                and_(RoughOutline.id == request.outline_id, RoughOutline.user_id == current_user.id)
            ).first()
        else:
            outline = db.query(DetailedOutline).filter(
                and_(DetailedOutline.id == request.outline_id, DetailedOutline.user_id == current_user.id)
            ).first()
        
        if not outline:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="大纲不存在"
            )
        
        # TODO: 这里应该调用AI总结服务
        # 暂时返回模拟数据
        return OutlineSummaryResponse(
            success=False,
            message="AI总结功能暂未实现",
            summary="",
            outline_id=request.outline_id,
            outline_type=request.outline_type
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成大纲总结失败: {str(e)}"
        )