"""
AI模型配置管理API
Author: AI Writer Team
Created: 2025-06-01
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.ai_model_config import AIModelConfig, ModelType, RequestFormat
from app.schemas.ai_model_config import (
    AIModelConfigCreate, AIModelConfigUpdate, AIModelConfigResponse,
    AIModelConfigFullResponse, AIModelConfigListResponse,
    AIModelConfigTestRequest, AIModelConfigTestResponse,
    AIModelConfigBatchRequest, AIModelConfigStatsResponse,
    AIModelConfigTemplateResponse, AI_MODEL_TEMPLATES
)
from app.services.ai_service import get_ai_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", response_model=AIModelConfigResponse, summary="创建AI模型配置")
async def create_ai_config(
    config_data: AIModelConfigCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建新的AI模型配置"""
    try:
        # 验证配置
        if config_data.is_default:
            # 如果设为默认，先取消其他配置的默认状态
            db.query(AIModelConfig).filter(
                AIModelConfig.user_id == current_user.id,
                AIModelConfig.is_default == True
            ).update({"is_default": False})
        
        # 创建配置
        config = AIModelConfig(
            user_id=current_user.id,
            **config_data.dict()
        )
        
        # 验证配置有效性
        errors = config.validate_config()
        if errors:
            raise HTTPException(status_code=422, detail=f"配置验证失败: {'; '.join(errors)}")
        
        db.add(config)
        db.commit()
        db.refresh(config)
        
        logger.info(f"用户 {current_user.id} 创建AI配置: {config.name}")
        
        return config
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"创建AI配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail="创建配置失败")


