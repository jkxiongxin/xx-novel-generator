<template>
  <section class="quick-actions-section">
    <div class="actions-container">
      <!-- 标题区域 -->
      <div class="section-header">
        <h2 class="section-title">⚡ 快速入口</h2>
        <p class="section-subtitle">
          一键开始你的创作之旅
        </p>
      </div>
      
      <!-- 已登录用户的快速操作 -->
      <div v-if="isLoggedIn" class="logged-in-actions">
        <!-- 主要操作区域 -->
        <div class="primary-actions">
          <div class="action-card create-novel" @click="handleCreateNovel">
            <div class="card-background">
              <div class="bg-pattern"></div>
            </div>
            <div class="card-content">
              <el-icon class="action-icon" :size="48">
                <EditPen />
              </el-icon>
              <h3 class="action-title">创建新小说</h3>
              <p class="action-description">
                开始一个全新的创作项目
              </p>
              <el-button 
                type="primary" 
                size="large"
                :loading="createLoading"
                class="action-button"
              >
                立即创建
              </el-button>
            </div>
          </div>
          
          <div class="action-card continue-writing" @click="handleContinueWriting">
            <div class="card-background">
              <div class="bg-pattern"></div>
            </div>
            <div class="card-content">
              <el-icon class="action-icon" :size="48">
                <Document />
              </el-icon>
              <h3 class="action-title">继续创作</h3>
              <p class="action-description">
                回到最近编辑的作品
              </p>
              <el-button 
                type="success" 
                size="large"
                :loading="continueLoading"
                class="action-button"
              >
                继续写作
              </el-button>
            </div>
          </div>
        </div>
        
        <!-- 辅助操作区域 -->
        <div class="secondary-actions">
          <el-row :gutter="20">
            <el-col :span="8" v-for="action in secondaryActions" :key="action.id">
              <div 
                class="secondary-action-card"
                @click="handleSecondaryAction(action)"
              >
                <div class="secondary-icon" :style="{ color: action.color }">
                  <el-icon :size="24">
                    <component :is="action.icon" />
                  </el-icon>
                </div>
                <div class="secondary-content">
                  <h4 class="secondary-title">{{ action.title }}</h4>
                  <p class="secondary-description">{{ action.description }}</p>
                </div>
                <el-icon class="arrow-icon">
                  <ArrowRight />
                </el-icon>
              </div>
            </el-col>
          </el-row>
        </div>
      </div>
      
      <!-- 未登录用户的引导操作 -->
      <div v-else class="guest-actions">
        <div class="guest-content">
          <div class="guest-illustration">
            <el-icon :size="80" color="#409eff">
              <Star />
            </el-icon>
          </div>
          <h3 class="guest-title">开始你的创作之旅</h3>
          <p class="guest-description">
            注册账号，解锁全部AI创作功能
          </p>
          
          <!-- 体验功能 -->
          <div class="trial-features">
            <div class="trial-item" v-for="feature in trialFeatures" :key="feature.id">
              <el-icon :size="20" :color="feature.color">
                <component :is="feature.icon" />
              </el-icon>
              <span>{{ feature.title }}</span>
            </div>
          </div>
          
          <!-- 操作按钮 -->
          <div class="guest-buttons">
            <el-button 
              type="primary" 
              size="large"
              @click="handleRegister"
              class="register-button"
            >
              立即注册
            </el-button>
            <el-button 
              size="large"
              @click="handleLogin"
              plain
              class="login-button"
            >
              已有账号登录
            </el-button>
          </div>
          
          <!-- 免费体验入口 -->
          <div class="free-trial">
            <p class="trial-text">或者先免费体验</p>
            <el-button 
              type="success" 
              @click="handleTrialFeature"
              plain
              class="trial-button"
            >
              <el-icon><MagicStick /></el-icon>
              脑洞生成器
            </el-button>
          </div>
        </div>
      </div>
      
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  EditPen,
  Document,
  MagicStick,
  Star,
  TrendCharts,
  UserFilled,
  ArrowRight,
  Folder,
  DataAnalysis,
  Setting
} from '@element-plus/icons-vue'
import { HomepageService } from '@/api/homepage'

