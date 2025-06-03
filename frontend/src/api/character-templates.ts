import apiClient from '@/api/index'
import type { AxiosResponse } from 'axios'

export interface CharacterTemplateFilter {
  gender?: string;
  power_systems?: string[];
  worldviews?: string[];
  tags?: string[];
  is_popular?: boolean;
  is_new?: boolean;
  sort_by?: string;
  sort_order?: string;
  page?: number;
  page_size?: number;
}

export interface AppearanceDetail {
  height?: string;
  build?: string;
  hair?: string;
  eyes?: string;
  distinctive_features?: string;
  other?: Record<string, string>;
}

export interface TemplateDetail {
  id: number;
  character_id: number;
  detailed_description?: string;
  background_story?: string;
  relationships?: string;
  strengths: string[];
  weaknesses: string[];
  motivation?: string;
  character_arc?: string;
  dialogue_style?: string;
  appearance?: AppearanceDetail;
  combat_style?: string;
  equipment: string[];
  special_abilities: string[];
  usage_count: number;
  rating: number;
  is_popular: boolean;
  is_new: boolean;
  created_at: string;
  updated_at: string;
}

export interface UsageExample {
  id: number;
  template_detail_id: number;
  novel_genre: string;
  usage_context: string;
  adaptation_notes?: string;
  created_at: string;
  updated_at: string;
}

export interface CharacterTemplateSummary {
  id: number;
  name: string;
  gender: string;
  character_type: string;
  tags: string[];
  description?: string;
  is_template: boolean;
  usage_count: number;
  rating: number;
  is_popular: boolean;
  is_new: boolean;
  is_favorited?: boolean;
}

export interface CharacterTemplateDetail extends CharacterTemplateSummary {
  personality?: string;
  novel_id?: number;
  worldview_id?: number;
  faction_id?: number;
  abilities?: string;
  power_system?: string;
  original_world?: string;
  user_id: number;
  created_at: string;
  updated_at: string;
  template_detail?: TemplateDetail;
  usage_examples?: UsageExample[];
}

export interface TemplateFilterOption {
  value: string;
  label: string;
  count: number;
}

export interface CharacterTemplateListResponse {
  characters: CharacterTemplateSummary[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  filters_available?: Record<string, TemplateFilterOption[]>;
}

export interface UseTemplateRequest {
  novel_id: number;
  customizations?: Record<string, any>;
  adaptation_notes?: string;
}

export interface UseTemplateResponse {
  success: boolean;
  character: any;
  template_used: CharacterTemplateSummary;
  adaptation_applied: boolean;
  message: string;
}

export interface BatchUseTemplateItem {
  template_id: number;
  customizations?: Record<string, any>;
}

export interface BatchUseTemplatesRequest {
  novel_id: number;
  templates: BatchUseTemplateItem[];
}

export interface BatchUseFailedItem {
  template_id: number;
  reason: string;
}

export interface BatchUseTemplatesResponse {
  success_count: number;
  failed_count: number;
  created_characters: CharacterTemplateSummary[];
  failed_items: BatchUseFailedItem[];
  message: string;
}

export interface FavoriteResponse {
  success: boolean;
  is_favorited: boolean;
  message: string;
}

export interface SearchMetadata {
  keyword: string;
  total_matches: number;
  search_time: number;
  suggestions?: string[];
}

export interface SearchTemplatesRequest {
  keyword: string;
  filters?: CharacterTemplateFilter;
  search_fields?: string[];
  fuzzy_search?: boolean;
  highlight?: boolean;
}

export class CharacterTemplateService {
  /**
   * 获取角色模板列表
   */
  static async getTemplates(filters?: CharacterTemplateFilter): Promise<CharacterTemplateListResponse> {
    const params = new URLSearchParams();
    
    if (filters) {
      if (filters.gender) params.append('gender', filters.gender);
      if (filters.power_systems) {
        filters.power_systems.forEach(system => params.append('power_systems', system));
      }
      if (filters.worldviews) {
        filters.worldviews.forEach(worldview => params.append('worldviews', worldview));
      }
      if (filters.tags) {
        filters.tags.forEach(tag => params.append('tags', tag));
      }
      if (filters.is_popular !== undefined) params.append('is_popular', String(filters.is_popular));
      if (filters.is_new !== undefined) params.append('is_new', String(filters.is_new));
      if (filters.sort_by) params.append('sort_by', filters.sort_by);
      if (filters.sort_order) params.append('sort_order', filters.sort_order);
      if (filters.page) params.append('page', String(filters.page));
      if (filters.page_size) params.append('page_size', String(filters.page_size));
    }
    
    // 默认包含筛选选项
    params.append('include_filters', 'true');
    
    const response = await apiClient.get(`/character-templates/?${params}`);
    return response.data;
  }
  
  /**
   * 获取角色模板详情
   */
  static async getTemplateDetail(templateId: number): Promise<CharacterTemplateDetail> {
    const response = await apiClient.get(`/character-templates/${templateId}`);
    return response.data;
  }
  
  /**
   * 搜索角色模板
   */
  static async searchTemplates(request: SearchTemplatesRequest): Promise<CharacterTemplateListResponse> {
    const response = await apiClient.post('/character-templates/search', request);
    return response.data;
  }
  
  /**
   * 获取搜索建议
   */
  static async getSearchSuggestions(keyword: string): Promise<any[]> {
    const response = await apiClient.get(`/character-templates/suggestions/search?keyword=${encodeURIComponent(keyword)}`);
    return response.data;
  }
  
  /**
   * 使用角色模板
   */
  static async useTemplate(templateId: number, request: UseTemplateRequest): Promise<UseTemplateResponse> {
    const response = await apiClient.post(`/character-templates/${templateId}/use`, request);
    return response.data;
  }
  
  /**
   * 批量使用角色模板
   */
  static async batchUseTemplates(request: BatchUseTemplatesRequest): Promise<BatchUseTemplatesResponse> {
    const response = await apiClient.post('/character-templates/batch-use', request);
    return response.data;
  }
  
  /**
   * 收藏/取消收藏角色模板
   */
  static async toggleFavorite(templateId: number): Promise<FavoriteResponse> {
    const response = await apiClient.post(`/character-templates/${templateId}/favorite`);
    return response.data;
  }
  
  /**
   * 获取收藏的角色模板
   */
  static async getFavoriteTemplates(): Promise<CharacterTemplateListResponse> {
    const response = await apiClient.get('/character-templates/favorites');
    return response.data;
  }
  
  /**
   * 获取推荐的角色模板
   */
  static async getRecommendations(
    based_on: string = 'popular',
    novel_id?: number,
    limit: number = 10,
    exclude_used: boolean = true
  ): Promise<any> {
    let params = new URLSearchParams();
    params.append('based_on', based_on);
    if (novel_id) params.append('novel_id', String(novel_id));
    params.append('limit', String(limit));
    params.append('exclude_used', String(exclude_used));
    
    const response = await apiClient.get(`/character-templates/recommendations?${params}`);
    return response.data;
  }
}