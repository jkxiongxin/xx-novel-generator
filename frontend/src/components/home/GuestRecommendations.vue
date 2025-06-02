<template>
  <section class="guest-recommendations-section">
    <div class="recommendations-container">
      <!-- 标题区域 -->
      <div class="section-header">
        <h2 class="section-title">✨ 探索AI创作的魅力</h2>
        <p class="section-subtitle">
          无需注册，立即体验我们的核心功能
        </p>
      </div>
      
      <!-- 推荐功能卡片 -->
      <div class="recommendations-grid">
        <!-- 脑洞生成器推荐 -->
        <div class="recommendation-card featured-card">
          <div class="card-badge">
            <el-tag type="success" size="small" round>免费体验</el-tag>
          </div>
          <div class="card-icon">
            <el-icon :size="64" color="#67c23a">
              <MagicStick />
            </el-icon>
          </div>
          <h3 class="card-title">脑洞生成器</h3>
          <p class="card-description">
            输入简单的关键词，AI为你生成充满创意的小说设定和故事灵感
          </p>
          <div class="card-features">
            <div class="feature-item">
              <el-icon><Check /></el-icon>
              <span>无限次数生成</span>
            </div>
            <div class="feature-item">
              <el-icon><Check /></el-icon>
              <span>多种创意风格</span>
            </div>
            <div class="feature-item">
              <el-icon><Check /></el-icon>
              <span>即时生成结果</span>
            </div>
          </div>
          <el-button 
            type="success" 
            size="large"
            @click="handleTryFeature('brain-generator')"
            class="try-button"
          >
            立即体验
          </el-button>
        </div>
        
        <!-- 角色模板推荐 -->
        <div class="recommendation-card">
          <div class="card-icon">
            <el-icon :size="48" color="#409eff">
              <UserFilled />
            </el-icon>
          </div>
          <h3 class="card-title">角色模板库</h3>
          <p class="card-description">
            浏览各种类型的角色模板，为你的小说寻找完美的主角
          </p>
          <el-button 
            type="primary" 
            @click="handleTryFeature('character-templates')"
            class="try-button"
            plain
          >
            查看模板
          </el-button>
        </div>
        
        <!-- 创作指南推荐 -->
        <div class="recommendation-card">
          <div class="card-icon">
            <el-icon :size="48" color="#e6a23c">
              <DocumentCopy />
            </el-icon>
          </div>
          <h3 class="card-title">创作指南</h3>
          <p class="card-description">
            学习专业的小说创作技巧，从新手到高手的进阶之路
          </p>
          <el-button 
            type="warning" 
            @click="handleTryFeature('writing-guide')"
            class="try-button"
            plain
          >
            查看指南
          </el-button>
        </div>
      </div>
      
      <!-- 成功案例展示 -->
      <div class="success-stories">
        <h3 class="stories-title">💫 用户创作案例</h3>
        <div class="stories-grid">
          <div 
            v-for="story in successStories" 
            :key="story.id"
            class="story-card"
          >
            <div class="story-content">
              <h4 class="story-title">{{ story.title }}</h4>
              <p class="story-excerpt">{{ story.excerpt }}</p>
              <div class="story-meta">
                <span class="story-genre">{{ story.genre }}</span>
                <span class="story-words">{{ story.words }}字</span>
              </div>
            </div>
            <div class="story-author">
              <el-avatar :size="32" :src="story.authorAvatar">
                {{ story.authorName.charAt(0) }}
              </el-avatar>
              <span class="author-name">{{ story.authorName }}</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 注册引导 -->
      <div class="registration-cta">
        <div class="cta-content">
          <h3 class="cta-title">🚀 准备开始你的创作之旅？</h3>
          <p class="cta-description">
            注册账号，解锁全部AI创作功能，包括智能写作助手、大纲生成器等高级工具
          </p>
          
          <!-- 会员功能预览 -->
          <div class="premium-features">
            <div class="feature-group">
              <h4>核心功能</h4>
              <ul>
                <li><el-icon><Check /></el-icon>无限制小说创作</li>
                <li><el-icon><Check /></el-icon>AI智能写作助手</li>
                <li><el-icon><Check /></el-icon>自动大纲生成</li>
              </ul>
            </div>
            <div class="feature-group">
              <h4>高级功能</h4>
              <ul>
                <li><el-icon><Check /></el-icon>角色关系分析</li>
                <li><el-icon><Check /></el-icon>情节冲突检测</li>
                <li><el-icon><Check /></el-icon>多平台发布</li>
              </ul>
            </div>
          </div>
          
          <div class="cta-buttons">
            <el-button 
              type="primary" 
              size="large"
              @click="handleRegister"
              class="register-button"
            >
              免费注册
            </el-button>
            <el-button 
              size="large"
              @click="handleLogin"
              class="login-button"
            >
              立即登录
            </el-button>
          </div>
        </div>
      </div>
      
      <!-- 常见问题 -->
      <div class="faq-section">
        <h3 class="faq-title">❓ 常见问题</h3>
        <el-collapse v-model="activeFaq" class="faq-collapse">
          <el-collapse-item 
            v-for="faq in faqList" 
            :key="faq.id"
            :title="faq.question"
            :name="faq.id"
          >
            <p class="faq-answer">{{ faq.answer }}</p>
          </el-collapse-item>
        </el-collapse>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  MagicStick,
  UserFilled,
  DocumentCopy,
  Check
} from '@element-plus/icons-vue'

