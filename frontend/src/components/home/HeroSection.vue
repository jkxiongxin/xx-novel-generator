<template>
  <section class="hero-section">
    <div class="hero-container">
      <!-- 主要内容区域 -->
      <div class="hero-content">
        <div class="hero-badge">
          <el-tag type="success" size="large" round>
            🚀 AI智能创作助手
          </el-tag>
        </div>
        
        <h1 class="hero-title">
          让AI成为你的
          <span class="highlight">创作伙伴</span>
        </h1>
        
        <p class="hero-subtitle">
          从灵感火花到完整作品，我们提供全流程AI辅助创作工具
          <br />
          让每个人都能成为优秀的小说家
        </p>
        
        <!-- 统计数据 -->
        <div class="hero-stats" v-if="userStats">
          <div class="stat-item">
            <div class="stat-number">{{ formatNumber(userStats.total_novels) }}</div>
            <div class="stat-label">我的小说</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">{{ formatWordCount(userStats.total_words) }}</div>
            <div class="stat-label">总字数</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">{{ formatNumber(userStats.active_novels) }}</div>
            <div class="stat-label">连载中</div>
          </div>
        </div>
        
        <!-- 操作按钮 -->
        <div class="hero-actions">
          <el-button 
            type="primary" 
            size="large"
            :icon="EditPen"
            @click="handleCreateNovel"
            class="primary-action"
            :loading="createLoading"
          >
            {{ isLoggedIn ? '开始创作' : '立即体验' }}
          </el-button>
          
          <el-button 
            size="large"
            :icon="MagicStick"
            @click="handleBrainGenerator"
            class="secondary-action"
            plain
          >
            脑洞生成器
          </el-button>
        </div>
        
        <!-- 快速入门提示 -->
        <div class="hero-tips" v-if="!isLoggedIn">
          <p class="tip-text">
            <el-icon><InfoFilled /></el-icon>
            无需注册即可体验脑洞生成器
          </p>
        </div>
      </div>
      
      <!-- 装饰性内容区域 -->
      <div class="hero-decoration">
        <!-- 浮动卡片 -->
        <div class="floating-card card-1" :class="{ 'animate': showAnimation }">
          <div class="card-icon">💡</div>
          <div class="card-content">
            <h4>AI灵感助手</h4>
            <p>"在遥远的星球上，有一个会唱歌的机器人..."</p>
          </div>
        </div>
        
        <div class="floating-card card-2" :class="{ 'animate': showAnimation }">
          <div class="card-icon">📝</div>
          <div class="card-content">
            <h4>智能写作</h4>
            <p>AI正在为您生成精彩的情节发展...</p>
          </div>
        </div>
        
        <div class="floating-card card-3" :class="{ 'animate': showAnimation }">
          <div class="card-icon">⭐</div>
          <div class="card-content">
            <h4>角色塑造</h4>
            <p>为您的主角设计独特的性格和背景...</p>
          </div>
        </div>
        
        <!-- 背景装饰元素 -->
        <div class="decoration-dots">
          <div class="dot" v-for="i in 12" :key="i" :style="getDotStyle(i)"></div>
        </div>
      </div>
    </div>
    
    <!-- 背景渐变效果 -->
    <div class="hero-background">
      <div class="gradient-orb orb-1"></div>
      <div class="gradient-orb orb-2"></div>
      <div class="gradient-orb orb-3"></div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { EditPen, MagicStick, InfoFilled } from '@element-plus/icons-vue'
import { HomepageService, HomepageUtils, type NovelOverviewStats } from '@/api/homepage'

const router = useRouter()

// 响应式数据
const userStats = ref<NovelOverviewStats | null>(null)
const createLoading = ref(false)
const showAnimation = ref(false)

// 计算属性
const isLoggedIn = computed(() => {
  return !!localStorage.getItem('access_token')
})

// 格式化数字
const formatNumber = (num: number) => {
  if (num >= 1000) {
    return `${(num / 1000).toFixed(1)}k`
  }
  return num.toString()
}

// 格式化字数
const formatWordCount = HomepageUtils.formatWordCount

// 获取装饰点的样式
const getDotStyle = (index: number) => {
  const angle = (index * 30) % 360
  const radius = 200 + (index % 3) * 50
  const x = Math.cos(angle * Math.PI / 180) * radius
  const y = Math.sin(angle * Math.PI / 180) * radius
  
  return {
    transform: `translate(${x}px, ${y}px)`,
    animationDelay: `${index * 0.2}s`
  }
}

// 处理创建小说
const handleCreateNovel = async () => {
  if (!isLoggedIn.value) {
    router.push('/auth/register')
    return
  }
  
  try {
    createLoading.value = true
    // 跳转到小说创建页面
    router.push('/novels/create')
  } catch (error) {
    console.error('跳转失败:', error)
    ElMessage.error('跳转失败，请重试')
  } finally {
    createLoading.value = false
  }
}

// 处理脑洞生成器
const handleBrainGenerator = () => {
  router.push('/tools/brain-generator')
}

