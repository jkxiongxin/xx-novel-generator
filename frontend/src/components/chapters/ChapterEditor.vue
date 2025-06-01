<template>
  <div class="chapter-editor">
    <div class="editor-header">
      <div class="header-left">
        <div class="chapter-info">
          <h2 v-if="chapter">
            第{{ chapter.chapter_number }}章: {{ chapter.title }}
          </h2>
          <h2 v-else>新建章节</h2>
          
          <div class="chapter-meta" v-if="chapter">
            <el-tag :type="getStatusColor(chapter.status)" size="small">
              {{ getStatusLabel(chapter.status) }}
            </el-tag>
            <span class="version">v{{ chapter.version || 1 }}</span>
            <span class="word-count">{{ currentWordCount }} 字</span>
            <span class="update-time" v-if="chapter.updated_at">
              更新于 {{ formatTime(chapter.updated_at) }}
            </span>
          </div>
        </div>
      </div>
      
      <div class="header-actions">
        <el-button-group>
          <el-button @click="showAIGenerator" type="primary" :disabled="!chapter">
            <el-icon><magic-stick /></el-icon>
            AI续写
          </el-button>
          <el-button @click="saveChapter" :loading="saving">
            <el-icon><document /></el-icon>
            {{ saving ? '保存中...' : '保存' }}
          </el-button>
          <el-button @click="previewChapter">
            <el-icon><view /></el-icon>
            预览
          </el-button>
        </el-button-group>
        
        <el-dropdown @command="handleMoreAction" v-if="chapter">
          <el-button>
            更多<el-icon class="el-icon--right"><arrow-down /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="duplicate">复制章节</el-dropdown-item>
              <el-dropdown-item command="export">导出章节</el-dropdown-item>
              <el-dropdown-item command="history">版本历史</el-dropdown-item>
              <el-dropdown-item command="settings">章节设置</el-dropdown-item>
              <el-dropdown-item command="delete" divided>删除章节</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>
    
    <div class="editor-body">
      <div class="editor-sidebar">
        <el-tabs v-model="sidebarTab" tab-position="top">
          <el-tab-pane label="基本信息" name="info">
            <div class="info-section">
              <el-form :model="editForm" label-width="80px" size="small">
                <el-form-item label="章节标题">
                  <el-input
                    v-model="editForm.title"
                    placeholder="请输入章节标题"
                    @change="markChanged"
                  />
                </el-form-item>
                
                <el-form-item label="章节序号">
                  <el-input-number
                    v-model="editForm.chapter_number"
                    :min="1"
                    :max="10000"
                    style="width: 100%;"
                    @change="markChanged"
                  />
                </el-form-item>
                
                <el-form-item label="状态">
                  <el-select v-model="editForm.status" style="width: 100%;" @change="markChanged">
                    <el-option label="草稿" value="draft" />
                    <el-option label="已完成" value="completed" />
                    <el-option label="已发布" value="published" />
                  </el-select>
                </el-form-item>
                
                <el-form-item label="关联大纲">
                  <el-select
                    v-model="editForm.outline_id"
                    placeholder="选择大纲"
                    clearable
                    style="width: 100%;"
                    @change="markChanged"
                  >
                    <el-option
                      v-for="outline in outlines"
                      :key="outline.id"
                      :label="outline.chapter_title || '未命名大纲'"
                      :value="outline.id"
                    />
                  </el-select>
                </el-form-item>
                
                <el-form-item label="相关角色">
                  <el-select
                    v-model="editForm.character_ids"
                    placeholder="选择角色"
                    multiple
                    style="width: 100%;"
                    @change="markChanged"
                  >
                    <el-option
                      v-for="character in characters"
                      :key="character.id"
                      :label="character.name"
                      :value="character.id"
                    />
                  </el-select>
                </el-form-item>
                
                <el-form-item label="备注">
                  <el-input
                    v-model="editForm.notes"
                    type="textarea"
                    :rows="3"
                    placeholder="章节备注"
                    @change="markChanged"
                  />
                </el-form-item>
              </el-form>
            </div>
          </el-tab-pane>
          
          <el-tab-pane label="写作助手" name="assistant">
            <div class="assistant-section">
              <div class="assistant-item">
                <h4>相关角色</h4>
                <div class="character-cards" v-if="relatedCharacters.length > 0">
                  <div
                    v-for="character in relatedCharacters"
                    :key="character.id"
                    class="character-card"
                    @click="insertCharacterInfo(character)"
                  >
                    <div class="character-name">{{ character.name }}</div>
                    <div class="character-desc">{{ character.personality }}</div>
                  </div>
                </div>
                <el-empty v-else description="暂无相关角色" />
              </div>
              
              <div class="assistant-item">
                <h4>大纲要点</h4>
                <div class="outline-info" v-if="relatedOutline">
                  <p><strong>章节标题：</strong>{{ relatedOutline.chapter_title }}</p>
                  <p><strong>情节点：</strong>{{ relatedOutline.plot_points }}</p>
                  <p><strong>角色进出场：</strong>{{ relatedOutline.character_appearances }}</p>
                </div>
                <el-empty v-else description="暂无关联大纲" />
              </div>
              
              <div class="assistant-item">
                <h4>快速操作</h4>
                <div class="quick-actions">
                  <el-button size="small" @click="insertTemplate('dialogue')">
                    插入对话模板
                  </el-button>
                  <el-button size="small" @click="insertTemplate('scene')">
                    插入场景描述
                  </el-button>
                  <el-button size="small" @click="insertTemplate('action')">
                    插入动作场面
                  </el-button>
                </div>
              </div>
            </div>
          </el-tab-pane>
          
          <el-tab-pane label="统计信息" name="stats">
            <div class="stats-section">
              <div class="stat-item">
                <div class="stat-label">字数统计</div>
                <div class="stat-value">{{ currentWordCount }}</div>
              </div>
              <div class="stat-item">
                <div class="stat-label">目标字数</div>
                <div class="stat-value">{{ targetWordCount || '未设置' }}</div>
              </div>
              <div class="stat-item">
                <div class="stat-label">完成度</div>
                <div class="stat-value">
                  {{ targetWordCount ? Math.round((currentWordCount / targetWordCount) * 100) : 0 }}%
                </div>
              </div>
              <div class="stat-item">
                <div class="stat-label">段落数</div>
                <div class="stat-value">{{ paragraphCount }}</div>
              </div>
              <div class="stat-item">
                <div class="stat-label">写作时间</div>
                <div class="stat-value">{{ writingTime }}</div>
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
      
      <div class="editor-main">
        <RichTextEditor
          ref="editorRef"
          v-model="editForm.content"
          :chapter-id="chapter?.id"
          :auto-save-interval="30000"
          min-height="calc(100vh - 200px)"
          @save="handleSave"
          @word-count-change="handleWordCountChange"
        />
      </div>
    </div>
    
    <!-- AI续写对话框 -->
    <ChapterAIGenerator
      ref="aiGeneratorRef"
      :novel-id="novelId"
      :characters="characters"
      :outlines="outlines"
      :existing-chapters="[chapter].filter(Boolean)"
      @generated="handleAIGenerated"
    />
    
    <!-- 预览对话框 -->
    <el-dialog v-model="showPreview" title="章节预览" width="80%" top="5vh">
      <div class="preview-content" v-html="previewContent"></div>
    </el-dialog>
    
    <!-- 章节设置对话框 -->
    <el-dialog v-model="showSettings" title="章节设置" width="500px">
      <el-form :model="settingsForm" label-width="100px">
        <el-form-item label="目标字数">
          <el-input-number
            v-model="settingsForm.target_word_count"
            :min="0"
            :max="50000"
            style="width: 100%;"
          />
        </el-form-item>
        <el-form-item label="自动保存">
          <el-switch v-model="settingsForm.auto_save" />
        </el-form-item>
        <el-form-item label="保存间隔">
          <el-select v-model="settingsForm.save_interval" style="width: 100%;">
            <el-option label="15秒" :value="15000" />
            <el-option label="30秒" :value="30000" />
            <el-option label="60秒" :value="60000" />
            <el-option label="5分钟" :value="300000" />
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showSettings = false">取消</el-button>
        <el-button type="primary" @click="saveSettings">保存设置</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  MagicStick, Document, View, ArrowDown
} from '@element-plus/icons-vue'
import RichTextEditor from './RichTextEditor.vue'
import ChapterAIGenerator from './ChapterAIGenerator.vue'
import * as chaptersApi from '@/api/chapters'

