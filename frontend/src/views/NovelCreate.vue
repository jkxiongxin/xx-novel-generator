<template>
  <div class="novel-create">
    <div class="container">
      <el-card class="create-card">
        <template #header>
          <div class="card-header">
            <h2>📚 小说创作助手</h2>
            <p class="subtitle">让AI帮助你从创意到成书</p>
          </div>
        </template>

        <el-tabs v-model="activeTab" type="border-card">
          <!-- 小说名生成 -->
          <el-tab-pane label="🏷️ 小说名生成" name="name">
            <el-form :model="nameForm" label-width="120px">
              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="小说类型">
                    <el-select v-model="nameForm.genre" placeholder="选择类型" style="width: 100%">
                      <el-option label="玄幻" value="玄幻" />
                      <el-option label="都市" value="都市" />
                      <el-option label="历史" value="历史" />
                      <el-option label="科幻" value="科幻" />
                      <el-option label="武侠" value="武侠" />
                      <el-option label="言情" value="言情" />
                      <el-option label="悬疑" value="悬疑" />
                      <el-option label="其他" value="其他" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="风格偏好">
                    <el-select v-model="nameForm.style" placeholder="选择风格" style="width: 100%">
                      <el-option label="霸气" value="霸气" />
                      <el-option label="优雅" value="优雅" />
                      <el-option label="神秘" value="神秘" />
                      <el-option label="温馨" value="温馨" />
                      <el-option label="搞笑" value="搞笑" />
                      <el-option label="简洁" value="简洁" />
                    </el-select>
                  </el-form-item>
                </el-col>
              </el-row>

              <el-form-item label="关键词">
                <el-input
                  v-model="nameForm.keywords"
                  placeholder="例如：修仙、爱情、复仇..."
                  maxlength="200"
                  show-word-limit
                />
              </el-form-item>

              <el-form-item label="具体需求">
                <el-input
                  v-model="nameForm.user_input"
                  type="textarea"
                  :rows="3"
                  placeholder="描述你想要的小说名风格或要求..."
                  maxlength="1000"
                  show-word-limit
                />
              </el-form-item>

              <el-form-item>
                <el-button 
                  type="primary" 
                  @click="generateNovelName"
                  :loading="nameLoading"
                >
                  生成小说名
                </el-button>
                <el-button @click="resetNameForm">重置</el-button>
              </el-form-item>
            </el-form>

            <!-- 小说名结果 -->
            <div v-if="nameResult" class="result-section">
              <h3>生成的小说名：</h3>
              <div v-if="nameResult.data && nameResult.data.titles" class="title-list">
                <el-card
                  v-for="(titleItem, index) in nameResult.data.titles"
                  :key="index"
                  class="title-card"
                  :class="{ selected: selectedTitle === titleItem.title }"
                  @click="selectTitle(titleItem.title)"
                >
                  <div class="title-content">
                    <h4>{{ titleItem.title }}</h4>
                    <p class="reason">{{ titleItem.reason }}</p>
                  </div>
                  <div class="title-actions">
                    <el-button 
                      size="small" 
                      :type="selectedTitle === titleItem.title ? 'primary' : 'default'"
                    >
                      {{ selectedTitle === titleItem.title ? '已选择' : '选择' }}
                    </el-button>
                  </div>
                </el-card>
              </div>
            </div>
          </el-tab-pane>

          <!-- 小说创意生成 -->
          <el-tab-pane label="💡 创意生成" name="idea">
            <el-form :model="ideaForm" label-width="120px">
              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="小说类型">
                    <el-select v-model="ideaForm.genre" placeholder="选择类型" style="width: 100%">
                      <el-option label="玄幻" value="玄幻" />
                      <el-option label="都市" value="都市" />
                      <el-option label="历史" value="历史" />
                      <el-option label="科幻" value="科幻" />
                      <el-option label="武侠" value="武侠" />
                      <el-option label="言情" value="言情" />
                      <el-option label="悬疑" value="悬疑" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="篇幅长度">
                    <el-select v-model="ideaForm.length" placeholder="选择篇幅" style="width: 100%">
                      <el-option label="短篇（5万字以下）" value="短篇" />
                      <el-option label="中篇（5-20万字）" value="中篇" />
                      <el-option label="长篇（20万字以上）" value="长篇" />
                    </el-select>
                  </el-form-item>
                </el-col>
              </el-row>

              <el-form-item label="主题">
                <el-input
                  v-model="ideaForm.themes"
                  placeholder="例如：成长、友情、正义、复仇..."
                  maxlength="200"
                  show-word-limit
                />
              </el-form-item>

              <el-form-item label="创意要求">
                <el-input
                  v-model="ideaForm.user_input"
                  type="textarea"
                  :rows="3"
                  placeholder="描述你想要的故事背景、角色设定或情节要求..."
                  maxlength="1000"
                  show-word-limit
                />
              </el-form-item>

              <el-form-item>
                <el-button 
                  type="primary" 
                  @click="generateNovelIdea"
                  :loading="ideaLoading"
                >
                  生成创意
                </el-button>
                <el-button @click="resetIdeaForm">重置</el-button>
              </el-form-item>
            </el-form>

            <!-- 创意结果 -->
            <div v-if="ideaResult" class="result-section">
              <h3>生成的小说创意：</h3>
              <div v-if="ideaResult.data && ideaResult.data.idea" class="idea-content">
                <el-card class="idea-card">
                  <el-descriptions :column="1" border>
                    <el-descriptions-item label="建议标题">
                      {{ ideaResult.data.idea.title }}
                    </el-descriptions-item>
                    <el-descriptions-item label="世界设定">
                      {{ ideaResult.data.idea.setting }}
                    </el-descriptions-item>
                    <el-descriptions-item label="主角设定">
                      {{ ideaResult.data.idea.main_character }}
                    </el-descriptions-item>
                    <el-descriptions-item label="核心冲突">
                      {{ ideaResult.data.idea.conflict }}
                    </el-descriptions-item>
                    <el-descriptions-item label="故事主线">
                      {{ ideaResult.data.idea.plot }}
                    </el-descriptions-item>
                    <el-descriptions-item label="独特卖点">
                      {{ ideaResult.data.idea.unique_selling_point }}
                    </el-descriptions-item>
                    <el-descriptions-item label="目标读者">
                      {{ ideaResult.data.idea.target_audience }}
                    </el-descriptions-item>
                  </el-descriptions>
                  
                  <div class="idea-actions">
                    <el-button type="primary" @click="adoptIdea">
                      <el-icon><Check /></el-icon>
                      采用此创意
                    </el-button>
                    <el-button @click="copyIdea">
                      <el-icon><DocumentCopy /></el-icon>
                      复制创意
                    </el-button>
                  </div>
                </el-card>
              </div>
            </div>
          </el-tab-pane>

          <!-- 综合创作 -->
          <el-tab-pane label="🎯 综合创作" name="compose">
            <div class="compose-section">
              <el-alert
                title="即将开放"
                description="综合创作功能将整合小说名、创意、大纲等所有生成功能，敬请期待！"
                type="info"
                show-icon
                :closable="false"
              />
              
              <!-- 已选择的内容展示 -->
              <div v-if="selectedTitle || adoptedIdea" class="selected-content">
                <h3>已选择的内容：</h3>
                
                <el-card v-if="selectedTitle" class="selected-item">
                  <template #header>
                    <span>📖 小说标题</span>
                  </template>
                  <p>{{ selectedTitle }}</p>
                </el-card>

                <el-card v-if="adoptedIdea" class="selected-item">
                  <template #header>
                    <span>💡 小说创意</span>
                  </template>
                  <el-descriptions :column="1" size="small">
                    <el-descriptions-item label="标题">{{ adoptedIdea.title }}</el-descriptions-item>
                    <el-descriptions-item label="设定">{{ adoptedIdea.setting }}</el-descriptions-item>
                    <el-descriptions-item label="主角">{{ adoptedIdea.main_character }}</el-descriptions-item>
                  </el-descriptions>
                </el-card>
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
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
import { ref, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Check, DocumentCopy } from '@element-plus/icons-vue'
import { generationApi, type GenerationResponse } from '../api/generation'

