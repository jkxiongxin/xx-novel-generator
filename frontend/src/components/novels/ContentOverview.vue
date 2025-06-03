<template>
  <el-card class="content-overview-card" shadow="hover">
    <template #header>
      <div class="card-header">
        <h3>内容概览</h3>
        <el-tag 
          v-if="overview.last_activity_date" 
          size="small" 
          type="info"
        >
          {{ formatLastActivity(overview.last_activity_date) }}
        </el-tag>
      </div>
    </template>

    <div class="overview-content">
      <!-- 基本信息 -->
      <div class="basic-info">
        <div class="info-item">
          <span class="label">字数进度：</span>
          <div class="progress-info">
            <span class="current">{{ formatWordCount(novel.word_count) }}</span>
            <span v-if="novel.target_words" class="target">
              / {{ formatWordCount(novel.target_words) }}
            </span>
          </div>
        </div>
        
        <div class="info-item">
          <span class="label">章节进度：</span>
          <span class="value">{{ novel.chapter_count }} 章</span>
        </div>
        
        <div v-if="novel.last_chapter_title" class="info-item">
          <span class="label">最新章节：</span>
          <el-button 
            type="text" 
            @click="$emit('quick-access', 'chapters')"
            class="chapter-link"
          >
            {{ novel.last_chapter_title }}
          </el-button>
        </div>
      </div>

      <!-- 进度条 -->
      <div v-if="novel.target_words" class="progress-section">
        <div class="progress-header">
          <span class="progress-label">完成进度</span>
          <span class="progress-percentage">{{ novel.progress_percentage }}%</span>
        </div>
        <el-progress 
          :percentage="novel.progress_percentage"
          :color="getProgressColor(novel.progress_percentage)"
          :stroke-width="8"
        />
      </div>

      <!-- 内容模块状态 -->
      <div class="modules-section">
        <h4 class="section-title">创作模块</h4>
        <div class="modules-grid">
          <!-- 世界观 -->
          <div 
            class="module-item"
            :class="{ 'has-content': overview.has_worldview }"
            @click="$emit('quick-access', 'worldview')"
          >
            <div class="module-icon">
              <el-icon><Globe /></el-icon>
            </div>
            <div class="module-content">
              <div class="module-name">世界观</div>
              <div class="module-status">
                <span v-if="overview.has_worldview" class="status-text">
                  {{ overview.worldview_count }} 个世界
                </span>
                <span v-else class="status-empty">未创建</span>
              </div>
            </div>
            <div class="module-action">
              <el-icon><ArrowRight /></el-icon>
            </div>
          </div>

          <!-- 角色 -->
          <div 
            class="module-item"
            :class="{ 'has-content': overview.character_count > 0 }"
            @click="$emit('quick-access', 'characters')"
          >
            <div class="module-icon">
              <el-icon><User /></el-icon>
            </div>
            <div class="module-content">
              <div class="module-name">角色</div>
              <div class="module-status">
                <span v-if="overview.character_count > 0" class="status-text">
                  {{ overview.character_count }} 个角色
                </span>
                <span v-else class="status-empty">未创建</span>
              </div>
            </div>
            <div class="module-action">
              <el-icon><ArrowRight /></el-icon>
            </div>
          </div>

          <!-- 大纲 -->
          <div 
            class="module-item"
            :class="{ 'has-content': overview.rough_outline_count > 0 || overview.detailed_outline_count > 0 }"
            @click="$emit('quick-access', 'outline')"
          >
            <div class="module-icon">
              <el-icon><List /></el-icon>
            </div>
            <div class="module-content">
              <div class="module-name">大纲</div>
              <div class="module-status">
                <span v-if="overview.rough_outline_count > 0 || overview.detailed_outline_count > 0" class="status-text">
                  粗略: {{ overview.rough_outline_count }} / 详细: {{ overview.detailed_outline_count }}
                </span>
                <span v-else class="status-empty">未创建</span>
              </div>
            </div>
            <div class="module-action">
              <el-icon><ArrowRight /></el-icon>
            </div>
          </div>

          <!-- 章节 -->
          <div 
            class="module-item"
            :class="{ 'has-content': novel.chapter_count > 0 }"
            @click="$emit('quick-access', 'chapters')"
          >
            <div class="module-icon">
              <el-icon><Document /></el-icon>
            </div>
            <div class="module-content">
              <div class="module-name">章节</div>
              <div class="module-status">
                <span v-if="novel.chapter_count > 0" class="status-text">
                  {{ novel.chapter_count }} 章
                </span>
                <span v-else class="status-empty">未创建</span>
              </div>
            </div>
            <div class="module-action">
              <el-icon><ArrowRight /></el-icon>
            </div>
          </div>
        </div>
      </div>

      <!-- 创作建议 -->
      <div class="suggestions-section">
        <h4 class="section-title">创作建议</h4>
        <div class="suggestions">
          <div v-if="getSuggestions().length === 0" class="suggestion-item completed">
            <el-icon class="suggestion-icon"><CircleCheck /></el-icon>
            <span class="suggestion-text">创作模块已完善，继续加油写作！</span>
          </div>
          <div 
            v-for="suggestion in getSuggestions()" 
            :key="suggestion.type"
            class="suggestion-item"
            @click="$emit('quick-access', suggestion.module)"
          >
            <el-icon class="suggestion-icon"><Warning /></el-icon>
            <span class="suggestion-text">{{ suggestion.text }}</span>
            <el-button type="text" size="small">去完善</el-button>
          </div>
        </div>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import {
  Connection as Globe,
  User,
  List,
  Document,
  ArrowRight,
  Warning,
  CircleCheck
} from '@element-plus/icons-vue'
import { NovelUtils, type NovelDetailResponse } from '@/api/novels'

