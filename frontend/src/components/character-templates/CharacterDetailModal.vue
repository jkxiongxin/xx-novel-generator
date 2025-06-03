<template>
  <el-dialog
    v-model="dialogVisible"
    :title="`角色详情: ${character?.name || ''}`"
    width="700px"
    class="character-detail-modal"
    destroy-on-close
  >
    <div class="modal-content" v-if="character">
      <!-- 模态框头部 - 角色基本信息 -->
      <div class="modal-header">
        <div v-if="hasAvatarUrl" class="character-avatar-large">
          <img :src="character.avatar_url" :alt="character.name" />
        </div>
        <div v-else class="character-avatar-large avatar-placeholder">
          {{ character.name.charAt(0).toUpperCase() }}
        </div>
        
        <div class="character-basic">
          <h2 class="character-name">{{ character.name }}</h2>
          <div class="character-subtitle">
            {{ formatType(character.character_type) }} · 
            {{ formatGender(character.gender) }}
            <span v-if="hasPowerSystem">· {{ character.power_system }}</span>
          </div>
          <div class="character-tags" v-if="character.tags && character.tags.length > 0">
            <el-tag
              v-for="(tag, index) in character.tags"
              :key="index"
              size="small"
              class="tag"
            >
              {{ tag }}
            </el-tag>
          </div>
          <div class="character-actions">
            <el-button 
              :type="character.is_favorited ? 'warning' : ''"
              :icon="character.is_favorited ? StarFilled : Star"
              @click="handleToggleFavorite"
            >
              {{ character.is_favorited ? '已收藏' : '收藏' }}
            </el-button>
            <el-button type="primary" @click="handleUseTemplate">使用模板</el-button>
          </div>
        </div>
      </div>
      
      <!-- 模态框主体 - 角色详细信息 -->
      <div class="modal-body">
        <!-- 基本信息部分 -->
        <div class="detail-section">
          <h3 class="section-title">
            <el-icon class="icon"><InfoFilled /></el-icon>
            基本信息
          </h3>
          <div class="section-content">
            <div class="detail-grid">
              <div class="detail-item" v-if="character.original_world">
                <div class="item-label">所属世界:</div>
                <div class="item-value">{{ character.original_world }}</div>
              </div>
              <div class="detail-item" v-if="character.personality">
                <div class="item-label">性格特点:</div>
                <div class="item-value">{{ character.personality }}</div>
              </div>
              <div class="detail-item" v-if="template?.usage_count">
                <div class="item-label">使用次数:</div>
                <div class="item-value">{{ template.usage_count }}</div>
              </div>
              <div class="detail-item" v-if="template?.rating">
                <div class="item-label">评分:</div>
                <div class="item-value">{{ template?.rating.toFixed(1) }}</div>
              </div>
            </div>
            <div class="character-description" v-if="character.description">
              <p>{{ character.description }}</p>
            </div>
          </div>
        </div>
        
        <!-- 详细描述部分 -->
        <div class="detail-section" v-if="template?.detailed_description">
          <h3 class="section-title">
            <el-icon class="icon"><Document /></el-icon>
            详细描述
          </h3>
          <div class="section-content">
            <p>{{ template.detailed_description }}</p>
          </div>
        </div>
        
        <!-- 背景故事部分 -->
        <div class="detail-section" v-if="template?.background_story">
          <h3 class="section-title">
            <el-icon class="icon"><Film /></el-icon>
            背景故事
          </h3>
          <div class="section-content">
            <p>{{ template.background_story }}</p>
          </div>
        </div>
        
        <!-- 人际关系部分 -->
        <div class="detail-section" v-if="template?.relationships">
          <h3 class="section-title">
            <el-icon class="icon"><Connection /></el-icon>
            人际关系
          </h3>
          <div class="section-content">
            <p>{{ template.relationships }}</p>
          </div>
        </div>
        
        <!-- 优势与弱点部分 -->
        <div class="detail-section" v-if="hasStrengthsOrWeaknesses">
          <h3 class="section-title">
            <el-icon class="icon"><MagicStick /></el-icon>
            特点与弱点
          </h3>
          <div class="section-content">
            <div class="strengths-weaknesses">
              <div class="strengths" v-if="template?.strengths?.length">
                <h4>优势特点:</h4>
                <ul>
                  <li v-for="(strength, index) in template.strengths" :key="`strength-${index}`">
                    {{ strength }}
                  </li>
                </ul>
              </div>
              <div class="weaknesses" v-if="template?.weaknesses?.length">
                <h4>弱点缺陷:</h4>
                <ul>
                  <li v-for="(weakness, index) in template.weaknesses" :key="`weakness-${index}`">
                    {{ weakness }}
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 能力与战斗部分 -->
        <div class="detail-section" v-if="hasAbilitiesOrCombat">
          <h3 class="section-title">
            <el-icon class="icon"><Trophy /></el-icon>
            能力与战斗
          </h3>
          <div class="section-content">
            <div v-if="character.abilities" class="abilities">
              <h4>角色能力:</h4>
              <p>{{ character.abilities }}</p>
            </div>
            <div v-if="template?.combat_style" class="combat-style">
              <h4>战斗风格:</h4>
              <p>{{ template.combat_style }}</p>
            </div>
            <div v-if="template?.special_abilities?.length" class="special-abilities">
              <h4>特殊能力:</h4>
              <el-tag
                v-for="(ability, index) in template.special_abilities"
                :key="index"
                class="ability-tag"
                effect="dark"
              >
                {{ ability }}
              </el-tag>
            </div>
            <div v-if="template?.equipment?.length" class="equipment">
              <h4>装备道具:</h4>
              <el-tag
                v-for="(item, index) in template.equipment"
                :key="index"
                class="equipment-tag"
                type="info"
              >
                {{ item }}
              </el-tag>
            </div>
          </div>
        </div>
        
        <!-- 使用示例部分 -->
        <div class="detail-section" v-if="character.usage_examples?.length">
          <h3 class="section-title">
            <el-icon class="icon"><Guide /></el-icon>
            使用示例
          </h3>
          <div class="section-content">
            <el-collapse>
              <el-collapse-item
                v-for="(example, index) in character.usage_examples"
                :key="index"
                :title="`示例 ${index + 1}: ${example.novel_genre}`"
              >
                <div class="usage-example">
                  <p><strong>使用场景:</strong> {{ example.usage_context }}</p>
                  <p v-if="example.adaptation_notes"><strong>适配说明:</strong> {{ example.adaptation_notes }}</p>
                </div>
              </el-collapse-item>
            </el-collapse>
          </div>
        </div>
      </div>
      
      <!-- 模态框底部 - 操作按钮 -->
      <div class="modal-footer">
        <el-button @click="closeDialog">关闭</el-button>
        <el-button type="primary" @click="handleUseTemplate">使用模板</el-button>
      </div>
    </div>
  </el-dialog>
