<template>
  <el-card class="recent-activity-card" shadow="hover">
    <template #header>
      <div class="card-header">
        <h3>最近活动</h3>
        <el-button 
          type="text" 
          :icon="Refresh" 
          @click="$emit('refresh')"
          :loading="loading"
          size="small"
        >
          刷新
        </el-button>
      </div>
    </template>

    <div v-loading="loading" class="activity-content">
      <div v-if="activities.length === 0" class="empty-state">
        <el-empty 
          :image-size="100" 
          description="暂无活动记录"
        >
          <el-button type="primary" @click="$emit('refresh')">
            刷新数据
          </el-button>
        </el-empty>
      </div>

      <el-timeline v-else>
        <el-timeline-item
          v-for="activity in activities"
          :key="activity.id"
          :timestamp="formatTimestamp(activity.timestamp)"
          :color="getActivityColor(activity.type)"
          placement="top"
        >
          <div class="activity-item">
            <div class="activity-header">
              <div class="activity-icon">
                <el-icon>
                  <component :is="getActivityIcon(activity.type)" />
                </el-icon>
              </div>
              <div class="activity-title">{{ activity.title }}</div>
              <div class="activity-type">
                <el-tag :type="getActivityTagType(activity.type)" size="small">
                  {{ getActivityTypeText(activity.type) }}
                </el-tag>
              </div>
            </div>
            
            <div v-if="activity.description" class="activity-description">
              {{ activity.description }}
            </div>
            
            <div v-if="activity.metadata" class="activity-metadata">
              <div 
                v-if="activity.metadata.words_added && activity.metadata.words_added > 0" 
                class="meta-item"
              >
                <el-icon class="meta-icon"><Document /></el-icon>
                <span class="meta-text">新增 {{ activity.metadata.words_added }} 字</span>
              </div>
              
              <div 
                v-if="activity.metadata.chapter_id" 
                class="meta-item clickable"
                @click="handleChapterClick(activity.metadata.chapter_id)"
              >
                <el-icon class="meta-icon"><Link /></el-icon>
                <span class="meta-text">查看章节</span>
              </div>
              
              <div 
                v-if="activity.metadata.character_id" 
                class="meta-item clickable"
                @click="handleCharacterClick(activity.metadata.character_id)"
              >
                <el-icon class="meta-icon"><User /></el-icon>
                <span class="meta-text">查看角色</span>
              </div>
            </div>
          </div>
        </el-timeline-item>
      </el-timeline>

      <!-- 查看更多 -->
      <div v-if="activities.length >= 10" class="load-more">
        <el-button 
          type="text" 
          @click="$emit('load-more')"
          :loading="loadingMore"
        >
          查看更多活动
        </el-button>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { 
  Refresh, 
  Document, 
  User, 
  Link,
  EditPen,
  Plus,
  List,
  Connection
} from '@element-plus/icons-vue'
import { NovelUtils, type Activity } from '@/api/novels'

interface Props {
  activities: Activity[]
  loading?: boolean
  loadingMore?: boolean
}

interface Emits {
  (e: 'refresh'): void
  (e: 'load-more'): void
  (e: 'chapter-click', chapterId: string): void
  (e: 'character-click', characterId: string): void
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  loadingMore: false
})

const emit = defineEmits<Emits>()

// 方法定义
const formatTimestamp = (timestamp: string) => {
  return NovelUtils.formatRelativeTime(timestamp)
}

const getActivityColor = (type: string) => {
  const colorMap: Record<string, string> = {
    'chapter_created': '#67C23A',
    'chapter_updated': '#409EFF',
    'character_added': '#E6A23C',
    'outline_generated': '#F56C6C',
    'worldview_updated': '#909399'
  }
  return colorMap[type] || '#409EFF'
}

const getActivityIcon = (type: string) => {
  const iconMap: Record<string, any> = {
    'chapter_created': Plus,
    'chapter_updated': EditPen,
    'character_added': User,
    'outline_generated': List,
    'worldview_updated': Connection
  }
  return iconMap[type] || Document
}

const getActivityTagType = (type: string) => {
  const typeMap: Record<string, string> = {
    'chapter_created': 'success',
    'chapter_updated': 'primary',
    'character_added': 'warning',
    'outline_generated': 'danger',
    'worldview_updated': 'info'
  }
  return typeMap[type] || 'primary'
}

