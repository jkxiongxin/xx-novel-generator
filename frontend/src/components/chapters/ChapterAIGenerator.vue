<template>
  <div class="chapter-ai-generator">
    <el-dialog
      v-model="visible"
      title="AI章节生成"
      width="700px"
      @close="resetForm"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="120px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="章节序号" prop="chapter_number">
              <el-input-number
                v-model="form.chapter_number"
                :min="1"
                :max="10000"
                placeholder="章节序号"
                style="width: 100%;"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="目标字数" prop="target_word_count">
              <el-input-number
                v-model="form.target_word_count"
                :min="100"
                :max="50000"
                :step="500"
                placeholder="目标字数"
                style="width: 100%;"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="生成模式" prop="generation_mode">
          <el-radio-group v-model="form.generation_mode">
            <el-radio label="create">全新创作</el-radio>
            <el-radio label="continue">续写章节</el-radio>
            <el-radio label="rewrite">重写优化</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="提示词模板">
          <el-select
            v-model="form.prompt_template"
            placeholder="选择提示词模板"
            style="width: 100%;"
            @change="handleTemplateChange"
          >
            <el-option
              v-for="template in promptTemplates"
              :key="template.id"
              :label="template.name"
              :value="template.template_type"
            >
              <div style="display: flex; justify-content: space-between;">
                <span>{{ template.name }}</span>
                <el-tag size="small" type="info">{{ template.category }}</el-tag>
              </div>
            </el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="关联大纲">
          <el-select
            v-model="form.outline_id"
            placeholder="选择相关大纲"
            clearable
            style="width: 100%;"
          >
            <el-option
              v-for="outline in outlines"
              :key="outline.id"
              :label="outline.chapter_title || '未命名大纲'"
              :value="outline.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="关联角色">
          <el-select
            v-model="form.character_ids"
            placeholder="选择相关角色"
            multiple
            style="width: 100%;"
          >
            <el-option
              v-for="character in characters"
              :key="character.id"
              :label="character.name"
              :value="character.id"
            >
              <div style="display: flex; justify-content: space-between;">
                <span>{{ character.name }}</span>
                <el-tag size="small" :type="getCharacterTypeColor(character.character_type)">
                  {{ getCharacterTypeLabel(character.character_type) }}
                </el-tag>
              </div>
            </el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="上下文设置">
          <el-checkbox-group v-model="contextOptions">
            <el-checkbox label="include_worldview">包含世界观信息</el-checkbox>
            <el-checkbox label="include_characters">包含角色信息</el-checkbox>
            <el-checkbox label="include_outline">包含大纲信息</el-checkbox>
          </el-checkbox-group>
        </el-form-item>

        <el-form-item label="用户建议">
          <el-input
            v-model="form.user_suggestion"
            type="textarea"
            :rows="4"
            placeholder="请输入您希望AI生成的章节特点、情节发展方向或其他要求..."
          />
        </el-form-item>

        <el-form-item label="高级参数">
          <el-collapse>
            <el-collapse-item title="生成参数设置" name="advanced">
              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="创造性">
                    <el-slider
                      v-model="form.generation_params.temperature"
                      :min="0"
                      :max="1"
                      :step="0.1"
                      show-input
                      :format-tooltip="formatTemperature"
                    />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="最大令牌">
                    <el-input-number
                      v-model="form.generation_params.max_tokens"
                      :min="100"
                      :max="30000"
                      :step="100"
                      style="width: 100%;"
                    />
                  </el-form-item>
                </el-col>
              </el-row>
            </el-collapse-item>
          </el-collapse>
        </el-form-item>
      </el-form>

      <!-- 预览区域 -->
      <div class="preview-section" v-if="selectedTemplate">
        <h4>
          <el-icon><view /></el-icon>
          提示词预览
        </h4>
        <div class="template-preview">
          <div class="template-info">
            <el-tag type="success">{{ selectedTemplate.name }}</el-tag>
            <span class="template-desc">{{ selectedTemplate.description }}</span>
          </div>
          <div class="template-content">
            {{ selectedTemplate.template_content }}
          </div>
        </div>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <div class="footer-info">
            <el-icon><info-filled /></el-icon>
            <span>生成时间约需要 30-60 秒，请耐心等待</span>
          </div>
          <div class="footer-actions">
            <el-button @click="visible = false">取消</el-button>
            <el-button type="primary" @click="generateChapter" :loading="generating">
              {{ generating ? '生成中...' : '开始生成' }}
            </el-button>
          </div>
        </div>
      </template>
    </el-dialog>

    <!-- 生成进度对话框 -->
    <el-dialog
      v-model="showProgress"
      title="正在生成章节"
      width="500px"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      :show-close="false"
    >
      <div class="progress-content">
        <div class="progress-icon">
          <el-icon class="rotating"><loading /></el-icon>
        </div>
        <div class="progress-text">
          <h3>AI正在创作中...</h3>
          <p>{{ progressMessage }}</p>
          <el-progress :percentage="progressPercentage" :show-text="false" />
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { View, InfoFilled, Loading } from '@element-plus/icons-vue'
import * as chaptersApi from '@/api/chapters'

