<template>
  <div class="history-section">
    <div class="section-header">
      <h3>历史事件</h3>
      <div class="actions">
        <el-button type="primary" @click="$emit('create')">新建历史事件</el-button>
        <el-button @click="generateHistory">AI生成</el-button>
      </div>
    </div>

    <div class="history-content">
      <div v-if="histories.length === 0" class="empty-state">
        <el-empty description="暂无历史事件，点击新建开始创建" />
      </div>
      
      <div v-else class="history-timeline">
        <div
          v-for="history in sortedHistories"
          :key="history.id"
          class="timeline-item"
        >
          <div class="timeline-marker">
            <div class="marker-dot" :class="getEventTypeClass(history.event_type)"></div>
          </div>
          <div class="timeline-content">
            <div class="event-header">
              <div class="event-info">
                <h4 class="event-title">{{ history.event_name }}</h4>
                <div class="event-meta">
                  <el-tag :type="getEventTypeTagType(history.event_type)" size="small">
                    {{ getEventTypeLabel(history.event_type) }}
                  </el-tag>
                  <span v-if="history.event_year" class="event-year">
                    {{ formatEventYear(history.event_year) }}
                  </span>
                </div>
              </div>
              <div class="event-actions">
                <el-button size="small" @click="$emit('update', history)">编辑</el-button>
                <el-button size="small" type="danger" @click="$emit('delete', history)">删除</el-button>
              </div>
            </div>
            
            <p class="event-description">{{ history.description }}</p>
            
            <div v-if="history.participants" class="event-participants">
              <strong>参与者：</strong>{{ history.participants }}
            </div>
            
            <div v-if="history.consequences" class="event-consequences">
              <strong>历史影响：</strong>{{ history.consequences }}
            </div>
            
            <div v-if="history.related_locations" class="event-locations">
              <strong>相关地点：</strong>{{ history.related_locations }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  worldviewId: {
    type: Number,
    required: true
  },
  histories: {
    type: Array,
    default: () => []
  }
})

defineEmits(['create', 'update', 'delete', 'refresh'])

// 按年份排序历史事件
const sortedHistories = computed(() => {
  return [...props.histories].sort((a, b) => {
    // 如果有年份，按年份排序；否则按创建时间排序
    if (a.event_year && b.event_year) {
      return a.event_year - b.event_year
    }
    if (a.event_year && !b.event_year) return -1
    if (!a.event_year && b.event_year) return 1
    return new Date(a.created_at) - new Date(b.created_at)
  })
})

// 获取事件类型样式类
const getEventTypeClass = (eventType) => {
  const typeClasses = {
    war: 'war-event',
    peace: 'peace-event',
    discovery: 'discovery-event',
    disaster: 'disaster-event',
    political: 'political-event',
    cultural: 'cultural-event',
    economic: 'economic-event',
    other: 'other-event'
  }
  return typeClasses[eventType] || 'other-event'
}

// 获取事件类型标签样式
const getEventTypeTagType = (eventType) => {
  const tagTypes = {
    war: 'danger',
    peace: 'success',
    discovery: 'primary',
    disaster: 'warning',
    political: 'info',
    cultural: 'purple',
    economic: 'gold',
    other: 'default'
  }
  return tagTypes[eventType] || 'default'
}

// 获取事件类型显示标签
const getEventTypeLabel = (eventType) => {
  const labels = {
    war: '战争',
    peace: '和平',
    discovery: '发现',
    disaster: '灾难',
    political: '政治',
    cultural: '文化',
    economic: '经济',
    other: '其他'
  }
  return labels[eventType] || '未知'
}

// 格式化事件年份
const formatEventYear = (year) => {
  if (year > 0) {
    return `${year}年`
  } else {
    return `前${Math.abs(year)}年`
  }
}

const generateHistory = () => {
  ElMessage.info('AI生成历史事件功能开发中...')
}
</script>

<style scoped>
.history-section {
  padding: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h3 {
  margin: 0;
  font-size: 18px;
}

.actions {
  display: flex;
  gap: 8px;
}

.empty-state {
  text-align: center;
  padding: 60px;
}

.history-timeline {
  position: relative;
}

.history-timeline::before {
  content: '';
  position: absolute;
  left: 20px;
  top: 0;
  bottom: 0;
  width: 2px;
  background: linear-gradient(to bottom, #409eff, #67c23a);
}

.timeline-item {
  position: relative;
  display: flex;
  margin-bottom: 24px;
  padding-left: 60px;
}

.timeline-marker {
  position: absolute;
  left: 0;
  top: 8px;
}

.marker-dot {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 3px solid #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
}

.war-event { background: #f56c6c; }
.peace-event { background: #67c23a; }
.discovery-event { background: #409eff; }
.disaster-event { background: #e6a23c; }
.political-event { background: #909399; }
.cultural-event { background: #c0392b; }
.economic-event { background: #f39c12; }
.other-event { background: #bfbfbf; }

.timeline-content {
  flex: 1;
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.event-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.event-info {
  flex: 1;
}

.event-title {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

.event-meta {
  display: flex;
  align-items: center;
  gap: 12px;
}

.event-year {
  font-size: 14px;
  color: #606266;
  background: #f5f7fa;
  padding: 2px 8px;
  border-radius: 4px;
}

.event-actions {
  display: flex;
  gap: 4px;
  flex-shrink: 0;
}

.event-description {
  margin: 0 0 12px 0;
  color: #303133;
  line-height: 1.6;
}

.event-participants,
.event-consequences,
.event-locations {
  margin: 8px 0;
  font-size: 14px;
  color: #606266;
}

.event-participants strong,
.event-consequences strong,
.event-locations strong {
  color: #303133;
  margin-right: 8px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .timeline-item {
    padding-left: 40px;
  }
  
  .marker-dot {
    width: 24px;
    height: 24px;
  }
  
  .history-timeline::before {
    left: 12px;
  }
  
  .event-header {
    flex-direction: column;
    gap: 12px;
  }
  
  .event-actions {
    align-self: flex-start;
  }
}
</style>