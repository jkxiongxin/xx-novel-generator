/**
 * 首页API服务
 * Author: AI Writer Team
 * Created: 2025-06-01
 */

import apiClient from './index'

// 首页数据类型定义
export interface NovelOverviewStats {
  total_novels: number
  total_chapters: number
  total_words: number
  active_novels: number
  completed_novels: number
  recent_activity: {
    last_edit_date: string
    daily_words: number
  }
}

export interface RecentNovel {
  id: number
  title: string
  description: string
  genre: string
  status: 'draft' | 'ongoing' | 'completed'
  cover_image?: string
  word_count: number
  chapter_count: number
  created_at: string
  updated_at: string
  last_chapter_title?: string
}

export interface RecentNovelsResponse {
  novels: RecentNovel[]
  total: number
}

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
  last_login_at?: string
  preferences?: {
    theme: 'light' | 'dark' | 'auto'
    language: string
  }
}

export interface SystemStatus {
  ai_service: 'available' | 'unavailable' | 'limited'
  database: 'connected' | 'disconnected'
  feature_flags: {
    brain_generator: boolean
    character_templates: boolean
    ai_generation: boolean
  }
}

export interface QuickCreateNovelRequest {
  title: string
  genre: string
  description?: string
  target_words?: number
  audience?: 'male' | 'female' | 'general'
}

export interface QuickCreateNovelResponse {
  novel: RecentNovel
  redirect_url: string
}

// 统一响应格式
export interface ApiResponse<T> {
  status: 'success' | 'error'
  data: T
  message: string
}

// 首页API服务类
export class HomepageService {
  /**
   * 获取用户统计数据
   */
  static async getOverviewStats(): Promise<NovelOverviewStats> {
    const response = await apiClient.get<ApiResponse<NovelOverviewStats>>('/novels/stats/overview')
    return response.data.data
  }

  /**
   * 获取最近编辑的小说
   */
  static async getRecentNovels(limit: number = 6): Promise<RecentNovelsResponse> {
    const response = await apiClient.get<ApiResponse<RecentNovelsResponse>>('/novels/recent', {
      params: { limit }
    })
    return response.data.data
  }

  /**
   * 获取用户基本信息
   */
  static async getUserInfo(): Promise<UserInfo> {
    const response = await apiClient.get<ApiResponse<UserInfo>>('/auth/me')
    return response.data.data
  }

  /**
   * 检查系统状态
   */
  static async getSystemStatus(): Promise<SystemStatus> {
    const response = await apiClient.get<ApiResponse<SystemStatus>>('/generation/status')
    return response.data.data
  }

  /**
   * 快速创建小说
   */
  static async quickCreateNovel(novelData: QuickCreateNovelRequest): Promise<QuickCreateNovelResponse> {
    const response = await apiClient.post<ApiResponse<QuickCreateNovelResponse>>('/novels', novelData)
    return response.data.data
  }
}

// 工具函数
export const HomepageUtils = {
  /**
   * 格式化字数显示
   */
  formatWordCount(count: number): string {
    if (count >= 10000) {
      return `${(count / 10000).toFixed(1)}万字`
    }
    return `${count}字`
  },

  /**
   * 格式化日期显示
   */
  formatDate(dateString: string): string {
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

    if (diffDays === 0) {
      return '今天'
    } else if (diffDays === 1) {
      return '昨天'
    } else if (diffDays < 7) {
      return `${diffDays}天前`
    } else {
      return date.toLocaleDateString('zh-CN', {
        month: '2-digit',
        day: '2-digit'
      })
    }
  },

  /**
   * 获取状态对应的颜色
   */
  getStatusColor(status: string): string {
    const colorMap = {
      'draft': '#909399',
      'ongoing': '#409EFF',
      'completed': '#67C23A'
    }
    return colorMap[status as keyof typeof colorMap] || '#909399'
  },

  /**
   * 获取状态显示文本
   */
  getStatusText(status: string): string {
    const statusMap = {
      'draft': '草稿',
      'ongoing': '连载中',
      'completed': '已完成'
    }
    return statusMap[status as keyof typeof statusMap] || status
  },

  /**
   * 获取类型显示文本
   */
  getGenreText(genre: string): string {
    const genreMap = {
      'fantasy': '奇幻',
      'romance': '言情',
      'mystery': '悬疑',
      'scifi': '科幻',
      'historical': '历史',
      'modern': '现代',
      'martial_arts': '武侠',
      'urban': '都市',
      'game': '游戏',
      'other': '其他'
    }
    return genreMap[genre as keyof typeof genreMap] || genre
  }
}

export default HomepageService