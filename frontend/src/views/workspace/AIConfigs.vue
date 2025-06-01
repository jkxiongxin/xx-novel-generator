<template>
  <div class="ai-configs-container">
    <!-- 页面标题和操作栏 -->
    <div class="header-section">
      <div class="title-section">
        <h2>AI模型配置</h2>
        <p class="subtitle">管理您的AI模型配置，支持多种模型和自定义参数</p>
      </div>
      <div class="action-section">
        <el-button type="primary" icon="Plus" @click="showCreateDialog = true">
          新建配置
        </el-button>
        <el-button icon="Download" @click="showTemplateDialog = true">
          从模板创建
        </el-button>
        <el-button 
          icon="Delete" 
          :disabled="selectedConfigs.length === 0"
          @click="handleBatchDelete"
        >
          批量删除
        </el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-section">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-number">{{ stats.total_configs }}</div>
              <div class="stats-label">总配置数</div>
            </div>
            <el-icon class="stats-icon"><Setting /></el-icon>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card active">
            <div class="stats-content">
              <div class="stats-number">{{ stats.active_configs }}</div>
              <div class="stats-label">已启用</div>
            </div>
            <el-icon class="stats-icon"><Check /></el-icon>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card inactive">
            <div class="stats-content">
              <div class="stats-number">{{ stats.inactive_configs }}</div>
              <div class="stats-label">已禁用</div>
            </div>
            <el-icon class="stats-icon"><Close /></el-icon>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card default">
            <div class="stats-content">
              <div class="stats-number">{{ stats.default_config_id ? '1' : '0' }}</div>
              <div class="stats-label">默认配置</div>
            </div>
            <el-icon class="stats-icon"><Star /></el-icon>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 筛选和搜索 -->
    <div class="filter-section">
      <el-row :gutter="20" align="middle">
        <el-col :span="8">
          <el-input
            v-model="filters.search"
            placeholder="搜索配置名称、描述或模型名称"
            prefix-icon="Search"
            clearable
            @input="handleSearch"
          />
        </el-col>
        <el-col :span="4">
          <el-select v-model="filters.model_type" placeholder="模型类型" clearable @change="loadConfigs">
            <el-option 
              v-for="(label, value) in MODEL_TYPE_LABELS" 
              :key="value"
              :label="label" 
              :value="value"
            />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select v-model="filters.is_active" placeholder="状态" clearable @change="loadConfigs">
            <el-option label="已启用" :value="true" />
            <el-option label="已禁用" :value="false" />
          </el-select>
        </el-col>
        <el-col :span="8">
          <div class="view-toggle">
            <el-radio-group v-model="viewMode" size="small">
              <el-radio-button label="list">列表视图</el-radio-button>
              <el-radio-button label="card">卡片视图</el-radio-button>
            </el-radio-group>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 配置列表 -->
    <div class="configs-section">
      <!-- 列表视图 -->
      <el-table 
        v-if="viewMode === 'list'"
        v-loading="loading"
        :data="configs"
        @selection-change="handleSelectionChange"
        row-key="id"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="name" label="配置名称" min-width="150">
          <template #default="{ row }">
            <div class="config-name">
              <span>{{ row.name }}</span>
              <el-tag v-if="row.is_default" type="warning" size="small">默认</el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="model_type" label="模型类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getModelTypeTagType(row.model_type)">
              {{ MODEL_TYPE_LABELS[row.model_type as keyof typeof MODEL_TYPE_LABELS] }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="model_name" label="模型名称" width="150" />
        <el-table-column prop="is_active" label="状态" width="80">
          <template #default="{ row }">
            <el-switch
              v-model="row.is_active"
              @change="handleToggleStatus(row)"
              :loading="row.updating"
            />
          </template>
        </el-table-column>
        <el-table-column prop="priority" label="优先级" width="80" />
        <el-table-column prop="created_at" label="创建时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" icon="View" @click="handleView(row)">
              查看
            </el-button>
            <el-button size="small" icon="Edit" @click="handleEdit(row)">
              编辑
            </el-button>
            <el-button size="small" icon="Promotion" @click="handleTest(row)">
              测试
            </el-button>
            <el-button 
              size="small" 
              type="danger" 
              icon="Delete" 
              @click="handleDelete(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 卡片视图 -->
      <div v-else class="cards-grid">
        <div 
          v-for="config in configs" 
          :key="config.id" 
          class="config-card"
          :class="{ active: config.is_active, default: config.is_default }"
        >
          <div class="card-header">
            <div class="card-title">
              <h4>{{ config.name }}</h4>
              <div class="card-badges">
                <el-tag v-if="config.is_default" type="warning" size="small">默认</el-tag>
                <el-tag :type="config.is_active ? 'success' : 'info'" size="small">
                  {{ config.is_active ? '已启用' : '已禁用' }}
                </el-tag>
              </div>
            </div>
            <el-dropdown trigger="click">
              <el-button text icon="MoreFilled" />
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item icon="View" @click="handleView(config)">
                    查看详情
                  </el-dropdown-item>
                  <el-dropdown-item icon="Edit" @click="handleEdit(config)">
                    编辑配置
                  </el-dropdown-item>
                  <el-dropdown-item icon="Promotion" @click="handleTest(config)">
                    测试连接
                  </el-dropdown-item>
                  <el-dropdown-item 
                    v-if="!config.is_default" 
                    icon="Star" 
                    @click="handleSetDefault(config)"
                  >
                    设为默认
                  </el-dropdown-item>
                  <el-dropdown-item 
                    icon="Delete" 
                    @click="handleDelete(config)"
                    divided
                  >
                    删除配置
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
          
          <div class="card-content">
            <p class="card-description">{{ config.description || '无描述' }}</p>
            <div class="card-info">
              <div class="info-item">
                <span class="label">模型类型:</span>
                <el-tag :type="getModelTypeTagType(config.model_type)" size="small">
                  {{ MODEL_TYPE_LABELS[config.model_type as keyof typeof MODEL_TYPE_LABELS] }}
                </el-tag>
              </div>
              <div class="info-item">
                <span class="label">模型名称:</span>
                <span class="value">{{ config.model_name }}</span>
              </div>
              <div class="info-item">
                <span class="label">优先级:</span>
                <span class="value">{{ config.priority }}</span>
              </div>
            </div>
          </div>
          
          <div class="card-footer">
            <div class="card-status">
              <el-switch
                v-model="config.is_active"
                @change="handleToggleStatus(config)"
                :loading="config.updating"
              />
            </div>
            <div class="card-actions">
              <el-button size="small" @click="handleTest(config)">测试</el-button>
              <el-button size="small" @click="handleEdit(config)">编辑</el-button>
            </div>
          </div>
        </div>
      </div>

      <!-- 分页 -->
      <div class="pagination-section">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadConfigs"
          @current-change="loadConfigs"
        />
      </div>
    </div>

    <!-- 创建/编辑配置对话框 -->
    <AIConfigDialog
      v-model:visible="showCreateDialog"
      :config="editingConfig"
      :mode="dialogMode"
      @success="handleDialogSuccess"
    />

    <!-- 模板选择对话框 -->
    <AIConfigTemplateDialog
      v-model:visible="showTemplateDialog"
      @success="handleTemplateSuccess"
    />

    <!-- 配置详情对话框 -->
    <AIConfigDetailDialog
      v-model:visible="showDetailDialog"
      :config="viewingConfig"
    />

    <!-- 测试配置对话框 -->
    <AIConfigTestDialog
      v-model:visible="showTestDialog"
      :config="testingConfig"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Setting, Check, Close, Star, Plus, Download, Delete,
  Search, View, Edit, Promotion, MoreFilled
} from '@element-plus/icons-vue'

