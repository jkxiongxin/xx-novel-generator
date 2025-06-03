<template>
  <el-card class="stats-card" shadow="hover">
    <template #header>
      <div class="card-header">
        <h3>创作统计</h3>
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

    <div v-loading="loading" class="stats-content">
      <!-- 基础统计 -->
      <div class="stats-group">
        <h4 class="group-title">基础数据</h4>
        <div class="stats-grid">
          <div class="stat-item">
            <el-statistic
              :value="stats.total_words"
              title="总字数"
              :formatter="formatWordCount"
            >
              <template #suffix>
                <el-icon class="stat-icon"><Document /></el-icon>
              </template>
            </el-statistic>
          </div>
          
          <div class="stat-item">
            <el-statistic
              :value="stats.total_chapters"
              title="总章节"
            >
              <template #suffix>
                <el-icon class="stat-icon"><Notebook /></el-icon>
              </template>
            </el-statistic>
          </div>
          
          <div class="stat-item">
            <el-statistic
              :value="stats.completed_chapters"
              title="已完成章节"
            >
              <template #suffix>
                <el-icon class="stat-icon completed"><Select /></el-icon>
              </template>
            </el-statistic>
          </div>
          
          <div class="stat-item">
            <el-statistic
              :value="stats.draft_chapters"
              title="草稿章节"
            >
              <template #suffix>
                <el-icon class="stat-icon draft"><EditPen /></el-icon>
              </template>
            </el-statistic>
          </div>
        </div>
      </div>

      <!-- 写作效率 -->
      <div class="stats-group">
        <h4 class="group-title">写作效率</h4>
        <div class="stats-grid">
          <div class="stat-item">
            <el-statistic
              :value="stats.average_words_per_chapter"
              title="平均章节字数"
              :formatter="formatNumber"
            >
              <template #suffix>
                <span class="unit">字/章</span>
              </template>
            </el-statistic>
          </div>
          
          <div class="stat-item">
            <el-statistic
              :value="stats.writing_days"
              title="写作天数"
            >
              <template #suffix>
                <span class="unit">天</span>
              </template>
            </el-statistic>
          </div>
          
          <div class="stat-item">
            <el-statistic
              :value="stats.average_daily_words"
              title="日均字数"
              :formatter="formatNumber"
            >
              <template #suffix>
                <span class="unit">字/天</span>
              </template>
            </el-statistic>
          </div>
          
          <div class="stat-item">
            <div class="completion-rate">
              <div class="rate-label">完成率</div>
              <div class="rate-value">
                {{ completionRate }}%
              </div>
              <el-progress 
                :percentage="completionRate" 
                :color="progressColor"
                :stroke-width="6"
                :show-text="false"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- 时间预估 -->
      <div v-if="stats.estimated_completion_time" class="stats-group">
        <h4 class="group-title">时间预估</h4>
        <div class="estimation-card">
          <el-icon class="time-icon"><Timer /></el-icon>
          <div class="estimation-content">
            <div class="estimation-label">预计完成时间</div>
            <div class="estimation-value">{{ stats.estimated_completion_time }}</div>
          </div>
        </div>
      </div>

      <!-- 趋势指标 -->
      <div class="stats-group">
        <h4 class="group-title">趋势分析</h4>
        <div class="trend-items">
          <div class="trend-item">
            <div class="trend-label">写作活跃度</div>
            <div class="trend-value">
              <el-rate 
                :model-value="activityRate" 
                disabled 
                show-score 
                :colors="['#99A9BF', '#F7BA2A', '#FF9900']"
              />
            </div>
          </div>
          
          <div class="trend-item">
            <div class="trend-label">内容丰富度</div>
            <div class="trend-badges">
              <el-tag v-if="stats.total_chapters > 10" type="success" size="small">
                章节充实
              </el-tag>
              <el-tag v-if="stats.average_words_per_chapter > 2000" type="success" size="small">
                内容详细
              </el-tag>
              <el-tag v-if="stats.writing_days > 30" type="success" size="small">
                坚持创作
              </el-tag>
            </div>
          </div>
        </div>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { 
  Refresh, 
  Document, 
  Notebook, 
  Select, 
  EditPen, 
  Timer 
} from '@element-plus/icons-vue'

interface Stats {
  total_chapters: number
  completed_chapters: number
  draft_chapters: number
  total_words: number
  average_words_per_chapter: number
  estimated_completion_time?: string
  writing_days: number
  average_daily_words: number
}

