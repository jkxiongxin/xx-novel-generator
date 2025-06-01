<template>
  <div class="chapters-workspace">
    <!-- 顶部工具栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <div class="novel-info">
          <h2>{{ novelTitle }}</h2>
          <div class="stats-summary" v-if="stats">
            <el-tag type="info">{{ stats.total_chapters }} 章</el-tag>
            <el-tag type="success">{{ stats.total_words.toLocaleString() }} 字</el-tag>
            <el-tag type="warning">{{ stats.average_words }} 字/章</el-tag>
          </div>
        </div>
      </div>
      
      <div class="toolbar-right">
        <el-button-group>
          <el-button type="primary" @click="createChapter">
            <el-icon><plus /></el-icon>
            新建章节
          </el-button>
          <el-button @click="showAIGenerator">
            <el-icon><magic-stick /></el-icon>
            AI生成
          </el-button>
          <el-button @click="showImportDialog">
            <el-icon><upload /></el-icon>
            导入章节
          </el-button>
        </el-button-group>
        
        <el-dropdown @command="handleToolbarAction">
          <el-button>
            更多工具<el-icon class="el-icon--right"><arrow-down /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="export-all">导出全部章节</el-dropdown-item>
              <el-dropdown-item command="batch-edit">批量编辑</el-dropdown-item>
              <el-dropdown-item command="reorganize">章节重排</el-dropdown-item>
              <el-dropdown-item command="statistics">统计报告</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>
    
    <!-- 视图切换 -->
    <div class="view-tabs">
      <el-tabs v-model="currentView" @tab-change="handleViewChange">
        <el-tab-pane label="列表视图" name="list">
          <template #label>
            <span><el-icon><list /></el-icon> 列表视图</span>
          </template>
        </el-tab-pane>
        <el-tab-pane label="编辑器" name="editor">
          <template #label>
            <span><el-icon><edit /></el-icon> 编辑器</span>
          </template>
        </el-tab-pane>
        <el-tab-pane label="大纲视图" name="outline">
          <template #label>
            <span><el-icon><document /></el-icon> 大纲视图</span>
          </template>
        </el-tab-pane>
      </el-tabs>
    </div>
    
    <!-- 主体内容 -->
    <div class="workspace-content">
      <!-- 列表视图 -->
      <div v-show="currentView === 'list'" class="list-view">
        <div class="content-layout">
          <div class="left-panel">
            <ChapterList
              ref="chapterListRef"
              :novel-id="novelId"
              :stats="stats"
              @chapter-selected="selectChapter"
              @create-chapter="createChapter"
              @edit-chapter="editChapter"
              @refresh-stats="loadStats"
            />
          </div>
          
          <div class="right-panel" v-if="selectedChapter">
            <div class="chapter-preview">
              <div class="preview-header">
                <h3>第{{ selectedChapter.chapter_number }}章: {{ selectedChapter.title }}</h3>
                <div class="preview-actions">
                  <el-button size="small" @click="editChapter(selectedChapter)">
                    编辑
                  </el-button>
                  <el-button size="small" @click="quickEdit(selectedChapter)">
                    快速编辑
                  </el-button>
                </div>
              </div>
              
              <div class="preview-meta">
                <el-descriptions :column="2" size="small" border>
                  <el-descriptions-item label="状态">
                    <el-tag :type="getStatusColor(selectedChapter.status)">
                      {{ getStatusLabel(selectedChapter.status) }}
                    </el-tag>
                  </el-descriptions-item>
                  <el-descriptions-item label="字数">
                    {{ selectedChapter.word_count.toLocaleString() }}
                  </el-descriptions-item>
                  <el-descriptions-item label="版本">
                    v{{ selectedChapter.version }}
                  </el-descriptions-item>
                  <el-descriptions-item label="更新时间">
                    {{ formatTime(selectedChapter.updated_at) }}
                  </el-descriptions-item>
                </el-descriptions>
              </div>
              
              <div class="preview-content" v-loading="loadingChapter">
                <div v-if="chapterContent" v-html="chapterContent" class="content-display"></div>
                <el-empty v-else description="点击章节查看内容" />
              </div>
            </div>
          </div>
          
          <div class="right-panel empty-state" v-else>
            <el-empty description="请选择一个章节查看详情">
              <el-button type="primary" @click="createChapter">创建第一个章节</el-button>
            </el-empty>
          </div>
        </div>
      </div>
      
      <!-- 编辑器视图 -->
      <div v-show="currentView === 'editor'" class="editor-view">
        <ChapterEditor
          ref="chapterEditorRef"
          :chapter="editingChapter"
          :novel-id="novelId"
          :characters="characters"
          :outlines="outlines"
          @saved="handleChapterSaved"
          @deleted="handleChapterDeleted"
          @status-changed="handleStatusChanged"
        />
      </div>
      
      <!-- 大纲视图 -->
      <div v-show="currentView === 'outline'" class="outline-view">
        <div class="outline-container">
          <div class="outline-sidebar">
            <h3>章节大纲</h3>
            <div class="outline-list">
              <div
                v-for="chapter in chapters"
                :key="chapter.id"
                class="outline-item"
                :class="{ active: selectedOutlineChapter?.id === chapter.id }"
                @click="selectOutlineChapter(chapter)"
              >
                <div class="outline-number">{{ chapter.chapter_number }}</div>
                <div class="outline-content">
                  <div class="outline-title">{{ chapter.title }}</div>
                  <div class="outline-meta">
                    <span>{{ chapter.word_count }} 字</span>
                    <el-tag :type="getStatusColor(chapter.status)" size="small">
                      {{ getStatusLabel(chapter.status) }}
                    </el-tag>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div class="outline-main">
            <div v-if="selectedOutlineChapter" class="outline-detail">
              <h2>第{{ selectedOutlineChapter.chapter_number }}章: {{ selectedOutlineChapter.title }}</h2>
              
              <div class="outline-summary">
                <el-card>
                  <template #header>
                    <span>章节概要</span>
                  </template>
                  <div class="summary-content">
                    <p v-if="selectedOutlineChapter.notes">{{ selectedOutlineChapter.notes }}</p>
                    <p v-else class="no-summary">暂无章节概要</p>
                    <el-button size="small" @click="editSummary">编辑概要</el-button>
                  </div>
                </el-card>
              </div>
              
              <div class="outline-structure">
                <el-row :gutter="20">
                  <el-col :span="12">
                    <el-card>
                      <template #header>
                        <span>相关角色</span>
                      </template>
                      <div class="related-characters">
                        <el-tag
                          v-for="characterId in selectedOutlineChapter.character_ids"
                          :key="characterId"
                          style="margin: 4px;"
                        >
                          {{ getCharacterName(characterId) }}
                        </el-tag>
                        <div v-if="selectedOutlineChapter.character_ids.length === 0" class="empty-hint">
                          暂无相关角色
                        </div>
                      </div>
                    </el-card>
                  </el-col>
                  
                  <el-col :span="12">
                    <el-card>
                      <template #header>
                        <span>章节统计</span>
                      </template>
                      <div class="chapter-stats">
                        <div class="stat-row">
                          <span class="stat-label">字数:</span>
                          <span class="stat-value">{{ selectedOutlineChapter.word_count.toLocaleString() }}</span>
                        </div>
                        <div class="stat-row">
                          <span class="stat-label">版本:</span>
                          <span class="stat-value">v{{ selectedOutlineChapter.version }}</span>
                        </div>
                        <div class="stat-row">
                          <span class="stat-label">状态:</span>
                          <el-tag :type="getStatusColor(selectedOutlineChapter.status)" size="small">
                            {{ getStatusLabel(selectedOutlineChapter.status) }}
                          </el-tag>
                        </div>
                      </div>
                    </el-card>
                  </el-col>
                </el-row>
              </div>
            </div>
            
            <div v-else class="outline-empty">
              <el-empty description="请选择一个章节查看大纲" />
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- AI生成对话框 -->
    <ChapterAIGenerator
      ref="aiGeneratorRef"
      :novel-id="novelId"
      :characters="characters"
      :outlines="outlines"
      :existing-chapters="chapters"
      @generated="handleAIGenerated"
    />
    
    <!-- 快速编辑对话框 -->
    <el-dialog v-model="showQuickEdit" title="快速编辑" width="600px">
      <el-form :model="quickEditForm" label-width="80px">
        <el-form-item label="章节标题">
          <el-input v-model="quickEditForm.title" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="quickEditForm.status" style="width: 100%;">
            <el-option label="草稿" value="draft" />
            <el-option label="已完成" value="completed" />
            <el-option label="已发布" value="published" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="quickEditForm.notes" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showQuickEdit = false">取消</el-button>
        <el-button type="primary" @click="saveQuickEdit" :loading="quickSaving">
          保存
        </el-button>
      </template>
    </el-dialog>
    
    <!-- 导入对话框 -->
    <el-dialog v-model="showImport" title="导入章节" width="500px">
      <div class="import-section">
        <el-upload
          class="upload-demo"
          drag
          :auto-upload="false"
          :on-change="handleFileChange"
          accept=".txt,.md"
        >
          <el-icon class="el-icon--upload"><upload-filled /></el-icon>
          <div class="el-upload__text">
            将文件拖到此处，或<em>点击上传</em>
          </div>
          <template #tip>
            <div class="el-upload__tip">
              支持 .txt 和 .md 格式的文本文件
            </div>
          </template>
        </el-upload>
      </div>
      
      <template #footer>
        <el-button @click="showImport = false">取消</el-button>
        <el-button type="primary" @click="importChapters" :loading="importing">
          导入
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, MagicStick, Upload, ArrowDown, List, Edit, Document, UploadFilled
} from '@element-plus/icons-vue'
import ChapterList from '@/components/chapters/ChapterList.vue'
import ChapterEditor from '@/components/chapters/ChapterEditor.vue'
import ChapterAIGenerator from '@/components/chapters/ChapterAIGenerator.vue'
import * as chaptersApi from '@/api/chapters'
import * as charactersApi from '@/api/characters'
import * as outlineApi from '@/api/outline'

