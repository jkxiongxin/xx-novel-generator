<script setup lang="ts">
import type { PropType } from 'vue';

interface Novel {
  id: string;
  name: string;
  cover_image_url: string;
  created_at: string;
}

defineProps({
  novel: {
    type: Object as PropType<Novel>,
    required: true,
  },
});
</script>

<template>
  <div class="novel-card">
    <div class="novel-cover">
      <img :src="novel.cover_image_url" :alt="novel.name + ' Cover'" />
    </div>
    <div class="novel-info">
      <h3>{{ novel.name }}</h3>
      <p class="creation-date">创建于: {{ novel.created_at }}</p>
    </div>
    <div class="novel-actions">
      <router-link :to="{ name: 'NovelDetail', params: { id: novel.id } }" class="action-button details-button">
        查看详情
      </router-link>
      <div class="export-buttons">
        <button class="action-button export-button">导出TXT</button>
        <button class="action-button export-button">导出DOCX</button>
        <button class="action-button export-button">导出PDF</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.novel-card {
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  padding: 20px;
  background-color: #ffffff;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.novel-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.12);
}

.novel-cover img {
  width: 150px;
  height: 220px;
  object-fit: cover;
  border-radius: 8px;
  margin-bottom: 15px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.novel-info h3 {
  margin: 0 0 8px 0;
  font-size: 1.4em;
  color: #333;
  font-weight: 600;
}

.novel-info .creation-date {
  font-size: 0.9em;
  color: #777;
  margin-bottom: 15px;
}

.novel-actions {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 10px; /* Consistent gap for all actions */
}

.action-button {
  padding: 10px 15px;
  border: none;
  border-radius: 6px;
  font-size: 0.95em;
  cursor: pointer;
  transition: background-color 0.2s ease, color 0.2s ease;
  text-decoration: none; /* For router-link styled as button */
  display: inline-block; /* For router-link */
  text-align: center;
}

.details-button {
  background-color: #007bff;
  color: white;
}

.details-button:hover {
  background-color: #0056b3;
}

.export-buttons {
  display: flex;
  flex-direction: column; /* Stack export buttons vertically */
  gap: 8px; /* Spacing between export buttons */
}

.export-button {
  background-color: #6c757d;
  color: white;
}

.export-button:hover {
  background-color: #545b62;
}

/* Responsive adjustments if needed */
@media (min-width: 500px) { /* Example: side-by-side export buttons on larger cards */
  .export-buttons {
    flex-direction: row; /* Row for wider screens */
    justify-content: space-around; /* Distribute space */
  }
   .export-button {
    flex-grow: 1; /* Allow buttons to grow and fill space */
    margin: 0 2px; /* Minimal horizontal margin */
  }
}

</style>
