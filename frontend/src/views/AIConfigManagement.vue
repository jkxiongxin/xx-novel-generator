<template>
  <div class="ai-config-management">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="container">
        <div class="header-content">
          <div class="header-info">
            <h1 class="page-title">
              <el-icon><Setting /></el-icon>
              AI模型配置管理
            </h1>
            <p class="page-description">
              管理和配置你的AI模型，支持OpenAI、Claude、本地模型等多种类型
            </p>
          </div>
          <div class="header-actions">
            <el-button type="primary" @click="handleCreateConfig">
              <el-icon><Plus /></el-icon>
              新增配置
            </el-button>
            <el-button @click="showTemplateDialog = true">
              <el-icon><Document /></el-icon>
              从模板创建
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="main-content">
      <div class="container">
        <!-- 统计概览 -->
        <div class="stats-section">
          <el-row :gutter="20">
            <el-col :span="6">
              <div class="stat-card">
                <div class="stat-icon total">
                  <el-icon><DataAnalysis /></el-icon>
                </div>
                <div class="stat-content">
                  <div class="stat-number">{{ stats.total_configs || 0 }}</div>
                  <div class="stat-label">总配置数</div>
                </div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-card">
                <div class="stat-icon active">
                  <el-icon><Check /></el-icon>
                </div>
                <div class="stat-content">
                  <div class="stat-number">{{ stats.active_configs || 0 }}</div>
                  <div class="stat-label">已启用</div>
                </div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-card">
                <div class="stat-icon groups">
                  <el-icon><FolderOpened /></el-icon>
                </div>
                <div class="stat-content">
                  <div class="stat-number">{{ groupList.total_groups || 0 }}</div>
                  <div class="stat-label">分组数量</div>
                </div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-card">
                <div class="stat-icon default">
                  <el-icon><Star /></el-icon>
                </div>
                <div class="stat-content">
                  <div class="stat-number">{{ stats.default_config_id ? 1 : 0 }}</div>
                  <div class="stat-label">默认配置</div>
                </div>
              </div>
            </el-col>
          </el-row>
        </div>

        <!-- 分组展示 -->
        <div class="groups-section">
          <div class="section-header">
            <h2 class="section-title">
              <el-icon><FolderOpened /></el-icon>
              配置分组
            </h2>
            <div class="section-actions">
              <el-select v-model="selectedGroupFilter" placeholder="筛选分组" clearable style="width: 200px;">
                <el-option label="全部分组" value="" />
                <el-option 
                  v-for="group in groupList.groups" 
                  :key="group.group_name"
                  :label="group.group_name"
                  :value="group.group_name"
                />
              </el-select>
              <el-button @click="refreshData">
                <el-icon><Refresh /></el-icon>
                刷新
              </el-button>
            </div>
          </div>

          <!-- 分组卡片 -->
          <div class="groups-grid" v-loading="groupsLoading">
            <div 
              v-for="group in filteredGroups" 
              :key="group.group_name"
              class="group-card"
              @click="expandGroup(group)"
            >
              <div class="group-header">
                <div class="group-info">
                  <h3 class="group-name">{{ group.group_name }}</h3>
                  <p class="group-description">{{ group.group_description || '暂无描述' }}</p>
                </div>
                <div class="group-stats">
                  <div class="stat-item">
                    <span class="stat-label">配置数</span>
                    <span class="stat-value">{{ group.model_count }}</span>
                  </div>
                  <div class="stat-item">
                    <span class="stat-label">已启用</span>
                    <span class="stat-value active">{{ group.active_count }}</span>
                  </div>
                </div>
              </div>
              
              <div class="group-configs">
                <div class="config-item" v-for="config in group.configs.slice(0, 3)" :key="config.id">
                  <el-tag 
                    :type="config.is_active ? 'success' : 'info'"
                    size="small"
                  >
                    {{ config.name }}
                  </el-tag>
                  <el-tag 
                    v-if="config.is_default || config.is_group_default"
                    type="warning"
                    size="small"
                  >
                    默认
                  </el-tag>
                </div>
                <div v-if="group.model_count > 3" class="more-configs">
                  +{{ group.model_count - 3 }} 个配置
                </div>
              </div>

              <div class="group-actions">
                <el-button size="small" @click.stop="manageGroup(group)">
                  <el-icon><Edit /></el-icon>
                  管理
                </el-button>
                <el-button size="small" type="primary" @click.stop="addToGroup(group.group_name)">
                  <el-icon><Plus /></el-icon>
                  添加配置
                </el-button>
              </div>
            </div>

            <!-- 空状态 -->
            <div v-if="filteredGroups.length === 0" class="empty-state">
              <el-empty description="暂无配置分组">
                <el-button type="primary" @click="handleCreateConfig">
                  创建第一个配置
                </el-button>
              </el-empty>
            </div>
          </div>
        </div>

        <!-- 最近使用的配置 -->
        <div class="recent-section">
          <div class="section-header">
            <h2 class="section-title">
              <el-icon><Clock /></el-icon>
              最近使用
            </h2>
          </div>
          <div class="recent-configs">
            <div 
              v-for="config in recentConfigs" 
              :key="config.id"
              class="recent-config-card"
              @click="handleViewDetail(config)"
            >
              <div class="config-info">
                <div class="config-name">{{ config.name }}</div>
                <div class="config-meta">
                  <el-tag size="small">{{ MODEL_TYPE_LABELS[config.model_type] }}</el-tag>
                  <span class="config-group">{{ config.group_name || '未分组' }}</span>
                </div>
              </div>
              <div class="config-status">
                <el-switch 
                  v-model="config.is_active" 
                  @change="toggleConfig(config)"
                  @click.stop
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- AI配置创建/编辑对话框 -->
    <AIConfigDialog
      v-model:visible="showConfigDialog"
      :config="currentEditConfig"
      :mode="configDialogMode"
      @success="handleConfigSuccess"
    />

    <!-- AI配置详情对话框 -->
    <AIConfigDetailDialog
      v-model:visible="showDetailDialog"
      :config="selectedConfig"
      @edit="handleEditConfig"
      @test="handleTestConfig"
    />

    <!-- 模板选择对话框 -->
    <el-dialog
      v-model="showTemplateDialog"
      title="从模板创建"
      width="600px"
    >
      <p>此处可集成模板选择功能</p>
      <template #footer>
        <el-button @click="showTemplateDialog = false">取消</el-button>
        <el-button type="primary">确定</el-button>
      </template>
    </el-dialog>

    <!-- 分组管理对话框 -->
    <el-dialog
      v-model="showGroupDialog"
      title="分组管理"
      width="800px"
    >
      <div v-if="selectedGroup">
        <div class="group-detail-header">
          <h3>{{ selectedGroup.group_name }}</h3>
          <p>{{ selectedGroup.group_description }}</p>
        </div>
        
        <el-table :data="selectedGroup.configs" stripe>
          <el-table-column prop="name" label="配置名称" />
          <el-table-column prop="model_type" label="类型">
            <template #default="{ row }">
              <el-tag size="small">{{ MODEL_TYPE_LABELS[row.model_type as keyof typeof MODEL_TYPE_LABELS] }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="is_active" label="状态" width="80">
            <template #default="{ row }">
              <el-switch v-model="row.is_active" @change="toggleConfig(row)" />
            </template>
          </el-table-column>
          <el-table-column label="默认" width="80">
            <template #default="{ row }">
              <el-button 
                v-if="!row.is_group_default && row.is_active"
                size="small"
                type="primary"
                text
                @click="setGroupDefault(row)"
              >
                设为默认
              </el-button>
              <el-tag v-else-if="row.is_group_default" type="warning" size="small">
                默认
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120">
            <template #default="{ row }">
              <el-button size="small" @click="handleEditConfig(row)">编辑</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Setting,
  Plus,
  Document,
  DataAnalysis,
  Check,
  FolderOpened,
  Star,
  Refresh,
  Edit,
  Clock
} from '@element-plus/icons-vue'
import {
  aiConfigs,
  MODEL_TYPE_LABELS,
  type AIModelConfig,
  type AIModelConfigStats,
  type AIModelGroupListResponse,
  type AIModelGroup
} from '@/api/ai-configs'
import AIConfigDialog from '@/components/ai-configs/AIConfigDialog.vue'
import AIConfigDetailDialog from '@/components/ai-configs/AIConfigDetailDialog.vue'

