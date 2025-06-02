<template>
  <section class="features-section">
    <div class="features-container">
      <!-- 标题区域 -->
      <div class="section-header">
        <h2 class="section-title">🎯 强大功能</h2>
        <p class="section-subtitle">
          全方位AI创作工具，让每个人都能成为优秀的小说家
        </p>
      </div>
      
      <!-- 功能卡片网格 -->
      <div class="features-grid">
        <el-card 
          v-for="(feature, index) in features" 
          :key="feature.id"
          class="feature-card"
          :class="{ 'animate': showAnimation }"
          :style="{ 'animation-delay': `${index * 0.2}s` }"
          @click="handleFeatureClick(feature)"
          shadow="hover"
        >
          <!-- 卡片头部 -->
          <div class="card-header">
            <div class="feature-icon" :style="{ color: feature.color }">
              <el-icon :size="48">
                <component :is="feature.icon" />
              </el-icon>
            </div>
            <div class="feature-status" v-if="feature.status">
              <el-tag 
                :type="getStatusType(feature.status)" 
                size="small" 
                round
              >
                {{ getStatusText(feature.status) }}
              </el-tag>
            </div>
          </div>
          
          <!-- 卡片内容 -->
          <div class="card-content">
            <h3 class="feature-title">{{ feature.title }}</h3>
            <p class="feature-description">{{ feature.description }}</p>
            
            <!-- 功能亮点 -->
            <ul class="feature-highlights" v-if="feature.highlights">
              <li v-for="highlight in feature.highlights" :key="highlight">
                <el-icon class="highlight-icon"><Check /></el-icon>
                {{ highlight }}
              </li>
            </ul>
          </div>
          
          <!-- 卡片底部操作 -->
          <div class="card-actions">
            <el-button 
              :type="feature.primary ? 'primary' : 'default'" 
              :plain="!feature.primary"
              @click.stop="handleFeatureAction(feature)"
              :disabled="feature.disabled"
              class="action-button"
            >
              {{ feature.actionText }}
            </el-button>
            
            <!-- 使用统计 -->
            <div class="usage-stats" v-if="feature.usageCount">
              <span class="stats-text">
                已使用 {{ formatUsageCount(feature.usageCount) }} 次
              </span>
            </div>
          </div>
        </el-card>
      </div>
      
      <!-- 更多功能预告 -->
      <div class="coming-soon-section" v-if="comingSoonFeatures.length > 0">
        <h3 class="coming-soon-title">🚀 即将推出</h3>
        <div class="coming-soon-grid">
          <div 
            v-for="feature in comingSoonFeatures" 
            :key="feature.id"
            class="coming-soon-card"
          >
            <div class="coming-soon-icon">
              <el-icon :size="32">
                <component :is="feature.icon" />
              </el-icon>
            </div>
            <div class="coming-soon-content">
              <h4>{{ feature.title }}</h4>
              <p>{{ feature.description }}</p>
              <el-tag type="info" size="small">{{ feature.timeline }}</el-tag>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  MagicStick,
  EditPen,
  TrendCharts,
  Star,
  UserFilled,
  DocumentCopy,
  Setting,
  Timer,
  Check
} from '@element-plus/icons-vue'
import { HomepageService } from '@/api/homepage'

const router = useRouter()

// 响应式数据
const showAnimation = ref(false)
const systemStatus = ref<any>(null)

// 功能配置
interface Feature {
  id: string
  title: string
  description: string
  icon: any
  color: string
  route: string
  actionText: string
  primary?: boolean
  disabled?: boolean
  status?: 'available' | 'limited' | 'unavailable'
  highlights?: string[]
  usageCount?: number
}

