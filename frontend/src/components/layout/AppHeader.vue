<template>
  <el-header class="app-header">
    <div class="header-container">
      <!-- Logo和标题 -->
      <div class="header-left">
        <el-avatar 
          :size="40" 
          src="/favicon.ico" 
          class="logo"
          @click="navigateTo('/')"
        />
        <h1 class="title" @click="navigateTo('/')">
          AI智能小说创作平台
        </h1>
      </div>

      <!-- 导航菜单 -->
      <div class="header-center" v-if="!isMobile">
        <el-menu
          mode="horizontal"
          :ellipsis="false"
          background-color="transparent"
          text-color="#ffffff"
          active-text-color="#ffd04b"
          class="nav-menu"
          :default-active="activeMenu"
          @select="handleMenuSelect"
        >
          <el-menu-item index="/">首页</el-menu-item>
          <el-menu-item index="/novels" v-if="isLoggedIn">我的小说</el-menu-item>
          <el-menu-item index="/brain-generator">脑洞生成器</el-menu-item>
          <el-menu-item index="/tools/character-templates">角色模板</el-menu-item>
          <el-menu-item index="/admin/character-templates" v-if="isLoggedIn && userInfo?.is_admin">
            角色模板管理
          </el-menu-item>
        </el-menu>
      </div>

      <!-- 用户操作区域 -->
      <div class="header-right">
        <!-- 未登录状态 -->
        <div v-if="!isLoggedIn" class="auth-buttons">
          <el-button 
            text 
            @click="navigateTo('/auth/login')"
            class="login-btn"
          >
            登录
          </el-button>
          <el-button 
            type="primary" 
            @click="navigateTo('/auth/register')"
            class="register-btn"
          >
            注册
          </el-button>
        </div>

        <!-- 已登录状态 -->
        <div v-else class="user-menu">
          <!-- 快速创建按钮 -->
          <el-button 
            type="success" 
            :icon="EditPen"
            @click="quickCreate"
            class="quick-create-btn"
            v-if="!isMobile"
          >
            新建小说
          </el-button>

          <!-- 用户头像和菜单 -->
          <el-dropdown @command="handleUserCommand" trigger="click">
            <div class="user-avatar-wrapper">
              <el-avatar 
                :size="36" 
                :src="userInfo?.avatar_url"
                class="user-avatar"
              >
                {{ userInfo?.username?.charAt(0)?.toUpperCase() }}
              </el-avatar>
              <span class="username" v-if="!isMobile">{{ userInfo?.username }}</span>
              <el-icon class="dropdown-icon">
                <ArrowDown />
              </el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>
                  个人资料
                </el-dropdown-item>
                <el-dropdown-item command="workspace">
                  <el-icon><Folder /></el-icon>
                  我的工作台
                </el-dropdown-item>
                <el-dropdown-item command="settings">
                  <el-icon><Setting /></el-icon>
                  系统设置
                </el-dropdown-item>
                <el-dropdown-item divided command="logout">
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>

        <!-- 移动端菜单按钮 -->
        <el-button 
          v-if="isMobile"
          text
          :icon="Menu"
          @click="toggleMobileMenu"
          class="mobile-menu-btn"
        />
      </div>
    </div>

    <!-- 移动端抽屉菜单 -->
    <el-drawer
      v-model="showMobileMenu"
      title="菜单"
      direction="rtl"
      size="80%"
      class="mobile-drawer"
    >
      <div class="mobile-menu-content">
        <!-- 用户信息区域 -->
        <div class="mobile-user-section" v-if="isLoggedIn">
          <el-avatar 
            :size="60" 
            :src="userInfo?.avatar_url"
            class="mobile-user-avatar"
          >
            {{ userInfo?.username?.charAt(0)?.toUpperCase() }}
          </el-avatar>
          <div class="mobile-user-info">
            <div class="mobile-username">{{ userInfo?.username }}</div>
            <div class="mobile-user-email">{{ userInfo?.email }}</div>
          </div>
        </div>

        <!-- 菜单列表 -->
        <el-menu
          :default-active="activeMenu"
          @select="handleMobileMenuSelect"
          class="mobile-menu"
        >
          <el-menu-item index="/">
            <el-icon><House /></el-icon>
            <span>首页</span>
          </el-menu-item>
          <el-menu-item index="/novels" v-if="isLoggedIn">
            <el-icon><Document /></el-icon>
            <span>我的小说</span>
          </el-menu-item>
          <el-menu-item index="/brain-generator">
            <el-icon><MagicStick /></el-icon>
            <span>脑洞生成器</span>
          </el-menu-item>
          <el-menu-item index="/tools/character-templates">
            <el-icon><Avatar /></el-icon>
            <span>角色模板</span>
          </el-menu-item>
          <el-menu-item index="/admin/character-templates" v-if="isLoggedIn && userInfo?.is_admin">
            <el-icon><Setting /></el-icon>
            <span>角色模板管理</span>
          </el-menu-item>
        </el-menu>

        <!-- 移动端操作按钮 -->
        <div class="mobile-actions">
          <el-button 
            v-if="isLoggedIn"
            type="primary" 
            :icon="EditPen"
            @click="quickCreate"
            class="mobile-create-btn"
            block
          >
            新建小说
          </el-button>
          <template v-else>
            <el-button 
              @click="navigateTo('/auth/login')"
              block
              class="mobile-login-btn"
            >
              登录
            </el-button>
            <el-button 
              type="primary" 
              @click="navigateTo('/auth/register')"
              block
              class="mobile-register-btn"
            >
              注册
            </el-button>
          </template>
        </div>
      </div>
    </el-drawer>
  </el-header>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  EditPen,
  ArrowDown,
  User,
  Folder,
  Setting,
  SwitchButton,
  Menu,
  House,
  Document,
  MagicStick,
  Avatar
} from '@element-plus/icons-vue'
import { HomepageService, type UserInfo } from '@/api/homepage'

