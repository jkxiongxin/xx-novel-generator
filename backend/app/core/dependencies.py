"""
依赖注入配置
Author: AI Writer Team
Created: 2025-06-01
"""

from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.core.config import get_settings, Settings
from app.models.user import User


# HTTP Bearer认证
security = HTTPBearer()


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    获取当前用户ID
    
    Args:
        credentials: HTTP认证凭据
        
    Returns:
        str: 用户ID
        
    Raises:
        HTTPException: 认证失败时抛出异常
    """
    token = credentials.credentials
    payload = decode_access_token(token)
    user_id = payload.get("sub")
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无法验证用户身份",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user_id


def get_current_user(
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
) -> User:
    """
    获取当前用户对象
    
    Args:
        db: 数据库会话
        current_user_id: 当前用户ID
        
    Returns:
        User: 用户对象
        
    Raises:
        HTTPException: 用户不存在时抛出异常
    """
    user = db.query(User).filter(User.id == int(current_user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户已被禁用"
        )
    return user


def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    )
) -> Optional[str]:
    """
    获取当前用户ID（可选）
    
    Args:
        credentials: HTTP认证凭据（可选）
        
    Returns:
        Optional[str]: 用户ID，未认证时返回None
    """
    if credentials is None:
        return None
    
    try:
        token = credentials.credentials
        payload = decode_access_token(token)
        return payload.get("sub")
    except HTTPException:
        return None


def get_database_session() -> Generator[Session, None, None]:
    """
    获取数据库会话
    
    Yields:
        Session: 数据库会话
    """
    db = get_db()
    try:
        yield next(db)
    finally:
        pass


def get_app_settings() -> Settings:
    """
    获取应用设置
    
    Returns:
        Settings: 应用配置
    """
    return get_settings()


def validate_pagination_params(
    page: int = 1,
    page_size: int = 20,
    settings: Settings = Depends(get_app_settings)
) -> dict:
    """
    验证分页参数
    
    Args:
        page: 页码
        page_size: 每页大小
        settings: 应用设置
        
    Returns:
        dict: 验证后的分页参数
        
    Raises:
        HTTPException: 参数无效时抛出异常
    """
    if page < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="页码必须大于0"
        )
    
    if page_size < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="每页大小必须大于0"
        )
    
    if page_size > settings.MAX_PAGE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"每页大小不能超过{settings.MAX_PAGE_SIZE}"
        )
    
    # 计算偏移量
    offset = (page - 1) * page_size
    
    return {
        "page": page,
        "page_size": page_size,
        "offset": offset,
        "limit": page_size
    }


class CommonDependencies:
    """通用依赖集合"""
    
    @staticmethod
    def get_db_session() -> Generator[Session, None, None]:
        """获取数据库会话"""
        return get_database_session()
    
    @staticmethod
    def get_current_user() -> str:
        """获取当前用户"""
        return get_current_user_id
    
    @staticmethod
    def get_settings() -> Settings:
        """获取应用设置"""
        return get_app_settings()
    
    @staticmethod
    def validate_pagination(page: int = 1, page_size: int = 20) -> dict:
        """验证分页参数"""
        return validate_pagination_params(page, page_size)


def require_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    要求管理员用户权限
    
    Args:
        current_user: 当前用户对象
        
    Returns:
        User: 管理员用户对象
        
    Raises:
        HTTPException: 非管理员用户时抛出异常
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    return current_user


def validate_content_owner(
    content_user_id: int,
    current_user_id: str = Depends(get_current_user_id)
) -> bool:
    """
    验证内容所有者权限
    
    Args:
        content_user_id: 内容所有者ID
        current_user_id: 当前用户ID
        
    Returns:
        bool: 是否有权限
        
    Raises:
        HTTPException: 无权限时抛出异常
    """
    if str(content_user_id) != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您没有权限访问此内容"
        )
    return True


# 常用依赖组合
DatabaseDep = Depends(get_db)
CurrentUserIdDep = Depends(get_current_user_id)
CurrentUserDep = Depends(get_current_user)
OptionalUserDep = Depends(get_current_user_optional)
SettingsDep = Depends(get_app_settings)
AdminUserDep = Depends(require_admin_user)