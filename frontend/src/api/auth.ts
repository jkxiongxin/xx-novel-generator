/**
 * 用户认证API服务
 * Author: AI Writer Team
 * Created: 2025-06-01
 */

import apiClient from './index'

// 用户数据类型定义
export interface User {
  id: number
  email: string
  username: string
  full_name?: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface UserCreate {
  email: string
  username: string
  password: string
  full_name?: string
}

export interface UserLogin {
  email: string
  password: string
}

export interface AuthResponse {
  user: User
  access_token: string
  token_type: string
}

export interface UserUpdate {
  email?: string
  username?: string
  full_name?: string
}

export interface PasswordChange {
  current_password: string
  new_password: string
}

// 扩展的认证相关类型定义
export interface UserInfo {
  id: string
  username: string
  email: string
  avatar_url?: string
  display_name?: string
  role: string
  email_verified: boolean
  created_at: string
  last_active_at: string
  preferences: {
    theme?: string
    language?: string
  }
}

export interface LoginRequestExtended {
  username: string  // 用户名或邮箱
  password: string
  remember_me?: boolean
  captcha_token?: string
}

export interface LoginResponseExtended {
  success: boolean
  user: UserInfo
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
  permissions: string[]
  last_login_at?: string
  login_count: number
}

export interface RegisterRequestExtended {
  username: string
  email: string
  password: string
  confirm_password: string
  agree_terms: boolean
  invite_code?: string
  captcha_token?: string
}

export interface RegisterResponseExtended {
  success: boolean
  user: UserInfo
  verification_sent: boolean
  message: string
  next_steps: string[]
}

export interface ForgotPasswordRequest {
  email: string
}

export interface ForgotPasswordResponse {
  success: boolean
  message: string
  reset_token_expires?: string
}

export interface ResetPasswordRequest {
  token: string
  password: string
  confirm_password: string
}

export interface ResetPasswordResponse {
  success: boolean
  message: string
  auto_login: boolean
}

export interface VerifyEmailRequest {
  token: string
}

export interface VerifyEmailResponse {
  success: boolean
  user?: UserInfo
  access_token?: string
  message: string
}

export interface ResendVerificationRequest {
  email: string
}

export interface ResendVerificationResponse {
  success: boolean
  message: string
  next_resend_time?: string
}

export interface RefreshTokenRequest {
  refresh_token: string
}

export interface RefreshTokenResponse {
  access_token: string
  refresh_token: string
  expires_in: number
}

export interface LogoutRequest {
  all_devices?: boolean
}

export interface LogoutResponse {
  success: boolean
  message: string
}

export interface GitHubLoginRequest {
  code: string
  state?: string
}

export interface GoogleLoginRequest {
  credential: string
}

// 认证API服务类
export class AuthService {
  /**
   * 用户注册
   */
  static async register(userData: UserCreate): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>('/auth/register', userData)
    
    // 保存token和用户信息
    if (response.data.access_token) {
      localStorage.setItem('access_token', response.data.access_token)
      localStorage.setItem('user_info', JSON.stringify(response.data.user))
    }
    
    return response.data
  }

  /**
   * 用户登录
   */
  static async login(credentials: UserLogin): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>('/auth/login', credentials)
    
    // 保存token和用户信息
    if (response.data.access_token) {
      localStorage.setItem('access_token', response.data.access_token)
      localStorage.setItem('user_info', JSON.stringify(response.data.user))
    }
    
