/**
 * 小说管理API服务
 * Author: AI Writer Team
 * Created: 2025-06-01
 * Updated: 2025-06-01 - 添加"我的小说"页面所需接口
 */

import apiClient from './index'

// 小说状态枚举
export enum NovelStatus {
  DRAFT = 'draft',
  WRITING = 'writing',
  COMPLETED = 'completed',
  PUBLISHED = 'published',
  PAUSED = 'paused'
}

// 小说类型枚举
export enum NovelGenre {
  FANTASY = 'fantasy',
  ROMANCE = 'romance',
  MYSTERY = 'mystery',
  SCIFI = 'scifi',
  HISTORICAL = 'historical',
  MODERN = 'modern',
  MARTIAL_ARTS = 'martial_arts',
  URBAN = 'urban',
  GAME = 'game',
  OTHER = 'other'
}

// 小说列表项类型（用于我的小说页面）
export interface NovelListItem {
  id: number
  title: string
  description: string
  genre: string
  status: 'draft' | 'ongoing' | 'completed' | 'paused'
  cover_image?: string
  word_count: number
  chapter_count: number
  target_words?: number
  progress_percentage: number
  created_at: string
  updated_at: string
  last_chapter_title?: string
  last_edit_date?: string
}

// 小说数据类型定义
export interface Novel {
  id: number
  title: string
  description?: string
  genre: NovelGenre
  tags: string[]
  status: NovelStatus
  target_word_count?: number
  word_count: number
  user_id: number
  created_at: string
  updated_at: string
}

export interface NovelCreate {
  title: string
  description?: string
  genre: NovelGenre
  tags?: string[]
  target_word_count?: number
}

export interface NovelUpdate {
  title?: string
  description?: string
  genre?: NovelGenre
  tags?: string[]
  target_word_count?: number
  status?: NovelStatus
}

