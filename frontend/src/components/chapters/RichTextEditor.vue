<template>
  <div class="rich-text-editor">
    <div class="editor-toolbar">
      <div class="toolbar-left">
        <el-button-group>
          <el-button @click="formatText('bold')" :type="isActive('bold') ? 'primary' : 'default'" size="small">
            <el-icon><i class="fas fa-bold"></i></el-icon>
          </el-button>
          <el-button @click="formatText('italic')" :type="isActive('italic') ? 'primary' : 'default'" size="small">
            <el-icon><i class="fas fa-italic"></i></el-icon>
          </el-button>
          <el-button @click="formatText('underline')" :type="isActive('underline') ? 'primary' : 'default'" size="small">
            <el-icon><i class="fas fa-underline"></i></el-icon>
          </el-button>
        </el-button-group>
        
        <el-button-group style="margin-left: 8px;">
          <el-button @click="formatText('list', 'ordered')" size="small">
            <el-icon><i class="fas fa-list-ol"></i></el-icon>
          </el-button>
          <el-button @click="formatText('list', 'bullet')" size="small">
            <el-icon><i class="fas fa-list-ul"></i></el-icon>
          </el-button>
        </el-button-group>
        
        <el-button-group style="margin-left: 8px;">
          <el-button @click="formatText('align', 'left')" size="small">
            <el-icon><i class="fas fa-align-left"></i></el-icon>
          </el-button>
          <el-button @click="formatText('align', 'center')" size="small">
            <el-icon><i class="fas fa-align-center"></i></el-icon>
          </el-button>
          <el-button @click="formatText('align', 'right')" size="small">
            <el-icon><i class="fas fa-align-right"></i></el-icon>
          </el-button>
        </el-button-group>
      </div>
      
      <div class="toolbar-right">
        <span class="word-count">字数: {{ wordCount }}</span>
        <el-button v-if="autoSaveEnabled" @click="saveContent" :loading="saving" type="success" size="small">
          {{ saving ? '保存中...' : '保存' }}
        </el-button>
      </div>
    </div>
    
    <div class="editor-container">
      <QuillEditor
        ref="quillEditor"
        v-model:content="content"
        :options="editorOptions"
        content-type="html"
        @textChange="handleTextChange"
        @ready="onEditorReady"
        class="quill-editor"
      />
    </div>
    
    <div class="editor-footer">
      <div class="auto-save-info" v-if="autoSaveEnabled">
        <el-switch
          v-model="autoSaveEnabled"
          size="small"
          active-text="自动保存"
          inactive-text="手动保存"
        />
        <span v-if="lastSaveTime" class="last-save">
          最后保存: {{ formatTime(lastSaveTime) }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { QuillEditor } from '@vueup/vue-quill'
import '@vueup/vue-quill/dist/vue-quill.snow.css'
import { ElMessage } from 'element-plus'

// Props
const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  chapterId: {
    type: Number,
    default: null
  },
  autoSaveInterval: {
    type: Number,
    default: 30000 // 30秒
  },
  placeholder: {
    type: String,
    default: '请输入章节内容...'
  },
  minHeight: {
    type: String,
    default: '400px'
  }
})

// Emits
const emit = defineEmits(['update:modelValue', 'save', 'word-count-change'])

// 响应式数据
const content = ref(props.modelValue)
const quillEditor = ref(null)
const saving = ref(false)
const autoSaveEnabled = ref(true)
const lastSaveTime = ref(null)
const autoSaveTimer = ref(null)

// 编辑器配置
const editorOptions = {
  theme: 'snow',
  placeholder: props.placeholder,
  modules: {
    toolbar: false, // 使用自定义工具栏
    history: {
      delay: 1000,
      maxStack: 50,
      userOnly: true
    }
  },
  formats: [
    'bold', 'italic', 'underline', 'strike',
    'blockquote', 'list', 'bullet', 'indent',
    'link', 'align', 'color', 'background',
    'size', 'header'
  ]
}

// 计算属性
const wordCount = computed(() => {
  if (!content.value) return 0
  // 移除HTML标签并计算字符数
  const text = content.value.replace(/<[^>]*>/g, '')
  return text.length
})

