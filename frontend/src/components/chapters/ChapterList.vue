<template>
  <div class="chapter-list">
    <div class="list-header">
      <div class="header-left">
        <h3>章节列表</h3>
        <el-tag v-if="stats" type="info">
          共 {{ stats.total_chapters }} 章 / {{ stats.total_words }} 字
        </el-tag>
      </div>
      
      <div class="header-actions">
        <el-select
          v-model="filterStatus"
          placeholder="状态筛选"
          clearable
          size="small"
          style="width: 120px;"
          @change="handleFilterChange"
        >
          <el-option label="草稿" value="draft" />
          <el-option label="已完成" value="completed" />
          <el-option label="已发布" value="published" />
        </el-select>
        
        <el-input
          v-model="searchKeyword"
          placeholder="搜索章节"
          size="small"
          style="width: 180px;"
          @input="handleSearch"
          clearable
        >
          <template #prefix>
            <el-icon><i class="fas fa-search"></i></el-icon>
          </template>
        </el-input>
        
        <el-button type="primary" size="small" @click="$emit('create-chapter')">
          新建章节
        </el-button>
        
        <el-dropdown @command="handleBatchAction" v-if="selectedChapters.length > 0">
          <el-button size="small">
            批量操作<el-icon class="el-icon--right"><arrow-down /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="update-status-draft">设为草稿</el-dropdown-item>
              <el-dropdown-item command="update-status-completed">设为完成</el-dropdown-item>
              <el-dropdown-item command="update-status-published">设为发布</el-dropdown-item>
              <el-dropdown-item command="delete" divided>删除选中</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>
    
    <div class="list-body">
      <el-table
        ref="tableRef"
        :data="chapters"
        v-loading="loading"
        @selection-change="handleSelectionChange"
        @row-click="handleRowClick"
        stripe
        height="100%"
      >
        <el-table-column type="selection" width="55" />
        
        <el-table-column prop="chapter_number" label="章节号" width="80" sortable>
          <template #default="scope">
            <span class="chapter-number">第{{ scope.row.chapter_number }}章</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="title" label="标题" min-width="200">
          <template #default="scope">
            <div class="chapter-title">
              <span>{{ scope.row.title }}</span>
              <el-tag
                v-if="scope.row.version > 1"
                size="small"
                type="warning"
                style="margin-left: 8px;"
              >
                v{{ scope.row.version }}
              </el-tag>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="word_count" label="字数" width="100" sortable>
          <template #default="scope">
            <span :class="getWordCountClass(scope.row.word_count)">
              {{ scope.row.word_count.toLocaleString() }}
            </span>
          </template>
        </el-table-column>
        
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusColor(scope.row.status)" size="small">
              {{ getStatusLabel(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="character_count" label="角色数" width="80">
          <template #default="scope">
            <el-badge :value="scope.row.character_count" type="primary" v-if="scope.row.character_count > 0">
              <el-icon><user /></el-icon>
            </el-badge>
            <span v-else>-</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="updated_at" label="更新时间" width="160" sortable>
          <template #default="scope">
            {{ formatTime(scope.row.updated_at) }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="scope">
            <el-button-group>
              <el-button size="small" @click.stop="editChapter(scope.row)">
                编辑
              </el-button>
              <el-dropdown @command="(cmd) => handleAction(cmd, scope.row)" @click.stop>
                <el-button size="small">
                  更多<el-icon class="el-icon--right"><arrow-down /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="duplicate">复制章节</el-dropdown-item>
                    <el-dropdown-item command="export">导出章节</el-dropdown-item>
                    <el-dropdown-item command="preview">预览</el-dropdown-item>
                    <el-dropdown-item command="status">状态管理</el-dropdown-item>
                    <el-dropdown-item command="delete" divided>删除</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>
    </div>
    
    <div class="list-footer" v-if="pagination.total > 0">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
      />
    </div>
    
    <!-- 状态更新对话框 -->
    <el-dialog v-model="showStatusDialog" title="状态管理" width="400px">
      <el-form :model="statusForm" label-width="80px">
        <el-form-item label="当前状态">
          <el-tag :type="getStatusColor(currentChapter?.status)">
            {{ getStatusLabel(currentChapter?.status) }}
          </el-tag>
        </el-form-item>
        <el-form-item label="新状态">
          <el-radio-group v-model="statusForm.newStatus">
            <el-radio label="draft">草稿</el-radio>
            <el-radio label="completed">已完成</el-radio>
            <el-radio label="published">已发布</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showStatusDialog = false">取消</el-button>
        <el-button type="primary" @click="updateStatus" :loading="updating">
          更新状态
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowDown, User } from '@element-plus/icons-vue'
import * as chaptersApi from '@/api/chapters'

// Props
const props = defineProps({
  novelId: {
    type: Number,
    required: true
  },
  stats: {
    type: Object,
    default: null
  }
})

// Emits
const emit = defineEmits(['chapter-selected', 'create-chapter', 'edit-chapter', 'refresh-stats'])

// 响应式数据
const chapters = ref([])
const loading = ref(false)
const selectedChapters = ref([])
const filterStatus = ref('')
const searchKeyword = ref('')
const showStatusDialog = ref(false)
const currentChapter = ref(null)
const updating = ref(false)

// 分页数据
const pagination = ref({
  page: 1,
  pageSize: 20,
  total: 0
})

// 表单数据
const statusForm = ref({
  newStatus: 'draft'
})

// 计算属性
const tableRef = ref(null)

// 方法
const loadChapters = async () => {
  try {
    loading.value = true
    const params = {
      novel_id: props.novelId,
      page: pagination.value.page,
      size: pagination.value.pageSize,
      sort_by: 'chapter_number',
      sort_order: 'asc'
    }
    
    if (filterStatus.value) {
      params.status = filterStatus.value
    }
    
    if (searchKeyword.value.trim()) {
      params.keyword = searchKeyword.value.trim()
    }
    
    const data = await chaptersApi.getChapters(params)
    chapters.value = data.items || []
    pagination.value.total = data.total
    
  } catch (error) {
    console.error('加载章节列表失败:', error)
    ElMessage.error('加载章节列表失败')
  } finally {
    loading.value = false
  }
}

const handleSelectionChange = (selection) => {
  selectedChapters.value = selection
}

const handleRowClick = (row) => {
  emit('chapter-selected', row)
}

const handleFilterChange = () => {
  pagination.value.page = 1
  loadChapters()
}

const handleSearch = () => {
  pagination.value.page = 1
  loadChapters()
}

const handlePageChange = (page) => {
  pagination.value.page = page
  loadChapters()
}

const handleSizeChange = (size) => {
  pagination.value.pageSize = size
  pagination.value.page = 1
  loadChapters()
}

const editChapter = (chapter) => {
  emit('edit-chapter', chapter)
}

const handleAction = async (command, chapter) => {
  switch (command) {
    case 'duplicate':
      await duplicateChapter(chapter)
      break
    case 'export':
      exportChapter(chapter)
      break
    case 'preview':
      previewChapter(chapter)
      break
    case 'status':
      openStatusDialog(chapter)
      break
    case 'delete':
      await deleteChapter(chapter)
      break
  }
}

const handleBatchAction = async (command) => {
  const chapterIds = selectedChapters.value.map(c => c.id)
  
  try {
    if (command.startsWith('update-status-')) {
      const status = command.replace('update-status-', '')
      await chaptersApi.batchOperateChapters({
        chapter_ids: chapterIds,
        operation: 'update_status',
        operation_data: { status }
      })
      ElMessage.success('状态更新成功')
    } else if (command === 'delete') {
      await ElMessageBox.confirm('确定要删除选中的章节吗？', '确认删除', {
        type: 'warning'
      })
      
      await chaptersApi.batchOperateChapters({
        chapter_ids: chapterIds,
        operation: 'delete'
      })
      ElMessage.success('删除成功')
    }
    
    // 清空选择并刷新列表
    tableRef.value?.clearSelection()
    selectedChapters.value = []
    await loadChapters()
    emit('refresh-stats')
    
  } catch (error) {
    if (error !== 'cancel') {
      console.error('批量操作失败:', error)
      ElMessage.error('操作失败')
    }
  }
}

const duplicateChapter = async (chapter) => {
  try {
    const maxChapter = Math.max(...chapters.value.map(c => c.chapter_number))
    await chaptersApi.createChapter({
      novel_id: props.novelId,
      title: `${chapter.title} (副本)`,
      content: '', // 复制时不复制内容，避免重复
      chapter_number: maxChapter + 1,
      character_ids: [],
      notes: `复制自第${chapter.chapter_number}章`
    })
    
    ElMessage.success('章节复制成功')
    await loadChapters()
    emit('refresh-stats')
  } catch (error) {
    console.error('复制章节失败:', error)
    ElMessage.error('复制失败')
  }
}

const exportChapter = (chapter) => {
  // 导出功能实现
  ElMessage.info('导出功能开发中...')
}

const previewChapter = (chapter) => {
  // 预览功能实现
  ElMessage.info('预览功能开发中...')
}

const openStatusDialog = (chapter) => {
  currentChapter.value = chapter
  statusForm.value.newStatus = chapter.status
  showStatusDialog.value = true
}

const updateStatus = async () => {
  try {
    updating.value = true
    await chaptersApi.updateChapterStatus(
      currentChapter.value.id,
      statusForm.value.newStatus
    )
    
    ElMessage.success('状态更新成功')
    showStatusDialog.value = false
    await loadChapters()
    emit('refresh-stats')
    
  } catch (error) {
    console.error('状态更新失败:', error)
    ElMessage.error('状态更新失败')
  } finally {
    updating.value = false
  }
}

const deleteChapter = async (chapter) => {
  try {
    await ElMessageBox.confirm(`确定要删除第${chapter.chapter_number}章吗？`, '确认删除', {
      type: 'warning'
    })
    
    await chaptersApi.deleteChapter(chapter.id)
    ElMessage.success('删除成功')
    await loadChapters()
    emit('refresh-stats')
    
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除章节失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

const getStatusColor = (status) => {
  const colors = {
    draft: 'info',
    completed: 'success',
    published: 'warning'
  }
  return colors[status] || 'info'
}

const getStatusLabel = (status) => {
  const labels = {
    draft: '草稿',
    completed: '已完成',
    published: '已发布'
  }
  return labels[status] || status
}

const getWordCountClass = (count) => {
  if (count < 1000) return 'word-count-low'
  if (count < 3000) return 'word-count-medium'
  return 'word-count-high'
}

const formatTime = (time) => {
  if (!time) return ''
  return new Date(time).toLocaleString()
}

// 监听器
watch(() => props.novelId, () => {
  if (props.novelId) {
    loadChapters()
  }
})

// 生命周期
onMounted(() => {
  if (props.novelId) {
    loadChapters()
  }
})

// 暴露方法
defineExpose({
  loadChapters,
  clearSelection: () => {
    tableRef.value?.clearSelection()
    selectedChapters.value = []
  }
})
</script>

<style scoped>
.chapter-list {
  height: 100%;
  display: flex;
  flex-direction: column;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: #f5f7fa;
  border-bottom: 1px solid #e4e7ed;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-left h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.list-body {
  flex: 1;
  overflow: hidden;
}

.list-footer {
  padding: 16px 20px;
  border-top: 1px solid #e4e7ed;
  background: #fafafa;
  display: flex;
  justify-content: center;
}

.chapter-number {
  font-weight: 500;
  color: #409eff;
}

.chapter-title {
  display: flex;
  align-items: center;
}

.word-count-low {
  color: #f56c6c;
}

.word-count-medium {
  color: #e6a23c;
}

.word-count-high {
  color: #67c23a;
}

/* 表格行点击效果 */
.el-table :deep(.el-table__body tr:hover) {
  cursor: pointer;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .list-header {
    flex-direction: column;
    gap: 12px;
    padding: 12px 16px;
  }
  
  .header-actions {
    width: 100%;
    justify-content: space-between;
  }
  
  .list-footer {
    padding: 12px 16px;
  }
}
</style>