<template>
  <el-card class="novel-info-card" shadow="hover">
    <div class="novel-main-info">
      <!-- 封面区域 -->
      <div class="cover-section">
        <div 
          v-if="novel.cover_image" 
          class="cover-image"
          @click="handleCoverClick"
        >
          <img :src="novel.cover_image" :alt="novel.title" />
          <div class="cover-overlay">
            <el-icon class="upload-icon"><Upload /></el-icon>
            <span>更换封面</span>
          </div>
        </div>
        <div 
          v-else 
          class="cover-placeholder"
          @click="handleCoverClick"
        >
          <el-icon class="placeholder-icon"><Picture /></el-icon>
          <span class="placeholder-text">点击上传封面</span>
        </div>
        
        <!-- 隐藏的文件输入 -->
        <input
          ref="fileInput"
          type="file"
          accept="image/*"
          style="display: none"
          @change="handleFileChange"
        />
      </div>

      <!-- 信息区域 -->
      <div class="info-section">
        <!-- 标题行 -->
        <div class="title-section">
          <div v-if="!editing" class="title-display">
            <h1 class="novel-title">{{ novel.title }}</h1>
            <el-button 
              v-if="canEdit"
              type="text" 
              :icon="Edit" 
              @click="handleEditTitle"
              class="edit-title-btn"
            >
              编辑
            </el-button>
          </div>
          <div v-else class="title-edit">
            <el-input
              v-model="editData.title"
              placeholder="请输入小说标题"
              class="title-input"
              @keyup.enter="handleSaveTitle"
              @keyup.esc="handleCancelEdit"
            />
            <div class="edit-actions">
              <el-button size="small" @click="handleCancelEdit">取消</el-button>
              <el-button size="small" type="primary" @click="handleSaveTitle">保存</el-button>
            </div>
          </div>
        </div>

        <!-- 元信息 -->
        <div class="meta-info">
          <div class="meta-item">
            <span class="label">作者：</span>
            <span class="value">{{ novel.author }}</span>
          </div>
          <div class="meta-item">
            <span class="label">类型：</span>
            <el-tag size="small" class="genre-tag">
              {{ NovelUtils.getGenreText(novel.genre) }}
            </el-tag>
          </div>
          <div class="meta-item">
            <span class="label">状态：</span>
            <el-tag 
              size="small" 
              :type="getStatusTagType(novel.status)"
              :color="NovelUtils.getStatusColor(novel.status)"
            >
              {{ NovelUtils.getStatusText(novel.status) }}
            </el-tag>
          </div>
          <div class="meta-item">
            <span class="label">创建时间：</span>
            <span class="value">{{ NovelUtils.formatDate(novel.created_at) }}</span>
          </div>
          <div v-if="novel.last_edit_date" class="meta-item">
            <span class="label">最后编辑：</span>
            <span class="value">{{ NovelUtils.formatRelativeTime(novel.last_edit_date) }}</span>
          </div>
        </div>

        <!-- 简介 -->
        <div class="description-section">
          <div class="section-header">
            <h3>简介</h3>
            <el-button 
              v-if="canEdit && !editingDescription"
              type="text" 
              :icon="Edit" 
              @click="handleEditDescription"
              size="small"
            >
              编辑
            </el-button>
          </div>
          
          <div v-if="!editingDescription" class="description-display">
            <p v-if="novel.description" class="description-text">
              {{ novel.description }}
            </p>
            <p v-else class="no-description">
              暂无简介
            </p>
          </div>
          
          <div v-else class="description-edit">
            <el-input
              v-model="editData.description"
              type="textarea"
              :rows="4"
              placeholder="请输入小说简介"
              maxlength="1000"
              show-word-limit
            />
            <div class="edit-actions">
              <el-button size="small" @click="handleCancelDescriptionEdit">取消</el-button>
              <el-button size="small" type="primary" @click="handleSaveDescription">保存</el-button>
            </div>
          </div>
        </div>

        <!-- 标签 -->
        <div class="tags-section">
          <div class="section-header">
            <h3>标签</h3>
            <el-button 
              v-if="canEdit && !editingTags"
              type="text" 
              :icon="Edit" 
              @click="handleEditTags"
              size="small"
            >
              编辑
            </el-button>
          </div>
          
          <div v-if="!editingTags" class="tags-display">
            <el-tag
              v-for="tag in novel.tags"
              :key="tag"
              size="small"
              class="tag-item"
            >
              {{ tag }}
            </el-tag>
            <span v-if="!novel.tags?.length" class="no-tags">暂无标签</span>
          </div>
          
          <div v-else class="tags-edit">
            <el-tag
              v-for="(tag, index) in editData.tags"
              :key="tag"
              closable
              size="small"
              class="tag-item"
              @close="removeTag(index)"
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
            <div class="edit-actions">
              <el-button size="small" @click="handleCancelTagsEdit">取消</el-button>
              <el-button size="small" type="primary" @click="handleSaveTags">保存</el-button>
            </div>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="action-buttons">
          <el-button 
            type="primary" 
            size="large"
            :icon="Notebook"
            @click="$emit('enter-workspace')"
          >
            进入工作台
          </el-button>
          
          <el-dropdown @command="handleMenuCommand">
            <el-button size="large" :icon="More">
              更多操作
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="settings" :icon="Setting">
                  小说设置
                </el-dropdown-item>
                <el-dropdown-item command="share" :icon="Share">
                  分享小说
                </el-dropdown-item>
                <el-dropdown-item command="export" :icon="Download">
                  导出小说
                </el-dropdown-item>
                <el-dropdown-item divided command="delete" :icon="Delete" class="danger-item">
                  删除小说
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { ref, reactive, computed, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Edit, 
  Upload, 
  Picture, 
  Notebook, 
  More, 
  Setting, 
  Share, 
  Download, 
  Delete 
} from '@element-plus/icons-vue'
import { NovelUtils, type NovelDetailResponse } from '@/api/novels'

