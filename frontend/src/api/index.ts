/**
 * API服务配置
 * Author: AI Writer Team
 * Created: 2025-06-01
 */

import axios from 'axios'
import type { AxiosInstance, InternalAxiosRequestConfig, AxiosResponse } from 'axios'

// API基础配置
const useProxy = import.meta.env.VITE_USE_PROXY === 'true'
const API_BASE_URL = useProxy
  ? import.meta.env.VITE_API_BASE_URL
  : import.meta.env.VITE_DIRECT_API_URL || 'http://localhost:8001/api/v1'

// 调试信息
if (import.meta.env.VITE_DEBUG === 'true') {
  console.log('[API配置]', {
    useProxy,
    API_BASE_URL,
    mode: import.meta.env.MODE,
    dev: import.meta.env.DEV
  })
}

// 创建axios实例
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000, // 增加超时时间，支持AI生成等长时间操作
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
  // 支持跨域cookie（如果需要）
  withCredentials: false,
})

// 扩展axios配置类型
declare module 'axios' {
  interface InternalAxiosRequestConfig {
    metadata?: {
      startTime: number
    }
  }
}

// 请求拦截器
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // 调试日志
    if (import.meta.env.VITE_DEBUG === 'true') {
      console.log(`[API请求] ${config.method?.toUpperCase()} ${config.url}`, {
        baseURL: config.baseURL,
        data: config.data,
        params: config.params
      })
    }

    // 添加认证token
    const token = localStorage.getItem('access_token')
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }

    // 添加请求时间戳
    config.metadata = { startTime: new Date().getTime() }

    return config
  },
  (error) => {
    console.error('[API请求错误]', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    // 计算请求耗时
    const endTime = new Date().getTime()
    const duration = endTime - (response.config.metadata?.startTime || endTime)

    // 调试日志
    if (import.meta.env.VITE_DEBUG === 'true') {
      console.log(`[API响应] ${response.status} ${response.config.url} (${duration}ms)`, {
        data: response.data,
        headers: response.headers
      })
    }

    // 统一处理响应格式
    if (response.data && typeof response.data === 'object') {
      // 如果是标准响应格式 {success, data, message}
      if ('success' in response.data) {
        return response.data.success ? response.data : Promise.reject(response.data)
      }
    }

    return response
  },
  (error) => {
    // 计算请求耗时
    const endTime = new Date().getTime()
    const duration = endTime - (error.config?.metadata?.startTime || endTime)

    // 详细错误日志
    console.error(`[API错误] ${error.config?.method?.toUpperCase()} ${error.config?.url} (${duration}ms)`, {
      status: error.response?.status,
      statusText: error.response?.statusText,
      data: error.response?.data,
      message: error.message
    })

    // 网络错误处理
    if (!error.response) {
      console.error('[网络错误] 无法连接到服务器')
      return Promise.reject({
        success: false,
        code: 0,
        message: '网络连接失败，请检查网络设置或服务器状态',
        error: 'NETWORK_ERROR'
      })
    }

    // HTTP错误处理
    const { status, data } = error.response
    
    switch (status) {
      case 401:
        // 清除本地token
        localStorage.removeItem('access_token')
        localStorage.removeItem('user_info')
        // 重定向到登录页面
        window.location.href = '/auth/login'
        return Promise.reject({
          success: false,
          code: 401,
          message: '登录已过期，请重新登录',
          error: 'UNAUTHORIZED'
        })
      
      case 403:
        return Promise.reject({
          success: false,
          code: 403,
          message: '权限不足，无法访问该资源',
          error: 'FORBIDDEN'
        })
      
      case 404:
        return Promise.reject({
          success: false,
          code: 404,
          message: '请求的资源不存在',
          error: 'NOT_FOUND'
        })
      
      case 422:
        return Promise.reject({
          success: false,
          code: 422,
          message: data?.message || '请求参数错误',
          errors: data?.errors || [],
          error: 'VALIDATION_ERROR'
        })
      
      case 500:
        return Promise.reject({
          success: false,
          code: 500,
          message: '服务器内部错误，请稍后重试',
          error: 'SERVER_ERROR'
        })
      
      default:
        return Promise.reject({
          success: false,
          code: status,
          message: data?.message || error.message || '请求失败',
          error: 'REQUEST_FAILED'
        })
    }
  }
)

export default apiClient

// 导出一些常用的请求方法
export const api = {
  get: <T = any>(url: string, config?: any) =>
    apiClient.get<T>(url, config),
  
  post: <T = any>(url: string, data?: any, config?: any) =>
    apiClient.post<T>(url, data, config),
  
  put: <T = any>(url: string, data?: any, config?: any) =>
    apiClient.put<T>(url, data, config),
  
  delete: <T = any>(url: string, config?: any) =>
    apiClient.delete<T>(url, config),
  
  patch: <T = any>(url: string, data?: any, config?: any) =>
    apiClient.patch<T>(url, data, config)
}

// 导出配置信息供调试使用
export const apiConfig = {
  baseURL: API_BASE_URL,
  useProxy,
  debug: import.meta.env.VITE_DEBUG === 'true'
}