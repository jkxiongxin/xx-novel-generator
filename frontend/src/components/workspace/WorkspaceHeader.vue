<template>
  <div class="workspace-header">
    <div class="header-content">
      <!-- 小说基本信息 -->
      <div class="novel-info">
        <h1 class="novel-title">{{ novel?.title || '加载中...' }}</h1>
        <div class="novel-meta" v-if="novel">
          <div class="meta-item">
            <el-icon class="icon"><Document /></el-icon>
            <span>{{ novel.genre }}</span>
          </div>
          <div class="meta-item">
            <el-icon class="icon"><Calendar /></el-icon>
            <span>创建于 {{ formatDate(novel.created_at) }}</span>
          </div>
          <div class="meta-item">
            <el-icon class="icon"><EditPen /></el-icon>
            <span>{{ formatDate(novel.updated_at) }} 更新</span>
          </div>
          <div class="meta-item" v-if="novel.word_count">
            <el-icon class="icon"><Reading /></el-icon>
            <span>{{ novel.word_count }} 字</span>
          </div>
        </div>
        <p class="novel-description" v-if="novel?.description">
          {{ novel.description }}
        </p>
      </div>

      <!-- 快捷操作按钮 -->
      <div class="quick-actions">
        <el-button
          type="primary"
          size="large"
          class="action-btn primary-action"
          @click="continueWriting"
          :loading="actionLoading.continue"
        >
          <el-icon><EditPen /></el-icon>
          {{ continueWritingText }}
        </el-button>

        <el-button
          type="success"
          size="default"
          class="action-btn"
          @click="openAIAssistant"
          :loading="actionLoading.ai"
        >
          <el-icon><MagicStick /></el-icon>
          AI助手
        </el-button>

        <el-button
          type="default"
          size="default"
          class="action-btn"
          @click="openSettings"
        >
          <el-icon><Setting /></el-icon>
          设置
        </el-button>
      </div>
    </div>

    <!-- 进度指示器 -->
    <div class="progress-indicator" v-if="progress">
      <div class="progress-info">
        <span class="progress-text">整体进度</span>
        <span class="progress-value">{{ Math.round(progress.overall_progress) }}%</span>
      </div>
      <el-progress
        :percentage="progress.overall_progress"
        :stroke-width="6"
        :show-text="false"
        color="#409EFF"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Document,
  Calendar,
  EditPen,
  Reading,
  MagicStick,
  Setting
} from '@element-plus/icons-vue'
import { WorkspaceService, type NovelBasicInfo, type ProgressOverview, type RecentChapterResponse } from '@/api/workspace'

// Props
interface Props {
  novelId: number
  novel?: NovelBasicInfo
  progress?: ProgressOverview
}

const props = withDefaults(defineProps<Props>(), {
  novel: undefined,
  progress: undefined
})

// Emits
const emit = defineEmits<{
  openAIAssistant: []
  refreshData: []
}>()

// Router
const router = useRouter()

// 响应式数据
const actionLoading = ref({
  continue: false,
  ai: false
})

const recentChapter = ref<RecentChapterResponse['chapter']>()

// 计算属性
const continueWritingText = computed(() => {
  if (recentChapter.value) {
    return '继续写作'
  }
  return '开始创作'
})

// 方法
const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const continueWriting = async () => {
  try {
    actionLoading.value.continue = true

    // 获取最近编辑的章节
    const recentData = await WorkspaceService.getRecentChapter(props.novelId)
    
    if (recentData.chapter) {
      // 跳转到最近章节编辑
      router.push(`/workspace/${props.novelId}/chapters?chapter=${recentData.chapter.id}`)
    } else {
      // 询问是否创建新章节
      await ElMessageBox.confirm(
        '还没有章节内容，是否创建第一章？',
        '开始创作',
        {
          confirmButtonText: '创建第一章',
          cancelButtonText: '取消',
          type: 'info'
        }
      )
      
      // 跳转到章节创建页面
      router.push(`/workspace/${props.novelId}/chapters?action=create`)
    }
    
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('继续写作失败:', error)
      ElMessage.error('无法继续写作，请稍后重试')
    }
  } finally {
    actionLoading.value.continue = false
  }
}

const openAIAssistant = () => {
  actionLoading.value.ai = true
  
  // 触发父组件的AI助手打开事件
  emit('openAIAssistant')
  
  // 记录使用行为
  console.log('Open AI Assistant:', {
    novel_id: props.novelId,
    current_module: 'overview'
  })
  
  setTimeout(() => {
    actionLoading.value.ai = false
  }, 500)
}

const openSettings = () => {
  router.push(`/workspace/${props.novelId}/settings`)
}

const loadRecentChapter = async () => {
  try {
    const data = await WorkspaceService.getRecentChapter(props.novelId)
    recentChapter.value = data.chapter
  } catch (error) {
    console.error('加载最近章节失败:', error)
  }
}

// 生命周期
onMounted(() => {
  loadRecentChapter()
})
</script>

<style scoped lang="scss">
.workspace-header {
  background: #ffffff;
  padding: 24px;
  margin-bottom: 24px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);

  .header-content {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 16px;

    .novel-info {
      flex: 1;

      .novel-title {
        font-size: 24px;
        font-weight: 600;
        color: #303133;
        margin: 0 0 8px 0;
      }

      .novel-meta {
        display: flex;
        gap: 16px;
        color: #606266;
        font-size: 14px;
        flex-wrap: wrap;

        .meta-item {
          display: flex;
          align-items: center;
          gap: 4px;

          .icon {
            color: #909399;
            font-size: 16px;
          }
        }
      }

      .novel-description {
        color: #606266;
        margin: 12px 0 0 0;
        line-height: 1.5;
        max-width: 600px;
      }
    }

    .quick-actions {
      display: flex;
      gap: 12px;
      flex-shrink: 0;

      .action-btn {
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 14px;

        &.primary-action {
          background: linear-gradient(45deg, #409EFF, #67C23A);
          border: none;
          color: white;

          &:hover {
            opacity: 0.9;
            transform: translateY(-1px);
          }
        }
      }
    }
  }

  .progress-indicator {
    .progress-info {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;

      .progress-text {
        font-size: 14px;
        color: #606266;
      }

      .progress-value {
        font-size: 14px;
        font-weight: 600;
        color: #409EFF;
      }
    }
  }
}

// 响应式设计
@media (max-width: 767px) {
  .workspace-header {
    padding: 16px;

    .header-content {
      flex-direction: column;
      gap: 16px;

      .novel-meta {
        gap: 12px;
      }

      .quick-actions {
        width: 100%;
        justify-content: center;

        .action-btn {
          flex: 1;
          max-width: 120px;
        }
      }
    }
  }
}

@media (max-width: 480px) {
  .workspace-header {
    .header-content {
      .novel-info {
        .novel-title {
          font-size: 20px;
        }

        .novel-meta {
          flex-direction: column;
          gap: 8px;
        }
      }

      .quick-actions {
        flex-direction: column;

        .action-btn {
          max-width: none;
        }
      }
    }
  }
}
</style>