// Props
const props = defineProps({
  chapter: {
    type: Object,
    default: null
  },
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
  }
})

// Emits
const emit = defineEmits(['saved', 'deleted', 'status-changed'])

// 响应式数据
const editorRef = ref(null)
const aiGeneratorRef = ref(null)
const saving = ref(false)
const hasChanges = ref(false)
const sidebarTab = ref('info')
const showPreview = ref(false)
const showSettings = ref(false)
const currentWordCount = ref(0)
const startTime = ref(Date.now())
const writingTime = ref('0分钟')

// 表单数据
const editForm = reactive({
  title: '',
  content: '',
  chapter_number: 1,
  status: 'draft',
  outline_id: null,
  character_ids: [],
  notes: ''
})

const settingsForm = reactive({
  target_word_count: 3000,
  auto_save: true,
  save_interval: 30000
})

// 计算属性
const relatedCharacters = computed(() => {
  return props.characters.filter(c => editForm.character_ids.includes(c.id))
})

const relatedOutline = computed(() => {
  return props.outlines.find(o => o.id === editForm.outline_id)
})

const targetWordCount = computed(() => {
  return settingsForm.target_word_count
})

const paragraphCount = computed(() => {
  if (!editForm.content) return 0
  const text = editForm.content.replace(/<[^>]*>/g, '')
  return text.split(/\n\s*\n/).filter(p => p.trim()).length
})