// 加载用户统计数据
const loadUserStats = async () => {
  if (!isLoggedIn.value) return
  
  try {
    const stats = await HomepageService.getOverviewStats()
    userStats.value = stats
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

// 启动动画
const startAnimation = () => {
  setTimeout(() => {
    showAnimation.value = true
  }, 500)
}

// 生命周期
onMounted(() => {
  loadUserStats()
  startAnimation()
})
</script>

<style scoped>
.hero-section {
  position: relative;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 80px 0 120px;
  min-height: 70vh;
  overflow: hidden;
}

.hero-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 20px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 60px;
  align-items: center;
  position: relative;
  z-index: 2;
}

.hero-content {
  animation: fadeInUp 0.8s ease-out;
}

.hero-badge {
  margin-bottom: 24px;
}

.hero-badge .el-tag {
  font-size: 14px;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.hero-title {
  font-size: 3.2rem;
  font-weight: 700;
  margin-bottom: 24px;
  line-height: 1.2;
}

.highlight {
  background: linear-gradient(135deg, #ffd700 0%, #ffb347 100%);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.hero-subtitle {
  font-size: 1.2rem;
  margin-bottom: 32px;
  opacity: 0.9;
  line-height: 1.6;
}

.hero-stats {
  display: flex;
  gap: 32px;
  margin-bottom: 40px;
}

.stat-item {
  text-align: center;
}

.stat-number {
  font-size: 2rem;
  font-weight: 700;
  color: #ffd700;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  opacity: 0.8;
}

.hero-actions {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.primary-action {
  padding: 16px 32px;
  font-size: 1.1rem;
  border-radius: 25px;
  background: linear-gradient(135deg, #ffd700 0%, #ffb347 100%);
  border: none;
  color: #333;
  font-weight: 600;
  transition: all 0.3s ease;
}

.primary-action:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(255, 215, 0, 0.4);
}

.secondary-action {
  padding: 16px 32px;
  font-size: 1.1rem;
  border-radius: 25px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.secondary-action:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
}

.hero-tips {
  margin-top: 16px;
}

.tip-text {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  opacity: 0.8;
  margin: 0;
}

.hero-decoration {
  position: relative;
  height: 500px;
}

.floating-card {
  position: absolute;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  padding: 20px;
  max-width: 280px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  transform: translateY(20px);
  opacity: 0;
  transition: all 0.8s ease;
}

.floating-card.animate {
  transform: translateY(0);
  opacity: 1;
}

.card-1 {
  top: 50px;
  right: 100px;
  animation: float 6s ease-in-out infinite;
}

.card-2 {
  top: 200px;
  right: 20px;
  animation: float 6s ease-in-out infinite 2s;
}

.card-3 {
  top: 350px;
  right: 120px;
  animation: float 6s ease-in-out infinite 4s;
}

.card-icon {
  font-size: 24px;
  margin-bottom: 12px;
}

.card-content h4 {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
}

.card-content p {
  margin: 0;
  font-size: 14px;
  opacity: 0.9;
  line-height: 1.4;
}

.decoration-dots {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.dot {
  position: absolute;
  width: 4px;
  height: 4px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  animation: twinkle 3s ease-in-out infinite;
}

.hero-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  overflow: hidden;
  z-index: 1;
}

.gradient-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(60px);
  opacity: 0.3;
  animation: float 8s ease-in-out infinite;
}

.orb-1 {
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, #ff6b6b, transparent);
  top: 10%;
  right: 10%;
  animation-delay: 0s;
}

.orb-2 {
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, #4ecdc4, transparent);
  bottom: 20%;
  left: 10%;
  animation-delay: 3s;
}

.orb-3 {
  width: 250px;
  height: 250px;
  background: radial-gradient(circle, #ffe66d, transparent);
  top: 50%;
  left: 50%;
  animation-delay: 6s;
}

/* 动画效果 */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(40px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-20px);
  }
}

@keyframes twinkle {
  0%, 100% {
    opacity: 0.3;
    transform: scale(1);
  }
  50% {
    opacity: 1;
    transform: scale(1.5);
  }
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .hero-container {
    grid-template-columns: 1fr;
    gap: 40px;
    text-align: center;
  }
  
  .hero-decoration {
    height: 300px;
  }
  
  .floating-card {
    position: static;
    display: none;
  }
  
  .decoration-dots {
    display: none;
  }
}

@media (max-width: 768px) {
  .hero-section {
    padding: 60px 0 80px;
  }
  
  .hero-container {
    padding: 0 16px;
  }
  
  .hero-title {
    font-size: 2.4rem;
  }
  
  .hero-subtitle {
    font-size: 1rem;
  }
  
  .hero-stats {
    flex-direction: column;
    gap: 16px;
    margin-bottom: 32px;
  }
  
  .stat-number {
    font-size: 1.6rem;
  }
  
  .hero-actions {
    flex-direction: column;
    align-items: center;
  }
  
  .primary-action,
  .secondary-action {
    width: 100%;
    max-width: 280px;
  }
  
  .hero-decoration {
    display: none;
  }
}

@media (max-width: 480px) {
  .hero-title {
    font-size: 2rem;
  }
  
  .hero-stats {
    flex-direction: row;
    justify-content: space-around;
  }
}
</style>