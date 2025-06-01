<script setup lang="ts">
import type { PropType } from 'vue';

interface CharacterTemplate {
  id: string;
  name: string;
  personality: string;
  gender: string;
  abilities: string;
  tags: string[];
  description: string;
  power_system: string;
  original_world: string;
}

defineProps({
  template: {
    type: Object as PropType<CharacterTemplate>,
    required: true,
  },
});

const useTemplate = (templateName: string) => {
  console.log(`Using template: ${templateName}`);
  // In a real app, this would likely involve navigating to a character creation screen
  // or setting some state in a store.
  alert(`选择使用模板："${templateName}" (功能待实现)`);
};
</script>

<template>
  <div class="character-template-card">
    <div class="card-header">
      <h3>{{ template.name }}</h3>
    </div>
    <div class="card-content">
      <p><strong>性格:</strong> {{ template.personality }}</p>
      <p><strong>性别:</strong> {{ template.gender }}</p>
      <p><strong>能力:</strong> {{ template.abilities }}</p>
      <p><strong>标签:</strong> <el-tag v-for="tag in template.tags" :key="tag" type="success" size="small" style="margin-right: 5px;">{{ tag }}</el-tag></p>
      <p><strong>描述:</strong> {{ template.description }}</p>
      <p><strong>所属力量体系:</strong> {{ template.power_system }}</p>
      <p><strong>原生世界名:</strong> {{ template.original_world }}</p>
    </div>
    <div class="card-actions">
      <el-button type="primary" @click="useTemplate(template.name)">
        使用此模板
      </el-button>
    </div>
  </div>
</template>

<style scoped>
.character-template-card {
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  background-color: #fff;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
  justify-content: space-between; /* Ensures footer is at bottom */
  transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
}

.character-template-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.12);
}

.card-header h3 {
  margin-top: 0;
  margin-bottom: 15px;
  font-size: 1.6em;
  color: #303133;
  text-align: center;
  border-bottom: 1px solid #ebeef5;
  padding-bottom: 10px;
}

.card-content p {
  margin: 0 0 10px 0;
  font-size: 0.95em;
  line-height: 1.6;
  color: #606266;
}

.card-content p strong {
  color: #303133;
  font-weight: 600;
}

.card-actions {
  margin-top: 20px;
  text-align: center;
}

.card-actions .el-button {
  width: 100%;
  max-width: 200px; /* Prevent button from being too wide */
}
</style>