const router = useRouter()

// 响应式数据
const statsLoading = ref(false)
const groupsLoading = ref(false)
const showConfigDialog = ref(false)
const showTemplateDialog = ref(false)
const showDetailDialog = ref(false)
const showGroupDialog = ref(false)
const selectedGroupFilter = ref('')
const selectedConfig = ref<AIModelConfig | null>(null)
const selectedGroup = ref<AIModelGroup | null>(null)
const currentEditConfig = ref<AIModelConfig | null>(null)
const configDialogMode = ref<'create' | 'edit'>('create')

// 数据状态
const stats = ref<AIModelConfigStats>({
  total_configs: 0,
  active_configs: 0,
  inactive_configs: 0,
  model_types: {},
  request_formats: {}
})

const groupList = ref<AIModelGroupListResponse>({
  groups: [],
  total_groups: 0,
  total_configs: 0
})

const recentConfigs = ref<AIModelConfig[]>([])

// 计算属性
const filteredGroups = computed(() => {
  if (!selectedGroupFilter.value) {
    return groupList.value.groups
  }
  return groupList.value.groups.filter(group => 
    group.group_name === selectedGroupFilter.value
  )
})

// 方法
const loadStats = async () => {
  try {
    statsLoading.value = true
    const data = await aiConfigs.getStats()
    stats.value = data
  } catch (error) {
    console.error('加载统计数据失败:', error)
    ElMessage.error('加载统计数据失败')
  } finally {
    statsLoading.value = false
  }
}

