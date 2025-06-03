import apiClient from './index'

// 脑洞生成相关接口定义
export interface BrainStormRequest {
  topic: string
  creativity_level?: number
  idea_count?: number
  idea_type?: ('plot' | 'character' | 'worldview' | 'mixed')[]
  elements?: string[]
  style?: string
  user_input?: string
  language?: string
  avoid_keywords?: string[]
  reference_works?: string[]
}

export interface GeneratedIdea {
  id: string
  content: string
  type: string
  tags: string[]
  creativity_score: number
  practical_score: number
  summary: string
  potential_development: string
  related_elements: string[]
}

export interface BrainStormResponse {
  success: boolean
  ideas: GeneratedIdea[]
  generation_id: string
  metadata: {
    topic: string
    parameters: BrainStormRequest
    generation_time: number
    model_used: string
    prompt_tokens: number
    completion_tokens: number
  }
}

export interface HistoryItem {
  id: string
  topic: string
  parameters: BrainStormRequest
  ideas_count: number
  created_at: string
  generation_time: number
  rating?: number
  tags: string[]
}

export interface BrainStormHistoryResponse {
  history: HistoryItem[]
  total: number
  limit: number
  offset: number
}

export interface ElementCategory {
  category: string
  display_name: string
  elements: ElementItem[]
}

export interface ElementItem {
  name: string
  description: string
  usage_count: number
  effectiveness_score: number
  related_elements: string[]
}

export interface ElementSuggestionsResponse {
  categories: ElementCategory[]
}

export interface TopicSuggestion {
  topic: string
  description: string
  popularity: number
  expected_ideas: number
  related_topics: string[]
  sample_ideas: string[]
}

export interface TopicSuggestionsResponse {
  suggestions: TopicSuggestion[]
}

export interface UserPreferences {
  default_creativity_level: number
  default_idea_count: number
  preferred_types: string[]
  favorite_elements: string[]
  default_style: string
  auto_save_history: boolean
  updated_at: string
}

export interface SavePreferencesRequest {
  default_creativity_level?: number
  default_idea_count?: number
  preferred_types?: string[]
  favorite_elements?: string[]
  default_style?: string
  auto_save_history?: boolean
}

export interface RateGenerationRequest {
  rating: number
  feedback?: string
  useful_ideas?: string[]
  improvement_suggestions?: string
}

export interface GenerationStatsResponse {
  total_generations: number
  total_ideas: number
  average_ideas_per_generation: number
  most_popular_elements: string[]
  creativity_distribution: {
    level: number
    count: number
  }[]
  usage_trends: {
    date: string
    generations: number
  }[]
}

// 兼容旧接口
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

// 脑洞生成器API服务类
export class BrainStormService {
  // 生成脑洞
  static async generateBrainStorm(request: BrainStormRequest): Promise<BrainStormResponse> {
    // 创建一个新的对象，避免修改原始请求
    const requestData = { ...request };
    
    // 处理elements字段：将数组转换为逗号分隔的字符串
    if (Array.isArray(requestData.elements)) {
      // 使用类型断言解决TypeScript类型问题
      const elementsString = requestData.elements.length > 0
        ? requestData.elements.join(',')
        : null;
      
      // 使用类型断言告诉TypeScript我们知道这里的类型转换是安全的
      (requestData as any).elements = elementsString;
    }
    
    const response = await apiClient.post('/generation/brain-storm', requestData)
    
    // 处理后端新格式响应
    if (response.data && response.data.data && response.data.data.brainstorms) {
      // 将后端新格式转换为前端期望的格式
      const ideas: GeneratedIdea[] = response.data.data.brainstorms.map((brainstorm: any, index: number) => {
        return {
          id: `generated_${Date.now()}_${index}`,
          content: `${brainstorm.concept}\n\n${brainstorm.implementation}`,
          type: brainstorm.style || "mixed",
          tags: [brainstorm.style],
          creativity_score: 8,
          practical_score: 7,
          summary: brainstorm.concept,
          potential_development: brainstorm.development,
          related_elements: []
        };
      });
      
      // 构建标准响应格式
      return {
        success: true,
        ideas: ideas,
        generation_id: `gen_${Date.now()}`,
        metadata: {
          topic: request.topic,
          parameters: request,
          generation_time: response.data.generation_time || 0,
          model_used: response.data.model_used || "unknown",
          prompt_tokens: response.data.tokens_used || 0,
          completion_tokens: response.data.tokens_used || 0
        }
      };
    }
    
    // 如果格式不匹配，返回原始响应
    return response.data;
  }

