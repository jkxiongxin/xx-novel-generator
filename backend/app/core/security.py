"""
安全相关配置
Author: AI Writer Team
Created: 2025-06-01
"""

from datetime import datetime, timedelta
from typing import Any, Union, Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import settings


# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT认证
security = HTTPBearer()


def create_access_token(
    subject: Union[str, Any], 
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    创建访问令牌
    
    Args:
        subject: 令牌主体（通常是用户ID或用户名）
        expires_delta: 过期时间间隔
        
    Returns:
        str: JWT令牌
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "iat": datetime.utcnow(),
        "type": "access"
    }
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """
    验证JWT令牌
    
    Args:
        token: JWT令牌
        
    Returns:
        dict: 解码后的令牌数据，验证失败返回None
    """
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None


def get_password_hash(password: str) -> str:
    """
    获取密码哈希值
    
    Args:
        password: 明文密码
        
    Returns:
        str: 哈希密码
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码
    
    Args:
        plain_password: 明文密码
        hashed_password: 哈希密码
        
    Returns:
        bool: 密码是否匹配
    """
    return pwd_context.verify(plain_password, hashed_password)


def decode_access_token(token: str) -> dict:
    """
    解码访问令牌
    
    Args:
        token: JWT令牌
        
    Returns:
        dict: 令牌载荷
        
    Raises:
        HTTPException: 令牌无效时抛出异常
    """
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="令牌无效",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 检查令牌类型
        token_type: str = payload.get("type")
        if token_type != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="令牌类型无效",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="令牌验证失败",
            headers={"WWW-Authenticate": "Bearer"},
        )


class SecurityUtils:
    """安全工具类"""
    
    @staticmethod
    def generate_password_hash(password: str) -> str:
        """生成密码哈希"""
        return get_password_hash(password)
    
    @staticmethod
    def check_password(password: str, hashed: str) -> bool:
        """检查密码"""
        return verify_password(password, hashed)
    
    @staticmethod
    def create_token(user_id: Union[str, int], expires_minutes: Optional[int] = None) -> str:
        """创建令牌"""
        expires_delta = None
        if expires_minutes:
            expires_delta = timedelta(minutes=expires_minutes)
        return create_access_token(subject=user_id, expires_delta=expires_delta)
    
    @staticmethod
    def validate_token(token: str) -> Optional[dict]:
        """验证令牌"""
        return verify_token(token)
    
    @staticmethod
    def extract_user_id_from_token(token: str) -> Optional[str]:
        """从令牌中提取用户ID"""
        payload = verify_token(token)
        if payload:
            return payload.get("sub")
        return None


# 创建安全工具实例
security_utils = SecurityUtils()


def validate_password_strength(password: str) -> bool:
    """
    验证密码强度
    
    Args:
        password: 密码
        
    Returns:
        bool: 密码是否符合强度要求
    """
    # 密码长度至少8位
    if len(password) < 8:
        return False
    
    # 至少包含一个数字
    if not any(char.isdigit() for char in password):
        return False
    
    # 至少包含一个字母
    if not any(char.isalpha() for char in password):
        return False
    
    return True


def get_password_requirements() -> dict:
    """
    获取密码要求说明
    
    Returns:
        dict: 密码要求
    """
    return {
        "min_length": 8,
        "require_digit": True,
        "require_letter": True,
        "require_special_char": False,
        "description": "密码至少8位，包含字母和数字"
    }