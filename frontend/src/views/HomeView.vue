<template>
  <div class="home-view">
    <!-- 英雄区域 -->
    <HeroSection />
    
    <!-- 功能特性区域 -->
    <FeatureCards />
    
    <!-- 快速操作区域 -->
    <QuickActions />
    
    <!-- 最近作品区域 (仅登录用户显示) -->
    <RecentNovels v-if="currentLoginStatus" />
    
    <!-- 客座用户推荐区域 -->
    <GuestRecommendations v-else />
    
    <!-- 系统通知 -->
    <SystemNotifications />
  </div>
</template>

<script setup lang="ts">
import { computed, inject, onMounted, ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import HeroSection from '@/components/home/HeroSection.vue'
import FeatureCards from '@/components/home/FeatureCards.vue'
import QuickActions from '@/components/home/QuickActions.vue'
import RecentNovels from '@/components/home/RecentNovels.vue'
import GuestRecommendations from '@/components/home/GuestRecommendations.vue'
import SystemNotifications from '@/components/home/SystemNotifications.vue'

const router = useRouter()
const route = useRoute()

// 从父组件（App.vue）注入数据
const systemStatus = inject('systemStatus')
const userInfo = inject('userInfo')
const isLoggedIn = inject('isLoggedIn')

// 本地响应式状态，用于实时更新
const localLoginStatus = ref(!!localStorage.getItem('access_token'))

// 监听localStorage变化
watch(() => localStorage.getItem('access_token'), (newToken) => {
  localLoginStatus.value = !!newToken
}, { immediate: true })

// 使用本地状态或注入状态
const currentLoginStatus = computed(() => localLoginStatus.value)

// 处理路由变化
const handleRouteChange = () => {
  // 如果从其他页面返回首页，清除refresh参数
  if (route.query.refresh === 'true') {
    router.replace({ path: '/', query: {} })
  }
}

// 生命周期钩子
onMounted(() => {
  // 监听路由变化
  handleRouteChange()
  
  // 设置页面标题
  document.title = 'AI智能小说创作平台 - 让AI成为你的创作伙伴'
  
  // 设置页面描述
  const metaDescription = document.querySelector('meta[name="description"]')
  if (metaDescription) {
    metaDescription.setAttribute('content', '专业的AI智能小说创作平台，提供脑洞生成器、智能写作助手、角色塑造工具等全方位创作支持，让每个人都能成为优秀的小说家。')
  }
})
</script>

<style scoped>
.home-view {
  display: flex;
  flex-direction: column;
  width: 100%;
}

/* 页面加载动画 */
.home-view {
  animation: fadeIn 0.6s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

/* 无障碍访问支持 */
@media (prefers-reduced-motion: reduce) {
  .home-view,
  .home-view * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .home-view {
    /* 移动端特定样式 */
  }
}
</style>