interface ContentOverview {
  has_worldview: boolean
  worldview_count: number
  character_count: number
  rough_outline_count: number
  detailed_outline_count: number
  last_activity_date?: string
}

interface Props {
  overview: ContentOverview
  novel: NovelDetailResponse
}

interface Emits {
  (e: 'quick-access', module: string): void
}

const props = defineProps<Props>()
defineEmits<Emits>()

// 计算属性
const getSuggestions = () => {
  const suggestions = []
  
  if (!props.overview.has_worldview) {
    suggestions.push({
      type: 'worldview',
      module: 'worldview',
      text: '建议创建世界观，丰富小说背景设定'
    })
  }
  
  if (props.overview.character_count === 0) {
    suggestions.push({
      type: 'characters',
      module: 'characters',
      text: '建议添加角色，完善人物设定'
    })
  }
  
  if (props.overview.rough_outline_count === 0) {
    suggestions.push({
      type: 'outline',
      module: 'outline',
      text: '建议制定大纲，规划故事情节'
    })
  }
  
  if (props.novel.chapter_count === 0) {
    suggestions.push({
      type: 'chapters',
      module: 'chapters',
      text: '开始创作第一章吧！'
    })
  }
  
  return suggestions
}

// 方法定义
const formatWordCount = (count: number) => {
  return NovelUtils.formatWordCount(count)
}

const formatLastActivity = (dateString: string) => {
  return `最后活动: ${NovelUtils.formatRelativeTime(dateString)}`
}

const getProgressColor = (percentage: number) => {
  return NovelUtils.getProgressColor(percentage)
}
</script>