// 路由参数
const route = useRoute()
const novelId = computed(() => parseInt(route.params.novelId))

// 响应式数据
const currentView = ref('list')
const chapters = ref([])
const characters = ref([])
const outlines = ref([])
const selectedChapter = ref(null)
const editingChapter = ref(null)
const selectedOutlineChapter = ref(null)
const chapterContent = ref('')
const loadingChapter = ref(false)
const stats = ref(null)
const novelTitle = ref('小说章节管理')

// 对话框状态
const showQuickEdit = ref(false)
const showImport = ref(false)
const quickSaving = ref(false)
const importing = ref(false)

// 表单数据
const quickEditForm = reactive({
  title: '',
  status: 'draft',
  notes: ''
})

const importFiles = ref([])

// 组件引用
const chapterListRef = ref(null)
const chapterEditorRef = ref(null)
const aiGeneratorRef = ref(null)

// 方法
const loadChapters = async () => {
  try {
    const data = await chaptersApi.getChapters({
      novel_id: novelId.value,
      page: 1,
      size: 1000,
      sort_by: 'chapter_number',
      sort_order: 'asc'
    })
    chapters.value = data.items || []
  } catch (error) {
    console.error('加载章节列表失败:', error)
    ElMessage.error('加载章节列表失败')
  }
}

