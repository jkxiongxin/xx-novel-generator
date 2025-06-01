<template>
  <div class="detailed-outline-section">
    <div class="section-header">
      <h3>详细大纲</h3>
      <div class="actions">
        <el-button type="primary" size="small" @click="$emit('create')">
          新建章节大纲
        </el-button>
        <el-button size="small" @click="$emit('generate')">
          AI生成
        </el-button>
      </div>
    </div>

    <div class="section-content">
      <div v-if="items.length === 0" class="empty-state">
        <el-empty description="暂无详细大纲，点击新建开始创建" />
      </div>
      
      <div v-else class="outline-list">
        <div
          v-for="item in sortedItems"
          :key="item.id"
          class="outline-item"
          :class="{ active: selectedItem?.id === item.id }"
          @click="selectItem(item)"
        >
          <div class="item-header">
            <div class="chapter-info">
              <el-tag type="primary" size="large">第{{ item.chapter_number }}章</el-tag>
              <h4 class="chapter-title">{{ item.chapter_title || '未设置标题' }}</h4>
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
            <div class="plot-points">
              <label>情节点：</label>
              <p>{{ getContentPreview(item.plot_points) }}</p>
            </div>
            
            <div v-if="item.chapter_summary" class="chapter-summary">
              <label>章节简介：</label>
              <p>{{ getContentPreview(item.chapter_summary) }}</p>
            </div>
            
            <div class="characters-info">
              <div v-if="item.participating_characters?.length" class="character-group">
                <label>参与角色：</label>
                <div class="character-tags">
                  <el-tag
                    v-for="characterId in item.participating_characters"
                    :key="`participating-${characterId}`"
                    size="small"
                    type="primary"
                  >
                    {{ getCharacterName(characterId) }}
                  </el-tag>
                </div>
              </div>
              
              <div v-if="item.entering_characters?.length" class="character-group">
                <label>入场角色：</label>
                <div class="character-tags">
                  <el-tag
                    v-for="characterId in item.entering_characters"
                    :key="`entering-${characterId}`"
                    size="small"
                    type="success"
                  >
                    {{ getCharacterName(characterId) }}
                  </el-tag>
                </div>
              </div>
              
              <div v-if="item.exiting_characters?.length" class="character-group">
                <label>离场角色：</label>
                <div class="character-tags">
                  <el-tag
                    v-for="characterId in item.exiting_characters"
                    :key="`exiting-${characterId}`"
                    size="small"
                    type="danger"
                  >
                    {{ getCharacterName(characterId) }}
                  </el-tag>
                </div>
              </div>
            </div>
            
            <div class="plot-flags">
              <el-tag v-if="item.is_new_plot" type="warning" size="small">新剧情开始</el-tag>
              <el-tag v-if="item.is_plot_end" type="info" size="small">剧情结束</el-tag>
            </div>
          </div>
          
          <div class="item-footer">
            <div class="meta-info">
              <span class="update-time">{{ formatTime(item.updated_at) }}</span>
            </div>
            
            <div class="item-tools">
              <el-button size="small" text @click.stop="$emit('ai-review', item)">
                AI审核
              </el-button>
              <el-button size="small" text @click.stop="$emit('generate-summary', item)">
                生成总结
              </el-button>
              <el-button size="small" text @click.stop="generateNext(item)">
                生成下一个
              </el-button>
            </div>
          </div>
          
          <!-- 展开的详细信息 -->
          <div v-if="selectedItem?.id === item.id" class="expanded-content">
            <el-divider>详细信息</el-divider>
            
            <div class="detail-sections">
              <div class="detail-section">
                <h5>完整情节点</h5>
                <div class="content-text">{{ item.plot_points }}</div>
              </div>
              
              <div v-if="item.chapter_summary" class="detail-section">
                <h5>完整章节简介</h5>
                <div class="content-text">{{ item.chapter_summary }}</div>
              </div>
              
              <div v-if="item.is_new_plot && item.new_plot_summary" class="detail-section">
                <h5>新剧情简介</h5>
                <div class="content-text">{{ item.new_plot_summary }}</div>
              </div>
              
              <div class="detail-section">
                <h5>角色分配详情</h5>
                <div class="character-details">
                  <div v-if="item.participating_characters?.length" class="character-detail-group">
                    <strong>参与角色：</strong>
                    <span>{{ getCharacterNames(item.participating_characters).join('、') }}</span>
                  </div>
                  <div v-if="item.entering_characters?.length" class="character-detail-group">
                    <strong>入场角色：</strong>
                    <span>{{ getCharacterNames(item.entering_characters).join('、') }}</span>
                  </div>
                  <div v-if="item.exiting_characters?.length" class="character-detail-group">
                    <strong>离场角色：</strong>
                    <span>{{ getCharacterNames(item.exiting_characters).join('、') }}</span>
                  </div>
                </div>
              </div>
              
              <div class="detail-section">
                <h5>剧情标识</h5>
                <div class="plot-flags-detail">
                  <div class="flag-item">
                    <strong>是否新剧情开始：</strong>
                    <span>{{ item.is_new_plot ? '是' : '否' }}</span>
                  </div>
                  <div class="flag-item">
                    <strong>是否剧情结束：</strong>
                    <span>{{ item.is_plot_end ? '是' : '否' }}</span>
                  </div>
                </div>
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
  },
  characters: {
    type: Array,
    default: () => []
  }
})

