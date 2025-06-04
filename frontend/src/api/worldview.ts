/**
 * 世界观API接口
 * Author: AI Assistant
 * Created: 2025-06-03
 */

import apiClient from './index'

// 类型定义
export interface Worldview {
  id: number
  novel_id: number
  name: string
  description?: string
  is_primary: boolean
  user_id: number
  created_at: string
  updated_at: string
}

export interface WorldMap {
  id: number
  worldview_id: number
  region_name: string
  description: string
  parent_region_id?: number
  level: number
  climate?: string
  terrain?: string
  resources?: string
  population?: string
  culture?: string
  user_id: number
  created_at: string
  updated_at: string
}

export interface CultivationSystem {
  id: number
  worldview_id: number
  system_name: string
  level_name: string
  description: string
  level_order: number
  cultivation_method?: string
  required_resources?: string
  breakthrough_condition?: string
  power_description?: string
  user_id: number
  created_at: string
  updated_at: string
}

export interface History {
  id: number
  worldview_id: number
  event_name: string
  time_period?: string
  time_order: number
  event_type?: string
  description: string
  participants?: string
  consequences?: string
  related_locations?: string
  user_id: number
  created_at: string
  updated_at: string
}

export interface Faction {
  id: number
  worldview_id: number
  name: string
  faction_type: string
  description?: string
  leader?: string
  territory?: string
  power_level?: string
  ideology?: string
  allies?: string[]
  enemies?: string[]
  member_count?: string
  user_id: number
  created_at: string
  updated_at: string
}

export interface WorldviewCreateData {
  novel_id: number
  name: string
  description?: string
  is_primary?: boolean
}

export interface WorldviewUpdateData {
  name?: string
  description?: string
  is_primary?: boolean
}

export interface WorldMapCreateData {
  region_name: string
  description: string
  parent_region_id?: number
  level?: number
  climate?: string
  terrain?: string
  resources?: string
  population?: string
  culture?: string
}

export interface WorldMapUpdateData {
  region_name?: string
  description?: string
  parent_region_id?: number
  level?: number
  climate?: string
  terrain?: string
  resources?: string
  population?: string
  culture?: string
}

export interface CultivationSystemCreateData {
  system_name: string
  level_name: string
  description: string
  level_order: number
  cultivation_method?: string
  required_resources?: string
  breakthrough_condition?: string
  power_description?: string
}

export interface CultivationSystemUpdateData {
  system_name?: string
  level_name?: string
  description?: string
  level_order?: number
  cultivation_method?: string
  required_resources?: string
  breakthrough_condition?: string
  power_description?: string
}

export interface HistoryCreateData {
  event_name: string
  time_period?: string
  time_order: number
  event_type?: string
  description: string
  participants?: string
  consequences?: string
  related_locations?: string
}

export interface HistoryUpdateData {
  event_name?: string
  time_period?: string
  time_order?: number
  event_type?: string
  description?: string
  participants?: string
  consequences?: string
  related_locations?: string
}

export interface FactionCreateData {
  name: string
  faction_type: string
  description?: string
  leader?: string
  territory?: string
  power_level?: string
  ideology?: string
  allies?: string[]
  enemies?: string[]
  member_count?: string
}

export interface FactionUpdateData {
  name?: string
  faction_type?: string
  description?: string
  leader?: string
  territory?: string
  power_level?: string
  ideology?: string
  allies?: string[]
  enemies?: string[]
  member_count?: string
}

export interface WorldviewGenerationRequest {
  novel_id: number
  worldview_name?: string
  generation_types: string[]
  user_suggestion?: string
  include_novel_idea?: boolean
  include_novel_settings?: boolean
}

export interface ApiListResponse<T> {
  items: T[]
  total: number
}

// 世界观API类
export class WorldviewAPI {
  // ============ 世界观管理 ============
  
  /**
   * 创建世界观
   */
  static async createWorldview(data: WorldviewCreateData): Promise<Worldview> {
    const response = await apiClient.post('/worldview/', data)
    return response.data
  }

  /**
   * 获取小说的世界观列表
   */
  static async getWorldviewsByNovel(novelId: number): Promise<ApiListResponse<Worldview>> {
    const response = await apiClient.get(`/worldview/novel/${novelId}`)
    return response.data
  }

  /**
   * 获取世界观详情
   */
  static async getWorldview(worldviewId: number): Promise<Worldview> {
    const response = await apiClient.get(`/worldview/${worldviewId}`)
    return response.data
  }

  /**
   * 更新世界观
   */
  static async updateWorldview(worldviewId: number, data: WorldviewUpdateData): Promise<Worldview> {
    const response = await apiClient.put(`/worldview/${worldviewId}`, data)
    return response.data
  }

  /**
   * 删除世界观
   */
  static async deleteWorldview(worldviewId: number): Promise<void> {
    await apiClient.delete(`/worldview/${worldviewId}`)
  }

  // ============ 世界地图管理 ============
  
  /**
   * 创建世界地图
   */
  static async createWorldMap(worldviewId: number, data: WorldMapCreateData): Promise<WorldMap> {
    const response = await apiClient.post(`/worldview/${worldviewId}/maps`, data)
    return response.data
  }

  /**
   * 获取世界地图列表
   */
  static async getWorldMaps(worldviewId: number): Promise<ApiListResponse<WorldMap>> {
    const response = await apiClient.get(`/worldview/${worldviewId}/maps`)
    return response.data
  }