interface Props {
  novel: NovelDetailResponse
  editing?: boolean
  canEdit?: boolean
}

interface Emits {
  (e: 'edit', field: string): void
  (e: 'save', field: string, data: any): void
  (e: 'cancel', field: string): void
  (e: 'enter-workspace'): void
  (e: 'open-settings'): void
  (e: 'upload-cover', file: File): void
}

const props = withDefaults(defineProps<Props>(), {
  editing: false,
  canEdit: true
})

const emit = defineEmits<Emits>()

// 响应式数据
const editing = ref(false)
const editingDescription = ref(false)
const editingTags = ref(false)

const editData = reactive({
  title: '',
  description: '',
  tags: [] as string[]
})

// 标签编辑相关
const inputVisible = ref(false)
const inputValue = ref('')
const inputRef = ref()
const fileInput = ref()

// 计算属性
const getStatusTagType = (status: string) => {
  const typeMap: Record<string, string> = {
    'draft': 'info',
    'ongoing': 'warning', 
    'completed': 'success',
    'paused': 'danger'
  }
  return typeMap[status] || 'info'
}

// 方法定义
const handleCoverClick = () => {
  if (props.canEdit) {
    fileInput.value?.click()
  }
}

const handleFileChange = (event: Event) => {
  const file = (event.target as HTMLInputElement).files?.[0]
  if (file) {
    // 验证文件类型和大小
    if (!file.type.startsWith('image/')) {
      ElMessage.error('请选择图片文件')
      return
    }
    
    if (file.size > 5 * 1024 * 1024) {
      ElMessage.error('图片大小不能超过5MB')
      return
    }
    
    emit('upload-cover', file)
  }
  
  // 清空input值，允许重复选择同一文件
  ;(event.target as HTMLInputElement).value = ''
}

const handleEditTitle = () => {
  editData.title = props.novel.title
  editing.value = true
}

const handleSaveTitle = () => {
  if (!editData.title.trim()) {
    ElMessage.warning('标题不能为空')
    return
  }
  
  emit('save', 'title', { title: editData.title.trim() })
  editing.value = false
}

const handleCancelEdit = () => {
  editing.value = false
  editData.title = ''
}

const handleEditDescription = () => {
  editData.description = props.novel.description || ''
  editingDescription.value = true
}

const handleSaveDescription = () => {
  emit('save', 'description', { description: editData.description })
  editingDescription.value = false
}

const handleCancelDescriptionEdit = () => {
  editingDescription.value = false
  editData.description = ''
}

const handleEditTags = () => {
  editData.tags = [...(props.novel.tags || [])]
  editingTags.value = true
}

const handleSaveTags = () => {
  emit('save', 'tags', { tags: editData.tags })
  editingTags.value = false
}

const handleCancelTagsEdit = () => {
  editingTags.value = false
  editData.tags = []
  inputVisible.value = false
  inputValue.value = ''
}

const removeTag = (index: number) => {
  editData.tags.splice(index, 1)
}

const showInput = () => {
  inputVisible.value = true
  nextTick(() => {
    inputRef.value?.focus()
  })
}

const handleInputConfirm = () => {
  const value = inputValue.value.trim()
  if (value && !editData.tags.includes(value)) {
    editData.tags.push(value)
  }
  inputVisible.value = false
  inputValue.value = ''
}

