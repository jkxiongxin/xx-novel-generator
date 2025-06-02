<template>
  <div class="novel-grid">
    <el-row :gutter="20" v-loading="loading">
      <el-col
        v-for="novel in novels"
        :key="novel.id"
        :xs="24"
        :sm="12"
        :md="8"
        :lg="6"
        :xl="4"
        :xxl="3"
        class="novel-col"
      >
        <div class="novel-card-wrapper">
          <el-card 
            class="novel-card"
            :class="{ 'selected': isSelected(novel.id) }"
            shadow="hover"
            @click="handleCardClick(novel)"
          >
            <!-- 选择框 -->
            <div class="card-selection" @click.stop>
              <el-checkbox 
                :model-value="isSelected(novel.id)"
                @change="toggleSelection(novel.id)"
              />
            </div>

            <!-- 封面图片 -->
            <div class="cover-container">
              <img 
                v-if="novel.cover_image" 
                :src="novel.cover_image" 
                :alt="novel.title"
                class="cover-image"
                @error="handleImageError"
              />
              <div v-else class="cover-placeholder">
                <el-icon :size="48" color="#c0c4cc">
                  <Document />
                </el-icon>
                <span class="genre-text">{{ NovelUtils.getGenreText(novel.genre) }}</span>
              </div>
            </div>

            <!-- 卡片内容 -->
            <div class="card-content">
              <div class="card-header">
                <h3 class="novel-title" :title="novel.title">{{ novel.title }}</h3>
                <el-dropdown 
                  class="card-menu"
                  @click.stop
                  trigger="click"
                  placement="bottom-end"
                >
                  <el-button 
                    type="text" 
                    :icon="MoreFilled" 
                    size="small"
                    circle
                  />
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item @click="$emit('view-detail', novel.id)">
                        <el-icon><View /></el-icon>
                        查看详情
                      </el-dropdown-item>
                      <el-dropdown-item @click="$emit('enter-workspace', novel.id)">
                        <el-icon><Edit /></el-icon>
                        进入工作台
                      </el-dropdown-item>
                      <el-dropdown-item divided @click="$emit('export-novel', novel)">
                        <el-icon><Download /></el-icon>
                        导出小说
                      </el-dropdown-item>
                      <el-dropdown-item @click="$emit('delete-novel', novel)">
                        <el-icon><Delete /></el-icon>
                        <span style="color: #f56c6c;">删除小说</span>
                      </el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>

              <div class="novel-meta">
                <div class="status-row">
                  <el-tag 
                    :type="getStatusTagType(novel.status)" 
                    size="small"
                    effect="light"
                  >
                    {{ NovelUtils.getStatusText(novel.status) }}
                  </el-tag>
                  <span class="word-count">{{ NovelUtils.formatWordCount(novel.word_count) }}</span>
                </div>

                <div class="progress-row" v-if="novel.target_words && novel.target_words > 0">
                  <div class="progress-info">
                    <span class="progress-text">进度</span>
                    <span class="progress-percentage">{{ NovelUtils.formatProgress(novel.progress_percentage) }}</span>
                  </div>
                  <el-progress 
                    :percentage="novel.progress_percentage" 
                    :stroke-width="4"
                    :color="NovelUtils.getProgressColor(novel.progress_percentage)"
                    :show-text="false"
                  />
                </div>

                <div class="stats-row">
                  <span class="stat-item">
                    <el-icon><Document /></el-icon>
                    {{ novel.chapter_count }} 章
                  </span>
                  <span class="update-time">
                    {{ NovelUtils.formatRelativeTime(novel.updated_at) }}
                  </span>
                </div>

                <div class="last-chapter" v-if="novel.last_chapter_title">
                  <span class="last-chapter-label">最新：</span>
                  <span class="last-chapter-title" :title="novel.last_chapter_title">
                    {{ novel.last_chapter_title }}
                  </span>
                </div>
              </div>

              <div class="card-actions">
                <el-button 
                  type="primary" 
                  size="small"
                  style="width: 100%;"
                  @click.stop="$emit('enter-workspace', novel.id)"
                >
                  进入工作台
                </el-button>
              </div>
            </div>
          </el-card>
        </div>
      </el-col>
    </el-row>

    <!-- 空状态 -->
    <div v-if="!loading && novels.length === 0" class="empty-state">
      <el-empty 
        description="暂无小说数据"
        :image-size="120"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { 
  Document, MoreFilled, View, Edit, Download, Delete 
} from '@element-plus/icons-vue'
import type { NovelListItem } from '@/api/novels'
import { NovelUtils } from '@/api/novels'