  // 获取生成历史
  static async getHistory(limit: number = 20, offset: number = 0): Promise<BrainStormHistoryResponse> {
    const response = await apiClient.get(`/generation/brain-storm/history?limit=${limit}&offset=${offset}`)
    return response.data
  }

  // 获取历史详情
  static async getHistoryDetail(historyId: string): Promise<{ history: HistoryItem; ideas: GeneratedIdea[] }> {
    const response = await apiClient.get(`/generation/brain-storm/history/${historyId}`)
    return response.data
  }

  // 获取要素建议
  static async getElementSuggestions(category?: string): Promise<ElementSuggestionsResponse> {
    const url = category ? `/generation/brain-storm/elements?category=${category}` : '/generation/brain-storm/elements'
    const response = await apiClient.get(url)
    return response.data
  }

  // 获取主题建议
  static async getTopicSuggestions(query: string, limit: number = 10): Promise<TopicSuggestionsResponse> {
    const response = await apiClient.get(`/generation/brain-storm/topic-suggestions?q=${encodeURIComponent(query)}&limit=${limit}`)
    return response.data
  }

  // 获取用户偏好
  static async getUserPreferences(): Promise<UserPreferences> {
    const response = await apiClient.get('/generation/brain-storm/preferences')
    return response.data
  }

  // 保存用户偏好
  static async saveUserPreferences(preferences: SavePreferencesRequest): Promise<{ success: boolean; preferences: UserPreferences }> {
    const response = await apiClient.post('/generation/brain-storm/preferences', preferences)
    return response.data
  }

  // 评价生成结果
  static async rateGeneration(generationId: string, rating: RateGenerationRequest): Promise<{ success: boolean; average_rating: number }> {
    const response = await apiClient.post(`/generation/brain-storm/${generationId}/rating`, rating)
    return response.data
  }

  // 获取统计信息
  static async getStats(): Promise<GenerationStatsResponse> {
    const response = await apiClient.get('/generation/brain-storm/stats')
    return response.data
  }
}

// 兼容旧API（保留向后兼容性）
export const generationApi = {
  // 生成小说名
  async generateNovelName(data: NovelNameRequest): Promise<any> {
    const response = await apiClient.post('/generation/novel-name', data)
    return response.data
  },

  // 生成小说创意
  async generateNovelIdea(data: NovelIdeaRequest): Promise<any> {
    const response = await apiClient.post('/demo/novel-idea', data)
    return response.data
  },

  // 生成脑洞（使用新接口）
  async generateBrainStorm(data: any): Promise<any> {
    // 转换旧格式到新格式
    const request: BrainStormRequest = {
      topic: data.topic || data.user_input || '',
      creativity_level: data.creativity_level || 7,
      idea_count: 10,
      elements: data.elements ? [data.elements] : [],
      user_input: data.user_input
    }
    return await BrainStormService.generateBrainStorm(request)
  },

  // 获取服务状态
  async getStatus(): Promise<ServiceStatus> {
    const response = await apiClient.get('/generation/status')
    return response.data
  },

  // 获取提示词类型
  async getPromptTypes(): Promise<PromptType[]> {
    const response = await apiClient.get('/generation/prompt-types')
    return response.data.data
  }
}