const loadGroups = async () => {
  try {
    groupsLoading.value = true
    const data = await aiConfigs.getGroups()
    groupList.value = data
  } catch (error) {
    console.error('加载分组数据失败:', error)
    ElMessage.error('加载分组数据失败')
  } finally {
    groupsLoading.value = false
  }
}

const loadRecentConfigs = async () => {
  try {
    // 获取最近使用的配置（取前5个）
    const data = await aiConfigs.list({ page: 1, page_size: 5 })
    recentConfigs.value = data.items
  } catch (error) {
    console.error('加载最近配置失败:', error)
  }
}

const refreshData = async () => {
  await Promise.all([
    loadStats(),
    loadGroups(),
    loadRecentConfigs()
  ])
}

const expandGroup = (group: AIModelGroup) => {
  // 可以实现展开/折叠逻辑，这里暂时使用管理功能
  manageGroup(group)
}

const manageGroup = (group: AIModelGroup) => {
  selectedGroup.value = group
  showGroupDialog.value = true
}

const addToGroup = (groupName: string) => {
  // 预填充分组名称，创建新配置
  currentEditConfig.value = null
  configDialogMode.value = 'create'
  showConfigDialog.value = true
  // 这里可以通过事件或者其他方式传递默认分组
}

const handleCreateConfig = () => {
  currentEditConfig.value = null
  configDialogMode.value = 'create'
  showConfigDialog.value = true
}

const handleViewDetail = (config: AIModelConfig) => {
  selectedConfig.value = config
  showDetailDialog.value = true
}

const handleEditConfig = (config: AIModelConfig) => {
  currentEditConfig.value = config
  configDialogMode.value = 'edit'
  showConfigDialog.value = true
}