const features = ref<Feature[]>([
  {
    id: 'brain-generator',
    title: '脑洞生成器',
    description: '激发无限创意，让AI帮你打开想象力的闸门',
    icon: MagicStick,
    color: '#409eff',
    route: '/tools/brain-generator',
    actionText: '立即体验',
    primary: true,
    highlights: [
      '智能主题生成',
      '多维度创意组合',
      '一键生成完整设定'
    ],
    usageCount: 1234
  },
  {
    id: 'novel-assistant',
    title: '小说创作助手',
    description: '从标题到大纲，从角色到情节，全流程AI辅助创作',
    icon: EditPen,
    color: '#67c23a',
    route: '/novels/create',
    actionText: '开始创作',
    highlights: [
      '智能标题生成',
      'AI情节建议',
      '角色关系分析'
    ],
    usageCount: 2156
  },
  {
    id: 'outline-generator',
    title: '智能大纲生成',
    description: '结构化故事框架，让你的小说逻辑清晰，情节紧凑',
    icon: TrendCharts,
    color: '#e6a23c',
    route: '/workspace',
    actionText: '生成大纲',
    highlights: [
      '三幕式结构',
      '冲突点设计',
      '节奏控制优化'
    ],
    usageCount: 876
  },
  {
    id: 'character-builder',
    title: '角色塑造工具',
    description: '立体化角色设定，让每个人物都有独特的性格和成长轨迹',
    icon: Star,
    color: '#f56c6c',
    route: '/tools/character-templates',
    actionText: '角色模板',
    highlights: [
      '性格特征分析',
      '背景故事生成',
      '角色关系图谱'
    ],
    usageCount: 654
  }
])

const comingSoonFeatures = ref([
  {
    id: 'ai-reviewer',
    title: 'AI审核助手',
    description: '智能内容审核和质量评估',
    icon: UserFilled,
    timeline: 'V2.0'
  },
  {
    id: 'export-tools',
    title: '多平台导出',
    description: '一键发布到各大小说平台',
    icon: DocumentCopy,
    timeline: 'V2.1'
  },
  {
    id: 'advanced-settings',
    title: '高级设置',
    description: '个性化AI写作风格定制',
    icon: Setting,
    timeline: 'V2.2'
  },
  {
    id: 'timeline-manager',
    title: '时间轴管理',
    description: '故事时间线可视化管理',
    icon: Timer,
    timeline: 'V2.3'
  }
])

// 格式化使用次数
const formatUsageCount = (count: number) => {
  if (count >= 1000) {
    return `${(count / 1000).toFixed(1)}k`
  }
  return count.toString()
}

// 获取状态类型
const getStatusType = (status: string) => {
  const typeMap = {
    'available': 'success',
    'limited': 'warning',
    'unavailable': 'danger'
  }
  return typeMap[status as keyof typeof typeMap] || 'info'
}

// 获取状态文本
const getStatusText = (status: string) => {
  const textMap = {
    'available': '可用',
    'limited': '限制',
    'unavailable': '不可用'
  }
  return textMap[status as keyof typeof textMap] || status
}

// 处理功能卡片点击
const handleFeatureClick = (feature: Feature) => {
  if (feature.disabled) {
    ElMessage.warning('该功能暂时不可用')
    return
  }
  
  // 添加点击统计
  console.log(`Feature clicked: ${feature.id}`)
}

// 处理功能操作
const handleFeatureAction = (feature: Feature) => {
  if (feature.disabled) {
    ElMessage.warning('该功能暂时不可用')
    return
  }
  
  // 检查登录状态（某些功能需要登录）
  const requiresAuth = ['novel-assistant', 'outline-generator']
  const isLoggedIn = !!localStorage.getItem('access_token')
  
  if (requiresAuth.includes(feature.id) && !isLoggedIn) {
    ElMessage.info('请先登录以使用此功能')
    router.push('/auth/login')
    return
  }
  
  // 跳转到对应页面
  router.push(feature.route)
}

// 加载系统状态
const loadSystemStatus = async () => {
  try {
    const status = await HomepageService.getSystemStatus()
    systemStatus.value = status
    
    // 根据系统状态更新功能可用性
    updateFeatureStatus(status)
  } catch (error) {
    console.error('加载系统状态失败:', error)
  }
}

