<template>
  <el-dialog
    :model-value="visible"
    @update:model-value="$emit('update:visible', $event)"
    :title="dialogTitle"
    width="800px"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="formRules"
      label-width="120px"
      @submit.prevent
    >
      <!-- 基础信息 -->
      <el-card class="form-section" shadow="never">
        <template #header>
          <div class="section-header">
            <el-icon><Setting /></el-icon>
            <span>基础信息</span>
          </div>
        </template>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="配置名称" prop="name">
              <el-input
                v-model="formData.name"
                placeholder="请输入配置名称"
                maxlength="200"
                show-word-limit
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="模型类型" prop="model_type">
              <el-select
                v-model="formData.model_type"
                placeholder="请选择模型类型"
                @change="handleModelTypeChange"
              >
                <el-option
                  v-for="(label, value) in MODEL_TYPE_LABELS"
                  :key="value"
                  :label="label"
                  :value="value"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="请输入配置描述"
            maxlength="1000"
            show-word-limit
          />
        </el-form-item>
        
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="优先级" prop="priority">
              <el-input-number
                v-model="formData.priority"
                :min="1"
                :max="10"
                controls-position="right"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="启用状态">
              <el-switch v-model="formData.is_active" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="设为默认">
              <el-switch v-model="formData.is_default" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-card>

      <!-- API配置 -->
      <el-card class="form-section" shadow="never">
        <template #header>
          <div class="section-header">
            <el-icon><Link /></el-icon>
            <span>API配置</span>
          </div>
        </template>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="API端点" prop="api_endpoint">
              <el-input
                v-model="formData.api_endpoint"
                placeholder="https://api.example.com/v1/chat/completions"
              >
                <template #prepend>
                  <el-select
                    v-model="selectedPreset"
                    placeholder="预设"
                    style="width: 100px"
                    @change="handlePresetChange"
                  >
                    <el-option label="OpenAI" value="openai" />
                    <el-option label="Claude" value="claude" />
                    <el-option label="OpenRouter" value="openrouter" />
                  </el-select>
                </template>
              </el-input>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="请求格式" prop="request_format">
              <el-select v-model="formData.request_format" placeholder="请选择请求格式">
                <el-option
                  v-for="(label, value) in REQUEST_FORMAT_LABELS"
                  :key="value"
                  :label="label"
                  :value="value"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="模型名称" prop="model_name">
              <el-input
                v-model="formData.model_name"
                placeholder="gpt-3.5-turbo"
              >
                <template #append>
                  <el-button @click="showModelSelector = true">选择</el-button>
                </template>
              </el-input>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="API密钥" prop="api_key">
              <el-input
                v-model="formData.api_key"
                type="password"
                placeholder="请输入API密钥"
                show-password
              />
            </el-form-item>
          </el-col>
        </el-row>
      </el-card>

      <!-- 请求参数 -->
      <el-card class="form-section" shadow="never">
        <template #header>
          <div class="section-header">
            <el-icon><Tools /></el-icon>
            <span>请求参数</span>
          </div>
        </template>
        
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="最大Token数" prop="max_tokens">
              <el-input-number
                v-model="formData.max_tokens"
                :min="1"
                :max="100000"
                controls-position="right"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="温度参数" prop="temperature">
              <el-input
                v-model="formData.temperature"
                placeholder="0.7"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="超时时间(秒)" prop="timeout">
              <el-input-number
                v-model="formData.timeout"
                :min="1"
                :max="300"
                controls-position="right"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="重试次数" prop="retry_count">
              <el-input-number
                v-model="formData.retry_count"
                :min="0"
                :max="10"
                controls-position="right"
              />
            </el-form-item>
          </el-col>
        </el-row>
      </el-card>

      <!-- 高级配置 -->
      <el-collapse v-model="activeCollapse">
        <el-collapse-item title="高级配置" name="advanced">
          <!-- 自定义请求头 -->
          <el-card class="form-section" shadow="never">
            <template #header>
              <div class="section-header">
                <el-icon><Document /></el-icon>
                <span>自定义请求头</span>
                <el-button size="small" type="primary" @click="addRequestHeader">
                  添加
                </el-button>
              </div>
            </template>
            
            <div v-for="(header, index) in requestHeaders" :key="index" class="header-item">
              <el-row :gutter="10">
                <el-col :span="10">
                  <el-input v-model="header.key" placeholder="Header名称" />
                </el-col>
                <el-col :span="12">
                  <el-input v-model="header.value" placeholder="Header值" />
                </el-col>
                <el-col :span="2">
                  <el-button
                    type="danger"
                    icon="Delete"
                    circle
                    size="small"
                    @click="removeRequestHeader(index)"
                  />
                </el-col>
              </el-row>
            </div>
          </el-card>

          <!-- 提示词模板 -->
          <el-card class="form-section" shadow="never">
            <template #header>
              <div class="section-header">
                <el-icon><EditPen /></el-icon>
                <span>提示词配置</span>
              </div>
            </template>
            
            <el-form-item label="系统消息">
              <el-input
                v-model="formData.system_message"
                type="textarea"
                :rows="3"
                placeholder="系统消息模板，可使用 {变量名} 占位符"
              />
            </el-form-item>
            
            <el-form-item label="提示词模板">
              <el-input
                v-model="formData.prompt_template"
                type="textarea"
                :rows="4"
                placeholder="提示词模板，可使用 {prompt} 等占位符"
              />
            </el-form-item>
          </el-card>

          <!-- 使用限制 -->
          <el-card class="form-section" shadow="never">
            <template #header>
              <div class="section-header">
                <el-icon><Clock /></el-icon>
                <span>使用限制</span>
              </div>
            </template>
            
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="每日限制">
                  <el-input-number
                    v-model="formData.daily_limit"
                    :min="1"
                    controls-position="right"
                    placeholder="不限制"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="每月限制">
                  <el-input-number
                    v-model="formData.monthly_limit"
                    :min="1"
                    controls-position="right"
                    placeholder="不限制"
                  />
                </el-form-item>
              </el-col>
            </el-row>
          </el-card>
        </el-collapse-item>
      </el-collapse>
    </el-form>

    <!-- 模型选择器对话框 -->
    <el-dialog
      v-model="showModelSelector"
      title="选择模型"
      width="500px"
      append-to-body
    >
      <div class="model-selector">
        <el-tabs v-model="activeModelTab">
          <el-tab-pane label="OpenAI" name="openai">
            <el-radio-group v-model="selectedModel" direction="vertical">
              <el-radio
                v-for="model in COMMON_MODELS.OPENAI"
                :key="model"
                :label="model"
              >
                {{ model }}
              </el-radio>
            </el-radio-group>
          </el-tab-pane>
          <el-tab-pane label="Claude" name="claude">
            <el-radio-group v-model="selectedModel" direction="vertical">
              <el-radio
                v-for="model in COMMON_MODELS.CLAUDE"
                :key="model"
                :label="model"
              >
                {{ model }}
              </el-radio>
            </el-radio-group>
          </el-tab-pane>
        </el-tabs>
      </div>
      
      <template #footer>
        <el-button @click="showModelSelector = false">取消</el-button>
        <el-button type="primary" @click="handleModelSelect">确定</el-button>
      </template>
    </el-dialog>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleCancel">取消</el-button>
        <el-button type="primary" @click="handleTest" :loading="testing">
          测试连接
        </el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          {{ mode === 'create' ? '创建' : '保存' }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Setting, Link, Tools, Document, EditPen, Clock, Delete
} from '@element-plus/icons-vue'

