<template>
  <div class="novel-create">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="container">
        <el-steps :active="currentStep" finish-status="success" align-center>
          <el-step title="基本信息" description="设置小说名称和类型" />
          <el-step title="创意设定" description="描述故事创意" />
          <el-step title="目标设置" description="配置创作目标" />
          <el-step title="完成创建" description="确认并创建小说" />
        </el-steps>
      </div>
    </div>

    <!-- 创建表单区域 -->
    <div class="create-form-container">
      <div class="container">
        <el-card class="form-card">
          <!-- 标题输入区域 -->
          <div v-if="currentStep === 0" class="form-section">
            <div class="section-title">
              <el-icon><EditPen /></el-icon>
              <span>小说名称</span>
            </div>
            <div class="section-description">
              为您的小说起一个吸引人的名字，或者让AI帮您生成
            </div>
            
            <div class="input-with-ai">
              <el-input
                v-model="novelForm.title"
                class="input-field"
                placeholder="请输入小说名称"
                maxlength="100"
                show-word-limit
                @input="clearFieldError('title')"
                :class="{ 'is-error': formErrors.title }"
              />
              <el-button 
                type="success" 
                class="ai-generate-btn"
                :loading="isGeneratingTitle"
                @click="generateNovelTitle"
              >
                <el-icon><MagicStick /></el-icon>
                AI生成
              </el-button>
            </div>
            <div v-if="formErrors.title" class="error-message">{{ formErrors.title }}</div>

            <!-- 类型选择 -->
            <div class="genre-selector">
              <h4>选择小说类型</h4>
              <div class="genre-grid">
                <div
                  v-for="genre in genreOptions"
                  :key="genre.value"
                  class="genre-option"
                  :class="{ selected: selectedGenre === genre.value }"
                  @click="selectGenre(genre.value as NovelGenre)"
                >
                  <div class="icon">{{ genre.icon }}</div>
                  <div class="label">{{ genre.label }}</div>
                </div>
              </div>
              <div v-if="formErrors.genre" class="error-message">{{ formErrors.genre }}</div>
            </div>
          </div>

          <!-- 创意描述区域 -->
          <div v-if="currentStep === 1" class="form-section">
            <div class="section-title">
              <el-icon><Sunny /></el-icon>
              <span>小说创意</span>
            </div>
            <div class="section-description">
              描述您的故事创意，包括背景设定、主要角色和核心冲突
            </div>

            <div class="input-with-ai">
              <el-input
                v-model="novelForm.description"
                type="textarea"
                class="input-field"
                :rows="8"
                placeholder="请描述您的小说创意..."
                maxlength="1000"
                show-word-limit
                @input="clearFieldError('description')"
              />
              <el-button 
                type="success" 
                class="ai-generate-btn"
                :loading="isGeneratingIdea"
                @click="generateNovelIdea"
                :disabled="!selectedGenre"
              >
                <el-icon><MagicStick /></el-icon>
                AI生成
              </el-button>
            </div>
            <div v-if="!selectedGenre" class="tip-message">
              请先选择小说类型再使用AI生成创意
            </div>
          </div>

          <!-- 目标设置区域 -->
          <div v-if="currentStep === 2" class="form-section">
            <div class="section-title">
              <el-icon><Setting /></el-icon>
              <span>创作目标</span>
            </div>
            <div class="section-description">
              设置您的创作目标和偏好，帮助系统为您提供更好的建议
            </div>

            <div class="target-settings">
              <!-- 字数目标 -->
              <div class="setting-group">
                <div class="setting-label">目标字数</div>
                <div class="setting-control">
                  <div class="word-count-options">
                    <div
                      v-for="option in wordCountOptions"
                      :key="option.value"
                      class="word-count-btn"
                      :class="{ selected: selectedWordCount === option.value }"
                      @click="selectWordCount(option.value)"
                    >
                      {{ option.label }}
                    </div>
                  </div>
                  <el-input-number
                    v-if="selectedWordCount === 'custom'"
                    v-model="customWordCount"
                    :min="1000"
                    :max="10000000"
                    :step="1000"
                    placeholder="自定义字数"
                    style="margin-top: 12px; width: 200px;"
                  />
                </div>
              </div>

              <!-- 读者群体 -->
              <div class="setting-group">
                <div class="setting-label">读者群体</div>
                <div class="setting-control">
                  <el-radio-group v-model="selectedAudience">
                    <el-radio value="male">男性向</el-radio>
                    <el-radio value="female">女性向</el-radio>
                    <el-radio value="general">通用</el-radio>
                  </el-radio-group>
                </div>
              </div>

              <!-- 世界观复杂度 -->
              <div class="setting-group">
                <div class="setting-label">世界观设定</div>
                <div class="setting-control">
                  <el-radio-group v-model="worldviewCount">
                    <el-radio value="single">简单世界观</el-radio>
                    <el-radio value="multiple">复杂世界观</el-radio>
                  </el-radio-group>
                </div>
              </div>

              <!-- 写作风格 -->
              <div class="setting-group">
                <div class="setting-label">写作风格</div>
                <div class="setting-control">
                  <el-select v-model="writingStyle" placeholder="选择写作风格" style="width: 200px;">
                    <el-option label="轻松幽默" value="humorous" />
                    <el-option label="严肃正剧" value="serious" />
                    <el-option label="悬疑紧张" value="suspense" />
                    <el-option label="温馨治愈" value="healing" />
                    <el-option label="热血激昂" value="passionate" />
                    <el-option label="深度思考" value="philosophical" />
                  </el-select>
                </div>
              </div>

              <!-- 标签选择 -->
              <div class="setting-group">
                <div class="setting-label">小说标签</div>
                <div class="setting-control">
                  <el-select
                    v-model="selectedTags"
                    multiple
                    filterable
                    allow-create
                    placeholder="选择或输入标签"
                    style="width: 100%;"
                  >
                    <el-option
                      v-for="tag in recommendedTags"
                      :key="tag"
                      :label="tag"
                      :value="tag"
                    />
                  </el-select>
                </div>
              </div>
            </div>
          </div>

          <!-- 确认创建区域 -->
          <div v-if="currentStep === 3" class="form-section">
            <div class="section-title">
              <el-icon><Check /></el-icon>
              <span>确认创建</span>
            </div>
            <div class="section-description">
              请确认您的小说信息，创建后可以在工作台中继续完善
            </div>

            <div class="summary-card">
              <el-descriptions :column="1" border>
                <el-descriptions-item label="小说名称">
                  {{ novelForm.title || '未设置' }}
                </el-descriptions-item>
                <el-descriptions-item label="小说类型">
                  {{ getGenreLabel(selectedGenre) }}
                </el-descriptions-item>
                <el-descriptions-item label="故事创意">
                  <div class="description-text">
                    {{ novelForm.description || '未设置' }}
                  </div>
                </el-descriptions-item>
                <el-descriptions-item label="目标字数">
                  {{ getWordCountLabel() }}
                </el-descriptions-item>
                <el-descriptions-item label="读者群体">
                  {{ getAudienceLabel() }}
                </el-descriptions-item>
                <el-descriptions-item label="世界观设定">
                  {{ worldviewCount === 'single' ? '简单世界观' : '复杂世界观' }}
                </el-descriptions-item>
                <el-descriptions-item label="写作风格">
                  {{ getWritingStyleLabel() }}
                </el-descriptions-item>
                <el-descriptions-item label="小说标签" v-if="selectedTags.length > 0">
                  <el-tag v-for="tag in selectedTags" :key="tag" style="margin-right: 8px;">
                    {{ tag }}
                  </el-tag>
                </el-descriptions-item>
              </el-descriptions>
            </div>
          </div>

          <!-- 导航按钮 -->
          <div class="form-actions">
            <el-button 
              v-if="currentStep > 0" 
              @click="prevStep"
              :disabled="isCreating"
            >
              上一步
            </el-button>
            <el-button 
              v-if="currentStep < 3" 
              type="primary" 
              @click="nextStep"
              :disabled="!canProceed"
            >
              下一步
            </el-button>
            <el-button 
              v-if="currentStep === 3" 
              type="primary" 
              @click="createNovel"
              :loading="isCreating"
            >
              创建小说
            </el-button>
            <el-button @click="saveDraft" :loading="isDrafting">
              保存草稿
            </el-button>
            <el-button @click="cancelCreate">
              取消
            </el-button>
          </div>
        </el-card>
      </div>
    </div>

    <!-- AI生成选项对话框 -->
    <el-dialog
      v-model="showTitleOptions"
      title="选择生成的标题"
      width="600px"
      :close-on-click-modal="false"
    >
      <div class="generated-options">
        <div
          v-for="(option, index) in generatedTitles"
          :key="index"
          class="option-card"
          :class="{ selected: selectedTitleOption === option.title }"
          @click="selectTitleOption(option.title)"
        >
          <h4>{{ option.title }}</h4>
          <p class="reason">{{ option.reason }}</p>
        </div>
      </div>
      
      <template #footer>
        <el-button @click="showTitleOptions = false">取消</el-button>
        <el-button @click="regenerateTitles" :loading="isGeneratingTitle">重新生成</el-button>
        <el-button 
          type="primary" 
          @click="applySelectedTitle"
          :disabled="!selectedTitleOption"
        >
          使用选中标题
        </el-button>
      </template>
    </el-dialog>

    <!-- AI生成创意对话框 -->
    <el-dialog
      v-model="showIdeaOptions"
      title="生成的创意"
      width="800px"
      :close-on-click-modal="false"
    >
      <div v-if="generatedIdea" class="idea-content">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="建议标题">
            {{ generatedIdea.title }}
          </el-descriptions-item>
          <el-descriptions-item label="世界设定">
            {{ generatedIdea.setting }}
          </el-descriptions-item>
          <el-descriptions-item label="主角设定">
            {{ generatedIdea.main_character }}
          </el-descriptions-item>
          <el-descriptions-item label="核心冲突">
            {{ generatedIdea.conflict }}
          </el-descriptions-item>
          <el-descriptions-item label="故事主线">
            {{ generatedIdea.plot }}
          </el-descriptions-item>
          <el-descriptions-item label="独特卖点">
            {{ generatedIdea.unique_selling_point }}
          </el-descriptions-item>
          <el-descriptions-item label="目标读者">
            {{ generatedIdea.target_audience }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
      
      <template #footer>
        <el-button @click="showIdeaOptions = false">取消</el-button>
        <el-button @click="regenerateIdea" :loading="isGeneratingIdea">重新生成</el-button>
        <el-button type="primary" @click="applyGeneratedIdea">
          使用此创意
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { useRouter, onBeforeRouteLeave } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  EditPen, 
  MagicStick, 
  Sunny, 
  Setting, 
  Check 
} from '@element-plus/icons-vue'
import { NovelService, type NovelGenre } from '@/api/novels'
import { generationApi } from '@/api/generation'

