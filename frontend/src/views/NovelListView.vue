<template>
  <div class="novel-list-view">
    <!-- 页面头部 -->
    <PageHeader 
      :loading="loadingStates.initial"
      @create-novel="createNovel"
      @refresh="handleRefresh"
      @search="handleSearch"
    />
    
    <!-- 筛选工具栏 -->
    <NovelFilters
      v-model:filters="filters"
      v-model:sort-config="sortConfig"
      v-model:view-mode="viewMode"
      :loading="loadingStates.refresh"
      @reset="resetFilters"
      @refresh="handleRefresh"
    />
    
    <!-- 批量操作栏 -->
    <BatchOperationBar
      v-if="selectedNovels.length > 0"
      :selected-count="selectedNovels.length"
      :loading="loadingStates.batchOperation"
      @batch-delete="handleBatchDelete"
      @batch-export="handleBatchExport"
      @batch-status-change="handleBatchStatusChange"
      @clear-selection="clearSelection"
    />
    
    <!-- 小说列表区域 -->
    <div class="novel-content-area">
      <el-loading :loading="loadingStates.initial" element-loading-text="加载中...">
        <!-- 网格视图 -->
        <NovelGrid
          v-if="viewMode === 'grid'"
          :novels="novels"
          :loading="loadingStates.refresh"
          v-model:selected="selectedNovels"
          @view-detail="viewDetail"
          @enter-workspace="enterWorkspace"
          @export-novel="exportNovel"
          @delete-novel="deleteNovel"
        />
        
        <!-- 表格视图 -->
        <NovelTable
          v-else
          :novels="novels"
          :loading="loadingStates.refresh"
          v-model:selected="selectedNovels"
          @view-detail="viewDetail"
          @enter-workspace="enterWorkspace"
          @export-novel="exportNovel"
          @delete-novel="deleteNovel"
        />
        
        <!-- 空状态 -->
        <el-empty
          v-if="!loadingStates.initial && novels.length === 0"
          :image="emptyStateConfig.image"
          :description="emptyStateConfig.description"
        >
          <template #default>
            <h3>{{ emptyStateConfig.title }}</h3>
            <p>{{ emptyStateConfig.description }}</p>
          </template>
          <template #extra>
            <el-button
              v-for="action in emptyStateConfig.actions"
              :key="action.text"
              :type="action.type"
              @click="action.handler"
            >
              {{ action.text }}
            </el-button>
          </template>
        </el-empty>
      </el-loading>
    </div>
    
    <!-- 分页组件 -->
    <PaginationBar
      v-if="!loadingStates.initial && totalPages > 1"
      :current-page="currentPage"
      :page-size="pageSize"
      :total="totalNovels"
      :total-pages="totalPages"
      @page-change="handlePageChange"
      @size-change="handleSizeChange"
    />
    
    <!-- 导出对话框 -->
    <ExportDialog
      v-model:visible="showExportDialog"
      :novel="selectedNovelForExport"
      :loading="loadingStates.export"
      @export="handleExportConfirm"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { debounce } from 'lodash-es'

// 导入组件
import PageHeader from '@/components/novels/PageHeader.vue'
import NovelFilters from '@/components/novels/NovelFilters.vue'
import NovelGrid from '@/components/novels/NovelGrid.vue'
import NovelTable from '@/components/novels/NovelTable.vue'
import BatchOperationBar from '@/components/novels/BatchOperationBar.vue'
import ExportDialog from '@/components/novels/ExportDialog.vue'
import PaginationBar from '@/components/novels/PaginationBar.vue'

// 导入API和类型
import { NovelService, type NovelListItem, type NovelSearchParams } from '@/api/novels'

const router = useRouter()

// 响应式数据
const novels = ref<NovelListItem[]>([])
const selectedNovels = ref<number[]>([])
const currentPage = ref(1)
const pageSize = ref(20)
const totalNovels = ref(0)
const totalPages = ref(0)
const viewMode = ref<'grid' | 'table'>('grid')
const searchKeyword = ref('')
const showExportDialog = ref(false)
const selectedNovelForExport = ref<NovelListItem | null>(null)