const router = useRouter()

// 响应式数据
const createLoading = ref(false)
const continueLoading = ref(false)
const loginStatus = ref(!!localStorage.getItem('access_token'))

// 计算属性
const isLoggedIn = computed(() => loginStatus.value)

// 监听localStorage变化
const handleStorageChange = (event: StorageEvent) => {
  if (event.key === 'access_token') {
    loginStatus.value = !!event.newValue
  }
}

// 监听token变化
watch(() => localStorage.getItem('access_token'), (newToken) => {
  loginStatus.value = !!newToken
}, { immediate: true })


// 次要操作配置
const secondaryActions = ref([
  {
    id: 'my-novels',
    title: '我的小说',
    description: '查看管理所有作品',
    icon: Folder,
    color: '#409eff',
    route: '/novels'
  },
  {
    id: 'brain-generator',
    title: '脑洞生成器',
    description: 'AI创意激发工具',
    icon: MagicStick,
    color: '#67c23a',
    route: '/brain-generator'
  },
  {
    id: 'ai-config-management',
    title: 'AI模型配置',
    description: '管理AI模型和设置',
    icon: Setting,
    color: '#909399',
    route: '/ai-config-management'
  }
])

// 体验功能列表
const trialFeatures = [
  { id: 'brain', title: '脑洞生成', icon: MagicStick, color: '#67c23a' },
  { id: 'template', title: '角色模板', icon: UserFilled, color: '#409eff' },
  { id: 'outline', title: '大纲助手', icon: TrendCharts, color: '#e6a23c' }
]

// 处理创建新小说 - 直接跳转到创建页面
const handleCreateNovel = () => {
  router.push('/novels/create')
}

// 处理继续写作
const handleContinueWriting = async () => {
  try {
    continueLoading.value = true
    
    // 获取最近编辑的小说
    const recentNovels = await HomepageService.getRecentNovels(1)
    
    if (recentNovels.novels.length > 0) {
      const latestNovel = recentNovels.novels[0]
      router.push(`/workspace/${latestNovel.id}/chapters`)
    } else {
      ElMessage.info('暂无作品，请先创建一部小说')
      // 没有小说时也跳转到创建页面，与"创建新小说"保持一致
      router.push('/novels/create')
    }
  } catch (error) {
    console.error('获取最近作品失败:', error)
    ElMessage.error('获取最近作品失败')
    // 出错时也跳转到创建页面
    router.push('/novels/create')
  } finally {
    continueLoading.value = false
  }
}

// 处理次要操作
const handleSecondaryAction = (action: any) => {
  router.push(action.route)
}


// 处理注册
const handleRegister = () => {
  router.push('/auth/register')
}

// 处理登录
const handleLogin = () => {
  router.push('/auth/login')
}

// 处理免费体验
const handleTrialFeature = () => {
  router.push('/tools/brain-generator')
}

// 生命周期
onMounted(() => {
  // 组件初始化
  window.addEventListener('storage', handleStorageChange)
})

onUnmounted(() => {
  window.removeEventListener('storage', handleStorageChange)
})
</script>

<style scoped>
.quick-actions-section {
  padding: 80px 0;
  background: white;
}

.actions-container {
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
}

/* 已登录用户操作 */
.logged-in-actions {
  max-width: 1000px;
  margin: 0 auto;
}

.primary-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 32px;
  margin-bottom: 48px;
}

.action-card {
  position: relative;
  background: white;
  border-radius: 20px;
  padding: 40px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
  overflow: hidden;
  min-height: 280px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.action-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  opacity: 0.05;
  transition: opacity 0.3s ease;
}

.action-card:hover::before {
  opacity: 0.1;
}

