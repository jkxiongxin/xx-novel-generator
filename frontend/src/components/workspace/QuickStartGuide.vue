<template>
  <div class="quick-start-guide" v-if="showGuide">
    <div class="guide-header">
      <div class="guide-content">
        <h3 class="guide-title">🎉 欢迎来到创作工作台！</h3>
        <p class="guide-description">
          让我们开始您的创作之旅，跟随引导快速完成小说的基础设置
        </p>
      </div>
      <el-button
        type="text"
        class="skip-btn"
        @click="skipGuide"
      >
        <el-icon><Close /></el-icon>
      </el-button>
    </div>

    <div class="guide-steps">
      <div
        v-for="(step, index) in guideSteps"
        :key="step.id"
        :class="['step-item', { 
          active: currentStep === index, 
          completed: completedSteps.includes(step.id),
          clickable: step.available 
        }]"
        @click="step.available ? goToStep(step) : null"
      >
        <div class="step-number">
          <el-icon v-if="completedSteps.includes(step.id)"><Check /></el-icon>
          <span v-else>{{ index + 1 }}</span>
        </div>
        
        <div class="step-content">
          <div class="step-title">{{ step.title }}</div>
          <div class="step-description">{{ step.description }}</div>
          
          <div class="step-progress" v-if="step.progress !== undefined">
            <el-progress
              :percentage="step.progress"
              :stroke-width="3"
              :show-text="false"
              :color="step.progress === 100 ? '#67C23A' : '#409EFF'"
            />
            <span class="progress-text">{{ step.progress }}% 完成</span>
          </div>
        </div>

        <div class="step-action" v-if="currentStep === index">
          <el-button
            type="primary"
            size="small"
            @click.stop="executeStepAction(step)"
            :loading="stepLoading"
          >
            {{ step.actionText }}
          </el-button>
        </div>
      </div>
    </div>

    <div class="guide-footer">
      <div class="progress-indicator">
        <span class="progress-text">
          进度: {{ completedSteps.length }}/{{ guideSteps.length }}
        </span>
        <el-progress
          :percentage="(completedSteps.length / guideSteps.length) * 100"
          :stroke-width="4"
          :show-text="false"
          color="#67C23A"
        />
      </div>
      
      <div class="footer-actions">
        <el-button
          v-if="completedSteps.length === guideSteps.length"
          type="success"
          @click="completeGuide"
        >
          <el-icon><Trophy /></el-icon>
          完成引导
        </el-button>
        <el-button
          v-else
          type="primary"
          @click="startGuidedCreation"
        >
          开始创作
        </el-button>
        <el-button
          type="text"
          @click="skipGuide"
        >
          稍后设置
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Close,
  Check,
  Trophy
} from '@element-plus/icons-vue'

// Props
interface Props {
  novelId: number
  moduleProgress?: Record<string, number>
}

const props = withDefaults(defineProps<Props>(), {
  moduleProgress: () => ({})
})

// Emits
const emit = defineEmits<{
  skip: []
  complete: []
  stepCompleted: [stepId: string]
}>()

// Router
const router = useRouter()

// 响应式数据
const showGuide = ref(true)
const currentStep = ref(0)
const completedSteps = ref<string[]>([])
const stepLoading = ref(false)

// 引导步骤配置
const guideSteps = ref([
  {
    id: 'worldview',
    title: '构建世界观',
    description: '为您的小说设定背景世界',
    actionText: '开始设定',
    route: 'worldview',
    available: true,
    progress: 0
  },
  {
    id: 'characters',
    title: '创建角色',
    description: '添加小说的主要角色',
    actionText: '添加角色',
    route: 'characters',
    available: true,
    progress: 0
  },
  {
    id: 'outline',
    title: '规划大纲',
    description: '制定小说的整体结构',
    actionText: '制定大纲',
    route: 'outline',
    available: true,
    progress: 0
  },
  {
    id: 'chapters',
    title: '开始写作',
    description: '创作您的第一章内容',
    actionText: '开始写作',
    route: 'chapters',
    available: true,
    progress: 0
  }
])

