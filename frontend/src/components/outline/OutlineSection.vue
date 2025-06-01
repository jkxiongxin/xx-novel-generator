<template>
  <div class="outline-section">
    <div class="section-header">
      <h3>{{ title }}</h3>
      <div class="actions">
        <el-button type="primary" size="small" @click="$emit('create', type)">
          新建{{ title }}
        </el-button>
        <el-button size="small" @click="$emit('generate', type)">
          AI生成
        </el-button>
      </div>
    </div>

    <div class="section-content">
      <div v-if="items.length === 0" class="empty-state">
        <el-empty :description="`暂无${title}，点击新建开始创建`" />
      </div>
      
      <div v-else class="items-list">
        <div
          v-for="item in sortedItems"
          :key="item.id"
          class="outline-item"
          :class="{ active: selectedItem?.id === item.id }"
          @click="selectItem(item)"
        >
          <div class="item-header">
            <h4 class="item-title">{{ item.title }}</h4>
            <div class="item-actions">
              <el-button size="small" text @click.stop="editItem(item)">
                编辑
              </el-button>
              <el-button size="small" text @click.stop="$emit('delete', item)">
                删除
              </el-button>
            </div>
          </div>
          
          <div class="item-content">
            <p class="content-preview">{{ getContentPreview(item.content) }}</p>
            
            <div v-if="type === 'plot_point' && (item.start_chapter || item.end_chapter)" class="chapter-range">
              <el-tag size="small" type="info">
                章节：{{ item.start_chapter || '?' }} - {{ item.end_chapter || '?' }}
              </el-tag>
            </div>
          </div>
          
          <div class="item-footer">
            <div class="meta-info">
              <span class="order-index">排序：{{ item.order_index }}</span>
              <span class="update-time">{{ formatTime(item.updated_at) }}</span>
            </div>
            
            <div class="item-tools">
              <el-button size="small" text @click.stop="reviewItem(item)">
                AI审核
              </el-button>
              <el-button size="small" text @click.stop="generateSummary(item)">
                生成总结
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'

// Props
const props = defineProps({
  items: {
    type: Array,
    default: () => []
  },
  type: {
    type: String,
    required: true
  },
  title: {
    type: String,
    required: true
  }
})

// Emits
const emit = defineEmits(['create', 'update', 'delete', 'generate'])

// 状态
const selectedItem = ref(null)

// 计算属性
const sortedItems = computed(() => {
  return [...props.items].sort((a, b) => a.order_index - b.order_index)
})

// 方法
const selectItem = (item) => {
  selectedItem.value = selectedItem.value?.id === item.id ? null : item
}

const editItem = (item) => {
  emit('update', item)
}

const getContentPreview = (content) => {
  if (!content) return '暂无内容'
  return content.length > 100 ? content.substring(0, 100) + '...' : content
}

const formatTime = (time) => {
  if (!time) return ''
  return new Date(time).toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const reviewItem = (item) => {
  ElMessage.info('AI审核功能开发中...')
}

const generateSummary = (item) => {
  ElMessage.info('生成总结功能开发中...')
}
</script>

<style scoped>
.outline-section {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: white;
  border-radius: 8px;
  overflow: hidden;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #e4e7ed;
  background: #fafafa;
}

.section-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 500;
  color: #303133;
}

.actions {
  display: flex;
  gap: 8px;
}

.section-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.empty-state {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.items-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.outline-item {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 16px;
  background: white;
  cursor: pointer;
  transition: all 0.2s;
}

.outline-item:hover {
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

.outline-item.active {
  border-color: #409eff;
  background: #f0f9ff;
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.item-title {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
  color: #303133;
  flex: 1;
  line-height: 1.4;
}

.item-actions {
  display: flex;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.2s;
}

.outline-item:hover .item-actions {
  opacity: 1;
}

.item-content {
  margin-bottom: 12px;
}

.content-preview {
  margin: 0 0 8px 0;
  color: #606266;
  line-height: 1.6;
  font-size: 14px;
}

.chapter-range {
  margin-top: 8px;
}

.item-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #909399;
}

.meta-info {
  display: flex;
  gap: 12px;
}

.item-tools {
  display: flex;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.2s;
}

.outline-item:hover .item-tools {
  opacity: 1;
}

.order-index,
.update-time {
  font-size: 12px;
  color: #909399;
}
</style>