  /**
   * 更新世界地图
   */
  static async updateWorldMap(mapId: number, data: WorldMapUpdateData): Promise<WorldMap> {
    const response = await apiClient.put(`/worldview/maps/${mapId}`, data)
    return response.data
  }

  /**
   * 删除世界地图
   */
  static async deleteWorldMap(mapId: number): Promise<void> {
    await apiClient.delete(`/worldview/maps/${mapId}`)
  }

  // ============ 修炼体系管理 ============
  
  /**
   * 创建修炼体系
   */
  static async createCultivationSystem(worldviewId: number, data: CultivationSystemCreateData): Promise<CultivationSystem> {
    const response = await apiClient.post(`/worldview/${worldviewId}/cultivation`, data)
    return response.data
  }

  /**
   * 获取修炼体系列表
   */
  static async getCultivationSystems(worldviewId: number): Promise<ApiListResponse<CultivationSystem>> {
    const response = await apiClient.get(`/worldview/${worldviewId}/cultivation`)
    return response.data
  }

  /**
   * 更新修炼体系
   */
  static async updateCultivationSystem(cultivationId: number, data: CultivationSystemUpdateData): Promise<CultivationSystem> {
    const response = await apiClient.put(`/worldview/cultivation/${cultivationId}`, data)
    return response.data
  }

  /**
   * 删除修炼体系
   */
  static async deleteCultivationSystem(cultivationId: number): Promise<void> {
    await apiClient.delete(`/worldview/cultivation/${cultivationId}`)
  }

  // ============ 历史事件管理 ============
  
  /**
   * 创建历史事件
   */
  static async createHistory(worldviewId: number, data: HistoryCreateData): Promise<History> {
    const response = await apiClient.post(`/worldview/${worldviewId}/history`, data)
    return response.data
  }

  /**
   * 获取历史事件列表
   */
  static async getHistories(worldviewId: number): Promise<ApiListResponse<History>> {
    const response = await apiClient.get(`/worldview/${worldviewId}/history`)
    return response.data
  }

  /**
   * 更新历史事件
   */
  static async updateHistory(historyId: number, data: HistoryUpdateData): Promise<History> {
    const response = await apiClient.put(`/worldview/history/${historyId}`, data)
    return response.data
  }

  /**
   * 删除历史事件
   */
  static async deleteHistory(historyId: number): Promise<void> {
    await apiClient.delete(`/worldview/history/${historyId}`)
  }

  // ============ 阵营势力管理 ============
  
  /**
   * 创建阵营势力
   */
  static async createFaction(worldviewId: number, data: FactionCreateData): Promise<Faction> {
    const response = await apiClient.post(`/worldview/${worldviewId}/factions`, data)
    return response.data
  }

  /**
   * 获取阵营势力列表
   */
  static async getFactions(worldviewId: number): Promise<ApiListResponse<Faction>> {
    const response = await apiClient.get(`/worldview/${worldviewId}/factions`)
    return response.data
  }

  /**
   * 更新阵营势力
   */
  static async updateFaction(factionId: number, data: FactionUpdateData): Promise<Faction> {
    const response = await apiClient.put(`/worldview/factions/${factionId}`, data)
    return response.data
  }

  /**
   * 删除阵营势力
   */
  static async deleteFaction(factionId: number): Promise<void> {
    await apiClient.delete(`/worldview/factions/${factionId}`)
  }

  // ============ AI生成功能 ============
  
  /**
   * AI生成世界观
   */
  static async generateWorldview(data: WorldviewGenerationRequest): Promise<any> {
    const response = await apiClient.post('/worldview/generate', data)
    return response
  }

  /**
   * 保存AI生成的世界观数据
   */
  static async saveGeneratedWorldview(novelId: number, generatedData: any): Promise<any> {
    const response = await apiClient.post('/worldview/save-generated', {
      novel_id: novelId,
      generated_data: generatedData
    })
    return response
  }

  /**
   * AI生成世界地图区域
   */
  static async generateWorldMaps(worldviewId: number, params: {
    parent_region_id?: number
    count?: number
    include?: string[]
    suggestion?: string
  }): Promise<any> {
    const response = await apiClient.post(`/worldview/${worldviewId}/maps/generate`, params)
    return response
  }

  /**
   * 保存AI生成的地图数据
   */
  static async saveGeneratedMaps(worldviewId: number, data: {
    generated_maps: any[]
    parent_region_id?: number
  }): Promise<any> {
    const response = await apiClient.post(`/worldview/${worldviewId}/maps/save-generated`, data)
    return response
  }

  /**
   * AI生成修炼体系
   */
  static async generateCultivationSystem(worldviewId: number, params: {
    system_name?: string
    level_count?: number
    include?: string[]
    suggestion?: string
  }): Promise<any> {
    const response = await apiClient.post(`/worldview/${worldviewId}/cultivation/generate`, params)
    return response
  }

  /**
   * 保存AI生成的修炼体系数据
   */
  static async saveGeneratedCultivation(worldviewId: number, data: {
    generated_systems: any[]
  }): Promise<any> {
    const response = await apiClient.post(`/worldview/${worldviewId}/cultivation/save-generated`, data)
    return response
  }
}

// 导出默认实例
export default WorldviewAPI