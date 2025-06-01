"""
用户数据模式
Author: AI Writer Team
Created: 2025-06-01
"""

from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """用户基础模式"""
    email: EmailStr
    username: str
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """用户创建模式"""
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        """验证密码强度"""
        if len(v) < 8:
            raise ValueError('密码长度不能少于8位')
        if not any(char.isdigit() for char in v):
            raise ValueError('密码必须包含至少一个数字')
        if not any(char.isalpha() for char in v):
            raise ValueError('密码必须包含至少一个字母')
        return v
    
    @validator('username')
    def validate_username(cls, v):
        """验证用户名"""
        if len(v) < 3:
            raise ValueError('用户名长度不能少于3位')
        if len(v) > 20:
            raise ValueError('用户名长度不能超过20位')
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('用户名只能包含字母、数字、下划线和短划线')
        return v


class UserLogin(BaseModel):
    """用户登录模式"""
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """用户更新模式"""
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    
    @validator('username')
    def validate_username(cls, v):
        """验证用户名"""
        if v is not None:
            if len(v) < 3:
                raise ValueError('用户名长度不能少于3位')
            if len(v) > 20:
                raise ValueError('用户名长度不能超过20位')
            if not v.replace('_', '').replace('-', '').isalnum():
                raise ValueError('用户名只能包含字母、数字、下划线和短划线')
        return v


class UserInDBBase(UserBase):
    """数据库中的用户基础模式"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class User(UserInDBBase):
    """用户响应模式"""
    pass


class UserInDB(UserInDBBase):
    """数据库中的用户模式（包含哈希密码）"""
    hashed_password: str


class Token(BaseModel):
    """令牌模式"""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """令牌数据模式"""
    user_id: Optional[int] = None


class UserResponse(BaseModel):
    """用户响应模式"""
    id: int
    email: str
    username: str
    full_name: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RegisterResponse(BaseModel):
    """注册响应模式"""
    user: UserResponse
    access_token: str
    token_type: str


class LoginResponse(BaseModel):
    """登录响应模式"""
    user: UserResponse
    access_token: str
    token_type: str


class PasswordChange(BaseModel):
    """密码修改模式"""
    current_password: str
    new_password: str
    
    @validator('new_password')
    def validate_new_password(cls, v):
        """验证新密码强度"""
        if len(v) < 8:
            raise ValueError('密码长度不能少于8位')
        if not any(char.isdigit() for char in v):
            raise ValueError('密码必须包含至少一个数字')
        if not any(char.isalpha() for char in v):
            raise ValueError('密码必须包含至少一个字母')
        return v