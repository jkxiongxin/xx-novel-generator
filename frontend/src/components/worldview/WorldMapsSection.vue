<template>
  <div class="world-maps-section">
    <div class="section-header">
      <h3>世界地图</h3>
      <div class="actions">
        <el-button type="primary" @click="$emit('create')">新建地图区域</el-button>
        <el-button @click="generateMaps">AI生成</el-button>
      </div>
    </div>

    <div class="maps-content">
      <div v-if="maps.length === 0" class="empty-state">
        <el-empty description="暂无地图区域，点击新建开始创建" />
      </div>
      
      <div v-else class="maps-list">
        <div
          v-for="map in maps"
          :key="map.id"
          class="map-item"
        >
          <div class="map-header">
            <h4>{{ map.region_name }}</h4>
            <div class="map-actions">
              <el-button size="small" @click="$emit('update', map)">编辑</el-button>
              <el-button size="small" type="danger" @click="$emit('delete', map)">删除</el-button>
            </div>
          </div>
          <p class="map-description">{{ map.description }}</p>
          <div class="map-meta">
            <el-tag size="small">层级 {{ map.level }}</el-tag>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ElMessage } from 'element-plus'

defineProps({
  worldviewId: {
    type: Number,
    required: true
  },
  maps: {
    type: Array,
    default: () => []
  }
})

defineEmits(['create', 'update', 'delete', 'refresh'])

const generateMaps = () => {
  ElMessage.info('AI生成地图功能开发中...')
}
</script>

<style scoped>
.world-maps-section {
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

.maps-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.map-item {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 16px;
}

.map-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.map-header h4 {
  margin: 0;
  font-size: 16px;
}

.map-actions {
  display: flex;
  gap: 4px;
}

.map-description {
  margin: 8px 0;
  color: #606266;
  line-height: 1.6;
}

.map-meta {
  display: flex;
  gap: 8px;
}
</style>