// 更新功能状态
const updateFeatureStatus = (status: any) => {
  features.value.forEach(feature => {
    switch (feature.id) {
      case 'brain-generator':
        feature.status = status.feature_flags?.brain_generator ? 'available' : 'unavailable'
        feature.disabled = !status.feature_flags?.brain_generator
        break
      case 'novel-assistant':
        feature.status = status.ai_service === 'available' ? 'available' : 
                        status.ai_service === 'limited' ? 'limited' : 'unavailable'
        feature.disabled = status.ai_service === 'unavailable'
        break
      default:
        feature.status = 'available'
    }
  })
}

// 启动动画
const startAnimation = () => {
  setTimeout(() => {
    showAnimation.value = true
  }, 300)
}

// 生命周期
onMounted(() => {
  loadSystemStatus()
  startAnimation()
})
</script>

<style scoped>
.features-section {
  padding: 80px 0;
  background: #f8fafc;
}

.features-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 20px;
}

.section-header {
  text-align: center;
  margin-bottom: 60px;
}

.section-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: #2d3748;
  margin-bottom: 16px;
}

.section-subtitle {
  font-size: 1.2rem;
  color: #718096;
  margin: 0;
  max-width: 600px;
  margin: 0 auto;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 32px;
  margin-bottom: 80px;
}

.feature-card {
  border-radius: 16px;
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
  transform: translateY(20px);
  opacity: 0;
  overflow: hidden;
  background: white;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
}

.feature-card.animate {
  transform: translateY(0);
  opacity: 1;
}

.feature-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}

.feature-icon {
  margin-bottom: 20px;
  transition: transform 0.3s ease;
}

.feature-card:hover .feature-icon {
  transform: scale(1.1);
}

.feature-status {
  flex-shrink: 0;
}

.card-content {
  flex: 1;
}

.feature-title {
  font-size: 1.4rem;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 12px;
}

.feature-description {
  color: #718096;
  line-height: 1.6;
  margin-bottom: 16px;
}

.feature-highlights {
  list-style: none;
  padding: 0;
  margin: 0 0 20px 0;
}

.feature-highlights li {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #4a5568;
  font-size: 14px;
  margin-bottom: 6px;
}

.highlight-icon {
  color: #48bb78;
  font-size: 12px;
}

.card-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: auto;
  padding-top: 16px;
  border-top: 1px solid #e2e8f0;
}

.action-button {
  flex: 1;
  max-width: 140px;
  border-radius: 8px;
}

.usage-stats {
  font-size: 12px;
  color: #a0aec0;
}

.stats-text {
  white-space: nowrap;
}

/* 即将推出功能 */
.coming-soon-section {
  margin-top: 60px;
}

.coming-soon-title {
  font-size: 1.8rem;
  font-weight: 600;
  color: #2d3748;
  text-align: center;
  margin-bottom: 40px;
}

.coming-soon-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 24px;
}

.coming-soon-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: white;
  border-radius: 12px;
  border: 2px dashed #e2e8f0;
  transition: all 0.3s ease;
}

.coming-soon-card:hover {
  border-color: #cbd5e0;
  background: #f7fafc;
}

.coming-soon-icon {
  color: #a0aec0;
  flex-shrink: 0;
}

.coming-soon-content h4 {
  margin: 0 0 4px 0;
  font-size: 16px;
  color: #4a5568;
}

.coming-soon-content p {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: #718096;
  line-height: 1.4;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .features-section {
    padding: 60px 0;
  }
  
  .features-container {
    padding: 0 16px;
  }
  
  .section-title {
    font-size: 2rem;
  }
  
  .section-subtitle {
    font-size: 1rem;
  }
  
  .features-grid {
    grid-template-columns: 1fr;
    gap: 24px;
    margin-bottom: 60px;
  }
  
  .card-actions {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .action-button {
    max-width: none;
  }
  
  .usage-stats {
    text-align: center;
  }
  
  .coming-soon-grid {
    grid-template-columns: 1fr;
  }
  
  .coming-soon-card {
    flex-direction: column;
    text-align: center;
  }
}

@media (max-width: 480px) {
  .feature-card {
    padding: 16px;
  }
  
  .feature-highlights {
    font-size: 13px;
  }
  
  .coming-soon-card {
    padding: 16px;
  }
}

/* 动画效果 */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.feature-card.animate {
  animation: fadeInUp 0.6s ease-out forwards;
}
</style>