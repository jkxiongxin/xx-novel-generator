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
}

export default AuthService