// 加载状态
const loadingStates = reactive({
  initial: false,
  refresh: false,
  delete: false,
  export: false,
  batchOperation: false
})

// 筛选条件
const filters = reactive({
  status: null as string | null,
  genre: null as string | null,
  dateFrom: null as string | null,
  dateTo: null as string | null
})

// 排序配置
const sortConfig = reactive({
  sortBy: 'updated_at' as string,
  sortOrder: 'desc' as 'asc' | 'desc'
})

// 计算属性
const hasFilters = computed(() => {
  return !!(filters.status || filters.genre || filters.dateFrom || filters.dateTo || searchKeyword.value)
})

const emptyStateConfig = computed(() => {
  if (hasFilters.value) {
    return {
      image: '/images/no-results.svg',
      title: '没有找到匹配的小说',
      description: '尝试调整筛选条件或清空筛选器',
      actions: [
        {
          text: '清空筛选',
          type: 'primary' as const,
          handler: resetFilters
        }
      ]
    }
  } else {
    return {
      image: '/images/empty-novels.svg',
      title: '还没有创作任何小说',
      description: '开始您的第一部小说创作吧',
      actions: [
        {
          text: '创建小说',
          type: 'primary' as const,
          handler: () => router.push('/novel-create')
        }
      ]
    }
  }
})

// 生命周期
onMounted(async () => {
  await loadNovels()
})

// 监听筛选条件变化
watch([filters, sortConfig, searchKeyword], 
  debounce(async () => {
    currentPage.value = 1
    await loadNovels()
  }, 300),
  { deep: true }
)

// 方法
const loadNovels = async () => {
  try {
    loadingStates.initial = novels.value.length === 0
    loadingStates.refresh = novels.value.length > 0
    
    const params: NovelSearchParams = {
      page: currentPage.value,
      page_size: pageSize.value,
      sort_by: sortConfig.sortBy,
      sort_order: sortConfig.sortOrder
    }
    
    // 添加筛选条件
    if (searchKeyword.value) params.search = searchKeyword.value
    if (filters.status) params.status = filters.status
    if (filters.genre) params.genre = filters.genre
    if (filters.dateFrom) params.date_from = filters.dateFrom
    if (filters.dateTo) params.date_to = filters.dateTo
    
    const response = await NovelService.getNovels(params)
    
    if (response.status === 'success') {
      novels.value = response.data.novels
      totalNovels.value = response.data.total
      totalPages.value = response.data.total_pages
    } else {
      throw new Error(response.message || '获取小说列表失败')
    }
    
  } catch (error: any) {
    console.error('加载小说列表失败:', error)
    ElMessage.error(error.message || '加载小说列表失败')
  } finally {
    loadingStates.initial = false
    loadingStates.refresh = false
  }
}

const createNovel = () => {
  router.push('/novel-create')
}

const handleRefresh = async () => {
  await loadNovels()
  ElMessage.success('刷新成功')
}

const handleSearch = (keyword: string) => {
  searchKeyword.value = keyword
}

const resetFilters = () => {
  Object.assign(filters, {
    status: null,
    genre: null,
    dateFrom: null,
    dateTo: null
  })
  searchKeyword.value = ''
  currentPage.value = 1
}

const clearSelection = () => {
  selectedNovels.value = []
}

const handlePageChange = (page: number) => {
  currentPage.value = page
  loadNovels()
}

const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
  loadNovels()
}

// 小说操作
const viewDetail = (novelId: number) => {
  router.push(`/novels/${novelId}`)
}

const enterWorkspace = (novelId: number) => {
  router.push(`/workspace/${novelId}/characters`)
}

const exportNovel = (novel: NovelListItem) => {
  selectedNovelForExport.value = novel
  showExportDialog.value = true
}