import {
  aiConfigsApi,
  MODEL_TYPE_LABELS,
  REQUEST_FORMAT_LABELS,
  DEFAULT_CONFIG,
  PRESET_ENDPOINTS,
  COMMON_MODELS,
  type AIModelConfig,
  type AIModelConfigCreate,
  type AIModelConfigUpdate
} from '@/api/ai-configs'

// Props
interface Props {
  visible: boolean
  config?: AIModelConfig | null
  mode: 'create' | 'edit'
}

const props = withDefaults(defineProps<Props>(), {
  visible: false,
  config: null,
  mode: 'create'
})

// Emits
const emit = defineEmits<{
  'update:visible': [value: boolean]
  success: []
}>()

// 响应式数据
const formRef = ref()
const submitting = ref(false)
const testing = ref(false)
const activeCollapse = ref<string[]>([])
const showModelSelector = ref(false)
const activeModelTab = ref('openai')
const selectedModel = ref('')
const selectedPreset = ref('')

// 表单数据
const formData = reactive<AIModelConfigCreate>({
  name: '',
  description: '',
  model_type: 'openai_compatible',
  is_active: true,
  is_default: false,
  api_endpoint: '',
  api_key: '',
  model_name: '',
  request_format: 'openai_chat',
  max_tokens: DEFAULT_CONFIG.max_tokens,
  temperature: DEFAULT_CONFIG.temperature,
  timeout: DEFAULT_CONFIG.timeout,
  retry_count: DEFAULT_CONFIG.retry_count,
  priority: DEFAULT_CONFIG.priority
})

