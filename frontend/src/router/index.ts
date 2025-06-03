import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: { title: 'AI写作助手 - 首页' }
    },
    {
      path: '/about',
      name: 'about',
      component: () => import('../views/AboutView.vue'),
      meta: { title: '关于我们' }
    },
    {
      path: '/brain-generator',
      name: 'brain-generator',
      component: () => import('../views/BrainGenerator.vue'),
      meta: { title: '脑洞生成器' }
    },
    {
      path: '/novels',
      name: 'novels',
      component: () => import('../views/NovelListView.vue'),
      meta: { title: '我的小说', requiresAuth: true }
    },
    {
      path: '/novels/create',
      name: 'novel-create',
      component: () => import('../views/NovelCreate.vue'),
      meta: { title: '创建小说', requiresAuth: true }
    },
    {
      path: '/novels/:novelId',
      name: 'novel-detail',
      component: () => import('../views/NovelDetailView.vue'),
      meta: { title: '小说详情', requiresAuth: true }
    },
    // 认证相关路由
    {
      path: '/auth/login',
      name: 'login',
      component: () => import('../views/auth/LoginView.vue'),
      meta: { title: '登录' }
    },
    {
      path: '/auth/register',
      name: 'register',
      component: () => import('../views/auth/RegisterView.vue'),
      meta: { title: '注册' }
    },
    {
      path: '/auth/forgot-password',
      name: 'forgot-password',
      component: () => import('../views/auth/ForgotPasswordView.vue'),
      meta: { title: '找回密码' }
    },
    {
      path: '/auth/reset-password',
      name: 'reset-password',
      component: () => import('../views/auth/ResetPasswordView.vue'),
      meta: { title: '重置密码' }
    },
    {
      path: '/auth/email-verification',
      name: 'email-verification',
      component: () => import('../views/auth/EmailVerificationView.vue'),
      meta: { title: '邮箱验证' }
    },
    // 工作台路由
    {
      path: '/workspace/:novelId',
      name: 'workspace',
      redirect: to => `/workspace/${to.params.novelId}/chapters`,
      meta: { requiresAuth: true }
    },
    {
      path: '/workspace/:novelId/chapters',
      name: 'workspace-chapters',
      component: () => import('../views/workspace/Chapters.vue'),
      meta: { title: '章节管理', requiresAuth: true }
    },
    {
      path: '/workspace/:novelId/outline',
      name: 'workspace-outline',
      component: () => import('../views/workspace/Outline.vue'),
      meta: { title: '大纲管理', requiresAuth: true }
    },
    {
      path: '/workspace/:novelId/characters',
      name: 'workspace-characters',
      component: () => import('../views/workspace/Characters.vue'),
      meta: { title: '角色管理', requiresAuth: true }
    },
    {
      path: '/workspace/:novelId/worldview',
      name: 'workspace-worldview',
      component: () => import('../views/workspace/Worldview.vue'),
      meta: { title: '世界观管理', requiresAuth: true }
    },
    {
      path: '/workspace/:novelId/ai-configs',
      name: 'workspace-ai-configs',
      component: () => import('../views/workspace/AIConfigs.vue'),
      meta: { title: 'AI配置', requiresAuth: true }
    },
    {
      path: '/ai-config-management',
      name: 'ai-config-management',
      component: () => import('../views/AIConfigManagement.vue'),
      meta: { title: 'AI模型配置管理', requiresAuth: true }
    }
  ]
})

// 路由守卫 - 检查认证状态
router.beforeEach((to, from, next) => {
  // 设置页面标题
  if (to.meta.title) {
    document.title = to.meta.title as string
  }

  // 检查是否需要认证
  if (to.meta.requiresAuth) {
    const token = localStorage.getItem('access_token')
    if (!token) {
      // 重定向到登录页面，并保存原始路径
      next({
        name: 'login',
        query: { redirect: to.fullPath }
      })
      return
    }
  }

  next()
})

export default router