// 方法
const handleTextChange = () => {
  emit('update:modelValue', content.value)
  emit('word-count-change', wordCount.value)
  
  // 如果启用自动保存，重置定时器
  if (autoSaveEnabled.value && props.chapterId) {
    resetAutoSaveTimer()
  }
}

const onEditorReady = (quill) => {
  // 编辑器准备就绪
  console.log('编辑器已就绪')
}

const formatText = (format, value = true) => {
  const quill = quillEditor.value?.getQuill()
  if (!quill) return
  
  if (format === 'list') {
    quill.format('list', value)
  } else if (format === 'align') {
    quill.format('align', value)
  } else {
    quill.format(format, value)
  }
}

const isActive = (format) => {
  const quill = quillEditor.value?.getQuill()
  if (!quill) return false
  
  const range = quill.getSelection()
  if (!range) return false
  
  const formats = quill.getFormat(range)
  return !!formats[format]
}

const saveContent = async () => {
  if (saving.value || !props.chapterId) return
  
  try {
    saving.value = true
    await emit('save', {
      chapterId: props.chapterId,
      content: content.value,
      wordCount: wordCount.value
    })
    
    lastSaveTime.value = new Date()
    ElMessage.success('保存成功')
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

const resetAutoSaveTimer = () => {
  if (autoSaveTimer.value) {
    clearTimeout(autoSaveTimer.value)
  }
  
  autoSaveTimer.value = setTimeout(() => {
    if (autoSaveEnabled.value) {
      saveContent()
    }
  }, props.autoSaveInterval)
}

const formatTime = (time) => {
  if (!time) return ''
  return new Date(time).toLocaleTimeString()
}

// 监听器
watch(() => props.modelValue, (newValue) => {
  if (newValue !== content.value) {
    content.value = newValue
  }
})

watch(autoSaveEnabled, (enabled) => {
  if (enabled && props.chapterId) {
    resetAutoSaveTimer()
  } else if (autoSaveTimer.value) {
    clearTimeout(autoSaveTimer.value)
    autoSaveTimer.value = null
  }
})

// 生命周期
onMounted(() => {
  if (autoSaveEnabled.value && props.chapterId) {
    resetAutoSaveTimer()
  }
})

onUnmounted(() => {
  if (autoSaveTimer.value) {
    clearTimeout(autoSaveTimer.value)
  }
})

// 暴露方法给父组件
defineExpose({
  saveContent,
  getContent: () => content.value,
  getWordCount: () => wordCount.value,
  focus: () => {
    const quill = quillEditor.value?.getQuill()
    if (quill) {
      quill.focus()
    }
  }
})
</script>

<style scoped>
.rich-text-editor {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
}

.editor-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f5f7fa;
  border-bottom: 1px solid #e4e7ed;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.word-count {
  font-size: 14px;
  color: #606266;
  margin-right: 8px;
}

.editor-container {
  min-height: v-bind(minHeight);
}

.quill-editor :deep(.ql-container) {
  min-height: v-bind(minHeight);
  font-size: 16px;
  line-height: 1.8;
}

.quill-editor :deep(.ql-editor) {
  padding: 20px;
  color: #303133;
}

.quill-editor :deep(.ql-editor.ql-blank::before) {
  color: #c0c4cc;
  font-style: normal;
}

.editor-footer {
  padding: 8px 16px;
  background: #fafafa;
  border-top: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.auto-save-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.last-save {
  font-size: 12px;
  color: #909399;
}

/* 工具栏按钮样式 */
.el-button-group .el-button {
  border: none;
  background: transparent;
}

.el-button-group .el-button:hover {
  background: #ecf5ff;
  color: #409eff;
}

.el-button-group .el-button.is-type-primary {
  background: #409eff;
  color: white;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .editor-toolbar {
    flex-direction: column;
    gap: 8px;
    padding: 8px 12px;
  }
  
  .toolbar-left {
    justify-content: center;
  }
  
  .toolbar-right {
    justify-content: center;
  }
  
  .quill-editor :deep(.ql-editor) {
    padding: 12px;
  }
}
</style>