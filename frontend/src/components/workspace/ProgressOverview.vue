<template>
  <div class="progress-overview">
    <div class="overview-header">
      <h3 class="overview-title">创作进度总览</h3>
      <div class="header-actions">
        <el-button
          type="text"
          size="small"
          @click="viewDetailedStats"
        >
          <el-icon><TrendCharts /></el-icon>
          详细统计
        </el-button>
        <el-button
          type="text"
          size="small"
          @click="exportProgressReport"
          :loading="exportLoading"
        >
          <el-icon><Download /></el-icon>
          导出报告
        </el-button>
      </div>
    </div>

    <div class="overview-content">
      <!-- 统计数据区域 -->
      <div class="stats-section">
        <div class="section-title">写作统计</div>
        <div class="stats-grid" v-if="writingStats">
          <div class="stat-row">
            <span class="stat-label">总字数</span>
            <span class="stat-value">{{ formatNumber(progress?.word_count || 0) }}</span>
          </div>
          <div class="stat-row">
            <span class="stat-label">章节数</span>
            <span class="stat-value">{{ progress?.chapter_count || 0 }}</span>
          </div>
          <div class="stat-row">
            <span class="stat-label">写作天数</span>
            <span class="stat-value">{{ writingStats.writing_days }}</span>
          </div>
          <div class="stat-row">
            <span class="stat-label">日均字数</span>
            <span class="stat-value">{{ Math.round(writingStats.average_daily_words) }}</span>
          </div>
          <div class="stat-row">
            <span class="stat-label">连续天数</span>
            <span class="stat-value">{{ writingStats.writing_streak }}</span>
          </div>
          <div class="stat-row">
            <span class="stat-label">写作趋势</span>
            <span :class="['stat-value', `trend-${writingStats.productivity_trend}`]">
              {{ getTrendText(writingStats.productivity_trend) }}
            </span>
          </div>
        </div>
        <div v-else class="loading-placeholder">
          <el-skeleton :rows="3" animated />
        </div>
      </div>

      <!-- 进度图表区域 -->
      <div class="chart-section">
        <div class="section-title">进度趋势</div>
        <div class="chart-container" ref="chartContainer">
          <div v-if="chartLoading" class="chart-loading">
            <el-skeleton animated>
              <template #template>
                <el-skeleton-item variant="rect" style="width: 100%; height: 200px;" />
              </template>
            </el-skeleton>
          </div>
          <div v-else-if="!chartData.length" class="chart-empty">
            <el-icon><TrendCharts /></el-icon>
            <span>暂无数据</span>
          </div>
          <div v-else class="simple-chart">
            <div class="chart-bars">
              <div
                v-for="(item, index) in chartData.slice(-7)"
                :key="index"
                class="chart-bar"
                :style="{ height: `${(item.words / Math.max(...chartData.map(d => d.words))) * 100}%` }"
              >
                <div class="bar-value">{{ item.words }}</div>
                <div class="bar-label">{{ item.date }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 最近活动区域 -->
      <div class="activity-section">
        <div class="section-title">最近活动</div>
        <div class="activity-list" v-if="recentActivities?.length">
          <div
            v-for="activity in recentActivities.slice(0, 8)"
            :key="activity.id"
            class="activity-item"
          >
            <div class="activity-content">
              <el-icon class="activity-icon">
                <component :is="getActivityIcon(activity.type)" />
              </el-icon>
              <span class="activity-text">{{ activity.description }}</span>
            </div>
            <div class="activity-time">{{ formatActivityTime(activity.timestamp) }}</div>
          </div>
        </div>
        <div v-else-if="activitiesLoading" class="loading-placeholder">
          <el-skeleton :rows="4" animated />
        </div>
        <div v-else class="activity-empty">
          <el-icon><Clock /></el-icon>
          <span>暂无活动记录</span>
        </div>
      </div>
    </div>

    <!-- 里程碑进度 -->
    <div class="milestones-section" v-if="progress?.milestones?.length">
      <div class="section-title">创作里程碑</div>
      <div class="milestones-grid">
        <div
          v-for="milestone in progress.milestones"
          :key="milestone.id"
          :class="['milestone-item', { completed: milestone.completed }]"
        >
          <div class="milestone-progress">
            <el-progress
              type="circle"
              :percentage="milestone.progress"
              :width="50"
              :stroke-width="4"
              :color="milestone.completed ? '#67C23A' : '#409EFF'"
            />
          </div>
          <div class="milestone-info">
            <div class="milestone-title">{{ milestone.title }}</div>
            <div class="milestone-date">{{ formatDate(milestone.target_date) }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, watch, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  TrendCharts,
  Download,
  Clock,
  Document,
  User,
  List,
  EditPen,
  Timer
} from '@element-plus/icons-vue'
// import * as echarts from 'echarts' // 暂时注释，后续可安装echarts
import { WorkspaceService, type ProgressOverview, type WritingStats, type Activity } from '@/api/workspace'

// Props
interface Props {
  novelId: number
  progress?: ProgressOverview
  writingStats?: WritingStats
  recentActivities?: Activity[]
}

const props = withDefaults(defineProps<Props>(), {
  progress: undefined,
  writingStats: undefined,
  recentActivities: undefined
})

// 响应式数据
const chartContainer = ref<HTMLElement>()
const chartLoading = ref(false)
const activitiesLoading = ref(false)
const exportLoading = ref(false)
const chartData = ref<Array<{ date: string; words: number; chapters: number }>>([])

// 方法
const formatNumber = (num: number): string => {
  if (num >= 10000) {
    return `${(num / 10000).toFixed(1)}万`
  }
  return num.toLocaleString()
}

const getTrendText = (trend: string): string => {
  switch (trend) {
    case 'increasing':
      return '上升'
    case 'stable':
      return '稳定'
    case 'decreasing':
      return '下降'
    default:
      return '未知'
  }
}

const formatDate = (dateString: string): string => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    month: 'short',
    day: 'numeric'
  })
}

