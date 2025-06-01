<template>
  <el-dialog
    :model-value="visible"
    @update:model-value="$emit('update:visible', $event)"
    title="从模板创建配置"
    width="700px"
  >
    <div v-loading="loading" class="template-container">
      <div class="template-grid">
        <div
          v-for="template in templates"
          :key="template.name"
          class="template-card"
          :class="{ selected: selectedTemplate?.name === template.name }"
          @click="selectTemplate(template)"
        >
          <div class="template-header">
            <h4>{{ template.name }}</h4>
            <el-tag :type="getTemplateTagType(template.model_type)">
              {{ MODEL_TYPE_LABELS[template.model_type as keyof typeof MODEL_TYPE_LABELS] }}
            </el-tag>
          </div>
          <p class="template-description">{{ template.description }}</p>
          <div class="template-details">
            <div class="detail-item">
              <span class="label">请求格式:</span>
              <span class="value">{{ REQUEST_FORMAT_LABELS[template.request_format as keyof typeof REQUEST_FORMAT_LABELS] }}</span>
            </div>
            <div class="detail-item">
              <span class="label">默认模型:</span>
              <span class="value">{{ template.default_config.model_name }}</span>
            </div>
          </div>
          <div class="template-footer">
            <el-icon class="check-icon" v-if="selectedTemplate?.name === template.name">
              <Check />
            </el-icon>
          </div>
        </div>
      </div>

      <!-- API密钥输入 -->
      <div v-if="selectedTemplate" class="api-key-section">
        <el-card shadow="never">
          <template #header>
            <div class="section-header">
              <el-icon><Key /></el-icon>
              <span>API密钥配置</span>
            </div>
          </template>
          
          <el-form :model="configForm" label-width="100px">
            <el-form-item label="API密钥" required>
              <el-input
                v-model="configForm.api_key"
                type="password"
                placeholder="请输入API密钥"
                show-password
                maxlength="500"
              />
              <div class="help-text">
                <p>请输入对应服务的API密钥。如果暂时没有，可以稍后在配置中添加。</p>
              </div>
            </el-form-item>
            
            <el-form-item label="配置名称">
              <el-input
                v-model="configForm.name"
                placeholder="自定义配置名称（可选）"
                maxlength="200"
              />
              <div class="help-text">
                <p>如果不填写，将使用默认名称。</p>
              </div>
            </el-form-item>
          </el-form>
        </el-card>
      </div>

      <!-- 配置预览 -->
      <div v-if="selectedTemplate" class="config-preview">
        <el-card shadow="never">
          <template #header>
            <div class="section-header">
              <el-icon><View /></el-icon>
              <span>配置预览</span>
            </div>
          </template>
          
          <div class="preview-content">
            <el-descriptions :column="2" border>
              <el-descriptions-item label="配置名称">
                {{ configForm.name || `${selectedTemplate.name} - ${mockUser.username}` }}
              </el-descriptions-item>
              <el-descriptions-item label="模型类型">
                {{ MODEL_TYPE_LABELS[selectedTemplate.model_type as keyof typeof MODEL_TYPE_LABELS] }}
              </el-descriptions-item>
              <el-descriptions-item label="API端点">
                {{ selectedTemplate.default_config.api_endpoint }}
              </el-descriptions-item>
              <el-descriptions-item label="模型名称">
                {{ selectedTemplate.default_config.model_name }}
              </el-descriptions-item>
              <el-descriptions-item label="请求格式">
                {{ REQUEST_FORMAT_LABELS[selectedTemplate.request_format as keyof typeof REQUEST_FORMAT_LABELS] }}
              </el-descriptions-item>
              <el-descriptions-item label="最大Token">
                {{ selectedTemplate.default_config.max_tokens }}
              </el-descriptions-item>
              <el-descriptions-item label="温度参数">
                {{ selectedTemplate.default_config.temperature }}
              </el-descriptions-item>
              <el-descriptions-item label="超时时间">
                {{ selectedTemplate.default_config.timeout }}秒
              </el-descriptions-item>
            </el-descriptions>
          </div>
        </el-card>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleCancel">取消</el-button>
        <el-button
          type="primary"
          :disabled="!selectedTemplate"
          :loading="creating"
          @click="handleCreate"
        >
          创建配置
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Check, Key, View } from '@element-plus/icons-vue'