// Props
interface Props {
  novels: NovelListItem[]
  loading?: boolean
  selected: number[]
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  selected: () => []
})

// Emits
const emit = defineEmits<{
  'update:selected': [selected: number[]]
  'view-detail': [novelId: number]
  'enter-workspace': [novelId: number]
  'export-novel': [novel: NovelListItem]
  'delete-novel': [novel: NovelListItem]
}>()

// 计算属性
const selectedSet = computed(() => new Set(props.selected))

// 方法
const isSelected = (novelId: number): boolean => {
  return selectedSet.value.has(novelId)
}

const toggleSelection = (novelId: number) => {
  const newSelected = [...props.selected]
  const index = newSelected.indexOf(novelId)
  
  if (index > -1) {
    newSelected.splice(index, 1)
  } else {
    newSelected.push(novelId)
  }
  
  emit('update:selected', newSelected)
}

const handleCardClick = (novel: NovelListItem) => {
  // 卡片点击进入详情页
  emit('view-detail', novel.id)
}

const handleImageError = (event: Event) => {
  // 图片加载失败时隐藏
  const target = event.target as HTMLImageElement
  target.style.display = 'none'
}

const getStatusTagType = (status: string): string => {
  const typeMap: Record<string, string> = {
    'draft': 'info',
    'ongoing': 'warning',
    'completed': 'success',
    'paused': 'danger'
  }
  return typeMap[status] || 'info'
}
</script>

<style lang="scss" scoped>
.novel-grid {
  .novel-col {
    margin-bottom: 20px;
  }

  .novel-card-wrapper {
    height: 100%;
  }

  .novel-card {
    height: 400px;
    cursor: pointer;
    transition: all 0.3s ease;
    position: relative;
    
    &:hover {
      transform: translateY(-4px);
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
    }

    &.selected {
      border-color: #409eff;
      box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
    }

    :deep(.el-card__body) {
      padding: 0;
      height: 100%;
      display: flex;
      flex-direction: column;
    }

    .card-selection {
      position: absolute;
      top: 8px;
      left: 8px;
      z-index: 10;
      background: rgba(255, 255, 255, 0.9);
      border-radius: 4px;
      padding: 4px;
    }

    .cover-container {
      height: 180px;
      overflow: hidden;
      border-radius: 8px 8px 0 0;
      background: #f5f7fa;
      display: flex;
      align-items: center;
      justify-content: center;

      .cover-image {
        width: 100%;
        height: 100%;
        object-fit: cover;
      }

      .cover-placeholder {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        color: #c0c4cc;
        
        .genre-text {
          margin-top: 8px;
          font-size: 14px;
          color: #909399;
        }
      }
    }

    .card-content {
      flex: 1;
      padding: 16px;
      display: flex;
      flex-direction: column;
    }

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 12px;

      .novel-title {
        font-size: 16px;
        font-weight: 600;
        color: #303133;
        margin: 0;
        flex: 1;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        line-height: 1.2;
      }

      .card-menu {
        flex-shrink: 0;
        margin-left: 8px;
      }
    }

    .novel-meta {
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 8px;

      .status-row {
        display: flex;
        justify-content: space-between;
        align-items: center;

        .word-count {
          font-size: 13px;
          color: #606266;
          font-weight: 500;
        }
      }

      .progress-row {
        .progress-info {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 4px;
          font-size: 12px;
          color: #606266;

          .progress-percentage {
            font-weight: 600;
          }
        }
      }

      .stats-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 12px;
        color: #909399;

        .stat-item {
          display: flex;
          align-items: center;
          gap: 4px;
        }

        .update-time {
          font-size: 11px;
        }
      }

      .last-chapter {
        font-size: 12px;
        color: #606266;
        
        .last-chapter-label {
          color: #909399;
        }

        .last-chapter-title {
          font-weight: 500;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
          display: inline-block;
          max-width: 150px;
          vertical-align: bottom;
        }
      }
    }

    .card-actions {
      margin-top: 12px;
      padding-top: 12px;
      border-top: 1px solid #f0f2f5;
    }
  }

  .empty-state {
    text-align: center;
    padding: 60px 0;
    color: #909399;
  }
}

// 响应式设计
@media (max-width: 768px) {
  .novel-grid {
    .novel-card {
      height: 350px;

      .cover-container {
        height: 150px;
      }

      .card-content {
        padding: 12px;
      }

      .card-header .novel-title {
        font-size: 14px;
      }
    }
  }
}
</style>