const handleMenuCommand = (command: string) => {
  switch (command) {
    case 'settings':
      emit('open-settings')
      break
    case 'share':
      // TODO: 实现分享功能
      ElMessage.info('分享功能开发中')
      break
    case 'export':
      // TODO: 实现导出功能
      ElMessage.info('导出功能开发中')
      break
    case 'delete':
      handleDeleteNovel()
      break
  }
}

const handleDeleteNovel = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要删除小说《${props.novel.title}》吗？此操作不可恢复！`,
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }
    )
    
    // 二次确认
    const { value: inputTitle } = await ElMessageBox.prompt(
      '请输入小说标题以确认删除：',
      '二次确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        inputPattern: new RegExp(`^${props.novel.title}$`),
        inputErrorMessage: '标题不匹配'
      }
    )
    
    if (inputTitle === props.novel.title) {
      // TODO: 调用删除API
      ElMessage.success('删除成功')
    }
    
  } catch (error) {
    // 用户取消删除
  }
}
</script>

<style scoped lang="scss">
.novel-info-card {
  margin-bottom: 24px;
  
  :deep(.el-card__body) {
    padding: 24px;
  }
}

.novel-main-info {
  display: flex;
  gap: 24px;
  
  @media (max-width: 768px) {
    flex-direction: column;
    gap: 16px;
  }
}

.cover-section {
  flex-shrink: 0;
  width: 200px;
  height: 280px;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  
  @media (max-width: 768px) {
    width: 120px;
    height: 168px;
    align-self: center;
  }
  
  .cover-image {
    position: relative;
    width: 100%;
    height: 100%;
    
    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
    
    .cover-overlay {
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0, 0, 0, 0.6);
      color: white;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      opacity: 0;
      transition: opacity 0.3s;
      
      .upload-icon {
        font-size: 24px;
        margin-bottom: 8px;
      }
    }
    
    &:hover .cover-overlay {
      opacity: 1;
    }
  }
  
  .cover-placeholder {
    width: 100%;
    height: 100%;
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: #8c939d;
    transition: all 0.3s;
    
    .placeholder-icon {
      font-size: 48px;
      margin-bottom: 8px;
    }
    
    .placeholder-text {
      font-size: 14px;
    }
    
    &:hover {
      background: linear-gradient(135deg, #e3e7ed 0%, #b5c6d9 100%);
      color: #606266;
    }
  }
}

.info-section {
  flex: 1;
  min-width: 0;
}

.title-section {
  margin-bottom: 16px;
  
  .title-display {
    display: flex;
    align-items: center;
    gap: 12px;
    
    .novel-title {
      font-size: 28px;
      font-weight: 600;
      color: #303133;
      margin: 0;
      word-break: break-word;
      
      @media (max-width: 768px) {
        font-size: 24px;
      }
    }
    
    .edit-title-btn {
      flex-shrink: 0;
    }
  }
  
  .title-edit {
    .title-input {
      margin-bottom: 12px;
      
      :deep(.el-input__inner) {
        font-size: 24px;
        font-weight: 600;
      }
    }
    
    .edit-actions {
      display: flex;
      gap: 8px;
    }
  }
}

.meta-info {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 20px;
  
  @media (max-width: 768px) {
    flex-direction: column;
    gap: 8px;
  }
  
  .meta-item {
    display: flex;
    align-items: center;
    gap: 4px;
    
    .label {
      font-weight: 500;
      color: #606266;
    }
    
    .value {
      color: #303133;
    }
  }
}

.description-section,
.tags-section {
  margin-bottom: 20px;
  
  .section-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 12px;
    
    h3 {
      font-size: 16px;
      font-weight: 600;
      color: #303133;
      margin: 0;
    }
  }
  
  .description-display {
    .description-text {
      line-height: 1.6;
      color: #606266;
      margin: 0;
    }
    
    .no-description {
      color: #c0c4cc;
      font-style: italic;
      margin: 0;
    }
  }
  
  .description-edit {
    .edit-actions {
      display: flex;
      gap: 8px;
      margin-top: 12px;
    }
  }
}

.tags-display {
  .tag-item {
    margin-right: 8px;
    margin-bottom: 8px;
  }
  
  .no-tags {
    color: #c0c4cc;
    font-style: italic;
  }
}

.tags-edit {
  .tag-item {
    margin-right: 8px;
    margin-bottom: 8px;
  }
  
  .edit-actions {
    display: flex;
    gap: 8px;
    margin-top: 12px;
  }
}

.action-buttons {
  display: flex;
  gap: 12px;
  margin-top: 24px;
  
  @media (max-width: 768px) {
    flex-direction: column;
  }
}

.genre-tag {
  background-color: #f0f9ff;
  color: #409eff;
  border: 1px solid #b3d8ff;
}

:deep(.danger-item) {
  color: #f56c6c;
}
</style>