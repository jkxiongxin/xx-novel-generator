<template>
  <div class="admin-character-templates">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="page-title">
          <h1>角色模板管理</h1>
          <p class="subtitle">管理系统中的所有角色模板</p>
        </div>
        <div class="header-actions">
          <el-button 
            type="primary" 
            @click="showCreateDialog = true"
            :icon="Plus"
          >
            创建模板
          </el-button>
        </div>
      </div>
    </div>

    <!-- 搜索和筛选工具栏 -->
    <div class="filter-toolbar">
      <div class="filter-group">
        <div class="filter-item">
          <el-input
            v-model="searchParams.search"
            placeholder="搜索角色名称、描述..."
            :prefix-icon="Search"
            @input="handleSearch"
            clearable
            style="width: 300px;"
          />
        </div>
        
        <div class="filter-item">
          <span class="filter-label">性别:</span>
          <el-select 
            v-model="searchParams.gender" 
            placeholder="全部" 
            clearable
            @change="loadTemplates"
          >
            <el-option label="男性" value="male" />
            <el-option label="女性" value="female" />
            <el-option label="未知" value="unknown" />
            <el-option label="其他" value="other" />
          </el-select>
        </div>

        <div class="filter-item">
          <span class="filter-label">类型:</span>
          <el-select 
            v-model="searchParams.character_type" 
            placeholder="全部" 
            clearable
            @change="loadTemplates"
          >
            <el-option label="主角" value="protagonist" />
            <el-option label="配角" value="supporting" />
            <el-option label="反派" value="antagonist" />
            <el-option label="次要角色" value="minor" />
            <el-option label="路人" value="passerby" />
          </el-select>
        </div>

        <div class="filter-item">
          <span class="filter-label">状态:</span>
          <el-select 
            v-model="statusFilter" 
            placeholder="全部" 
            clearable
            @change="handleStatusFilter"
          >
            <el-option label="热门" value="popular" />
            <el-option label="新增" value="new" />
          </el-select>
        </div>

        <div class="filter-item">
          <span class="filter-label">排序:</span>
          <el-select 
            v-model="searchParams.sort_by" 
            @change="loadTemplates"
          >
            <el-option label="创建时间" value="created_at" />
            <el-option label="更新时间" value="updated_at" />
            <el-option label="角色名称" value="name" />
            <el-option label="使用次数" value="usage_count" />
            <el-option label="评分" value="rating" />
          </el-select>
        </div>

        <div class="filter-item">
          <el-select 
            v-model="searchParams.sort_order" 
            @change="loadTemplates"
          >
            <el-option label="降序" value="desc" />
            <el-option label="升序" value="asc" />
          </el-select>
        </div>

        <div class="filter-actions">
          <el-button @click="resetFilters">重置</el-button>
        </div>
      </div>
    </div>

    <!-- 批量操作工具栏 -->
    <div v-if="selectedTemplates.length > 0" class="batch-actions">
      <div class="selection-info">
        已选择 <strong>{{ selectedTemplates.length }}</strong> 个模板
      </div>
      <div class="action-buttons">
        <el-button 
          @click="showBatchStatusDialog = true"
          :icon="Setting"
        >
          批量设置状态
        </el-button>
        <el-button 
          type="danger" 
          @click="handleBatchDelete"
          :icon="Delete"
        >
          批量删除
        </el-button>
        <el-button @click="clearSelection">取消选择</el-button>
      </div>
    </div>

    <!-- 模板列表 -->
    <div class="templates-content">
      <el-table
        v-loading="loading"
        :data="templates"
        @selection-change="handleSelectionChange"
        row-key="id"
        style="width: 100%"
      >
        <el-table-column type="selection" width="55" />
        
        <el-table-column prop="name" label="角色名称" min-width="120">
          <template #default="{ row }">
            <div class="character-name">
              <strong>{{ row.name }}</strong>
              <div class="character-badges">
                <el-tag v-if="row.template_detail?.is_popular" type="danger" size="small">热门</el-tag>
                <el-tag v-if="row.template_detail?.is_new" type="warning" size="small">新增</el-tag>
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="gender" label="性别" width="80">
          <template #default="{ row }">
            {{ getGenderLabel(row.gender) }}
          </template>
        </el-table-column>

        <el-table-column prop="character_type" label="类型" width="100">
          <template #default="{ row }">
            {{ getCharacterTypeLabel(row.character_type) }}
          </template>
        </el-table-column>

        <el-table-column prop="description" label="描述" min-width="200">
          <template #default="{ row }">
            <div class="description-cell">
              {{ row.description || '无描述' }}
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="tags" label="标签" width="150">
          <template #default="{ row }">
            <div class="tags-cell">
              <el-tag 
                v-for="tag in row.tags?.slice(0, 2)" 
                :key="tag" 
                size="small"
                style="margin-right: 4px;"
              >
                {{ tag }}
              </el-tag>
              <span v-if="row.tags?.length > 2" class="more-tags">
                +{{ row.tags.length - 2 }}
              </span>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="统计" width="120">
          <template #default="{ row }">
            <div class="stats-cell">
              <div>使用: {{ row.template_detail?.usage_count || 0 }}</div>
              <div>评分: {{ (row.template_detail?.rating || 0).toFixed(1) }}</div>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="created_at" label="创建时间" width="120">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>

        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button size="small" @click="editTemplate(row)">编辑</el-button>
              <el-button 
                size="small" 
                type="warning" 
                @click="setTemplateStatus(row)"
              >
                状态
              </el-button>
              <el-button 
                size="small" 
                type="danger" 
                @click="deleteTemplate(row)"
              >
                删除
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="searchParams.page"
          v-model:page-size="searchParams.page_size"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadTemplates"
          @current-change="loadTemplates"
        />
      </div>
    </div>

    <!-- 创建/编辑模板对话框 -->
    <TemplateEditDialog
      v-model="showCreateDialog"
      :template="editingTemplate"
      @success="handleEditSuccess"
    />

    <!-- 批量状态设置对话框 -->
    <BatchStatusDialog
      v-model="showBatchStatusDialog"
      :template-ids="selectedTemplates.map(t => t.id)"
      @success="handleBatchStatusSuccess"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox, ElNotification } from 'element-plus'