</template>

<script setup lang="ts">
import { defineProps, defineEmits, computed, ref, watch } from 'vue'
import { type PropType } from 'vue'
import { 
  InfoFilled, 
  Document, 
  Film, 
  Connection, 
  MagicStick, 
  Trophy, 
  Guide,
  StarFilled,
  Star
} from '@element-plus/icons-vue'

import { 
  type CharacterTemplateDetail,
  type TemplateDetail
} from '@/api/character-templates'

// 定义props
const props = defineProps({
  character: {
    type: Object as PropType<CharacterTemplateDetail & Record<string, any>>,
    required: true
  },
  visible: {
    type: Boolean,
    required: true,
    default: false
  }
})

// 定义emits
const emit = defineEmits(['update:visible', 'use-template', 'toggle-favorite'])

// 响应式数据
const dialogVisible = ref(false)

// 计算属性
const template = computed<TemplateDetail | undefined>(
  () => props.character?.template_detail
)

const hasAvatarUrl = computed(() => {
  return 'avatar_url' in props.character && props.character.avatar_url
})

const hasPowerSystem = computed(() => {
  return 'power_system' in props.character && props.character.power_system
})

const hasStrengthsOrWeaknesses = computed(() => {
  return (
    (template.value?.strengths && template.value.strengths.length > 0) || 
    (template.value?.weaknesses && template.value.weaknesses.length > 0)
  )
})

const hasAbilitiesOrCombat = computed(() => {
  return (
    props.character.abilities || 
    template.value?.combat_style || 
    (template.value?.special_abilities && template.value.special_abilities.length > 0) ||
    (template.value?.equipment && template.value.equipment.length > 0)
  )
})

// 方法
const formatGender = (gender: string): string => {
  const genderMap: Record<string, string> = {
    'male': '男性',
    'female': '女性',
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
    'minor': '次要角色',
    'passerby': '路人'
  }
  return typeMap[type] || type
}