.action-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
  border-color: #667eea;
}

.card-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  overflow: hidden;
}

.bg-pattern {
  position: absolute;
  top: -50%;
  right: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(102, 126, 234, 0.1) 0%, transparent 70%);
  animation: rotate 20s linear infinite;
}

.card-content {
  position: relative;
  z-index: 2;
  text-align: center;
}

.action-icon {
  color: #667eea;
  margin-bottom: 20px;
}

.action-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 12px;
}

.action-description {
  color: #718096;
  margin-bottom: 24px;
  line-height: 1.5;
}

.action-button {
  width: 100%;
  height: 48px;
  font-size: 16px;
  border-radius: 12px;
}

.create-novel .action-button {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
}

.continue-writing .action-button {
  background: linear-gradient(135deg, #67c23a 0%, #85ce61 100%);
  border: none;
}

.secondary-actions {
  margin-top: 40px;
}

.secondary-action-card {
  display: flex;
  align-items: center;
  padding: 20px;
  background: #f8fafc;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid #e2e8f0;
}

.secondary-action-card:hover {
  background: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.secondary-icon {
  margin-right: 16px;
  flex-shrink: 0;
}

.secondary-content {
  flex: 1;
}

.secondary-title {
  font-size: 16px;
  font-weight: 600;
  color: #2d3748;
  margin: 0 0 4px 0;
}

.secondary-description {
  font-size: 14px;
  color: #718096;
  margin: 0;
}

.arrow-icon {
  color: #a0aec0;
  transition: transform 0.3s ease;
}

.secondary-action-card:hover .arrow-icon {
  transform: translateX(4px);
}

/* 未登录用户操作 */
.guest-actions {
  max-width: 600px;
  margin: 0 auto;
  text-align: center;
}

.guest-content {
  background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
  border-radius: 20px;
  padding: 60px 40px;
}

.guest-illustration {
  margin-bottom: 24px;
}

.guest-title {
  font-size: 1.8rem;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 16px;
}

.guest-description {
  font-size: 1.1rem;
  color: #718096;
  margin-bottom: 32px;
}

.trial-features {
  display: flex;
  justify-content: center;
  gap: 24px;
  margin-bottom: 32px;
  flex-wrap: wrap;
}

.trial-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: white;
  border-radius: 20px;
  font-size: 14px;
  color: #4a5568;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.guest-buttons {
  display: flex;
  gap: 16px;
  justify-content: center;
  margin-bottom: 32px;
  flex-wrap: wrap;
}

.register-button,
.login-button {
  min-width: 140px;
  height: 48px;
  font-size: 16px;
  border-radius: 12px;
}

.free-trial {
  border-top: 1px solid #e2e8f0;
  padding-top: 24px;
}

.trial-text {
  font-size: 14px;
  color: #718096;
  margin-bottom: 16px;
}

.trial-button {
  border-radius: 12px;
}

/* 动画效果 */
@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .quick-actions-section {
    padding: 60px 0;
  }
  
  .actions-container {
    padding: 0 16px;
  }
  
  .section-title {
    font-size: 2rem;
  }
  
  .primary-actions {
    grid-template-columns: 1fr;
    gap: 24px;
  }
  
  .action-card {
    padding: 32px 24px;
    min-height: 240px;
  }
  
  .secondary-actions .el-col {
    margin-bottom: 16px;
  }
  
  .guest-content {
    padding: 40px 24px;
  }
  
  .guest-buttons {
    flex-direction: column;
    align-items: center;
  }
  
  .register-button,
  .login-button {
    width: 100%;
    max-width: 280px;
  }
  
  .trial-features {
    flex-direction: column;
    align-items: center;
  }
}

@media (max-width: 480px) {
  .action-card {
    padding: 24px 20px;
  }
  
  .action-title {
    font-size: 1.3rem;
  }
  
  .secondary-action-card {
    padding: 16px;
  }
}
</style>