// Props
const props = defineProps({
  novelId: {
    type: Number,
    required: true
  },
  characters: {
    type: Array,
    default: () => []
  },
  outlines: {
    type: Array,
    default: () => []
  },
  existingChapters: {
    type: Array,
    default: () => []
  }
})

// Emits
const emit = defineEmits(['generated', 'close'])

// 响应式数据
const visible = ref(false)
const showProgress = ref(false)
const generating = ref(false)
const formRef = ref(null)
const promptTemplates = ref([])
const selectedTemplate = ref(null)
const progressMessage = ref('正在准备生成...')
const progressPercentage = ref(0)

// 表单数据
const form = reactive({
  chapter_number: 1,
  target_word_count: 3000,
  generation_mode: 'create',
  prompt_template: '',
  outline_id: null,
  character_ids: [],
  user_suggestion: '',
  generation_params: {
    temperature: 0.7,
    max_tokens: 30000
  }
})

// 上下文选项
const contextOptions = ref(['include_worldview', 'include_characters', 'include_outline'])

// 表单验证规则
const rules = {
  chapter_number: [
    { required: true, message: '请输入章节序号', trigger: 'blur' },
    { type: 'number', min: 1, max: 10000, message: '章节序号必须在1-10000之间', trigger: 'blur' }
  ],
  target_word_count: [
    { required: true, message: '请输入目标字数', trigger: 'blur' },
    { type: 'number', min: 100, max: 50000, message: '目标字数必须在100-50000之间', trigger: 'blur' }
  ]
}

// 计算属性
const nextChapterNumber = computed(() => {
  if (props.existingChapters.length === 0) return 1
  return Math.max(...props.existingChapters.map(c => c.chapter_number)) + 1
})

// 方法
const show = (chapterNumber = null) => {
  form.chapter_number = chapterNumber || nextChapterNumber.value
  visible.value = true
  loadPromptTemplates()
}

const hide = () => {
  visible.value = false
  emit('close')
}

const resetForm = () => {
  Object.assign(form, {
    chapter_number: nextChapterNumber.value,
    target_word_count: 3000,
    generation_mode: 'create',
    prompt_template: '',
    outline_id: null,
    character_ids: [],
    user_suggestion: '',
    generation_params: {
      temperature: 0.7,
      max_tokens: 30000
    }
  })
  contextOptions.value = ['include_worldview', 'include_characters', 'include_outline']
  selectedTemplate.value = null
}

const loadPromptTemplates = async () => {
  try {
    // 模拟获取提示词模板
    promptTemplates.value = [
      {
        id: 1,
        name: '通用章节生成',
        template_type: 'chapter_general',
        category: '通用',
        description: '适用于各种类型的章节生成',
        template_content: '根据小说背景和前文内容，创作一个引人入胜的新章节...'
      },
      {
        id: 2,
        name: '情感对话重点',
        template_type: 'chapter_dialogue',
        category: '对话',
        description: '重点生成角色对话和情感表达',
        template_content: '注重角色间的对话交流，展现人物性格和情感变化...'
      },
      {
        id: 3,
        name: '动作场景',
        template_type: 'chapter_action',
        category: '动作',
        description: '适合战斗、追逐等动作场景',
        template_content: '创作紧张刺激的动作场景，注重节奏和画面感...'
      }
    ]
  } catch (error) {
    console.error('加载提示词模板失败:', error)
  }
}

const handleTemplateChange = (templateType) => {
  selectedTemplate.value = promptTemplates.value.find(t => t.template_type === templateType)
}

