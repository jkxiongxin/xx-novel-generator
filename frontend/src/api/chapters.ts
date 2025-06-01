/**
 * 章节管理API服务
 * Author: AI Writer Team
 * Created: 2025-06-01
 */

import apiClient from './index'

// ========== 类型定义 ==========

export interface Chapter {
  id?: number
  novel_id: number
  title: string
  content: string
  chapter_number: number
  word_count: number
  status: ChapterStatus
  outline_id?: number
  character_ids: number[]
  version: number
  notes?: string
  user_id?: number
  created_at?: string
  updated_at?: string
}

export enum ChapterStatus {
  DRAFT = 'draft',
  COMPLETED = 'completed',
  PUBLISHED = 'published'
}

export interface ChapterSummary {
  id: number
  novel_id: number
  title: string
  chapter_number: number
  word_count: number
  status: ChapterStatus
  version: number
  outline_id?: number
  character_count: number
  created_at: string
  updated_at: string
}

export interface ChapterListResponse {
  items: ChapterSummary[]
  total: number
  page: number
  page_size: number
  total_pages: number
  total_words: number
}

export interface ChapterCreateRequest {
  novel_id: number
  title: string
  content?: string
  chapter_number: number
  status?: ChapterStatus
  outline_id?: number
  character_ids?: number[]
  notes?: string
}

export interface ChapterUpdateRequest {
  title?: string
  content?: string
  chapter_number?: number
  status?: ChapterStatus
  outline_id?: number
  character_ids?: number[]
  notes?: string
}

export interface ChapterGenerationRequest {
  novel_id: number
  chapter_number: number
  prompt_template?: string
  target_word_count?: number
  generation_mode?: 'create' | 'continue' | 'rewrite'
  outline_id?: number
  character_ids?: number[]
  user_suggestion?: string
  include_worldview?: boolean
  include_characters?: boolean
  include_outline?: boolean
  generation_params?: {
    temperature?: number
    max_tokens?: number
  }
}

export interface ChapterGenerationResponse {
  success: boolean
  message: string
  chapter?: Chapter
  generated_content?: string
  used_prompt_template?: string
  generation_data?: any
  word_count?: number
}

export interface ChapterFilterRequest {
  novel_id?: number
  status?: ChapterStatus
  chapter_number_start?: number
  chapter_number_end?: number
  keyword?: string
  sort_by?: string
  sort_order?: 'asc' | 'desc'
}

export interface ChapterBatchRequest {
  chapter_ids: number[]
  operation: 'update_status' | 'delete' | 'update_outline' | 'add_characters' | 'remove_characters'
  operation_data?: any
}

export interface ChapterBatchResponse {
  success: boolean
  message: string
  processed_count: number
  failed_count: number
  failed_ids: number[]
  results: Array<{
    chapter_id: number
    operation: string
    success: boolean
    message: string
  }>
}

export interface ChapterStatsResponse {
  total_chapters: number
  draft_count: number
  completed_count: number
  published_count: number
  total_words: number
  average_words: number
  latest_chapter?: ChapterSummary
  chapter_distribution: {
    by_status: {
      draft: number
      completed: number
      published: number
    }
    by_word_count: {
      [key: string]: number
    }
  }
}

// ========== API接口 ==========

/**
 * 获取章节列表
 */
export const getChapters = async (params: {
  novel_id?: number
  page?: number
  size?: number
  status?: ChapterStatus
  chapter_number_start?: number
  chapter_number_end?: number
  keyword?: string
  sort_by?: string
  sort_order?: string
}): Promise<ChapterListResponse> => {
  const response = await apiClient.get('/chapters', { params })
  return response.data
}

/**
 * 获取章节详情
 */
export const getChapter = async (chapterId: number): Promise<Chapter> => {
  const response = await apiClient.get(`/chapters/${chapterId}`)
  return response.data
}

/**
 * 创建章节
 */
export const createChapter = async (data: ChapterCreateRequest): Promise<Chapter> => {
  const response = await apiClient.post('/chapters', data)
  return response.data
}

/**
 * 更新章节
 */
export const updateChapter = async (
  chapterId: number, 
  data: ChapterUpdateRequest
): Promise<Chapter> => {
  const response = await apiClient.put(`/chapters/${chapterId}`, data)
  return response.data
}

/**
 * 删除章节
 */
export const deleteChapter = async (chapterId: number): Promise<{ message: string }> => {
  const response = await apiClient.delete(`/chapters/${chapterId}`)
  return response.data
}

/**
 * 更新章节状态
 */
export const updateChapterStatus = async (
  chapterId: number,
  status: ChapterStatus
): Promise<Chapter> => {
  const response = await apiClient.patch(`/chapters/${chapterId}/status`, null, {
    params: { new_status: status }
  })
  return response.data
}

/**
 * AI生成章节
 */
export const generateChapter = async (
  data: ChapterGenerationRequest
): Promise<ChapterGenerationResponse> => {
  const response = await apiClient.post('/chapters/generate', data)
  return response.data
}

/**
 * 批量操作章节
 */
export const batchOperateChapters = async (
  data: ChapterBatchRequest
): Promise<ChapterBatchResponse> => {
  const response = await apiClient.post('/chapters/batch', data)
  return response.data
}

/**
 * 获取章节统计
 */
export const getChapterStats = async (novelId: number): Promise<ChapterStatsResponse> => {
  const response = await apiClient.get(`/chapters/stats/${novelId}`)
  return response.data
}

/**
 * 自动保存章节内容
 */
export const autoSaveChapter = async (
  chapterId: number,
  content: string
): Promise<Chapter> => {
  const response = await apiClient.put(`/chapters/${chapterId}`, {
    content,
    notes: `自动保存于 ${new Date().toLocaleString()}`
  })
  return response.data
}