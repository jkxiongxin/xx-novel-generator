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


class ForgotPasswordRequest(BaseModel):
    """忘记密码请求模式"""
    email: EmailStr


class ForgotPasswordResponse(BaseModel):
    """忘记密码响应模式"""
    success: bool
    message: str
    reset_token_expires: Optional[str] = None


class ResetPasswordRequest(BaseModel):
    """重置密码请求模式"""
    token: str
    password: str
    confirm_password: str
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        """验证密码匹配"""
        if 'password' in values and v != values['password']:
            raise ValueError('两次输入的密码不一致')
        return v
    
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


class ResetPasswordResponse(BaseModel):
    """重置密码响应模式"""
    success: bool
    message: str
    auto_login: bool = False


class VerifyEmailRequest(BaseModel):
    """邮箱验证请求模式"""
    token: str


class VerifyEmailResponse(BaseModel):
    """邮箱验证响应模式"""
    success: bool
    user: Optional[UserResponse] = None
    access_token: Optional[str] = None
    message: str


class ResendVerificationRequest(BaseModel):
    """重发验证邮件请求模式"""
    email: EmailStr


class ResendVerificationResponse(BaseModel):
    """重发验证邮件响应模式"""
    success: bool
    message: str
    next_resend_time: Optional[str] = None


class GitHubLoginRequest(BaseModel):
    """GitHub登录请求模式"""
    code: str
    state: Optional[str] = None


class GoogleLoginRequest(BaseModel):
    """Google登录请求模式"""
    credential: str


class RefreshTokenRequest(BaseModel):
    """刷新Token请求模式"""
    refresh_token: str


class RefreshTokenResponse(BaseModel):
    """刷新Token响应模式"""
    access_token: str
    refresh_token: str
    expires_in: int


class LogoutRequest(BaseModel):
    """登出请求模式"""
    all_devices: bool = False


class LogoutResponse(BaseModel):
    """登出响应模式"""
    success: bool
    message: str


class UserInfo(BaseModel):
    """用户信息模式"""
    id: str
    username: str
    email: str
    avatar_url: Optional[str] = None
    display_name: Optional[str] = None
    role: str = "user"
    email_verified: bool = False
    created_at: str
    last_active_at: str
    preferences: dict


class LoginResponseExtended(BaseModel):
    """扩展登录响应模式"""
    success: bool
    user: UserInfo
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    permissions: list = []
    last_login_at: Optional[str] = None
    login_count: int = 0


class RegisterRequestExtended(BaseModel):
    """扩展注册请求模式"""
    username: str
    email: EmailStr
    password: str
    confirm_password: str
    agree_terms: bool
    invite_code: Optional[str] = None
    captcha_token: Optional[str] = None
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        """验证密码匹配"""
        if 'password' in values and v != values['password']:
            raise ValueError('两次输入的密码不一致')
        return v
    
    @validator('agree_terms')
    def terms_agreed(cls, v):
        """验证用户同意条款"""
        if not v:
            raise ValueError('必须同意用户协议和隐私政策')
        return v
    
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


class RegisterResponseExtended(BaseModel):
    """扩展注册响应模式"""
    success: bool
    user: UserInfo
    verification_sent: bool
    message: str
    next_steps: list


class LoginRequestExtended(BaseModel):
    """扩展登录请求模式"""
    username: str  # 用户名或邮箱
    password: str
    remember_me: bool = False
    captcha_token: Optional[str] = None