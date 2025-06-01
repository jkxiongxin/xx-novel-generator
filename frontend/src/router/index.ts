import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/about',
      name: 'about',
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../views/AboutView.vue'),
    },
    {
      path: '/brain-generator',
      name: 'brain-generator',
      component: () => import('../views/BrainGenerator.vue'),
      meta: {
        title: '脑洞生成器'
      }
    },
    {
      path: '/novel-create',
      name: 'novel-create',
      component: () => import('../views/NovelCreate.vue'),
      meta: {
        title: '小说创作'
      }
    },
    {
      path: '/workspace/:novelId',
      name: 'workspace',
      redirect: to => `/workspace/${to.params.novelId}/characters`,
      meta: {
        title: '创作工作空间'
      }
    },
    {
      path: '/workspace/:novelId/characters',
      name: 'workspace-characters',
      component: () => import('../views/workspace/Characters.vue'),
      meta: {
        title: '角色管理'
      }
    },
    {
      path: '/workspace/:novelId/outline',
      name: 'workspace-outline',
      component: () => import('../views/workspace/Outline.vue'),
      meta: {
        title: '大纲管理'
      }
    },
    {
      path: '/workspace/:novelId/worldview',
      name: 'workspace-worldview',
      component: () => import('../views/workspace/Worldview.vue'),
      meta: {
        title: '世界观管理'
      }
    },
  ],
})

export default router