const closeDialog = () => {
  dialogVisible.value = false
}

const handleUseTemplate = () => {
  emit('use-template', props.character)
}

const handleToggleFavorite = () => {
  emit('toggle-favorite', props.character.id)
}

// 监听visible属性变化
watch(() => props.visible, (val) => {
  dialogVisible.value = val
})

// 监听内部dialogVisible变化，同步回父组件
watch(dialogVisible, (val) => {
  emit('update:visible', val)
})
</script>

<style scoped>
.character-detail-modal {
  :deep(.el-dialog__header) {
    padding: 20px 20px 0;
  }
  
  :deep(.el-dialog__body) {
    padding: 20px;
  }
  
  .modal-content {
    max-height: 70vh;
    overflow-y: auto;
    padding-right: 10px;
    
    &::-webkit-scrollbar {
      width: 6px;
    }
    
    &::-webkit-scrollbar-thumb {
      background-color: #dcdfe6;
      border-radius: 3px;
    }
  }

  .modal-header {
    display: flex;
    align-items: flex-start;
    gap: 20px;
    padding-bottom: 20px;
    border-bottom: 1px solid #EBEEF5;
    
    .character-avatar-large {
      width: 100px;
      height: 100px;
      border-radius: 50%;
      object-fit: cover;
      border: 3px solid #ffffff;
      box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
      overflow: hidden;
      flex-shrink: 0;
      
      img {
        width: 100%;
        height: 100%;
        object-fit: cover;
      }
      
      &.avatar-placeholder {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 40px;
        color: #ffffff;
      }
    }
    
    .character-basic {
      flex: 1;
      
      .character-name {
        font-size: 24px;
        font-weight: 600;
        color: #303133;
        margin: 0 0 8px 0;
      }
      
      .character-subtitle {
        color: #606266;
        font-size: 16px;
        margin-bottom: 12px;
      }
      
      .character-tags {
        margin-bottom: 16px;
        
        .tag {
          margin-right: 8px;
          margin-bottom: 8px;
        }
      }
      
      .character-actions {
        display: flex;
        gap: 12px;
      }
    }
  }
  
  .modal-body {
    padding: 20px 0;
    
    .detail-section {
      margin-bottom: 24px;
      
      .section-title {
        font-size: 18px;
        font-weight: 600;
        color: #303133;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        
        .icon {
          margin-right: 8px;
          color: #409EFF;
        }
      }
      
      .section-content {
        color: #606266;
        line-height: 1.6;
        
        p {
          margin: 0 0 10px;
        }
        
        .detail-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 16px;
          margin-bottom: 16px;
          
          .detail-item {
            display: flex;
            flex-direction: column;
            gap: 4px;
            
            .item-label {
              color: #909399;
              font-size: 14px;
            }
            
            .item-value {
              color: #303133;
              font-weight: 500;
            }
          }
        }
        
        .character-description {
          margin-bottom: 16px;
        }
        
        .strengths-weaknesses {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 24px;
          
          h4 {
            margin-top: 0;
            margin-bottom: 12px;
            color: #303133;
          }
          
          ul {
            margin: 0;
            padding-left: 20px;
            
            li {
              margin-bottom: 8px;
            }
          }
          
          @media (max-width: 767px) {
            grid-template-columns: 1fr;
            gap: 16px;
          }
        }
        
        .abilities, .combat-style {
          margin-bottom: 16px;
          
          h4 {
            margin-top: 0;
            margin-bottom: 8px;
            color: #303133;
          }
        }
        
        .special-abilities, .equipment {
          margin-bottom: 16px;
          
          h4 {
            margin-top: 0;
            margin-bottom: 8px;
            color: #303133;
          }
          
          .ability-tag, .equipment-tag {
            margin-right: 8px;
            margin-bottom: 8px;
          }
        }
        
        .usage-example {
          p {
            margin-bottom: 12px;
          }
        }
      }
    }
  }
  
  .modal-footer {
    padding-top: 20px;
    border-top: 1px solid #EBEEF5;
    display: flex;
    justify-content: flex-end;
    gap: 12px;
  }
}

@media (max-width: 767px) {
  .character-detail-modal {
    .modal-header {
      flex-direction: column;
      align-items: center;
      text-align: center;
      
      .character-basic {
        .character-actions {
          justify-content: center;
        }
      }
    }
  }
}
</style>