import { Plus, Search, Setting, Delete } from '@element-plus/icons-vue'
import AdminCharacterTemplateService, { 
  type CharacterTemplateResponse,
  type AdminTemplateSearchParams 
} from '@/api/admin-character-templates'
import TemplateEditDialog from '@/components/admin/TemplateEditDialog.vue'
import BatchStatusDialog from '@/components/admin/BatchStatusDialog.vue'

// === 响应式数据 ===
const loading = ref(false)
const templates = ref<CharacterTemplateResponse[]>([])
const selectedTemplates = ref<CharacterTemplateResponse[]>([])
const total = ref(0)
const totalPages = ref(0)

const showCreateDialog = ref(false)
const showBatchStatusDialog = ref(false)
const editingTemplate = ref<CharacterTemplateResponse | null>(null)

// 搜索参数
const searchParams = reactive<AdminTemplateSearchParams>({
  page: 1,
  page_size: 20,
  search: '',
  gender: undefined,
  character_type: undefined,
  is_popular: undefined,
  is_new: undefined,
  sort_by: 'created_at',
  sort_order: 'desc'
})

const statusFilter = ref<string>('')

// === 计算属性 ===
const hasSelectedTemplates = computed(() => selectedTemplates.value.length > 0)

// === 生命周期 ===
onMounted(() => {
  loadTemplates()
})

// === 方法 ===

/**
 * 加载模板列表
 */
const loadTemplates = async () => {
  try {
    loading.value = true
    const response = await AdminCharacterTemplateService.getList(searchParams)
    templates.value = response.templates
    total.value = response.total
    totalPages.value = response.total_pages
  } catch (error) {
    console.error('加载模板列表失败:', error)
    ElMessage.error('加载模板列表失败')
  } finally {
    loading.value = false
  }
}

/**
 * 搜索处理（防抖）
 */
let searchTimeout: ReturnType<typeof setTimeout> | null = null
const handleSearch = () => {
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    searchParams.page = 1
    loadTemplates()
  }, 500)
}

/**
 * 状态筛选处理
 */
const handleStatusFilter = () => {
  if (statusFilter.value === 'popular') {
    searchParams.is_popular = true
    searchParams.is_new = undefined
  } else if (statusFilter.value === 'new') {
    searchParams.is_popular = undefined
    searchParams.is_new = true
  } else {
    searchParams.is_popular = undefined
    searchParams.is_new = undefined
  }
  searchParams.page = 1
  loadTemplates()
}

/**
 * 重置筛选
 */
const resetFilters = () => {
  Object.assign(searchParams, {
    page: 1,
    page_size: 20,
    search: '',
    gender: undefined,
    character_type: undefined,
    is_popular: undefined,
    is_new: undefined,
    sort_by: 'created_at',
    sort_order: 'desc'
  })
  statusFilter.value = ''
  loadTemplates()
}

