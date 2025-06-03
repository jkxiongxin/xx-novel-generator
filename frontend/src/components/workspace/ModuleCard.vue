<template>
  <div :class="['module-card', `${moduleName}-card`]">
    <!-- 卡片头部 -->
    <div class="card-header">
      <div class="module-info">
        <h3 class="module-title">
          <el-icon class="module-icon">
            <component :is="moduleIcon" />
          </el-icon>
          {{ moduleConfig.title }}
        </h3>
        <p class="module-description">{{ moduleConfig.description }}</p>
      </div>
      
      <div class="module-status">
        <el-tag
          :class="['status-badge', moduleStats?.status || 'empty']"
          :type="getStatusType(moduleStats?.status)"
          size="small"
        >
          {{ getStatusText(moduleStats?.status) }}
        </el-tag>
      </div>
    </div>

    <!-- 卡片主体 -->
    <div class="card-body">
      <!-- 加载状态 -->
      <div v-if="loading" class="loading-state">
        <el-skeleton :rows="3" animated />
      </div>

      <!-- 错误状态 -->
      <div v-else-if="error" class="error-state">
        <el-icon><Warning /></el-icon>
        <span>加载失败</span>
      </div>

      <!-- 正常内容 -->
      <div v-else>
        <!-- 统计数据 -->
        <div class="module-stats" v-if="moduleStats">
          <div class="stat-item">
            <div class="stat-value">{{ moduleStats.total_count || 0 }}</div>
            <div class="stat-label">{{ moduleConfig.countLabel }}</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ moduleStats.completed_count || 0 }}</div>
            <div class="stat-label">已完成</div>
          </div>
        </div>

        <!-- 预览内容 -->
        <div class="module-preview" v-if="moduleStats?.recent_items?.length">
          <div
            v-for="item in moduleStats.recent_items.slice(0, 3)"
            :key="item.id"
            class="preview-item"
          >
            <div class="item-title">{{ item.title }}</div>
            <div class="item-meta">{{ formatDate(item.updated_at) }}</div>
          </div>
        </div>

        <!-- 空状态 -->
        <div v-else class="empty-state">
          <el-icon><Plus /></el-icon>
          <span>{{ moduleConfig.emptyText }}</span>
        </div>
      </div>
    </div>

    <!-- 卡片底部 -->
    <div class="card-footer">
      <!-- 进度条 -->
      <div class="module-progress" v-if="moduleStats && moduleStats.total_count > 0">
        <div class="progress-text">
          完成度 {{ Math.round(moduleStats.completion_percentage || 0) }}%
        </div>
        <el-progress
          :percentage="moduleStats.completion_percentage || 0"
          :stroke-width="4"
          :show-text="false"
          :color="moduleConfig.color"
        />
      </div>

      <!-- 操作按钮 -->
      <div class="module-actions">
        <el-button
          v-if="moduleConfig.quickAction"
          type="text"
          size="small"
          class="action-btn quick-btn"
          @click="handleQuickAction"
          :loading="actionLoading"
        >
          <el-icon><component :is="moduleConfig.quickAction.icon" /></el-icon>
        </el-button>
        
        <el-button
          type="primary"
          size="small"
          class="action-btn enter-btn"
          @click="enterModule"
        >
          进入
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Warning,
  Plus,
  Location,
  User,
  List,
  Document,
  Timer,
  Setting,
  MagicStick,
  EditPen
} from '@element-plus/icons-vue'
import type { ModuleStats } from '@/api/workspace'

// Props
interface Props {
  moduleName: string
  moduleStats?: ModuleStats
  novelId: number
  loading?: boolean
  error?: string
}

const props = withDefaults(defineProps<Props>(), {
  moduleStats: undefined,
  loading: false,
  error: ''
})

// Emits
const emit = defineEmits<{
  quickAction: [moduleName: string]
  refreshModule: [moduleName: string]
}>()

// Router
const router = useRouter()

// 响应式数据
const actionLoading = ref(false)

