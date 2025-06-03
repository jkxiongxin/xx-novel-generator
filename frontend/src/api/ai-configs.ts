/**
 * AI模型配置管理API客户端
 * Author: AI Writer Team
 * Created: 2025-06-02
 * Updated: 2025-06-02 - 重构为统一API客户端模式
 */

import apiClient from './index'

// 类型定义
export interface AIModelConfig {
  id: number
  name: string
  description?: string
  model_type: ModelType
  is_active: boolean
  is_default: boolean
  group_name?: string
  group_description?: string
  is_group_default: boolean
  api_endpoint: string
  api_key?: string
  model_name: string
  request_format: RequestFormat
  max_tokens: number
  temperature: string
  timeout: number
  retry_count: number
  request_headers?: Record<string, string>
  request_params?: Record<string, any>
  response_mapping?: Record<string, string>
  prompt_template?: string
  system_message?: string
  daily_limit?: number
  monthly_limit?: number
  priority: number
  user_id: number
  created_at: string
  updated_at: string
}

export type ModelType = 
  | 'openai_compatible'
  | 'custom_http'
  | 'claude_compatible'
  | 'hugging_face'
  | 'ollama'
  | 'openrouter'

export type RequestFormat = 
  | 'openai_chat'
  | 'openai_completion'
  | 'claude_messages'
  | 'custom_json'
  | 'rest_api'

export interface AIModelConfigCreate {
  name: string
  description?: string
  model_type: ModelType
  is_active?: boolean
  is_default?: boolean
  group_name?: string
  group_description?: string
  is_group_default?: boolean
  api_endpoint: string
  api_key?: string
  model_name: string
  request_format: RequestFormat
  max_tokens?: number
  temperature?: string
  timeout?: number
  retry_count?: number
  request_headers?: Record<string, string>
  request_params?: Record<string, any>
  response_mapping?: Record<string, string>
  prompt_template?: string
  system_message?: string
  daily_limit?: number
  monthly_limit?: number
  priority?: number
}

export interface AIModelConfigUpdate extends Partial<AIModelConfigCreate> {}