// 计算属性
const isGuideCompleted = computed(() => {
  return completedSteps.value.length === guideSteps.value.length
})

// 方法
const checkGuideStatus = () => {
  // 检查是否已经完成引导
  const guideCompleted = localStorage.getItem('workspace_guide_completed')
  if (guideCompleted === 'true') {
    showGuide.value = false
    return
  }

  // 根据模块进度更新步骤状态
  guideSteps.value.forEach(step => {
    const progress = props.moduleProgress[step.id] || 0
    step.progress = progress
    
    if (progress > 0 && !completedSteps.value.includes(step.id)) {
      completedSteps.value.push(step.id)
    }
  })

  // 更新当前步骤
  updateCurrentStep()
}

const updateCurrentStep = () => {
  const nextStep = guideSteps.value.findIndex(
    step => !completedSteps.value.includes(step.id)
  )
  currentStep.value = nextStep >= 0 ? nextStep : guideSteps.value.length - 1
}

const goToStep = (step: any) => {
  if (!step.available) return
  
  const stepIndex = guideSteps.value.findIndex(s => s.id === step.id)
  if (stepIndex >= 0) {
    currentStep.value = stepIndex
  }
}

const executeStepAction = async (step: any) => {
  try {
    stepLoading.value = true
    
    // 跳转到对应模块页面，带上引导标识
    const route = `/workspace/${props.novelId}/${step.route}?guided=true`
    
    ElMessage.info(`即将进入${step.title}模块`)
    
    // 延迟跳转，给用户反馈
    setTimeout(() => {
      router.push(route)
    }, 500)
    
  } catch (error) {
    console.error('执行步骤操作失败:', error)
    ElMessage.error('操作失败，请稍后重试')
  } finally {
    setTimeout(() => {
      stepLoading.value = false
    }, 500)
  }
}

const markStepCompleted = (stepId: string) => {
  if (!completedSteps.value.includes(stepId)) {
    completedSteps.value.push(stepId)
    updateCurrentStep()
    
    // 更新对应步骤的进度
    const step = guideSteps.value.find(s => s.id === stepId)
    if (step) {
      step.progress = 100
    }
    
    emit('stepCompleted', stepId)
    
    // 保存进度到本地存储
    localStorage.setItem('guide_completed_steps', JSON.stringify(completedSteps.value))
  }
}

const startGuidedCreation = () => {
  const firstIncompleteStep = guideSteps.value.find(
    step => !completedSteps.value.includes(step.id)
  )
  
  if (firstIncompleteStep) {
    executeStepAction(firstIncompleteStep)
  } else {
    // 所有步骤都完成了，跳转到章节编辑
    router.push(`/workspace/${props.novelId}/chapters`)
  }
}

const skipGuide = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要跳过新手引导吗？您可以随时通过帮助菜单重新打开。',
      '跳过引导',
      {
        confirmButtonText: '确定跳过',
        cancelButtonText: '继续引导',
        type: 'warning'
      }
    )
    
    showGuide.value = false
    localStorage.setItem('workspace_guide_completed', 'true')
    
    emit('skip')
    
  } catch (error) {
    // 用户取消了操作
  }
}

const completeGuide = () => {
  showGuide.value = false
  localStorage.setItem('workspace_guide_completed', 'true')
  
  ElMessage.success('🎉 恭喜您完成了新手引导！')
  
  emit('complete')
}

// 公开方法给父组件
const showQuickGuide = () => {
  showGuide.value = true
  localStorage.removeItem('workspace_guide_completed')
}

const hideQuickGuide = () => {
  showGuide.value = false
}

// 暴露方法给父组件
defineExpose({
  showQuickGuide,
  hideQuickGuide,
  markStepCompleted
})