import { aiConfigsApi, MODEL_TYPE_LABELS, type AIModelConfig, type AIModelConfigStats } from '@/api/ai-configs'
import AIConfigDialog from '@/components/ai-configs/AIConfigDialog.vue'
import AIConfigTemplateDialog from '@/components/ai-configs/AIConfigTemplateDialog.vue'
import AIConfigDetailDialog from '@/components/ai-configs/AIConfigDetailDialog.vue'
import AIConfigTestDialog from '@/components/ai-configs/AIConfigTestDialog.vue'

// 响应式数据
const loading = ref(false)
const configs = ref<AIModelConfig[]>([])
const selectedConfigs = ref<AIModelConfig[]>([])
const viewMode = ref<'list' | 'card'>('list')

// 统计数据
const stats = ref<AIModelConfigStats>({
  total_configs: 0,
  active_configs: 0,
  inactive_configs: 0,
  model_types: {},
  request_formats: {},
  default_config_id: undefined
})

// 筛选条件
const filters = reactive({
  search: '',
  model_type: '',
  is_active: undefined as boolean | undefined
})

// 分页数据
const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

// 对话框状态
const showCreateDialog = ref(false)
const showTemplateDialog = ref(false)
const showDetailDialog = ref(false)
const showTestDialog = ref(false)