// 请求头数据
const requestHeaders = ref<Array<{key: string, value: string}>>([])

// 表单验证规则
const formRules = {
  name: [
    { required: true, message: '请输入配置名称', trigger: 'blur' },
    { min: 1, max: 200, message: '配置名称长度在 1 到 200 个字符', trigger: 'blur' }
  ],
  model_type: [
    { required: true, message: '请选择模型类型', trigger: 'change' }
  ],
  api_endpoint: [
    { required: true, message: '请输入API端点', trigger: 'blur' },
    { type: 'url', message: '请输入有效的URL', trigger: 'blur' }
  ],
  model_name: [
    { required: true, message: '请输入模型名称', trigger: 'blur' }
  ],
  request_format: [
    { required: true, message: '请选择请求格式', trigger: 'change' }
  ],
  max_tokens: [
    { required: true, message: '请输入最大Token数', trigger: 'blur' },
    { type: 'number', min: 1, max: 100000, message: '最大Token数必须在1-100000之间', trigger: 'blur' }
  ],
  temperature: [
    { required: true, message: '请输入温度参数', trigger: 'blur' }
  ],
  timeout: [
    { required: true, message: '请输入超时时间', trigger: 'blur' },
    { type: 'number', min: 1, max: 300, message: '超时时间必须在1-300秒之间', trigger: 'blur' }
  ],
  retry_count: [
    { required: true, message: '请输入重试次数', trigger: 'blur' },
    { type: 'number', min: 0, max: 10, message: '重试次数必须在0-10之间', trigger: 'blur' }
  ]
}

// 计算属性
const dialogTitle = computed(() => {
  return props.mode === 'create' ? '创建AI配置' : '编辑AI配置'
})

// 监听配置变化
watch(() => props.config, (config) => {
  if (config && props.visible) {
    Object.assign(formData, {
      ...config,
      api_key: '' // 编辑时不显示密钥
    })
    
    // 处理请求头
    if (config.request_headers) {
      requestHeaders.value = Object.entries(config.request_headers).map(([key, value]) => ({
        key,
        value: String(value)
      }))
    } else {
      requestHeaders.value = []
    }
  }
}, { immediate: true })

// 监听对话框显示状态
watch(() => props.visible, (visible) => {
  if (visible) {
    if (props.mode === 'create') {
      resetForm()
    }
    nextTick(() => {
      formRef.value?.clearValidate()
    })
  }
})

// 重置表单
const resetForm = () => {
  Object.assign(formData, {
    name: '',
    description: '',
    model_type: 'openai_compatible',
    is_active: true,
    is_default: false,
    api_endpoint: '',
    api_key: '',
    model_name: '',
    request_format: 'openai_chat',
    max_tokens: DEFAULT_CONFIG.max_tokens,
    temperature: DEFAULT_CONFIG.temperature,
    timeout: DEFAULT_CONFIG.timeout,
    retry_count: DEFAULT_CONFIG.retry_count,
    priority: DEFAULT_CONFIG.priority
  })
  requestHeaders.value = []
}