const handleTestConfig = async (config: AIModelConfig) => {
  try {
    // 这里可以调用测试配置的API
    ElMessage.info('测试连接功能开发中...')
  } catch (error) {
    console.error('测试配置失败:', error)
    ElMessage.error('测试配置失败')
  }
}

const toggleConfig = async (config: AIModelConfig) => {
  try {
    await aiConfigs.toggle(config.id)
    ElMessage.success(`配置已${config.is_active ? '启用' : '禁用'}`)
    refreshData()
  } catch (error) {
    console.error('切换配置状态失败:', error)
    ElMessage.error('操作失败')
    // 恢复原状态
    config.is_active = !config.is_active
  }
}

const setGroupDefault = async (config: AIModelConfig) => {
  try {
    await aiConfigs.setGroupDefault(config.id)
    ElMessage.success('已设为分组默认配置')
    refreshData()
  } catch (error) {
    console.error('设置分组默认失败:', error)
    ElMessage.error('设置失败')
  }
}

const handleConfigSuccess = () => {
  refreshData()
  showConfigDialog.value = false
}

// 生命周期
onMounted(() => {
  refreshData()
})
</script>

<style scoped>
.ai-config-management {
  min-height: 100vh;
  background: #f5f7fa;
}

.page-header {
  background: white;
  border-bottom: 1px solid #e4e7ed;
  padding: 24px 0;
}

.container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 20px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 8px 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.page-description {
  color: #606266;
  margin: 0;
  font-size: 14px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.main-content {
  padding: 24px 0;
}

/* 统计卡片 */
.stats-section {
  margin-bottom: 32px;
}

.stat-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  display: flex;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  font-size: 20px;
  color: white;
}

.stat-icon.total { background: #409eff; }
.stat-icon.active { background: #67c23a; }
.stat-icon.groups { background: #e6a23c; }
.stat-icon.default { background: #f56c6c; }

.stat-content {
  flex: 1;
}

.stat-number {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  line-height: 1;
}

.stat-label {
  color: #909399;
  font-size: 14px;
  margin-top: 4px;
}

/* 分组部分 */
.groups-section {
  margin-bottom: 32px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.section-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.groups-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 20px;
}

.group-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid #e4e7ed;
}

.group-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.group-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.group-name {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 4px 0;
}

.group-description {
  color: #909399;
  font-size: 12px;
  margin: 0;
}

.group-stats {
  display: flex;
  gap: 16px;
}

.stat-item {
  text-align: center;
}

.stat-item .stat-label {
  display: block;
  font-size: 12px;
  color: #909399;
}

.stat-item .stat-value {
  display: block;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.stat-item .stat-value.active {
  color: #67c23a;
}

.group-configs {
  margin-bottom: 16px;
}

.config-item {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
}

.more-configs {
  color: #909399;
  font-size: 12px;
  font-style: italic;
}

.group-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

/* 最近使用 */
.recent-section {
  margin-bottom: 32px;
}

.recent-configs {
  background: white;
  border-radius: 8px;
  overflow: hidden;
}

.recent-config-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #f0f2f5;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.recent-config-card:last-child {
  border-bottom: none;
}

.recent-config-card:hover {
  background: #f8f9fa;
}

.config-info {
  flex: 1;
}

.config-name {
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.config-meta {
  display: flex;
  align-items: center;
  gap: 12px;
}

.config-group {
  color: #909399;
  font-size: 12px;
}

/* 分组详情对话框 */
.group-detail-header {
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f2f5;
}

.group-detail-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 8px 0;
}

.group-detail-header p {
  color: #606266;
  margin: 0;
  font-size: 14px;
}

/* 空状态 */
.empty-state {
  grid-column: 1 / -1;
  padding: 40px;
  text-align: center;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }

  .groups-grid {
    grid-template-columns: 1fr;
  }

  .group-header {
    flex-direction: column;
    gap: 12px;
  }

  .group-stats {
    align-self: flex-start;
  }

  .section-header {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }

  .section-actions {
    width: 100%;
    justify-content: flex-start;
  }
}
</style>