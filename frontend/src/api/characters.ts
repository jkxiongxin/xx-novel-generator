/**
 * 角色管理API服务
 * Author: AI Writer Team
 * Created: 2025-06-01
 */

import apiClient from './index'

// ========== 类型定义 ==========

export interface Character {
  id?: number
  name: string
  gender: 'male' | 'female' | 'unknown' | 'other'
  personality: string
  character_type: 'protagonist' | 'supporting' | 'antagonist' | 'minor'
  tags: string[]
  description?: string
  abilities?: string
  novel_id?: number
  worldview_id?: number
  faction_id?: number
  is_template: boolean
  power_system?: string
  original_world?: string
  created_at?: string
  updated_at?: string
}

export interface CharacterSummary {
  id: number
  name: string
  character_type: string
  gender: string
  tags: string[]
  is_template: boolean
  novel_id?: number
}

export interface CharacterListResponse {
  items: CharacterSummary[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface CharacterCreateRequest {
  name: string
  gender: 'male' | 'female' | 'unknown' | 'other'
  personality: string
  character_type: 'protagonist' | 'supporting' | 'antagonist' | 'minor'
  tags: string[]
  description?: string
  abilities?: string
  novel_id?: number
  worldview_id?: number
  faction_id?: number
  is_template: boolean
  power_system?: string
  original_world?: string
}

export interface CharacterUpdateRequest {
  name?: string
  gender?: 'male' | 'female' | 'unknown' | 'other'
  personality?: string
  character_type?: 'protagonist' | 'supporting' | 'antagonist' | 'minor'
  tags?: string[]
  description?: string
  abilities?: string
  novel_id?: number
  worldview_id?: number
  faction_id?: number
  is_template?: boolean
  power_system?: string
  original_world?: string
}

export interface CharacterGenerationRequest {
  novel_id: number
  character_type?: string
  character_count: number
  user_suggestion?: string
  include_worldview: boolean
  worldview_id?: number
}

export interface CharacterGenerationResponse {
  success: boolean
  message: string
  characters: Character[]
  total_generated: number
  generation_data?: any[]
}

export interface CharacterBatchAddRequest {
  novel_id: number
  character_ids: number[]
}

export interface CharacterBatchAddResponse {
  success: boolean
  message: string
  added_count: number
  failed_count: number
  added_characters: Character[]
}

// ========== API接口 ==========

/**
 * 获取角色列表
 */
export const getCharacters = async (params: {
  novel_id?: number
  character_type?: string
  gender?: string
  is_template?: boolean
  search?: string
  page?: number
  page_size?: number
}): Promise<CharacterListResponse> => {
  const response = await apiClient.get('/characters', { params })
  return response.data
}

/**
 * 获取角色详情
 */
export const getCharacter = async (characterId: number): Promise<Character> => {
  const response = await apiClient.get(`/characters/${characterId}`)
  return response.data
}

/**
 * 创建角色
 */
export const createCharacter = async (data: CharacterCreateRequest): Promise<Character> => {
  const response = await apiClient.post('/characters', data)
  return response.data
}

/**
 * 更新角色
 */
export const updateCharacter = async (
  characterId: number, 
  data: CharacterUpdateRequest
): Promise<Character> => {
  const response = await apiClient.put(`/characters/${characterId}`, data)
  return response.data
}

/**
 * 删除角色
 */
export const deleteCharacter = async (characterId: number): Promise<{ message: string }> => {
  const response = await apiClient.delete(`/characters/${characterId}`)
  return response.data
}

/**
 * 获取角色模板列表
 */
export const getCharacterTemplates = async (params: {
  character_type?: string
  gender?: string
  power_system?: string
  original_world?: string
  tags?: string[]
  search?: string
  page?: number
  page_size?: number
}): Promise<CharacterListResponse> => {
  const response = await apiClient.get('/characters/templates', { params })
  return response.data
}

/**
 * 批量添加角色到小说
 */
export const batchAddCharacters = async (
  data: CharacterBatchAddRequest
): Promise<CharacterBatchAddResponse> => {
  const response = await apiClient.post('/characters/batch-add', data)
  return response.data
}

/**
 * AI生成角色
 */
export const generateCharacters = async (
  data: CharacterGenerationRequest
): Promise<CharacterGenerationResponse> => {
  const response = await apiClient.post('/characters/generate', data)
  return response.data
}