const router = useRouter()

// 响应式数据
const activeFaq = ref(['1'])

// 成功案例数据
const successStories = ref([
  {
    id: 1,
    title: '星辰大海的征途',
    excerpt: '在遥远的银河系边缘，一支探险队发现了古老文明的遗迹...',
    genre: '科幻',
    words: '125,000',
    authorName: '星空漫步者',
    authorAvatar: ''
  },
  {
    id: 2,
    title: '江湖夜雨十年灯',
    excerpt: '少年剑客踏入江湖，却卷入了一场武林风波...',
    genre: '武侠',
    words: '98,000',
    authorName: '墨染青衫',
    authorAvatar: ''
  },
  {
    id: 3,
    title: '都市修仙传奇',
    excerpt: '现代都市中隐藏着修仙者的秘密，主角意外踏入这个世界...',
    genre: '都市',
    words: '167,000',
    authorName: '夜行者',
    authorAvatar: ''
  }
])

// FAQ数据
const faqList = ref([
  {
    id: '1',
    question: '平台是否完全免费？',
    answer: '基础功能完全免费，包括脑洞生成器、角色模板等。注册用户可以享受更多高级功能，如智能写作助手、大纲生成器等。'
  },
  {
    id: '2',
    question: 'AI生成的内容质量如何？',
    answer: '我们使用先进的AI模型，生成的内容具有很高的创意性和逻辑性。同时提供多种风格选择，满足不同类型小说的需求。'
  },
  {
    id: '3',
    question: '我的作品数据是否安全？',
    answer: '我们采用银行级别的数据加密技术，确保用户作品的安全性和隐私性。所有数据都会定期备份，永不丢失。'
  },
  {
    id: '4',
    question: '支持哪些小说类型？',
    answer: '支持所有主流小说类型，包括奇幻、科幻、都市、言情、武侠、历史等。AI可以根据不同类型提供相应的创作建议。'
  },
  {
    id: '5',
    question: '可以导出我的作品吗？',
    answer: '当然可以！支持多种格式导出，包括Word、PDF、TXT等，方便您在其他平台发布或保存。'
  }
])

// 处理功能体验
const handleTryFeature = (feature: string) => {
  switch (feature) {
    case 'brain-generator':
      router.push('/tools/brain-generator')
      break
    case 'character-templates':
      router.push('/tools/character-templates')
      break
    case 'writing-guide':
      router.push('/help/guide')
      break
    default:
      ElMessage.info('功能即将推出')
  }
}

// 处理注册
const handleRegister = () => {
  router.push('/auth/register')
}

// 处理登录
const handleLogin = () => {
  router.push('/auth/login')
}
</script>

<style scoped>
.guest-recommendations-section {
  padding: 80px 0;
  background: white;
}