const loadCharacters = async () => {
  try {
    const data = await charactersApi.getCharacters({
      novel_id: novelId.value,
      page: 1,
      page_size: 1000
    })
    characters.value = data.items || []
  } catch (error) {
    console.error('加载角色列表失败:', error)
  }
}

const loadOutlines = async () => {
  try {
    const data = await outlineApi.getDetailedOutlines({
      novel_id: novelId.value,
      page: 1,
      page_size: 1000
    })
    outlines.value = data.items || []
  } catch (error) {
    console.error('加载大纲列表失败:', error)
  }
}

const loadStats = async () => {
  try {
    stats.value = await chaptersApi.getChapterStats(novelId.value)
  } catch (error) {
    console.error('加载统计信息失败:', error)
  }
}

const selectChapter = async (chapter) => {
  selectedChapter.value = chapter
  
  if (currentView.value === 'list') {
    await loadChapterContent(chapter.id)
  }
}

const loadChapterContent = async (chapterId) => {
  try {
    loadingChapter.value = true
    const chapter = await chaptersApi.getChapter(chapterId)
    chapterContent.value = chapter.content || ''
  } catch (error) {
    console.error('加载章节内容失败:', error)
    chapterContent.value = ''
  } finally {
    loadingChapter.value = false
  }
}

const createChapter = () => {
  editingChapter.value = null
  currentView.value = 'editor'
}

const editChapter = (chapter) => {
  editingChapter.value = chapter
  currentView.value = 'editor'
}

const quickEdit = (chapter) => {
  Object.assign(quickEditForm, {
    title: chapter.title,
    status: chapter.status,
    notes: chapter.notes || ''
  })
  showQuickEdit.value = true
}

const saveQuickEdit = async () => {
  try {
    quickSaving.value = true
    await chaptersApi.updateChapter(selectedChapter.value.id, quickEditForm)
    
    ElMessage.success('更新成功')
    showQuickEdit.value = false
    
    // 刷新数据
    await Promise.all([
      loadChapters(),
      loadStats(),
      chapterListRef.value?.loadChapters()
    ])
    
  } catch (error) {
    console.error('快速编辑失败:', error)
    ElMessage.error('更新失败')
  } finally {
    quickSaving.value = false
  }
}

