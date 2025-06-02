<template>
  <el-footer class="app-footer">
    <div class="footer-container">
      <!-- 主要内容区域 -->
      <div class="footer-main">
        <!-- 品牌信息 -->
        <div class="brand-section">
          <div class="brand-logo">
            <el-avatar :size="40" src="/favicon.ico" />
            <h3 class="brand-name">AI智能小说创作平台</h3>
          </div>
          <p class="brand-description">
            让AI成为你的创作伙伴，从灵感火花到完整作品，我们陪伴你的每一步创作之旅。
          </p>
          <div class="social-links">
            <el-button 
              v-for="social in socialLinks" 
              :key="social.name"
              :icon="social.icon"
              circle
              size="small"
              @click="handleSocialClick(social)"
              class="social-btn"
            />
          </div>
        </div>
        
        <!-- 链接区域 -->
        <div class="links-section">
          <!-- 产品功能 -->
          <div class="link-group">
            <h4 class="group-title">产品功能</h4>
            <ul class="link-list">
              <li v-for="link in productLinks" :key="link.name">
                <router-link :to="link.path" class="footer-link">
                  {{ link.name }}
                </router-link>
              </li>
            </ul>
          </div>
          
          <!-- 帮助支持 -->
          <div class="link-group">
            <h4 class="group-title">帮助支持</h4>
            <ul class="link-list">
              <li v-for="link in helpLinks" :key="link.name">
                <a 
                  :href="link.path" 
                  class="footer-link"
                  :target="link.external ? '_blank' : '_self'"
                >
                  {{ link.name }}
                </a>
              </li>
            </ul>
          </div>
          
          <!-- 关于我们 -->
          <div class="link-group">
            <h4 class="group-title">关于我们</h4>
            <ul class="link-list">
              <li v-for="link in aboutLinks" :key="link.name">
                <a 
                  :href="link.path" 
                  class="footer-link"
                  :target="link.external ? '_blank' : '_self'"
                >
                  {{ link.name }}
                </a>
              </li>
            </ul>
          </div>
        </div>
      </div>
      
      <!-- 底部信息 -->
      <div class="footer-bottom">
        <div class="copyright">
          <span>© 2025 AI智能小说创作平台. 保留所有权利.</span>
        </div>
        <div class="bottom-links">
          <a href="/privacy" class="bottom-link">隐私政策</a>
          <span class="separator">|</span>
          <a href="/terms" class="bottom-link">服务条款</a>
          <span class="separator">|</span>
          <a href="/contact" class="bottom-link">联系我们</a>
        </div>
        <div class="system-info">
          <span>当前版本: v{{ version }}</span>
          <span class="separator">|</span>
          <span 
            class="status-indicator"
            :class="{ 'online': systemStatus.online }"
          >
            {{ systemStatus.online ? '服务正常' : '服务异常' }}
          </span>
        </div>
      </div>
    </div>
  </el-footer>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  ChatLineRound, 
  Position, 
  MessageBox,
  Service 
} from '@element-plus/icons-vue'
import { HomepageService } from '@/api/homepage'

// 响应式数据
const version = ref('1.0.0')
const systemStatus = ref({
  online: true
})

// 社交媒体链接
const socialLinks = [
  {
    name: 'QQ群',
    icon: ChatLineRound,
    url: '#',
    type: 'qq'
  },
  {
    name: '微信群',
    icon: MessageBox,
    url: '#',
    type: 'wechat'
  },
  {
    name: '技术支持',
    icon: Service,
    url: '#',
    type: 'support'
  },
  {
    name: '反馈建议',
    icon: Position,
    url: '#',
    type: 'feedback'
  }
]

// 产品功能链接
const productLinks = [
  { name: '脑洞生成器', path: '/tools/brain-generator' },
  { name: '小说创作', path: '/novels/create' },
  { name: '角色模板', path: '/tools/character-templates' },
  { name: '我的工作台', path: '/workspace' },
  { name: '作品管理', path: '/novels' }
]

// 帮助支持链接
const helpLinks = [
  { name: '使用指南', path: '/help/guide', external: false },
  { name: '常见问题', path: '/help/faq', external: false },
  { name: 'API文档', path: '/docs/api', external: true },
  { name: '视频教程', path: '/help/videos', external: false },
  { name: '在线客服', path: '#', external: false }
]

// 关于我们链接
const aboutLinks = [
  { name: '公司介绍', path: '/about', external: false },
  { name: '加入我们', path: '/careers', external: false },
  { name: '合作伙伴', path: '/partners', external: false },
  { name: '媒体报道', path: '/news', external: false },
  { name: '开源项目', path: 'https://github.com', external: true }
]