const previewContent = computed(() => {
  return editForm.content || '<p>暂无内容</p>'
})

// 方法
const loadChapter = () => {
  if (props.chapter) {
    Object.assign(editForm, {
      title: props.chapter.title || '',
      content: props.chapter.content || '',
      chapter_number: props.chapter.chapter_number || 1,
      status: props.chapter.status || 'draft',
      outline_id: props.chapter.outline_id || null,
      character_ids: props.chapter.character_ids || [],
      notes: props.chapter.notes || ''
    })
    currentWordCount.value = props.chapter.word_count || 0
    hasChanges.value = false
  } else {
    // 新建章节时重置表单
    Object.assign(editForm, {
      title: '',
      content: '',
      chapter_number: 1,
      status: 'draft',
      outline_id: null,
      character_ids: [],
      notes: ''
    })
    currentWordCount.value = 0
    hasChanges.value = false
  }
}

const markChanged = () => {
  hasChanges.value = true
}

const saveChapter = async () => {
  try {
    saving.value = true
    
    const saveData = {
      ...editForm,
      novel_id: props.novelId
    }
    
    let savedChapter
    if (props.chapter?.id) {
      // 更新现有章节
      savedChapter = await chaptersApi.updateChapter(props.chapter.id, saveData)
      ElMessage.success('章节保存成功')
    } else {
      // 创建新章节
      savedChapter = await chaptersApi.createChapter(saveData)
      ElMessage.success('章节创建成功')
    }
    
    hasChanges.value = false
    emit('saved', savedChapter)
    
  } catch (error) {
    console.error('保存章节失败:', error)
    ElMessage.error('保存失败，请重试')
  } finally {
    saving.value = false
  }
}

const handleSave = async (data) => {
  await saveChapter()
}

const handleWordCountChange = (count) => {
  currentWordCount.value = count
  markChanged()
}

const showAIGenerator = () => {
  if (!props.chapter) {
    ElMessage.warning('请先保存章节后再使用AI续写功能')
    return
  }
  aiGeneratorRef.value?.show()
}

const handleAIGenerated = (newChapter) => {
  // AI生成的内容追加到当前内容
  if (newChapter && newChapter.content) {
    editForm.content += '\n\n' + newChapter.content
    markChanged()
    ElMessage.success('AI内容已添加到编辑器')
  }
}

const previewChapter = () => {
  showPreview.value = true
}

const handleMoreAction = async (command) => {
  switch (command) {
    case 'duplicate':
      await duplicateChapter()
      break
    case 'export':
      exportChapter()
      break
    case 'history':
      showVersionHistory()
      break
    case 'settings':
      showSettings.value = true
      break
    case 'delete':
      await deleteChapter()
      break
  }
}

const duplicateChapter = async () => {
  try {
    const newChapter = await chaptersApi.createChapter({
      novel_id: props.novelId,
      title: `${editForm.title} (副本)`,
      content: editForm.content,
      chapter_number: editForm.chapter_number + 1,
      character_ids: editForm.character_ids,
      notes: `复制自第${editForm.chapter_number}章`
    })
    
    ElMessage.success('章节复制成功')
    emit('saved', newChapter)
  } catch (error) {
    console.error('复制章节失败:', error)
    ElMessage.error('复制失败')
  }
}