const router = useRouter()
const route = useRoute()

// 响应式数据
const isLoggedIn = ref(false)
const userInfo = ref<UserInfo | null>(null)
const showMobileMenu = ref(false)
const isMobile = ref(false)

// 计算属性
const activeMenu = computed(() => route.path)

// 加载用户信息
const loadUserInfo = async () => {
  if (!isLoggedIn.value) return
  
  try {
    const userData = await HomepageService.getUserInfo()
    userInfo.value = userData
    localStorage.setItem('user_info', JSON.stringify(userData))
  } catch (error) {
    console.error('加载用户信息失败:', error)
  }
}

// 监听token变化
watch(() => localStorage.getItem('access_token'), (newToken) => {
  if (newToken) {
    isLoggedIn.value = true
    loadUserInfo()
  } else {
    isLoggedIn.value = false
    userInfo.value = null
  }
}, { immediate: true })

// 检查是否为移动设备
const checkMobile = () => {
  isMobile.value = window.innerWidth < 768
}

// 页面跳转
const navigateTo = (path: string) => {
  router.push(path)
  showMobileMenu.value = false
}

// 菜单选择处理
const handleMenuSelect = (index: string) => {
  navigateTo(index)
}

// 移动端菜单选择处理
const handleMobileMenuSelect = (index: string) => {
  navigateTo(index)
}

// 切换移动端菜单显示
const toggleMobileMenu = () => {
  showMobileMenu.value = !showMobileMenu.value
}

// 快速创建小说
const quickCreate = () => {
  navigateTo('/novels/create')
  showMobileMenu.value = false
}

// 用户菜单命令处理
const handleUserCommand = (command: string) => {
  switch (command) {
    case 'profile':
      navigateTo('/profile')
      break
    case 'workspace':
      navigateTo('/workspace')
      break
    case 'settings':
      navigateTo('/settings')
      break
    case 'logout':
      handleLogout()
      break
  }
}

// 处理退出登录
const handleLogout = async () => {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    // 清除本地存储
    localStorage.removeItem('access_token')
    localStorage.removeItem('user_info')
    
    // 重置状态
    isLoggedIn.value = false
    userInfo.value = null
    
    ElMessage.success('已成功退出登录')
    
    // 跳转到首页
    navigateTo('/')
  } catch {
    // 用户取消操作
  }
}

