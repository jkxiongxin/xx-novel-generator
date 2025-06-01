"""
世界观管理API
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
from app.models.worldview import (
    Worldview, WorldMap, CultivationSystem, History, Faction
)
from app.schemas.worldview import (
    WorldviewCreate, WorldviewUpdate, WorldviewResponse,
    WorldMapCreate, WorldMapUpdate, WorldMapResponse,
    CultivationSystemCreate, CultivationSystemUpdate, CultivationSystemResponse,
    HistoryCreate, HistoryUpdate, HistoryResponse,
    FactionCreate, FactionUpdate, FactionResponse,
    WorldviewListResponse, WorldMapListResponse,
    CultivationSystemListResponse, HistoryListResponse, FactionListResponse,
    WorldviewGenerationRequest, WorldviewGenerationResponse
)

router = APIRouter(prefix="/worldview", tags=["世界观管理"])


# ============ 世界观 API ============

@router.post("/", response_model=WorldviewResponse, status_code=status.HTTP_201_CREATED)
async def create_worldview(
    worldview_data: WorldviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建世界观
    
    Args:
        worldview_data: 世界观创建数据
        db: 数据库会话
        current_user: 当前用户
        
    Returns:
        WorldviewResponse: 创建的世界观信息
    """
    try:
        # 验证小说是否属于当前用户
        novel = db.query(Novel).filter(
            and_(Novel.id == worldview_data.novel_id, Novel.user_id == current_user.id)
        ).first()
        if not novel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="小说不存在或无权访问"
            )
        
        # 如果设置为主世界，将其他世界观的主世界标识设为False
        if worldview_data.is_primary:
            db.query(Worldview).filter(
                and_(Worldview.novel_id == worldview_data.novel_id, Worldview.user_id == current_user.id)
            ).update({"is_primary": False})
        
        # 创建世界观
        worldview = Worldview(
            **worldview_data.model_dump(),
            user_id=current_user.id
        )
        
        db.add(worldview)
        db.commit()
        db.refresh(worldview)
        
        return WorldviewResponse.model_validate(worldview)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建世界观失败: {str(e)}"
        )


@router.get("/novel/{novel_id}", response_model=WorldviewListResponse)
async def get_worldviews_by_novel(
    novel_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取小说的世界观列表
    
    Args:
        novel_id: 小说ID
        db: 数据库会话
        current_user: 当前用户
        
    Returns:
        WorldviewListResponse: 世界观列表响应
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
        
        # 获取世界观列表
        worldviews = db.query(Worldview).filter(
            and_(Worldview.novel_id == novel_id, Worldview.user_id == current_user.id)
        ).order_by(Worldview.is_primary.desc(), Worldview.created_at).all()
        
        # 转换为响应格式
        worldview_responses = [
            WorldviewResponse.model_validate(worldview)
            for worldview in worldviews
        ]
        
        return WorldviewListResponse(
            items=worldview_responses,
            total=len(worldview_responses)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取世界观列表失败: {str(e)}"
        )


@router.get("/{worldview_id}", response_model=WorldviewResponse)
async def get_worldview(
    worldview_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取单个世界观详情"""
    worldview = db.query(Worldview).filter(
        and_(Worldview.id == worldview_id, Worldview.user_id == current_user.id)
    ).first()
    
    if not worldview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="世界观不存在"
        )
    
    return WorldviewResponse.model_validate(worldview)


@router.put("/{worldview_id}", response_model=WorldviewResponse)
async def update_worldview(
    worldview_id: int,
    worldview_data: WorldviewUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新世界观信息"""
    try:
        worldview = db.query(Worldview).filter(
            and_(Worldview.id == worldview_id, Worldview.user_id == current_user.id)
        ).first()
        
        if not worldview:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="世界观不存在"
            )
        
        # 如果设置为主世界，将其他世界观的主世界标识设为False
        if worldview_data.is_primary is True:
            db.query(Worldview).filter(
                and_(
                    Worldview.novel_id == worldview.novel_id,
                    Worldview.user_id == current_user.id,
                    Worldview.id != worldview_id
                )
            ).update({"is_primary": False})
        
        # 更新世界观信息
        update_data = worldview_data.model_dump(exclude_unset=True)
        worldview.update_from_dict(update_data)
        
        db.commit()
        db.refresh(worldview)
        
        return WorldviewResponse.model_validate(worldview)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新世界观失败: {str(e)}"
        )