// 活动标签
const activeTab = ref('name')

// 小说名生成表单
const nameForm = reactive({
  genre: '',
  keywords: '',
  style: '',
  user_input: ''
})

// 创意生成表单
const ideaForm = reactive({
  genre: '',
  themes: '',
  length: '',
  user_input: ''
})

// 响应式数据
const nameLoading = ref(false)
const ideaLoading = ref(false)
const nameResult = ref<GenerationResponse | null>(null)
const ideaResult = ref<GenerationResponse | null>(null)
const error = ref('')

// 选择的内容
const selectedTitle = ref('')
const adoptedIdea = ref<any>(null)

// 生成小说名
const generateNovelName = async () => {
  try {
    nameLoading.value = true
    error.value = ''

    const response = await generationApi.generateNovelName({
      genre: nameForm.genre || undefined,
      keywords: nameForm.keywords || undefined,
      style: nameForm.style || undefined,
      user_input: nameForm.user_input || undefined
    })

    nameResult.value = response
    ElMessage.success('小说名生成成功！')
  } catch (err: any) {
    error.value = err.response?.data?.detail || err.message || '生成失败'
    ElMessage.error('生成失败，请重试')
  } finally {
    nameLoading.value = false
  }
}

// 生成小说创意
const generateNovelIdea = async () => {
  try {
    ideaLoading.value = true
    error.value = ''

    const response = await generationApi.generateNovelIdea({
      genre: ideaForm.genre || undefined,
      themes: ideaForm.themes || undefined,
      length: ideaForm.length || undefined,
      user_input: ideaForm.user_input || undefined
    })

    ideaResult.value = response
    ElMessage.success('小说创意生成成功！')
  } catch (err: any) {
    error.value = err.response?.data?.detail || err.message || '生成失败'
    ElMessage.error('生成失败，请重试')
  } finally {
    ideaLoading.value = false
  }
}

