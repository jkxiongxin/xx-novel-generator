"""
世界观管理API
Author: AI Assistant
Created: 2025-06-01
Updated: 2025-06-03
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

@router.post("/")
async def create_worldview(
    worldview_data: WorldviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建世界观"""
    try:
        # 验证小说是否属于当前用户
        novel = db.query(Novel).filter(
            and_(Novel.id == worldview_data.novel_id, Novel.user_id == current_user.id)
        ).first()
        if not novel:
            return {
                "success": False,
                "code": 404,
                "message": "小说不存在或无权访问",
                "data": None
            }
        
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
        
        return {
            "success": True,
            "code": 201,
            "message": "世界观创建成功",
            "data": WorldviewResponse.model_validate(worldview)
        }
        
    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "code": 500,
            "message": f"创建世界观失败: {str(e)}",
            "data": None
        }


@router.get("/novel/{novel_id}")
async def get_worldviews_by_novel(
    novel_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取小说的世界观列表"""
    try:
        # 验证小说是否属于当前用户
        novel = db.query(Novel).filter(
            and_(Novel.id == novel_id, Novel.user_id == current_user.id)
        ).first()
        if not novel:
            return {
                "success": False,
                "code": 404,
                "message": "小说不存在或无权访问",
                "data": None
            }
        
        # 获取世界观列表
        worldviews = db.query(Worldview).filter(
            and_(Worldview.novel_id == novel_id, Worldview.user_id == current_user.id)
        ).order_by(Worldview.is_primary.desc(), Worldview.created_at).all()
        
        # 转换为响应格式
        worldview_responses = [
            WorldviewResponse.model_validate(worldview)
            for worldview in worldviews
        ]
        
        return {
            "success": True,
            "code": 200,
            "message": "获取世界观列表成功",
            "data": {
                "items": worldview_responses,
                "total": len(worldview_responses)
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "code": 500,
            "message": f"获取世界观列表失败: {str(e)}",
            "data": None
        }


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


@router.put("/{worldview_id}")
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
            return {
                "success": False,
                "code": 404,
                "message": "世界观不存在",
                "data": None
            }
        
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
        
        return {
            "success": True,
            "code": 200,
            "message": "世界观更新成功",
            "data": WorldviewResponse.model_validate(worldview)
        }
        
    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "code": 500,
            "message": f"更新世界观失败: {str(e)}",
            "data": None
        }


@router.delete("/{worldview_id}")
async def delete_worldview(
    worldview_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除世界观及其所有相关数据"""
    try:
        worldview = db.query(Worldview).filter(
            and_(Worldview.id == worldview_id, Worldview.user_id == current_user.id)
        ).first()
        
        if not worldview:
            return {
                "success": False,
                "code": 404,
                "message": "世界观不存在",
                "data": None
            }
        
        # 统计删除数量
        deleted_count = {"worldview": 1}
        
        # 删除世界地图
        world_maps = db.query(WorldMap).filter(
            and_(WorldMap.worldview_id == worldview_id, WorldMap.user_id == current_user.id)
        ).all()
        deleted_count["world_maps"] = len(world_maps)
        for world_map in world_maps:
            db.delete(world_map)
        
        # 删除修炼体系
        cultivation_systems = db.query(CultivationSystem).filter(
            and_(CultivationSystem.worldview_id == worldview_id, CultivationSystem.user_id == current_user.id)
        ).all()
        deleted_count["cultivation_systems"] = len(cultivation_systems)
        for cultivation in cultivation_systems:
            db.delete(cultivation)
        
        # 删除历史事件
        histories = db.query(History).filter(
            and_(History.worldview_id == worldview_id, History.user_id == current_user.id)
        ).all()
        deleted_count["histories"] = len(histories)
        for history in histories:
            db.delete(history)
        
        # 删除阵营势力
        factions = db.query(Faction).filter(
            and_(Faction.worldview_id == worldview_id, Faction.user_id == current_user.id)
        ).all()
        deleted_count["factions"] = len(factions)
        for faction in factions:
            db.delete(faction)
        
        # 最后删除世界观本身
        db.delete(worldview)
        db.commit()
        
        total_deleted = sum(deleted_count.values())
        
        return {
            "success": True,
            "code": 200,
            "message": f"世界观删除成功，共删除 {total_deleted} 项数据",
            "data": {
                "deleted_count": deleted_count,
                "total_deleted": total_deleted,
                "worldview_name": worldview.name
            }
        }
        
    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "code": 500,
            "message": f"删除世界观失败: {str(e)}",
            "data": None
        }


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