const router = useRouter()

// ==================== 步骤控制 ====================
const currentStep = ref(0)

// ==================== 表单数据 ====================
const novelForm = reactive({
  title: '',
  description: '',
  tags: [] as string[]
})

const selectedGenre = ref<NovelGenre | ''>('')
const selectedWordCount = ref<string | number>('50000')
const customWordCount = ref<number>(50000)
const selectedAudience = ref<'male' | 'female' | 'general'>('general')
const worldviewCount = ref<'single' | 'multiple'>('single')
const writingStyle = ref('')
const selectedTags = ref<string[]>([])

// ==================== 表单状态 ====================
const isCreating = ref(false)
const isDrafting = ref(false)
const formErrors = ref<Record<string, string>>({})

// ==================== AI 生成相关 ====================
const isGeneratingTitle = ref(false)
const isGeneratingIdea = ref(false)
const showTitleOptions = ref(false)
const showIdeaOptions = ref(false)
const generatedTitles = ref<any[]>([])
const generatedIdea = ref<any>(null)
const selectedTitleOption = ref('')

// ==================== 选项数据 ====================
const genreOptions = [
  { value: 'fantasy', label: '奇幻', icon: '🏰' },
  { value: 'romance', label: '言情', icon: '💕' },
  { value: 'mystery', label: '悬疑', icon: '🔍' },
  { value: 'scifi', label: '科幻', icon: '🚀' },
  { value: 'historical', label: '历史', icon: '📜' },
  { value: 'modern', label: '现代', icon: '🏙️' },
  { value: 'martial_arts', label: '武侠', icon: '⚔️' },
  { value: 'urban', label: '都市', icon: '🌆' },
  { value: 'game', label: '游戏', icon: '🎮' },
  { value: 'other', label: '其他', icon: '📚' }
]

