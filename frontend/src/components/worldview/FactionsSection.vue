<template>
  <div class="factions-section">
    <div class="section-header">
      <h3>阵营势力</h3>
      <div class="actions">
        <el-button type="primary" @click="$emit('create')">新建阵营势力</el-button>
        <el-button @click="generateFactions">AI生成</el-button>
      </div>
    </div>

    <div class="factions-content">
      <div v-if="factions.length === 0" class="empty-state">
        <el-empty description="暂无阵营势力，点击新建开始创建" />
      </div>
      
      <div v-else class="factions-grid">
        <div
          v-for="faction in groupedFactions"
          :key="faction.id"
          class="faction-card"
          :class="getFactionTypeClass(faction.faction_type)"
        >
          <div class="faction-header">
            <div class="faction-title">
              <h4 class="faction-name">{{ faction.name }}</h4>
              <el-tag 
                :type="getFactionTypeTagType(faction.faction_type)" 
                size="small"
                class="faction-type-tag"
              >
                {{ getFactionTypeLabel(faction.faction_type) }}
              </el-tag>
            </div>
            <div class="faction-actions">
              <el-button size="small" @click="$emit('update', faction)">编辑</el-button>
              <el-button size="small" type="danger" @click="$emit('delete', faction)">删除</el-button>
            </div>
          </div>
          
          <div class="faction-info">
            <div class="faction-description">
              <p>{{ faction.description || '暂无描述' }}</p>
            </div>
            
            <div class="faction-details">
              <div v-if="faction.leader" class="detail-item">
                <strong>领导者：</strong>
                <span>{{ faction.leader }}</span>
              </div>
              
              <div v-if="faction.territory" class="detail-item">
                <strong>控制区域：</strong>
                <span>{{ faction.territory }}</span>
              </div>
              
              <div v-if="faction.power_level" class="detail-item">
                <strong>势力等级：</strong>
                <el-rate 
                  v-model="faction.power_level" 
                  :max="5" 
                  disabled 
                  show-score
                  text-color="#ff9900"
                />
              </div>
              
              <div v-if="faction.goals" class="detail-item">
                <strong>主要目标：</strong>
                <span>{{ faction.goals }}</span>
              </div>
              
              <div v-if="faction.resources" class="detail-item">
                <strong>主要资源：</strong>
                <span>{{ faction.resources }}</span>
              </div>
              
              <div v-if="faction.allies && faction.allies.length > 0" class="detail-item">
                <strong>盟友：</strong>
                <div class="relation-tags">
                  <el-tag 
                    v-for="ally in faction.allies" 
                    :key="ally"
                    type="success" 
                    size="small"
                  >
                    {{ ally }}
                  </el-tag>
                </div>
              </div>
              
              <div v-if="faction.enemies && faction.enemies.length > 0" class="detail-item">
                <strong>敌对：</strong>
                <div class="relation-tags">
                  <el-tag 
                    v-for="enemy in faction.enemies" 
                    :key="enemy"
                    type="danger" 
                    size="small"
                  >
                    {{ enemy }}
                  </el-tag>
                </div>
              </div>
            </div>
          </div>
          
          <div v-if="faction.notable_members" class="faction-members">
            <strong>重要成员：</strong>
            <p class="members-text">{{ faction.notable_members }}</p>
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
  factions: {
    type: Array,
    default: () => []
  }
})

defineEmits(['create', 'update', 'delete', 'refresh'])

// 按势力等级排序
const groupedFactions = computed(() => {
  return [...props.factions].sort((a, b) => {
    // 先按势力等级排序，再按名称排序
    if (a.power_level !== b.power_level) {
      return (b.power_level || 0) - (a.power_level || 0)
    }
    return a.name.localeCompare(b.name)
  })
})

// 获取阵营类型样式类
const getFactionTypeClass = (factionType) => {
  const typeClasses = {
    kingdom: 'kingdom-faction',
    sect: 'sect-faction',
    clan: 'clan-faction',
    guild: 'guild-faction',
    organization: 'organization-faction',
    mercenary: 'mercenary-faction',
    religious: 'religious-faction',
    criminal: 'criminal-faction',
    other: 'other-faction'
  }
  return typeClasses[factionType] || 'other-faction'
}

// 获取阵营类型标签样式
const getFactionTypeTagType = (factionType) => {
  const tagTypes = {
    kingdom: 'primary',
    sect: 'success',
    clan: 'warning',
    guild: 'info',
    organization: 'danger',
    mercenary: 'warning',
    religious: 'success',
    criminal: 'danger',
    other: 'info'
  }
  return tagTypes[factionType] || 'info'
}

// 获取阵营类型显示标签
const getFactionTypeLabel = (factionType) => {
  const labels = {
    kingdom: '王国',
    sect: '宗门',
    clan: '家族',
    guild: '公会',
    organization: '组织',
    mercenary: '佣兵团',
    religious: '宗教',
    criminal: '犯罪组织',
    other: '其他'
  }
  return labels[factionType] || '未知'
}

const generateFactions = () => {
  ElMessage.info('AI生成阵营势力功能开发中...')
}
</script>

<style scoped>
.factions-section {
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

.factions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 20px;
}

.faction-card {
  border: 1px solid #e4e7ed;
  border-radius: 12px;
  padding: 20px;
  background: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.faction-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.faction-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #409eff, #67c23a);
}

.kingdom-faction::before { background: linear-gradient(90deg, #8e44ad, #3498db); }
.sect-faction::before { background: linear-gradient(90deg, #27ae60, #2ecc71); }
.clan-faction::before { background: linear-gradient(90deg, #f39c12, #e67e22); }
.guild-faction::before { background: linear-gradient(90deg, #3498db, #2980b9); }
.organization-faction::before { background: linear-gradient(90deg, #e74c3c, #c0392b); }
.mercenary-faction::before { background: linear-gradient(90deg, #95a5a6, #7f8c8d); }
.religious-faction::before { background: linear-gradient(90deg, #f1c40f, #f39c12); }
.criminal-faction::before { background: linear-gradient(90deg, #2c3e50, #34495e); }

.faction-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.faction-title {
  flex: 1;
}

.faction-name {
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.faction-type-tag {
  margin-left: 8px;
}

.faction-actions {
  display: flex;
  gap: 4px;
  flex-shrink: 0;
}

.faction-info {
  margin-bottom: 16px;
}

.faction-description {
  margin-bottom: 16px;
}

.faction-description p {
  margin: 0;
  color: #606266;
  line-height: 1.6;
}

.faction-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.detail-item strong {
  color: #303133;
  min-width: 80px;
  flex-shrink: 0;
}

.detail-item span {
  color: #606266;
  flex: 1;
}

.relation-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.faction-members {
  border-top: 1px solid #f0f0f0;
  padding-top: 16px;
  margin-top: 16px;
}

.faction-members strong {
  color: #303133;
  font-size: 14px;
}

.members-text {
  margin: 8px 0 0 0;
  color: #606266;
  font-size: 14px;
  line-height: 1.5;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .factions-grid {
    grid-template-columns: 1fr;
  }
  
  .faction-header {
    flex-direction: column;
    gap: 12px;
  }
  
  .faction-actions {
    align-self: flex-start;
  }
  
  .detail-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }
  
  .detail-item strong {
    min-width: auto;
  }
}
</style>