// 生命周期
onMounted(() => {
  checkGuideStatus()
  
  // 从本地存储恢复已完成的步骤
  const savedSteps = localStorage.getItem('guide_completed_steps')
  if (savedSteps) {
    try {
      completedSteps.value = JSON.parse(savedSteps)
      updateCurrentStep()
    } catch (error) {
      console.warn('恢复引导进度失败:', error)
    }
  }
})
</script>

<style scoped lang="scss">
.quick-start-guide {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  position: relative;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M 10 0 L 0 0 0 10" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="0.5"/></pattern></defs><rect width="100" height="100" fill="url(%23grid)"/></svg>');
    opacity: 0.3;
  }

  .guide-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 20px;
    position: relative;
    z-index: 1;

    .guide-content {
      flex: 1;

      .guide-title {
        font-size: 20px;
        font-weight: 600;
        margin: 0 0 8px 0;
      }

      .guide-description {
        opacity: 0.9;
        margin: 0;
        line-height: 1.5;
      }
    }

    .skip-btn {
      color: rgba(255, 255, 255, 0.8);
      padding: 4px;
      
      &:hover {
        color: white;
        background: rgba(255, 255, 255, 0.1);
      }
    }
  }

  .guide-steps {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 16px;
    margin-bottom: 20px;
    position: relative;
    z-index: 1;

    .step-item {
      background: rgba(255, 255, 255, 0.1);
      border-radius: 8px;
      padding: 16px;
      transition: all 0.3s ease;
      border: 2px solid transparent;

      &.active {
        background: rgba(255, 255, 255, 0.2);
        border-color: rgba(255, 255, 255, 0.3);
        transform: translateY(-2px);
      }

      &.completed {
        background: rgba(103, 194, 58, 0.2);
        border-color: rgba(103, 194, 58, 0.3);
      }

      &.clickable {
        cursor: pointer;

        &:hover {
          background: rgba(255, 255, 255, 0.15);
        }
      }

      .step-number {
        width: 32px;
        height: 32px;
        background: rgba(255, 255, 255, 0.2);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 12px;
        font-weight: 600;
        font-size: 14px;

        .el-icon {
          color: #67C23A;
          font-size: 16px;
        }
      }

      .step-content {
        text-align: center;

        .step-title {
          font-weight: 500;
          margin-bottom: 4px;
          font-size: 14px;
        }

        .step-description {
          font-size: 12px;
          opacity: 0.8;
          margin-bottom: 8px;
        }

        .step-progress {
          margin-top: 8px;

          .progress-text {
            font-size: 11px;
            opacity: 0.8;
            margin-top: 4px;
            display: block;
          }
        }
      }

      .step-action {
        margin-top: 12px;
        text-align: center;
      }
    }
  }

  .guide-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    position: relative;
    z-index: 1;
    gap: 16px;

    .progress-indicator {
      flex: 1;

      .progress-text {
        font-size: 12px;
        opacity: 0.9;
        margin-bottom: 4px;
        display: block;
      }
    }

    .footer-actions {
      display: flex;
      gap: 8px;
      flex-shrink: 0;
    }
  }
}

// 响应式设计
@media (max-width: 767px) {
  .quick-start-guide {
    padding: 16px;

    .guide-steps {
      grid-template-columns: 1fr;
      gap: 12px;
    }

    .guide-footer {
      flex-direction: column;
      gap: 12px;

      .footer-actions {
        width: 100%;
        justify-content: center;
      }
    }
  }
}

@media (max-width: 480px) {
  .quick-start-guide {
    .guide-header {
      .guide-title {
        font-size: 18px;
      }

      .guide-description {
        font-size: 13px;
      }
    }

    .guide-steps {
      .step-item {
        padding: 12px;

        .step-number {
          width: 28px;
          height: 28px;
          margin-bottom: 8px;
        }
      }
    }
  }
}
</style>