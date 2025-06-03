/**
 * 管理员角色模板管理API
 * Author: AI Assistant
 * Created: 2025-06-03
 */

import apiClient from './index'

// === 类型定义 ===

export interface CharacterTemplateCreateRequest {
  name: string
  gender: string
  personality?: string
  character_type: string
  tags: string[]
  description?: string
  abilities?: string
  power_system?: string
  original_world?: string
  template_detail?: TemplateDetailBase
}

export interface CharacterTemplateUpdateRequest {
  name?: string
  gender?: string
  personality?: string
  character_type?: string
  tags?: string[]
  description?: string
  abilities?: string
  power_system?: string
  original_world?: string
  template_detail?: TemplateDetailBase
}

export interface TemplateDetailBase {
  detailed_description?: string
  background_story?: string
  relationships?: string
  strengths: string[]
  weaknesses: string[]
  motivation?: string
  character_arc?: string
  dialogue_style?: string
  appearance?: AppearanceDetail
  combat_style?: string
  equipment: string[]
  special_abilities: string[]
}

export interface AppearanceDetail {
  height?: string
  build?: string
  hair?: string
  eyes?: string
  distinctive_features?: string
  other?: Record<string, string>
}

export interface CharacterTemplateResponse {
  id: number
  name: string
  gender: string
  personality?: string
  character_type: string
  tags: string[]
  description?: string
  abilities?: string
  power_system?: string
  original_world?: string
  is_template: boolean
  created_at: string
  updated_at: string
  user_id: number
  template_detail?: TemplateDetailResponse
  usage_examples: UsageExampleResponse[]
  is_favorited?: boolean
}

export interface TemplateDetailResponse extends TemplateDetailBase {
  id: number
  character_id: number
  usage_count: number
  rating: number
  is_popular: boolean
  is_new: boolean
  created_at: string
  updated_at: string
}

export interface UsageExampleResponse {
  id: number
  template_detail_id: number
  novel_genre: string
  usage_context: string
  adaptation_notes?: string
  created_at: string
  updated_at: string
}

export interface CharacterTemplateCreateResponse {
  success: boolean
  template: CharacterTemplateResponse
  message: string
}

export interface CharacterTemplateUpdateResponse {
  success: boolean
  template: CharacterTemplateResponse
  message: string
}

export interface CharacterTemplateDeleteResponse {
  success: boolean
  template_id: number
  message: string
}

export interface AdminTemplateListResponse {
  templates: CharacterTemplateResponse[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface TemplateStatusUpdateRequest {
  is_popular?: boolean
  is_new?: boolean
  rating?: number
}

export interface BatchTemplateStatusUpdateRequest {
  template_ids: number[]
  status_updates: TemplateStatusUpdateRequest
}

export interface BatchTemplateStatusUpdateResponse {
  success_count: number
  failed_count: number
  failed_items: Array<{
    template_id: number
    reason: string
  }>
  message: string
}

export interface UsageExampleCreate {
  template_detail_id: number
  novel_genre: string
  usage_context: string
  adaptation_notes?: string
}

export interface AdminTemplateSearchParams {
  page?: number
  page_size?: number
  search?: string
  gender?: string
  character_type?: string
  is_popular?: boolean
  is_new?: boolean
  sort_by?: string
  sort_order?: string
}

// === API调用函数 ===

/**
 * 创建角色模板
 */
export const createCharacterTemplate = async (
  data: CharacterTemplateCreateRequest
): Promise<CharacterTemplateCreateResponse> => {
  const response = await apiClient.post('/admin/character-templates', data)
  return response.data
}

/**
 * 更新角色模板
 */
export const updateCharacterTemplate = async (
  templateId: number,
  data: CharacterTemplateUpdateRequest
): Promise<CharacterTemplateUpdateResponse> => {
  const response = await apiClient.put(`/admin/character-templates/${templateId}`, data)
  return response.data
}

/**
 * 删除角色模板
 */
export const deleteCharacterTemplate = async (
  templateId: number
): Promise<CharacterTemplateDeleteResponse> => {
  const response = await apiClient.delete(`/admin/character-templates/${templateId}`)
  return response.data
}

/**
 * 获取管理员模板列表
 */
export const getAdminTemplateList = async (
  params?: AdminTemplateSearchParams
): Promise<AdminTemplateListResponse> => {
  const response = await apiClient.get('/admin/character-templates', { params })
  return response.data
}

/**
 * 更新模板状态
 */
export const updateTemplateStatus = async (
  templateId: number,
  data: TemplateStatusUpdateRequest
): Promise<CharacterTemplateUpdateResponse> => {
  const response = await apiClient.patch(`/admin/character-templates/${templateId}/status`, data)
  return response.data
}

/**
 * 批量更新模板状态
 */
export const batchUpdateTemplateStatus = async (
  data: BatchTemplateStatusUpdateRequest
): Promise<BatchTemplateStatusUpdateResponse> => {
  const response = await apiClient.patch('/admin/character-templates/batch/status', data)
  return response.data
}

/**
 * 为模板添加使用示例
 */
export const createUsageExample = async (
  templateId: number,
  data: UsageExampleCreate
): Promise<UsageExampleResponse> => {
  const response = await apiClient.post(`/admin/character-templates/${templateId}/usage-examples`, data)
  return response.data
}

// === 默认导出服务类 ===

export class AdminCharacterTemplateService {
  /**
   * 创建角色模板
   */
  static async create(data: CharacterTemplateCreateRequest): Promise<CharacterTemplateCreateResponse> {
    return createCharacterTemplate(data)
  }

  /**
   * 更新角色模板
   */
  static async update(
    templateId: number,
    data: CharacterTemplateUpdateRequest
  ): Promise<CharacterTemplateUpdateResponse> {
    return updateCharacterTemplate(templateId, data)
  }

  /**
   * 删除角色模板
   */
  static async delete(templateId: number): Promise<CharacterTemplateDeleteResponse> {
    return deleteCharacterTemplate(templateId)
  }

  /**
   * 获取管理员模板列表
   */
  static async getList(params?: AdminTemplateSearchParams): Promise<AdminTemplateListResponse> {
    return getAdminTemplateList(params)
  }

  /**
   * 更新模板状态
   */
  static async updateStatus(
    templateId: number,
    data: TemplateStatusUpdateRequest
  ): Promise<CharacterTemplateUpdateResponse> {
    return updateTemplateStatus(templateId, data)
  }

  /**
   * 批量更新模板状态
   */
  static async batchUpdateStatus(
    data: BatchTemplateStatusUpdateRequest
  ): Promise<BatchTemplateStatusUpdateResponse> {
    return batchUpdateTemplateStatus(data)
  }

  /**
   * 为模板添加使用示例
   */
  static async createUsageExample(
    templateId: number,
    data: UsageExampleCreate
  ): Promise<UsageExampleResponse> {
    return createUsageExample(templateId, data)
  }
}

export default AdminCharacterTemplateService