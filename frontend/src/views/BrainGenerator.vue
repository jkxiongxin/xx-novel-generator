<template>
  <div class="brain-generator">
    <div class="container">
      <el-card class="generator-card">
        <template #header>
          <div class="card-header">
            <h2>🧠 脑洞生成器</h2>
            <p class="subtitle">释放想象力，让AI帮你打开脑洞！</p>
          </div>
        </template>

        <!-- 输入表单 -->
        <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="主题" prop="topic">
                <el-input
                  v-model="form.topic"
                  placeholder="例如：时间旅行、超能力、外星人..."
                  maxlength="200"
                  show-word-limit
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="要素" prop="elements">
                <el-input
                  v-model="form.elements"
                  placeholder="例如：校园、悬疑、恋爱..."
                  maxlength="300"
                  show-word-limit
                />
              </el-form-item>
            </el-col>
          </el-row>

          <el-form-item label="创意程度" prop="creativity_level">
            <el-slider
              v-model="form.creativity_level"
              :min="0"
              :max="100"
              :step="10"
              show-stops
              show-input
              style="margin-right: 20px;"
            />
            <span class="creativity-hint">
              {{ getCreativityHint(form.creativity_level) }}
            </span>
          </el-form-item>

          <el-form-item label="你的想法" prop="user_input">
            <el-input
              v-model="form.user_input"
              type="textarea"
              :rows="3"
              placeholder="描述一下你的想法或需求..."
              maxlength="1000"
              show-word-limit
            />
          </el-form-item>

          <el-form-item label="高级设置">
            <el-collapse>
              <el-collapse-item title="生成参数" name="1">
                <el-row :gutter="20">
                  <el-col :span="12">
                    <el-form-item label="最大字数">
                      <el-input-number
                        v-model="form.max_tokens"
                        :min="500"
                        :max="8000"
                        :step="500"
                        style="width: 100%"
                      />
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="随机性">
                      <el-slider
                        v-model="form.temperature"
                        :min="0"
                        :max="100"
                        show-input
                      />
                    </el-form-item>
                  </el-col>
                </el-row>
              </el-collapse-item>
            </el-collapse>
          </el-form-item>

          <el-form-item>
            <el-button
              type="primary"
              size="large"
              @click="generateBrainStorm"
              :loading="loading"
              :disabled="!canGenerate"
              style="width: 200px;"
            >
              <el-icon><MagicStick /></el-icon>
              {{ loading ? '生成中...' : '生成脑洞' }}
            </el-button>
            <el-button size="large" @click="resetForm">重置</el-button>
          </el-form-item>
        </el-form>
      </el-card>

      <!-- 生成结果 -->
      <el-card v-if="result" class="result-card">
        <template #header>
          <div class="result-header">
            <h3>🎉 生成结果</h3>
            <div class="result-meta">
              <span>模型: {{ result.model_used }}</span>
              <span>耗时: {{ result.generation_time }}s</span>
            </div>
          </div>
        </template>

        <div v-if="result.data && result.data.brainstorms" class="brainstorm-results">
          <el-row :gutter="20">
            <el-col 
              v-for="(brainstorm, index) in result.data.brainstorms" 
              :key="index"
              :span="8"
            >
              <el-card class="brainstorm-card" :class="`style-${index + 1}`">
                <template #header>
                  <div class="brainstorm-header">
                    <el-tag :type="getStyleType(brainstorm.style)">
                      {{ brainstorm.style }}
                    </el-tag>
                  </div>
                </template>
                
                <div class="brainstorm-content">
                  <div class="section">
                    <h4>💡 核心概念</h4>
                    <p>{{ brainstorm.concept }}</p>
                  </div>
                  
                  <div class="section">
                    <h4>🛠️ 实现方式</h4>
                    <p>{{ brainstorm.implementation }}</p>
                  </div>
                  
                  <div class="section">
                    <h4>🚀 发展方向</h4>
                    <p>{{ brainstorm.development }}</p>
                  </div>
                </div>

                <div class="brainstorm-actions">
                  <el-button size="small" @click="copyToClipboard(brainstorm)">
                    <el-icon><DocumentCopy /></el-icon>
                    复制
                  </el-button>
                  <el-button size="small" type="primary" @click="useAsBasis(brainstorm)">
                    <el-icon><Plus /></el-icon>
                    采用
                  </el-button>
                </div>
              </el-card>
            </el-col>
          </el-row>
        </div>

        <div v-else class="simple-result">
          <pre>{{ JSON.stringify(result.data, null, 2) }}</pre>
        </div>
      </el-card>

      <!-- 错误信息 -->
      <el-alert
        v-if="error"
        type="error"
        :title="error"
        show-icon
        :closable="false"
        style="margin-top: 20px;"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { MagicStick, DocumentCopy, Plus } from '@element-plus/icons-vue'
import { generationApi, type GenerationResponse } from '../api/generation'

