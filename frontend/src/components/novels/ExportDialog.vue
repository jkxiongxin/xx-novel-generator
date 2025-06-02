<template>
  <el-dialog
    :model-value="visible"
    @update:model-value="$emit('update:visible', $event)"
    title="导出小说"
    width="500px"
    align-center
    :close-on-click-modal="false"
    :close-on-press-escape="false"
  >
    <div class="export-dialog-content">
      <!-- 小说信息 -->
      <div class="novel-info" v-if="novel">
        <div class="novel-header">
          <h3 class="novel-title">{{ novel.title }}</h3>
          <el-tag :type="getStatusTagType(novel.status)" size="small" effect="light">
            {{ NovelUtils.getStatusText(novel.status) }}
          </el-tag>
        </div>
        <div class="novel-stats">
          <span class="stat-item">{{ NovelUtils.formatWordCount(novel.word_count) }}</span>
          <span class="stat-item">{{ novel.chapter_count }} 章</span>
          <span class="stat-item">{{ NovelUtils.getGenreText(novel.genre) }}</span>
        </div>
      </div>

      <!-- 导出配置 -->
      <div class="export-config">
        <el-form :model="exportOptions" label-width="100px" label-position="left">
          <!-- 导出格式 -->
          <el-form-item label="导出格式" required>
            <el-radio-group v-model="exportOptions.format" class="format-group">
              <el-radio value="txt" class="format-option">
                <div class="format-item">
                  <el-icon><Document /></el-icon>
                  <div class="format-info">
                    <span class="format-name">TXT 文本</span>
                    <span class="format-desc">纯文本格式，体积小</span>
                  </div>
                </div>
              </el-radio>
              <el-radio value="docx" class="format-option">
                <div class="format-item">
                  <el-icon><Document /></el-icon>
                  <div class="format-info">
                    <span class="format-name">DOCX 文档</span>
                    <span class="format-desc">Word文档，支持格式</span>
                  </div>
                </div>
              </el-radio>
              <el-radio value="pdf" class="format-option">
                <div class="format-item">
                  <el-icon><Document /></el-icon>
                  <div class="format-info">
                    <span class="format-name">PDF 文档</span>
                    <span class="format-desc">便携文档，阅读友好</span>
                  </div>
                </div>
              </el-radio>
            </el-radio-group>
          </el-form-item>

          <!-- 包含内容 -->
          <el-form-item label="包含内容">
            <div class="content-options">
              <el-checkbox v-model="exportOptions.include_outline">
                <span class="option-label">
                  <el-icon><List /></el-icon>
                  包含大纲
                </span>
                <span class="option-desc">导出小说大纲信息</span>
              </el-checkbox>
              
              <el-checkbox v-model="exportOptions.include_worldview">
                <span class="option-label">
                  <el-icon><GlobeAltOutline /></el-icon>
                  包含世界观
                </span>
                <span class="option-desc">导出世界观设定</span>
              </el-checkbox>
              
              <el-checkbox v-model="exportOptions.include_characters">
                <span class="option-label">
                  <el-icon><User /></el-icon>
                  包含角色
                </span>
                <span class="option-desc">导出角色信息</span>
              </el-checkbox>
            </div>
          </el-form-item>

          <!-- 章节筛选 -->
          <el-form-item label="章节筛选">
            <div class="chapter-options">
              <el-radio-group v-model="chapterFilter" class="filter-group">
                <el-radio value="all">全部章节</el-radio>
                <el-radio value="completed">仅已完成章节</el-radio>
                <el-radio value="range">自定义范围</el-radio>
              </el-radio-group>
              
              <div v-if="chapterFilter === 'range'" class="range-input">
                <span class="range-label">章节范围：</span>
                <el-input-number
                  v-model="exportOptions.start_chapter"
                  :min="1"
                  :max="novel?.chapter_count || 1"
                  size="small"
                  style="width: 80px;"
                />
                <span class="range-separator">至</span>
                <el-input-number
                  v-model="exportOptions.end_chapter"
                  :min="exportOptions.start_chapter || 1"
                  :max="novel?.chapter_count || 1"
                  size="small"
                  style="width: 80px;"
                />
              </div>
            </div>
          </el-form-item>
        </el-form>
      </div>

      <!-- 预览信息 -->
      <div class="export-preview">
        <div class="preview-header">
          <el-icon><View /></el-icon>
          <span>导出预览</span>
        </div>
        <div class="preview-content">
          <div class="preview-item">
            <span class="preview-label">估计文件大小：</span>
            <span class="preview-value">{{ estimatedSize }}</span>
          </div>
          <div class="preview-item">
            <span class="preview-label">估计导出时间：</span>
            <span class="preview-value">{{ estimatedTime }}</span>
          </div>
        </div>
      </div>
    </div>

    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleCancel" :disabled="loading">取消</el-button>
        <el-button 
          type="primary" 
          @click="handleConfirm"
          :loading="loading"
          :disabled="!exportOptions.format"
        >
          <el-icon v-if="!loading"><Download /></el-icon>
          {{ loading ? '导出中...' : '开始导出' }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { 
  Document, List, User, View, Download 
} from '@element-plus/icons-vue'
import type { NovelListItem } from '@/api/novels'
import { NovelUtils } from '@/api/novels'

// 自定义图标组件（Element Plus 可能没有的图标）
const GlobeAltOutline = Document // 临时使用 Document 图标

// Props
interface Props {
  visible: boolean
  novel: NovelListItem | null
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  loading: false
})