/**
 * 选择变化处理
 */
const handleSelectionChange = (selection: CharacterTemplateResponse[]) => {
  selectedTemplates.value = selection
}

/**
 * 清除选择
 */
const clearSelection = () => {
  selectedTemplates.value = []
}

/**
 * 编辑模板
 */
const editTemplate = (template: CharacterTemplateResponse) => {
  editingTemplate.value = template
  showCreateDialog.value = true
}

/**
 * 编辑成功处理
 */
const handleEditSuccess = () => {
  showCreateDialog.value = false
  editingTemplate.value = null
  loadTemplates()
}

/**
 * 设置模板状态
 */
const setTemplateStatus = (template: CharacterTemplateResponse) => {
  // TODO: 实现单个模板状态设置对话框
  ElMessage.info('功能开发中...')
}

/**
 * 删除模板
 */
const deleteTemplate = async (template: CharacterTemplateResponse) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除角色模板 "${template.name}" 吗？此操作不可逆。`,
      '确认删除',
      {
        type: 'warning',
        confirmButtonText: '确定删除',
        cancelButtonText: '取消'
      }
    )

    await AdminCharacterTemplateService.delete(template.id)
    ElMessage.success('模板删除成功')
    loadTemplates()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除模板失败:', error)
      ElMessage.error('删除模板失败')
    }
  }
}

/**
 * 批量删除
 */
const handleBatchDelete = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedTemplates.value.length} 个角色模板吗？此操作不可逆。`,
      '确认批量删除',
      {
        type: 'warning',
        confirmButtonText: '确定删除',
        cancelButtonText: '取消'
      }
    )

    // 依次删除选中的模板
    let successCount = 0
    let failedCount = 0

    for (const template of selectedTemplates.value) {
      try {
        await AdminCharacterTemplateService.delete(template.id)
        successCount++
      } catch (error) {
        console.error(`删除模板 ${template.name} 失败:`, error)
        failedCount++
      }
    }

    if (successCount > 0) {
      ElNotification.success({
        title: '批量删除完成',
        message: `成功删除 ${successCount} 个模板${failedCount > 0 ? `，失败 ${failedCount} 个` : ''}`
      })
    }

    clearSelection()
    loadTemplates()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('批量删除失败:', error)
      ElMessage.error('批量删除失败')
    }
  }
}

/**
 * 批量状态设置成功处理
 */
const handleBatchStatusSuccess = () => {
  showBatchStatusDialog.value = false
  clearSelection()
  loadTemplates()
}

/**
 * 格式化日期
 */
const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN')
}

/**
 * 获取性别标签
 */
const getGenderLabel = (gender: string) => {
  const labels: Record<string, string> = {
    male: '男',
    female: '女',
    unknown: '未知',
    other: '其他'
  }
  return labels[gender] || gender
}

/**
 * 获取角色类型标签
 */
const getCharacterTypeLabel = (type: string) => {
  const labels: Record<string, string> = {
    protagonist: '主角',
    supporting: '配角',
    antagonist: '反派',
    minor: '次要',
    passerby: '路人'
  }
  return labels[type] || type
}
</script>

<style scoped>
.admin-character-templates {
  padding: 24px;
}

.page-header {
  margin-bottom: 24px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-title h1 {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.subtitle {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.filter-toolbar {
  background: #f8f9fa;
  padding: 16px 20px;
  border-radius: 8px;
  margin-bottom: 24px;
}

.filter-group {
  display: flex;
  gap: 16px;
  align-items: center;
  flex-wrap: wrap;
}

.filter-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-label {
  font-weight: 500;
  color: #606266;
  white-space: nowrap;
}

.filter-actions {
  margin-left: auto;
}

.batch-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #e6f7ff;
  border: 1px solid #91d5ff;
  border-radius: 6px;
  margin-bottom: 16px;
}

.selection-info {
  color: #1890ff;
  font-weight: 500;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.character-name strong {
  display: block;
  margin-bottom: 4px;
}

.character-badges {
  display: flex;
  gap: 4px;
}

.description-cell {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.tags-cell {
  display: flex;
  align-items: center;
  gap: 4px;
}

.more-tags {
  color: #909399;
  font-size: 12px;
}

.stats-cell {
  font-size: 12px;
  color: #606266;
}

.stats-cell div {
  margin-bottom: 2px;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 24px;
}
</style>