const formatActivityTime = (timestamp: string): string => {
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const hours = Math.floor(diff / (1000 * 60 * 60))
  const days = Math.floor(hours / 24)
  
  if (days > 0) {
    return `${days}天前`
  } else if (hours > 0) {
    return `${hours}小时前`
  } else {
    return '刚刚'
  }
}

const getActivityIcon = (type: string) => {
  switch (type) {
    case 'chapter_created':
    case 'chapter_updated':
      return Document
    case 'character_added':
    case 'character_updated':
      return User
    case 'outline_updated':
      return List
    case 'worldview_modified':
      return Timer
    default:
      return EditPen
  }
}

const initChart = async () => {
  try {
    chartLoading.value = true
    
    // 模拟加载图表数据
    await new Promise(resolve => setTimeout(resolve, 500))
    
    // 生成模拟数据
    const data = generateMockChartData()
    chartData.value = data
    
  } catch (error) {
    console.error('初始化图表失败:', error)
  } finally {
    chartLoading.value = false
  }
}

const generateMockChartData = () => {
  const data = []
  const now = new Date()
  
  for (let i = 29; i >= 0; i--) {
    const date = new Date(now.getTime() - i * 24 * 60 * 60 * 1000)
    data.push({
      date: date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' }),
      words: Math.floor(Math.random() * 2000) + 500,
      chapters: Math.floor(Math.random() * 3)
    })
  }
  
  return data
}

const viewDetailedStats = () => {
  ElMessage.info('打开详细统计面板')
  // 这里可以打开一个详细统计的模态框
}

