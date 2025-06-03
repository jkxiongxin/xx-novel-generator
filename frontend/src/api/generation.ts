import apiClient from './index'

// 生成请求接口
export interface GenerationRequest {
  user_input?: string
  max_tokens?: number
  temperature?: number
}

export interface NovelNameRequest extends GenerationRequest {
  genre?: string
  keywords?: string
  style?: string
}

export interface NovelIdeaRequest extends GenerationRequest {
  genre?: string
  themes?: string
  length?: string
}

export interface BrainStormRequest extends GenerationRequest {
  topic?: string
  elements?: string
  creativity_level?: number
}

// 生成响应接口
export interface GenerationResponse {
  data: any
  tokens_used?: number
  model_used?: string
  generation_time?: number
}

export interface ServiceStatus {
  ai_service_available: boolean
  available_adapters: string[]
  default_adapter: string
}

export interface PromptType {
  value: string
  label: string
  description: string
}

// AI生成API
export const generationApi = {
  // 生成小说名（使用演示模式）
  async generateNovelName(data: NovelNameRequest): Promise<GenerationResponse> {
    const response = await apiClient.post('/generation/novel-name', data)
    return response.data
  },

  // 生成小说创意（使用演示模式）
  async generateNovelIdea(data: NovelIdeaRequest): Promise<GenerationResponse> {
    const response = await apiClient.post('/demo/novel-idea', data)
    return response.data
  },

  // 生成脑洞（使用演示模式）
  async generateBrainStorm(data: BrainStormRequest): Promise<GenerationResponse> {
    const response = await apiClient.post('/demo/brain-storm', data)
    return response.data
  },

  // 获取服务状态（使用演示模式）
  async getStatus(): Promise<ServiceStatus> {
    const response = await apiClient.get('/demo/status')
    return response.data.data
  },

  // 获取提示词类型
  async getPromptTypes(): Promise<PromptType[]> {
    const response = await apiClient.get('/generation/prompt-types')
    return response.data.data
  }
}