@router.delete("/{worldview_id}")
async def delete_worldview(
    worldview_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除世界观"""
    try:
        worldview = db.query(Worldview).filter(
            and_(Worldview.id == worldview_id, Worldview.user_id == current_user.id)
        ).first()
        
        if not worldview:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="世界观不存在"
            )
        
        db.delete(worldview)
        db.commit()
        
        return {"message": "世界观删除成功"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除世界观失败: {str(e)}"
        )


# ============ 世界地图 API ============

@router.post("/{worldview_id}/maps", response_model=WorldMapResponse, status_code=status.HTTP_201_CREATED)
async def create_world_map(
    worldview_id: int,
    map_data: WorldMapCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建世界地图区域"""
    try:
        # 验证世界观是否属于当前用户
        worldview = db.query(Worldview).filter(
            and_(Worldview.id == worldview_id, Worldview.user_id == current_user.id)
        ).first()
        if not worldview:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="世界观不存在或无权访问"
            )
        
        # 创建世界地图
        world_map = WorldMap(
            **map_data.model_dump(),
            worldview_id=worldview_id,
            user_id=current_user.id
        )
        
        db.add(world_map)
        db.commit()
        db.refresh(world_map)
        
        return WorldMapResponse.model_validate(world_map)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建世界地图失败: {str(e)}"
        )


@router.get("/{worldview_id}/maps", response_model=WorldMapListResponse)
async def get_world_maps(
    worldview_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取世界地图列表"""
    try:
        # 验证世界观是否属于当前用户
        worldview = db.query(Worldview).filter(
            and_(Worldview.id == worldview_id, Worldview.user_id == current_user.id)
        ).first()
        if not worldview:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="世界观不存在或无权访问"
            )
        
        # 获取世界地图列表
        maps = db.query(WorldMap).filter(
            and_(WorldMap.worldview_id == worldview_id, WorldMap.user_id == current_user.id)
        ).order_by(WorldMap.level, WorldMap.region_name).all()
        
        # 转换为响应格式
        map_responses = [
            WorldMapResponse.model_validate(map_item)
            for map_item in maps
        ]
        
        return WorldMapListResponse(
            items=map_responses,
            total=len(map_responses)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取世界地图列表失败: {str(e)}"
        )


# ============ 修炼体系 API ============

@router.post("/{worldview_id}/cultivation", response_model=CultivationSystemResponse, status_code=status.HTTP_201_CREATED)
async def create_cultivation_system(
    worldview_id: int,
    cultivation_data: CultivationSystemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建修炼体系"""
    try:
        # 验证世界观是否属于当前用户
        worldview = db.query(Worldview).filter(
            and_(Worldview.id == worldview_id, Worldview.user_id == current_user.id)
        ).first()
        if not worldview:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="世界观不存在或无权访问"
            )
        
        # 创建修炼体系
        cultivation = CultivationSystem(
            **cultivation_data.model_dump(),
            worldview_id=worldview_id,
            user_id=current_user.id
        )
        
        db.add(cultivation)
        db.commit()
        db.refresh(cultivation)
        
        return CultivationSystemResponse.model_validate(cultivation)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建修炼体系失败: {str(e)}"
        )