@router.get("/{worldview_id}/maps")
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
            return {
                "success": False,
                "code": 404,
                "message": "世界观不存在或无权访问",
                "data": None
            }
        
        # 获取世界地图列表
        maps = db.query(WorldMap).filter(
            and_(WorldMap.worldview_id == worldview_id, WorldMap.user_id == current_user.id)
        ).order_by(WorldMap.level, WorldMap.region_name).all()
        
        # 转换为响应格式
        map_responses = [
            WorldMapResponse.model_validate(map_item)
            for map_item in maps
        ]
        
        return {
            "success": True,
            "code": 200,
            "message": "获取世界地图列表成功",
            "data": {
                "items": map_responses,
                "total": len(map_responses)
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "code": 500,
            "message": f"获取世界地图列表失败: {str(e)}",
            "data": None
        }


@router.put("/maps/{map_id}", response_model=WorldMapResponse)
async def update_world_map(
    map_id: int,
    map_data: WorldMapUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新世界地图"""
    try:
        world_map = db.query(WorldMap).filter(
            and_(WorldMap.id == map_id, WorldMap.user_id == current_user.id)
        ).first()
        
        if not world_map:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="世界地图不存在"
            )
        
        # 更新数据
        update_data = map_data.model_dump(exclude_unset=True)
        world_map.update_from_dict(update_data)
        
        db.commit()
        db.refresh(world_map)
        
        return WorldMapResponse.model_validate(world_map)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新世界地图失败: {str(e)}"
        )


@router.delete("/maps/{map_id}")
async def delete_world_map(
    map_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除世界地图"""
    try:
        world_map = db.query(WorldMap).filter(
            and_(WorldMap.id == map_id, WorldMap.user_id == current_user.id)
        ).first()
        
        if not world_map:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="世界地图不存在"
            )
        
        db.delete(world_map)
        db.commit()
        
        return {"message": "世界地图删除成功"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除世界地图失败: {str(e)}"
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


@router.get("/{worldview_id}/cultivation")
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
            return {
                "success": False,
                "code": 404,
                "message": "世界观不存在或无权访问",
                "data": None
            }
        
        # 获取修炼体系列表
        systems = db.query(CultivationSystem).filter(
            and_(CultivationSystem.worldview_id == worldview_id, CultivationSystem.user_id == current_user.id)
        ).order_by(CultivationSystem.system_name, CultivationSystem.level_order).all()
        
        # 转换为响应格式
        system_responses = [
            CultivationSystemResponse.model_validate(system)
            for system in systems
        ]
        
        return {
            "success": True,
            "code": 200,
            "message": "获取修炼体系列表成功",
            "data": {
                "items": system_responses,
                "total": len(system_responses)
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "code": 500,
            "message": f"获取修炼体系列表失败: {str(e)}",
            "data": None
        }


@router.put("/cultivation/{cultivation_id}", response_model=CultivationSystemResponse)
async def update_cultivation_system(
    cultivation_id: int,
    cultivation_data: CultivationSystemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新修炼体系"""
    try:
        cultivation = db.query(CultivationSystem).filter(
            and_(CultivationSystem.id == cultivation_id, CultivationSystem.user_id == current_user.id)
        ).first()
        
        if not cultivation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="修炼体系不存在"
            )
        
        # 更新数据
        update_data = cultivation_data.model_dump(exclude_unset=True)
        cultivation.update_from_dict(update_data)
        
        db.commit()
        db.refresh(cultivation)
        
        return CultivationSystemResponse.model_validate(cultivation)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新修炼体系失败: {str(e)}"
        )


@router.delete("/cultivation/{cultivation_id}")
async def delete_cultivation_system(
    cultivation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除修炼体系"""
    try:
        cultivation = db.query(CultivationSystem).filter(
            and_(CultivationSystem.id == cultivation_id, CultivationSystem.user_id == current_user.id)
        ).first()
        
        if not cultivation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="修炼体系不存在"
            )
        
        db.delete(cultivation)
        db.commit()
        
        return {"message": "修炼体系删除成功"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除修炼体系失败: {str(e)}"
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


@router.get("/{worldview_id}/history")
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
            return {
                "success": False,
                "code": 404,
                "message": "世界观不存在或无权访问",
                "data": None
            }
        
        # 获取历史事件列表
        histories = db.query(History).filter(
            and_(History.worldview_id == worldview_id, History.user_id == current_user.id)
        ).order_by(History.time_order).all()
        
        # 转换为响应格式
        history_responses = [
            HistoryResponse.model_validate(history)
            for history in histories
        ]
        
        return {
            "success": True,
            "code": 200,
            "message": "获取历史事件列表成功",
            "data": {
                "items": history_responses,
                "total": len(history_responses)
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "code": 500,
            "message": f"获取历史事件列表失败: {str(e)}",
            "data": None
        }


@router.put("/history/{history_id}", response_model=HistoryResponse)
async def update_history(
    history_id: int,
    history_data: HistoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新历史事件"""
    try:
        history = db.query(History).filter(
            and_(History.id == history_id, History.user_id == current_user.id)
        ).first()
        
        if not history:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="历史事件不存在"
            )
        
        # 更新数据
        update_data = history_data.model_dump(exclude_unset=True)
        history.update_from_dict(update_data)
        
        db.commit()
        db.refresh(history)
        
        return HistoryResponse.model_validate(history)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新历史事件失败: {str(e)}"
        )


@router.delete("/history/{history_id}")
async def delete_history(
    history_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除历史事件"""
    try:
        history = db.query(History).filter(
            and_(History.id == history_id, History.user_id == current_user.id)
        ).first()
        
        if not history:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="历史事件不存在"
            )
        
        db.delete(history)
        db.commit()
        
        return {"message": "历史事件删除成功"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除历史事件失败: {str(e)}"
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


@router.get("/{worldview_id}/factions")
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
            return {
                "success": False,
                "code": 404,
                "message": "世界观不存在或无权访问",
                "data": None
            }
        
        # 获取阵营势力列表
        factions = db.query(Faction).filter(
            and_(Faction.worldview_id == worldview_id, Faction.user_id == current_user.id)
        ).order_by(Faction.faction_type, Faction.name).all()
        
        # 转换为响应格式
        faction_responses = [
            FactionResponse.model_validate(faction)
            for faction in factions
        ]
        
        return {
            "success": True,
            "code": 200,
            "message": "获取阵营势力列表成功",
            "data": {
                "items": faction_responses,
                "total": len(faction_responses)
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "code": 500,
            "message": f"获取阵营势力列表失败: {str(e)}",
            "data": None
        }


@router.put("/factions/{faction_id}", response_model=FactionResponse)
async def update_faction(
    faction_id: int,
    faction_data: FactionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新阵营势力"""
    try:
        faction = db.query(Faction).filter(
            and_(Faction.id == faction_id, Faction.user_id == current_user.id)
        ).first()
        
        if not faction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="阵营势力不存在"
            )
        
        # 更新数据
        update_data = faction_data.model_dump(exclude_unset=True)
        faction.update_from_dict(update_data)
        
        db.commit()
        db.refresh(faction)
        
        return FactionResponse.model_validate(faction)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新阵营势力失败: {str(e)}"
        )


@router.delete("/factions/{faction_id}")
async def delete_faction(
    faction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除阵营势力"""
    try:
        faction = db.query(Faction).filter(
            and_(Faction.id == faction_id, Faction.user_id == current_user.id)
        ).first()
        
        if not faction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="阵营势力不存在"
            )
        
        db.delete(faction)
        db.commit()
        
        return {"message": "阵营势力删除成功"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除阵营势力失败: {str(e)}"
        )


# ============ 世界观生成 API ============

@router.post("/generate", response_model=WorldviewGenerationResponse)
async def generate_worldview(
    request: WorldviewGenerationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """AI生成世界观"""
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
        
        # 调用生成服务
        from app.services.generation_service import get_generation_service
        from app.services.prompt_service import get_prompt_service
        
        prompt_service = get_prompt_service(db)
        generation_service = get_generation_service(prompt_service)
        
        result = await generation_service.generate_worldview(
            request=request,
            user_id=current_user.id,
            db=db
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成世界观失败: {str(e)}"
        )


@router.post("/save-generated")
async def save_generated_worldview(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """保存AI生成的世界观数据到数据库"""
    try:
        # 直接获取参数，前端传参格式：{"novel_id": 6, "generated_data": {...}}
        novel_id = request.get("novel_id")
        generated_data = request.get("generated_data", {})
        
        print(f"接收到的参数 - novel_id: {novel_id}")
        print(f"generated_data keys: {list(generated_data.keys()) if isinstance(generated_data, dict) else type(generated_data)}")
        
        if not novel_id:
            raise HTTPException(status_code=400, detail="缺少 novel_id 参数")
        
        if not generated_data:
            raise HTTPException(status_code=400, detail="缺少 generated_data 参数")
        
        # 验证小说归属
        novel = db.query(Novel).filter(
            and_(Novel.id == novel_id, Novel.user_id == current_user.id)
        ).first()
        
        if not novel:
            raise HTTPException(status_code=404, detail="小说不存在或无权访问")
        
        # 检查是否已存在主世界观，如果有则将其设为非主世界观
        existing_primary = db.query(Worldview).filter(
            and_(Worldview.novel_id == novel_id, Worldview.is_primary == True)
        ).first()
        if existing_primary:
            existing_primary.is_primary = False
        
        # 创建主世界观
        worldview_data = generated_data.get("worldview", {})
        worldview = Worldview(
            name=worldview_data.get("name", "AI生成世界观"),
            description=worldview_data.get("description", ""),
            novel_id=novel_id,
            user_id=current_user.id,
            is_primary=True
        )
        
        db.add(worldview)
        db.flush()  # 获取 worldview.id
        
        saved_count = 1  # 世界观本身
        
        # 保存世界地图
        world_maps = generated_data.get("world_maps", [])
        for map_data in world_maps:
            try:
                # 处理notable_features
                notable_features = map_data.get("notable_features", [])
                description = map_data.get("description", "")
                if notable_features and isinstance(notable_features, list):
                    features_str = ", ".join(str(f) for f in notable_features)
                    description += f"\n\n特色地点：{features_str}"
                
                world_map = WorldMap(
                    region_name=map_data.get("name", ""),
                    description=description,
                    climate=map_data.get("climate", ""),
                    terrain=None,
                    resources=None,
                    population=None,
                    culture=None,
                    parent_region_id=None,
                    worldview_id=worldview.id,
                    user_id=current_user.id,
                    level=1
                )
                db.add(world_map)
                saved_count += 1
            except Exception as e:
                print(f"保存世界地图时出错: {e}")
                continue
        
        # 保存修炼体系
        cultivation_system = generated_data.get("cultivation_system", {})
        if cultivation_system:
            try:
                system_name = cultivation_system.get("name", "未命名修炼体系")
                system_description = cultivation_system.get("description", "")
                levels = cultivation_system.get("levels", [])
                
                # 处理额外信息
                unique_features = cultivation_system.get("unique_features", [])
                cultivation_methods = cultivation_system.get("cultivation_methods", [])
                
                if unique_features:
                    system_description += f"\n\n特色功能：{', '.join(str(f) for f in unique_features)}"
                if cultivation_methods:
                    system_description += f"\n\n修炼方法：{', '.join(str(m) for m in cultivation_methods)}"
                
                # 为每个等级创建记录
                for idx, level_data in enumerate(levels):
                    if isinstance(level_data, dict):
                        level_name = level_data.get("name", f"第{idx+1}级")
                        level_desc = level_data.get("description", "")
                    else:
                        level_name = str(level_data)
                        level_desc = f"{level_name}等级"
                    
                    # 创建修炼体系记录，包含所有字段
                    cultivation_level = CultivationSystem(
                        system_name=system_name,
                        level_name=level_name,
                        description=level_desc,
                        level_order=idx + 1,
                        worldview_id=worldview.id,
                        user_id=current_user.id,
                        cultivation_method=system_description,
                        required_resources=None,
                        breakthrough_condition=None,
                        power_description=None
                    )
                    db.add(cultivation_level)
                    saved_count += 1
                    
            except Exception as e:
                print(f"保存修炼体系时出错: {e}")
        
        # 保存历史事件
        histories = generated_data.get("histories", [])
        for idx, history_data in enumerate(histories):
            try:
                # 处理major_events
                major_events = history_data.get("major_events", [])
                description = history_data.get("description", "")
                
                if major_events and isinstance(major_events, list):
                    events_str = "; ".join(str(e) for e in major_events)
                    description += f"\n\n重大事件：{events_str}"
                
                history = History(
                    event_name=history_data.get("name", f"历史事件{idx+1}"),
                    background=description,  # 使用 background 字段（NOT NULL）
                    description=description,  # 保留新的 description 字段
                    time_period=history_data.get("time_period", ""),
                    event_type=None,
                    participants=None,
                    consequences=None,
                    related_locations=None,
                    worldview_id=worldview.id,
                    user_id=current_user.id,
                    time_order=idx + 1
                )
                db.add(history)
                saved_count += 1
            except Exception as e:
                print(f"保存历史事件时出错: {e}")
                continue
        
        # 保存阵营势力
        factions = generated_data.get("factions", [])
        for faction_data in factions:
            try:
                # 处理alliance信息
                alliance_data = faction_data.get("alliance", "")
                allies = [alliance_data] if alliance_data else []
                
                faction = Faction(
                    name=faction_data.get("name", ""),
                    description=faction_data.get("description", ""),
                    ideology=faction_data.get("ideology", ""),
                    allies=allies,
                    worldview_id=worldview.id,
                    user_id=current_user.id,
                    faction_type="organization",
                    leader=None,
                    territory=None,
                    power_level=None,
                    enemies=None,
                    member_count=None
                )
                db.add(faction)
                saved_count += 1
            except Exception as e:
                print(f"保存阵营势力时出错: {e}")
                continue
        
        db.commit()
        
        # 返回标准API响应格式
        return {
            "success": True,
            "code": 200,
            "message": f"世界观数据保存成功，共保存 {saved_count} 项内容",
            "data": {
                "worldview": {
                    "id": worldview.id,
                    "name": worldview.name,
                    "description": worldview.description,
                    "is_primary": worldview.is_primary
                },
                "saved_count": saved_count
            },
            "timestamp": None
        }
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        print(f"保存世界观数据时发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"保存失败: {str(e)}")