// Emits
const emit = defineEmits<{
  'update:visible': [visible: boolean]
  'export': [options: any]
}>()

// 导出选项类型
interface ExportOptions {
  format: 'txt' | 'docx' | 'pdf'
  include_outline: boolean
  include_worldview: boolean
  include_characters: boolean
  start_chapter?: number
  end_chapter?: number
  only_completed?: boolean
}

// 响应式数据
const exportOptions = ref<ExportOptions>({
  format: 'txt',
  include_outline: false,
  include_worldview: false,
  include_characters: false,
  start_chapter: 1,
  end_chapter: 1
})

const chapterFilter = ref<'all' | 'completed' | 'range'>('all')

// 计算属性
const estimatedSize = computed(() => {
  if (!props.novel) return '0 KB'
  
  let baseSize = props.novel.word_count * 2 // 假设每个字符2字节
  
  if (exportOptions.value.include_outline) baseSize += 1024
  if (exportOptions.value.include_worldview) baseSize += 2048
  if (exportOptions.value.include_characters) baseSize += 1024
  
  // 根据格式调整大小
  switch (exportOptions.value.format) {
    case 'docx':
      baseSize *= 1.5
      break
    case 'pdf':
      baseSize *= 2
      break
  }
  
  if (baseSize < 1024) return `${Math.round(baseSize)} B`
  if (baseSize < 1024 * 1024) return `${Math.round(baseSize / 1024)} KB`
  return `${(baseSize / (1024 * 1024)).toFixed(1)} MB`
})

const estimatedTime = computed(() => {
  if (!props.novel) return '0 秒'
  
  const wordCount = props.novel.word_count
  let seconds = Math.max(1, Math.round(wordCount / 1000)) // 假设每秒处理1000字
  
  if (exportOptions.value.format === 'pdf') seconds *= 2
  
  if (seconds < 60) return `${seconds} 秒`
  const minutes = Math.round(seconds / 60)
  return `${minutes} 分钟`
})

// 监听小说变化，重置表单
watch(() => props.novel, (newNovel) => {
  if (newNovel) {
    exportOptions.value.end_chapter = newNovel.chapter_count
  }
})

watch(() => props.visible, (visible) => {
  if (visible && props.novel) {
    // 重置选项
    exportOptions.value = {
      format: 'txt',
      include_outline: false,
      include_worldview: false,
      include_characters: false,
      start_chapter: 1,
      end_chapter: props.novel.chapter_count
    }
    chapterFilter.value = 'all'
  }
})