import {
  aiConfigsApi,
  MODEL_TYPE_LABELS,
  REQUEST_FORMAT_LABELS,
  type AIModelConfigTemplate
} from '@/api/ai-configs'

// Props
interface Props {
  visible: boolean
}

defineProps<Props>()

// Emits
const emit = defineEmits<{
  'update:visible': [value: boolean]
  success: []
}>()

// 模拟用户信息，实际项目中应该从store或其他地方获取
const mockUser = { username: 'user' }

// 响应式数据
const loading = ref(false)
const creating = ref(false)
const templates = ref<AIModelConfigTemplate[]>([])
const selectedTemplate = ref<AIModelConfigTemplate | null>(null)

// 表单数据
const configForm = reactive({
  api_key: '',
  name: ''
})

// 加载模板
const loadTemplates = async () => {
  try {
    loading.value = true
    templates.value = await aiConfigsApi.getTemplates()
  } catch (error) {
    console.error('加载模板失败:', error)
    ElMessage.error('加载模板失败')
  } finally {
    loading.value = false
  }
}

// 选择模板
const selectTemplate = (template: AIModelConfigTemplate) => {
  selectedTemplate.value = template
  // 重置表单
  configForm.api_key = ''
  configForm.name = ''
}

// 获取模板标签类型
const getTemplateTagType = (modelType: string) => {
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

// 处理取消
const handleCancel = () => {
  emit('update:visible', false)
  selectedTemplate.value = null
  configForm.api_key = ''
  configForm.name = ''
}

// 处理创建
const handleCreate = async () => {
  if (!selectedTemplate.value) {
    ElMessage.warning('请选择一个模板')
    return
  }
  
  if (!configForm.api_key.trim()) {
    ElMessage.warning('请输入API密钥')
    return
  }
  
  try {
    creating.value = true
    
    // 构建模板名称
    const templateName = selectedTemplate.value.name.toLowerCase().replace(/\s+/g, '-')
    
    // 创建配置
    await aiConfigsApi.createFromTemplate(templateName, configForm.api_key)
    
    ElMessage.success('从模板创建配置成功')
    emit('success')
    handleCancel()
    
  } catch (error) {
    console.error('从模板创建配置失败:', error)
    ElMessage.error('从模板创建配置失败')
  } finally {
    creating.value = false
  }
}

// 组件挂载
onMounted(() => {
  loadTemplates()
})
</script>

<style scoped>
.template-container {
  min-height: 400px;
}

.template-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.template-card {
  border: 2px solid #e4e7ed;
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  background: white;
}

.template-card:hover {
  border-color: #409eff;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15);
}

.template-card.selected {
  border-color: #409eff;
  background-color: #f0f9ff;
}

.template-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.template-header h4 {
  margin: 0;
  color: #303133;
  font-size: 16px;
  font-weight: 600;
}

.template-description {
  color: #606266;
  font-size: 14px;
  line-height: 1.5;
  margin: 0 0 12px 0;
}

.template-details {
  margin-bottom: 12px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 2px 0;
  font-size: 13px;
}

.detail-item .label {
  color: #909399;
  font-weight: 500;
}

.detail-item .value {
  color: #606266;
}

.template-footer {
  text-align: right;
  height: 20px;
}

.check-icon {
  color: #67c23a;
  font-size: 20px;
}

.api-key-section {
  margin: 20px 0;
}

.config-preview {
  margin-top: 20px;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.help-text {
  margin-top: 4px;
}

.help-text p {
  margin: 0;
  font-size: 12px;
  color: #909399;
  line-height: 1.4;
}

.preview-content {
  margin-top: 16px;
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
}

:deep(.el-descriptions__content) {
  color: #303133;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .template-grid {
    grid-template-columns: 1fr;
  }
  
  .template-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}
</style>