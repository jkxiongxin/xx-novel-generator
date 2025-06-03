<template>
  <div class="workspace-overview">
    <!-- 加载状态 -->
    <div v-if="initialLoading" class="loading-container">
      <el-skeleton :rows="8" animated />
    </div>

    <!-- 错误状态 -->
    <div v-else-if="errorState.show" class="error-container">
      <el-result
        :icon="errorState.config.type"
        :title="errorState.config.title"
        :sub-title="errorState.config.message"
      >
        <template #extra>
          <el-button
            v-for="action in errorState.config.actions"
            :key="action.text"
            :type="action.type || 'primary'"
            @click="action.handler"
          >
            {{ action.text }}
          </el-button>
        </template>
      </el-result>
    </div>

    <!-- 正常内容 -->
    <div v-else class="workspace-content">
      <!-- 快速开始引导 -->
      <QuickStartGuide
        ref="quickStartGuideRef"
        :novel-id="novelId"
        :module-progress="moduleProgress"
        @skip="handleGuideSkip"
        @complete="handleGuideComplete"
        @step-completed="handleStepCompleted"
      />

      <!-- 工作台头部 -->
      <WorkspaceHeader
        :novel-id="novelId"
        :novel="overviewData?.novel"
        :progress="overviewData?.progress"
        @open-ai-assistant="handleOpenAIAssistant"
        @refresh-data="refreshWorkspaceData"
      />

      <!-- 功能模块网格 -->
      <ModuleGrid
        ref="moduleGridRef"
        :novel-id="novelId"
        :initial-modules="overviewData?.modules"
        @module-updated="handleModuleUpdated"
      />

      <!-- 创作进度总览 -->
      <ProgressOverview
        :novel-id="novelId"
        :progress="overviewData?.progress"
        :writing-stats="overviewData?.writing_stats"
        :recent-activities="overviewData?.recent_activities"
      />
    </div>

    <!-- AI助手对话框 -->
    <el-dialog
      v-model="showAIAssistant"
      title="AI创作助手"
      width="50%"
      :before-close="handleCloseAIAssistant"
    >
      <div class="ai-assistant-content">
        <el-alert
          title="AI助手"
          type="info"
          description="AI助手功能正在开发中，敬请期待！"
          show-icon
          :closable="false"
        />
      </div>
      <template #footer>
        <el-button @click="showAIAssistant = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElNotification } from 'element-plus'
import WorkspaceHeader from '@/components/workspace/WorkspaceHeader.vue'
import ModuleGrid from '@/components/workspace/ModuleGrid.vue'
import ProgressOverview from '@/components/workspace/ProgressOverview.vue'
import QuickStartGuide from '@/components/workspace/QuickStartGuide.vue'
import { 
  WorkspaceService, 
  type WorkspaceOverviewResponse, 
  type ModuleStats,
  type Activity 
} from '@/api/workspace'

// 路由和参数
const route = useRoute()
const router = useRouter()
const novelId = computed(() => parseInt(route.params.novelId as string))

// 组件引用
const quickStartGuideRef = ref()
const moduleGridRef = ref()

// 响应式数据
const initialLoading = ref(true)
const overviewData = ref<WorkspaceOverviewResponse>()
const showAIAssistant = ref(false)
const connectionStatus = ref<'connected' | 'disconnected' | 'failed'>('connected')
const refreshTimer = ref<number>()

// 错误状态
const errorState = reactive({
  show: false,
  config: {
    type: 'error' as 'error' | 'warning' | 'info',
    title: '',
    message: '',
    actions: [] as Array<{
      text: string
      type?: string
      handler: () => void
    }>
  }
})

// 计算属性
const moduleProgress = computed(() => {
  if (!overviewData.value?.modules) return {}
  
  const progress: Record<string, number> = {}
  Object.entries(overviewData.value.modules).forEach(([key, value]) => {
    progress[key] = value.completion_percentage || 0
  })
  
  return progress
})

// 方法
const initializeWorkspace = async () => {
  try {
    initialLoading.value = true
    errorState.show = false
    
    // 并行加载核心数据
    const [overview] = await Promise.all([
      WorkspaceService.getOverview(novelId.value)
    ])
    
    // 设置数据
    overviewData.value = overview
    
    // 设置页面标题
    if (overview.novel?.title) {
      document.title = `${overview.novel.title} - 工作台`
    }
    
    ElMessage.success('工作台加载完成')
    
  } catch (error: any) {
    console.error('工作台初始化失败:', error)
    handleInitializationError(error)
  } finally {
    initialLoading.value = false
  }
}

const handleInitializationError = (error: any) => {
  const { status } = error.response || {}
  
  switch (status) {
    case 404:
      errorState.show = true
      errorState.config = {
        type: 'warning',
        title: '小说不存在',
        message: '您访问的小说可能已被删除或不存在',
        actions: [
          {
            text: '返回小说列表',
            type: 'primary',
            handler: () => router.push('/novels')
          }
        ]
      }
      break
      
    case 403:
      errorState.show = true
      errorState.config = {
        type: 'warning',
        title: '无权限访问',
        message: '您没有权限访问此工作台',
        actions: [
          {
            text: '返回首页',
            type: 'primary',
            handler: () => router.push('/')
          }
        ]
      }
      break
      
    default:
      errorState.show = true
      errorState.config = {
        type: 'error',
        title: '加载失败',
        message: '工作台数据加载失败，请刷新页面重试',
        actions: [
          {
            text: '重新加载',
            type: 'primary',
            handler: () => window.location.reload()
          },
          {
            text: '返回小说列表',
            handler: () => router.push('/novels')
          }
        ]
      }
  }
}