const selectOutlineChapter = (chapter) => {
  selectedOutlineChapter.value = chapter
}

const handleViewChange = (viewName) => {
  currentView.value = viewName
  
  if (viewName === 'outline' && chapters.value.length > 0) {
    selectedOutlineChapter.value = chapters.value[0]
  }
}

const handleChapterSaved = async (chapter) => {
  editingChapter.value = chapter
  selectedChapter.value = chapter
  
  // 刷新数据
  await Promise.all([
    loadChapters(),
    loadStats(),
    chapterListRef.value?.loadChapters()
  ])
  
  ElMessage.success('章节保存成功')
}

const handleChapterDeleted = async (chapter) => {
  editingChapter.value = null
  selectedChapter.value = null
  currentView.value = 'list'
  
  // 刷新数据
  await Promise.all([
    loadChapters(),
    loadStats(),
    chapterListRef.value?.loadChapters()
  ])
}

const handleStatusChanged = async () => {
  await Promise.all([
    loadChapters(),
    loadStats(),
    chapterListRef.value?.loadChapters()
  ])
}

const showAIGenerator = () => {
  aiGeneratorRef.value?.show()
}

const handleAIGenerated = async (chapter) => {
  // 刷新数据
  await Promise.all([
    loadChapters(),
    loadStats(),
    chapterListRef.value?.loadChapters()
  ])
  
  // 切换到编辑视图
  editingChapter.value = chapter
  currentView.value = 'editor'
}

const showImportDialog = () => {
  showImport.value = true
  importFiles.value = []
}

const handleFileChange = (file) => {
  importFiles.value = [file]
}

const importChapters = async () => {
  if (importFiles.value.length === 0) {
    ElMessage.warning('请选择要导入的文件')
    return
  }
  
  try {
    importing.value = true
    
    const file = importFiles.value[0].raw
    const content = await file.text()
    
    // 简单的文本分割逻辑（可以根据需要改进）
    const chapters = content.split(/第\s*\d+\s*章/).filter(Boolean)
    
    for (let i = 0; i < chapters.length; i++) {
      const chapterContent = chapters[i].trim()
      const titleMatch = chapterContent.match(/^(.+?)(?:\n|\r\n)/)
      const title = titleMatch ? titleMatch[1].trim() : `导入章节 ${i + 1}`
      const content = chapterContent.replace(/^.+?(?:\n|\r\n)/, '').trim()
      
      await chaptersApi.createChapter({
        novel_id: novelId.value,
        title,
        content,
        chapter_number: chapters.value.length + i + 1,
        status: 'draft',
        notes: '从文件导入'
      })
    }
    
    ElMessage.success(`成功导入 ${chapters.length} 个章节`)
    showImport.value = false
    
    // 刷新数据
    await Promise.all([
      loadChapters(),
      loadStats(),
      chapterListRef.value?.loadChapters()
    ])
    
  } catch (error) {
    console.error('导入失败:', error)
    ElMessage.error('导入失败，请检查文件格式')
  } finally {
    importing.value = false
  }
}

const handleToolbarAction = (command) => {
  switch (command) {
    case 'export-all':
      exportAllChapters()
      break
    case 'batch-edit':
      ElMessage.info('批量编辑功能开发中...')
      break
    case 'reorganize':
      ElMessage.info('章节重排功能开发中...')
      break
    case 'statistics':
      ElMessage.info('统计报告功能开发中...')
      break
  }
}

