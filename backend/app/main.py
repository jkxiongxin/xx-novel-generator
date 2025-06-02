"""
FastAPI应用入口
Author: AI Writer Team
Created: 2025-06-01
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import time

from app.core.config import settings
from app.core.database import init_db, check_database_health
from app.api.v1.api import api_router


# 配置日志
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(settings.LOG_FILE) if settings.LOG_FILE else logging.StreamHandler(),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("正在启动AI智能小说创作平台后端服务...")
    
    # 初始化数据库
    try:
        init_db()
        logger.info("数据库初始化完成")
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        raise
    
    # 检查数据库连接
    if check_database_health():
        logger.info("数据库连接正常")
    else:
        logger.warning("数据库连接异常")
    
    logger.info(f"服务启动完成，运行在 {settings.HOST}:{settings.PORT}")
    
    yield
    
    # 关闭时执行
    logger.info("正在关闭服务...")


# 创建FastAPI应用实例
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI智能小说创作平台后端API",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)


# 添加中间件
# CORS中间件
app.add_middleware(
    CORSMiddleware,
    **settings.cors_config
)

# 受信任主机中间件
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)


# 请求处理时间中间件
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """添加请求处理时间头"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# 请求日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """记录请求日志"""
    logger.info(f"请求: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"响应: {response.status_code}")
    return response


# CORS调试中间件
@app.middleware("http")
async def cors_debug_middleware(request: Request, call_next):
    """CORS调试中间件"""
    if settings.DEBUG:
        origin = request.headers.get("origin")
        method = request.method
        
        if origin:
            logger.info(f"CORS请求 - Origin: {origin}, Method: {method}")
        
        # 处理预检请求
        if method == "OPTIONS":
            logger.info(f"预检请求 - Headers: {dict(request.headers)}")
    
    response = await call_next(request)
    
    if settings.DEBUG and request.headers.get("origin"):
        cors_headers = {
            k: v for k, v in response.headers.items()
            if k.lower().startswith("access-control-")
        }
        logger.info(f"CORS响应头: {cors_headers}")
    
    return response


# 全局异常处理器
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP异常处理器"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "code": exc.status_code,
            "message": exc.detail,
            "timestamp": time.time()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """通用异常处理器"""
    logger.error(f"未处理的异常: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "code": 500,
            "message": "服务器内部错误",
            "timestamp": time.time()
        }
    )


# 健康检查接口
@app.get("/health", tags=["健康检查"])
async def health_check():
    """健康检查接口"""
    db_health = check_database_health()
    
    return {
        "success": True,
        "data": {
            "status": "healthy" if db_health else "degraded",
            "version": settings.APP_VERSION,
            "database": "connected" if db_health else "disconnected",
            "timestamp": time.time()
        }
    }


# 根路径
@app.get("/", tags=["根路径"])
async def root():
    """根路径"""
    return {
        "success": True,
        "message": f"欢迎使用{settings.APP_NAME}API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "redoc": "/redoc"
    }


# 包含API路由
app.include_router(
    api_router,
    prefix=settings.API_V1_PREFIX,
    tags=["API v1"]
)


# 应用信息接口
@app.get("/info", tags=["应用信息"])
async def app_info():
    """获取应用信息"""
    return {
        "success": True,
        "data": {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "debug": settings.DEBUG,
            "environment": "development" if settings.DEBUG else "production",
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        log_level=settings.LOG_LEVEL.lower()
    )