<template>
  <el-card class="progress-section-card" shadow="hover">
    <template #header>
      <div class="card-header">
        <h3>创作进度</h3>
        <el-tag :type="getStatusTagType(novel.status)">
          {{ NovelUtils.getStatusText(novel.status) }}
        </el-tag>
      </div>
    </template>

    <div class="progress-content">
      <!-- 总体进度 -->
      <div class="overall-progress">
        <div class="progress-header">
          <span class="progress-title">完成进度</span>
          <span class="progress-stats">
            {{ formatWordCount(novel.word_count) }}
            <span v-if="novel.target_words">
              / {{ formatWordCount(novel.target_words) }}
            </span>
          </span>
        </div>
        
        <div class="progress-bar-container">
          <el-progress 
            :percentage="novel.progress_percentage"
            :color="getProgressColor(novel.progress_percentage)"
            :stroke-width="12"
            :show-text="false"
          />
          <span class="progress-percentage">{{ novel.progress_percentage }}%</span>
        </div>
        
        <div v-if="novel.target_words" class="progress-details">
          <div class="detail-item">
            <span class="label">剩余字数：</span>
            <span class="value">{{ formatWordCount(novel.target_words - novel.word_count) }}</span>
          </div>
          <div v-if="estimatedDays > 0" class="detail-item">
            <span class="label">预计完成：</span>
            <span class="value">{{ estimatedDays }} 天后</span>
          </div>
        </div>
      </div>

      <!-- 章节进度 -->
      <div class="chapter-progress">
        <div class="section-title">
          <h4>章节统计</h4>
          <el-button 
            type="text" 
            size="small" 
            @click="$emit('quick-access', 'chapters')"
          >
            管理章节
          </el-button>
        </div>
        
        <div class="chapter-stats">
          <div class="stat-circle">
            <el-progress 
              type="circle" 
              :percentage="chapterCompletionRate"
              :width="80"
              :color="getProgressColor(chapterCompletionRate)"
            >
              <template #default="{ percentage }">
                <span class="circle-text">{{ percentage }}%</span>
              </template>
            </el-progress>
            <div class="circle-label">章节完成率</div>
          </div>
          
          <div class="stat-details">
            <div class="stat-row">
              <span class="stat-label">总章节：</span>
              <span class="stat-value">{{ novel.stats.total_chapters }}</span>
            </div>
            <div class="stat-row">
              <span class="stat-label">已完成：</span>
              <span class="stat-value completed">{{ novel.stats.completed_chapters }}</span>
            </div>
            <div class="stat-row">
              <span class="stat-label">草稿：</span>
              <span class="stat-value draft">{{ novel.stats.draft_chapters }}</span>
            </div>
            <div class="stat-row">
              <span class="stat-label">平均字数：</span>
              <span class="stat-value">{{ novel.stats.average_words_per_chapter }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 快捷操作 -->
      <div class="quick-actions">
        <div class="section-title">
          <h4>快捷操作</h4>
        </div>
        
        <div class="action-grid">
          <div 
            class="action-item"
            @click="$emit('quick-access', 'worldview')"
          >
            <div class="action-icon worldview">
              <el-icon><Connection /></el-icon>
            </div>
            <div class="action-content">
              <div class="action-name">世界观</div>
              <div class="action-desc">设定背景</div>
            </div>
          </div>
          
          <div 
            class="action-item"
            @click="$emit('quick-access', 'characters')"
          >
            <div class="action-icon characters">
              <el-icon><User /></el-icon>
            </div>
            <div class="action-content">
              <div class="action-name">角色</div>
              <div class="action-desc">管理人物</div>
            </div>
          </div>
          
          <div 
            class="action-item"
            @click="$emit('quick-access', 'outline')"
          >
            <div class="action-icon outline">
              <el-icon><List /></el-icon>
            </div>
            <div class="action-content">
              <div class="action-name">大纲</div>
              <div class="action-desc">规划情节</div>
            </div>
          </div>
          
          <div 
            class="action-item"
            @click="$emit('quick-access', 'chapters')"
          >
            <div class="action-icon chapters">
              <el-icon><Document /></el-icon>
            </div>
            <div class="action-content">
              <div class="action-name">章节</div>
              <div class="action-desc">开始写作</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 写作目标 -->
      <div v-if="novel.target_words" class="writing-goals">
        <div class="section-title">
          <h4>写作目标</h4>
          <el-button 
            type="text" 
            size="small"
            @click="showGoalDialog = true"
          >
            调整目标
          </el-button>
        </div>
        
        <div class="goal-content">
          <div class="goal-item">
            <div class="goal-icon">
              <el-icon><Flag /></el-icon>
            </div>
            <div class="goal-info">
              <div class="goal-label">总字数目标</div>
              <div class="goal-value">{{ formatWordCount(novel.target_words) }}</div>
            </div>
            <div class="goal-progress">
              <el-progress 
                :percentage="novel.progress_percentage"
                :show-text="false"
                :stroke-width="4"
                :color="getProgressColor(novel.progress_percentage)"
              />
            </div>
          </div>
          
          <div v-if="dailyTarget > 0" class="goal-item">
            <div class="goal-icon">
              <el-icon><Calendar /></el-icon>
            </div>
            <div class="goal-info">
              <div class="goal-label">日均目标</div>
              <div class="goal-value">{{ dailyTarget }} 字/天</div>
            </div>
            <div class="goal-status">
              <el-tag 
                :type="dailyTargetStatus.type" 
                size="small"
              >
                {{ dailyTargetStatus.text }}
              </el-tag>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 目标设置对话框 -->
    <el-dialog
      v-model="showGoalDialog"
      title="调整写作目标"
      width="400px"
    >
      <el-form :model="goalForm" label-width="100px">
        <el-form-item label="目标字数">
          <el-input-number
            v-model="goalForm.targetWords"
            :min="novel.word_count"
            :max="10000000"
            :step="1000"
            controls-position="right"
          />
          <span class="form-help">字</span>
        </el-form-item>
        <el-form-item label="完成期限">
          <el-date-picker
            v-model="goalForm.deadline"
            type="date"
            placeholder="选择目标完成日期"
            :disabled-date="disabledDate"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showGoalDialog = false">取消</el-button>
        <el-button type="primary" @click="updateGoal">确定</el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup lang="ts">
import { ref, computed, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  Connection, 
  User, 
  List, 
  Document, 
  Flag, 
  Calendar 
} from '@element-plus/icons-vue'
import { NovelUtils, type NovelDetailResponse } from '@/api/novels'

interface Props {
  novel: NovelDetailResponse
}

interface Emits {
  (e: 'quick-access', module: string): void
  (e: 'update-goal', data: { targetWords: number; deadline?: Date }): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// 响应式数据
const showGoalDialog = ref(false)
const goalForm = reactive({
  targetWords: 0,
  deadline: null as Date | null
})

// 计算属性
const chapterCompletionRate = computed(() => {
  if (props.novel.stats.total_chapters === 0) return 0
  return Math.round((props.novel.stats.completed_chapters / props.novel.stats.total_chapters) * 100)
})

const estimatedDays = computed(() => {
  if (!props.novel.target_words || props.novel.stats.average_daily_words <= 0) return 0
  const remainingWords = props.novel.target_words - props.novel.word_count
  return Math.ceil(remainingWords / props.novel.stats.average_daily_words)
})

const dailyTarget = computed(() => {
  if (!props.novel.target_words) return 0
  const remainingWords = props.novel.target_words - props.novel.word_count
  const remainingDays = estimatedDays.value
  return remainingDays > 0 ? Math.ceil(remainingWords / remainingDays) : 0
})

const dailyTargetStatus = computed(() => {
  const averageDaily = props.novel.stats.average_daily_words
  const target = dailyTarget.value
  
  if (averageDaily >= target) {
    return { type: 'success', text: '进度良好' }
  } else if (averageDaily >= target * 0.8) {
    return { type: 'warning', text: '需要加油' }
  } else {
    return { type: 'danger', text: '进度偏慢' }
  }
})

// 方法定义
const formatWordCount = (count: number) => {
  return NovelUtils.formatWordCount(count)
}

const getProgressColor = (percentage: number) => {
  return NovelUtils.getProgressColor(percentage)
}

const getStatusTagType = (status: string) => {
  const typeMap: Record<string, string> = {
    'draft': 'info',
    'ongoing': 'warning',
    'completed': 'success',
    'paused': 'danger'
  }
  return typeMap[status] || 'info'
}

const disabledDate = (time: Date) => {
  return time.getTime() < Date.now() - 24 * 60 * 60 * 1000
}

const updateGoal = () => {
  if (goalForm.targetWords < props.novel.word_count) {
    ElMessage.warning('目标字数不能小于当前字数')
    return
  }
  
  emit('update-goal', {
    targetWords: goalForm.targetWords,
    deadline: goalForm.deadline || undefined
  })
  
  showGoalDialog.value = false
  ElMessage.success('目标更新成功')
}

// 初始化表单数据
const initGoalForm = () => {
  goalForm.targetWords = props.novel.target_words || props.novel.word_count + 50000
  goalForm.deadline = null
}

// 监听对话框显示
const handleGoalDialog = () => {
  if (showGoalDialog.value) {
    initGoalForm()
  }
}
</script>

<style scoped lang="scss">
.progress-section-card {
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

.progress-content {
  .overall-progress {
    margin-bottom: 24px;
    padding: 16px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 8px;
    color: white;
    
    .progress-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;
      
      .progress-title {
        font-size: 16px;
        font-weight: 600;
      }
      
      .progress-stats {
        font-size: 14px;
        opacity: 0.9;
      }
    }
    
    .progress-bar-container {
      position: relative;
      margin-bottom: 12px;
      
      .progress-percentage {
        position: absolute;
        right: 0;
        top: -6px;
        font-size: 12px;
        font-weight: 600;
      }
    }
    
    .progress-details {
      display: flex;
      justify-content: space-between;
      font-size: 12px;
      opacity: 0.9;
      
      @media (max-width: 768px) {
        flex-direction: column;
        gap: 4px;
      }
      
      .detail-item {
        .label {
          margin-right: 4px;
        }
        
        .value {
          font-weight: 500;
        }
      }
    }
  }
  
  .section-title {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
    
    h4 {
      font-size: 14px;
      font-weight: 600;
      color: #606266;
      margin: 0;
    }
  }
}

.chapter-progress {
  margin-bottom: 24px;
  
  .chapter-stats {
    display: flex;
    align-items: center;
    gap: 20px;
    
    @media (max-width: 768px) {
      flex-direction: column;
      gap: 16px;
    }
    
    .stat-circle {
      text-align: center;
      
      .circle-text {
        font-size: 14px;
        font-weight: 600;
        color: #303133;
      }
      
      .circle-label {
        margin-top: 8px;
        font-size: 12px;
        color: #909399;
      }
    }
    
    .stat-details {
      flex: 1;
      
      .stat-row {
        display: flex;
        justify-content: space-between;
        margin-bottom: 8px;
        
        &:last-child {
          margin-bottom: 0;
        }
        
        .stat-label {
          font-size: 13px;
          color: #606266;
        }
        
        .stat-value {
          font-size: 13px;
          font-weight: 500;
          color: #303133;
          
          &.completed {
            color: #67C23A;
          }
          
          &.draft {
            color: #E6A23C;
          }
        }
      }
    }
  }
}

.quick-actions {
  margin-bottom: 24px;
  
  .action-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
    
    @media (max-width: 768px) {
      grid-template-columns: 1fr;
    }
  }
  
  .action-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px;
    background: #fafafa;
    border: 1px solid #f0f0f0;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.3s;
    
    &:hover {
      background: #f5f7fa;
      border-color: #409EFF;
      transform: translateY(-1px);
    }
    
    .action-icon {
      width: 32px;
      height: 32px;
      border-radius: 6px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 16px;
      color: white;
      
      &.worldview {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      }
      
      &.characters {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
      }
      
      &.outline {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
      }
      
      &.chapters {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
      }
    }
    
    .action-content {
      .action-name {
        font-size: 13px;
        font-weight: 500;
        color: #303133;
        margin-bottom: 2px;
      }
      
      .action-desc {
        font-size: 11px;
        color: #909399;
      }
    }
  }
}

