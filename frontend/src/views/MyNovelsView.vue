<script setup lang="ts">
import { ref } from 'vue';
import { NovelCard } from '@/components/novels'; // Import using the index.ts

// Placeholder data for novels
const novels = ref([
  {
    id: '1',
    name: '我的第一本小说',
    cover_image_url: 'https://via.placeholder.com/150x220.png?text=小说封面1',
    created_at: '2023-01-15',
  },
  {
    id: '2',
    name: 'AI创世纪',
    cover_image_url: 'https://via.placeholder.com/150x220.png?text=小说封面2',
    created_at: '2023-02-20',
  },
  {
    id: '3',
    name: '未来代码',
    cover_image_url: 'https://via.placeholder.com/150x220.png?text=小说封面3',
    created_at: '2023-03-10',
  },
]);
</script>

<template>
  <div class="my-novels-view">
    <h1>我的小说</h1>
    <div class="novels-grid">
      <NovelCard v-for="novel in novels" :key="novel.id" :novel="novel" />
    </div>
  </div>
</template>

<style scoped>
.my-novels-view {
  padding: 20px;
  font-family: 'Arial', sans-serif;
  background-color: #f4f7f6; /* Light background for the view */
  min-height: 100vh;
}

.my-novels-view h1 {
  text-align: center;
  margin-bottom: 40px; /* Increased margin */
  color: #2c3e50; /* Darker, more modern color */
  font-size: 2.5em; /* Larger title */
  font-weight: 600;
}

.novels-grid {
  display: grid;
  /* Adjusted minmax for potentially larger cards or more spacing */
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 30px; /* Increased gap for better separation */
  max-width: 1200px; /* Max width for the grid */
  margin: 0 auto; /* Center the grid */
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .my-novels-view h1 {
    font-size: 2em;
  }
  .novels-grid {
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 20px;
  }
}

@media (max-width: 480px) {
  .novels-grid {
    grid-template-columns: 1fr; /* Single column on very small screens */
    gap: 15px;
  }
}
</style>