// Emits
const emit = defineEmits(['create', 'update', 'delete', 'generate', 'ai-review', 'generate-summary'])

// 状态
const selectedItem = ref(null)

// 计算属性
const sortedItems = computed(() => {
  return [...props.items].sort((a, b) => a.chapter_number - b.chapter_number)
})

// 创建角色ID到名称的映射
const characterMap = computed(() => {
  const map = new Map()
  props.characters.forEach(character => {
    map.set(character.id, character.name)
  })
  return map
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

const getCharacterName = (characterId) => {
  return characterMap.value.get(characterId) || `角色${characterId}`
}

const getCharacterNames = (characterIds) => {
  return characterIds.map(id => getCharacterName(id))
}

const generateNext = (item) => {
  ElMessage.info(`正在为第${item.chapter_number + 1}章生成大纲...`)
  // 这里可以触发生成下一章节大纲的逻辑
}
</script>

<style scoped>
.detailed-outline-section {
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

.outline-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.outline-item {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 20px;
  background: white;
  cursor: pointer;
  transition: all 0.2s;
}

.outline-item:hover {
  border-color: #409eff;
  box-shadow: 0 2px 12px rgba(64, 158, 255, 0.1);
}

.outline-item.active {
  border-color: #409eff;
  background: #f0f9ff;
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.chapter-info {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.chapter-title {
  margin: 0;
  font-size: 18px;
  font-weight: 500;
  color: #303133;
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
  margin-bottom: 16px;
}

.plot-points,
.chapter-summary {
  margin-bottom: 12px;
}

.plot-points label,
.chapter-summary label {
  display: block;
  font-weight: 500;
  color: #606266;
  margin-bottom: 4px;
  font-size: 14px;
}

.plot-points p,
.chapter-summary p {
  margin: 0;
  color: #303133;
  line-height: 1.6;
  font-size: 14px;
}

.characters-info {
  margin-bottom: 12px;
}

.character-group {
  margin-bottom: 8px;
}

.character-group label {
  display: inline-block;
  font-weight: 500;
  color: #606266;
  margin-right: 8px;
  font-size: 14px;
  min-width: 80px;
}

.character-tags {
  display: inline-flex;
  flex-wrap: wrap;
  gap: 4px;
}

.plot-flags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.item-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #909399;
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

.expanded-content {
  margin-top: 20px;
}

.detail-sections {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.detail-section h5 {
  margin: 0 0 8px 0;
  font-size: 14px;
  font-weight: 500;
  color: #606266;
}

.content-text {
  background: #f5f7fa;
  padding: 12px;
  border-radius: 6px;
  line-height: 1.6;
  color: #303133;
  font-size: 14px;
}

.character-details {
  background: #f5f7fa;
  padding: 12px;
  border-radius: 6px;
}

.character-detail-group {
  margin-bottom: 8px;
  font-size: 14px;
}

.character-detail-group:last-child {
  margin-bottom: 0;
}

.character-detail-group strong {
  color: #606266;
  margin-right: 8px;
}

.character-detail-group span {
  color: #303133;
}

.plot-flags-detail {
  background: #f5f7fa;
  padding: 12px;
  border-radius: 6px;
}

.flag-item {
  margin-bottom: 8px;
  font-size: 14px;
}

.flag-item:last-child {
  margin-bottom: 0;
}

.flag-item strong {
  color: #606266;
  margin-right: 8px;
}

.flag-item span {
  color: #303133;
}

.update-time {
  font-size: 12px;
  color: #909399;
}
</style>