export interface NovelListResponse {
  novels: NovelListItem[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface NovelStats {
  total_novels: number
  total_word_count: number
  novels_by_status: Record<string, number>
  novels_by_genre: Record<string, number>
  average_word_count: number
}

export interface NovelSearchParams {
  page?: number
  page_size?: number
  search?: string
  genre?: string
  status?: string
  sort_by?: string
  sort_order?: string
  date_from?: string
  date_to?: string
}

// 批量操作相关类型
export interface BatchDeleteResponse {
  success_count: number
  failed_count: number
  failed_items: {
    novel_id: number
    reason: string
  }[]
  message: string
}

export interface BatchStatusUpdateResponse {
  success_count: number
  failed_count: number
  updated_novels: NovelListItem[]
}

// 导出相关类型
export interface ExportRequest {
  format: 'txt' | 'docx' | 'pdf'
  include_outline?: boolean
  include_worldview?: boolean
  include_characters?: boolean
  only_completed?: boolean
}

export interface ExportResponse {
  export_id: string
  download_url: string
  expires_at: string
  file_size: number
  estimated_time: number
}

export interface ExportStatusResponse {
  export_id: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  progress_percentage: number
  download_url?: string
  error_message?: string
  file_info?: {
    filename: string
    size: number
    format: string
  }
}

// 小说API服务类
export class NovelService {
  /**
   * 创建新小说
   */
  static async createNovel(novelData: NovelCreate): Promise<any> {
    const response = await apiClient.post('/novels', novelData)
    return response.data
  }

  /**
   * 获取小说列表 - 支持完整的筛选和排序参数
   */
  static async getNovels(params?: NovelSearchParams): Promise<any> {
    const response = await apiClient.get('/novels', { params })
    return response.data
  }

  /**
   * 获取小说详情
   */
  static async getNovel(novelId: number): Promise<Novel> {
    const response = await apiClient.get<Novel>(`/novels/${novelId}`)
    return response.data
  }

  /**
   * 更新小说信息
   */
  static async updateNovel(novelId: number, novelData: NovelUpdate): Promise<Novel> {
    const response = await apiClient.put<Novel>(`/novels/${novelId}`, novelData)
    return response.data
  }

  /**
   * 删除小说
   */
  static async deleteNovel(novelId: number): Promise<any> {
    const response = await apiClient.delete(`/novels/${novelId}`)
    return response.data
  }

  /**
   * 获取小说统计信息
   */
  static async getNovelStats(): Promise<NovelStats> {
    const response = await apiClient.get<NovelStats>('/novels/stats/overview')
    return response.data
  }

  /**
   * 更新小说状态
   */
  static async updateNovelStatus(novelId: number, status: NovelStatus): Promise<Novel> {
    const response = await apiClient.patch<Novel>(`/novels/${novelId}/status`, null, {
      params: { new_status: status }
    })
    return response.data
  }

  /**
   * 搜索小说
   */
  static async searchNovels(searchParams: NovelSearchParams): Promise<any> {
    return this.getNovels(searchParams)
  }

  // 批量操作方法
  /**
   * 批量删除小说
   */
  static async batchDeleteNovels(novelIds: number[]): Promise<any> {
    const response = await apiClient.post('/novels/batch/delete', novelIds)
    return response.data
  }

  /**
   * 批量修改状态
   */
  static async batchUpdateStatus(novelIds: number[], status: string): Promise<any> {
    const response = await apiClient.post('/novels/batch/status', {
      novel_ids: novelIds,
      new_status: status
    })
    return response.data
  }

  // 导出功能方法
  /**
   * 创建导出任务
   */
  static async exportNovel(novelId: number, options: ExportRequest): Promise<any> {
    const params = new URLSearchParams({
      export_format: options.format,
      include_outline: options.include_outline?.toString() || 'false',
      include_worldview: options.include_worldview?.toString() || 'false',
      include_characters: options.include_characters?.toString() || 'false',
      only_completed: options.only_completed?.toString() || 'false'
    })
    
    const response = await apiClient.post(`/novels/${novelId}/export?${params}`)
    return response.data
  }

  /**
   * 获取导出状态
   */
  static async getExportStatus(exportId: string): Promise<any> {
    const response = await apiClient.get(`/novels/export/${exportId}/status`)
    return response.data
  }

  /**
   * 批量导出小说
   */
  static async batchExportNovels(novelIds: number[], format: string): Promise<any> {
    const response = await apiClient.post('/novels/batch/export', {
      novel_ids: novelIds,
      format: format,
      export_options: {}
    })
    return response.data
  }
}

// 工具函数
export const NovelUtils = {
  /**
   * 获取状态显示文本
   */
  getStatusText(status: NovelStatus | string): string {
    const statusMap: Record<string, string> = {
      'draft': '草稿',
      'writing': '写作中',
      'ongoing': '进行中',
      'completed': '已完成',
      'published': '已发布',
      'paused': '暂停'
    }
    return statusMap[status] || status
  },

  /**
   * 获取类型显示文本
   */
  getGenreText(genre: NovelGenre | string): string {
    const genreMap: Record<string, string> = {
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
    return genreMap[genre] || genre
  },

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
    return date.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit'
    })
  },

  /**
   * 格式化相对时间显示
   */
  formatRelativeTime(dateString: string): string {
    const date = new Date(dateString)
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    
    const minutes = Math.floor(diff / (1000 * 60))
    const hours = Math.floor(diff / (1000 * 60 * 60))
    const days = Math.floor(diff / (1000 * 60 * 60 * 24))
    
    if (minutes < 1) return '刚刚'
    if (minutes < 60) return `${minutes}分钟前`
    if (hours < 24) return `${hours}小时前`
    if (days < 7) return `${days}天前`
    
    return this.formatDate(dateString)
  },

  /**
   * 获取状态对应的颜色
   */
  getStatusColor(status: NovelStatus | string): string {
    const colorMap: Record<string, string> = {
      'draft': '#909399',
      'writing': '#409EFF',
      'ongoing': '#E6A23C',
      'completed': '#67C23A',
      'published': '#E6A23C',
      'paused': '#F56C6C'
    }
    return colorMap[status] || '#909399'
  },

  /**
   * 计算进度条颜色
   */
  getProgressColor(percentage: number): string {
    if (percentage >= 100) return '#67C23A'
    if (percentage >= 75) return '#409EFF'
    if (percentage >= 50) return '#E6A23C'
    return '#F56C6C'
  },

  /**
   * 格式化进度百分比
   */
  formatProgress(percentage: number): string {
    return `${Math.round(percentage)}%`
  }
}

export default NovelService