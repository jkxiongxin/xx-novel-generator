<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { MagicStick, EditPen, TrendCharts, Star } from '@element-plus/icons-vue'

const router = useRouter()

// 功能特性数据
const features = ref([
  {
    icon: MagicStick,
    title: '脑洞生成器',
    description: '激发无限创意，让AI帮你打开想象力的闸门',
    route: '/brain-generator',
    color: '#409eff'
  },
  {
    icon: EditPen,
    title: '小说创作助手',
    description: '从标题到大纲，从角色到情节，全流程AI辅助创作',
    route: '/novel-create',
    color: '#67c23a'
  },
  {
    icon: TrendCharts,
    title: '智能大纲生成',
    description: '结构化故事框架，让你的小说逻辑清晰，情节紧凑',
    route: '/novel-create',
    color: '#e6a23c'
  },
  {
    icon: Star,
    title: '角色塑造工具',
    description: '立体化角色设定，让每个人物都有独特的性格和成长轨迹',
    route: '/novel-create',
    color: '#f56c6c'
  }
])

// 统计数据
const stats = ref([
  { label: '累计生成作品', value: '1,234', suffix: '部' },
  { label: '活跃创作者', value: '5,678', suffix: '人' },
  { label: '创意脑洞', value: '9,876', suffix: '个' },
  { label: '好评率', value: '98.5', suffix: '%' }
])

// 跳转到功能页面
const navigateTo = (route: string) => {
  router.push(route)
}
</script>

<template>
  <div class="home-view">
    <!-- Hero Section -->
    <section class="hero-section">
      <div class="hero-content">
        <h1 class="hero-title">
          🚀 AI智能小说创作平台
        </h1>
        <p class="hero-subtitle">
          让人工智能成为你的创作伙伴，从灵感火花到完整作品，我们陪伴你的每一步创作之旅
        </p>
        <div class="hero-actions">
          <el-button 
            type="primary" 
            size="large"
            @click="navigateTo('/brain-generator')"
            class="cta-button"
          >
            <el-icon><MagicStick /></el-icon>
            开始创作
          </el-button>
          <el-button 
            size="large"
            @click="navigateTo('/novel-create')"
            class="secondary-button"
          >
            <el-icon><EditPen /></el-icon>
            探索功能
          </el-button>
        </div>
      </div>
      <div class="hero-image">
        <div class="floating-card">
          <div class="card-content">
            <h3>💡 灵感瞬间</h3>
            <p>"在遥远的星球上，有一个会唱歌的机器人..."</p>
          </div>
        </div>
        <div class="floating-card card-2">
          <div class="card-content">
            <h3>📝 智能助手</h3>
            <p>AI正在为您生成精彩的情节发展...</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section class="features-section">
      <div class="container">
        <h2 class="section-title">🎯 强大功能</h2>
        <p class="section-subtitle">
          全方位AI创作工具，让每个人都能成为优秀的小说家
        </p>
        
        <div class="features-grid">
          <el-card 
            v-for="feature in features" 
            :key="feature.title"
            class="feature-card"
            :class="{ 'hover-effect': true }"
            @click="navigateTo(feature.route)"
          >
            <div class="feature-icon" :style="{ color: feature.color }">
              <el-icon :size="48">
                <component :is="feature.icon" />
              </el-icon>
            </div>
            <h3 class="feature-title">{{ feature.title }}</h3>
            <p class="feature-description">{{ feature.description }}</p>
            <el-button 
              :type="'primary'" 
              plain 
              size="small"
              @click.stop="navigateTo(feature.route)"
            >
              立即体验
            </el-button>
          </el-card>
        </div>
      </div>
    </section>

    <!-- Stats Section -->
    <section class="stats-section">
      <div class="container">
        <h2 class="section-title">📊 平台数据</h2>
        <div class="stats-grid">
          <div v-for="stat in stats" :key="stat.label" class="stat-item">
            <div class="stat-value">
              {{ stat.value }}
              <span class="stat-suffix">{{ stat.suffix }}</span>
            </div>
            <div class="stat-label">{{ stat.label }}</div>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="cta-section">
      <div class="container">
        <div class="cta-content">
          <h2 class="cta-title">🌟 准备好开始你的创作之旅了吗？</h2>
          <p class="cta-subtitle">
            无论你是资深作家还是写作新手，AI都能为你提供强大的创作支持
          </p>
          <div class="cta-actions">
            <el-button 
              type="primary" 
              size="large"
              @click="navigateTo('/brain-generator')"
              class="cta-primary"
            >
              <el-icon><MagicStick /></el-icon>
              开启脑洞模式
            </el-button>
            <el-button 
              type="success" 
              size="large"
              @click="navigateTo('/novel-create')"
              class="cta-secondary"
            >
              <el-icon><EditPen /></el-icon>
              开始写小说
            </el-button>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.home-view {
  min-height: 100vh;
}