const wordCountOptions = [
  { value: 30000, label: '短篇 (3万字)' },
  { value: 50000, label: '中短篇 (5万字)' },
  { value: 100000, label: '中篇 (10万字)' },
  { value: 200000, label: '长篇 (20万字)' },
  { value: 500000, label: '超长篇 (50万字)' },
  { value: 'custom', label: '自定义' }
]

const recommendedTags = computed(() => {
  const baseTagMap: Record<string, string[]> = {
    'fantasy': ['魔法', '异世界', '修仙', '玄幻', '冒险', '成长'],
    'romance': ['都市', '甜宠', '虐恋', '重生', '穿越', '豪门'],
    'mystery': ['推理', '悬疑', '犯罪', '侦探', '心理', '惊悚'],
    'scifi': ['未来', '机甲', '星际', '末世', '人工智能', '时空'],
    'historical': ['古代', '宫廷', '战争', '历史', '穿越', '架空'],
    'modern': ['都市', '职场', '校园', '青春', '励志', '生活'],
    'martial_arts': ['武侠', '江湖', '门派', '功夫', '侠义', '复仇'],
    'urban': ['都市', '商战', '豪门', '娱乐圈', '医生', '律师'],
    'game': ['游戏', '电竞', '虚拟现实', '网游', '竞技', '升级'],
    'other': ['原创', '创新', '实验', '文学', '艺术', '哲学']
  }
  
  return baseTagMap[selectedGenre.value as string] || baseTagMap['other']
})