const exportAllChapters = async () => {
  try {
    if (chapters.value.length === 0) {
      ElMessage.warning('暂无章节可导出')
      return
    }
    
    let content = `${novelTitle.value}\n\n`
    
    for (const chapter of chapters.value) {
      const fullChapter = await chaptersApi.getChapter(chapter.id)
      content += `第${chapter.chapter_number}章: ${chapter.title}\n\n`
      content += fullChapter.content.replace(/<[^>]*>/g, '') + '\n\n'
    }
    
    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${novelTitle.value}-全部章节.txt`
    a.click()
    URL.revokeObjectURL(url)
    
    ElMessage.success('导出成功')
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败')
  }
}

const editSummary = () => {
  ElMessage.info('编辑概要功能开发中...')
}

const getCharacterName = (characterId) => {
  const character = characters.value.find(c => c.id === characterId)
  return character ? character.name : '未知角色'
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
watch(novelId, () => {
  if (novelId.value) {
    loadData()
  }
})

// 数据加载
const loadData = async () => {
  await Promise.all([
    loadChapters(),
    loadCharacters(),
    loadOutlines(),
    loadStats()
  ])
}

// 生命周期
onMounted(() => {
  if (novelId.value) {
    loadData()
  }
})
</script>

<style scoped>
.chapters-workspace {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f5f5;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: white;
  border-bottom: 1px solid #e4e7ed;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.toolbar-left {
  flex: 1;
}

.novel-info h2 {
  margin: 0 0 8px 0;
  font-size: 20px;
  font-weight: 500;
  color: #303133;
}

.stats-summary {
  display: flex;
  gap: 8px;
}

.toolbar-right {
  display: flex;
  gap: 12px;
}

.view-tabs {
  background: white;
  border-bottom: 1px solid #e4e7ed;
}

.view-tabs :deep(.el-tabs__header) {
  margin: 0;
  padding: 0 20px;
}

.view-tabs :deep(.el-tabs__item) {
  padding: 0 20px;
  height: 48px;
  line-height: 48px;
}

.workspace-content {
  flex: 1;
  overflow: hidden;
}

.list-view {
  height: 100%;
}

.content-layout {
  display: flex;
  height: 100%;
}

.left-panel {
  width: 400px;
  border-right: 1px solid #e4e7ed;
}

.right-panel {
  flex: 1;
  background: white;
  overflow: hidden;
}

.right-panel.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
}

.chapter-preview {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #e4e7ed;
  background: #fafafa;
}

.preview-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 500;
}

.preview-actions {
  display: flex;
  gap: 8px;
}

.preview-meta {
  padding: 16px 20px;
  border-bottom: 1px solid #e4e7ed;
}

.preview-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.content-display {
  line-height: 1.8;
  font-size: 16px;
  color: #303133;
}

.editor-view {
  height: 100%;
}

.outline-view {
  height: 100%;
  background: white;
}

.outline-container {
  display: flex;
  height: 100%;
}

.outline-sidebar {
  width: 300px;
  border-right: 1px solid #e4e7ed;
  background: #fafafa;
}

.outline-sidebar h3 {
  margin: 0;
  padding: 20px;
  font-size: 16px;
  font-weight: 500;
  border-bottom: 1px solid #e4e7ed;
}

.outline-list {
  overflow-y: auto;
  height: calc(100% - 60px);
}

.outline-item {
  display: flex;
  padding: 16px 20px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: all 0.2s;
}

.outline-item:hover {
  background: #f0f9ff;
}

.outline-item.active {
  background: #409eff;
  color: white;
}

.outline-number {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #e4e7ed;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 500;
  margin-right: 12px;
  flex-shrink: 0;
}

.outline-item.active .outline-number {
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

.outline-content {
  flex: 1;
  min-width: 0;
}

.outline-title {
  font-weight: 500;
  margin-bottom: 4px;
  word-break: break-all;
}

.outline-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #909399;
}

.outline-item.active .outline-meta {
  color: rgba(255, 255, 255, 0.8);
}

.outline-main {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.outline-detail h2 {
  margin: 0 0 20px 0;
  font-size: 24px;
  font-weight: 500;
}

.outline-summary {
  margin-bottom: 20px;
}

.summary-content {
  color: #606266;
  line-height: 1.6;
}

.no-summary {
  color: #c0c4cc;
  font-style: italic;
}

.outline-structure {
  margin-top: 20px;
}

.related-characters {
  min-height: 40px;
}

.empty-hint {
  color: #c0c4cc;
  font-style: italic;
}

.chapter-stats {
  font-size: 14px;
}

.stat-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.stat-row:last-child {
  margin-bottom: 0;
}

.stat-label {
  color: #606266;
}

.stat-value {
  font-weight: 500;
}

.outline-empty {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.import-section {
  margin: 20px 0;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .left-panel {
    width: 350px;
  }
  
  .outline-sidebar {
    width: 250px;
  }
}

@media (max-width: 768px) {
  .toolbar {
    flex-direction: column;
    gap: 12px;
    padding: 12px 16px;
  }
  
  .content-layout {
    flex-direction: column;
  }
  
  .left-panel {
    width: 100%;
    height: 300px;
    border-right: none;
    border-bottom: 1px solid #e4e7ed;
  }
  
  .outline-container {
    flex-direction: column;
  }
  
  .outline-sidebar {
    width: 100%;
    height: 200px;
    border-right: none;
    border-bottom: 1px solid #e4e7ed;
  }
}
</style>