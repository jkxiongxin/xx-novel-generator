<template>
  <div class="module-grid">
    <ModuleCard
      v-for="moduleName in moduleOrder"
      :key="moduleName"
      :module-name="moduleName"
      :module-stats="moduleStates[moduleName]?.data || undefined"
      :novel-id="novelId"
      :loading="moduleStates[moduleName]?.loading"
      :error="moduleStates[moduleName]?.error"
      @quick-action="handleQuickAction"
      @refresh-module="handleRefreshModule"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import ModuleCard from './ModuleCard.vue'
import { WorkspaceService, type ModuleStats, type ModuleOverview } from '@/api/workspace'

// Props
interface Props {
  novelId: number
  initialModules?: ModuleOverview
}

const props = withDefaults(defineProps<Props>(), {
  initialModules: undefined
})

// Emits
const emit = defineEmits<{
  moduleUpdated: [moduleName: string, data: ModuleStats]
}>()

// 响应式数据
const moduleOrder = ref([
  'worldview',
  'characters', 
  'outline',
  'chapters',
  'timeline',
  'settings'
])

interface ModuleState {
  loading: boolean
  data: ModuleStats | null
  error: string
}

const moduleStates = reactive<Record<string, ModuleState>>({
  worldview: { loading: false, data: null, error: '' },
  characters: { loading: false, data: null, error: '' },
  outline: { loading: false, data: null, error: '' },
  chapters: { loading: false, data: null, error: '' },
  timeline: { loading: false, data: null, error: '' },
  settings: { loading: false, data: null, error: '' }
})

// 方法
const initializeModuleStates = (modules?: ModuleOverview) => {
  if (modules) {
    Object.keys(modules).forEach(moduleName => {
      if (moduleStates[moduleName]) {
        moduleStates[moduleName].data = modules[moduleName as keyof ModuleOverview]
        moduleStates[moduleName].loading = false
        moduleStates[moduleName].error = ''
      }
    })
  }
}

const loadModuleData = async (moduleName: string): Promise<void> => {
  try {
    moduleStates[moduleName].loading = true
    moduleStates[moduleName].error = ''
    
    const data = await WorkspaceService.getModuleStats(props.novelId, moduleName)
    moduleStates[moduleName].data = data
    
    // 触发更新事件
    emit('moduleUpdated', moduleName, data)
    
  } catch (error: any) {
    console.error(`加载${moduleName}模块失败:`, error)
    moduleStates[moduleName].error = error.message || '加载失败'
    
    // 显示错误提示
    const moduleNames: Record<string, string> = {
      worldview: '世界观',
      characters: '角色',
      outline: '大纲',
      chapters: '章节',
      timeline: '时间轴',
      settings: '设置'
    }
    
    ElMessage.warning(`${moduleNames[moduleName] || moduleName}数据加载失败`)
    
  } finally {
    moduleStates[moduleName].loading = false
  }
}

const loadAllModules = async (): Promise<void> => {
  // 并行加载所有模块数据
  const loadPromises = moduleOrder.value.map(moduleName => {
    // 如果没有初始数据，才进行加载
    if (!moduleStates[moduleName].data) {
      return loadModuleData(moduleName)
    }
    return Promise.resolve()
  })
  
  try {
    await Promise.allSettled(loadPromises)
  } catch (error) {
    console.error('加载模块数据失败:', error)
  }
}

const handleQuickAction = async (moduleName: string): Promise<void> => {
  try {
    // 这里可以根据不同模块执行不同的快捷操作
    console.log('执行快捷操作:', moduleName)
    
    // 示例：调用后端API执行快捷操作
    // await WorkspaceService.executeQuickAction(props.novelId, `${moduleName}_quick`, {})
    
    // 操作完成后刷新模块数据
    setTimeout(() => {
      handleRefreshModule(moduleName)
    }, 1000)
    
  } catch (error: any) {
    console.error('快捷操作失败:', error)
    ElMessage.error('操作失败，请稍后重试')
  }
}

const handleRefreshModule = async (moduleName: string): Promise<void> => {
  await loadModuleData(moduleName)
}

// 公开方法给父组件
const refreshAllModules = async (): Promise<void> => {
  await loadAllModules()
}

const refreshModule = async (moduleName: string): Promise<void> => {
  await loadModuleData(moduleName)
}

// 暴露方法给父组件
defineExpose({
  refreshAllModules,
  refreshModule,
  moduleStates
})

// 生命周期
onMounted(() => {
  // 使用初始数据初始化状态
  initializeModuleStates(props.initialModules)
  
  // 如果没有初始数据，则加载所有模块
  if (!props.initialModules) {
    loadAllModules()
  }
})
</script>

<style scoped lang="scss">
.module-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
}

// 响应式布局
@media (max-width: 1023px) {
  .module-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
  }
}

@media (max-width: 767px) {
  .module-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
}

// 大屏幕优化
@media (min-width: 1400px) {
  .module-grid {
    grid-template-columns: repeat(3, 1fr);
    max-width: 1200px;
    margin: 0 auto 32px auto;
  }
}
</style>