<style scoped lang="scss">
.content-overview-card {
  height: 100%;
  
  :deep(.el-card__header) {
    padding: 16px 20px;
    border-bottom: 1px solid #f0f0f0;
  }
  
  :deep(.el-card__body) {
    padding: 20px;
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  
  h3 {
    margin: 0;
    font-size: 16px;
    font-weight: 600;
    color: #303133;
  }
}

.overview-content {
  .basic-info {
    margin-bottom: 20px;
    
    .info-item {
      display: flex;
      align-items: center;
      margin-bottom: 12px;
      
      &:last-child {
        margin-bottom: 0;
      }
      
      .label {
        font-size: 14px;
        color: #606266;
        margin-right: 8px;
        min-width: 80px;
      }
      
      .value {
        font-size: 14px;
        color: #303133;
        font-weight: 500;
      }
      
      .progress-info {
        display: flex;
        align-items: center;
        gap: 4px;
        
        .current {
          font-size: 14px;
          color: #303133;
          font-weight: 600;
        }
        
        .target {
          font-size: 14px;
          color: #909399;
        }
      }
      
      .chapter-link {
        padding: 0;
        font-size: 14px;
        
        &:hover {
          color: #409EFF;
        }
      }
    }
  }
  
  .progress-section {
    margin-bottom: 24px;
    
    .progress-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;
      
      .progress-label {
        font-size: 14px;
        color: #606266;
      }
      
      .progress-percentage {
        font-size: 14px;
        color: #303133;
        font-weight: 600;
      }
    }
  }
  
  .section-title {
    font-size: 14px;
    font-weight: 600;
    color: #606266;
    margin: 0 0 16px 0;
    padding-bottom: 8px;
    border-bottom: 1px solid #f0f0f0;
  }
}

.modules-section {
  margin-bottom: 24px;
  
  .modules-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
    
    @media (max-width: 768px) {
      grid-template-columns: 1fr;
    }
  }
  
  .module-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 16px;
    background: #fafafa;
    border: 1px solid #f0f0f0;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.3s;
    
    &:hover {
      background: #f5f7fa;
      border-color: #409EFF;
      transform: translateY(-1px);
    }
    
    &.has-content {
      border-color: #67C23A;
      
      .module-icon {
        color: #67C23A;
      }
      
      .status-text {
        color: #67C23A;
      }
    }
    
    .module-icon {
      font-size: 20px;
      color: #c0c4cc;
      flex-shrink: 0;
    }
    
    .module-content {
      flex: 1;
      min-width: 0;
      
      .module-name {
        font-size: 14px;
        font-weight: 500;
        color: #303133;
        margin-bottom: 4px;
      }
      
      .module-status {
        font-size: 12px;
        
        .status-text {
          color: #606266;
        }
        
        .status-empty {
          color: #c0c4cc;
          font-style: italic;
        }
      }
    }
    
    .module-action {
      font-size: 14px;
      color: #c0c4cc;
      flex-shrink: 0;
    }
  }
}

.suggestions-section {
  .suggestions {
    .suggestion-item {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 12px;
      margin-bottom: 8px;
      background: #fdf6ec;
      border: 1px solid #faecd8;
      border-radius: 6px;
      cursor: pointer;
      transition: all 0.3s;
      
      &:last-child {
        margin-bottom: 0;
      }
      
      &:hover {
        background: #faecd8;
      }
      
      &.completed {
        background: #f0f9ff;
        border-color: #b3d8ff;
        cursor: default;
        
        &:hover {
          background: #f0f9ff;
        }
        
        .suggestion-icon {
          color: #67C23A;
        }
        
        .suggestion-text {
          color: #409EFF;
        }
      }
      
      .suggestion-icon {
        font-size: 16px;
        color: #E6A23C;
        flex-shrink: 0;
      }
      
      .suggestion-text {
        flex: 1;
        font-size: 13px;
        color: #E6A23C;
      }
    }
  }
}

// 响应式调整
@media (max-width: 768px) {
  .basic-info {
    .info-item {
      flex-direction: column;
      align-items: flex-start;
      gap: 4px;
      margin-bottom: 16px;
      
      .label {
        min-width: auto;
        margin-right: 0;
      }
    }
  }
  
  .modules-grid {
    .module-item {
      padding: 12px;
      
      .module-icon {
        font-size: 18px;
      }
      
      .module-name {
        font-size: 13px;
      }
      
      .module-status {
        font-size: 11px;
      }
    }
  }
  
  .suggestions {
    .suggestion-item {
      padding: 10px;
      
      .suggestion-text {
        font-size: 12px;
      }
    }
  }
}
</style>