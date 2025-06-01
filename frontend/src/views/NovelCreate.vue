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
              <!-- 已选择的内容展示 (Simplified) -->
              <div v-if="selectedTitle || adoptedIdea" class="selected-content-summary">
                <h4>已选参考信息:</h4>
                <p v-if="selectedTitle"><strong>选定标题:</strong> {{ selectedTitle }}</p>
                <p v-if="adoptedIdea && adoptedIdea.title"><strong>创意标题:</strong> {{ adoptedIdea.title }}</p>
                <p v-if="adoptedIdea && adoptedIdea.genre"><strong>创意类型:</strong> {{ adoptedIdea.genre }}</p>
                 <p v-if="adoptedIdea && adoptedIdea.target_audience"><strong>创意受众:</strong> {{ adoptedIdea.target_audience }}</p>
              </div>

              <el-form
                ref="creationFormRef"
                :model="creationForm"
                :rules="creationFormRules"
                label-width="120px"
                label-position="right"
                style="margin-top: 20px;"
              >
                <el-form-item label="小说名称" prop="name">
                  <el-input v-model="creationForm.name" placeholder="请输入小说名称" />
                </el-form-item>

                <el-form-item label="小说类型" prop="type">
                  <el-select v-model="creationForm.type" placeholder="请选择小说类型" style="width: 100%;">
                    <el-option v-for="item in novelTypeOptions" :key="item" :label="item" :value="item" />
                  </el-select>
                </el-form-item>

                <el-form-item label="小说创意概述" prop="idea_summary">
                  <el-input
                    v-model="creationForm.idea_summary"
                    type="textarea"
                    :rows="4"
                    placeholder="简要描述小说的核心创意、故事梗概等"
                  />
                </el-form-item>

                <el-row :gutter="20">
                  <el-col :xs="24" :sm="12">
                    <el-form-item label="字数目标" prop="word_target">
                      <el-select v-model="creationForm.word_target" placeholder="请选择字数目标" style="width: 100%;">
                        <el-option v-for="item in wordTargetOptions" :key="item" :label="item" :value="item" />
                      </el-select>
                    </el-form-item>
                  </el-col>
                  <el-col :xs="24" :sm="12">
                    <el-form-item label="面向读者" prop="audience">
                      <el-select v-model="creationForm.audience" placeholder="请选择面向读者" style="width: 100%;">
                        <el-option v-for="item in audienceOptions" :key="item" :label="item" :value="item" />
                      </el-select>
                    </el-form-item>
                  </el-col>
                </el-row>

                <el-form-item label="世界观数量" prop="worldview_quantity">
                  <el-select v-model="creationForm.worldview_quantity" placeholder="请选择世界观数量" style="width: 100%;">
                     <el-option v-for="item in worldviewQuantityOptions" :key="item" :label="item" :value="item" />
                  </el-select>
                </el-form-item>

                <el-form-item>
                  <el-button
                    type="primary"
                    @click="handleCreateNovel"
                    :loading="creationLoading"
                    size="large"
                  >
                    <el-icon style="margin-right: 5px;"><MagicStick /></el-icon>
                    创建小说
                  </el-button>
                </el-form-item>
              </el-form>
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

// --- Forms & Data ---

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

// 综合创作表单
const creationFormRef = ref<FormInstance>()
const creationForm = reactive({
  name: '',
  type: '', // 玄幻, 奇幻, 历史, 轻小说, 都市, 科幻, 武侠, 言情, 悬疑, 其他
  idea_summary: '',
  word_target: '', // 1w字, 10w字, 100w字, 300w字, 500w字, 1000w字
  audience: '', // 男频, 女频
  worldview_quantity: '单世界' // 单世界, 多世界
})

const creationFormRules = reactive<FormRules>({
  name: [{ required: true, message: '请输入小说名称', trigger: 'blur' }],
  type: [{ required: true, message: '请选择小说类型', trigger: 'change' }],
  idea_summary: [{ required: true, message: '请输入小说创意概述', trigger: 'blur' }],
  word_target: [{ required: true, message: '请选择字数目标', trigger: 'change' }],
  audience: [{ required: true, message: '请选择面向读者', trigger: 'change' }],
  worldview_quantity: [{ required: true, message: '请选择世界观数量', trigger: 'change' }],
})