// 表单数据
const form = reactive({
  topic: '',
  elements: '',
  creativity_level: 80,
  user_input: '',
  max_tokens: 2000,
  temperature: 90
})

// 表单验证规则
const rules = {
  // 暂时不设置必填验证，让用户可以灵活输入
}

// 响应式数据
const formRef = ref()
const loading = ref(false)
const result = ref<GenerationResponse | null>(null)
const error = ref('')

// 计算属性
const canGenerate = computed(() => {
  return form.topic || form.elements || form.user_input
})

// 获取创意程度提示
const getCreativityHint = (level: number): string => {
  if (level >= 90) return '🚀 极度创新'
  if (level >= 70) return '🌟 高度创意'
  if (level >= 50) return '💡 中等创意'
  if (level >= 30) return '📝 稳重实用'
  return '🏠 贴近现实'
}

// 获取风格标签类型
const getStyleType = (style: string): string => {
  if (style.includes('现实')) return 'success'
  if (style.includes('想象')) return 'primary'
  if (style.includes('颠覆')) return 'danger'
  return 'info'
}

// 生成脑洞
const generateBrainStorm = async () => {
  try {
    loading.value = true
    error.value = ''
    result.value = null

    const response = await generationApi.generateBrainStorm({
      topic: form.topic || undefined,
      elements: form.elements || undefined,
      creativity_level: form.creativity_level,
      user_input: form.user_input || undefined,
      max_tokens: form.max_tokens,
      temperature: form.temperature
    })

    result.value = response
    ElMessage.success('脑洞生成成功！')
  } catch (err: any) {
    error.value = err.response?.data?.detail || err.message || '生成失败'
    ElMessage.error('生成失败，请重试')
  } finally {
    loading.value = false
  }
}

// 重置表单
const resetForm = () => {
  form.topic = ''
  form.elements = ''
  form.creativity_level = 80
  form.user_input = ''
  form.max_tokens = 2000
  form.temperature = 90
  result.value = null
  error.value = ''
}

// 复制到剪贴板
const copyToClipboard = async (brainstorm: any) => {
  try {
    const text = `
风格：${brainstorm.style}
核心概念：${brainstorm.concept}
实现方式：${brainstorm.implementation}
发展方向：${brainstorm.development}
    `.trim()
    
    await navigator.clipboard.writeText(text)
    ElMessage.success('已复制到剪贴板')
  } catch (err) {
    ElMessage.error('复制失败')
  }
}

// 采用为基础
const useAsBasis = async (brainstorm: any) => {
  try {
    await ElMessageBox.confirm(
      '是否将此创意作为基础，跳转到小说创建页面？',
      '确认采用',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'info'
      }
    )
    
    // TODO: 跳转到小说创建页面，并传递创意数据
    ElMessage.info('功能开发中...')
  } catch {
    // 用户取消
  }
}
</script>

<style scoped>
.brain-generator {
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: calc(100vh - 60px);
}

.container {
  max-width: 1200px;
  margin: 0 auto;
}

.generator-card {
  margin-bottom: 20px;
}

.card-header {
  text-align: center;
}

.card-header h2 {
  margin: 0;
  color: #333;
  font-size: 2rem;
}

.subtitle {
  margin: 10px 0 0 0;
  color: #666;
  font-size: 1rem;
}

.creativity-hint {
  color: #409eff;
  font-weight: bold;
  margin-left: 10px;
}

.result-card {
  animation: fadeInUp 0.5s ease-out;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.result-meta {
  display: flex;
  gap: 20px;
  font-size: 0.9rem;
  color: #666;
}

.brainstorm-results {
  margin-top: 20px;
}

.brainstorm-card {
  height: 100%;
  transition: transform 0.3s ease;
}

.brainstorm-card:hover {
  transform: translateY(-5px);
}

.brainstorm-card.style-1 {
  border-left: 4px solid #67c23a;
}

.brainstorm-card.style-2 {
  border-left: 4px solid #409eff;
}

.brainstorm-card.style-3 {
  border-left: 4px solid #f56c6c;
}

.brainstorm-header {
  text-align: center;
}

.brainstorm-content {
  min-height: 300px;
}

.section {
  margin-bottom: 20px;
}

.section h4 {
  margin: 0 0 8px 0;
  font-size: 1rem;
  color: #333;
}

.section p {
  margin: 0;
  line-height: 1.6;
  color: #666;
}

.brainstorm-actions {
  display: flex;
  gap: 10px;
  justify-content: center;
  padding-top: 15px;
  border-top: 1px solid #eee;
}

.simple-result {
  background: #f5f5f5;
  padding: 20px;
  border-radius: 5px;
  font-family: monospace;
  white-space: pre-wrap;
  max-height: 400px;
  overflow-y: auto;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

:deep(.el-collapse-item__header) {
  font-size: 14px;
}
</style>