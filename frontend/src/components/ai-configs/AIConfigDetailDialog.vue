<template>
  <el-dialog
    :model-value="visible"
    @update:model-value="$emit('update:visible', $event)"
    title="配置详情"
    width="800px"
  >
    <div v-if="config" class="config-detail">
      <!-- 基础信息 -->
      <el-card class="detail-section" shadow="never">
        <template #header>
          <div class="section-header">
            <el-icon><InfoFilled /></el-icon>
            <span>基础信息</span>
          </div>
        </template>
        
        <el-descriptions :column="2" border>
          <el-descriptions-item label="配置名称">
            <div class="name-with-badges">
              <span>{{ config.name }}</span>
              <el-tag v-if="config.is_default" type="warning" size="small">默认</el-tag>
              <el-tag :type="config.is_active ? 'success' : 'info'" size="small">
                {{ config.is_active ? '已启用' : '已禁用' }}
              </el-tag>
            </div>
          </el-descriptions-item>
          <el-descriptions-item label="模型类型">
            <el-tag :type="getModelTypeTagType(config.model_type)">
              {{ MODEL_TYPE_LABELS[config.model_type as keyof typeof MODEL_TYPE_LABELS] }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="描述" :span="2">
            {{ config.description || '无描述' }}
          </el-descriptions-item>
          <el-descriptions-item label="优先级">
            <el-rate v-model="config.priority" disabled show-score text-color="#ff9900" />
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatDate(config.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="更新时间" :span="2">
            {{ formatDate(config.updated_at) }}
          </el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- API配置 -->
      <el-card class="detail-section" shadow="never">
        <template #header>
          <div class="section-header">
            <el-icon><Link /></el-icon>
            <span>API配置</span>
          </div>
        </template>
        
        <el-descriptions :column="2" border>
          <el-descriptions-item label="API端点" :span="2">
            <div class="endpoint-display">
              <el-input
                :model-value="config.api_endpoint"
                readonly
                class="readonly-input"
              />
              <el-button
                size="small"
                icon="CopyDocument"
                @click="copyToClipboard(config.api_endpoint)"
              />
            </div>
          </el-descriptions-item>
          <el-descriptions-item label="模型名称">
            {{ config.model_name }}
          </el-descriptions-item>
          <el-descriptions-item label="请求格式">
            <el-tag>{{ REQUEST_FORMAT_LABELS[config.request_format as keyof typeof REQUEST_FORMAT_LABELS] }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="API密钥">
            <span class="masked-key">{{ config.api_key || '未设置' }}</span>
          </el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- 请求参数 -->
      <el-card class="detail-section" shadow="never">
        <template #header>
          <div class="section-header">
            <el-icon><Setting /></el-icon>
            <span>请求参数</span>
          </div>
        </template>
        
        <el-descriptions :column="3" border>
          <el-descriptions-item label="最大Token数">
            <el-tag type="info">{{ config.max_tokens }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="温度参数">
            <el-tag type="info">{{ config.temperature }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="超时时间">
            <el-tag type="info">{{ config.timeout }}秒</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="重试次数" :span="3">
            <el-tag type="info">{{ config.retry_count }}次</el-tag>
          </el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- 高级配置 -->
      <el-card v-if="hasAdvancedConfig" class="detail-section" shadow="never">
        <template #header>
          <div class="section-header">
            <el-icon><Tools /></el-icon>
            <span>高级配置</span>
          </div>
        </template>
        
        <!-- 自定义请求头 -->
        <div v-if="config.request_headers && Object.keys(config.request_headers).length > 0" class="advanced-item">
          <h4>自定义请求头</h4>
          <el-table :data="requestHeadersData" size="small">
            <el-table-column prop="key" label="Header名称" />
            <el-table-column prop="value" label="Header值" />
          </el-table>
        </div>

        <!-- 请求参数映射 -->
        <div v-if="config.request_params && Object.keys(config.request_params).length > 0" class="advanced-item">
          <h4>请求参数映射</h4>
          <el-table :data="requestParamsData" size="small">
            <el-table-column prop="key" label="参数名" />
            <el-table-column prop="value" label="参数值" />
          </el-table>
        </div>

        <!-- 响应映射 -->
        <div v-if="config.response_mapping && Object.keys(config.response_mapping).length > 0" class="advanced-item">
          <h4>响应数据映射</h4>
          <el-table :data="responseMappingData" size="small">
            <el-table-column prop="key" label="字段名" />
            <el-table-column prop="value" label="映射路径" />
          </el-table>
        </div>

        <!-- 提示词配置 -->
        <div v-if="config.system_message || config.prompt_template" class="advanced-item">
          <h4>提示词配置</h4>
          <div v-if="config.system_message" class="prompt-item">
            <label>系统消息:</label>
            <el-input
              :model-value="config.system_message"
              type="textarea"
              :rows="3"
              readonly
              class="readonly-input"
            />
          </div>
          <div v-if="config.prompt_template" class="prompt-item">
            <label>提示词模板:</label>
            <el-input
              :model-value="config.prompt_template"
              type="textarea"
              :rows="4"
              readonly
              class="readonly-input"
            />
          </div>
        </div>

        <!-- 使用限制 -->
        <div v-if="config.daily_limit || config.monthly_limit" class="advanced-item">
          <h4>使用限制</h4>
          <el-descriptions :column="2" border size="small">
            <el-descriptions-item v-if="config.daily_limit" label="每日限制">
              {{ config.daily_limit }} 次
            </el-descriptions-item>
            <el-descriptions-item v-if="config.monthly_limit" label="每月限制">
              {{ config.monthly_limit }} 次
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </el-card>

      <!-- 使用统计 -->
      <el-card class="detail-section" shadow="never">
        <template #header>
          <div class="section-header">
            <el-icon><DataAnalysis /></el-icon>
            <span>使用统计</span>
          </div>
        </template>
        
        <div class="stats-placeholder">
          <el-empty description="暂无使用统计数据" />
        </div>
      </el-card>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="$emit('update:visible', false)">关闭</el-button>
        <el-button type="primary" @click="handleEdit">
          编辑配置
        </el-button>
        <el-button type="success" @click="handleTest">
          测试连接
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ElMessage } from 'element-plus'
import {
  InfoFilled, Link, Setting, Tools, DataAnalysis, CopyDocument
} from '@element-plus/icons-vue'

import {
  MODEL_TYPE_LABELS,
  REQUEST_FORMAT_LABELS,
  type AIModelConfig
} from '@/api/ai-configs'

// Props
interface Props {
  visible: boolean
  config?: AIModelConfig | null
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  'update:visible': [value: boolean]
  edit: [config: AIModelConfig]
  test: [config: AIModelConfig]
}>()

// 计算属性
const hasAdvancedConfig = computed(() => {
  if (!props.config) return false
  
  return !!(
    (props.config.request_headers && Object.keys(props.config.request_headers).length > 0) ||
    (props.config.request_params && Object.keys(props.config.request_params).length > 0) ||
    (props.config.response_mapping && Object.keys(props.config.response_mapping).length > 0) ||
    props.config.system_message ||
    props.config.prompt_template ||
    props.config.daily_limit ||
    props.config.monthly_limit
  )
})

const requestHeadersData = computed(() => {
  if (!props.config?.request_headers) return []
  return Object.entries(props.config.request_headers).map(([key, value]) => ({
    key,
    value: String(value)
  }))
})

const requestParamsData = computed(() => {
  if (!props.config?.request_params) return []
  return Object.entries(props.config.request_params).map(([key, value]) => ({
    key,
    value: JSON.stringify(value)
  }))
})

const responseMappingData = computed(() => {
  if (!props.config?.response_mapping) return []
  return Object.entries(props.config.response_mapping).map(([key, value]) => ({
    key,
    value: String(value)
  }))
})

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

// 复制到剪贴板
const copyToClipboard = async (text: string) => {
  try {
    await navigator.clipboard.writeText(text)
    ElMessage.success('已复制到剪贴板')
  } catch (error) {
    console.error('复制失败:', error)
    ElMessage.error('复制失败')
  }
}

// 处理编辑
const handleEdit = () => {
  if (props.config) {
    emit('edit', props.config)
  }
}

// 处理测试
const handleTest = () => {
  if (props.config) {
    emit('test', props.config)
  }
}
</script>

<style scoped>
.config-detail {
  max-height: 600px;
  overflow-y: auto;
}

.detail-section {
  margin-bottom: 20px;
}

.detail-section:last-child {
  margin-bottom: 0;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.name-with-badges {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.endpoint-display {
  display: flex;
  align-items: center;
  gap: 8px;
}

.readonly-input {
  background-color: #f5f7fa;
}

.masked-key {
  font-family: monospace;
  color: #909399;
}

.advanced-item {
  margin-bottom: 20px;
}

.advanced-item:last-child {
  margin-bottom: 0;
}

.advanced-item h4 {
  margin: 0 0 12px 0;
  color: #303133;
  font-size: 14px;
  font-weight: 600;
}

.prompt-item {
  margin-bottom: 12px;
}

.prompt-item:last-child {
  margin-bottom: 0;
}

.prompt-item label {
  display: block;
  margin-bottom: 4px;
  color: #606266;
  font-size: 13px;
  font-weight: 500;
}

.stats-placeholder {
  text-align: center;
  padding: 40px 20px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

:deep(.el-card__header) {
  padding: 12px 16px;
  border-bottom: 1px solid #f0f0f0;
}

:deep(.el-card__body) {
  padding: 16px;
}

:deep(.el-descriptions__label) {
  font-weight: 600;
  color: #606266;
  width: 120px;
}

:deep(.el-descriptions__content) {
  color: #303133;
}

:deep(.readonly-input .el-input__inner) {
  background-color: #f5f7fa;
  color: #606266;
}

:deep(.readonly-input .el-textarea__inner) {
  background-color: #f5f7fa;
  color: #606266;
}

/* 滚动条样式 */
.config-detail::-webkit-scrollbar {
  width: 6px;
}

.config-detail::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.config-detail::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.config-detail::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>