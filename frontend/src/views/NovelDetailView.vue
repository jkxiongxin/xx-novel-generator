<template>
  <div class="novel-detail-view">
    <!-- 页面头部 -->
    <div class="page-header">
      <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
        <el-breadcrumb-item :to="{ path: '/novels' }">我的小说</el-breadcrumb-item>
        <el-breadcrumb-item>{{ novel?.title || '小说详情' }}</el-breadcrumb-item>
      </el-breadcrumb>
      
      <el-button 
        type="primary" 
        :icon="ArrowLeft" 
        @click="goBack"
        class="back-button"
      >
        返回列表
      </el-button>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading.basic" class="loading-container">
      <el-skeleton :rows="8" animated />
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="error-container">
      <el-result
        icon="error"
        :title="error.title"
        :sub-title="error.message"
      >
        <template #extra>
          <el-button type="primary" @click="loadNovelData">重新加载</el-button>
          <el-button @click="goBack">返回列表</el-button>
        </template>
      </el-result>
    </div>

    <!-- 主要内容 -->
    <div v-else-if="novel" class="novel-content">
      <!-- 小说基本信息卡片 -->
      <NovelInfoCard
        :novel="novel"
        :editing="editing.basicInfo"
        @edit="handleEdit"
        @save="handleSave"
        @cancel="handleCancel"
        @enter-workspace="enterWorkspace"
        @open-settings="openSettings"
        @upload-cover="handleUploadCover"
      />

      <!-- 统计和概览区域 -->
      <el-row :gutter="24" class="stats-overview-section">
        <!-- 统计数据 -->
        <el-col :xs="24" :sm="24" :md="12" :lg="8">
          <StatsCard 
            :stats="novel.stats"
            :loading="loading.stats"
            @refresh="loadStats"
          />
        </el-col>

        <!-- 内容概览 -->
        <el-col :xs="24" :sm="24" :md="12" :lg="16">
          <ContentOverview
            :overview="novel.content_overview"
            :novel="novel"
            @quick-access="handleQuickAccess"
          />
        </el-col>
      </el-row>

      <!-- 进度和活动区域 -->
      <el-row :gutter="24" class="progress-activity-section">
        <!-- 进度展示 -->
        <el-col :xs="24" :sm="24" :md="12">
          <ProgressSection
            :novel="novel"
            @quick-access="handleQuickAccess"
          />
        </el-col>

        <!-- 最近活动 -->
        <el-col :xs="24" :sm="24" :md="12">
          <RecentActivity
            :activities="recentActivities"
            :loading="loading.activities"
            @refresh="loadActivities"
          />
        </el-col>
      </el-row>
    </div>

    <!-- 设置对话框 -->
    <NovelSettingsDialog
      v-model="showSettingsDialog"
      :novel="novel"
      @save="handleSettingsSave"
    />

    <!-- 分享对话框 -->
    <ShareDialog
      v-model="showShareDialog"
      :novel="novel"
      @share="handleShare"
    />

    <!-- 导出对话框 -->
    <ExportDialog
      v-model="showExportDialog"
      :novel="novel"
      @export="handleExport"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElNotification, ElMessageBox } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'

// 导入组件
import NovelInfoCard from '@/components/novels/NovelInfoCard.vue'
import StatsCard from '@/components/novels/StatsCard.vue'
import ContentOverview from '@/components/novels/ContentOverview.vue'
import ProgressSection from '@/components/novels/ProgressSection.vue'
import RecentActivity from '@/components/novels/RecentActivity.vue'
import NovelSettingsDialog from '@/components/novels/NovelSettingsDialog.vue'
import ShareDialog from '@/components/novels/ShareDialog.vue'
import ExportDialog from '@/components/novels/ExportDialog.vue'

// 导入API和类型
import { NovelService, type NovelDetailResponse, type Activity, NovelUtils } from '@/api/novels'

const route = useRoute()
const router = useRouter()

// 响应式数据
const novel = ref<NovelDetailResponse | null>(null)
const recentActivities = ref<Activity[]>([])
const error = ref<{ title: string; message: string } | null>(null)

// 加载状态
const loading = reactive({
  basic: true,
  stats: false,
  activities: false,
  saving: false
})

// 编辑状态
const editing = reactive<Record<string, boolean>>({
  basicInfo: false,
  description: false,
  tags: false
})

// 对话框状态
const showSettingsDialog = ref(false)
const showShareDialog = ref(false)
const showExportDialog = ref(false)

// 计算属性
const novelId = computed(() => {
  const id = route.params.novelId
  return Array.isArray(id) ? parseInt(id[0]) : parseInt(id as string)
})

// 页面标题
watch(() => novel.value?.title, (title) => {
  if (title) {
    document.title = `${title} - 小说详情`
  }
}, { immediate: true })

// 路由参数变化时重新加载
watch(() => route.params.novelId, async (newId) => {
  if (newId) {
    await loadNovelData()
  }
})

// 方法定义
const goBack = () => {
  router.push('/novels')
}

const loadNovelData = async () => {
  try {
    loading.basic = true
    error.value = null

    // 并行加载基本数据
    const [novelDetail, activities] = await Promise.all([
      NovelService.getNovelDetail(novelId.value),
      NovelService.getRecentActivities(novelId.value, 10).catch(() => ({ activities: [], total: 0 }))
    ])

    novel.value = novelDetail
    recentActivities.value = activities.activities

  } catch (err: any) {
    handleLoadError(err)
  } finally {
    loading.basic = false
  }
}

