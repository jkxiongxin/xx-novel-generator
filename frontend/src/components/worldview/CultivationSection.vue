<template>
  <div class="cultivation-section">
    <div class="section-header">
      <h3>修炼体系</h3>
      <div class="actions">
        <el-button type="primary" @click="$emit('create')">新建修炼体系</el-button>
        <el-button @click="generateSystems">AI生成</el-button>
      </div>
    </div>

    <div class="systems-content">
      <div v-if="systems.length === 0" class="empty-state">
        <el-empty description="暂无修炼体系，点击新建开始创建" />
      </div>
      
      <div v-else class="systems-list">
        <div
          v-for="system in groupedSystems"
          :key="system.name"
          class="system-group"
        >
          <h4 class="system-name">{{ system.name }}</h4>
          <div class="levels-list">
            <div
              v-for="level in system.levels"
              :key="level.id"
              class="level-item"
            >
              <div class="level-header">
                <span class="level-name">{{ level.level_name }}</span>
                <div class="level-actions">
                  <el-button size="small" @click="$emit('update', level)">编辑</el-button>
                  <el-button size="small" type="danger" @click="$emit('delete', level)">删除</el-button>
                </div>
              </div>
              <p class="level-description">{{ level.description }}</p>
              <div v-if="level.cultivation_method" class="level-method">
                <strong>修炼方法：</strong>{{ level.cultivation_method }}
              </div>
              <div v-if="level.required_resources" class="level-resources">
                <strong>所需资源：</strong>{{ level.required_resources }}
              </div>
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
  systems: {
    type: Array,
    default: () => []
  }
})

defineEmits(['create', 'update', 'delete', 'refresh'])

// 按体系名称分组
const groupedSystems = computed(() => {
  const groups = {}
  props.systems.forEach(system => {
    if (!groups[system.system_name]) {
      groups[system.system_name] = {
        name: system.system_name,
        levels: []
      }
    }
    groups[system.system_name].levels.push(system)
  })
  
  // 对每个体系的等级排序
  Object.values(groups).forEach(group => {
    group.levels.sort((a, b) => a.level_order - b.level_order)
  })
  
  return Object.values(groups)
})

const generateSystems = () => {
  ElMessage.info('AI生成修炼体系功能开发中...')
}
</script>

<style scoped>
.cultivation-section {
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

.systems-list {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.system-group {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 20px;
}

.system-name {
  margin: 0 0 16px 0;
  font-size: 18px;
  font-weight: 500;
  color: #303133;
  border-bottom: 2px solid #409eff;
  padding-bottom: 8px;
}

.levels-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.level-item {
  border: 1px solid #f0f0f0;
  border-radius: 6px;
  padding: 16px;
  background: #fafafa;
}

.level-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.level-name {
  font-size: 16px;
  font-weight: 500;
  color: #409eff;
}

.level-actions {
  display: flex;
  gap: 4px;
}

.level-description {
  margin: 8px 0;
  color: #303133;
  line-height: 1.6;
}

.level-method,
.level-resources {
  margin: 4px 0;
  font-size: 14px;
  color: #606266;
}

.level-method strong,
.level-resources strong {
  color: #303133;
  margin-right: 8px;
}
</style>