    return response.data
  }

  /**
   * 用户登出
   */
  static logout(): void {
    localStorage.removeItem('access_token')
    localStorage.removeItem('user_info')
  }

  /**
   * 获取当前用户信息
   */
  static async getCurrentUser(): Promise<User> {
    const response = await apiClient.get<User>('/auth/me')
    
    // 更新本地用户信息
    localStorage.setItem('user_info', JSON.stringify(response.data))
    
    return response.data
  }

  /**
   * 更新用户信息
   */
  static async updateUser(userData: UserUpdate): Promise<User> {
    const response = await apiClient.put<User>('/auth/me', userData)
    
    // 更新本地用户信息
    localStorage.setItem('user_info', JSON.stringify(response.data))
    
    return response.data
  }

  /**
   * 修改密码
   */
  static async changePassword(passwordData: PasswordChange): Promise<{ message: string }> {
    const response = await apiClient.post<{ message: string }>('/auth/change-password', passwordData)
    return response.data
  }

  /**
   * 检查是否已登录
   */
  static isAuthenticated(): boolean {
    return !!localStorage.getItem('access_token')
  }

  /**
   * 获取本地保存的用户信息
   */
  static getLocalUser(): User | null {
    const userInfo = localStorage.getItem('user_info')
    return userInfo ? JSON.parse(userInfo) : null
  }

  /**
   * 获取访问令牌
   */
  static getAccessToken(): string | null {
    return localStorage.getItem('access_token')
  }

  // 扩展的认证方法
  
  /**
   * 扩展登录 - 支持用户名或邮箱
   */
  static async loginExtended(credentials: LoginRequestExtended): Promise<LoginResponseExtended> {
    const response = await apiClient.post<LoginResponseExtended>('/auth/login/extended', credentials)
    
    // 保存tokens和用户信息
    if (response.data.access_token) {
      const storage = credentials.remember_me ? localStorage : sessionStorage
      storage.setItem('access_token', response.data.access_token)
      storage.setItem('refresh_token', response.data.refresh_token)
      storage.setItem('user_info', JSON.stringify(response.data.user))
      
      if (credentials.remember_me) {
        localStorage.setItem('remember_me', 'true')
      }
    }
    
    return response.data
  }

  /**
   * 扩展注册
   */
  static async registerExtended(userData: RegisterRequestExtended): Promise<RegisterResponseExtended> {
    const response = await apiClient.post<RegisterResponseExtended>('/auth/register/extended', userData)
    return response.data
  }

  /**
   * 忘记密码
   */
  static async forgotPassword(request: ForgotPasswordRequest): Promise<ForgotPasswordResponse> {
    const response = await apiClient.post<ForgotPasswordResponse>('/auth/forgot-password', request)
    return response.data
  }

  /**
   * 重置密码
   */
  static async resetPassword(request: ResetPasswordRequest): Promise<ResetPasswordResponse> {
    const response = await apiClient.post<ResetPasswordResponse>('/auth/reset-password', request)
    return response.data
  }

  /**
   * 验证邮箱
   */
  static async verifyEmail(request: VerifyEmailRequest): Promise<VerifyEmailResponse> {
    const response = await apiClient.post<VerifyEmailResponse>('/auth/verify-email', request)
    
    // 如果验证成功且返回了token，保存用户信息
    if (response.data.success && response.data.access_token && response.data.user) {
      localStorage.setItem('access_token', response.data.access_token)
      localStorage.setItem('user_info', JSON.stringify(response.data.user))
    }
    
    return response.data
  }

  /**
   * 重新发送验证邮件
   */
  static async resendVerification(request: ResendVerificationRequest): Promise<ResendVerificationResponse> {
    const response = await apiClient.post<ResendVerificationResponse>('/auth/resend-verification', request)
    return response.data
  }

  /**
   * 刷新Token
   */
  static async refreshToken(): Promise<RefreshTokenResponse> {
    const refreshToken = localStorage.getItem('refresh_token') || sessionStorage.getItem('refresh_token')
    if (!refreshToken) {
      throw new Error('No refresh token available')
    }

    const response = await apiClient.post<RefreshTokenResponse>('/auth/refresh', {
      refresh_token: refreshToken
    })

    // 更新tokens
    const storage = localStorage.getItem('remember_me') ? localStorage : sessionStorage
    storage.setItem('access_token', response.data.access_token)
    storage.setItem('refresh_token', response.data.refresh_token)

    return response.data
  }

  /**
   * 扩展登出
   */
  static async logoutExtended(allDevices: boolean = false): Promise<LogoutResponse> {
    try {
      const response = await apiClient.post<LogoutResponse>('/auth/logout', {
        all_devices: allDevices
      })
      
      // 清除本地存储
      this.clearAuth()
      
      return response.data
    } catch (error) {
      // 即使API调用失败，也要清除本地存储
      this.clearAuth()
      throw error
    }
  }

  /**
   * GitHub OAuth登录
   */
  static initiateGitHubLogin(): void {
    const clientId = import.meta.env.VITE_GITHUB_CLIENT_ID
    const redirectUri = encodeURIComponent(`${window.location.origin}/auth/callback/github`)
    const scope = encodeURIComponent('user:email')
    
    const authUrl = `https://github.com/login/oauth/authorize?client_id=${clientId}&redirect_uri=${redirectUri}&scope=${scope}`
    window.location.href = authUrl
  }

  /**
   * GitHub OAuth回调处理
   */
  static async handleGitHubCallback(code: string, state?: string): Promise<LoginResponseExtended> {
    const response = await apiClient.post<LoginResponseExtended>('/auth/github', {
      code,
      state
    })

    // 保存tokens和用户信息
    if (response.data.access_token) {
      localStorage.setItem('access_token', response.data.access_token)
      localStorage.setItem('refresh_token', response.data.refresh_token)
      localStorage.setItem('user_info', JSON.stringify(response.data.user))
    }

    return response.data
  }

  /**
   * Google OAuth登录
   */
  static async handleGoogleLogin(credential: string): Promise<LoginResponseExtended> {
    const response = await apiClient.post<LoginResponseExtended>('/auth/google', {
      credential
    })

    // 保存tokens和用户信息
    if (response.data.access_token) {
      localStorage.setItem('access_token', response.data.access_token)
      localStorage.setItem('refresh_token', response.data.refresh_token)
      localStorage.setItem('user_info', JSON.stringify(response.data.user))
    }

    return response.data
  }

  /**
   * 清除所有认证信息
   */
  static clearAuth(): void {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user_info')
    localStorage.removeItem('remember_me')
    sessionStorage.removeItem('access_token')
    sessionStorage.removeItem('refresh_token')
    sessionStorage.removeItem('user_info')
  }

  /**
   * 获取访问令牌（从localStorage或sessionStorage）
   */
  static getToken(): string | null {
    return localStorage.getItem('access_token') || sessionStorage.getItem('access_token')
  }

  /**
   * 获取刷新令牌
   */
  static getRefreshToken(): string | null {
    return localStorage.getItem('refresh_token') || sessionStorage.getItem('refresh_token')
  }

  /**
   * 检查是否有记住我设置
   */
  static hasRememberMe(): boolean {
    return localStorage.getItem('remember_me') === 'true'
  }

  /**
   * Token自动刷新设置
   */
  static setupTokenRefresh(): void {
    const token = this.getToken()
    if (!token) return

    try {
      const payload = JSON.parse(atob(token.split('.')[1]))
      const expiry = payload.exp * 1000
      const now = Date.now()
      const refreshTime = expiry - now - 5 * 60 * 1000 // 提前5分钟刷新

      if (refreshTime > 0) {
        setTimeout(async () => {
          try {
            await this.refreshToken()
          } catch (error) {
            console.error('Token refresh failed:', error)
            this.clearAuth()
            // 可以在这里触发重新登录的逻辑
            window.location.href = '/auth/login'
          }
        }, refreshTime)
      }
    } catch (error) {
      console.error('Error parsing token:', error)
    }
  }

  /**
   * 检查Token是否有效
   */
  static isTokenValid(): boolean {
    const token = this.getToken()
    if (!token) return false

    try {
      const payload = JSON.parse(atob(token.split('.')[1]))
      const expiry = payload.exp * 1000
      return Date.now() < expiry
    } catch (error) {
      return false
    }
  }

  /**
   * 检查邮箱是否已验证
   */
  static isEmailVerified(): boolean {
    const user = this.getLocalUser()
    return user ? (user as any).email_verified : false
  }
}

export default AuthService