const loadStats = async () => {
  if (!novel.value) return
  
  try {
    loading.stats = true
    const stats = await NovelService.getNovelStatsDetail(novelId.value)
    if (novel.value) {
      // 合并统计数据，保持原有结构并补充缺失字段
      novel.value.stats = {
        ...novel.value.stats,
        total_words: stats.basic_stats.total_words,
        total_chapters: stats.basic_stats.total_chapters,
        completed_chapters: stats.basic_stats.completed_chapters,
        average_words_per_chapter: stats.basic_stats.average_chapter_length,
        draft_chapters: stats.basic_stats.total_chapters - stats.basic_stats.completed_chapters,
        estimated_completion_time: undefined,
        writing_days: stats.writing_stats.writing_days,
        average_daily_words: stats.writing_stats.average_daily_words
      }
    }
  } catch (err) {
    console.warn('Failed to load stats:', err)
  } finally {
    loading.stats = false
  }
}

const loadActivities = async () => {
  try {
    loading.activities = true
    const activities = await NovelService.getRecentActivities(novelId.value, 10)
    recentActivities.value = activities.activities
  } catch (err) {
    console.warn('Failed to load activities:', err)
  } finally {
    loading.activities = false
  }
}

const handleLoadError = (err: any) => {
  const status = err.response?.status
  
  switch (status) {
    case 404:
      error.value = {
        title: '小说不存在',
        message: '您访问的小说可能已被删除或不存在'
      }
      break
    case 403:
      error.value = {
        title: '无权限访问',
        message: '您没有权限查看此小说'
      }
      break
    default:
      error.value = {
        title: '加载失败',
        message: '请检查网络连接后重试'
      }
  }
}

const handleEdit = (field: string) => {
  editing[field] = true
}

const handleSave = async (field: string, data: any) => {
  try {
    loading.saving = true
    
    await NovelService.updateNovel(novelId.value, data)
    
    // 更新本地数据
    if (novel.value) {
      Object.assign(novel.value, data)
    }
    
    editing[field] = false
    ElMessage.success('保存成功')
    
  } catch (err: any) {
    ElMessage.error(err.response?.data?.message || '保存失败')
  } finally {
    loading.saving = false
  }
}

const handleCancel = (field: string) => {
  editing[field] = false
}

const enterWorkspace = () => {
  router.push(`/workspace/${novelId.value}`)
}

const openSettings = () => {
  showSettingsDialog.value = true
}

const handleSettingsSave = async (settings: any) => {
  try {
    await NovelService.updateNovel(novelId.value, settings)
    
    // 更新本地数据
    if (novel.value) {
      Object.assign(novel.value, settings)
    }
    
    showSettingsDialog.value = false
    ElMessage.success('设置保存成功')
    
  } catch (err: any) {
    ElMessage.error(err.response?.data?.message || '设置保存失败')
  }
}

const handleUploadCover = async (file: File) => {
  try {
    const result = await NovelService.uploadCover(novelId.value, file)
    
    if (novel.value) {
      novel.value.cover_image = result.cover_url
    }
    
    ElMessage.success('封面上传成功')
    
  } catch (err: any) {
    ElMessage.error(err.response?.data?.message || '封面上传失败')
  }
}

const handleQuickAccess = (module: string) => {
  router.push(`/workspace/${novelId.value}/${module}`)
}

const handleShare = async (options: any) => {
  try {
    const result = await NovelService.createShareLink(novelId.value, options)
    
    // 复制分享链接到剪贴板
    await navigator.clipboard.writeText(result.share_url)
    
    showShareDialog.value = false
    ElNotification({
      title: '分享链接已生成',
      message: '链接已复制到剪贴板',
      type: 'success'
    })
    
  } catch (err: any) {
    ElMessage.error(err.response?.data?.message || '生成分享链接失败')
  }
}

const handleExport = async (options: any) => {
  try {
    const result = await NovelService.exportNovel(novelId.value, options)
    
    showExportDialog.value = false
    ElNotification({
      title: '导出任务已创建',
      message: '文件准备完成后将自动下载',
      type: 'success'
    })
    
    // 可以在这里添加下载逻辑
    
  } catch (err: any) {
    ElMessage.error(err.response?.data?.message || '导出失败')
  }
}

// 生命周期
onMounted(() => {
  loadNovelData()
})
</script>

<style scoped lang="scss">
.novel-detail-view {
  min-height: 100vh;
  background-color: #f5f7fa;
  padding: 20px;

  @media (max-width: 768px) {
    padding: 12px;
  }
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding: 16px 24px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);

  @media (max-width: 768px) {
    padding: 12px 16px;
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }

  .back-button {
    @media (max-width: 768px) {
      width: 100%;
    }
  }
}

.loading-container,
.error-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
}

.novel-content {
  max-width: 1200px;
  margin: 0 auto;
}

.stats-overview-section {
  margin-bottom: 24px;
}

.progress-activity-section {
  margin-bottom: 24px;
}

// 响应式布局
@media (max-width: 1023px) {
  .stats-overview-section,
  .progress-activity-section {
    .el-col {
      margin-bottom: 16px;
    }
  }
}

@media (max-width: 767px) {
  .novel-detail-view {
    padding: 8px;
  }
  
  .page-header {
    margin-bottom: 16px;
  }
  
  .stats-overview-section,
  .progress-activity-section {
    margin-bottom: 16px;
  }
}
</style>