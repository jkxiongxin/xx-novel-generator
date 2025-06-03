<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, provide } from 'vue'
import { RouterView, useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import AppHeader from '@/components/layout/AppHeader.vue'
import AppFooter from '@/components/layout/AppFooter.vue'
import { HomepageService } from '@/api/homepage'

const router = useRouter()
const route = useRoute()

// 响应式数据
const isLoading = ref(true)
const systemStatus = ref<any>(null)
const userInfo = ref<any>(null)

// 计算属性
const isLoggedIn = computed(() => {
  return !!localStorage.getItem('access_token')
})

// 初始化应用数据
const initializeAppData = async () => {
  try {
    isLoading.value = true
    
    // 并行加载系统状态和用户信息
    const promises = [
      loadSystemStatus()
    ]
    
    if (isLoggedIn.value) {
      promises.push(loadUserInfo())
    }
    
    await Promise.allSettled(promises)
    
  } catch (error) {
    console.error('初始化应用数据失败:', error)
  } finally {
    isLoading.value = false
  }
}

// 加载系统状态
const loadSystemStatus = async () => {
  try {
    const status = await HomepageService.getSystemStatus()
    systemStatus.value = status
    
    // 检查系统状态并显示相应提示
    checkSystemStatus(status)
    
  } catch (error) {
    console.error('加载系统状态失败:', error)
  }
}

// 加载用户信息
const loadUserInfo = async () => {
  try {
    const info = await HomepageService.getUserInfo()
    userInfo.value = info
    
    // 更新本地存储的用户信息
    localStorage.setItem('user_info', JSON.stringify(info))
    
  } catch (error: any) {
    console.error('加载用户信息失败:', error)
    
    // 如果是认证错误，清除本地状态
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('user_info')
    }
  }
}

// 检查系统状态
const checkSystemStatus = (status: any) => {
  if (status.ai_service === 'unavailable') {
    ElMessage.warning('AI服务暂时不可用，部分功能可能受限')
  } else if (status.ai_service === 'limited') {
    ElMessage.info('AI服务当前处于限制模式')
  }
  
  if (status.database !== 'connected') {
    ElMessage.error('数据库连接异常，请刷新页面重试')
  }
}

// 页面可见性变化处理
const handleVisibilityChange = () => {
  if (!document.hidden && isLoggedIn.value) {
    // 页面重新可见时，刷新用户数据
    loadUserInfo()
  }
}

// 监听登录状态变化
const handleStorageChange = (event: StorageEvent) => {
  if (event.key === 'access_token') {
    if (event.newValue) {
      // 用户登录
      loadUserInfo()
    } else {
      // 用户登出
      userInfo.value = null
    }
  }
}

// 手动刷新用户信息的方法，用于登录后立即更新
const refreshUserInfo = async () => {
  if (isLoggedIn.value) {
    await loadUserInfo()
  }
}

// 暴露给全局使用的方法
window.refreshUserInfo = refreshUserInfo

// 生命周期钩子
onMounted(() => {
  // 初始化应用数据
  initializeAppData()
  
  // 添加事件监听器
  document.addEventListener('visibilitychange', handleVisibilityChange)
  window.addEventListener('storage', handleStorageChange)
})

onUnmounted(() => {
  // 清理事件监听器
  document.removeEventListener('visibilitychange', handleVisibilityChange)
  window.removeEventListener('storage', handleStorageChange)
})

// 提供给子组件的数据
provide('systemStatus', systemStatus)
provide('userInfo', userInfo)
provide('isLoggedIn', isLoggedIn)
</script>

<template>
  <div id="app" class="app-layout">
    <!-- 全局导航 -->
    <AppHeader />
    
    <!-- 主要内容区域 -->
    <main class="app-main">
      <RouterView />
    </main>
    
    <!-- 页面底部 -->
    <AppFooter />
    
    <!-- 全局返回顶部按钮 -->
    <el-backtop :right="100" :bottom="100" />
  </div>
</template>

<style>
/* 全局样式重置 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  height: 100%;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

#app {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #ffffff;
}

.app-main {
  flex: 1;
  display: flex;
  flex-direction: column;
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 全局返回顶部按钮样式 */
:deep(.el-backtop) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
  transition: all 0.3s ease;
}

:deep(.el-backtop:hover) {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.6);
}

/* 页面加载动画 */
.app-layout {
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
  .app-layout,
  .app-layout * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}

/* 高对比度模式支持 */
@media (prefers-contrast: high) {
  .app-layout {
    filter: contrast(1.2);
  }
}

/* 深色模式支持 */
@media (prefers-color-scheme: dark) {
  .app-layout {
    background: #1a202c;
    color: #e2e8f0;
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .app-layout {
    /* 移动端特定样式 */
  }
}
</style>