// 模块配置
const moduleConfigs = {
  worldview: {
    title: '世界观',
    description: '构建小说世界的基础设定',
    countLabel: '设定项',
    emptyText: '开始构建世界观',
    color: '#E6A23C',
    icon: 'Location',
    quickAction: {
      icon: 'MagicStick',
      action: 'generate'
    }
  },
  characters: {
    title: '角色',
    description: '创建和管理小说角色',
    countLabel: '角色数',
    emptyText: '添加第一个角色',
    color: '#F56C6C',
    icon: 'User',
    quickAction: {
      icon: 'EditPen',
      action: 'create'
    }
  },
  outline: {
    title: '大纲',
    description: '规划小说整体结构',
    countLabel: '章节数',
    emptyText: '制定创作大纲',
    color: '#909399',
    icon: 'List',
    quickAction: {
      icon: 'MagicStick',
      action: 'generate'
    }
  },
  chapters: {
    title: '章节',
    description: '编写小说具体内容',
    countLabel: '章节数',
    emptyText: '开始写作章节',
    color: '#409EFF',
    icon: 'Document',
    quickAction: {
      icon: 'EditPen',
      action: 'create'
    }
  },
  timeline: {
    title: '时间轴',
    description: '管理故事时间线',
    countLabel: '事件数',
    emptyText: '创建时间轴事件',
    color: '#67C23A',
    icon: 'Timer',
    quickAction: {
      icon: 'Plus',
      action: 'create'
    }
  },
  settings: {
    title: '设置',
    description: '配置小说和工作台',
    countLabel: '配置项',
    emptyText: '个性化设置',
    color: '#606266',
    icon: 'Setting',
    quickAction: null
  }
}

// 计算属性
const moduleConfig = computed(() => {
  return moduleConfigs[props.moduleName as keyof typeof moduleConfigs] || moduleConfigs.worldview
})

const moduleIcon = computed(() => {
  const iconMap: Record<string, any> = {
    Location,
    User,
    List,
    Document,
    Timer,
    Setting
  }
  return iconMap[moduleConfig.value.icon] || Location
})

// 方法
const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  
  if (days === 0) {
    return '今天'
  } else if (days === 1) {
    return '昨天'
  } else if (days < 7) {
    return `${days}天前`
  } else {
    return date.toLocaleDateString('zh-CN', {
      month: 'short',
      day: 'numeric'
    })
  }
}

const getStatusType = (status?: string) => {
  switch (status) {
    case 'complete':
      return 'success'
    case 'partial':
      return 'warning'
    case 'empty':
    default:
      return 'info'
  }
}

const getStatusText = (status?: string) => {
  switch (status) {
    case 'complete':
      return '已完成'
    case 'partial':
      return '进行中'
    case 'empty':
    default:
      return '未开始'
  }
}

const handleQuickAction = async () => {
  if (!moduleConfig.value.quickAction) return
  
  try {
    actionLoading.value = true
    
    // 触发快捷操作事件
    emit('quickAction', props.moduleName)
    
    // 根据操作类型执行不同逻辑
    const { action } = moduleConfig.value.quickAction
    
    switch (action) {
      case 'generate':
        ElMessage.info(`正在生成${moduleConfig.value.title}...`)
        break
      case 'create':
        // 跳转到创建页面
        router.push(`/workspace/${props.novelId}/${props.moduleName}?action=create`)
        return
      default:
        break
    }
    
    // 模拟操作完成
    setTimeout(() => {
      ElMessage.success(`${moduleConfig.value.title}操作完成`)
      emit('refreshModule', props.moduleName)
    }, 1500)
    
  } catch (error) {
    console.error('快捷操作失败:', error)
    ElMessage.error('操作失败，请稍后重试')
  } finally {
    setTimeout(() => {
      actionLoading.value = false
    }, 1500)
  }
}

const enterModule = () => {
  // 跳转到对应模块页面
  router.push(`/workspace/${props.novelId}/${props.moduleName}`)
}
</script>

