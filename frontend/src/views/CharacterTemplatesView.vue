<template>
  <div class="character-templates">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="page-title">
          角色模板库
          <div class="subtitle">探索丰富的角色模板，为你的小说注入生命力</div>
        </div>
        <div class="header-actions">
          <div class="search-box">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索角色名称、标签或能力..."
              @keyup.enter="handleSearch"
              clearable
              @clear="resetSearch"
            >
              <template #prefix>
                <el-icon class="search-icon"><Search /></el-icon>
              </template>
            </el-input>
          </div>
          <!-- 管理员入口 -->
          <el-button
            v-if="userStore.isAdmin"
            type="primary"
            @click="goToAdminPage"
            :icon="Setting"
          >
            管理模板
          </el-button>
        </div>
      </div>
    </div>

    <!-- 筛选工具栏 -->
    <div class="filter-toolbar" v-loading="isLoadingFilters">
      <div class="filter-group">
        <!-- 性别筛选 -->
        <div class="filter-item">
          <span class="filter-label">性别:</span>
          <el-select
            v-model="filters.gender"
            class="filter-control"
            placeholder="全部"
            clearable
            @change="handleFilterChange"
          >
            <el-option label="全部" value="" />
            <el-option
              v-for="option in filterOptions.genders"
              :key="option.value"
              :label="formatGenderLabel(option.label) + ` (${option.count})`"
              :value="option.value"
            />
          </el-select>
        </div>

        <!-- 力量体系筛选 -->
        <div class="filter-item">
          <span class="filter-label">力量体系:</span>
          <el-select
            v-model="filters.power_systems"
            class="filter-control"
            placeholder="全部"
            multiple
            collapse-tags
            collapse-tags-tooltip
            clearable
            @change="handleFilterChange"
          >
            <el-option
              v-for="option in filterOptions.power_systems"
              :key="option.value"
              :label="`${option.label} (${option.count})`"
              :value="option.value"
            />
          </el-select>
        </div>

        <!-- 世界观筛选 -->
        <div class="filter-item">
          <span class="filter-label">世界观:</span>
          <el-select
            v-model="filters.worldviews"
            class="filter-control"
            placeholder="全部"
            multiple
            collapse-tags
            collapse-tags-tooltip
            clearable
            @change="handleFilterChange"
          >
            <el-option
              v-for="option in filterOptions.worldviews"
              :key="option.value"
              :label="`${option.label} (${option.count})`"
              :value="option.value"
            />
          </el-select>
        </div>

        <!-- 标签筛选 -->
        <div class="filter-item">
          <span class="filter-label">标签:</span>
          <el-select
            v-model="filters.tags"
            class="filter-control"
            placeholder="全部"
            multiple
            collapse-tags
            collapse-tags-tooltip
            clearable
            @change="handleFilterChange"
          >
            <el-option
              v-for="option in filterOptions.tags"
              :key="option.value"
              :label="`${option.label} (${option.count})`"
              :value="option.value"
            />
          </el-select>
        </div>

        <!-- 筛选操作 -->
        <div class="filter-actions">
          <el-checkbox v-model="filters.is_popular" @change="handleFilterChange">热门</el-checkbox>
          <el-checkbox v-model="filters.is_new" @change="handleFilterChange">新增</el-checkbox>
          <el-button 
            text 
            class="reset-btn" 
            :disabled="!hasActiveFilters"
            @click="resetFilters"
          >
            重置筛选
          </el-button>
        </div>
      </div>

      <!-- 当前激活的筛选标签 -->
      <div class="active-filters" v-if="activeFilterTags.length > 0">
        <el-tag
          v-for="(tag, index) in activeFilterTags"
          :key="index"
          class="filter-tag"
          closable
          @close="removeFilterTag(tag)"
        >
          {{ tag.label }}: {{ tag.value }}
        </el-tag>
      </div>
    </div>

    <!-- 排序和视图切换工具栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <el-select
          v-model="filters.sort_by"
          placeholder="排序方式"
          size="default"
          @change="handleFilterChange"
        >
          <el-option label="创建时间" value="created_at" />
          <el-option label="使用次数" value="usage_count" />
          <el-option label="评分" value="rating" />
          <el-option label="名称" value="name" />
        </el-select>
        <el-radio-group v-model="filters.sort_order" size="small" @change="handleFilterChange">
          <el-radio-button label="asc">升序</el-radio-button>
          <el-radio-button label="desc">降序</el-radio-button>
        </el-radio-group>
      </div>
      <div class="toolbar-right">
        <el-radio-group v-model="viewMode" size="small">
          <el-radio-button label="grid"><el-icon><Grid /></el-icon></el-radio-button>
          <el-radio-button label="list"><el-icon><List /></el-icon></el-radio-button>
        </el-radio-group>
      </div>
    </div>

    <!-- 角色网格 -->
    <div class="character-grid" v-loading="isLoading">
      <template v-if="templates.length > 0">
        <character-card
          v-for="template in templates"
          :key="template.id"
          :character="template"
          @view-details="openDetailModal"
          @use-template="showUseTemplateModal"
          @toggle-favorite="toggleFavorite"
        />
      </template>
      <div v-else-if="!isLoading" class="empty-state">
        <div class="empty-icon">
          <el-icon :size="64"><Failed /></el-icon>
        </div>
        <h3 class="empty-title">未找到符合条件的角色模板</h3>
        <p class="empty-description">
          {{ hasActiveFilters ? '尝试调整筛选条件或清除筛选器' : '暂无角色模板，请稍后再试' }}
        </p>
        <div class="empty-actions" v-if="hasActiveFilters">
          <el-button type="primary" @click="resetFilters">清除所有筛选</el-button>
        </div>
      </div>
    </div>

    <!-- 分页 -->
    <div class="pagination-container" v-if="total > 0">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[12, 24, 36, 48]"
        layout="total, sizes, prev, pager, next, jumper"
        :total="total"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>

    <!-- 角色详情弹窗 -->
    <character-detail-modal
      v-if="selectedTemplate"
      v-model:visible="showDetailModal"
      :character="selectedTemplate"
      @use-template="showUseTemplateModal"
      @toggle-favorite="toggleFavorite"
    />

    <!-- 使用角色模板弹窗 -->
    <el-dialog
      v-model="showUseModal"
      title="使用角色模板"
      width="600px"
      destroy-on-close
    >
      <template v-if="selectedTemplate">
        <div class="use-template-form">
          <p>你即将将角色 <strong>{{ selectedTemplate.name }}</strong> 添加到你的小说中：</p>
          
          <el-form :model="useTemplateForm" label-width="120px">
            <el-form-item label="选择小说：" required>
              <el-select v-model="useTemplateForm.novel_id" placeholder="请选择小说" @change="validateNovel">
                <el-option
                  v-for="novel in userNovels"
                  :key="novel.id"
                  :label="novel.title"
                  :value="novel.id"
                />
              </el-select>
              <div class="form-hint">选择你要添加该角色的小说</div>
            </el-form-item>
            
            <el-form-item label="适配说明：">
              <el-input
                v-model="useTemplateForm.adaptation_notes"
                type="textarea"
                :rows="3"
                placeholder="可选填写如何将此角色适配到你的小说中..."
              />
              <div class="form-hint">可以留空，系统会根据小说背景自动适配</div>
            </el-form-item>
            
            <div class="dialog-footer">
              <el-button @click="showUseModal = false">取消</el-button>
              <el-button 
                type="primary" 
                @click="confirmUseTemplate"
                :loading="isSubmitting"
                :disabled="!useTemplateForm.novel_id"
              >
                确认使用
              </el-button>
            </div>
          </el-form>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Grid,
  List,
  Search,
  Failed,
  Star,
  StarFilled,
  Setting
} from '@element-plus/icons-vue'

