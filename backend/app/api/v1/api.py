"""
API路由聚合
Author: AI Writer Team
Created: 2025-06-01
"""

from fastapi import APIRouter

# 创建API路由器
api_router = APIRouter()


# 健康检查路由
@api_router.get("/health", tags=["健康检查"])
async def api_health():
    """API健康检查"""
    return {
        "success": True,
        "message": "API v1 运行正常",
        "version": "1.0.0"
    }


# 导入路由模块
from app.api.v1 import auth, novels, generation, demo, characters, outline, worldview, chapters, ai_configs, workspace
from app.api.v1 import character_templates, character_template_interactions, admin_character_templates

# 包含认证路由
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["认证"]
)

# 包含小说管理路由
api_router.include_router(
    novels.router,
    prefix="/novels",
    tags=["小说管理"]
)

# 包含角色管理路由
api_router.include_router(
    characters.router,
    tags=["角色管理"]
)

# 包含大纲管理路由
api_router.include_router(
    outline.router,
    tags=["大纲管理"]
)

# 包含世界观管理路由
api_router.include_router(
    worldview.router,
    tags=["世界观管理"]
)

# 包含章节管理路由
api_router.include_router(
    chapters.router,
    prefix="/chapters",
    tags=["章节管理"]
)

# 包含AI配置管理路由
api_router.include_router(
    ai_configs.router,
    prefix="/ai-configs",
    tags=["AI配置管理"]
)

# 包含AI生成路由
api_router.include_router(
    generation.router,
    prefix="/generation",
    tags=["AI生成"]
)

# 包含演示路由（无需认证）
api_router.include_router(
    demo.router,
    prefix="/demo",
    tags=["演示功能"]
)

# 包含角色模板路由
api_router.include_router(
    character_templates.router,
    tags=["角色模板"]
)

# 包含角色模板交互路由
api_router.include_router(
    character_template_interactions.router,
    tags=["角色模板交互"]
)

# 包含管理员角色模板管理路由
api_router.include_router(
    admin_character_templates.router,
    tags=["管理员-角色模板管理"]
)

# 包含工作台路由
api_router.include_router(
    workspace.router,
    prefix="/workspace",
    tags=["工作台"]
)