const generateChapter = async () => {
  try {
    // 表单验证
    const valid = await formRef.value?.validate()
    if (!valid) return

    // 检查章节号是否已存在
    const existingChapter = props.existingChapters.find(c => c.chapter_number === form.chapter_number)
    if (existingChapter) {
      ElMessage.error(`第${form.chapter_number}章已存在，请选择其他章节号`)
      return
    }

    generating.value = true
    showProgress.value = true
    visible.value = false

    // 模拟生成进度
    const progressSteps = [
      { message: '正在分析小说背景...', percentage: 20 },
      { message: '正在整理角色信息...', percentage: 40 },
      { message: '正在构思章节大纲...', percentage: 60 },
      { message: '正在生成章节内容...', percentage: 80 },
      { message: '正在优化文本质量...', percentage: 95 }
    ]

    for (const step of progressSteps) {
      progressMessage.value = step.message
      progressPercentage.value = step.percentage
      await new Promise(resolve => setTimeout(resolve, 800))
    }

    // 构建生成请求
    const requestData = {
      novel_id: props.novelId,
      chapter_number: form.chapter_number,
      prompt_template: form.prompt_template,
      target_word_count: form.target_word_count,
      generation_mode: form.generation_mode,
      outline_id: form.outline_id,
      character_ids: form.character_ids,
      user_suggestion: form.user_suggestion,
      include_worldview: contextOptions.value.includes('include_worldview'),
      include_characters: contextOptions.value.includes('include_characters'),
      include_outline: contextOptions.value.includes('include_outline'),
      generation_params: form.generation_params
    }

    const result = await chaptersApi.generateChapter(requestData)

    progressMessage.value = '生成完成！'
    progressPercentage.value = 100

    if (result.success) {
      setTimeout(() => {
        showProgress.value = false
        ElMessage.success(`第${form.chapter_number}章生成成功！字数：${result.word_count}`)
        emit('generated', result.chapter)
        resetForm()
      }, 1000)
    } else {
      showProgress.value = false
      ElMessage.error(result.message || '章节生成失败')
    }

  } catch (error) {
    showProgress.value = false
    console.error('章节生成失败:', error)
    ElMessage.error('章节生成失败，请重试')
  } finally {
    generating.value = false
  }
}

const getCharacterTypeColor = (type) => {
  const colors = {
    protagonist: 'danger',
    supporting: 'primary',
    antagonist: 'warning',
    minor: 'info'
  }
  return colors[type] || 'info'
}

const getCharacterTypeLabel = (type) => {
  const labels = {
    protagonist: '主角',
    supporting: '配角',
    antagonist: '反派',
    minor: '次要角色'
  }
  return labels[type] || type
}

const formatTemperature = (value) => {
  const labels = {
    0: '保守',
    0.3: '稳定',
    0.5: '平衡',
    0.7: '创新',
    1: '大胆'
  }
  return labels[value] || `${value}`
}

// 监听器
watch(() => props.existingChapters, () => {
  form.chapter_number = nextChapterNumber.value
})

// 暴露方法
defineExpose({
  show,
  hide
})
</script>

<style scoped>
.chapter-ai-generator {
  /* 基础样式 */
}

.preview-section {
  margin-top: 20px;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 6px;
  border: 1px solid #e4e7ed;
}

.preview-section h4 {
  margin: 0 0 12px 0;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #606266;
}

.template-preview {
  background: white;
  border-radius: 4px;
  padding: 12px;
}

.template-info {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.template-desc {
  font-size: 12px;
  color: #909399;
}

.template-content {
  font-size: 13px;
  color: #606266;
  line-height: 1.5;
  padding: 8px;
  background: #fafafa;
  border-radius: 4px;
  border-left: 3px solid #409eff;
}

.dialog-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.footer-info {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #909399;
}

.footer-actions {
  display: flex;
  gap: 8px;
}

.progress-content {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 20px 0;
}

.progress-icon {
  font-size: 48px;
  color: #409eff;
}

.progress-text {
  flex: 1;
}

.progress-text h3 {
  margin: 0 0 8px 0;
  font-size: 18px;
  color: #303133;
}

.progress-text p {
  margin: 0 0 12px 0;
  color: #606266;
}

.rotating {
  animation: rotating 2s linear infinite;
}

@keyframes rotating {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .dialog-footer {
    flex-direction: column;
    gap: 12px;
  }
  
  .progress-content {
    flex-direction: column;
    text-align: center;
  }
}
</style>