// 处理社交媒体点击
const handleSocialClick = (social: any) => {
  switch (social.type) {
    case 'qq':
      ElMessage.info('QQ群: 123456789')
      break
    case 'wechat':
      ElMessage.info('微信群二维码已复制到剪贴板')
      break
    case 'support':
      ElMessage.info('技术支持邮箱: support@aiwriter.com')
      break
    case 'feedback':
      ElMessage.info('意见反馈邮箱: feedback@aiwriter.com')
      break
    default:
      if (social.url && social.url !== '#') {
        window.open(social.url, '_blank')
      }
  }
}

// 检查系统状态
const checkSystemStatus = async () => {
  try {
    await HomepageService.getSystemStatus()
    systemStatus.value.online = true
  } catch (error) {
    systemStatus.value.online = false
  }
}

// 生命周期
onMounted(() => {
  checkSystemStatus()
  
  // 定期检查系统状态
  setInterval(checkSystemStatus, 5 * 60 * 1000) // 每5分钟检查一次
})
</script>

<style scoped>
.app-footer {
  background: #2d3748;
  color: #e2e8f0;
  padding: 60px 0 20px;
  margin-top: auto;
}

.footer-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 20px;
  width: 100%;
}

.footer-main {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 60px;
  margin-bottom: 40px;
}

/* 品牌区域 */
.brand-section {
  max-width: 400px;
}

.brand-logo {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.brand-name {
  color: white;
  font-size: 1.2rem;
  font-weight: 600;
  margin: 0;
}

.brand-description {
  color: #a0aec0;
  line-height: 1.6;
  margin-bottom: 24px;
}

.social-links {
  display: flex;
  gap: 12px;
}

.social-btn {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #e2e8f0;
  transition: all 0.3s ease;
}

.social-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
}

/* 链接区域 */
.links-section {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 40px;
}

.link-group {
  /* 链接组样式 */
}

.group-title {
  color: white;
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0 0 20px 0;
  padding-bottom: 8px;
  border-bottom: 2px solid #4a5568;
}

.link-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.link-list li {
  margin-bottom: 12px;
}

.footer-link {
  color: #a0aec0;
  text-decoration: none;
  transition: color 0.3s ease;
  font-size: 14px;
}

.footer-link:hover {
  color: #667eea;
}

/* 底部信息 */
.footer-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 20px;
  border-top: 1px solid #4a5568;
  flex-wrap: wrap;
  gap: 16px;
}

.copyright {
  color: #718096;
  font-size: 14px;
}

.bottom-links {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.bottom-link {
  color: #a0aec0;
  text-decoration: none;
  transition: color 0.3s ease;
}

.bottom-link:hover {
  color: #667eea;
}

.separator {
  color: #4a5568;
}

.system-info {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #718096;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 4px;
}

.status-indicator::before {
  content: '';
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #f56c6c;
}

.status-indicator.online::before {
  background: #67c23a;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .footer-main {
    grid-template-columns: 1fr;
    gap: 40px;
  }
  
  .links-section {
    grid-template-columns: repeat(2, 1fr);
    gap: 30px;
  }
}

@media (max-width: 768px) {
  .app-footer {
    padding: 40px 0 20px;
  }
  
  .footer-container {
    padding: 0 16px;
  }
  
  .footer-main {
    gap: 30px;
  }
  
  .links-section {
    grid-template-columns: 1fr;
    gap: 24px;
  }
  
  .footer-bottom {
    flex-direction: column;
    text-align: center;
    gap: 12px;
  }
  
  .bottom-links {
    order: 2;
  }
  
  .system-info {
    order: 3;
  }
}

@media (max-width: 480px) {
  .brand-logo {
    flex-direction: column;
    text-align: center;
    gap: 8px;
  }
  
  .social-links {
    justify-content: center;
  }
  
  .bottom-links {
    flex-direction: column;
    gap: 8px;
  }
  
  .separator {
    display: none;
  }
}

/* 链接hover效果 */
.footer-link {
  position: relative;
}

.footer-link::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 0;
  height: 1px;
  background: #667eea;
  transition: width 0.3s ease;
}

.footer-link:hover::after {
  width: 100%;
}

/* 动画效果 */
.social-btn {
  animation: fadeInUp 0.6s ease-out;
}

.link-group {
  animation: fadeInUp 0.6s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 第一个链接组延迟动画 */
.link-group:nth-child(1) {
  animation-delay: 0.1s;
}

.link-group:nth-child(2) {
  animation-delay: 0.2s;
}

.link-group:nth-child(3) {
  animation-delay: 0.3s;
}
</style>