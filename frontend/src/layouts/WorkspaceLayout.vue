<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import {
  Setting,
  User,
  Notebook,
  Document,
  View as IconView, // Renamed to avoid conflict with ElIcon View
  Clock,
  DataAnalysis, // Example for AI Configs, replace if a better one is found
} from '@element-plus/icons-vue';

const route = useRoute();

const novelId = computed(() => {
  const idParam = route.params.novelId;
  return Array.isArray(idParam) ? idParam[0] : idParam;
});

// Placeholder for novel information - fetch this in a real app
const novelInfo = ref({
  name: '',
  author: 'AI助手 & 用户',
  type: '未知类型',
  synopsis: '一部等待被书写的传奇故事...',
});

onMounted(() => {
  // Simulate fetching novel info based on novelId
  if (novelId.value) {
    novelInfo.value.name = `我的小说 #${novelId.value}`;
    // In a real app: fetchNovelDetails(novelId.value).then(data => novelInfo.value = data);
  }
});

interface NavItem {
  name: string;
  routeName: string;
  icon: any; // Using 'any' for Element Plus icons
}

const workspaceNavItems = ref<NavItem[]>([
  { name: '世界观', routeName: 'WorkspaceWorldview', icon: IconView },
  { name: '角色', routeName: 'WorkspaceCharacters', icon: User },
  { name: '大纲', routeName: 'WorkspaceOutline', icon: Notebook },
  { name: '章节', routeName: 'WorkspaceChapters', icon: Document },
  { name: '时间轴', routeName: 'WorkspaceTimeline', icon: Clock }, // Route to be created
  { name: 'AI配置', routeName: 'WorkspaceAIConfigs', icon: Setting }, // Route might be 'ai-configs' from existing router
]);

</script>

<template>
  <el-container class="workspace-layout">
    <el-header class="workspace-header">
      <div class="novel-info-banner">
        <h1>{{ novelInfo.name }}</h1>
        <div class="novel-meta">
          <span><strong>作者:</strong> {{ novelInfo.author }}</span>
          <span><strong>类型:</strong> {{ novelInfo.type }}</span>
        </div>
        <p class="novel-synopsis">{{ novelInfo.synopsis }}</p>
      </div>
    </el-header>

    <el-container class="workspace-body">
      <el-aside width="220px" class="workspace-sidebar">
        <el-menu
          :default-active="route.name?.toString()"
          class="workspace-nav-menu"
          router
        >
          <el-menu-item
            v-for="item in workspaceNavItems"
            :key="item.routeName"
            :index="item.routeName"
            :route="{ name: item.routeName, params: { novelId: novelId } }"
          >
            <el-icon><component :is="item.icon" /></el-icon>
            <span>{{ item.name }}</span>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <el-main class="workspace-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<style scoped>
.workspace-layout {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.workspace-header {
  background-color: #2c3e50; /* Dark blue-grey */
  color: white;
  padding: 20px;
  line-height: normal; /* Override default ElHeader line-height if necessary */
  height: auto; /* Adjust height to content */
}

.novel-info-banner h1 {
  margin: 0 0 10px 0;
  font-size: 2em;
  font-weight: 600;
}

.novel-meta {
  display: flex;
  gap: 20px;
  margin-bottom: 10px;
  font-size: 0.9em;
  opacity: 0.9;
}

.novel-meta span strong {
  font-weight: 600;
}

.novel-synopsis {
  font-size: 0.95em;
  opacity: 0.8;
  margin: 0;
  line-height: 1.5;
}

.workspace-body {
  flex-grow: 1;
  overflow: hidden; /* Prevent double scrollbars if content is too long */
}

.workspace-sidebar {
  background-color: #ffffff;
  border-right: 1px solid #e0e0e0;
  padding-top:15px;
}

.workspace-nav-menu {
  border-right: none; /* El-menu might add its own border */
}

.workspace-nav-menu .el-menu-item {
  font-size: 1em;
}
.workspace-nav-menu .el-menu-item.is-active {
  background-color: #ecf5ff; /* Element Plus default active color */
  color: #409eff;
  font-weight: bold;
}
.workspace-nav-menu .el-menu-item:hover {
    background-color: #f5f7fa;
}

.workspace-content {
  padding: 20px;
  background-color: #f4f7f6; /* Light background for content area */
  overflow-y: auto; /* Allow scrolling for content area only */
}
</style>