const novelTypeOptions = ["玄幻", "奇幻", "历史", "轻小说", "都市", "科幻", "武侠", "言情", "悬疑", "其他"];
const wordTargetOptions = ["1w字", "10w字", "100w字", "300w字", "500w字", "1000w字"];
const audienceOptions = ["男频", "女频"];
const worldviewQuantityOptions = ["单世界", "多世界"];


// --- Loading, Results, Errors ---
const nameLoading = ref(false)
const ideaLoading = ref(false)
const creationLoading = ref(false) // For the create novel button
const nameResult = ref<GenerationResponse | null>(null)
const ideaResult = ref<GenerationResponse | null>(null)
const error = ref('')

// --- Selected/Adopted Data from other tabs ---
const selectedTitle = ref('') // From name generation
const adoptedIdea = ref<any>(null) // From idea generation, structure defined by API response

// --- Functions ---

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
    adoptedIdea.value = ideaResult.value.data.idea // Assuming ideaResult.data.idea is the object
    ElMessage.success('已采用此创意')

    // Pre-fill logic for creationForm, only if not already set by user or tab is compose
    if (activeTab.value === 'compose' || !creationForm.name) {
       if (adoptedIdea.value.title && !creationForm.name) {
        creationForm.name = adoptedIdea.value.title;
      }
    }
    if (activeTab.value === 'compose' || !creationForm.type) {
      if (adoptedIdea.value.genre && novelTypeOptions.includes(adoptedIdea.value.genre) && !creationForm.type) {
        creationForm.type = adoptedIdea.value.genre;
      }
    }
     if (activeTab.value === 'compose' || !creationForm.idea_summary) {
      let summary = '';
      if (adoptedIdea.value.title) summary += `标题：${adoptedIdea.value.title}\n`;
      if (adoptedIdea.value.plot) summary += `主线：${adoptedIdea.value.plot}\n`;
      else if (adoptedIdea.value.setting) summary += `设定：${adoptedIdea.value.setting}\n`;
      if (summary && !creationForm.idea_summary) {
        creationForm.idea_summary = summary.trim();
      }
    }
    if (activeTab.value === 'compose' || !creationForm.audience) {
       if (adoptedIdea.value.target_audience && audienceOptions.includes(adoptedIdea.value.target_audience) && !creationForm.audience) {
        creationForm.audience = adoptedIdea.value.target_audience;
      }
    }

    // 跳转到综合创作标签
    activeTab.value = 'compose'
  }
}


// Watchers for pre-filling creationForm, ensuring user edits are not overwritten.
watch(selectedTitle, (newTitle) => {
  if (newTitle && (!creationForm.name || activeTab.value !== 'compose')) {
    // Only pre-fill if creationForm.name is empty or if we are not on the compose tab (to avoid overwriting active edits)
    // This logic might need refinement based on exact desired UX when switching tabs.
    // A simpler approach: only pre-fill if creationForm.name is empty.
    if(!creationForm.name) {
        creationForm.name = newTitle;
    }
  }
});

watch(nameForm, (newNameFormValues) => {
    if (newNameFormValues.genre && novelTypeOptions.includes(newNameFormValues.genre) && !creationForm.type && !adoptedIdea.value?.genre) {
        creationForm.type = newNameFormValues.genre;
    }
}, { deep: true });


