/**
 * 小说管理API服务
 * Author: AI Writer Team
 * Created: 2025-06-01
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
  novels: Novel[]
  total: number
  page: number
  size: number
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
  size?: number
  keyword?: string
  genre?: NovelGenre
  status?: NovelStatus
  sort_by?: string
  sort_order?: string
}

// 小说API服务类
export class NovelService {
  /**
   * 创建新小说
   */
  static async createNovel(novelData: NovelCreate): Promise<Novel> {
    const response = await apiClient.post<Novel>('/novels', novelData)
    return response.data
  }

  /**
   * 获取小说列表
   */
  static async getNovels(params?: NovelSearchParams): Promise<NovelListResponse> {
    const response = await apiClient.get<NovelListResponse>('/novels', { params })
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
  static async deleteNovel(novelId: number): Promise<{ message: string }> {
    const response = await apiClient.delete<{ message: string }>(`/novels/${novelId}`)
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
  static async searchNovels(searchParams: NovelSearchParams): Promise<NovelListResponse> {
    return this.getNovels(searchParams)
  }
}

// 工具函数
export const NovelUtils = {
  /**
   * 获取状态显示文本
   */
  getStatusText(status: NovelStatus): string {
    const statusMap = {
      [NovelStatus.DRAFT]: '草稿',
      [NovelStatus.WRITING]: '写作中',
      [NovelStatus.COMPLETED]: '已完成',
      [NovelStatus.PUBLISHED]: '已发布',
      [NovelStatus.PAUSED]: '暂停'
    }
    return statusMap[status] || status
  },

  /**
   * 获取类型显示文本
   */
  getGenreText(genre: NovelGenre): string {
    const genreMap = {
      [NovelGenre.FANTASY]: '奇幻',
      [NovelGenre.ROMANCE]: '言情',
      [NovelGenre.MYSTERY]: '悬疑',
      [NovelGenre.SCIFI]: '科幻',
      [NovelGenre.HISTORICAL]: '历史',
      [NovelGenre.MODERN]: '现代',
      [NovelGenre.MARTIAL_ARTS]: '武侠',
      [NovelGenre.URBAN]: '都市',
      [NovelGenre.GAME]: '游戏',
      [NovelGenre.OTHER]: '其他'
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
   * 获取状态对应的颜色
   */
  getStatusColor(status: NovelStatus): string {
    const colorMap = {
      [NovelStatus.DRAFT]: '#909399',
      [NovelStatus.WRITING]: '#409EFF',
      [NovelStatus.COMPLETED]: '#67C23A',
      [NovelStatus.PUBLISHED]: '#E6A23C',
      [NovelStatus.PAUSED]: '#F56C6C'
    }
    return colorMap[status] || '#909399'
  }
}

export default NovelService