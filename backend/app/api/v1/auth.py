"""
用户认证API路由
Author: AI Writer Team
Created: 2025-06-01
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.database import get_db
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import (
    UserCreate, UserLogin, RegisterResponse, LoginResponse,
    UserResponse, UserUpdate, PasswordChange,
    ForgotPasswordRequest, ForgotPasswordResponse,
    ResetPasswordRequest, ResetPasswordResponse,
    VerifyEmailRequest, VerifyEmailResponse,
    ResendVerificationRequest, ResendVerificationResponse,
    RefreshTokenRequest, RefreshTokenResponse,
    LogoutRequest, LogoutResponse,
    RegisterRequestExtended, RegisterResponseExtended,
    LoginRequestExtended, LoginResponseExtended, UserInfo
)

logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer()


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_create: UserCreate,
    db: Session = Depends(get_db)
):
    """
    用户注册
    
    Args:
        user_create: 用户创建数据
        db: 数据库会话
        
    Returns:
        RegisterResponse: 注册响应，包含用户信息和访问令牌
        
    Raises:
        HTTPException: 用户已存在或创建失败时抛出异常
    """
    # 检查邮箱是否已存在
    existing_user = db.query(User).filter(User.email == user_create.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已被注册"
        )
    
    # 检查用户名是否已存在
    existing_username = db.query(User).filter(User.username == user_create.username).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已被使用"
        )
    
    try:
        # 创建新用户
        hashed_password = get_password_hash(user_create.password)
        db_user = User(
            email=user_create.email,
            username=user_create.username,
            nickname=user_create.full_name,
            password_hash=hashed_password,
            is_active=True
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        # 生成访问令牌
        access_token = create_access_token(subject=str(db_user.id))
        
        # 构造响应
        user_response = UserResponse(
            id=db_user.id,
            email=db_user.email,
            username=db_user.username,
            full_name=db_user.nickname,
            is_active=db_user.is_active,
            created_at=db_user.created_at,
            updated_at=db_user.updated_at
        )
        
        return RegisterResponse(
            user=user_response,
            access_token=access_token,
            token_type="bearer"
        )
        
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户创建失败，请检查输入数据"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="服务器内部错误"
        )


@router.post("/login", response_model=LoginResponse)
async def login(
    user_login: UserLogin,
    db: Session = Depends(get_db)
):
    """
    用户登录
    
    Args:
        user_login: 登录数据
        db: 数据库会话
        
    Returns:
        LoginResponse: 登录响应，包含用户信息和访问令牌
        
    Raises:
        HTTPException: 登录失败时抛出异常
    """
    # 查找用户
    user = db.query(User).filter(User.email == user_login.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误"
        )
    
    # 验证密码
    if not verify_password(user_login.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误"
        )
    
    # 检查用户状态
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="账户已被禁用"
        )
    
    # 生成访问令牌
    access_token = create_access_token(subject=str(user.id))
    
    # 构造响应
    user_response = UserResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        full_name=user.nickname,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at
    )
    
    return LoginResponse(
        user=user_response,
        access_token=access_token,
        token_type="bearer"
    )


@router.get("/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    获取当前用户基本信息 - 首页专用
    
    Args:
        current_user: 当前用户
        
    Returns:
        dict: 用户基本信息，符合设计文档格式
    """
    try:
        # 构建用户偏好设置（可以后续从数据库读取）
        preferences = {
            "theme": "light",  # 默认主题
            "language": "zh-CN"  # 默认语言
        }
        
        return {
            "status": "success",
            "data": {
                "id": str(current_user.id),
                "username": current_user.username,
                "email": current_user.email,
                "avatar_url": None,  # 可以后续添加头像功能
                "created_at": current_user.created_at.isoformat(),
                "last_login_at": current_user.updated_at.isoformat(),  # 暂用更新时间
                "preferences": preferences
            },
            "message": "用户信息获取成功"
        }
        
    except Exception as e:
        logger.error(f"获取用户信息失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取用户信息失败"
        )


