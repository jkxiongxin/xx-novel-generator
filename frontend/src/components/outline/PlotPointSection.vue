<template>
  <div class="plot-point-section">
    <div class="section-header">
      <h3>大情节点</h3>
      <div class="actions">
        <el-button type="primary" size="small" @click="$emit('create', 'plot_point')">
          新建大情节点
        </el-button>
        <el-button size="small" @click="$emit('generate', 'plot_point')">
          AI生成
        </el-button>
      </div>
    </div>

    <div class="section-content">
      <div v-if="items.length === 0" class="empty-state">
        <el-empty description="暂无大情节点，点击新建开始创建" />
      </div>
      
      <div v-else class="plot-points-list">
        <div
          v-for="item in sortedItems"
          :key="item.id"
          class="plot-point-item"
          :class="{ active: selectedItem?.id === item.id }"
          @click="selectItem(item)"
        >
          <div class="item-header">
            <div class="title-section">
              <h4 class="item-title">{{ item.title }}</h4>
              <div class="chapter-info">
                <el-tag v-if="item.start_chapter || item.end_chapter" size="small" type="primary">
                  第{{ item.start_chapter || '?' }}章 - 第{{ item.end_chapter || '?' }}章
                </el-tag>
                <span v-if="getChapterCount(item)" class="chapter-count">
                  共{{ getChapterCount(item) }}章
                </span>
              </div>
            </div>
            
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
          </div>
          
          <div class="item-footer">
            <div class="meta-info">
              <span class="order-index">排序：{{ item.order_index }}</span>
              <span class="update-time">{{ formatTime(item.updated_at) }}</span>
            </div>
            
            <div class="item-tools">
              <el-button 
                size="small" 
                type="success" 
                text 
                @click.stop="generateDetailed(item)"
                :disabled="!canGenerateDetailed(item)"
              >
                生成详细大纲
              </el-button>
              <el-button size="small" text @click.stop="reviewItem(item)">
                AI审核
              </el-button>
              <el-button size="small" text @click.stop="generateSummary(item)">
                生成总结
              </el-button>
            </div>
          </div>
          
          <!-- 展开的详细信息 -->
          <div v-if="selectedItem?.id === item.id" class="expanded-content">
            <el-divider>详细信息</el-divider>
            
            <div class="detail-grid">
              <div class="detail-item">
                <label>开始章节：</label>
                <span>{{ item.start_chapter || '未设置' }}</span>
              </div>
              <div class="detail-item">
                <label>结束章节：</label>
                <span>{{ item.end_chapter || '未设置' }}</span>
              </div>
              <div class="detail-item">
                <label>排序索引：</label>
                <span>{{ item.order_index }}</span>
              </div>
              <div class="detail-item">
                <label>创建时间：</label>
                <span>{{ formatTime(item.created_at) }}</span>
              </div>
            </div>
            
            <div class="full-content">
              <label>完整内容：</label>
              <div class="content-text">{{ item.content }}</div>
            </div>
            
            <div v-if="hasRelatedChapters(item)" class="related-chapters">
              <label>相关章节：</label>
              <div class="chapters-list">
                <el-tag
                  v-for="chapter in getRelatedChapters(item)"
                  :key="chapter"
                  size="small"
                  style="margin: 2px;"
                >
                  第{{ chapter }}章
                </el-tag>
              </div>
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
  }
})

// Emits
const emit = defineEmits(['create', 'update', 'delete', 'generate', 'generate-detailed'])

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
  return content.length > 150 ? content.substring(0, 150) + '...' : content
}

const formatTime = (time) => {
  if (!time) return ''
  return new Date(time).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getChapterCount = (item) => {
  if (item.start_chapter && item.end_chapter) {
    return item.end_chapter - item.start_chapter + 1
  }
  return 0
}

const canGenerateDetailed = (item) => {
  return item.start_chapter && item.end_chapter && item.start_chapter <= item.end_chapter
}

const generateDetailed = (item) => {
  if (!canGenerateDetailed(item)) {
    ElMessage.warning('请先设置有效的章节范围')
    return
  }
  emit('generate-detailed', item)
}

const hasRelatedChapters = (item) => {
  return item.start_chapter && item.end_chapter
}

const getRelatedChapters = (item) => {
  if (!hasRelatedChapters(item)) return []
  
  const chapters = []
  for (let i = item.start_chapter; i <= item.end_chapter; i++) {
    chapters.push(i)
  }
  return chapters
}

const reviewItem = (item) => {
  ElMessage.info('AI审核功能开发中...')
}

const generateSummary = (item) => {
  ElMessage.info('生成总结功能开发中...')
}
</script>

<style scoped>
.plot-point-section {
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

.plot-points-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.plot-point-item {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 16px;
  background: white;
  cursor: pointer;
  transition: all 0.2s;
}

.plot-point-item:hover {
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

.plot-point-item.active {
  border-color: #409eff;
  background: #f0f9ff;
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.title-section {
  flex: 1;
}

.item-title {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 500;
  color: #303133;
  line-height: 1.4;
}

.chapter-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.chapter-count {
  font-size: 12px;
  color: #909399;
}

.item-actions {
  display: flex;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.2s;
}

.plot-point-item:hover .item-actions {
  opacity: 1;
}

.item-content {
  margin-bottom: 12px;
}

.content-preview {
  margin: 0;
  color: #606266;
  line-height: 1.6;
  font-size: 14px;
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

.plot-point-item:hover .item-tools {
  opacity: 1;
}

.expanded-content {
  margin-top: 16px;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-bottom: 16px;
}

.detail-item {
  display: flex;
  align-items: center;
  font-size: 14px;
}

.detail-item label {
  font-weight: 500;
  color: #606266;
  margin-right: 8px;
  min-width: 80px;
}

.detail-item span {
  color: #303133;
}

.full-content {
  margin-bottom: 16px;
}

.full-content label {
  display: block;
  font-weight: 500;
  color: #606266;
  margin-bottom: 8px;
  font-size: 14px;
}

.content-text {
  background: #f5f7fa;
  padding: 12px;
  border-radius: 6px;
  line-height: 1.6;
  color: #303133;
  font-size: 14px;
}

.related-chapters {
  margin-bottom: 16px;
}

.related-chapters label {
  display: block;
  font-weight: 500;
  color: #606266;
  margin-bottom: 8px;
  font-size: 14px;
}

.chapters-list {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.order-index,
.update-time {
  font-size: 12px;
  color: #909399;
}
</style>