const getActivityTypeText = (type: string) => {
  const textMap: Record<string, string> = {
    'chapter_created': '创建章节',
    'chapter_updated': '更新章节',
    'character_added': '添加角色',
    'outline_generated': '生成大纲',
    'worldview_updated': '更新世界观'
  }
  return textMap[type] || type
}

const handleChapterClick = (chapterId: string) => {
  emit('chapter-click', chapterId)
}

const handleCharacterClick = (characterId: string) => {
  emit('character-click', characterId)
}
</script>

<style scoped lang="scss">
.recent-activity-card {
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

.activity-content {
  min-height: 300px;
  max-height: 500px;
  overflow-y: auto;
  
  &::-webkit-scrollbar {
    width: 4px;
  }
  
  &::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 2px;
  }
  
  &::-webkit-scrollbar-thumb {
    background: #c1c1c1;
    border-radius: 2px;
    
    &:hover {
      background: #a8a8a8;
    }
  }
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 300px;
}

:deep(.el-timeline) {
  padding-left: 0;
  
  .el-timeline-item {
    padding-bottom: 20px;
    
    &:last-child {
      padding-bottom: 0;
    }
    
    .el-timeline-item__timestamp {
      font-size: 12px;
      color: #909399;
      margin-bottom: 8px;
    }
    
    .el-timeline-item__node {
      width: 12px;
      height: 12px;
      left: -6px;
    }
    
    .el-timeline-item__wrapper {
      padding-left: 20px;
    }
  }
}

.activity-item {
  .activity-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 8px;
    
    .activity-icon {
      width: 24px;
      height: 24px;
      border-radius: 4px;
      background: #f5f7fa;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 12px;
      color: #409EFF;
    }
    
    .activity-title {
      flex: 1;
      font-size: 14px;
      font-weight: 500;
      color: #303133;
      min-width: 0;
      word-break: break-word;
    }
    
    .activity-type {
      flex-shrink: 0;
    }
  }
  
  .activity-description {
    font-size: 13px;
    color: #606266;
    line-height: 1.4;
    margin-bottom: 8px;
    padding-left: 32px;
  }
  
  .activity-metadata {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    padding-left: 32px;
    
    .meta-item {
      display: flex;
      align-items: center;
      gap: 4px;
      font-size: 12px;
      color: #909399;
      
      &.clickable {
        cursor: pointer;
        transition: color 0.3s;
        
        &:hover {
          color: #409EFF;
        }
      }
      
      .meta-icon {
        font-size: 12px;
      }
      
      .meta-text {
        white-space: nowrap;
      }
    }
  }
}

.load-more {
  text-align: center;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}

// 响应式调整
@media (max-width: 768px) {
  .activity-content {
    max-height: 400px;
  }
  
  .activity-item {
    .activity-header {
      .activity-title {
        font-size: 13px;
      }
      
      .activity-icon {
        width: 20px;
        height: 20px;
        font-size: 10px;
      }
    }
    
    .activity-description {
      font-size: 12px;
      padding-left: 28px;
    }
    
    .activity-metadata {
      padding-left: 28px;
      
      .meta-item {
        font-size: 11px;
        
        .meta-icon {
          font-size: 10px;
        }
      }
    }
  }
  
  :deep(.el-timeline-item__wrapper) {
    padding-left: 16px;
  }
}

// 活动类型特定样式
.activity-item {
  &[data-type="chapter_created"] {
    .activity-icon {
      background: #f0f9ff;
      color: #67C23A;
    }
  }
  
  &[data-type="chapter_updated"] {
    .activity-icon {
      background: #ecf5ff;
      color: #409EFF;
    }
  }
  
  &[data-type="character_added"] {
    .activity-icon {
      background: #fdf6ec;
      color: #E6A23C;
    }
  }
  
  &[data-type="outline_generated"] {
    .activity-icon {
      background: #fef0f0;
      color: #F56C6C;
    }
  }
  
  &[data-type="worldview_updated"] {
    .activity-icon {
      background: #f4f4f5;
      color: #909399;
    }
  }
}
</style>