@router.get("/me/detailed", response_model=UserResponse)
async def get_detailed_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    获取当前用户详细信息
    
    Args:
        current_user: 当前用户
        
    Returns:
        UserResponse: 详细用户信息
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.nickname,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at
    )


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新当前用户信息
    
    Args:
        user_update: 用户更新数据
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        UserResponse: 更新后的用户信息
        
    Raises:
        HTTPException: 更新失败时抛出异常
    """
    try:
        # 检查邮箱是否已被其他用户使用
        if user_update.email and user_update.email != current_user.email:
            existing_email = db.query(User).filter(
                User.email == user_update.email,
                User.id != current_user.id
            ).first()
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="邮箱已被其他用户使用"
                )
        
        # 检查用户名是否已被其他用户使用
        if user_update.username and user_update.username != current_user.username:
            existing_username = db.query(User).filter(
                User.username == user_update.username,
                User.id != current_user.id
            ).first()
            if existing_username:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="用户名已被其他用户使用"
                )
        
        # 更新用户信息
        update_data = user_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(current_user, field, value)
        
        db.commit()
        db.refresh(current_user)
        
        return UserResponse(
            id=current_user.id,
            email=current_user.email,
            username=current_user.username,
            full_name=current_user.nickname,
            is_active=current_user.is_active,
            created_at=current_user.created_at,
            updated_at=current_user.updated_at
        )
        
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户信息更新失败，请检查输入数据"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="服务器内部错误"
        )


@router.post("/change-password")
async def change_password(
    password_change: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    修改密码
    
    Args:
        password_change: 密码修改数据
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        dict: 操作结果
        
    Raises:
        HTTPException: 修改失败时抛出异常
    """
    # 验证当前密码
    if not verify_password(password_change.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="当前密码错误"
        )


@router.post("/forgot-password", response_model=ForgotPasswordResponse)
async def forgot_password(
    request: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    忘记密码 - 发送重置邮件
    
    Args:
        request: 忘记密码请求
        db: 数据库会话
        
    Returns:
        ForgotPasswordResponse: 操作结果
    """
    try:
        # 查找用户
        user = db.query(User).filter(User.email == request.email).first()
        if not user:
            # 为了安全，即使邮箱不存在也返回成功信息
            return ForgotPasswordResponse(
                success=True,
                message="如果该邮箱已注册，您将收到密码重置邮件",
                reset_token_expires="2025-06-02T10:29:00Z"  # 示例过期时间
            )
        
        # TODO: 生成重置token并发送邮件
        # reset_token = generate_reset_token(user.id)
        # send_reset_email(user.email, reset_token)
        
        logger.info(f"Password reset requested for user: {user.email}")
        
        return ForgotPasswordResponse(
            success=True,
            message="密码重置邮件已发送，请查收",
            reset_token_expires="2025-06-02T10:29:00Z"
        )
        
    except Exception as e:
        logger.error(f"Forgot password error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="发送重置邮件失败"
        )


@router.post("/reset-password", response_model=ResetPasswordResponse)
async def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    重置密码
    
    Args:
        request: 重置密码请求
        db: 数据库会话
        
    Returns:
        ResetPasswordResponse: 操作结果
    """
    try:
        # TODO: 验证重置token
        # user_id = verify_reset_token(request.token)
        # if not user_id:
        #     raise HTTPException(status_code=400, detail="重置链接已过期或无效")
        
        # 临时实现：假设token格式为 "reset_user_id"
        if not request.token.startswith("reset_"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="重置链接无效"
            )
        
        # 模拟用户查找（实际应该从token解析用户ID）
        user = db.query(User).filter(User.email.like("%@%")).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户不存在"
            )
        
        # 重置密码
        user.password_hash = get_password_hash(request.password)
        db.commit()
        
        logger.info(f"Password reset successful for user: {user.email}")
        
        return ResetPasswordResponse(
            success=True,
            message="密码重置成功",
            auto_login=False
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Reset password error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="密码重置失败"
        )


