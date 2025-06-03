/**
 * 用户状态管理
 * Author: AI Assistant
 * Created: 2025-06-03
 */

import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

export interface UserInfo {
  id: number
  username: string
  email: string
  nickname?: string
  bio?: string
  avatar_url?: string
  is_active: boolean
  is_verified: boolean
  is_admin: boolean
  preferred_language: string
  timezone: string
  created_at: string
  updated_at: string
}

export const useUserStore = defineStore('user', () => {
  // === 状态 ===
  const userInfo = ref<UserInfo | null>(null)
  const isLoggedIn = ref(false)
  const accessToken = ref<string | null>(null)

  // === 计算属性 ===
  const isAdmin = computed(() => userInfo.value?.is_admin || false)
  const displayName = computed(() => userInfo.value?.nickname || userInfo.value?.username || '')

  // === 方法 ===
  
  /**
   * 设置用户信息
   */
  const setUserInfo = (info: UserInfo) => {
    userInfo.value = info
    isLoggedIn.value = true
  }

  /**
   * 设置访问令牌
   */
  const setAccessToken = (token: string) => {
    accessToken.value = token
    localStorage.setItem('access_token', token)
  }

  /**
   * 清除用户信息
   */
  const clearUserInfo = () => {
    userInfo.value = null
    isLoggedIn.value = false
    accessToken.value = null
    localStorage.removeItem('access_token')
  }

  /**
   * 从本地存储恢复令牌
   */
  const restoreToken = () => {
    const token = localStorage.getItem('access_token')
    if (token) {
      accessToken.value = token
      // 这里可以验证令牌有效性并获取用户信息
      // TODO: 实现自动获取用户信息的逻辑
    }
  }

  /**
   * 登录
   */
  const login = (token: string, user: UserInfo) => {
    setAccessToken(token)
    setUserInfo(user)
  }

  /**
   * 登出
   */
  const logout = () => {
    clearUserInfo()
  }

  /**
   * 更新用户信息
   */
  const updateUserInfo = (updates: Partial<UserInfo>) => {
    if (userInfo.value) {
      userInfo.value = { ...userInfo.value, ...updates }
    }
  }

  return {
    // 状态
    userInfo,
    isLoggedIn,
    accessToken,
    
    // 计算属性
    isAdmin,
    displayName,
    
    // 方法
    setUserInfo,
    setAccessToken,
    clearUserInfo,
    restoreToken,
    login,
    logout,
    updateUserInfo
  }
})