// 处理模型类型变化
const handleModelTypeChange = (value: string) => {
  // 根据模型类型设置默认请求格式
  const formatMap: Record<string, string> = {
    'openai_compatible': 'openai_chat',
    'claude_compatible': 'claude_messages',
    'custom_http': 'custom_json'
  }
  
  if (formatMap[value]) {
    formData.request_format = formatMap[value]
  }
}

// 处理预设选择
const handlePresetChange = (preset: string) => {
  const endpointMap: Record<string, string> = {
    'openai': PRESET_ENDPOINTS.OPENAI,
    'claude': PRESET_ENDPOINTS.CLAUDE,
    'openrouter': PRESET_ENDPOINTS.OPENROUTER
  }
  
  if (endpointMap[preset]) {
    formData.api_endpoint = endpointMap[preset]
  }
  selectedPreset.value = ''
}

// 添加请求头
const addRequestHeader = () => {
  requestHeaders.value.push({ key: '', value: '' })
}

// 删除请求头
const removeRequestHeader = (index: number) => {
  requestHeaders.value.splice(index, 1)
}

// 处理模型选择
const handleModelSelect = () => {
  if (selectedModel.value) {
    formData.model_name = selectedModel.value
    showModelSelector.value = false
    selectedModel.value = ''
  }
}

// 处理取消
const handleCancel = () => {
  emit('update:visible', false)
}

// 处理测试
const handleTest = async () => {
  try {
    const valid = await formRef.value.validate()
    if (!valid) return
    
    testing.value = true
    
    // 构建测试配置
    const testConfig = {
      ...formData,
      request_headers: requestHeaders.value.reduce((acc, header) => {
        if (header.key && header.value) {
          acc[header.key] = header.value
        }
        return acc
      }, {} as Record<string, string>)
    }
    
    // 这里应该调用测试API，但由于需要先保存配置，我们暂时提示用户
    ElMessage.info('请先保存配置后再进行测试')
    
  } catch (error) {
    console.error('测试连接失败:', error)
  } finally {
    testing.value = false
  }
}

// 处理提交
const handleSubmit = async () => {
  try {
    const valid = await formRef.value.validate()
    if (!valid) return
    
    submitting.value = true
    
    // 构建提交数据
    const submitData: AIModelConfigCreate | AIModelConfigUpdate = {
      ...formData,
      request_headers: requestHeaders.value.reduce((acc, header) => {
        if (header.key && header.value) {
          acc[header.key] = header.value
        }
        return acc
      }, {} as Record<string, string>)
    }
    
    // 如果是编辑模式且密钥为空，则不提交密钥
    if (props.mode === 'edit' && !submitData.api_key) {
      delete submitData.api_key
    }
    
    if (props.mode === 'create') {
      await aiConfigsApi.createConfig(submitData as AIModelConfigCreate)
      ElMessage.success('创建配置成功')
    } else {
      await aiConfigsApi.updateConfig(props.config!.id, submitData as AIModelConfigUpdate)
      ElMessage.success('更新配置成功')
    }
    
    emit('success')
    emit('update:visible', false)
    
  } catch (error) {
    console.error('保存配置失败:', error)
    ElMessage.error('保存配置失败')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.form-section {
  margin-bottom: 20px;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.header-item {
  margin-bottom: 10px;
}

.header-item:last-child {
  margin-bottom: 0;
}

.model-selector {
  max-height: 300px;
  overflow-y: auto;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

:deep(.el-collapse-item__header) {
  font-weight: 600;
}

:deep(.el-card__header) {
  padding: 12px 20px;
  border-bottom: 1px solid #f0f0f0;
}

:deep(.el-card__body) {
  padding: 20px;
}
</style>