const exportChapter = () => {
  const content = `第${editForm.chapter_number}章: ${editForm.title}\n\n${editForm.content.replace(/<[^>]*>/g, '')}`
  const blob = new Blob([content], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `第${editForm.chapter_number}章-${editForm.title}.txt`
  a.click()
  URL.revokeObjectURL(url)
}

const showVersionHistory = () => {
  ElMessage.info('版本历史功能开发中...')
}

const deleteChapter = async () => {
  try {
    await ElMessageBox.confirm('确定要删除这个章节吗？', '确认删除', {
      type: 'warning'
    })
    
    if (props.chapter?.id) {
      await chaptersApi.deleteChapter(props.chapter.id)
      ElMessage.success('章节删除成功')
      emit('deleted', props.chapter)
    }
    
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除章节失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

const insertCharacterInfo = (character) => {
  const info = `【${character.name}】${character.personality ? ` - ${character.personality}` : ''}`
  insertTextAtCursor(info)
}

const insertTemplate = (type) => {
  const templates = {
    dialogue: '\n"对话内容，" 角色说道，"继续对话。"\n',
    scene: '\n【场景描述】这里描述环境、氛围和视觉细节。\n',
    action: '\n【动作场面】人物进行了什么动作，产生了什么结果。\n'
  }
  
  insertTextAtCursor(templates[type] || '')
}

const insertTextAtCursor = (text) => {
  const editor = editorRef.value
  if (editor) {
    const currentContent = editForm.content
    editForm.content = currentContent + text
    markChanged()
  }
}

const saveSettings = () => {
  localStorage.setItem('chapterEditorSettings', JSON.stringify(settingsForm))
  showSettings.value = false
  ElMessage.success('设置已保存')
}

const loadSettings = () => {
  const saved = localStorage.getItem('chapterEditorSettings')
  if (saved) {
    Object.assign(settingsForm, JSON.parse(saved))
  }
}

const updateWritingTime = () => {
  const elapsed = Date.now() - startTime.value
  const minutes = Math.floor(elapsed / 60000)
  const hours = Math.floor(minutes / 60)
  
  if (hours > 0) {
    writingTime.value = `${hours}小时${minutes % 60}分钟`
  } else {
    writingTime.value = `${minutes}分钟`
  }
}

const getStatusColor = (status) => {
  const colors = {
    draft: 'info',
    completed: 'success',
    published: 'warning'
  }
  return colors[status] || 'info'
}

const getStatusLabel = (status) => {
  const labels = {
    draft: '草稿',
    completed: '已完成',
    published: '已发布'
  }
  return labels[status] || status
}

const formatTime = (time) => {
  if (!time) return ''
  return new Date(time).toLocaleString()
}

// 监听器
watch(() => props.chapter, () => {
  loadChapter()
}, { immediate: true })

// 页面离开前确认
const beforeUnloadHandler = (e) => {
  if (hasChanges.value) {
    const message = '您有未保存的更改，确定要离开吗？'
    e.returnValue = message
    return message
  }
}

// 生命周期
onMounted(() => {
  loadSettings()
  loadChapter()
  
  // 添加页面离开前确认
  window.addEventListener('beforeunload', beforeUnloadHandler)
  
  // 定时更新写作时间
  const timer = setInterval(updateWritingTime, 60000)
  
  onUnmounted(() => {
    clearInterval(timer)
    window.removeEventListener('beforeunload', beforeUnloadHandler)
  })
})
</script>

<style scoped>
.chapter-editor {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #fff;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e4e7ed;
  background: #fafafa;
}

.header-left {
  flex: 1;
}

.chapter-info h2 {
  margin: 0 0 8px 0;
  font-size: 20px;
  font-weight: 500;
  color: #303133;
}

.chapter-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
  color: #606266;
}

.version {
  color: #909399;
}

.word-count {
  font-weight: 500;
  color: #409eff;
}

.update-time {
  color: #c0c4cc;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.editor-body {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.editor-sidebar {
  width: 320px;
  border-right: 1px solid #e4e7ed;
  background: #fafafa;
}

.editor-main {
  flex: 1;
  overflow: hidden;
}

.info-section {
  padding: 16px;
}

.assistant-section {
  padding: 16px;
}

.assistant-item {
  margin-bottom: 24px;
}

.assistant-item h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 500;
  color: #606266;
}

.character-cards {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.character-card {
  padding: 12px;
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.character-card:hover {
  border-color: #409eff;
  background: #f0f9ff;
}

.character-name {
  font-weight: 500;
  margin-bottom: 4px;
}

.character-desc {
  font-size: 12px;
  color: #909399;
  line-height: 1.4;
}

.outline-info {
  background: white;
  padding: 12px;
  border-radius: 6px;
  border: 1px solid #e4e7ed;
}

.outline-info p {
  margin: 0 0 8px 0;
  font-size: 13px;
  line-height: 1.5;
}

.outline-info p:last-child {
  margin-bottom: 0;
}

.quick-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.stats-section {
  padding: 16px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.stat-item:last-child {
  border-bottom: none;
}

.stat-label {
  font-size: 14px;
  color: #606266;
}

.stat-value {
  font-weight: 500;
  color: #303133;
}

.preview-content {
  max-height: 70vh;
  overflow-y: auto;
  padding: 20px;
  line-height: 1.8;
  font-size: 16px;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .editor-sidebar {
    width: 280px;
  }
}

@media (max-width: 768px) {
  .editor-header {
    flex-direction: column;
    gap: 12px;
    padding: 12px 16px;
  }
  
  .editor-body {
    flex-direction: column;
  }
  
  .editor-sidebar {
    width: 100%;
    height: 200px;
    border-right: none;
    border-bottom: 1px solid #e4e7ed;
  }
}
</style>