@router.get("/", response_model=AIModelConfigListResponse, summary="获取AI模型配置列表")
async def get_ai_configs(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    model_type: Optional[ModelType] = Query(None, description="模型类型筛选"),
    is_active: Optional[bool] = Query(None, description="启用状态筛选"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户的AI模型配置列表"""
    try:
        # 构建查询
        query = db.query(AIModelConfig).filter(AIModelConfig.user_id == current_user.id)
        
        # 添加筛选条件
        if search:
            query = query.filter(
                or_(
                    AIModelConfig.name.contains(search),
                    AIModelConfig.description.contains(search),
                    AIModelConfig.model_name.contains(search)
                )
            )
        
        if model_type:
            query = query.filter(AIModelConfig.model_type == model_type)
        
        if is_active is not None:
            query = query.filter(AIModelConfig.is_active == is_active)
        
        # 总数统计
        total = query.count()
        
        # 分页查询
        configs = query.order_by(
            AIModelConfig.is_default.desc(),
            AIModelConfig.priority.desc(),
            AIModelConfig.created_at.desc()
        ).offset((page - 1) * page_size).limit(page_size).all()
        
        return AIModelConfigListResponse(
            items=configs,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size
        )
        
    except Exception as e:
        logger.error(f"获取AI配置列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取配置列表失败")


@router.get("/{config_id}", response_model=AIModelConfigResponse, summary="获取AI模型配置详情")
async def get_ai_config(
    config_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取指定AI模型配置的详情"""
    config = db.query(AIModelConfig).filter(
        AIModelConfig.id == config_id,
        AIModelConfig.user_id == current_user.id
    ).first()
    
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    return config


@router.put("/{config_id}", response_model=AIModelConfigResponse, summary="更新AI模型配置")
async def update_ai_config(
    config_id: int,
    config_data: AIModelConfigUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新AI模型配置"""
    try:
        config = db.query(AIModelConfig).filter(
            AIModelConfig.id == config_id,
            AIModelConfig.user_id == current_user.id
        ).first()
        
        if not config:
            raise HTTPException(status_code=404, detail="配置不存在")
        
        # 更新数据
        update_data = config_data.dict(exclude_unset=True)
        
        # 处理默认配置
        if update_data.get("is_default") is True:
            # 取消其他配置的默认状态
            db.query(AIModelConfig).filter(
                AIModelConfig.user_id == current_user.id,
                AIModelConfig.id != config_id,
                AIModelConfig.is_default == True
            ).update({"is_default": False})
        
        # 更新配置
        for key, value in update_data.items():
            setattr(config, key, value)
        
        # 验证配置有效性
        errors = config.validate_config()
        if errors:
            raise HTTPException(status_code=422, detail=f"配置验证失败: {'; '.join(errors)}")
        
        db.commit()
        db.refresh(config)
        
        logger.info(f"用户 {current_user.id} 更新AI配置: {config.name}")
        
        return config
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"更新AI配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail="更新配置失败")


@router.delete("/{config_id}", summary="删除AI模型配置")
async def delete_ai_config(
    config_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除AI模型配置"""
    try:
        config = db.query(AIModelConfig).filter(
            AIModelConfig.id == config_id,
            AIModelConfig.user_id == current_user.id
        ).first()
        
        if not config:
            raise HTTPException(status_code=404, detail="配置不存在")
        
        config_name = config.name
        db.delete(config)
        db.commit()
        
        logger.info(f"用户 {current_user.id} 删除AI配置: {config_name}")
        
        return {"success": True, "message": "配置删除成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"删除AI配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail="删除配置失败")


@router.post("/{config_id}/test", response_model=AIModelConfigTestResponse, summary="测试AI模型配置")
async def test_ai_config(
    config_id: int,
    test_request: AIModelConfigTestRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """测试AI模型配置连接"""
    try:
        # 验证配置存在
        config = db.query(AIModelConfig).filter(
            AIModelConfig.id == config_id,
            AIModelConfig.user_id == current_user.id
        ).first()
        
        if not config:
            raise HTTPException(status_code=404, detail="配置不存在")
        
        # 测试连接
        ai_service = get_ai_service()
        result = await ai_service.test_user_config(
            config_id=config_id,
            user_id=current_user.id,
            db=db,
            test_prompt=test_request.prompt
        )
        
        return AIModelConfigTestResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"测试AI配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail="测试配置失败")


@router.patch("/{config_id}/toggle", response_model=AIModelConfigResponse, summary="切换AI模型配置状态")
async def toggle_ai_config(
    config_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """切换AI模型配置的启用状态"""
    try:
        config = db.query(AIModelConfig).filter(
            AIModelConfig.id == config_id,
            AIModelConfig.user_id == current_user.id
        ).first()
        
        if not config:
            raise HTTPException(status_code=404, detail="配置不存在")
        
        # 切换状态
        config.is_active = not config.is_active
        
        # 如果禁用了默认配置，取消默认状态
        if not config.is_active and config.is_default:
            config.is_default = False
        
        db.commit()
        db.refresh(config)
        
        status = "启用" if config.is_active else "禁用"
        logger.info(f"用户 {current_user.id} {status}AI配置: {config.name}")
        
        return config
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"切换AI配置状态失败: {str(e)}")
        raise HTTPException(status_code=500, detail="切换配置状态失败")


@router.patch("/{config_id}/set-default", response_model=AIModelConfigResponse, summary="设置默认AI模型配置")
async def set_default_ai_config(
    config_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """设置指定的AI模型配置为默认配置"""
    try:
        config = db.query(AIModelConfig).filter(
            AIModelConfig.id == config_id,
            AIModelConfig.user_id == current_user.id,
            AIModelConfig.is_active == True
        ).first()
        
        if not config:
            raise HTTPException(status_code=404, detail="配置不存在或未启用")
        
        # 取消其他配置的默认状态
        db.query(AIModelConfig).filter(
            AIModelConfig.user_id == current_user.id,
            AIModelConfig.id != config_id,
            AIModelConfig.is_default == True
        ).update({"is_default": False})
        
        # 设置为默认
        config.is_default = True
        
        db.commit()
        db.refresh(config)
        
        logger.info(f"用户 {current_user.id} 设置默认AI配置: {config.name}")
        
        return config
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"设置默认AI配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail="设置默认配置失败")


@router.post("/batch", summary="批量操作AI模型配置")
async def batch_ai_configs(
    batch_request: AIModelConfigBatchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """批量操作AI模型配置"""
    try:
        # 验证配置存在且属于当前用户
        configs = db.query(AIModelConfig).filter(
            AIModelConfig.id.in_(batch_request.config_ids),
            AIModelConfig.user_id == current_user.id
        ).all()
        
        if len(configs) != len(batch_request.config_ids):
            raise HTTPException(status_code=404, detail="部分配置不存在")
        
        # 执行批量操作
        if batch_request.action == "activate":
            for config in configs:
                config.is_active = True
        elif batch_request.action == "deactivate":
            for config in configs:
                config.is_active = False
                # 禁用时取消默认状态
                if config.is_default:
                    config.is_default = False
        elif batch_request.action == "delete":
            for config in configs:
                db.delete(config)
        
        db.commit()
        
        logger.info(f"用户 {current_user.id} 批量{batch_request.action} {len(configs)}个AI配置")
        
        return {
            "success": True,
            "message": f"批量{batch_request.action}成功",
            "affected_count": len(configs)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"批量操作AI配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail="批量操作失败")


@router.get("/stats/overview", response_model=AIModelConfigStatsResponse, summary="获取AI模型配置统计")
async def get_ai_config_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户的AI模型配置统计信息"""
    try:
        # 基础统计
        total_configs = db.query(AIModelConfig).filter(
            AIModelConfig.user_id == current_user.id
        ).count()
        
        active_configs = db.query(AIModelConfig).filter(
            AIModelConfig.user_id == current_user.id,
            AIModelConfig.is_active == True
        ).count()
        
        inactive_configs = total_configs - active_configs
        
        # 模型类型统计
        model_type_stats = db.query(
            AIModelConfig.model_type,
            func.count(AIModelConfig.id).label('count')
        ).filter(
            AIModelConfig.user_id == current_user.id
        ).group_by(AIModelConfig.model_type).all()
        
        model_types = {str(stat.model_type): stat.count for stat in model_type_stats}
        
        # 请求格式统计
        request_format_stats = db.query(
            AIModelConfig.request_format,
            func.count(AIModelConfig.id).label('count')
        ).filter(
            AIModelConfig.user_id == current_user.id
        ).group_by(AIModelConfig.request_format).all()
        
        request_formats = {str(stat.request_format): stat.count for stat in request_format_stats}
        
        # 默认配置
        default_config = db.query(AIModelConfig).filter(
            AIModelConfig.user_id == current_user.id,
            AIModelConfig.is_default == True
        ).first()
        
        return AIModelConfigStatsResponse(
            total_configs=total_configs,
            active_configs=active_configs,
            inactive_configs=inactive_configs,
            model_types=model_types,
            request_formats=request_formats,
            default_config_id=default_config.id if default_config else None
        )
        
    except Exception as e:
        logger.error(f"获取AI配置统计失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取统计信息失败")


@router.get("/templates/list", response_model=List[AIModelConfigTemplateResponse], summary="获取AI模型配置模板")
async def get_ai_config_templates():
    """获取预设的AI模型配置模板"""
    try:
        templates = []
        for template in AI_MODEL_TEMPLATES:
            templates.append(AIModelConfigTemplateResponse(**template))
        
        return templates
        
    except Exception as e:
        logger.error(f"获取AI配置模板失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取模板失败")


@router.post("/templates/{template_name}", response_model=AIModelConfigResponse, summary="从模板创建AI模型配置")
async def create_from_template(
    template_name: str,
    api_key: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """从预设模板创建AI模型配置"""
    try:
        # 查找模板
        template = None
        for t in AI_MODEL_TEMPLATES:
            if t["name"].lower() == template_name.lower() or template_name.lower() in t["name"].lower():
                template = t
                break
        
        if not template:
            raise HTTPException(status_code=404, detail="模板不存在")
        
        # 创建配置
        config_data = template["default_config"].copy()
        config_data["name"] = f"{template['name']} - {current_user.username}"
        
        if api_key:
            config_data["api_key"] = api_key
        
        config = AIModelConfig(
            user_id=current_user.id,
            **config_data
        )
        
        # 验证配置
        errors = config.validate_config()
        if errors:
            raise HTTPException(status_code=422, detail=f"配置验证失败: {'; '.join(errors)}")
        
        db.add(config)
        db.commit()
        db.refresh(config)
        
        logger.info(f"用户 {current_user.id} 从模板 {template_name} 创建AI配置")
        
        return config
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"从模板创建AI配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail="从模板创建配置失败")