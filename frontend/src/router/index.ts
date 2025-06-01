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
  ],
})

export default router