@router.get("/{worldview_id}/cultivation", response_model=CultivationSystemListResponse)
async def get_cultivation_systems(
    worldview_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取修炼体系列表"""
    try:
        # 验证世界观是否属于当前用户
        worldview = db.query(Worldview).filter(
            and_(Worldview.id == worldview_id, Worldview.user_id == current_user.id)
        ).first()
        if not worldview:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="世界观不存在或无权访问"
            )
        
        # 获取修炼体系列表
        systems = db.query(CultivationSystem).filter(
            and_(CultivationSystem.worldview_id == worldview_id, CultivationSystem.user_id == current_user.id)
        ).order_by(CultivationSystem.system_name, CultivationSystem.level_order).all()
        
        # 转换为响应格式
        system_responses = [
            CultivationSystemResponse.model_validate(system)
            for system in systems
        ]
        
        return CultivationSystemListResponse(
            items=system_responses,
            total=len(system_responses)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取修炼体系列表失败: {str(e)}"
        )


# ============ 历史事件 API ============

@router.post("/{worldview_id}/history", response_model=HistoryResponse, status_code=status.HTTP_201_CREATED)
async def create_history(
    worldview_id: int,
    history_data: HistoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建历史事件"""
    try:
        # 验证世界观是否属于当前用户
        worldview = db.query(Worldview).filter(
            and_(Worldview.id == worldview_id, Worldview.user_id == current_user.id)
        ).first()
        if not worldview:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="世界观不存在或无权访问"
            )
        
        # 创建历史事件
        history = History(
            **history_data.model_dump(),
            worldview_id=worldview_id,
            user_id=current_user.id
        )
        
        db.add(history)
        db.commit()
        db.refresh(history)
        
        return HistoryResponse.model_validate(history)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建历史事件失败: {str(e)}"
        )


@router.get("/{worldview_id}/history", response_model=HistoryListResponse)
async def get_histories(
    worldview_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取历史事件列表"""
    try:
        # 验证世界观是否属于当前用户
        worldview = db.query(Worldview).filter(
            and_(Worldview.id == worldview_id, Worldview.user_id == current_user.id)
        ).first()
        if not worldview:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="世界观不存在或无权访问"
            )
        
        # 获取历史事件列表
        histories = db.query(History).filter(
            and_(History.worldview_id == worldview_id, History.user_id == current_user.id)
        ).order_by(History.time_order).all()
        
        # 转换为响应格式
        history_responses = [
            HistoryResponse.model_validate(history)
            for history in histories
        ]
        
        return HistoryListResponse(
            items=history_responses,
            total=len(history_responses)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取历史事件列表失败: {str(e)}"
        )


# ============ 阵营势力 API ============

@router.post("/{worldview_id}/factions", response_model=FactionResponse, status_code=status.HTTP_201_CREATED)
async def create_faction(
    worldview_id: int,
    faction_data: FactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建阵营势力"""
    try:
        # 验证世界观是否属于当前用户
        worldview = db.query(Worldview).filter(
            and_(Worldview.id == worldview_id, Worldview.user_id == current_user.id)
        ).first()
        if not worldview:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="世界观不存在或无权访问"
            )
        
        # 创建阵营势力
        faction = Faction(
            **faction_data.model_dump(),
            worldview_id=worldview_id,
            user_id=current_user.id
        )
        
        db.add(faction)
        db.commit()
        db.refresh(faction)
        
        return FactionResponse.model_validate(faction)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建阵营势力失败: {str(e)}"
        )


@router.get("/{worldview_id}/factions", response_model=FactionListResponse)
async def get_factions(
    worldview_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取阵营势力列表"""
    try:
        # 验证世界观是否属于当前用户
        worldview = db.query(Worldview).filter(
            and_(Worldview.id == worldview_id, Worldview.user_id == current_user.id)
        ).first()
        if not worldview:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="世界观不存在或无权访问"
            )
        
        # 获取阵营势力列表
        factions = db.query(Faction).filter(
            and_(Faction.worldview_id == worldview_id, Faction.user_id == current_user.id)
        ).order_by(Faction.faction_type, Faction.name).all()
        
        # 转换为响应格式
        faction_responses = [
            FactionResponse.model_validate(faction)
            for faction in factions
        ]
        
        return FactionListResponse(
            items=faction_responses,
            total=len(faction_responses)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取阵营势力列表失败: {str(e)}"
        )


# ============ 世界观生成 API ============

@router.post("/generate", response_model=WorldviewGenerationResponse)
async def generate_worldview(
    request: WorldviewGenerationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    生成世界观
    
    Args:
        request: 世界观生成请求
        db: 数据库会话
        current_user: 当前用户
        
    Returns:
        WorldviewGenerationResponse: 世界观生成响应
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
        return WorldviewGenerationResponse(
            success=False,
            message="AI生成功能暂未实现，请手动创建世界观",
            worldview=None,
            world_maps=[],
            cultivation_systems=[],
            histories=[],
            factions=[],
            total_generated=0
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成世界观失败: {str(e)}"
        )