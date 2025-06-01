/**
 * 大纲管理API服务
 * Author: AI Writer Team
 * Created: 2025-06-01
 */

import apiClient from './index'

// ========== 类型定义 ==========

export type OutlineType = 'storyline' | 'character_growth' | 'major_event' | 'plot_point'

export interface RoughOutline {
  id?: number
  novel_id: number
  outline_type: OutlineType
  title: string
  content: string
  start_chapter?: number
  end_chapter?: number
  order_index: number
  user_id?: number
  created_at?: string
  updated_at?: string
}

export interface DetailedOutline {
  id?: number
  novel_id: number
  chapter_number: number
  chapter_title: string
  plot_points: string
  participating_characters: string[]
  entering_characters: string[]
  exiting_characters: string[]
  chapter_summary: string
  is_plot_end: boolean
  is_new_plot: boolean
  new_plot_summary?: string
  user_id?: number
  created_at?: string
  updated_at?: string
}

export interface RoughOutlineListResponse {
  items: RoughOutline[]
  total: number
}

export interface DetailedOutlineListResponse {
  items: DetailedOutline[]
  total: number
}

export interface RoughOutlineCreateRequest {
  novel_id: number
  outline_type: OutlineType
  title: string
  content: string
  start_chapter?: number
  end_chapter?: number
  order_index: number
}

export interface RoughOutlineUpdateRequest {
  outline_type?: OutlineType
  title?: string
  content?: string
  start_chapter?: number
  end_chapter?: number
  order_index?: number
}

export interface DetailedOutlineCreateRequest {
  novel_id: number
  chapter_number: number
  chapter_title: string
  plot_points: string
  participating_characters: string[]
  entering_characters: string[]
  exiting_characters: string[]
  chapter_summary: string
  is_plot_end: boolean
  is_new_plot: boolean
  new_plot_summary?: string
}

export interface DetailedOutlineUpdateRequest {
  chapter_number?: number
  chapter_title?: string
  plot_points?: string
  participating_characters?: string[]
  entering_characters?: string[]
  exiting_characters?: string[]
  chapter_summary?: string
  is_plot_end?: boolean
  is_new_plot?: boolean
  new_plot_summary?: string
}

export interface RoughOutlineGenerationRequest {
  novel_id: number
  outline_types: OutlineType[]
  user_suggestion?: string
  include_worldview: boolean
  include_novel_idea: boolean
}

export interface DetailedOutlineGenerationRequest {
  novel_id: number
  chapter_start: number
  chapter_end: number
  user_suggestion?: string
  include_worldview: boolean
  include_rough_outline: boolean
  include_characters: boolean
}

export interface OutlineGenerationResponse {
  success: boolean
  message: string
  rough_outlines: RoughOutline[]
  detailed_outlines: DetailedOutline[]
  total_generated: number
  generation_data?: any[]
}

export interface OutlineSummaryRequest {
  outline_id: number
  outline_type: 'rough' | 'detailed'
}

export interface OutlineSummaryResponse {
  success: boolean
  message: string
  summary: string
  outline_id: number
  outline_type: string
}

// ========== 粗略大纲 API ==========

/**
 * 获取小说的粗略大纲列表
 */
export const getRoughOutlinesByNovel = async (
  novelId: number,
  outlineType?: OutlineType
): Promise<RoughOutlineListResponse> => {
  const params = outlineType ? { outline_type: outlineType } : {}
  const response = await apiClient.get(`/outline/rough/novel/${novelId}`, { params })
  return response.data
}

/**
 * 获取粗略大纲详情
 */
export const getRoughOutline = async (outlineId: number): Promise<RoughOutline> => {
  const response = await apiClient.get(`/outline/rough/${outlineId}`)
  return response.data
}

/**
 * 创建粗略大纲
 */
export const createRoughOutline = async (data: RoughOutlineCreateRequest): Promise<RoughOutline> => {
  const response = await apiClient.post('/outline/rough', data)
  return response.data
}

/**
 * 更新粗略大纲
 */
export const updateRoughOutline = async (
  outlineId: number,
  data: RoughOutlineUpdateRequest
): Promise<RoughOutline> => {
  const response = await apiClient.put(`/outline/rough/${outlineId}`, data)
  return response.data
}

/**
 * 删除粗略大纲
 */
export const deleteRoughOutline = async (outlineId: number): Promise<{ message: string }> => {
  const response = await apiClient.delete(`/outline/rough/${outlineId}`)
  return response.data
}

// ========== 详细大纲 API ==========

/**
 * 获取小说的详细大纲列表
 */
export const getDetailedOutlinesByNovel = async (
  novelId: number,
  chapterStart?: number,
  chapterEnd?: number
): Promise<DetailedOutlineListResponse> => {
  const params: any = {}
  if (chapterStart !== undefined) params.chapter_start = chapterStart
  if (chapterEnd !== undefined) params.chapter_end = chapterEnd
  
  const response = await apiClient.get(`/outline/detailed/novel/${novelId}`, { params })
  return response.data
}

/**
 * 获取详细大纲详情
 */
export const getDetailedOutline = async (outlineId: number): Promise<DetailedOutline> => {
  const response = await apiClient.get(`/outline/detailed/${outlineId}`)
  return response.data
}

/**
 * 创建详细大纲
 */
export const createDetailedOutline = async (data: DetailedOutlineCreateRequest): Promise<DetailedOutline> => {
  const response = await apiClient.post('/outline/detailed', data)
  return response.data
}

/**
 * 更新详细大纲
 */
export const updateDetailedOutline = async (
  outlineId: number,
  data: DetailedOutlineUpdateRequest
): Promise<DetailedOutline> => {
  const response = await apiClient.put(`/outline/detailed/${outlineId}`, data)
  return response.data
}

/**
 * 删除详细大纲
 */
export const deleteDetailedOutline = async (outlineId: number): Promise<{ message: string }> => {
  const response = await apiClient.delete(`/outline/detailed/${outlineId}`)
  return response.data
}

// ========== 大纲生成 API ==========

/**
 * 生成粗略大纲
 */
export const generateRoughOutline = async (
  data: RoughOutlineGenerationRequest
): Promise<OutlineGenerationResponse> => {
  const response = await apiClient.post('/outline/generate/rough', data)
  return response.data
}

/**
 * 生成详细大纲
 */
export const generateDetailedOutline = async (
  data: DetailedOutlineGenerationRequest
): Promise<OutlineGenerationResponse> => {
  const response = await apiClient.post('/outline/generate/detailed', data)
  return response.data
}

/**
 * 生成大纲总结
 */
export const generateOutlineSummary = async (
  data: OutlineSummaryRequest
): Promise<OutlineSummaryResponse> => {
  const response = await apiClient.post('/outline/summary', data)
  return response.data
}