<script setup lang="ts">
import { ref } from 'vue';
import { CharacterTemplateCard } from '@/components/templates';

// Define the structure for a character template based on docs/pages.md
interface CharacterTemplate {
  id: string; // Added for v-for key
  name: string; // Template name, e.g., "勇敢的战士模板"
  personality: string;
  gender: string;
  abilities: string; // Could be a list or comma-separated string in display
  tags: string[];
  description: string;
  power_system: string;
  original_world: string;
}

const templates = ref<CharacterTemplate[]>([
  {
    id: 'template-1',
    name: '勇敢的战士模板',
    personality: '勇敢、正直、忠诚、不屈不挠',
    gender: '男',
    abilities: '精通各种兵器、强大的近战能力、快速恢复',
    tags: ['战士', '近战', '坦克', '物理'],
    description: '一位身经百战的战士，总是在战场的最前线，用身体保护队友，用利剑斩断敌人。',
    power_system: '斗气/内力',
    original_world: '艾泽拉斯',
  },
  {
    id: 'template-2',
    name: '神秘的法师模板',
    personality: '智慧、冷静、好奇心强、略带神秘',
    gender: '女',
    abilities: '掌握多种元素魔法、远程攻击、精神控制（初级）',
    tags: ['法师', '远程', '魔法', '元素'],
    description: '一位沉醉于知识与魔法奥秘的学者，能够操控强大的元素力量，但有时会因为过于专注而显得有些孤僻。',
    power_system: '魔法/灵能',
    original_world: '费伦大陆',
  },
  {
    id: 'template-3',
    name: '敏捷的刺客模板',
    personality: '冷静、果断、隐秘、目标导向',
    gender: '不限',
    abilities: '潜行、剧毒匕首、快速闪避、开锁',
    tags: ['刺客', '潜行', '爆发', '毒素'],
    description: '如影子般穿梭于黑暗之中，总能在敌人最意想不到的时刻给予致命一击。',
    power_system: '暗影之力/古武技巧',
    original_world: '瓦罗兰',
  }
]);

</script>

<template>
  <div class="character-templates-view">
    <h1 class="view-title">角色模板</h1>
    <div class="templates-grid">
      <CharacterTemplateCard
        v-for="templateItem in templates"
        :key="templateItem.id"
        :template="templateItem"
      />
    </div>
  </div>
</template>

<style scoped>
.character-templates-view {
  padding: 25px; /* Slightly more padding */
  font-family: 'Arial', sans-serif; /* Consider a more modern font stack if available in project */
  background-color: #f4f6f8; /* Adjusted background color */
  min-height: 100vh;
}

.view-title {
  text-align: center;
  margin-bottom: 40px; /* Increased margin */
  font-size: 2.5em; /* Larger title */
  color: #2c3e50; /* Darker, more professional color */
  font-weight: 700; /* Bolder */
}

.templates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); /* Slightly wider cards */
  gap: 30px; /* Increased gap */
  max-width: 1300px; /* Wider max-width */
  margin: 0 auto;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .character-templates-view {
    padding: 20px;
  }
  .view-title {
    font-size: 2em;
  }
  .templates-grid {
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 20px;
  }
}

@media (max-width: 480px) {
  .templates-grid {
    grid-template-columns: 1fr; /* Single column on very small screens */
  }
}
</style>
