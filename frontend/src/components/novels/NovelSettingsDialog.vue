<template>
  <el-dialog
    v-model="visible"
    title="小说设置"
    width="600px"
    :before-close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="100px"
    >
      <el-form-item label="小说标题" prop="title">
        <el-input v-model="form.title" placeholder="请输入小说标题" />
      </el-form-item>
      
      <el-form-item label="小说类型" prop="genre">
        <el-select v-model="form.genre" placeholder="选择小说类型" style="width: 100%">
          <el-option label="奇幻" value="fantasy" />
          <el-option label="言情" value="romance" />
          <el-option label="悬疑" value="mystery" />
          <el-option label="科幻" value="scifi" />
          <el-option label="历史" value="historical" />
          <el-option label="现代" value="modern" />
          <el-option label="武侠" value="martial_arts" />
          <el-option label="都市" value="urban" />
          <el-option label="游戏" value="game" />
          <el-option label="其他" value="other" />
        </el-select>
      </el-form-item>
      
      <el-form-item label="目标字数" prop="target_words">
        <el-input-number
          v-model="form.target_words"
          :min="1000"
          :max="10000000"
          :step="1000"
          controls-position="right"
          style="width: 100%"
        />
      </el-form-item>
      
      <el-form-item label="读者群体" prop="audience">
        <el-radio-group v-model="form.audience">
          <el-radio label="male">男性向</el-radio>
          <el-radio label="female">女性向</el-radio>
          <el-radio label="general">通用</el-radio>
        </el-radio-group>
      </el-form-item>
      
      <el-form-item label="写作风格" prop="writing_style">
        <el-input
          v-model="form.writing_style"
          placeholder="描述你的写作风格"
          type="textarea"
          :rows="3"
          maxlength="200"
          show-word-limit
        />
      </el-form-item>
      
      <el-form-item label="小说简介" prop="description">
        <el-input
          v-model="form.description"
          placeholder="请输入小说简介"
          type="textarea"
          :rows="4"
          maxlength="1000"
          show-word-limit
        />
      </el-form-item>
      
      <el-form-item label="标签" prop="tags">
        <div class="tags-input">
          <el-tag
            v-for="(tag, index) in form.tags"
            :key="tag"
            closable
            size="small"
            @close="removeTag(index)"
            class="tag-item"
          >
            {{ tag }}
          </el-tag>
          <el-input
            v-if="inputVisible"
            ref="inputRef"
            v-model="inputValue"
            size="small"
            style="width: 80px"
            @keyup.enter="handleInputConfirm"
            @blur="handleInputConfirm"
          />
          <el-button
            v-else
            size="small"
            @click="showInput"
          >
            + 添加标签
          </el-button>
        </div>
      </el-form-item>
      
      <el-form-item label="小说状态" prop="status">
        <el-select v-model="form.status" placeholder="选择小说状态" style="width: 100%">
          <el-option label="草稿" value="draft" />
          <el-option label="进行中" value="ongoing" />
          <el-option label="已完成" value="completed" />
          <el-option label="暂停" value="paused" />
        </el-select>
      </el-form-item>
    </el-form>

    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" @click="handleSave" :loading="saving">
          保存设置
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import type { NovelDetailResponse } from '@/api/novels'

interface Props {
  modelValue: boolean
  novel?: NovelDetailResponse | null
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'save', data: any): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// 响应式数据
const formRef = ref<FormInstance>()
const inputRef = ref()
const visible = ref(false)
const saving = ref(false)
const inputVisible = ref(false)
const inputValue = ref('')

const form = reactive({
  title: '',
  genre: '',
  target_words: null as number | null,
  audience: '',
  writing_style: '',
  description: '',
  tags: [] as string[],
  status: ''
})

// 表单验证规则
const rules: FormRules = {
  title: [
    { required: true, message: '请输入小说标题', trigger: 'blur' },
    { min: 1, max: 100, message: '标题长度应在1-100字符之间', trigger: 'blur' }
  ],
  genre: [
    { required: true, message: '请选择小说类型', trigger: 'change' }
  ],
  target_words: [
    { type: 'number', min: 1000, message: '目标字数不能少于1000字', trigger: 'blur' }
  ],
  description: [
    { max: 1000, message: '简介不能超过1000字符', trigger: 'blur' }
  ]
}

// 监听显示状态
watch(() => props.modelValue, (newValue) => {
  visible.value = newValue
  if (newValue && props.novel) {
    initForm()
  }
})

watch(visible, (newValue) => {
  emit('update:modelValue', newValue)
})

// 方法定义
const initForm = () => {
  if (!props.novel) return
  
  form.title = props.novel.title
  form.genre = props.novel.genre
  form.target_words = props.novel.target_words || null
  form.audience = props.novel.audience || ''
  form.writing_style = props.novel.writing_style || ''
  form.description = props.novel.description || ''
  form.tags = [...(props.novel.tags || [])]
  form.status = props.novel.status
}

const handleClose = () => {
  visible.value = false
}

const handleSave = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    saving.value = true
    
    const saveData = {
      title: form.title,
      genre: form.genre,
      target_words: form.target_words,
      audience: form.audience,
      writing_style: form.writing_style,
      description: form.description,
      tags: form.tags,
      status: form.status
    }
    
    emit('save', saveData)
    
  } catch (error) {
    console.error('表单验证失败:', error)
  } finally {
    saving.value = false
  }
}

const removeTag = (index: number) => {
  form.tags.splice(index, 1)
}

const showInput = () => {
  inputVisible.value = true
  nextTick(() => {
    inputRef.value?.focus()
  })
}

const handleInputConfirm = () => {
  const value = inputValue.value.trim()
  if (value && !form.tags.includes(value)) {
    form.tags.push(value)
  }
  inputVisible.value = false
  inputValue.value = ''
}
</script>

<style scoped lang="scss">
.tags-input {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
  
  .tag-item {
    margin: 0;
  }
}

:deep(.el-dialog__body) {
  padding: 20px;
}

:deep(.el-form-item__label) {
  font-weight: 500;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>