/* Hero Section */
.hero-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 80px 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 70vh;
  position: relative;
  overflow: hidden;
}

.hero-content {
  max-width: 600px;
  text-align: center;
  z-index: 2;
}

.hero-title {
  font-size: 3.5rem;
  font-weight: bold;
  margin-bottom: 20px;
  line-height: 1.2;
}

.hero-subtitle {
  font-size: 1.2rem;
  margin-bottom: 40px;
  opacity: 0.9;
  line-height: 1.6;
}

.hero-actions {
  display: flex;
  gap: 20px;
  justify-content: center;
  flex-wrap: wrap;
}

.cta-button, .secondary-button {
  padding: 15px 30px;
  font-size: 1.1rem;
  border-radius: 25px;
}

.hero-image {
  position: absolute;
  right: 50px;
  top: 50%;
  transform: translateY(-50%);
  z-index: 1;
}

.floating-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  padding: 20px;
  margin-bottom: 20px;
  max-width: 300px;
  animation: float 6s ease-in-out infinite;
}

.card-2 {
  animation-delay: 3s;
  margin-left: 50px;
}

.floating-card h3 {
  margin: 0 0 10px 0;
  font-size: 1.1rem;
}

.floating-card p {
  margin: 0;
  opacity: 0.8;
  font-size: 0.9rem;
}

@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-20px); }
}

/* Features Section */
.features-section {
  padding: 80px 20px;
  background: #f8fafc;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
}

.section-title {
  font-size: 2.5rem;
  text-align: center;
  margin-bottom: 15px;
  color: #2d3748;
}

.section-subtitle {
  font-size: 1.1rem;
  text-align: center;
  margin-bottom: 60px;
  color: #718096;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 30px;
}

.feature-card {
  text-align: center;
  padding: 40px 30px;
  border-radius: 15px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
}

.feature-card:hover {
  transform: translateY(-10px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
}

.feature-icon {
  margin-bottom: 20px;
}

.feature-title {
  font-size: 1.4rem;
  margin-bottom: 15px;
  color: #2d3748;
}

.feature-description {
  color: #718096;
  line-height: 1.6;
  margin-bottom: 25px;
}

/* Stats Section */
.stats-section {
  padding: 80px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 40px;
  margin-top: 40px;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 3rem;
  font-weight: bold;
  margin-bottom: 10px;
}

.stat-suffix {
  font-size: 1.5rem;
  opacity: 0.8;
}

.stat-label {
  font-size: 1.1rem;
  opacity: 0.9;
}

/* CTA Section */
.cta-section {
  padding: 80px 20px;
  background: #2d3748;
  color: white;
}

.cta-content {
  text-align: center;
  max-width: 800px;
  margin: 0 auto;
}

.cta-title {
  font-size: 2.5rem;
  margin-bottom: 20px;
}

.cta-subtitle {
  font-size: 1.2rem;
  margin-bottom: 40px;
  opacity: 0.9;
  line-height: 1.6;
}

.cta-actions {
  display: flex;
  gap: 20px;
  justify-content: center;
  flex-wrap: wrap;
}

.cta-primary, .cta-secondary {
  padding: 15px 30px;
  font-size: 1.1rem;
  border-radius: 25px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .hero-title {
    font-size: 2.5rem;
  }
  
  .hero-subtitle {
    font-size: 1rem;
  }
  
  .section-title {
    font-size: 2rem;
  }
  
  .hero-image {
    display: none;
  }
  
  .hero-actions, .cta-actions {
    flex-direction: column;
    align-items: center;
  }
  
  .cta-button, .secondary-button,
  .cta-primary, .cta-secondary {
    width: 100%;
    max-width: 300px;
  }
}
</style>