export interface AIModelConfigListResponse {
  items: AIModelConfig[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface AIModelConfigStats {
  total_configs: number
  active_configs: number
  inactive_configs: number
  model_types: Record<string, number>
  request_formats: Record<string, number>
  default_config_id?: number
}

export interface AIModelConfigTemplate {
  name: string
  description: string
  model_type: ModelType
  request_format: RequestFormat
  default_config: AIModelConfigCreate
}

export interface AIModelGroup {
  group_name: string
  group_description?: string
  model_count: number
  active_count: number
  default_config_id?: number
  configs: AIModelConfig[]
}

export interface AIModelGroupListResponse {
  groups: AIModelGroup[]
  total_groups: number
  total_configs: number
}

export interface AIModelGroupStats {
  group_name: string
  group_description?: string
  total_configs: number
  active_configs: number
  model_types: Record<string, number>
  default_config?: AIModelConfig
}

export interface TestConfigRequest {
  prompt: string
  max_tokens?: number
  temperature?: string
}

export interface TestConfigResponse {
  success: boolean
  response_time: number
  content?: string
  error?: string
  usage?: Record<string, any>
}

export interface BatchOperationRequest {
  config_ids: number[]
  action: 'activate' | 'deactivate' | 'delete'
}

export interface AvailableGroup {
  name: string
  description: string
  priority: number
  suggested_models: string[]
}

// 常量定义
export const MODEL_TYPE_LABELS: Record<ModelType, string> = {
  openai_compatible: 'OpenAI兼容',
  custom_http: '自定义HTTP',
  claude_compatible: 'Claude兼容',
  hugging_face: 'HuggingFace',
  ollama: 'Ollama本地',
  openrouter: 'OpenRouter'
}

export const REQUEST_FORMAT_LABELS: Record<RequestFormat, string> = {
  openai_chat: 'OpenAI Chat',
  openai_completion: 'OpenAI Completion',
  claude_messages: 'Claude Messages',
  custom_json: '自定义JSON',
  rest_api: 'REST API'
}

export const DEFAULT_CONFIG: Partial<AIModelConfigCreate> = {
  is_active: true,
  is_default: false,
  is_group_default: false,
  max_tokens: 2000,
  temperature: '0.7',
  timeout: 60,
  retry_count: 3,
  priority: 5
}

export const PRESET_ENDPOINTS: Record<string, string> = {
  'OpenAI官方': 'https://api.openai.com/v1/chat/completions',
  'Claude官方': 'https://api.anthropic.com/v1/messages',
  'Ollama本地': 'http://localhost:11434/v1/chat/completions',
  '自定义': ''
}

export const COMMON_MODELS: Record<ModelType, string[]> & Record<string, string[]> = {
  openai_compatible: ['gpt-3.5-turbo', 'gpt-4', 'gpt-4-turbo'],
  claude_compatible: ['claude-3-sonnet-20240229', 'claude-3-opus-20240229', 'claude-3-haiku-20240307'],
  ollama: ['llama2', 'mistral', 'codellama', 'vicuna'],
  custom_http: [],
  hugging_face: [],
  openrouter: [],
  // 兼容旧的键名
  OPENAI: ['gpt-3.5-turbo', 'gpt-4', 'gpt-4-turbo'],
  CLAUDE: ['claude-3-sonnet-20240229', 'claude-3-opus-20240229', 'claude-3-haiku-20240307'],
  OLLAMA: ['llama2', 'mistral', 'codellama', 'vicuna']
}

// 统一API服务 - 使用函数式API而非类
export const aiConfigsApi = {
  // 基础CRUD操作
  async createConfig(data: AIModelConfigCreate): Promise<AIModelConfig> {
    const response = await apiClient.post('/ai-configs', data)
    return response.data
  },

  async getConfigs(params?: {
    page?: number
    page_size?: number
    search?: string
    model_type?: ModelType
    is_active?: boolean
  }): Promise<AIModelConfigListResponse> {
    const response = await apiClient.get('/ai-configs', { params })
    return response.data
  },

  async getConfig(id: number): Promise<AIModelConfig> {
    const response = await apiClient.get(`/ai-configs/${id}`)
    return response.data
  },

  async updateConfig(id: number, data: AIModelConfigUpdate): Promise<AIModelConfig> {
    const response = await apiClient.put(`/ai-configs/${id}`, data)
    return response.data
  },

  async deleteConfig(id: number): Promise<{ success: boolean; message: string }> {
    const response = await apiClient.delete(`/ai-configs/${id}`)
    return response.data
  },

  // 配置管理操作
  async toggleConfig(id: number): Promise<AIModelConfig> {
    const response = await apiClient.patch(`/ai-configs/${id}/toggle`)
    return response.data
  },

  async setDefaultConfig(id: number): Promise<AIModelConfig> {
    const response = await apiClient.patch(`/ai-configs/${id}/set-default`)
    return response.data
  },

  async setGroupDefaultConfig(id: number): Promise<AIModelConfig> {
    const response = await apiClient.patch(`/ai-configs/${id}/set-group-default`)
    return response.data
  },

  async testConfig(id: number, testData: TestConfigRequest): Promise<TestConfigResponse> {
    const response = await apiClient.post(`/ai-configs/${id}/test`, testData)
    return response.data
  },

  async batchOperation(data: BatchOperationRequest): Promise<{
    success: boolean
    message: string
    affected_count: number
  }> {
    const response = await apiClient.post('/ai-configs/batch', data)
    return response.data
  },

  // 统计信息
  async getStats(): Promise<AIModelConfigStats> {
    const response = await apiClient.get('/ai-configs/stats/overview')
    return response.data
  },

  // 模板操作
  async getTemplates(): Promise<AIModelConfigTemplate[]> {
    const response = await apiClient.get('/ai-configs/templates/list')
    return response.data
  },

  async createFromTemplate(templateName: string, apiKey?: string): Promise<AIModelConfig> {
    const response = await apiClient.post(
      `/ai-configs/templates/${templateName}`,
      apiKey ? { api_key: apiKey } : {}
    )
    return response.data
  },

  // 分组操作
  async getGroups(): Promise<AIModelGroupListResponse> {
    const response = await apiClient.get('/ai-configs/groups/list')
    return response.data
  },

  async getGroupStats(groupName: string): Promise<AIModelGroupStats> {
    const response = await apiClient.get(`/ai-configs/groups/${groupName}/stats`)
    return response.data
  },

  async getAvailableGroups(): Promise<{
    success: boolean
    data: AvailableGroup[]
    message: string
  }> {
    const response = await apiClient.get('/ai-configs/groups/available')
    return response.data
  }
}

// 便捷方法导出（保持向后兼容）
export const aiConfigs = {
  // 基础操作
  create: aiConfigsApi.createConfig,
  list: aiConfigsApi.getConfigs,
  get: aiConfigsApi.getConfig,
  update: aiConfigsApi.updateConfig,
  delete: aiConfigsApi.deleteConfig,

  // 配置管理
  toggle: aiConfigsApi.toggleConfig,
  setDefault: aiConfigsApi.setDefaultConfig,
  setGroupDefault: aiConfigsApi.setGroupDefaultConfig,
  test: aiConfigsApi.testConfig,
  batchOperation: aiConfigsApi.batchOperation,

  // 统计和模板
  getStats: aiConfigsApi.getStats,
  getTemplates: aiConfigsApi.getTemplates,
  createFromTemplate: aiConfigsApi.createFromTemplate,

  // 分组操作
  getGroups: aiConfigsApi.getGroups,
  getGroupStats: aiConfigsApi.getGroupStats,
  getAvailableGroups: aiConfigsApi.getAvailableGroups,
}

// 默认导出
export default aiConfigsApi