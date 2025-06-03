<template>
  <div class="character-card" :class="{ 'selected': isSelected }">
    <!-- 卡片头部 - 背景和头像 -->
    <div class="card-header">
      <div v-if="hasAvatarUrl" class="character-avatar">
        <img :src="character.avatar_url as string" :alt="character.name" />
      </div>
      <div v-else class="avatar-placeholder">
        {{ character.name ? character.name.charAt(0).toUpperCase() : '?' }}
      </div>

      <!-- 标签徽章 -->
      <div v-if="character.is_new" class="card-badge new">新增</div>
      <div v-else-if="character.is_popular" class="card-badge popular">热门</div>
    </div>

    <!-- 卡片内容 -->
    <div class="card-body">
      <div class="character-name">{{ character.name }}</div>
      
      <div class="character-info">
        <div class="info-item">
          <span class="label">性别:</span>
          <span class="value">{{ formatGender(character.gender) }}</span>
        </div>
        <div class="info-item">
          <span class="label">类型:</span>
          <span class="value">{{ formatType(character.character_type) }}</span>
        </div>
        <div class="info-item" v-if="hasPowerSystem">
          <span class="label">力量:</span>
          <span class="value">{{ character.power_system as string }}</span>
        </div>
      </div>

      <div class="character-description" v-if="character.description">
        {{ character.description }}
      </div>

      <div class="character-tags" v-if="character.tags && character.tags.length > 0">
        <el-tag
          v-for="(tag, index) in character.tags.slice(0, 3)"
          :key="index"
          size="small"
          class="tag"
        >
          {{ tag }}
        </el-tag>
        <el-tag v-if="character.tags.length > 3" size="small" class="tag">
          +{{ character.tags.length - 3 }}
        </el-tag>
      </div>

      <!-- 使用数据 -->
      <div class="usage-stats" v-if="showStats">
        <el-tooltip content="使用次数" placement="top">
          <div class="stat-item">
            <el-icon><View /></el-icon>
            <span>{{ character.usage_count }}</span>
          </div>
        </el-tooltip>
        <el-tooltip content="评分" placement="top">
          <div class="stat-item">
            <el-icon><Star /></el-icon>
            <span>{{ character.rating.toFixed(1) }}</span>
          </div>
        </el-tooltip>
      </div>
    </div>

    <!-- 卡片底部 - 按钮操作区 -->
    <div class="card-footer">
      <el-button
        class="use-btn"
        type="primary"
        @click="$emit('use-template', character)"
      >
        使用
      </el-button>
      <el-button
        class="detail-btn"
        @click="$emit('view-details', character.id)"
      >
        详情
      </el-button>
      <el-button
        class="favorite-btn"
        :icon="character.is_favorited ? StarFilled : Star"
        circle
        :type="character.is_favorited ? 'warning' : ''"
        @click.stop="$emit('toggle-favorite', character.id)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineProps, defineEmits, computed } from 'vue'
import { type PropType } from 'vue'
import { View, Star, StarFilled } from '@element-plus/icons-vue'
import type { CharacterTemplateSummary } from '@/api/character-templates'

const props = defineProps({
  character: {
    type: Object as PropType<CharacterTemplateSummary & Record<string, any>>,
    required: true
  },
  selected: {
    type: Boolean,
    default: false
  },
  showStats: {
    type: Boolean,
    default: true
  }
})

defineEmits(['view-details', 'use-template', 'toggle-favorite'])

// 计算属性
const isSelected = computed(() => props.selected)
const hasAvatarUrl = computed(() => 'avatar_url' in props.character && props.character.avatar_url)
const hasPowerSystem = computed(() => 'power_system' in props.character && props.character.power_system)

// 方法
const formatGender = (gender: string): string => {
  const genderMap: Record<string, string> = {
    'male': '男',
    'female': '女',
    'unknown': '未知',
    'other': '其他'
  }
  return genderMap[gender] || gender
}

const formatType = (type: string): string => {
  const typeMap: Record<string, string> = {
    'protagonist': '主角',
    'supporting': '配角',
    'antagonist': '反派',
    'minor': '次要',
    'passerby': '路人'
  }
  return typeMap[type] || type
}
</script>

<style scoped>
.character-card {
  background: #ffffff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  position: relative;
  height: 100%;
  display: flex;
  flex-direction: column;
  
  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  }
  
  &.selected {
    box-shadow: 0 0 0 2px #409EFF;
  }
  
  .card-header {
    position: relative;
    height: 120px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    
    .character-avatar {
      width: 80px;
      height: 80px;
      border-radius: 50%;
      border: 3px solid #ffffff;
      overflow: hidden;
      
      img {
        width: 100%;
        height: 100%;
        object-fit: cover;
      }
    }
    
    .avatar-placeholder {
      width: 80px;
      height: 80px;
      border-radius: 50%;
      background: rgba(255, 255, 255, 0.3);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 32px;
      color: #ffffff;
      border: 3px solid #ffffff;
    }
    
    .card-badge {
      position: absolute;
      top: 8px;
      right: 8px;
      padding: 2px 8px;
      border-radius: 12px;
      font-size: 12px;
      font-weight: 500;
      
      &.new {
        background: #E6A23C;
        color: #ffffff;
      }
      
      &.popular {
        background: #F56C6C;
        color: #ffffff;
      }
    }
  }
  
  .card-body {
    padding: 16px;
    flex-grow: 1;
    display: flex;
    flex-direction: column;
    
    .character-name {
      font-size: 16px;
      font-weight: 600;
      color: #303133;
      margin-bottom: 8px;
      text-align: center;
    }
    
    .character-info {
      .info-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 6px;
        font-size: 13px;
        
        .label {
          color: #909399;
        }
        
        .value {
          color: #606266;
          font-weight: 500;
        }
      }
    }
    
    .character-description {
      color: #606266;
      font-size: 13px;
      line-height: 1.4;
      margin: 12px 0;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }
    
    .character-tags {
      margin: 12px 0;
      
      .tag {
        font-size: 11px;
        padding: 2px 6px;
        margin-right: 4px;
        margin-bottom: 4px;
      }
    }
    
    .usage-stats {
      display: flex;
      gap: 16px;
      margin-top: auto;
      
      .stat-item {
        display: flex;
        align-items: center;
        gap: 4px;
        font-size: 12px;
        color: #909399;
      }
    }
  }
  
  .card-footer {
    padding: 12px 16px;
    border-top: 1px solid #F2F6FC;
    display: flex;
    gap: 8px;
    
    .use-btn {
      flex: 1;
      border-radius: 16px;
      font-size: 13px;
      padding: 6px 16px;
    }
    
    .detail-btn {
      padding: 6px 12px;
      border-radius: 16px;
      font-size: 13px;
    }
    
    .favorite-btn {
      padding: 6px;
    }
  }
}

@media (max-width: 767px) {
  .character-card .card-body {
    padding: 12px;
    
    .character-name {
      font-size: 15px;
    }
    
    .character-info .info-item {
      font-size: 12px;
    }
    
    .character-description {
      font-size: 12px;
      -webkit-line-clamp: 2;
    }
  }
  
  .character-card .card-footer {
    padding: 10px;
    
    .use-btn, .detail-btn {
      font-size: 12px;
      padding: 4px 10px;
    }
  }
}
</style>