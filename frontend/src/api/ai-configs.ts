/**
 * AI模型配置管理API
 * Author: AI Writer Team
 * Created: 2025-06-01
 */

import apiClient from './index'

// AI模型配置相关的类型定义
export interface AIModelConfig {
  id: number
  name: string
  description?: string
  model_type: 'openai_compatible' | 'claude_compatible' | 'custom_http' | 'hugging_face' | 'ollama' | 'openrouter'
  is_active: boolean
  is_default: boolean
  api_endpoint: string
  api_key?: string
  model_name: string
  request_format: 'openai_chat' | 'claude_messages' | 'custom_json' | 'rest_api'
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
  updating?: boolean // 前端临时状态属性
}

export interface AIModelConfigCreate {
  name: string
  description?: string
  model_type: string
  is_active?: boolean
  is_default?: boolean
  api_endpoint: string
  api_key?: string
  model_name: string
  request_format: string
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

export interface AIModelConfigUpdate {
  name?: string
  description?: string
  model_type?: string
  is_active?: boolean
  is_default?: boolean
  api_endpoint?: string
  api_key?: string
  model_name?: string
  request_format?: string
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

export interface AIModelConfigListResponse {
  items: AIModelConfig[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface AIModelConfigTestRequest {
  prompt: string
  max_tokens?: number
  temperature?: string
}

export interface AIModelConfigTestResponse {
  success: boolean
  response_time: number
  content?: string
  error?: string
  usage?: Record<string, any>
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
  model_type: string
  request_format: string
  default_config: AIModelConfigCreate
}

// AI配置管理API
export const aiConfigsApi = {
  // 获取AI配置列表
  async getConfigs(params: {
    page?: number
    page_size?: number
    search?: string
    model_type?: string
    is_active?: boolean
  } = {}): Promise<AIModelConfigListResponse> {
    const response = await apiClient.get('/ai-configs/', { params })
    return response.data
  },

  // 获取AI配置详情
  async getConfig(configId: number): Promise<AIModelConfig> {
    const response = await apiClient.get(`/ai-configs/${configId}`)
    return response.data
  },

  // 创建AI配置
  async createConfig(data: AIModelConfigCreate): Promise<AIModelConfig> {
    const response = await apiClient.post('/ai-configs/', data)
    return response.data
  },

  // 更新AI配置
  async updateConfig(configId: number, data: AIModelConfigUpdate): Promise<AIModelConfig> {
    const response = await apiClient.put(`/ai-configs/${configId}`, data)
    return response.data
  },

  // 删除AI配置
  async deleteConfig(configId: number): Promise<{ success: boolean; message: string }> {
    const response = await apiClient.delete(`/ai-configs/${configId}`)
    return response.data
  },

  // 测试AI配置
  async testConfig(configId: number, testData: AIModelConfigTestRequest): Promise<AIModelConfigTestResponse> {
    const response = await apiClient.post(`/ai-configs/${configId}/test`, testData)
    return response.data
  },

  // 切换AI配置状态
  async toggleConfig(configId: number): Promise<AIModelConfig> {
    const response = await apiClient.patch(`/ai-configs/${configId}/toggle`)
    return response.data
  },

  // 设置默认AI配置
  async setDefaultConfig(configId: number): Promise<AIModelConfig> {
    const response = await apiClient.patch(`/ai-configs/${configId}/set-default`)
    return response.data
  },

  // 批量操作AI配置
  async batchOperation(data: {
    config_ids: number[]
    action: 'activate' | 'deactivate' | 'delete'
  }): Promise<{ success: boolean; message: string; affected_count: number }> {
    const response = await apiClient.post('/ai-configs/batch', data)
    return response.data
  },

  // 获取AI配置统计
  async getStats(): Promise<AIModelConfigStats> {
    const response = await apiClient.get('/ai-configs/stats/overview')
    return response.data
  },

  // 获取配置模板
  async getTemplates(): Promise<AIModelConfigTemplate[]> {
    const response = await apiClient.get('/ai-configs/templates/list')
    return response.data
  },

  // 从模板创建配置
  async createFromTemplate(templateName: string, apiKey?: string): Promise<AIModelConfig> {
    const response = await apiClient.post(`/ai-configs/templates/${templateName}`, {
      api_key: apiKey
    })
    return response.data
  }
}

// 导出模型类型常量
export const MODEL_TYPES = {
  OPENAI_COMPATIBLE: 'openai_compatible',
  CLAUDE_COMPATIBLE: 'claude_compatible', 
  CUSTOM_HTTP: 'custom_http',
  HUGGING_FACE: 'hugging_face',
  OLLAMA: 'ollama',
  OPENROUTER: 'openrouter'
} as const

export const REQUEST_FORMATS = {
  OPENAI_CHAT: 'openai_chat',
  CLAUDE_MESSAGES: 'claude_messages',
  CUSTOM_JSON: 'custom_json',
  REST_API: 'rest_api'
} as const

// 模型类型显示名称
export const MODEL_TYPE_LABELS = {
  [MODEL_TYPES.OPENAI_COMPATIBLE]: 'OpenAI 兼容',
  [MODEL_TYPES.CLAUDE_COMPATIBLE]: 'Claude 兼容',
  [MODEL_TYPES.CUSTOM_HTTP]: '自定义 HTTP',
  [MODEL_TYPES.HUGGING_FACE]: 'HuggingFace',
  [MODEL_TYPES.OLLAMA]: 'Ollama',
  [MODEL_TYPES.OPENROUTER]: 'OpenRouter'
} as const

// 请求格式显示名称
export const REQUEST_FORMAT_LABELS = {
  [REQUEST_FORMATS.OPENAI_CHAT]: 'OpenAI Chat',
  [REQUEST_FORMATS.CLAUDE_MESSAGES]: 'Claude Messages',
  [REQUEST_FORMATS.CUSTOM_JSON]: '自定义 JSON',
  [REQUEST_FORMATS.REST_API]: 'REST API'
} as const

// 默认配置值
export const DEFAULT_CONFIG = {
  max_tokens: 2000,
  temperature: '0.7',
  timeout: 60,
  retry_count: 3,
  priority: 5
} as const

// 预设的API端点
export const PRESET_ENDPOINTS = {
  OPENAI: 'https://api.openai.com/v1/chat/completions',
  CLAUDE: 'https://api.anthropic.com/v1/messages',
  OPENROUTER: 'https://openrouter.ai/api/v1/chat/completions'
} as const

// 常用模型名称
export const COMMON_MODELS = {
  OPENAI: [
    'gpt-3.5-turbo',
    'gpt-3.5-turbo-16k',
    'gpt-4',
    'gpt-4-32k',
    'gpt-4-turbo-preview'
  ],
  CLAUDE: [
    'claude-3-haiku-20240307',
    'claude-3-sonnet-20240229',
    'claude-3-opus-20240229'
  ]
} as const

export default aiConfigsApi