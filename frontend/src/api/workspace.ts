/**
 * 工作台相关API接口
 */
import apiClient from './index'

// TypeScript 类型定义
export interface NovelBasicInfo {
  id: number
  title: string
  description?: string
  genre: string
  status: string
  created_at: string
  updated_at: string
  last_activity?: string
  word_count?: number
  target_words?: number
}

export interface ModuleStats {
  total_count: number
  completed_count: number
  completion_percentage: number
  last_updated?: string
  status: 'empty' | 'partial' | 'complete'
  recent_items: RecentItem[]
  quick_stats: Record<string, any>
}

export interface ModuleOverview {
  worldview: ModuleStats
  characters: ModuleStats
  outline: ModuleStats
  chapters: ModuleStats
  timeline: ModuleStats
  settings: ModuleStats
}

export interface RecentItem {
  id: number
  title: string
  type: string
  updated_at: string
}

export interface ProgressOverview {
  overall_progress: number
  word_count: number
  target_words: number
  chapter_count: number
  completion_estimate?: string
  milestones: Milestone[]
}

export interface Milestone {
  id: string
  title: string
  description: string
  target_date: string
  completed: boolean
  progress: number
}

export interface WritingStats {
  writing_days: number
  total_sessions: number
  average_daily_words: number
  most_productive_day?: string
  writing_streak: number
  productivity_trend: 'increasing' | 'stable' | 'decreasing'
}

export interface Activity {
  id: string
  type: 'chapter_created' | 'character_added' | 'outline_updated' | 'worldview_modified'
  title: string
  description: string
  module: string
  entity_id?: string
  metadata: Record<string, any>
  timestamp: string
  word_count_change?: number
}

export interface QuickAction {
  id: string
  name: string
  description: string
  icon: string
  url: string
  enabled: boolean
  condition?: string
  badge?: string
  priority: number
}

export interface WorkspaceOverviewResponse {
  novel: NovelBasicInfo
  modules: ModuleOverview
  progress: ProgressOverview
  recent_activities: Activity[]
  writing_stats: WritingStats
  quick_actions: QuickAction[]
}

export interface RecentActivitiesResponse {
  activities: Activity[]
  total: number
}

export interface QuickActionsResponse {
  actions: QuickAction[]
  user_preferences: {
    pinned_actions: string[]
    hidden_actions: string[]
  }
}

export interface RecentChapterResponse {
  chapter?: {
    id: number
    title: string
    chapter_number: number
    word_count: number
    status: string
    updated_at: string
  }
  last_edit_position?: {
    paragraph: number
    character: number
  }
  editing_session?: {
    started_at: string
    word_count_start: number
    current_word_count: number
  }
}

/**
 * 工作台API服务类
 */
export class WorkspaceService {
  /**
   * 获取工作台概览数据
   */
  static async getOverview(novelId: number): Promise<WorkspaceOverviewResponse> {
    const response = await apiClient.get(`/workspace/${novelId}/overview`)
    return response.data
  }

  /**
   * 获取模块详细统计
   */
  static async getModuleStats(novelId: number, moduleName: string): Promise<ModuleStats> {
    const response = await apiClient.get(`/workspace/${novelId}/modules/${moduleName}/stats`)
    return response.data
  }

  /**
   * 获取最近活动
   */
  static async getRecentActivities(
    novelId: number,
    params?: { limit?: number; offset?: number }
  ): Promise<RecentActivitiesResponse> {
    const response = await apiClient.get(`/workspace/${novelId}/activities`, { params })
    return response.data
  }

  /**
   * 获取快捷操作配置
   */
  static async getQuickActions(novelId: number): Promise<QuickActionsResponse> {
    const response = await apiClient.get(`/workspace/${novelId}/quick-actions`)
    return response.data
  }

  /**
   * 获取最近编辑的章节
   */
  static async getRecentChapter(novelId: number): Promise<RecentChapterResponse> {
    const response = await apiClient.get(`/workspace/${novelId}/recent-chapter`)
    return response.data
  }

  /**
   * 获取写作统计数据
   */
  static async getWritingStats(novelId: number): Promise<WritingStats> {
    const response = await apiClient.get(`/workspace/${novelId}/writing-stats`)
    return response.data
  }

  /**
   * 执行快捷操作
   */
  static async executeQuickAction(
    novelId: number,
    actionId: string,
    parameters?: Record<string, any>
  ): Promise<{
    success: boolean
    result: any
    redirect_url?: string
    message?: string
  }> {
    const response = await apiClient.post(`/workspace/${novelId}/quick-actions/${actionId}/execute`, {
      parameters
    })
    return response.data
  }

  /**
   * 生成创作进度报告
   */
  static async generateProgressReport(
    novelId: number,
    options: {
      format: 'summary' | 'detailed' | 'visual'
      include_sections?: string[]
      date_range?: { start: string; end: string }
    }
  ): Promise<{
    report: any
    download_url?: string
    charts?: any[]
  }> {
    const response = await apiClient.post(`/workspace/${novelId}/progress-report`, options)
    return response.data
  }

  /**
   * 更新工作台设置
   */
  static async updateSettings(
    novelId: number,
    settings: {
      layout_preferences?: any
      notification_settings?: any
      writing_preferences?: any
      ai_assistant_settings?: any
    }
  ): Promise<{ success: boolean }> {
    const response = await apiClient.put(`/workspace/${novelId}/settings`, settings)
    return response.data
  }

  /**
   * 获取工作台设置
   */
  static async getSettings(novelId: number): Promise<{
    layout_preferences: any
    notification_settings: any
    writing_preferences: any
    ai_assistant_settings: any
  }> {
    const response = await apiClient.get(`/workspace/${novelId}/settings`)
    return response.data
  }
}

// 导出默认服务
export default WorkspaceService