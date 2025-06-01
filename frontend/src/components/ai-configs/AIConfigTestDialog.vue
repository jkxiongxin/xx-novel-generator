<template>
  <el-dialog
    :model-value="visible"
    @update:model-value="$emit('update:visible', $event)"
    title="测试AI配置"
    width="600px"
  >
    <div v-if="config" class="test-container">
      <!-- 配置信息 -->
      <el-card class="config-info" shadow="never">
        <template #header>
          <div class="section-header">
            <el-icon><Setting /></el-icon>
            <span>测试配置: {{ config.name }}</span>
          </div>
        </template>
        
        <el-descriptions :column="2" size="small">
          <el-descriptions-item label="模型类型">
            <el-tag :type="getModelTypeTagType(config.model_type)" size="small">
              {{ MODEL_TYPE_LABELS[config.model_type as keyof typeof MODEL_TYPE_LABELS] }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="模型名称">
            {{ config.model_name }}
          </el-descriptions-item>
          <el-descriptions-item label="API端点" :span="2">
            <div class="endpoint-text">{{ config.api_endpoint }}</div>
          </el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- 测试参数 -->
      <el-card class="test-params" shadow="never">
        <template #header>
          <div class="section-header">
            <el-icon><Edit /></el-icon>
            <span>测试参数</span>
          </div>
        </template>
        
        <el-form :model="testForm" label-width="100px">
          <el-form-item label="测试提示词" required>
            <el-input
              v-model="testForm.prompt"
              type="textarea"
              :rows="4"
              placeholder="请输入要测试的提示词内容"
              maxlength="1000"
              show-word-limit
            />
          </el-form-item>
          
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="最大Token">
                <el-input-number
                  v-model="testForm.max_tokens"
                  :min="1"
                  :max="1000"
                  controls-position="right"
                  placeholder="使用默认值"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="温度参数">
                <el-input
                  v-model="testForm.temperature"
                  placeholder="使用默认值"
                />
              </el-form-item>
            </el-col>
          </el-row>
        </el-form>
      </el-card>

      <!-- 测试结果 -->
      <el-card v-if="testResult" class="test-result" shadow="never">
        <template #header>
          <div class="section-header">
            <el-icon><DataLine /></el-icon>
            <span>测试结果</span>
            <el-tag 
              :type="testResult.success ? 'success' : 'danger'" 
              size="small"
            >
              {{ testResult.success ? '成功' : '失败' }}
            </el-tag>
          </div>
        </template>
        
        <div class="result-content">
          <!-- 成功结果 -->
          <div v-if="testResult.success" class="success-result">
            <div class="result-stats">
              <el-statistic
                title="响应时间"
                :value="testResult.response_time"
                suffix="秒"
                :precision="3"
              />
              <el-statistic
                v-if="testResult.usage?.total_tokens"
                title="使用Token"
                :value="testResult.usage.total_tokens"
              />
            </div>
            
            <div class="generated-content">
              <h4>生成内容:</h4>
              <div class="content-box">
                {{ testResult.content }}
              </div>
            </div>
            
            <div v-if="testResult.usage" class="usage-details">
              <h4>Token使用详情:</h4>
              <el-descriptions :column="3" size="small" border>
                <el-descriptions-item 
                  v-if="testResult.usage.prompt_tokens"
                  label="提示Token"
                >
                  {{ testResult.usage.prompt_tokens }}
                </el-descriptions-item>
                <el-descriptions-item 
                  v-if="testResult.usage.completion_tokens"
                  label="完成Token"
                >
                  {{ testResult.usage.completion_tokens }}
                </el-descriptions-item>
                <el-descriptions-item 
                  v-if="testResult.usage.total_tokens"
                  label="总Token"
                >
                  {{ testResult.usage.total_tokens }}
                </el-descriptions-item>
              </el-descriptions>
            </div>
          </div>
          
          <!-- 失败结果 -->
          <div v-else class="error-result">
            <div class="error-info">
              <el-alert
                title="测试失败"
                :description="testResult.error"
                type="error"
                show-icon
                :closable="false"
              />
            </div>
            
            <div class="error-stats">
              <el-statistic
                title="响应时间"
                :value="testResult.response_time"
                suffix="秒"
                :precision="3"
              />
            </div>
            
            <div class="troubleshooting">
              <h4>故障排除建议:</h4>
              <ul class="suggestions">
                <li>检查API密钥是否正确</li>
                <li>确认API端点URL是否有效</li>
                <li>验证网络连接是否正常</li>
                <li>检查API服务是否正在运行</li>
                <li>确认模型名称是否存在</li>
              </ul>
            </div>
          </div>
        </div>
      </el-card>

      <!-- 历史测试记录 -->
      <el-card v-if="testHistory.length > 0" class="test-history" shadow="never">
        <template #header>
          <div class="section-header">
            <el-icon><Clock /></el-icon>
            <span>测试历史</span>
            <el-button size="small" @click="clearHistory">
              清除历史
            </el-button>
          </div>
        </template>
        
        <div class="history-list">
          <div 
            v-for="(record, index) in testHistory" 
            :key="index"
            class="history-item"
            :class="{ success: record.success, error: !record.success }"
          >
            <div class="history-header">
              <span class="history-time">{{ formatTime(record.timestamp) }}</span>
              <el-tag 
                :type="record.success ? 'success' : 'danger'" 
                size="small"
              >
                {{ record.success ? '成功' : '失败' }}
              </el-tag>
            </div>
            <div class="history-content">
              <div class="history-prompt">{{ record.prompt }}</div>
              <div class="history-stats">
                响应时间: {{ record.response_time?.toFixed(3) }}秒
                <span v-if="record.usage?.total_tokens">
                  | Token: {{ record.usage.total_tokens }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="$emit('update:visible', false)">关闭</el-button>
        <el-button 
          type="primary" 
          :loading="testing"
          :disabled="!testForm.prompt.trim()"
          @click="handleTest"
        >
          开始测试
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Setting, Edit, DataLine, Clock
} from '@element-plus/icons-vue'

import {
  aiConfigsApi,
  MODEL_TYPE_LABELS,
  type AIModelConfig,
  type AIModelConfigTestResponse
} from '@/api/ai-configs'

// Props
interface Props {
  visible: boolean
  config?: AIModelConfig | null
}

const props = defineProps<Props>()

// Emits
defineEmits<{
  'update:visible': [value: boolean]
}>()

// 测试历史记录接口
interface TestHistoryRecord {
  timestamp: number
  prompt: string
  success: boolean
  response_time: number
  content?: string
  error?: string
  usage?: Record<string, any>
}

// 响应式数据
const testing = ref(false)
const testResult = ref<AIModelConfigTestResponse | null>(null)
const testHistory = ref<TestHistoryRecord[]>([])

// 测试表单
const testForm = reactive({
  prompt: '你好，请介绍一下你自己。',
  max_tokens: undefined as number | undefined,
  temperature: undefined as string | undefined
})

// 监听配置变化，重置表单
watch(() => props.config, (config) => {
  if (config && props.visible) {
    testResult.value = null
    // 可以根据配置类型设置默认测试提示词
    if (config.model_type === 'claude_compatible') {
      testForm.prompt = '请用中文简单介绍一下你自己。'
    } else {
      testForm.prompt = '你好，请介绍一下你自己。'
    }
  }
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

// 格式化时间
const formatTime = (timestamp: number) => {
  return new Date(timestamp).toLocaleTimeString('zh-CN')
}

// 处理测试
const handleTest = async () => {
  if (!props.config || !testForm.prompt.trim()) {
    ElMessage.warning('请输入测试提示词')
    return
  }
  
  try {
    testing.value = true
    
    const testData = {
      prompt: testForm.prompt.trim(),
      max_tokens: testForm.max_tokens,
      temperature: testForm.temperature
    }
    
    const result = await aiConfigsApi.testConfig(props.config.id, testData)
    testResult.value = result
    
    // 添加到历史记录
    const historyRecord: TestHistoryRecord = {
      timestamp: Date.now(),
      prompt: testForm.prompt.trim(),
      success: result.success,
      response_time: result.response_time,
      content: result.content,
      error: result.error,
      usage: result.usage
    }
    
    testHistory.value.unshift(historyRecord)
    
    // 限制历史记录数量
    if (testHistory.value.length > 10) {
      testHistory.value = testHistory.value.slice(0, 10)
    }
    
    if (result.success) {
      ElMessage.success('测试成功')
    } else {
      ElMessage.error('测试失败')
    }
    
  } catch (error) {
    console.error('测试失败:', error)
    ElMessage.error('测试请求失败')
  } finally {
    testing.value = false
  }
}

// 清除历史记录
const clearHistory = () => {
  testHistory.value = []
  ElMessage.success('已清除测试历史')
}
</script>

<style scoped>
.test-container {
  max-height: 70vh;
  overflow-y: auto;
}

.config-info,
.test-params,
.test-result,
.test-history {
  margin-bottom: 16px;
}

.config-info:last-child,
.test-params:last-child,
.test-result:last-child,
.test-history:last-child {
  margin-bottom: 0;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.endpoint-text {
  font-family: monospace;
  color: #606266;
  font-size: 12px;
  word-break: break-all;
}

.result-content {
  margin-top: 16px;
}

.success-result {
  color: #67c23a;
}

.error-result {
  color: #f56c6c;
}

.result-stats {
  display: flex;
  gap: 40px;
  margin-bottom: 20px;
}

.generated-content {
  margin-bottom: 20px;
}

.generated-content h4 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 14px;
}

.content-box {
  background: #f5f7fa;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 12px;
  color: #303133;
  line-height: 1.6;
  white-space: pre-wrap;
  max-height: 200px;
  overflow-y: auto;
}

.usage-details h4 {
  margin: 0 0 12px 0;
  color: #303133;
  font-size: 14px;
}

.error-info {
  margin-bottom: 16px;
}

.error-stats {
  margin-bottom: 20px;
}

.troubleshooting h4 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 14px;
}

.suggestions {
  margin: 0;
  padding-left: 20px;
  color: #606266;
}

.suggestions li {
  margin-bottom: 4px;
  line-height: 1.5;
}

.history-list {
  max-height: 300px;
  overflow-y: auto;
}

.history-item {
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  padding: 12px;
  margin-bottom: 8px;
  background: white;
  transition: all 0.3s ease;
}

.history-item:last-child {
  margin-bottom: 0;
}

.history-item:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.history-item.success {
  border-left: 3px solid #67c23a;
}

.history-item.error {
  border-left: 3px solid #f56c6c;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.history-time {
  font-size: 12px;
  color: #909399;
}

.history-prompt {
  color: #303133;
  font-size: 13px;
  margin-bottom: 4px;
  line-height: 1.4;
}

.history-stats {
  font-size: 12px;
  color: #909399;
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

/* 滚动条样式 */
.test-container::-webkit-scrollbar,
.history-list::-webkit-scrollbar,
.content-box::-webkit-scrollbar {
  width: 6px;
}

.test-container::-webkit-scrollbar-track,
.history-list::-webkit-scrollbar-track,
.content-box::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.test-container::-webkit-scrollbar-thumb,
.history-list::-webkit-scrollbar-thumb,
.content-box::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.test-container::-webkit-scrollbar-thumb:hover,
.history-list::-webkit-scrollbar-thumb:hover,
.content-box::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>