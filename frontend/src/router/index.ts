import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import MyNovelsView from '../views/MyNovelsView.vue'
import NovelDetailView from '../views/NovelDetailView.vue'
import CharacterTemplatesView from '../views/CharacterTemplatesView.vue'
import WorkspaceLayout from '../layouts/WorkspaceLayout.vue'
import WorkspaceTimelineView from '../views/workspace/TimelineView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/my-novels',
      name: 'MyNovels',
      component: MyNovelsView
    },
    {
      path: '/novel/:id/details', // Using :id as a route parameter
      name: 'NovelDetail',
      component: NovelDetailView,
      props: true // This allows the :id parameter to be passed as a prop to the component
    },
    {
      path: '/character-templates',
      name: 'CharacterTemplates',
      component: CharacterTemplatesView
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
      component: WorkspaceLayout,
      name: 'workspace', // Name for the layout route itself
      // Default child to redirect to. Let's use characters as it was before.
      redirect: to => ({ name: 'WorkspaceCharacters', params: { novelId: to.params.novelId } }),
      meta: { title: '创作工作空间' },
      children: [
        {
          path: 'worldview', // resolves to /workspace/:novelId/worldview
          name: 'WorkspaceWorldview',
          component: () => import('../views/workspace/Worldview.vue'),
          meta: { title: '世界观管理' }
        },
        {
          path: 'characters',
          name: 'WorkspaceCharacters',
          component: () => import('../views/workspace/Characters.vue'),
          meta: { title: '角色管理' }
        },
        {
          path: 'outline',
          name: 'WorkspaceOutline',
          component: () => import('../views/workspace/Outline.vue'),
          meta: { title: '大纲管理' }
        },
        {
          path: 'chapters',
          name: 'WorkspaceChapters',
          component: () => import('../views/workspace/Chapters.vue'),
          meta: { title: '章节管理' }
        },
        {
          path: 'timeline',
          name: 'WorkspaceTimeline',
          component: WorkspaceTimelineView,
          meta: { title: '时间轴' }
        },
        {
          // Assuming ai-configs is part of a specific novel's workspace
          path: 'ai-configs',
          name: 'WorkspaceAIConfigs', // Consistent naming
          component: () => import('../views/workspace/AIConfigs.vue'),
          meta: { title: 'AI配置管理' }
        }
      ]
    },
    // The old individual workspace routes are now children of the above layout route.
    // The old /ai-configs top-level route is also moved as a child.
  ],
})

export default router