const refreshWorkspaceData = async () => {
  try {
    const overview = await WorkspaceService.getOverview(novelId.value)
    overviewData.value = overview
    
    // 通知模块网格刷新
    if (moduleGridRef.value) {
      moduleGridRef.value.refreshAllModules()
    }
    
    ElMessage.success('数据已刷新')
    
  } catch (error) {
    console.error('刷新数据失败:', error)
    ElMessage.error('刷新失败，请稍后重试')
  }
}

const handleModuleUpdated = (moduleName: string, data: ModuleStats) => {
  if (overviewData.value?.modules) {
    overviewData.value.modules[moduleName as keyof typeof overviewData.value.modules] = data
  }
  
  // 更新快速引导的进度
  if (quickStartGuideRef.value && data.completion_percentage > 0) {
    quickStartGuideRef.value.markStepCompleted(moduleName)
  }
}

const handleOpenAIAssistant = () => {
  showAIAssistant.value = true
  
  // 记录使用行为
  console.log('AI助手被打开:', {
    novel_id: novelId.value,
    timestamp: new Date().toISOString()
  })
}

const handleCloseAIAssistant = () => {
  showAIAssistant.value = false
}

const handleGuideSkip = () => {
  ElMessage.info('您可以随时在帮助菜单中重新打开新手引导')
}

const handleGuideComplete = () => {
  ElNotification({
    title: '恭喜！',
    message: '您已完成新手引导，现在可以开始创作您的精彩小说了！',
    type: 'success',
    duration: 5000,
    position: 'top-right'
  })
}

const handleStepCompleted = (stepId: string) => {
  console.log('引导步骤完成:', stepId)
  
  // 可以在这里记录用户行为或发送统计数据
}

const startPeriodicRefresh = () => {
  // 每5分钟自动刷新一次统计数据
  refreshTimer.value = setInterval(async () => {
    try {
      const stats = await WorkspaceService.getWritingStats(novelId.value)
      if (overviewData.value) {
        overviewData.value.writing_stats = stats
      }
    } catch (error) {
      console.warn('定时刷新统计数据失败:', error)
    }
  }, 5 * 60 * 1000)
}

const handleVisibilityChange = () => {
  if (!document.hidden) {
    // 页面重新可见时刷新数据
    setTimeout(() => {
      refreshWorkspaceData()
    }, 1000)
  }
}

// 公开方法给其他组件使用
const showQuickGuide = () => {
  if (quickStartGuideRef.value) {
    quickStartGuideRef.value.showQuickGuide()
  }
}

const refreshModule = async (moduleName: string) => {
  if (moduleGridRef.value) {
    await moduleGridRef.value.refreshModule(moduleName)
  }
}

// 暴露方法
defineExpose({
  showQuickGuide,
  refreshModule,
  refreshWorkspaceData
})

// 生命周期
onMounted(() => {
  initializeWorkspace()
  
  // 启动定时刷新
  nextTick(() => {
    startPeriodicRefresh()
  })
  
  // 监听页面可见性变化
  document.addEventListener('visibilitychange', handleVisibilityChange)
})

onUnmounted(() => {
  // 清理定时器
  if (refreshTimer.value) {
    clearInterval(refreshTimer.value)
  }
  
  // 清理事件监听器
  document.removeEventListener('visibilitychange', handleVisibilityChange)
  
  // 恢复页面标题
  document.title = 'AI小说创作平台'
})
</script>

<style scoped lang="scss">
.workspace-overview {
  min-height: calc(100vh - 120px);
  background: #F8F9FA;
  padding: 24px;

  .loading-container {
    max-width: 1200px;
    margin: 0 auto;
    background: white;
    padding: 24px;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }

  .error-container {
    max-width: 800px;
    margin: 0 auto;
    background: white;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    padding: 40px;
  }

  .workspace-content {
    max-width: 1400px;
    margin: 0 auto;
  }

  .ai-assistant-content {
    padding: 20px 0;
  }
}

// 响应式设计
@media (max-width: 1023px) {
  .workspace-overview {
    padding: 16px;
  }
}

@media (max-width: 767px) {
  .workspace-overview {
    padding: 12px;
    
    .error-container {
      padding: 24px;
    }
  }
}

// 连接状态指示器
.connection-status {
  position: fixed;
  top: 80px;
  right: 20px;
  z-index: 1000;
  padding: 8px 12px;
  border-radius: 20px;
  font-size: 12px;
  color: white;
  
  &.connected {
    background: #67C23A;
  }
  
  &.disconnected {
    background: #E6A23C;
  }
  
  &.failed {
    background: #F56C6C;
  }
}

// 滚动条样式
:deep(.el-scrollbar__wrap) {
  scrollbar-width: thin;
  scrollbar-color: #C0C4CC transparent;
}

:deep(.el-scrollbar__wrap::-webkit-scrollbar) {
  width: 6px;
}

:deep(.el-scrollbar__wrap::-webkit-scrollbar-track) {
  background: transparent;
}

:deep(.el-scrollbar__wrap::-webkit-scrollbar-thumb) {
  background-color: #C0C4CC;
  border-radius: 3px;
}

:deep(.el-scrollbar__wrap::-webkit-scrollbar-thumb:hover) {
  background-color: #909399;
}
</style>