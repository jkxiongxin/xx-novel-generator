<template>
  <el-dialog
    v-model="visible"
    title="导出小说"
    width="500px"
    :before-close="handleClose"
  >
    <div class="export-content">
      <p class="export-description">
        选择导出格式和内容，我们将为您生成文件并提供下载链接。
      </p>
      
      <el-form :model="form" label-width="100px">
        <el-form-item label="导出格式" required>
          <el-radio-group v-model="form.format">
            <el-radio label="txt">TXT 文本</el-radio>
            <el-radio label="docx">Word 文档</el-radio>
            <el-radio label="pdf">PDF 文件</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="导出内容">
          <el-checkbox-group v-model="form.includes">
            <el-checkbox label="outline">大纲</el-checkbox>
            <el-checkbox label="worldview">世界观</el-checkbox>
            <el-checkbox label="characters">角色设定</el-checkbox>
            <el-checkbox label="metadata">小说信息</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        
        <el-form-item label="章节范围">
          <el-radio-group v-model="form.chapterRange">
            <el-radio label="all">全部章节</el-radio>
            <el-radio label="completed">仅已完成章节</el-radio>
            <el-radio label="custom">自定义范围</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item 
          v-if="form.chapterRange === 'custom'" 
          label="章节选择"
        >
          <div class="chapter-range">
            <el-input-number 
              v-model="form.startChapter" 
              :min="1" 
              :max="novel?.chapter_count || 1"
              placeholder="起始章节"
            />
            <span class="range-separator">至</span>
            <el-input-number 
              v-model="form.endChapter" 
              :min="form.startChapter || 1" 
              :max="novel?.chapter_count || 1"
              placeholder="结束章节"
            />
          </div>
        </el-form-item>
        
        <el-form-item 
          v-if="form.format === 'pdf'" 
          label="PDF 设置"
        >
          <div class="pdf-options">
            <div class="option-row">
              <span class="option-label">字体大小：</span>
              <el-select v-model="form.fontSize" style="width: 100px">
                <el-option label="12pt" :value="12" />
                <el-option label="14pt" :value="14" />
                <el-option label="16pt" :value="16" />
                <el-option label="18pt" :value="18" />
              </el-select>
            </div>
            <div class="option-row">
              <span class="option-label">行间距：</span>
              <el-select v-model="form.lineSpacing" style="width: 100px">
                <el-option label="1.0" :value="1.0" />
                <el-option label="1.2" :value="1.2" />
                <el-option label="1.5" :value="1.5" />
                <el-option label="2.0" :value="2.0" />
              </el-select>
            </div>
            <div class="option-row">
              <span class="option-label">页面大小：</span>
              <el-select v-model="form.pageFormat" style="width: 100px">
                <el-option label="A4" value="A4" />
                <el-option label="A5" value="A5" />
                <el-option label="Letter" value="letter" />
              </el-select>
            </div>
          </div>
        </el-form-item>
      </el-form>
      
      <div class="export-preview">
        <h4>导出预览</h4>
        <div class="preview-info">
          <div class="info-item">
            <span class="label">格式：</span>
            <span class="value">{{ getFormatText(form.format) }}</span>
          </div>
          <div class="info-item">
            <span class="label">章节：</span>
            <span class="value">{{ getChapterRangeText() }}</span>
          </div>
          <div class="info-item">
            <span class="label">附加内容：</span>
            <span class="value">{{ getIncludesText() }}</span>
          </div>
        </div>
      </div>
    </div>

    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" @click="handleExport" :loading="exporting">
          开始导出
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, watch, computed } from 'vue'
import type { NovelDetailResponse, NovelListItem } from '@/api/novels'

interface Props {
  modelValue: boolean
  novel?: NovelDetailResponse | NovelListItem | null
  loading?: boolean
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'export', data: any): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// 响应式数据
const visible = ref(false)
const exporting = computed(() => props.loading || false)

const form = reactive({
  format: 'txt',
  includes: ['metadata'],
  chapterRange: 'all',
  startChapter: 1,
  endChapter: 1,
  fontSize: 14,
  lineSpacing: 1.5,
  pageFormat: 'A4'
})

// 监听显示状态
watch(() => props.modelValue, (newValue) => {
  visible.value = newValue
  if (newValue) {
    resetForm()
  }
})

watch(visible, (newValue) => {
  emit('update:modelValue', newValue)
})

// 方法定义
const resetForm = () => {
  form.format = 'txt'
  form.includes = ['metadata']
  form.chapterRange = 'all'
  form.startChapter = 1
  form.endChapter = props.novel?.chapter_count || 1
  form.fontSize = 14
  form.lineSpacing = 1.5
  form.pageFormat = 'A4'
}

const handleClose = () => {
  visible.value = false
}

const handleExport = () => {
  const exportData: any = {
    format: form.format,
    include_outline: form.includes.includes('outline'),
    include_worldview: form.includes.includes('worldview'),
    include_characters: form.includes.includes('characters'),
    include_metadata: form.includes.includes('metadata')
  }
  
  if (form.chapterRange === 'completed') {
    exportData.only_completed = true
  } else if (form.chapterRange === 'custom') {
    exportData.chapter_range = {
      start_chapter: form.startChapter,
      end_chapter: form.endChapter
    }
  }
  
  if (form.format === 'pdf') {
    exportData.export_options = {
      font_size: form.fontSize,
      line_spacing: form.lineSpacing,
      page_format: form.pageFormat
    }
  }
  
  emit('export', exportData)
}

const getFormatText = (format: string) => {
  const formatMap: Record<string, string> = {
    'txt': 'TXT 文本文件',
    'docx': 'Word 文档',
    'pdf': 'PDF 文件'
  }
  return formatMap[format] || format
}

const getChapterRangeText = () => {
  if (form.chapterRange === 'all') {
    return '全部章节'
  } else if (form.chapterRange === 'completed') {
    return '仅已完成章节'
  } else {
    return `第 ${form.startChapter} - ${form.endChapter} 章`
  }
}

const getIncludesText = () => {
  if (form.includes.length === 0) {
    return '无'
  }
  
  const includeMap: Record<string, string> = {
    'outline': '大纲',
    'worldview': '世界观',
    'characters': '角色设定',
    'metadata': '小说信息'
  }
  
  return form.includes.map(item => includeMap[item]).join('、')
}
</script>

<style scoped lang="scss">
.export-content {
  .export-description {
    margin-bottom: 20px;
    color: #606266;
    font-size: 14px;
    line-height: 1.6;
  }
  
  .chapter-range {
    display: flex;
    align-items: center;
    gap: 8px;
    
    .range-separator {
      color: #606266;
      font-size: 14px;
    }
  }
  
  .pdf-options {
    .option-row {
      display: flex;
      align-items: center;
      margin-bottom: 12px;
      
      &:last-child {
        margin-bottom: 0;
      }
      
      .option-label {
        width: 80px;
        font-size: 14px;
        color: #606266;
      }
    }
  }
  
  .export-preview {
    margin-top: 20px;
    padding: 16px;
    background: #f5f7fa;
    border-radius: 6px;
    
    h4 {
      margin: 0 0 12px 0;
      font-size: 14px;
      color: #303133;
    }
    
    .preview-info {
      .info-item {
        display: flex;
        margin-bottom: 8px;
        
        &:last-child {
          margin-bottom: 0;
        }
        
        .label {
          width: 80px;
          font-size: 13px;
          color: #606266;
        }
        
        .value {
          font-size: 13px;
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