const editingConfig = ref<AIModelConfig | null>(null)
const viewingConfig = ref<AIModelConfig | null>(null)
const testingConfig = ref<AIModelConfig | null>(null)
const dialogMode = ref<'create' | 'edit'>('create')

// 搜索防抖
let searchTimeout: number | null = null

// 加载配置列表
const loadConfigs = async () => {
  try {
    loading.value = true
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      search: filters.search || undefined,
      model_type: filters.model_type || undefined,
      is_active: filters.is_active
    }
    
    const response = await aiConfigsApi.getConfigs(params)
    configs.value = response.items
    pagination.total = response.total
  } catch (error) {
    console.error('加载配置列表失败:', error)
    ElMessage.error('加载配置列表失败')
  } finally {
    loading.value = false
  }
}

// 加载统计数据
const loadStats = async () => {
  try {
    stats.value = await aiConfigsApi.getStats()
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

// 搜索处理
const handleSearch = () => {
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
  searchTimeout = setTimeout(() => {
    pagination.page = 1
    loadConfigs()
  }, 500)
}

// 选择变化处理
const handleSelectionChange = (selection: AIModelConfig[]) => {
  selectedConfigs.value = selection
}

// 切换状态
const handleToggleStatus = async (config: AIModelConfig) => {
  try {
    config.updating = true
    await aiConfigsApi.toggleConfig(config.id)
    ElMessage.success(`${config.is_active ? '启用' : '禁用'}配置成功`)
    await loadStats()
  } catch (error) {
    // 恢复原状态
    config.is_active = !config.is_active
    console.error('切换配置状态失败:', error)
    ElMessage.error('切换配置状态失败')
  } finally {
    config.updating = false
  }
}

// 设置默认配置
const handleSetDefault = async (config: AIModelConfig) => {
  try {
    await aiConfigsApi.setDefaultConfig(config.id)
    ElMessage.success('设置默认配置成功')
    await loadConfigs()
    await loadStats()
  } catch (error) {
    console.error('设置默认配置失败:', error)
    ElMessage.error('设置默认配置失败')
  }
}

// 查看配置
const handleView = (config: AIModelConfig) => {
  viewingConfig.value = config
  showDetailDialog.value = true
}

// 编辑配置
const handleEdit = (config: AIModelConfig) => {
  editingConfig.value = { ...config }
  dialogMode.value = 'edit'
  showCreateDialog.value = true
}

// 测试配置
const handleTest = (config: AIModelConfig) => {
  testingConfig.value = config
  showTestDialog.value = true
}

// 删除配置
const handleDelete = async (config: AIModelConfig) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除配置 "${config.name}" 吗？此操作不可撤销。`,
      '删除确认',
      {
        type: 'warning',
        confirmButtonText: '确定删除',
        cancelButtonText: '取消'
      }
    )
    
    await aiConfigsApi.deleteConfig(config.id)
    ElMessage.success('删除配置成功')
    await loadConfigs()
    await loadStats()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除配置失败:', error)
      ElMessage.error('删除配置失败')
    }
  }
}

// 批量删除
const handleBatchDelete = async () => {
  if (selectedConfigs.value.length === 0) {
    ElMessage.warning('请选择要删除的配置')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedConfigs.value.length} 个配置吗？此操作不可撤销。`,
      '批量删除确认',
      {
        type: 'warning',
        confirmButtonText: '确定删除',
        cancelButtonText: '取消'
      }
    )
    
    const configIds = selectedConfigs.value.map(config => config.id)
    await aiConfigsApi.batchOperation({
      config_ids: configIds,
      action: 'delete'
    })
    
    ElMessage.success(`成功删除 ${selectedConfigs.value.length} 个配置`)
    selectedConfigs.value = []
    await loadConfigs()
    await loadStats()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('批量删除失败:', error)
      ElMessage.error('批量删除失败')
    }
  }
}