@router.post("/verify-email", response_model=VerifyEmailResponse)
async def verify_email(
    request: VerifyEmailRequest,
    db: Session = Depends(get_db)
):
    """
    验证邮箱
    
    Args:
        request: 邮箱验证请求
        db: 数据库会话
        
    Returns:
        VerifyEmailResponse: 验证结果
    """
    try:
        # TODO: 验证邮箱验证token
        # user_id = verify_email_token(request.token)
        # if not user_id:
        #     raise HTTPException(status_code=400, detail="验证链接已过期或无效")
        
        # 临时实现：假设token格式为 "verify_user_id"
        if not request.token.startswith("verify_"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="验证链接无效"
            )
        
        # 模拟用户查找（实际应该从token解析用户ID）
        user = db.query(User).filter(User.email.like("%@%")).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户不存在"
            )
        
        # 验证邮箱
        user.verify_email()
        db.commit()
        
        # 生成访问token（验证后自动登录）
        access_token = create_access_token(subject=str(user.id))
        
        user_response = UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            full_name=user.nickname,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        
        logger.info(f"Email verified for user: {user.email}")
        
        return VerifyEmailResponse(
            success=True,
            user=user_response,
            access_token=access_token,
            message="邮箱验证成功，已自动登录"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Email verification error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="邮箱验证失败"
        )


@router.post("/resend-verification", response_model=ResendVerificationResponse)
async def resend_verification(
    request: ResendVerificationRequest,
    db: Session = Depends(get_db)
):
    """
    重新发送验证邮件
    
    Args:
        request: 重发验证邮件请求
        db: 数据库会话
        
    Returns:
        ResendVerificationResponse: 操作结果
    """
    try:
        # 查找用户
        user = db.query(User).filter(User.email == request.email).first()
        if not user:
            # 为了安全，即使邮箱不存在也返回成功信息
            return ResendVerificationResponse(
                success=True,
                message="如果该邮箱已注册，您将收到验证邮件",
                next_resend_time="2025-06-01T10:30:00Z"
            )
        
        if user.is_verified:
            return ResendVerificationResponse(
                success=False,
                message="该邮箱已经验证，无需重复验证"
            )
        
        # TODO: 发送验证邮件
        # verification_token = generate_verification_token(user.id)
        # send_verification_email(user.email, verification_token)
        
        logger.info(f"Verification email resent to: {user.email}")
        
        return ResendVerificationResponse(
            success=True,
            message="验证邮件已重新发送，请查收",
            next_resend_time="2025-06-01T10:31:00Z"  # 1分钟后可再次发送
        )
        
    except Exception as e:
        logger.error(f"Resend verification error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="发送验证邮件失败"
        )


@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    刷新访问token
    
    Args:
        request: 刷新token请求
        db: 数据库会话
        
    Returns:
        RefreshTokenResponse: 新的token
    """
    try:
        # TODO: 验证refresh token
        # user_id = verify_refresh_token(request.refresh_token)
        # if not user_id:
        #     raise HTTPException(status_code=401, detail="Refresh token无效")
        
        # 临时实现：生成新的tokens
        new_access_token = create_access_token(subject="1")  # 假设用户ID为1
        new_refresh_token = f"refresh_{new_access_token[:10]}"
        
        return RefreshTokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            expires_in=3600  # 1小时
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token刷新失败"
        )


@router.post("/logout", response_model=LogoutResponse)
async def logout(
    request: LogoutRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    用户登出
    
    Args:
        request: 登出请求
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        LogoutResponse: 操作结果
    """
    try:
        # TODO: 实现token黑名单或撤销逻辑
        # if request.all_devices:
        #     revoke_all_user_tokens(current_user.id)
        # else:
        #     revoke_current_token(token)
        
        logger.info(f"User logged out: {current_user.email}")
        
        return LogoutResponse(
            success=True,
            message="登出成功"
        )
        
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="登出失败"
        )