const exportProgressReport = async () => {
  try {
    exportLoading.value = true
    
    const report = await WorkspaceService.generateProgressReport(props.novelId, {
      format: 'summary',
      include_sections: ['stats', 'progress', 'activities']
    })
    
    // 模拟文件下载
    const content = `创作进度报告
    
总字数: ${props.progress?.word_count || 0}
章节数: ${props.progress?.chapter_count || 0}
整体进度: ${Math.round(props.progress?.overall_progress || 0)}%

生成时间: ${new Date().toLocaleString()}
    `
    
    const blob = new Blob([content], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `创作报告_${new Date().getTime()}.txt`
    a.click()
    URL.revokeObjectURL(url)
    
    ElMessage.success('报告导出成功')
    
  } catch (error) {
    console.error('导出报告失败:', error)
    ElMessage.error('导出失败，请稍后重试')
  } finally {
    exportLoading.value = false
  }
}

const resizeChart = () => {
  // 简化版本不需要resize
}

// 监听数据变化
watch(() => props.progress, () => {
  // 重新生成图表数据
  nextTick(() => {
    initChart()
  })
}, { deep: true })

// 生命周期
onMounted(() => {
  nextTick(() => {
    initChart()
  })
  
  // 监听窗口大小变化
  window.addEventListener('resize', resizeChart)
})

onUnmounted(() => {
  // 移除事件监听器
  window.removeEventListener('resize', resizeChart)
})
</script>

<style scoped lang="scss">
.progress-overview {
  background: #ffffff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);

  .overview-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;

    .overview-title {
      font-size: 18px;
      font-weight: 600;
      color: #303133;
      margin: 0;
    }

    .header-actions {
      display: flex;
      gap: 8px;
    }
  }

  .overview-content {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 24px;
    margin-bottom: 24px;

    .stats-section {
      .section-title {
        font-size: 14px;
        font-weight: 500;
        color: #606266;
        margin-bottom: 12px;
      }

      .stats-grid {
        display: grid;
        gap: 8px;

        .stat-row {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 4px 0;

          .stat-label {
            color: #909399;
            font-size: 13px;
          }

          .stat-value {
            font-weight: 500;
            color: #303133;
            font-size: 13px;

            &.trend-increasing {
              color: #67C23A;
            }

            &.trend-stable {
              color: #409EFF;
            }

            &.trend-decreasing {
              color: #F56C6C;
            }
          }
        }
      }
    }

    .chart-section {
      .section-title {
        font-size: 14px;
        font-weight: 500;
        color: #606266;
        margin-bottom: 12px;
      }

      .chart-container {
        height: 200px;
        width: 100%;

        .chart-loading,
        .chart-empty {
          display: flex;
          align-items: center;
          justify-content: center;
          height: 100%;
          color: #909399;
          flex-direction: column;
          gap: 8px;
        }

        .simple-chart {
          height: 100%;
          padding: 16px 0;

          .chart-bars {
            display: flex;
            align-items: flex-end;
            justify-content: space-between;
            height: 160px;
            gap: 8px;

            .chart-bar {
              flex: 1;
              background: linear-gradient(to top, #409EFF, #67C23A);
              border-radius: 4px 4px 0 0;
              position: relative;
              min-height: 20px;
              transition: all 0.3s ease;

              &:hover {
                opacity: 0.8;
                transform: scaleY(1.05);
              }

              .bar-value {
                position: absolute;
                top: -20px;
                left: 50%;
                transform: translateX(-50%);
                font-size: 11px;
                color: #606266;
                font-weight: 500;
                white-space: nowrap;
              }

              .bar-label {
                position: absolute;
                bottom: -25px;
                left: 50%;
                transform: translateX(-50%);
                font-size: 10px;
                color: #909399;
                white-space: nowrap;
              }
            }
          }
        }
      }
    }

    .activity-section {
      .section-title {
        font-size: 14px;
        font-weight: 500;
        color: #606266;
        margin-bottom: 12px;
      }

      .activity-list {
        max-height: 200px;
        overflow-y: auto;

        .activity-item {
          padding: 8px 0;
          border-bottom: 1px solid #F2F6FC;

          &:last-child {
            border-bottom: none;
          }

          .activity-content {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 13px;
            color: #606266;
            margin-bottom: 2px;

            .activity-icon {
              color: #909399;
              font-size: 14px;
            }

            .activity-text {
              flex: 1;
            }
          }

          .activity-time {
            font-size: 12px;
            color: #C0C4CC;
            padding-left: 22px;
          }
        }
      }

      .activity-empty {
        display: flex;
        align-items: center;
        justify-content: center;
        height: 100px;
        color: #909399;
        flex-direction: column;
        gap: 8px;
      }
    }

    .loading-placeholder {
      padding: 12px 0;
    }
  }

  .milestones-section {
    border-top: 1px solid #F2F6FC;
    padding-top: 20px;

    .section-title {
      font-size: 14px;
      font-weight: 500;
      color: #606266;
      margin-bottom: 12px;
    }

    .milestones-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 16px;

      .milestone-item {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px;
        border-radius: 8px;
        background: #F8F9FA;

        &.completed {
          background: #F0F9FF;
        }

        .milestone-info {
          flex: 1;

          .milestone-title {
            font-size: 13px;
            font-weight: 500;
            color: #303133;
            margin-bottom: 4px;
          }

          .milestone-date {
            font-size: 12px;
            color: #909399;
          }
        }
      }
    }
  }
}

// 响应式设计
@media (max-width: 1023px) {
  .progress-overview {
    .overview-content {
      grid-template-columns: 1fr;
      gap: 20px;
    }

    .milestones-section {
      .milestones-grid {
        grid-template-columns: 1fr;
      }
    }
  }
}

@media (max-width: 767px) {
  .progress-overview {
    padding: 16px;

    .overview-header {
      flex-direction: column;
      gap: 12px;
      align-items: flex-start;

      .header-actions {
        width: 100%;
        justify-content: center;
      }
    }
  }
}
</style>