.writing-goals {
  .goal-content {
    .goal-item {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 12px;
      margin-bottom: 12px;
      background: #fafafa;
      border-radius: 6px;
      
      &:last-child {
        margin-bottom: 0;
      }
      
      .goal-icon {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background: #409EFF;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 14px;
      }
      
      .goal-info {
        flex: 1;
        
        .goal-label {
          font-size: 12px;
          color: #909399;
          margin-bottom: 2px;
        }
        
        .goal-value {
          font-size: 14px;
          font-weight: 500;
          color: #303133;
        }
      }
      
      .goal-progress {
        width: 60px;
      }
      
      .goal-status {
        width: 80px;
        text-align: right;
      }
    }
  }
}

.form-help {
  margin-left: 8px;
  font-size: 12px;
  color: #909399;
}

// 响应式调整
@media (max-width: 768px) {
  .progress-content {
    .overall-progress {
      padding: 12px;
    }
  }
  
  .action-grid {
    .action-item {
      padding: 10px;
      
      .action-icon {
        width: 28px;
        height: 28px;
        font-size: 14px;
      }
      
      .action-name {
        font-size: 12px;
      }
      
      .action-desc {
        font-size: 10px;
      }
    }
  }
  
  .goal-content {
    .goal-item {
      padding: 10px;
      
      .goal-icon {
        width: 28px;
        height: 28px;
        font-size: 12px;
      }
      
      .goal-progress {
        width: 50px;
      }
      
      .goal-status {
        width: 70px;
      }
    }
  }
}
</style>