// ==================== 计算属性 ====================
const canProceed = computed(() => {
  switch (currentStep.value) {
    case 0: // 基本信息
      return !!(novelForm.title.trim() && selectedGenre.value)
    case 1: // 创意设定
      return true // 创意描述是可选的
    case 2: // 目标设置
      return true // 目标设置都有默认值
    case 3: // 确认创建
      return true
    default:
      return false
  }
})

const hasUnsavedChanges = computed(() => {
  return !!(
    novelForm.title.trim() ||
    novelForm.description.trim() ||
    selectedGenre.value ||
    selectedTags.value.length > 0
  )
})

// ==================== 方法 ====================

// 步骤导航
const nextStep = () => {
  if (canProceed.value && currentStep.value < 3) {
    currentStep.value++
  }
}

const prevStep = () => {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

// 选择相关
const selectGenre = (genre: NovelGenre) => {
  selectedGenre.value = genre
  clearFieldError('genre')
}

const selectWordCount = (count: string | number) => {
  selectedWordCount.value = count
}

// 标签处理
const getGenreLabel = (genre: string) => {
  const option = genreOptions.find(opt => opt.value === genre)
  return option ? option.label : genre
}

const getWordCountLabel = () => {
  if (selectedWordCount.value === 'custom') {
    return `${customWordCount.value?.toLocaleString() || 0}字`
  }
  const option = wordCountOptions.find(opt => opt.value === selectedWordCount.value)
  return option ? option.label : `${selectedWordCount.value?.toLocaleString()}字`
}

const getAudienceLabel = () => {
  const map = {
    'male': '男性向',
    'female': '女性向',
    'general': '通用'
  }
  return map[selectedAudience.value]
}

const getWritingStyleLabel = () => {
  const map = {
    'humorous': '轻松幽默',
    'serious': '严肃正剧',
    'suspense': '悬疑紧张',
    'healing': '温馨治愈',
    'passionate': '热血激昂',
    'philosophical': '深度思考'
  }
  return map[writingStyle.value as keyof typeof map] || '未设置'
}

// 错误处理
const clearFieldError = (field: string) => {
  if (formErrors.value[field]) {
    delete formErrors.value[field]
  }
}

const setFieldError = (field: string, message: string) => {
  formErrors.value[field] = message
}

// AI生成功能
const generateNovelTitle = async () => {
  try {
    isGeneratingTitle.value = true
    
    const response = await generationApi.generateNovelName({
      genre: selectedGenre.value || undefined,
      keywords: novelForm.title || undefined,
      style: writingStyle.value || undefined,
      user_input: `请为${getGenreLabel(selectedGenre.value)}小说生成标题`
    })

    if (response.data?.titles) {
      generatedTitles.value = response.data.titles
      showTitleOptions.value = true
      ElMessage.success('标题生成成功')
    } else {
      ElMessage.error('生成失败，请稍后重试')
    }
  } catch (error: any) {
    console.error('生成标题失败:', error)
    ElMessage.error('生成失败，请稍后重试')
  } finally {
    isGeneratingTitle.value = false
  }
}

const generateNovelIdea = async () => {
  if (!selectedGenre.value) {
    ElMessage.warning('请先选择小说类型')
    return
  }

  try {
    isGeneratingIdea.value = true
    
    const response = await generationApi.generateNovelIdea({
      genre: selectedGenre.value,
      themes: selectedTags.value.join('，') || undefined,
      length: getWordCountRange(),
      user_input: novelForm.title ? `小说标题：${novelForm.title}` : undefined
    })

    if (response.data?.idea) {
      generatedIdea.value = response.data.idea
      showIdeaOptions.value = true
      ElMessage.success('创意生成成功')
    } else {
      ElMessage.error('生成失败，请稍后重试')
    }
  } catch (error: any) {
    console.error('生成创意失败:', error)
    ElMessage.error('生成失败，请稍后重试')
  } finally {
    isGeneratingIdea.value = false
  }
}

const getWordCountRange = () => {
  const count = selectedWordCount.value === 'custom' ? customWordCount.value : selectedWordCount.value
  if (typeof count === 'number') {
    if (count <= 50000) return '短篇'
    if (count <= 200000) return '中篇'
    return '长篇'
  }
  return '中篇'
}

// AI生成选项处理
const selectTitleOption = (title: string) => {
  selectedTitleOption.value = title
}

const applySelectedTitle = () => {
  if (selectedTitleOption.value) {
    novelForm.title = selectedTitleOption.value
    showTitleOptions.value = false
    selectedTitleOption.value = ''
    ElMessage.success('已应用生成的标题')
  }
}

const applyGeneratedIdea = () => {
  if (generatedIdea.value) {
    // 组合创意信息为描述
    const ideaParts = [
      `世界设定：${generatedIdea.value.setting}`,
      `主角设定：${generatedIdea.value.main_character}`,
      `核心冲突：${generatedIdea.value.conflict}`,
      `故事主线：${generatedIdea.value.plot}`,
      `独特卖点：${generatedIdea.value.unique_selling_point}`
    ]
    novelForm.description = ideaParts.join('\n\n')
    
    // 如果标题为空，使用生成的标题
    if (!novelForm.title.trim() && generatedIdea.value.title) {
      novelForm.title = generatedIdea.value.title
    }
    
    showIdeaOptions.value = false
    ElMessage.success('已应用生成的创意')
  }
}

const regenerateTitles = () => {
  selectedTitleOption.value = ''
  generateNovelTitle()
}

const regenerateIdea = () => {
  generateNovelIdea()
}

// 表单验证
const validateForm = (): boolean => {
  formErrors.value = {}
  
  if (!novelForm.title.trim()) {
    setFieldError('title', '请输入小说标题')
  }
  
  if (!selectedGenre.value) {
    setFieldError('genre', '请选择小说类型')
  }
  
  return Object.keys(formErrors.value).length === 0
}

// 创建小说
const createNovel = async () => {
  if (!validateForm()) {
    ElMessage.error('请检查表单内容')
    return
  }
  
  try {
    isCreating.value = true
    
    const novelData = {
      title: novelForm.title,
      description: novelForm.description || undefined,
      genre: selectedGenre.value as NovelGenre,
      tags: selectedTags.value,
      target_word_count: selectedWordCount.value === 'custom' 
        ? customWordCount.value 
        : (selectedWordCount.value as number)
    }
    
    const response = await NovelService.createNovel(novelData)
    
    ElMessage.success('小说创建成功！')
    
    // 清除草稿
    localStorage.removeItem('novel_create_draft')
    
    // 跳转到工作台
    if (response.data?.redirect_url) {
      router.push(response.data.redirect_url)
    } else {
      router.push('/novels')
    }
    
  } catch (error: any) {
    console.error('创建小说失败:', error)
    handleCreateError(error)
  } finally {
    isCreating.value = false
  }
}

// 保存草稿
const saveDraft = async () => {
  try {
    isDrafting.value = true
    
    // 保存到本地存储
    const draftData = {
      ...novelForm,
      genre: selectedGenre.value,
      wordCount: selectedWordCount.value,
      customWordCount: customWordCount.value,
      audience: selectedAudience.value,
      worldviewCount: worldviewCount.value,
      writingStyle: writingStyle.value,
      tags: selectedTags.value,
      savedAt: Date.now()
    }
    
    localStorage.setItem('novel_create_draft', JSON.stringify(draftData))
    ElMessage.success('草稿已保存')
    
  } catch (error) {
    console.error('保存草稿失败:', error)
    ElMessage.error('保存草稿失败')
  } finally {
    isDrafting.value = false
  }
}

// 取消创建
const cancelCreate = async () => {
  if (hasUnsavedChanges.value) {
    try {
      await ElMessageBox.confirm(
        '您有未保存的内容，是否要保存为草稿？',
        '确认离开',
        {
          confirmButtonText: '保存草稿',
          cancelButtonText: '直接离开',
          distinguishCancelAndClose: true,
          type: 'warning'
        }
      )
      
      await saveDraft()
    } catch (action) {
      if (action === 'cancel') {
        // 用户选择直接离开
      } else {
        // 用户取消了离开操作
        return
      }
    }
  }
  
  router.back()
}

// 错误处理
const handleCreateError = (error: any) => {
  const { status, data } = error.response || {}
  
  switch (status) {
    case 422:
      if (data.errors) {
        Object.keys(data.errors).forEach(field => {
          setFieldError(field, data.errors[field][0])
        })
      }
      ElMessage.error('请检查表单内容')
      break
    case 409:
      setFieldError('title', '小说标题已存在，请使用其他标题')
      currentStep.value = 0 // 跳转到标题输入步骤
      break
    case 403:
      ElMessage.error('您没有创建小说的权限')
      break
    default:
      ElMessage.error('创建失败，请稍后重试')
  }
}

// 恢复草稿
const restoreDraft = () => {
  const savedDraft = localStorage.getItem('novel_create_draft')
  if (savedDraft) {
    try {
      const draftData = JSON.parse(savedDraft)
      
      // 检查保存时间是否在24小时内
      const saveTime = draftData.savedAt
      const now = Date.now()
      if (now - saveTime < 24 * 60 * 60 * 1000) {
        ElMessageBox.confirm(
          '检测到本地保存的草稿，是否恢复？',
          '恢复草稿',
          {
            confirmButtonText: '恢复',
            cancelButtonText: '忽略',
            type: 'info'
          }
        ).then(() => {
          Object.assign(novelForm, {
            title: draftData.title || '',
            description: draftData.description || '',
            tags: draftData.tags || []
          })
          selectedGenre.value = draftData.genre || ''
          selectedWordCount.value = draftData.wordCount || 50000
          customWordCount.value = draftData.customWordCount || 50000
          selectedAudience.value = draftData.audience || 'general'
          worldviewCount.value = draftData.worldviewCount || 'single'
          writingStyle.value = draftData.writingStyle || ''
          selectedTags.value = draftData.tags || []
          
          ElMessage.success('草稿已恢复')
        }).catch(() => {
          localStorage.removeItem('novel_create_draft')
        })
      }
    } catch (error) {
      console.warn('Failed to restore draft:', error)
      localStorage.removeItem('novel_create_draft')
    }
  }
}

// 页面离开前保存
onBeforeRouteLeave((to, from, next) => {
  if (hasUnsavedChanges.value) {
    saveDraft()
  }
  next()
})

// 初始化
onMounted(() => {
  restoreDraft()
})
</script>

<style scoped>
.novel-create {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.page-header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  padding: 20px 0;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.container {
  max-width: 900px;
  margin: 0 auto;
  padding: 0 20px;
}

.create-form-container {
  padding: 40px 0;
}

.form-card {
  margin-bottom: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border-radius: 16px;
  overflow: hidden;
}

.form-section {
  padding: 24px;
}

.section-title {
  display: flex;
  align-items: center;
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
}

.section-title .el-icon {
  margin-right: 8px;
  color: #409EFF;
}

.section-description {
  color: #606266;
  font-size: 14px;
  margin-bottom: 24px;
  line-height: 1.5;
}

.input-with-ai {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  margin-bottom: 16px;
}

.input-field {
  flex: 1;
}

.ai-generate-btn {
  flex-shrink: 0;
  height: 40px;
}

.ai-generate-btn .el-icon {
  margin-right: 4px;
}

.error-message {
  color: #F56C6C;
  font-size: 12px;
  margin-top: 4px;
}

.tip-message {
  color: #909399;
  font-size: 12px;
  margin-top: 4px;
}

.genre-selector {
  margin-top: 24px;
}

.genre-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 12px;
  margin-top: 16px;
}

.genre-option {
  padding: 16px 12px;
  text-align: center;
  border: 2px solid #EBEEF5;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: #ffffff;
}

.genre-option:hover {
  border-color: #C6E2FF;
  background-color: #F0F9FF;
}

.genre-option.selected {
  border-color: #409EFF;
  background-color: #E1F3FF;
  color: #409EFF;
}

.genre-option .icon {
  font-size: 24px;
  margin-bottom: 8px;
}

.genre-option .label {
  font-size: 14px;
  font-weight: 500;
}

.target-settings {
  margin-top: 16px;
}

.setting-group {
  display: flex;
  align-items: flex-start;
  margin-bottom: 24px;
  gap: 24px;
}

.setting-label {
  min-width: 120px;
  font-weight: 500;
  color: #303133;
  line-height: 32px;
}

.setting-control {
  flex: 1;
}

.word-count-options {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.word-count-btn {
  padding: 8px 16px;
  border: 1px solid #DCDFE6;
  border-radius: 20px;
  background: #ffffff;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
}

.word-count-btn:hover {
  border-color: #409EFF;
  color: #409EFF;
}

.word-count-btn.selected {
  background: #409EFF;
  border-color: #409EFF;
  color: #ffffff;
}

.summary-card {
  margin-top: 16px;
}

.description-text {
  max-width: 400px;
  word-break: break-word;
  white-space: pre-line;
}

.form-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
  padding: 24px;
  border-top: 1px solid #EBEEF5;
  background: #FAFAFA;
}

.generated-options {
  max-height: 400px;
  overflow-y: auto;
}

.option-card {
  padding: 16px;
  border: 1px solid #DCDFE6;
  border-radius: 8px;
  margin-bottom: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.option-card:hover {
  border-color: #409EFF;
  background-color: #F0F9FF;
}

.option-card.selected {
  border-color: #409EFF;
  background-color: #E1F3FF;
}

.option-card h4 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 16px;
}

.option-card .reason {
  margin: 0;
  color: #606266;
  font-size: 14px;
  line-height: 1.5;
}

.idea-content {
  margin-bottom: 16px;
}

.is-error :deep(.el-input__wrapper) {
  border-color: #F56C6C !important;
  box-shadow: 0 0 0 1px #F56C6C inset !important;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .container {
    padding: 0 16px;
  }
  
  .create-form-container {
    padding: 20px 0;
  }
  
  .form-section {
    padding: 16px;
  }
  
  .input-with-ai {
    flex-direction: column;
  }
  
  .ai-generate-btn {
    align-self: flex-start;
  }
  
  .genre-grid {
    grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
    gap: 8px;
  }
  
  .setting-group {
    flex-direction: column;
    gap: 8px;
  }
  
  .setting-label {
    min-width: auto;
  }
  
  .word-count-options {
    gap: 8px;
  }
  
  .word-count-btn {
    padding: 6px 12px;
    font-size: 12px;
  }
  
  .form-actions {
    flex-direction: column;
    gap: 12px;
  }
}
</style>