import CharacterCard from '@/components/character-templates/CharacterCard.vue'
import CharacterDetailModal from '@/components/character-templates/CharacterDetailModal.vue'

import { 
  CharacterTemplateService, 
  type CharacterTemplateSummary,
  type CharacterTemplateDetail,
  type CharacterTemplateFilter,
  type TemplateFilterOption,
  type UseTemplateRequest
} from '@/api/character-templates.ts'

// 从小说API导入获取小说列表的方法
import { NovelService } from '@/api/novels'

// 用户状态
import { useUserStore } from '@/stores/user'

// 路由
const router = useRouter()

// 用户状态管理
const userStore = useUserStore()

// 角色模板列表
const templates = ref<CharacterTemplateSummary[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(12)
const totalPages = ref(1)

// 视图模式
const viewMode = ref('grid')

// 加载状态
const isLoading = ref(false)
const isLoadingFilters = ref(false)
const isSubmitting = ref(false)

// 搜索
const searchKeyword = ref('')
const isSearchMode = ref(false)

// 筛选选项
const filterOptions = reactive({
  genders: [] as TemplateFilterOption[],
  power_systems: [] as TemplateFilterOption[],
  worldviews: [] as TemplateFilterOption[],
  tags: [] as TemplateFilterOption[]
})

// 筛选条件
const filters = reactive<CharacterTemplateFilter>({
  gender: undefined,
  power_systems: [] as string[],
  worldviews: [] as string[],
  tags: [] as string[],
  is_popular: false,
  is_new: false,
  sort_by: 'created_at',
  sort_order: 'desc',
  page: 1,
  page_size: 12
})

// 选中的模板
const selectedTemplate = ref<CharacterTemplateDetail | null>(null)
const showDetailModal = ref(false)
const showUseModal = ref(false)

// 使用模板表单
const useTemplateForm = reactive<UseTemplateRequest>({
  novel_id: 0,
  adaptation_notes: ''
})

// 用户的小说列表
const userNovels = ref<any[]>([])

// 计算属性：是否有激活的筛选条件
const hasActiveFilters = computed(() => {
  return (
    !!filters.gender ||
    (filters.power_systems?.length || 0) > 0 ||
    (filters.worldviews?.length || 0) > 0 ||
    (filters.tags?.length || 0) > 0 ||
    filters.is_popular ||
    filters.is_new
  )
})

// 计算属性：当前激活的筛选标签
const activeFilterTags = computed(() => {
  const tags = []

  if (filters.gender) {
    tags.push({
      type: 'gender',
      label: '性别',
      value: formatGenderLabel(filters.gender)
    })
  }

  if (filters.power_systems && filters.power_systems.length > 0) {
    filters.power_systems.forEach(system => {
      tags.push({
        type: 'power_system',
        label: '力量体系',
        value: system,
        originalValue: system
      })
    })
  }

  if (filters.worldviews && filters.worldviews.length > 0) {
    filters.worldviews.forEach(worldview => {
      tags.push({
        type: 'worldview',
        label: '世界观',
        value: worldview,
        originalValue: worldview
      })
    })
  }

  if (filters.tags && filters.tags.length > 0) {
    filters.tags.forEach(tag => {
      tags.push({
        type: 'tag',
        label: '标签',
        value: tag,
        originalValue: tag
      })
    })
  }

  if (filters.is_popular) {
    tags.push({
      type: 'is_popular',
      label: '筛选',
      value: '热门'
    })
  }

  if (filters.is_new) {
    tags.push({
      type: 'is_new',
      label: '筛选',
      value: '新增'
    })
  }

  return tags
})

// 格式化性别标签
const formatGenderLabel = (gender: string): string => {
  const genderMap: Record<string, string> = {
    'male': '男',
    'female': '女',
    'unknown': '未知',
    'other': '其他'
  }
  return genderMap[gender] || gender
}

// 加载角色模板列表
const loadTemplates = async () => {
  isLoading.value = true
  
  try {
    // 设置分页参数
    filters.page = currentPage.value
    filters.page_size = pageSize.value
    
    let result
    
    if (isSearchMode.value && searchKeyword.value) {
      // 搜索模式
      result = await CharacterTemplateService.searchTemplates({
        keyword: searchKeyword.value,
        filters: filters
      })
    } else {
      // 普通列表模式
      result = await CharacterTemplateService.getTemplates(filters)
      
      // 加载筛选选项
      if (result.filters_available) {
        filterOptions.genders = result.filters_available.genders || []
        filterOptions.power_systems = result.filters_available.power_systems || []
        filterOptions.worldviews = result.filters_available.worldviews || []
        filterOptions.tags = result.filters_available.tags || []
      }
    }
    
    templates.value = result.characters
    total.value = result.total
    totalPages.value = result.total_pages
    
  } catch (error) {
    console.error('加载角色模板失败:', error)
    ElMessage.error('加载角色模板失败，请稍后重试')
    templates.value = []
    total.value = 0
  } finally {
    isLoading.value = false
  }
}

// 加载筛选选项
const loadFilterOptions = async () => {
  if (Object.values(filterOptions).some(arr => arr.length === 0)) {
    isLoadingFilters.value = true
    try {
      const result = await CharacterTemplateService.getTemplates({
        page: 1,
        page_size: 1
      })
      
      if (result.filters_available) {
        filterOptions.genders = result.filters_available.genders || []
        filterOptions.power_systems = result.filters_available.power_systems || []
        filterOptions.worldviews = result.filters_available.worldviews || []
        filterOptions.tags = result.filters_available.tags || []
      }
    } catch (error) {
      console.error('加载筛选选项失败:', error)
    } finally {
      isLoadingFilters.value = false
    }
  }
}

// 处理筛选变化
const handleFilterChange = () => {
  currentPage.value = 1
  loadTemplates()
}

// 移除筛选标签
const removeFilterTag = (tag: any) => {
  if (tag.type === 'gender') {
    filters.gender = undefined
  } else if (tag.type === 'power_system' && filters.power_systems) {
    filters.power_systems = filters.power_systems.filter(item => item !== tag.originalValue)
  } else if (tag.type === 'worldview' && filters.worldviews) {
    filters.worldviews = filters.worldviews.filter(item => item !== tag.originalValue)
  } else if (tag.type === 'tag' && filters.tags) {
    filters.tags = filters.tags.filter(item => item !== tag.originalValue)
  } else if (tag.type === 'is_popular') {
    filters.is_popular = false
  } else if (tag.type === 'is_new') {
    filters.is_new = false
  }
  
  loadTemplates()
}

// 重置筛选条件
const resetFilters = () => {
  filters.gender = undefined
  filters.power_systems = [] as string[]
  filters.worldviews = [] as string[]
  filters.tags = [] as string[]
  filters.is_popular = false
  filters.is_new = false
  
  loadTemplates()
}

// 处理搜索
const handleSearch = () => {
  if (searchKeyword.value.trim()) {
    isSearchMode.value = true
    currentPage.value = 1
    loadTemplates()
  }
}

// 重置搜索
const resetSearch = () => {
  if (isSearchMode.value) {
    isSearchMode.value = false
    searchKeyword.value = ''
    loadTemplates()
  }
}

// 处理分页大小变化
const handleSizeChange = (size: number) => {
  pageSize.value = size
  loadTemplates()
}

// 处理页码变化
const handleCurrentChange = (page: number) => {
  currentPage.value = page
  loadTemplates()
}

// 打开详情弹窗
const openDetailModal = async (templateId: number) => {
  isLoading.value = true
  try {
    const data = await CharacterTemplateService.getTemplateDetail(templateId)
    selectedTemplate.value = data
    showDetailModal.value = true
  } catch (error) {
    console.error('获取角色详情失败:', error)
    ElMessage.error('获取角色详情失败')
  } finally {
    isLoading.value = false
  }
}

// 打开使用模板弹窗
const showUseTemplateModal = (template: CharacterTemplateDetail | CharacterTemplateSummary) => {
  // 如果只有摘要信息，先获取完整信息
  if (!('template_detail' in template)) {
    openDetailModal(template.id)
      .then(() => {
        resetUseTemplateForm()
        showUseModal.value = true
      })
  } else {
    selectedTemplate.value = template as CharacterTemplateDetail
    resetUseTemplateForm()
    showUseModal.value = true
  }
}

// 重置使用模板表单
const resetUseTemplateForm = () => {
  useTemplateForm.novel_id = 0
  useTemplateForm.adaptation_notes = ''
  loadUserNovels()
}

// 加载用户小说列表
const loadUserNovels = async () => {
  try {
    const response = await NovelService.getNovels()
    userNovels.value = response.novels || []
    
    // 如果有小说，默认选择第一个
    if (userNovels.value.length > 0) {
      useTemplateForm.novel_id = userNovels.value[0].id
    }
  } catch (error) {
    console.error('获取小说列表失败:', error)
    ElMessage.error('获取小说列表失败')
  }
}

// 验证小说选择
const validateNovel = (novelId: number) => {
  useTemplateForm.novel_id = novelId
}

// 确认使用模板
const confirmUseTemplate = async () => {
  if (!selectedTemplate.value) return
  if (!useTemplateForm.novel_id) {
    ElMessage.warning('请选择小说')
    return
  }
  
  isSubmitting.value = true
  
  try {
    const result = await CharacterTemplateService.useTemplate(
      selectedTemplate.value.id,
      useTemplateForm
    )
    
    if (result.success) {
      ElMessage.success(result.message || '成功添加角色到小说中')
      showUseModal.value = false
      
      // 询问是否查看新建的角色
      await ElMessageBox.confirm(
        '角色已成功添加到你的小说中，是否立即前往查看？',
        '操作成功',
        {
          confirmButtonText: '前往查看',
          cancelButtonText: '留在当前页面',
          type: 'success'
        }
      )
      
      // 跳转到角色页面
      router.push(`/workspace/${useTemplateForm.novel_id}/characters`)
    } else {
      ElMessage.error('添加角色失败')
    }
  } catch (error: any) {
    if (error.response?.data?.detail === '已经从该模板创建过角色') {
      ElMessage.warning('你已经在该小说中使用过此角色模板')
    } else {
      console.error('使用角色模板失败:', error)
      ElMessage.error('使用模板失败，请稍后重试')
    }
  } finally {
    isSubmitting.value = false
  }
}

// 收藏/取消收藏
const toggleFavorite = async (templateId: number) => {
  try {
    const response = await CharacterTemplateService.toggleFavorite(templateId)
    
    // 更新列表中的收藏状态
    const index = templates.value.findIndex(t => t.id === templateId)
    if (index !== -1) {
      templates.value[index].is_favorited = response.is_favorited
    }
    
    // 如果详情模态框打开，同时更新详情中的收藏状态
    if (selectedTemplate.value?.id === templateId) {
      selectedTemplate.value.is_favorited = response.is_favorited
    }
    
    ElMessage.success(response.message)
  } catch (error) {
    console.error('收藏操作失败:', error)
    ElMessage.error('收藏操作失败')
  }
}

// 跳转到管理员页面
const goToAdminPage = () => {
  router.push({ name: 'admin-character-templates' })
}

// 生命周期钩子
onMounted(() => {
  loadFilterOptions()
  loadTemplates()
})
</script>

<style scoped>
.character-templates {
  min-height: calc(100vh - 120px);
  padding: 20px;
  
  .page-header {
    padding: 24px 0;
    border-bottom: 1px solid #EBEEF5;
    margin-bottom: 24px;
    
    .header-content {
      display: flex;
      justify-content: space-between;
      align-items: center;
      
      .page-title {
        font-size: 24px;
        font-weight: 600;
        color: #303133;
        
        .subtitle {
          font-size: 14px;
          color: #909399;
          font-weight: normal;
          margin-top: 4px;
        }
      }
      
      .header-actions {
        display: flex;
        align-items: center;
        gap: 16px;
        
        .search-box {
          width: 320px;
          
          :deep(.el-input__inner) {
            border-radius: 20px;
            padding-left: 40px;
          }
          
          .search-icon {
            color: #C0C4CC;
          }
        }
      }
    }
  }
  
  .filter-toolbar {
    background: #F8F9FA;
    padding: 16px 20px;
    border-radius: 8px;
    margin-bottom: 24px;
    
    .filter-group {
      display: flex;
      gap: 24px;
      align-items: center;
      flex-wrap: wrap;
      
      .filter-item {
        display: flex;
        align-items: center;
        gap: 8px;
        
        .filter-label {
          font-weight: 500;
          color: #606266;
          white-space: nowrap;
        }
        
        .filter-control {
          min-width: 120px;
        }
      }
      
      .filter-actions {
        margin-left: auto;
        display: flex;
        align-items: center;
        gap: 16px;
        
        .reset-btn {
          color: #909399;
          
          &:hover {
            color: #409EFF;
          }
        }
      }
    }
    
    .active-filters {
      margin-top: 12px;
      
      .filter-tag {
        margin-right: 8px;
        margin-bottom: 4px;
      }
    }
  }
  
  .toolbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    
    .toolbar-left {
      display: flex;
      align-items: center;
      gap: 12px;
    }
  }
  
  .character-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: 20px;
    margin-bottom: 32px;
    min-height: 400px;
  }
  
  .pagination-container {
    display: flex;
    justify-content: center;
    margin: 30px 0;
  }
  
  .empty-state {
    text-align: center;
    padding: 80px 20px;
    grid-column: 1 / -1;
    
    .empty-icon {
      font-size: 64px;
      color: #C0C4CC;
      margin-bottom: 16px;
    }
    
    .empty-title {
      font-size: 18px;
      color: #606266;
      margin-bottom: 8px;
    }
    
    .empty-description {
      color: #909399;
      margin-bottom: 24px;
    }
    
    .empty-actions {
      .action-btn {
        margin: 0 8px;
      }
    }
  }
  
  .use-template-form {
    .form-hint {
      font-size: 12px;
      color: #909399;
      margin-top: 4px;
    }
    
    .dialog-footer {
      margin-top: 24px;
      display: flex;
      justify-content: flex-end;
      gap: 12px;
    }
  }
}

/* 响应式样式 */
@media (max-width: 1199px) {
  .character-templates .character-grid {
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 16px;
  }
}

@media (max-width: 767px) {
  .character-templates {
    .page-header .header-content {
      flex-direction: column;
      gap: 16px;
      
      .search-box {
        width: 100%;
      }
    }
    
    .filter-toolbar .filter-group {
      flex-direction: column;
      align-items: stretch;
      gap: 12px;
      
      .filter-item {
        justify-content: space-between;
      }
      
      .filter-actions {
        margin-left: 0;
        margin-top: 8px;
      }
    }
    
    .character-grid {
      grid-template-columns: repeat(2, 1fr);
      gap: 12px;
    }
  }
}
</style>