// 选择标题
const selectTitle = (title: string) => {
  selectedTitle.value = title
  ElMessage.success(`已选择标题：${title}`)
}

// 采用创意
const adoptIdea = () => {
  if (ideaResult.value?.data?.idea) {
    adoptedIdea.value = ideaResult.value.data.idea
    ElMessage.success('已采用此创意')
    // 跳转到综合创作标签
    activeTab.value = 'compose'
  }
}

// 复制创意
const copyIdea = async () => {
  if (ideaResult.value?.data?.idea) {
    try {
      const idea = ideaResult.value.data.idea
      const text = `
标题：${idea.title}
世界设定：${idea.setting}
主角设定：${idea.main_character}
核心冲突：${idea.conflict}
故事主线：${idea.plot}
独特卖点：${idea.unique_selling_point}
目标读者：${idea.target_audience}
      `.trim()
      
      await navigator.clipboard.writeText(text)
      ElMessage.success('创意已复制到剪贴板')
    } catch (err) {
      ElMessage.error('复制失败')
    }
  }
}

// 重置表单
const resetNameForm = () => {
  nameForm.genre = ''
  nameForm.keywords = ''
  nameForm.style = ''
  nameForm.user_input = ''
  nameResult.value = null
  error.value = ''
}

const resetIdeaForm = () => {
  ideaForm.genre = ''
  ideaForm.themes = ''
  ideaForm.length = ''
  ideaForm.user_input = ''
  ideaResult.value = null
  error.value = ''
}
</script>

<style scoped>
.novel-create {
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: calc(100vh - 60px);
}

.container {
  max-width: 1200px;
  margin: 0 auto;
}

.create-card {
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

.result-section {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.title-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 15px;
  margin-top: 15px;
}

.title-card {
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.title-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 12px rgba(0,0,0,0.1);
}

.title-card.selected {
  border-color: #409eff;
  background: #f0f9ff;
}

.title-content h4 {
  margin: 0 0 10px 0;
  color: #333;
  font-size: 1.2rem;
}

.reason {
  margin: 0;
  color: #666;
  font-size: 0.9rem;
  line-height: 1.5;
}

.title-actions {
  margin-top: 15px;
  text-align: center;
}

.idea-content {
  margin-top: 15px;
}

.idea-card {
  max-width: 800px;
}

.idea-actions {
  margin-top: 20px;
  display: flex;
  gap: 10px;
  justify-content: center;
}

.compose-section {
  padding: 20px 0;
}

.selected-content {
  margin-top: 30px;
}

.selected-item {
  margin-bottom: 15px;
}

:deep(.el-tabs__content) {
  padding: 20px;
}

:deep(.el-descriptions__label) {
  font-weight: bold;
  width: 120px;
}
</style>