# 扩展的登录和注册接口
@router.post("/login/extended", response_model=LoginResponseExtended)
async def login_extended(
    request: LoginRequestExtended,
    db: Session = Depends(get_db)
):
    """
    扩展登录接口 - 支持用户名或邮箱登录
    
    Args:
        request: 扩展登录请求
        db: 数据库会话
        
    Returns:
        LoginResponseExtended: 扩展登录响应
    """
    try:
        # 支持用户名或邮箱登录
        user = db.query(User).filter(
            (User.email == request.username) | (User.username == request.username)
        ).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误"
            )
        
        # 验证密码
        if not verify_password(request.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误"
            )
        
        # 检查用户状态
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="账户已被禁用"
            )
        
        # 生成tokens
        access_token = create_access_token(subject=str(user.id))
        refresh_token = f"refresh_{access_token[:10]}"
        
        # 构造用户信息
        user_info = UserInfo(
            id=str(user.id),
            username=user.username,
            email=user.email,
            avatar_url=user.avatar_url,
            display_name=user.display_name,
            role="admin" if user.is_admin else "user",
            email_verified=user.is_verified,
            created_at=user.created_at.isoformat(),
            last_active_at=user.updated_at.isoformat(),
            preferences={
                "theme": "light",
                "language": user.preferred_language
            }
        )
        
        # TODO: 更新登录统计
        # user.last_login_at = datetime.utcnow()
        # user.login_count += 1
        # db.commit()
        
        logger.info(f"Extended login successful for user: {user.email}")
        
        return LoginResponseExtended(
            success=True,
            user=user_info,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=3600,
            permissions=["read", "write"] if not user.is_admin else ["read", "write", "admin"],
            last_login_at=user.updated_at.isoformat(),
            login_count=1  # 临时值
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Extended login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="登录失败"
        )


@router.post("/register/extended", response_model=RegisterResponseExtended)
async def register_extended(
    request: RegisterRequestExtended,
    db: Session = Depends(get_db)
):
    """
    扩展注册接口
    
    Args:
        request: 扩展注册请求
        db: 数据库会话
        
    Returns:
        RegisterResponseExtended: 扩展注册响应
    """
    try:
        # 检查邮箱是否已存在
        existing_user = db.query(User).filter(User.email == request.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"conflict_field": "email", "message": "邮箱已被注册"}
            )
        
        # 检查用户名是否已存在
        existing_username = db.query(User).filter(User.username == request.username).first()
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"conflict_field": "username", "message": "用户名已被使用"}
            )
        
        # 创建新用户
        hashed_password = get_password_hash(request.password)
        db_user = User(
            email=request.email,
            username=request.username,
            password_hash=hashed_password,
            is_active=True,
            is_verified=False  # 需要邮箱验证
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        # 构造用户信息
        user_info = UserInfo(
            id=str(db_user.id),
            username=db_user.username,
            email=db_user.email,
            avatar_url=None,
            display_name=db_user.username,
            role="user",
            email_verified=False,
            created_at=db_user.created_at.isoformat(),
            last_active_at=db_user.created_at.isoformat(),
            preferences={
                "theme": "light",
                "language": "zh-CN"
            }
        )
        
        # TODO: 发送验证邮件
        # verification_token = generate_verification_token(db_user.id)
        # send_verification_email(db_user.email, verification_token)
        
        logger.info(f"Extended registration successful for user: {db_user.email}")
        
        return RegisterResponseExtended(
            success=True,
            user=user_info,
            verification_sent=True,
            message="注册成功，请查收验证邮件",
            next_steps=[
                "查收邮箱中的验证邮件",
                "点击验证链接激活账户",
                "验证成功后即可正常使用"
            ]
        )
        
    except HTTPException:
        raise
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户创建失败，请检查输入数据"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Extended registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="注册失败"
        )
    
    try:
        # 更新密码
        current_user.password_hash = get_password_hash(password_change.new_password)
        db.commit()
        
        return {"message": "密码修改成功"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="密码修改失败"
        )