// 监听章节筛选变化
watch(chapterFilter, (filter) => {
  if (filter === 'completed') {
    exportOptions.value.only_completed = true
  } else {
    exportOptions.value.only_completed = false
  }
})

// 方法
const getStatusTagType = (status: string): string => {
  const typeMap: Record<string, string> = {
    'draft': 'info',
    'ongoing': 'warning',
    'completed': 'success',
    'paused': 'danger'
  }
  return typeMap[status] || 'info'
}

const handleCancel = () => {
  emit('update:visible', false)
}

const handleConfirm = () => {
  const options: any = { ...exportOptions.value }
  
  // 根据章节筛选调整选项
  if (chapterFilter.value === 'all') {
    delete options.start_chapter
    delete options.end_chapter
  } else if (chapterFilter.value === 'completed') {
    options.only_completed = true
    delete options.start_chapter
    delete options.end_chapter
  }
  
  emit('export', options)
}
</script>

<style lang="scss" scoped>
.export-dialog-content {
  .novel-info {
    background: #f8f9fa;
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 20px;

    .novel-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;

      .novel-title {
        margin: 0;
        font-size: 16px;
        font-weight: 600;
        color: #303133;
      }
    }

    .novel-stats {
      display: flex;
      gap: 16px;
      font-size: 14px;
      color: #606266;

      .stat-item {
        &:not(:last-child)::after {
          content: "·";
          margin-left: 8px;
          color: #c0c4cc;
        }
      }
    }
  }

  .export-config {
    .format-group {
      width: 100%;

      .format-option {
        width: 100%;
        margin: 0 0 12px 0;
        padding: 12px;
        border: 1px solid #e4e7ed;
        border-radius: 6px;
        transition: all 0.3s ease;

        &:hover {
          border-color: #409eff;
          background-color: #f0f9ff;
        }

        :deep(.el-radio__input.is-checked + .el-radio__label) {
          color: #409eff;
        }

        :deep(.el-radio__input.is-checked) ~ .format-item {
          .format-name {
            color: #409eff;
          }
        }
      }

      .format-item {
        display: flex;
        align-items: center;
        gap: 12px;
        width: 100%;

        .el-icon {
          font-size: 24px;
          color: #909399;
        }

        .format-info {
          flex: 1;

          .format-name {
            display: block;
            font-weight: 500;
            color: #303133;
            margin-bottom: 2px;
          }

          .format-desc {
            font-size: 12px;
            color: #909399;
          }
        }
      }
    }

    .content-options {
      .el-checkbox {
        width: 100%;
        margin: 0 0 12px 0;
        padding: 8px 0;

        :deep(.el-checkbox__label) {
          display: flex;
          flex-direction: column;
          align-items: flex-start;
          gap: 2px;
          width: 100%;
          line-height: 1.2;
        }

        .option-label {
          display: flex;
          align-items: center;
          gap: 6px;
          font-weight: 500;
          color: #303133;
        }

        .option-desc {
          font-size: 12px;
          color: #909399;
          margin-left: 22px;
        }
      }
    }

    .chapter-options {
      .filter-group {
        margin-bottom: 12px;

        :deep(.el-radio) {
          margin-right: 20px;
        }
      }

      .range-input {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 8px 12px;
        background: #f8f9fa;
        border-radius: 6px;

        .range-label {
          font-size: 14px;
          color: #606266;
        }

        .range-separator {
          font-size: 14px;
          color: #909399;
        }
      }
    }
  }

  .export-preview {
    background: #f0f9ff;
    border: 1px solid #b3d8ff;
    border-radius: 6px;
    padding: 12px;
    margin-top: 20px;

    .preview-header {
      display: flex;
      align-items: center;
      gap: 6px;
      margin-bottom: 8px;
      font-size: 14px;
      font-weight: 500;
      color: #409eff;
    }

    .preview-content {
      .preview-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 4px;
        font-size: 13px;

        .preview-label {
          color: #606266;
        }

        .preview-value {
          font-weight: 500;
          color: #303133;
        }
      }
    }
  }
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>