.recommendations-container {
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

/* 推荐卡片 */
.recommendations-grid {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr;
  gap: 32px;
  margin-bottom: 80px;
}

.recommendation-card {
  background: white;
  border-radius: 16px;
  padding: 32px;
  text-align: center;
  transition: all 0.3s ease;
  border: 2px solid #f7fafc;
  position: relative;
}

.recommendation-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  border-color: #e2e8f0;
}

.featured-card {
  background: linear-gradient(135deg, #f0fff4 0%, #f7fafc 100%);
  border-color: #67c23a;
  border-width: 2px;
}

.card-badge {
  position: absolute;
  top: 16px;
  right: 16px;
}

.card-icon {
  margin-bottom: 24px;
}

.card-title {
  font-size: 1.4rem;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 16px;
}

.card-description {
  color: #718096;
  line-height: 1.6;
  margin-bottom: 24px;
}

.card-features {
  margin-bottom: 32px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #4a5568;
  font-size: 14px;
  margin-bottom: 8px;
}

.feature-item .el-icon {
  color: #67c23a;
  font-size: 16px;
}

.try-button {
  width: 100%;
  border-radius: 12px;
  height: 44px;
}

/* 成功案例 */
.success-stories {
  margin-bottom: 80px;
}

.stories-title {
  font-size: 1.8rem;
  font-weight: 600;
  color: #2d3748;
  text-align: center;
  margin-bottom: 40px;
}

.stories-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
}

.story-card {
  background: #f8fafc;
  border-radius: 12px;
  padding: 24px;
  transition: all 0.3s ease;
}

.story-card:hover {
  background: white;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.story-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 8px;
}

.story-excerpt {
  color: #718096;
  font-size: 14px;
  line-height: 1.5;
  margin-bottom: 16px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.story-meta {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
  font-size: 12px;
}

.story-genre {
  background: #667eea;
  color: white;
  padding: 2px 8px;
  border-radius: 4px;
}

.story-words {
  color: #a0aec0;
}

.story-author {
  display: flex;
  align-items: center;
  gap: 8px;
}

.author-name {
  font-size: 14px;
  color: #4a5568;
  font-weight: 500;
}

/* 注册引导 */
.registration-cta {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 20px;
  padding: 60px 40px;
  color: white;
  text-align: center;
  margin-bottom: 80px;
}

.cta-title {
  font-size: 1.8rem;
  font-weight: 600;
  margin-bottom: 16px;
}

.cta-description {
  font-size: 1.1rem;
  opacity: 0.9;
  margin-bottom: 40px;
  line-height: 1.6;
}

.premium-features {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 40px;
  margin-bottom: 40px;
  text-align: left;
}

.feature-group h4 {
  font-size: 1.1rem;
  margin-bottom: 16px;
  color: #ffd700;
}

.feature-group ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.feature-group li {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  font-size: 14px;
}

.feature-group .el-icon {
  color: #67c23a;
}

.cta-buttons {
  display: flex;
  gap: 16px;
  justify-content: center;
  flex-wrap: wrap;
}

.register-button,
.login-button {
  min-width: 140px;
  height: 48px;
  border-radius: 12px;
  font-size: 16px;
}

.login-button {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
}

.login-button:hover {
  background: rgba(255, 255, 255, 0.2);
}

/* FAQ部分 */
.faq-section {
  margin-top: 40px;
}

.faq-title {
  font-size: 1.8rem;
  font-weight: 600;
  color: #2d3748;
  text-align: center;
  margin-bottom: 40px;
}

.faq-collapse {
  max-width: 800px;
  margin: 0 auto;
}

.faq-answer {
  color: #718096;
  line-height: 1.6;
  margin: 0;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .recommendations-grid {
    grid-template-columns: 1fr;
    gap: 24px;
  }
  
  .premium-features {
    grid-template-columns: 1fr;
    gap: 24px;
  }
}

@media (max-width: 768px) {
  .guest-recommendations-section {
    padding: 60px 0;
  }
  
  .recommendations-container {
    padding: 0 16px;
  }
  
  .section-title {
    font-size: 2rem;
  }
  
  .recommendation-card {
    padding: 24px;
  }
  
  .registration-cta {
    padding: 40px 24px;
  }
  
  .cta-buttons {
    flex-direction: column;
    align-items: center;
  }
  
  .register-button,
  .login-button {
    width: 100%;
    max-width: 280px;
  }
}
</style>