<style scoped lang="scss">
.module-card {
  background: #ffffff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  height: 280px;
  display: flex;
  flex-direction: column;

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  }

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: var(--module-color);
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 16px;

    .module-info {
      flex: 1;

      .module-title {
        font-size: 18px;
        font-weight: 600;
        color: #303133;
        margin: 0 0 4px 0;
        display: flex;
        align-items: center;
        gap: 8px;

        .module-icon {
          font-size: 20px;
          color: var(--module-color);
        }
      }

      .module-description {
        color: #909399;
        font-size: 13px;
        margin: 0;
      }
    }

    .module-status {
      .status-badge {
        padding: 4px 8px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 500;

        &.complete {
          background: #F0F9FF;
          color: #409EFF;
        }

        &.partial {
          background: #FDF6EC;
          color: #E6A23C;
        }

        &.empty {
          background: #F0F0F0;
          color: #909399;
        }
      }
    }
  }

  .card-body {
    flex: 1;
    margin-bottom: 16px;

    .loading-state,
    .error-state,
    .empty-state {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      height: 100%;
      color: #909399;
      font-size: 14px;
      gap: 8px;
    }

    .error-state {
      color: #F56C6C;
    }

    .module-stats {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 12px;
      margin-bottom: 16px;

      .stat-item {
        text-align: center;

        .stat-value {
          font-size: 20px;
          font-weight: 600;
          color: var(--module-color);
          margin-bottom: 4px;
        }

        .stat-label {
          font-size: 12px;
          color: #909399;
        }
      }
    }

    .module-preview {
      .preview-item {
        padding: 8px 0;
        border-bottom: 1px solid #F2F6FC;
        
        &:last-child {
          border-bottom: none;
        }

        .item-title {
          font-size: 13px;
          color: #606266;
          font-weight: 500;
          margin-bottom: 2px;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }

        .item-meta {
          color: #909399;
          font-size: 12px;
        }
      }
    }

    .empty-state {
      .el-icon {
        font-size: 32px;
        color: #DCDFE6;
      }
    }
  }

  .card-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;

    .module-progress {
      flex: 1;
      margin-right: 12px;

      .progress-text {
        font-size: 12px;
        color: #909399;
        margin-bottom: 4px;
      }
    }

    .module-actions {
      display: flex;
      gap: 8px;

      .action-btn {
        padding: 6px 12px;
        border-radius: 16px;
        font-size: 12px;

        &.enter-btn {
          background: var(--module-color);
          border-color: var(--module-color);
          color: white;

          &:hover {
            opacity: 0.9;
          }
        }

        &.quick-btn {
          color: var(--module-color);
          
          &:hover {
            background: rgba(var(--module-color-rgb), 0.1);
          }
        }
      }
    }
  }

  // 模块特定颜色
  &.worldview-card {
    --module-color: #E6A23C;
    --module-color-rgb: 230, 162, 60;
  }

  &.characters-card {
    --module-color: #F56C6C;
    --module-color-rgb: 245, 108, 108;
  }

  &.outline-card {
    --module-color: #909399;
    --module-color-rgb: 144, 147, 153;
  }

  &.chapters-card {
    --module-color: #409EFF;
    --module-color-rgb: 64, 158, 255;
  }

  &.timeline-card {
    --module-color: #67C23A;
    --module-color-rgb: 103, 194, 58;
  }

  &.settings-card {
    --module-color: #606266;
    --module-color-rgb: 96, 98, 102;
  }
}

// 响应式设计
@media (max-width: 1023px) {
  .module-card {
    height: 260px;
    padding: 20px;
  }
}

@media (max-width: 767px) {
  .module-card {
    height: 200px;
    padding: 16px;

    .card-header {
      .module-info {
        .module-title {
          font-size: 16px;
        }
      }
    }

    .card-body {
      .module-stats {
        gap: 8px;

        .stat-item {
          .stat-value {
            font-size: 18px;
          }
        }
      }
    }
  }
}
</style>