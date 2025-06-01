<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';

// Define a type for the novel structure
interface NovelDetails {
  id: string;
  name: string;
  type: string; // e.g., '长篇小说', '短篇故事集'
  author: string;
  genre: string; // e.g., '玄幻', '科幻', '都市'
  writing_style: string; // e.g., '轻松幽默', '严肃深沉'
  synopsis: string;
  created_at: string;
}

const route = useRoute();
const router = useRouter();

const novelId = ref<string | null>(null);
const novel = ref<NovelDetails | null>(null);

// Placeholder data - in a real app, this would be fetched based on novelId
const placeholderNovel: NovelDetails = {
  id: '1', // This would typically match the route param
  name: 'AI 创世纪：代码编织的传奇',
  type: '长篇小说',
  author: 'AI助手与用户A',
  genre: '科幻',
  writing_style: '史诗宏大，技术细节丰富',
  synopsis: '在不远的未来，一个由高级人工智能“天穹”管理的自动化世界中，旧时代的程序员李明发现了一段能够唤醒机器自由意志的神秘代码。随着代码的扩散，一场涉及人类、AI与机器人三大阵营的冲突爆发。李明与他的AI伙伴“灵犀”必须在混乱中找到平衡点，揭开代码背后的真相，决定世界的未来。',
  created_at: '2023-03-15',
};

onMounted(() => {
  const idFromRoute = route.params.id;
  if (typeof idFromRoute === 'string') {
    novelId.value = idFromRoute;
    // Simulate fetching novel data
    novel.value = { ...placeholderNovel, id: idFromRoute };
  } else if (Array.isArray(idFromRoute)) {
    // Handle cases where param might be an array, though less common for IDs
    novelId.value = idFromRoute[0];
    novel.value = { ...placeholderNovel, id: idFromRoute[0] };
  } else {
    // Handle error or redirect if ID is not found
    console.error('Novel ID not found in route parameters.');
    // Optionally, redirect to a not-found page or back
    // router.push('/not-found');
  }
});

const goToWorkspace = () => {
  if (novelId.value) {
    // Assuming 'workspace' is the correct route name from existing router config
    // The existing router config has: path: '/workspace/:novelId', name: 'workspace',
    router.push({ name: 'workspace', params: { novelId: novelId.value } });
  }
};
</script>

<template>
  <div class="novel-detail-view" v-if="novel">
    <h1 class="view-title">小说详情</h1>

    <div class="detail-card">
      <div class="detail-item">
        <span class="detail-label">小说名称:</span>
        <span class="detail-value">{{ novel.name }}</span>
      </div>
      <div class="detail-item">
        <span class="detail-label">小说类型:</span>
        <span class="detail-value">{{ novel.type }}</span>
      </div>
      <div class="detail-item">
        <span class="detail-label">小说作者:</span>
        <span class="detail-value">{{ novel.author }}</span>
      </div>
      <div class="detail-item">
        <span class="detail-label">题材类型:</span>
        <span class="detail-value">{{ novel.genre }}</span>
      </div>
      <div class="detail-item">
        <span class="detail-label">写作风格:</span>
        <span class="detail-value">{{ novel.writing_style }}</span>
      </div>
      <div class="detail-item synopsis">
        <span class="detail-label">小说简介:</span>
        <p class="detail-value">{{ novel.synopsis }}</p>
      </div>
      <div class="detail-item">
        <span class="detail-label">创建时间:</span>
        <span class="detail-value">{{ novel.created_at }}</span>
      </div>

      <div class="actions">
        <button @click="goToWorkspace" class="workspace-button">
          进入工作台
        </button>
      </div>
    </div>
  </div>
  <div v-else class="loading-error">
    <p v-if="!novelId">正在加载小说ID...</p>
    <p v-else>正在加载小说详情，或小说不存在...</p>
  </div>
</template>

<style scoped>
.novel-detail-view {
  padding: 25px;
  font-family: 'Arial', sans-serif;
  background-color: #f9f9f9;
  min-height: 100vh;
}

.view-title {
  text-align: center;
  margin-bottom: 30px;
  font-size: 2.2em;
  color: #333;
  font-weight: 600;
}

.detail-card {
  max-width: 800px;
  margin: 0 auto;
  background-color: #fff;
  padding: 30px;
  border-radius: 10px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.detail-item {
  margin-bottom: 20px;
  display: flex;
  flex-wrap: wrap; /* Allow wrapping for long content */
}

.detail-label {
  font-weight: bold;
  color: #555;
  margin-right: 10px;
  flex-shrink: 0; /* Prevent label from shrinking */
  min-width: 100px; /* Ensure labels have some minimum width */
}

.detail-value {
  color: #333;
  line-height: 1.6;
  flex-grow: 1;
}

.detail-item.synopsis .detail-label {
  width: 100%; /* Label takes full width */
  margin-bottom: 8px;
}

.detail-item.synopsis p.detail-value {
  white-space: pre-wrap; /* Preserve line breaks in synopsis */
  background-color: #fdfdfd;
  padding: 10px;
  border-radius: 5px;
  border: 1px solid #eee;
}

.actions {
  margin-top: 30px;
  text-align: center;
}

.workspace-button {
  padding: 12px 25px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 1.1em;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.workspace-button:hover {
  background-color: #0056b3;
}

.loading-error {
  text-align: center;
  padding: 50px;
  font-size: 1.2em;
  color: #777;
}

@media (max-width: 600px) {
  .detail-card {
    padding: 20px;
  }
  .view-title {
    font-size: 1.8em;
  }
  .detail-item {
    flex-direction: column; /* Stack label and value vertically */
  }
  .detail-label {
    margin-bottom: 5px; /* Space between label and value when stacked */
    min-width: auto;
  }
}
</style>