// 检查登录状态
const checkAuthStatus = () => {
  const token = localStorage.getItem('access_token')
  const savedUserInfo = localStorage.getItem('user_info')
  
  if (token && savedUserInfo) {
    isLoggedIn.value = true
    userInfo.value = JSON.parse(savedUserInfo)
  }
}

// 窗口大小变化监听
const handleResize = () => {
  checkMobile()
  if (!isMobile.value) {
    showMobileMenu.value = false
  }
}

// 监听存储变化
const handleStorageChange = (event: StorageEvent) => {
  if (event.key === 'access_token') {
    if (event.newValue) {
      isLoggedIn.value = true
      loadUserInfo()
    } else {
      isLoggedIn.value = false
      userInfo.value = null
    }
  }
}

// 生命周期
onMounted(() => {
  checkMobile()
  checkAuthStatus()
  loadUserInfo()
  window.addEventListener('resize', handleResize)
  window.addEventListener('storage', handleStorageChange)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  window.removeEventListener('storage', handleStorageChange)
})
</script>

<style scoped>
.app-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-bottom: none;
  padding: 0;
  height: 64px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  width: 100%;
}

.header-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 20px;
  width: 100%;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo {
  cursor: pointer;
  transition: transform 0.2s ease;
}

.logo:hover {
  transform: scale(1.1);
}

.title {
  color: white;
  font-size: 20px;
  font-weight: 600;
  margin: 0;
  cursor: pointer;
  transition: opacity 0.2s ease;
}

.title:hover {
  opacity: 0.8;
}

.header-center {
  flex: 1;
  display: flex;
  justify-content: center;
}

.nav-menu {
  border-bottom: none !important;
  background: transparent !important;
}

.nav-menu .el-menu-item {
  border-bottom: none !important;
  color: rgba(255, 255, 255, 0.9) !important;
}

.nav-menu .el-menu-item:hover {
  background-color: rgba(255, 255, 255, 0.1) !important;
  color: white !important;
}

.nav-menu .el-menu-item.is-active {
  background-color: rgba(255, 255, 255, 0.2) !important;
  color: #ffd04b !important;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.auth-buttons {
  display: flex;
  align-items: center;
  gap: 12px;
}

.login-btn {
  color: rgba(255, 255, 255, 0.9) !important;
}

.login-btn:hover {
  color: white !important;
  background-color: rgba(255, 255, 255, 0.1) !important;
}

.register-btn {
  background-color: #ffd04b !important;
  border-color: #ffd04b !important;
  color: #333 !important;
}

.user-menu {
  display: flex;
  align-items: center;
  gap: 16px;
}

.quick-create-btn {
  background-color: #67c23a !important;
  border-color: #67c23a !important;
}

.user-avatar-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 20px;
  transition: background-color 0.2s ease;
}

.user-avatar-wrapper:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.username {
  color: white;
  font-size: 14px;
  font-weight: 500;
}

.dropdown-icon {
  color: rgba(255, 255, 255, 0.7);
  font-size: 12px;
}

.mobile-menu-btn {
  color: white !important;
  font-size: 20px;
}

/* 移动端抽屉样式 */
.mobile-drawer :deep(.el-drawer__header) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px;
  margin: 0;
}

.mobile-menu-content {
  padding: 20px;
}

.mobile-user-section {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px 0;
  border-bottom: 1px solid #eee;
  margin-bottom: 20px;
}

.mobile-user-info {
  flex: 1;
}

.mobile-username {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 4px;
}

.mobile-user-email {
  font-size: 14px;
  color: #666;
}

.mobile-menu {
  border-right: none;
  margin-bottom: 30px;
}

.mobile-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.mobile-create-btn,
.mobile-login-btn,
.mobile-register-btn {
  height: 44px;
  font-size: 16px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header-container {
    padding: 0 16px;
  }
  
  .title {
    font-size: 16px;
  }
  
  .header-center {
    display: none;
  }
  
  .auth-buttons {
    display: none;
  }
  
  .quick-create-btn {
    display: none;
  }
  
  .username {
    display: none;
  }
}

@media (max-width: 480px) {
  .title {
    display: none;
  }
}
</style>