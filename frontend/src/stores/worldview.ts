/**
 * 世界观状态管理
 * Author: AI Assistant
 * Created: 2025-06-03
 */

import { defineStore } from 'pinia'
import { ref, reactive, computed } from 'vue'
import WorldviewAPI, { 
  type Worldview, 
  type WorldMap, 
  type CultivationSystem, 
  type History, 
  type Faction,
  type WorldviewCreateData,
  type WorldviewUpdateData,
  type WorldMapCreateData,
  type WorldMapUpdateData,
  type CultivationSystemCreateData,
  type CultivationSystemUpdateData,
  type HistoryCreateData,
  type HistoryUpdateData,
  type FactionCreateData,
  type FactionUpdateData
} from '@/api/worldview'

export const useWorldviewStore = defineStore('worldview', () => {
  // ============ 状态定义 ============
  
  // 世界观列表
  const worldviews = ref<Worldview[]>([])
  const currentWorldview = ref<Worldview | null>(null)
  
  // 各类型数据
  const worldMaps = ref<WorldMap[]>([])
  const cultivationSystems = ref<CultivationSystem[]>([])
  const histories = ref<History[]>([])
  const factions = ref<Faction[]>([])
  
  // 加载状态
  const loading = reactive({
    worldviews: false,
    worldMaps: false,
    cultivationSystems: false,
    histories: false,
    factions: false
  })
  
  // 错误状态
  const errors = reactive({
    worldviews: '',
    worldMaps: '',
    cultivationSystems: '',
    histories: '',
    factions: ''
  })

  // ============ 计算属性 ============
  
  const primaryWorldview = computed(() => {
    return worldviews.value.find(w => w.is_primary) || null
  })
  
  const worldviewStats = computed(() => {
    if (!currentWorldview.value) return null
    
    return {
      totalMaps: worldMaps.value.length,
      totalCultivationSystems: cultivationSystems.value.length,
      totalHistories: histories.value.length,
      totalFactions: factions.value.length,
      completionPercentage: calculateCompletionPercentage()
    }
  })
  
  // ============ 工具方法 ============
  
  const calculateCompletionPercentage = (): number => {
    if (!currentWorldview.value) return 0
    
    let completed = 0
    let total = 4 // 4个主要类别
    
    if (worldMaps.value.length > 0) completed++
    if (cultivationSystems.value.length > 0) completed++
    if (histories.value.length > 0) completed++
    if (factions.value.length > 0) completed++
    
    return Math.round((completed / total) * 100)
  }
  
  const clearErrors = () => {
    Object.keys(errors).forEach(key => {
      errors[key as keyof typeof errors] = ''
    })
  }
  
  const handleError = (type: keyof typeof errors, error: any) => {
    console.error(`${type} error:`, error)
    errors[type] = error?.response?.data?.detail || error.message || '操作失败'
  }

  // ============ 世界观管理 ============
  
  const loadWorldviews = async (novelId: number): Promise<void> => {
    try {
      loading.worldviews = true
      errors.worldviews = ''
      
      const response = await WorldviewAPI.getWorldviewsByNovel(novelId)
      worldviews.value = response.items
      
      // 如果有主世界观，自动设置为当前世界观
      if (!currentWorldview.value && response.items.length > 0) {
        const primary = response.items.find(w => w.is_primary)
        setCurrentWorldview(primary || response.items[0])
      }
      
    } catch (error: any) {
      handleError('worldviews', error)
      throw error
    } finally {
      loading.worldviews = false
    }
  }
  
  const createWorldview = async (data: WorldviewCreateData): Promise<Worldview> => {
    try {
      loading.worldviews = true
      errors.worldviews = ''
      
      const newWorldview = await WorldviewAPI.createWorldview(data)
      worldviews.value.push(newWorldview)
      
      // 如果是主世界观，更新其他世界观的主世界状态
      if (newWorldview.is_primary) {
        worldviews.value.forEach(w => {
          if (w.id !== newWorldview.id) {
            w.is_primary = false
          }
        })
      }
      
      setCurrentWorldview(newWorldview)
      return newWorldview
      
    } catch (error: any) {
      handleError('worldviews', error)
      throw error
    } finally {
      loading.worldviews = false
    }
  }
  
  const updateWorldview = async (worldviewId: number, data: WorldviewUpdateData): Promise<Worldview> => {
    try {
      loading.worldviews = true
      errors.worldviews = ''
      
      const updatedWorldview = await WorldviewAPI.updateWorldview(worldviewId, data)
      
      // 更新本地状态
      const index = worldviews.value.findIndex(w => w.id === worldviewId)
      if (index !== -1) {
        worldviews.value[index] = updatedWorldview
      }
      
      // 如果是当前世界观，更新当前世界观
      if (currentWorldview.value?.id === worldviewId) {
        currentWorldview.value = updatedWorldview
      }
      
      // 如果设置为主世界观，更新其他世界观的主世界状态
      if (updatedWorldview.is_primary) {
        worldviews.value.forEach(w => {
          if (w.id !== worldviewId) {
            w.is_primary = false
          }
        })
      }
      
      return updatedWorldview
      
    } catch (error: any) {
      handleError('worldviews', error)
      throw error
    } finally {
      loading.worldviews = false
    }
  }
  
  const deleteWorldview = async (worldviewId: number): Promise<void> => {
    try {
      loading.worldviews = true
      errors.worldviews = ''
      
      await WorldviewAPI.deleteWorldview(worldviewId)
      
      // 更新本地状态
      worldviews.value = worldviews.value.filter(w => w.id !== worldviewId)
      
      // 如果删除的是当前世界观，清空当前世界观
      if (currentWorldview.value?.id === worldviewId) {
        currentWorldview.value = null
        clearCurrentWorldviewData()
      }
      
    } catch (error: any) {
      handleError('worldviews', error)
      throw error
    } finally {
      loading.worldviews = false
    }
  }
  
  const setCurrentWorldview = (worldview: Worldview | null): void => {
    currentWorldview.value = worldview
    if (worldview) {
      loadCurrentWorldviewData()
    } else {
      clearCurrentWorldviewData()
    }
  }
  
  // ============ 世界地图管理 ============
  
  const loadWorldMaps = async (): Promise<void> => {
    if (!currentWorldview.value) return
    
    try {
      loading.worldMaps = true
      errors.worldMaps = ''
      
      const response = await WorldviewAPI.getWorldMaps(currentWorldview.value.id)
      worldMaps.value = response.items
      
    } catch (error: any) {
      handleError('worldMaps', error)
    } finally {
      loading.worldMaps = false
    }
  }
  
  const createWorldMap = async (data: WorldMapCreateData): Promise<WorldMap> => {
    if (!currentWorldview.value) throw new Error('没有选择世界观')
    
    try {
      loading.worldMaps = true
      errors.worldMaps = ''
      
      const newMap = await WorldviewAPI.createWorldMap(currentWorldview.value.id, data)
      worldMaps.value.push(newMap)
      
      return newMap
      
    } catch (error: any) {
      handleError('worldMaps', error)
      throw error
    } finally {
      loading.worldMaps = false
    }
  }
  
  const updateWorldMap = async (mapId: number, data: WorldMapUpdateData): Promise<WorldMap> => {
    try {
      loading.worldMaps = true
      errors.worldMaps = ''
      
      const updatedMap = await WorldviewAPI.updateWorldMap(mapId, data)
      
      const index = worldMaps.value.findIndex(m => m.id === mapId)
      if (index !== -1) {
        worldMaps.value[index] = updatedMap
      }
      
      return updatedMap
      
    } catch (error: any) {
      handleError('worldMaps', error)
      throw error
    } finally {
      loading.worldMaps = false
    }
  }
  
  const deleteWorldMap = async (mapId: number): Promise<void> => {
    try {
      loading.worldMaps = true
      errors.worldMaps = ''
      
      await WorldviewAPI.deleteWorldMap(mapId)
      worldMaps.value = worldMaps.value.filter(m => m.id !== mapId)
      
    } catch (error: any) {
      handleError('worldMaps', error)
      throw error
    } finally {
      loading.worldMaps = false
    }
  }
  
  // ============ 修炼体系管理 ============
  
  const loadCultivationSystems = async (): Promise<void> => {
    if (!currentWorldview.value) return
    
    try {
      loading.cultivationSystems = true
      errors.cultivationSystems = ''
      
      const response = await WorldviewAPI.getCultivationSystems(currentWorldview.value.id)
      cultivationSystems.value = response.items
      
    } catch (error: any) {
      handleError('cultivationSystems', error)
    } finally {
      loading.cultivationSystems = false
    }
  }
  
  const createCultivationSystem = async (data: CultivationSystemCreateData): Promise<CultivationSystem> => {
    if (!currentWorldview.value) throw new Error('没有选择世界观')
    
    try {
      loading.cultivationSystems = true
      errors.cultivationSystems = ''
      
      const newSystem = await WorldviewAPI.createCultivationSystem(currentWorldview.value.id, data)
      cultivationSystems.value.push(newSystem)
      
      return newSystem
      
    } catch (error: any) {
      handleError('cultivationSystems', error)
      throw error
    } finally {
      loading.cultivationSystems = false
    }
  }
  
  const updateCultivationSystem = async (systemId: number, data: CultivationSystemUpdateData): Promise<CultivationSystem> => {
    try {
      loading.cultivationSystems = true
      errors.cultivationSystems = ''
      
      const updatedSystem = await WorldviewAPI.updateCultivationSystem(systemId, data)
      
      const index = cultivationSystems.value.findIndex(s => s.id === systemId)
      if (index !== -1) {
        cultivationSystems.value[index] = updatedSystem
      }
      
      return updatedSystem
      
    } catch (error: any) {
      handleError('cultivationSystems', error)
      throw error
    } finally {
      loading.cultivationSystems = false
    }
  }
  
  const deleteCultivationSystem = async (systemId: number): Promise<void> => {
    try {
      loading.cultivationSystems = true
      errors.cultivationSystems = ''
      
      await WorldviewAPI.deleteCultivationSystem(systemId)
      cultivationSystems.value = cultivationSystems.value.filter(s => s.id !== systemId)
      
    } catch (error: any) {
      handleError('cultivationSystems', error)
      throw error
    } finally {
      loading.cultivationSystems = false
    }
  }
  
  // ============ 历史事件管理 ============
  
  const loadHistories = async (): Promise<void> => {
    if (!currentWorldview.value) return
    
    try {
      loading.histories = true
      errors.histories = ''
      
      const response = await WorldviewAPI.getHistories(currentWorldview.value.id)
      histories.value = response.items
      
    } catch (error: any) {
      handleError('histories', error)
    } finally {
      loading.histories = false
    }
  }
  
  const createHistory = async (data: HistoryCreateData): Promise<History> => {
    if (!currentWorldview.value) throw new Error('没有选择世界观')
    
    try {
      loading.histories = true
      errors.histories = ''
      
      const newHistory = await WorldviewAPI.createHistory(currentWorldview.value.id, data)
      histories.value.push(newHistory)
      
      return newHistory
      
    } catch (error: any) {
      handleError('histories', error)
      throw error
    } finally {
      loading.histories = false
    }
  }
  
  const updateHistory = async (historyId: number, data: HistoryUpdateData): Promise<History> => {
    try {
      loading.histories = true
      errors.histories = ''
      
      const updatedHistory = await WorldviewAPI.updateHistory(historyId, data)
      
      const index = histories.value.findIndex(h => h.id === historyId)
      if (index !== -1) {
        histories.value[index] = updatedHistory
      }
      
      return updatedHistory
      
    } catch (error: any) {
      handleError('histories', error)
      throw error
    } finally {
      loading.histories = false
    }
  }
  
  const deleteHistory = async (historyId: number): Promise<void> => {
    try {
      loading.histories = true
      errors.histories = ''
      
      await WorldviewAPI.deleteHistory(historyId)
      histories.value = histories.value.filter(h => h.id !== historyId)
      
    } catch (error: any) {
      handleError('histories', error)
      throw error
    } finally {
      loading.histories = false
    }
  }
  
  // ============ 阵营势力管理 ============
  
  const loadFactions = async (): Promise<void> => {
    if (!currentWorldview.value) return
    
    try {
      loading.factions = true
      errors.factions = ''
      
      const response = await WorldviewAPI.getFactions(currentWorldview.value.id)
      factions.value = response.items
      
    } catch (error: any) {
      handleError('factions', error)
    } finally {
      loading.factions = false
    }
  }
  
  const createFaction = async (data: FactionCreateData): Promise<Faction> => {
    if (!currentWorldview.value) throw new Error('没有选择世界观')
    
    try {
      loading.factions = true
      errors.factions = ''
      
      const newFaction = await WorldviewAPI.createFaction(currentWorldview.value.id, data)
      factions.value.push(newFaction)
      
      return newFaction
      
    } catch (error: any) {
      handleError('factions', error)
      throw error
    } finally {
      loading.factions = false
    }
  }
  
  const updateFaction = async (factionId: number, data: FactionUpdateData): Promise<Faction> => {
    try {
      loading.factions = true
      errors.factions = ''
      
      const updatedFaction = await WorldviewAPI.updateFaction(factionId, data)
      
      const index = factions.value.findIndex(f => f.id === factionId)
      if (index !== -1) {
        factions.value[index] = updatedFaction
      }
      
      return updatedFaction
      
    } catch (error: any) {
      handleError('factions', error)
      throw error
    } finally {
      loading.factions = false
    }
  }
  
  const deleteFaction = async (factionId: number): Promise<void> => {
    try {
      loading.factions = true
      errors.factions = ''
      
      await WorldviewAPI.deleteFaction(factionId)
      factions.value = factions.value.filter(f => f.id !== factionId)
      
    } catch (error: any) {
      handleError('factions', error)
      throw error
    } finally {
      loading.factions = false
    }
  }
  
  // ============ 数据加载 ============
  
  const loadCurrentWorldviewData = async (): Promise<void> => {
    if (!currentWorldview.value) return
    
    await Promise.all([
      loadWorldMaps(),
      loadCultivationSystems(),
      loadHistories(),
      loadFactions()
    ])
  }
  
  const clearCurrentWorldviewData = (): void => {
    worldMaps.value = []
    cultivationSystems.value = []
    histories.value = []
    factions.value = []
  }
  
  const refreshCurrentWorldview = async (): Promise<void> => {
    if (currentWorldview.value) {
      await loadCurrentWorldviewData()
    }
  }
  
  // ============ 重置状态 ============
  
  const resetStore = (): void => {
    worldviews.value = []
    currentWorldview.value = null
    clearCurrentWorldviewData()
    clearErrors()
    
    Object.keys(loading).forEach(key => {
      loading[key as keyof typeof loading] = false
    })
  }

  return {
    // 状态
    worldviews,
    currentWorldview,
    worldMaps,
    cultivationSystems,
    histories,
    factions,
    loading,
    errors,
    
    // 计算属性
    primaryWorldview,
    worldviewStats,
    
    // 世界观管理
    loadWorldviews,
    createWorldview,
    updateWorldview,
    deleteWorldview,
    setCurrentWorldview,
    
    // 世界地图管理
    loadWorldMaps,
    createWorldMap,
    updateWorldMap,
    deleteWorldMap,
    
    // 修炼体系管理
    loadCultivationSystems,
    createCultivationSystem,
    updateCultivationSystem,
    deleteCultivationSystem,
    
    // 历史事件管理
    loadHistories,
    createHistory,
    updateHistory,
    deleteHistory,
    
    // 阵营势力管理
    loadFactions,
    createFaction,
    updateFaction,
    deleteFaction,
    
    // 数据管理
    loadCurrentWorldviewData,
    refreshCurrentWorldview,
    resetStore
  }
})