watch(activeTab, (newTab) => {
  if (newTab === 'compose') {
    // When switching to compose tab, re-evaluate pre-fills if fields are empty
    if (selectedTitle.value && !creationForm.name) {
      creationForm.name = selectedTitle.value;
    }
    if (adoptedIdea.value) {
      if (adoptedIdea.value.title && !creationForm.name) {
         creationForm.name = adoptedIdea.value.title; // Adopted idea title can also fill name
      }
      if (adoptedIdea.value.genre && novelTypeOptions.includes(adoptedIdea.value.genre) && !creationForm.type) {
        creationForm.type = adoptedIdea.value.genre;
      } else if (nameForm.genre && novelTypeOptions.includes(nameForm.genre) && !creationForm.type) {
        // Fallback to nameForm.genre if adoptedIdea.genre is not available/suitable
        creationForm.type = nameForm.genre;
      }

      if (!creationForm.idea_summary) {
        let summary = '';
        if (adoptedIdea.value.title) summary += `创意标题：${adoptedIdea.value.title}\n`;
        if (adoptedIdea.value.plot) summary += `故事情节：${adoptedIdea.value.plot}\n`;
        else if (adoptedIdea.value.setting) summary += `世界设定：${adoptedIdea.value.setting}\n`;
        if (adoptedIdea.value.main_character) summary += `主要角色：${adoptedIdea.value.main_character}\n`;
        if (adoptedIdea.value.conflict) summary += `核心冲突：${adoptedIdea.value.conflict}\n`;
        creationForm.idea_summary = summary.trim();
      }
      if (adoptedIdea.value.target_audience && audienceOptions.includes(adoptedIdea.value.target_audience) && !creationForm.audience) {
        creationForm.audience = adoptedIdea.value.target_audience;
      }
    } else if (nameForm.genre && novelTypeOptions.includes(nameForm.genre) && !creationForm.type) {
        // If no adopted idea, still try to fill type from nameForm
        creationForm.type = nameForm.genre;
    }
  }
});


// 复制创意
const copyIdea = async () => {
  if (ideaResult.value?.data?.idea) {
    try {
      const idea = ideaResult.value.data.idea
      const ideaToCopy = ideaResult.value.data.idea
      let textToCopy = `标题：${ideaToCopy.title}\n`;
      if(ideaToCopy.genre) textToCopy += `类型：${ideaToCopy.genre}\n`;
      if(ideaToCopy.setting) textToCopy += `世界设定：${ideaToCopy.setting}\n`;
      if(ideaToCopy.main_character) textToCopy += `主角设定：${ideaToCopy.main_character}\n`;
      if(ideaToCopy.conflict) textToCopy += `核心冲突：${ideaToCopy.conflict}\n`;
      if(ideaToCopy.plot) textToCopy += `故事情节：${ideaToCopy.plot}\n`;
      if(ideaToCopy.unique_selling_point) textToCopy += `独特卖点：${ideaToCopy.unique_selling_point}\n`;
      if(ideaToCopy.target_audience) textToCopy += `目标读者：${ideaToCopy.target_audience}\n`;
      
      await navigator.clipboard.writeText(textToCopy.trim())
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
  adoptedIdea.value = null // Also reset adopted idea
  error.value = ''
}

// 处理小说创建
const handleCreateNovel = async () => {
  if (!creationFormRef.value) return
  await creationFormRef.value.validate(async (valid) => {
    if (valid) {
      creationLoading.value = true
      try {
        // Simulate API call
        console.log('Form Data:', JSON.parse(JSON.stringify(creationForm))) // Use stringify/parse for clean log of reactive object
        await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate network delay
        ElMessage.success('小说创建成功（模拟）！')
        // Here you would typically call an API:
        // await novelApi.createNovel(creationForm);
        // And then maybe redirect or clear form:
        // router.push({ name: 'MyNovels' });
        // creationFormRef.value?.resetFields(); // if you want to reset
      } catch (err: any) {
        ElMessage.error(err.message || '小说创建失败，请重试。')
      } finally {
        creationLoading.value = false
      }
    } else {
      ElMessage.error('请检查表单填写是否正确。')
      return false
    }
  })
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
  padding: 10px 0; /* Adjusted padding */
}

.selected-content-summary {
  background-color: #f5f7fa;
  padding: 15px;
  border-radius: 6px;
  margin-bottom: 25px;
  border: 1px solid #e4e7ed;
}
.selected-content-summary h4 {
  margin-top: 0;
  margin-bottom: 10px;
  color: #303133;
}
.selected-content-summary p {
  margin: 5px 0;
  font-size: 0.9em;
  color: #606266;
}

:deep(.el-tabs__content) {
  padding: 20px;
}

:deep(.el-descriptions__label) {
  font-weight: bold;
  width: 120px;
}
</style>