// 对话框成功回调
const handleDialogSuccess = () => {
  showCreateDialog.value = false
  editingConfig.value = null
  loadConfigs()
  loadStats()
}

// 模板成功回调
const handleTemplateSuccess = () => {
  showTemplateDialog.value = false
  loadConfigs()
  loadStats()
}

// 获取模型类型标签类型
const getModelTypeTagType = (modelType: string) => {
  const typeMap: Record<string, string> = {
    'openai_compatible': 'primary',
    'claude_compatible': 'success',
    'custom_http': 'warning',
    'hugging_face': 'info',
    'ollama': 'danger',
    'openrouter': ''
  }
  return typeMap[modelType] || 'info'
}

// 格式化日期
const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleString('zh-CN')
}

// 组件挂载
onMounted(() => {
  loadConfigs()
  loadStats()
})
</script>

<style scoped>
.ai-configs-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: calc(100vh - 60px);
}

/* 头部区域 */
.header-section {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.title-section h2 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 24px;
  font-weight: 600;
}

.subtitle {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.action-section {
  display: flex;
  gap: 12px;
}

/* 统计卡片 */
.stats-section {
  margin-bottom: 20px;
}

.stats-card {
  position: relative;
  cursor: pointer;
  transition: all 0.3s ease;
}

.stats-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.stats-card.active {
  border-left: 4px solid #67c23a;
}

.stats-card.inactive {
  border-left: 4px solid #909399;
}

.stats-card.default {
  border-left: 4px solid #e6a23c;
}

.stats-content {
  padding: 10px 0;
}

.stats-number {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  line-height: 1;
}

.stats-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

.stats-icon {
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 24px;
  color: #c0c4cc;
}

/* 筛选区域 */
.filter-section {
  margin-bottom: 20px;
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.view-toggle {
  text-align: right;
}

/* 配置区域 */
.configs-section {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* 列表视图 */
.config-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 卡片视图 */
.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.config-card {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 20px;
  background: white;
  transition: all 0.3s ease;
  position: relative;
}

.config-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.config-card.active {
  border-left: 4px solid #67c23a;
}

.config-card.default {
  border-top: 3px solid #e6a23c;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.card-title h4 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 16px;
  font-weight: 600;
}

.card-badges {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.card-description {
  color: #606266;
  font-size: 14px;
  margin: 0 0 16px 0;
  line-height: 1.5;
}

.card-info {
  margin-bottom: 16px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 0;
  font-size: 14px;
}

.info-item .label {
  color: #909399;
  font-weight: 500;
}

.info-item .value {
  color: #606266;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid #f0f0f0;
  padding-top: 16px;
}

.card-actions {
  display: flex;
  gap: 8px;
}

/* 分页区域 */
.pagination-section {
  margin-top: 20px;
  text-align: center;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .ai-configs-container {
    padding: 10px;
  }
  
  .header-section {
    flex-direction: column;
    align-items: stretch;
    gap: 16px;
  }
  
  .action-section {
    flex-wrap: wrap;
  }
  
  .cards-grid {
    grid-template-columns: 1fr;
  }
  
  .filter-section .el-row {
    flex-direction: column;
    gap: 12px;
  }
  
  .view-toggle {
    text-align: left;
  }
}
</style>