const handleExportConfirm = async (exportOptions: any) => {
  try {
    loadingStates.export = true
    
    if (selectedNovelForExport.value) {
      const response = await NovelService.exportNovel(selectedNovelForExport.value.id, exportOptions)
      
      if (response.status === 'success') {
        ElMessage.success('导出任务已创建，请稍后查看下载链接')
        showExportDialog.value = false
        
        // 可以在这里处理下载链接，比如打开新窗口或显示下载状态
        console.log('导出信息:', response.data)
      } else {
        throw new Error(response.message || '导出失败')
      }
    }
  } catch (error: any) {
    console.error('导出失败:', error)
    ElMessage.error(error.message || '导出失败')
  } finally {
    loadingStates.export = false
  }
}

const deleteNovel = async (novel: NovelListItem) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除小说《${novel.title}》吗？此操作不可恢复。`,
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }
    )
    
    loadingStates.delete = true
    const response = await NovelService.deleteNovel(novel.id)
    
    if (response.status === 'success') {
      await loadNovels()
      ElMessage.success('小说删除成功')
    } else {
      throw new Error(response.message || '删除失败')
    }
    
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error(error.message || '删除失败')
    }
  } finally {
    loadingStates.delete = false
  }
}

// 批量操作
const handleBatchDelete = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedNovels.value.length} 部小说吗？此操作不可恢复。`,
      '批量删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }
    )
    
    loadingStates.batchOperation = true
    
    const response = await NovelService.batchDeleteNovels(selectedNovels.value)
    
    if (response.status === 'success') {
      await loadNovels()
      clearSelection()
      ElMessage.success(`批量删除完成，成功 ${response.data.success_count} 个，失败 ${response.data.failed_count} 个`)
    } else {
      throw new Error(response.message || '批量删除失败')
    }
    
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('批量删除失败:', error)
      ElMessage.error(error.message || '批量删除失败')
    }
  } finally {
    loadingStates.batchOperation = false
  }
}

const handleBatchExport = async (format: string) => {
  try {
    loadingStates.batchOperation = true
    
    const response = await NovelService.batchExportNovels(selectedNovels.value, format)
    
    if (response.status === 'success') {
      ElMessage.success('批量导出任务已创建，请稍后查看下载链接')
      console.log('批量导出信息:', response.data)
    } else {
      throw new Error(response.message || '批量导出失败')
    }
  } catch (error: any) {
    console.error('批量导出失败:', error)
    ElMessage.error(error.message || '批量导出失败')
  } finally {
    loadingStates.batchOperation = false
  }
}

const handleBatchStatusChange = async (status: string) => {
  try {
    loadingStates.batchOperation = true
    
    const response = await NovelService.batchUpdateStatus(selectedNovels.value, status)
    
    if (response.status === 'success') {
      await loadNovels()
      clearSelection()
      ElMessage.success(`批量状态修改完成，成功 ${response.data.success_count} 个，失败 ${response.data.failed_count} 个`)
    } else {
      throw new Error(response.message || '批量状态修改失败')
    }
  } catch (error: any) {
    console.error('批量状态修改失败:', error)
    ElMessage.error(error.message || '批量状态修改失败')
  } finally {
    loadingStates.batchOperation = false
  }
}
</script>

<style lang="scss" scoped>
.novel-list-view {
  min-height: 100vh;
  background-color: #f8f9fa;
  width: 100%;
  
  // 为每个主要区域添加容器和内边距
  > * {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
  }
  
  .novel-content-area {
    margin: 20px auto;
    min-height: 400px;
    max-width: 1200px;
    padding: 0 20px;
  }
}

// 响应式设计
@media (max-width: 768px) {
  .novel-list-view {
    > * {
      padding: 0 10px;
    }
    
    .novel-content-area {
      margin: 10px auto;
      padding: 0 10px;
    }
  }
}

// 平板设备
@media (max-width: 1024px) and (min-width: 769px) {
  .novel-list-view {
    > * {
      padding: 0 16px;
    }
    
    .novel-content-area {
      padding: 0 16px;
    }
  }
}

// 大屏幕设备
@media (min-width: 1240px) {
  .novel-list-view {
    > * {
      max-width: 1400px;
    }
    
    .novel-content-area {
      max-width: 1400px;
    }
  }
}
</style>