interface Props {
  stats: Stats
  loading?: boolean
}

interface Emits {
  (e: 'refresh'): void
}

const props = withDefaults(defineProps<Props>(), {
  loading: false
})

defineEmits<Emits>()

// 计算属性
const completionRate = computed(() => {
  if (props.stats.total_chapters === 0) return 0
  return Math.round((props.stats.completed_chapters / props.stats.total_chapters) * 100)
})

const progressColor = computed(() => {
  const rate = completionRate.value
  if (rate >= 80) return '#67C23A'
  if (rate >= 60) return '#E6A23C'
  if (rate >= 40) return '#F56C6C'
  return '#909399'
})

const activityRate = computed(() => {
  // 基于写作天数和日均字数计算活跃度评分
  const dailyWords = props.stats.average_daily_words
  const writingDays = props.stats.writing_days
  
  let score = 0
  
  // 日均字数评分 (最高3分)
  if (dailyWords >= 2000) score += 3
  else if (dailyWords >= 1000) score += 2
  else if (dailyWords >= 500) score += 1
  
  // 写作持续性评分 (最高2分)
  if (writingDays >= 30) score += 2
  else if (writingDays >= 7) score += 1
  
  return Math.min(score, 5)
})

// 方法定义
const formatWordCount = (value: number) => {
  if (value >= 10000) {
    return `${(value / 10000).toFixed(1)}万`
  }
  return value.toLocaleString()
}

const formatNumber = (value: number) => {
  return value.toLocaleString()
}
</script>

<style scoped lang="scss">
.stats-card {
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

.stats-content {
  min-height: 400px;
}

.stats-group {
  margin-bottom: 24px;
  
  &:last-child {
    margin-bottom: 0;
  }
  
  .group-title {
    font-size: 14px;
    font-weight: 600;
    color: #606266;
    margin: 0 0 16px 0;
    padding-bottom: 8px;
    border-bottom: 1px solid #f0f0f0;
  }
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
    gap: 12px;
  }
}

.stat-item {
  padding: 16px;
  background: #fafafa;
  border-radius: 8px;
  border: 1px solid #f0f0f0;
  transition: all 0.3s;
  
  &:hover {
    background: #f5f7fa;
    border-color: #e4e7ed;
  }
  
  :deep(.el-statistic) {
    .el-statistic__head {
      font-size: 12px;
      color: #909399;
      margin-bottom: 8px;
    }
    
    .el-statistic__content {
      display: flex;
      align-items: center;
      gap: 8px;
      
      .el-statistic__number {
        font-size: 20px;
        font-weight: 600;
        color: #303133;
      }
    }
  }
  
  .stat-icon {
    font-size: 16px;
    color: #409EFF;
    
    &.completed {
      color: #67C23A;
    }
    
    &.draft {
      color: #E6A23C;
    }
  }
  
  .unit {
    font-size: 12px;
    color: #909399;
  }
}

.completion-rate {
  .rate-label {
    font-size: 12px;
    color: #909399;
    margin-bottom: 8px;
  }
  
  .rate-value {
    font-size: 20px;
    font-weight: 600;
    color: #303133;
    margin-bottom: 8px;
  }
}

.estimation-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 8px;
  color: white;
  
  .time-icon {
    font-size: 24px;
    opacity: 0.8;
  }
  
  .estimation-content {
    .estimation-label {
      font-size: 12px;
      opacity: 0.8;
      margin-bottom: 4px;
    }
    
    .estimation-value {
      font-size: 16px;
      font-weight: 600;
    }
  }
}

.trend-items {
  .trend-item {
    margin-bottom: 16px;
    
    &:last-child {
      margin-bottom: 0;
    }
    
    .trend-label {
      font-size: 12px;
      color: #909399;
      margin-bottom: 8px;
    }
    
    .trend-value {
      :deep(.el-rate) {
        .el-rate__text {
          font-size: 12px;
          color: #606266;
        }
      }
    }
    
    .trend-badges {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }
  }
}

// 响应式调整
@media (max-width: 768px) {
  .stats-content {
    min-height: auto;
  }
  
  .stats-group {
    margin-bottom: 20px;
  }
  
  .stat-item {
    padding: 12px;
    
    :deep(.el-statistic__number) {
      font-size: 18px;
    }
  }
  
  .estimation-card {
    padding: 12px;
    
    .time-icon {
      font-size: 20px;
    }
    
    .estimation-value {
      font-size: 14px;
    }
  }
}
</style>