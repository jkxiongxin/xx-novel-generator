<template>
  <div class="world-maps-section">
    <div class="section-header">
      <h3>世界地图</h3>
      <div class="actions">
        <el-button type="primary" @click="$emit('create')">新建地图区域</el-button>
        <!-- Old AI 生成 button can be re-evaluated later. For now, focusing on empty state generation. -->
        <!-- <el-button @click="generateMaps">AI生成</el-button> -->
      </div>
    </div>

    <div class="maps-content">
      <div v-if="maps.length === 0" class="empty-state">
        <el-empty description="本地图区域暂无内容。" />
        <div class="empty-state-actions">
          <el-button @click="openPreviewPromptModal('defaultMapPrompt')">预览默认提示词</el-button>
          <el-button type="primary" @click="handleGenerateMapsWithPrompt">AI 生成地图区域</el-button>
        </div>
      </div>
      
      <div v-else class="maps-list">
        <div
          v-for="map in maps"
          :key="map.id"
          class="map-item"
        >
          <div class="map-header">
            <h4>{{ map.region_name }}</h4>
            <div class="map-actions">
              <el-button size="small" @click="$emit('update', map)">编辑</el-button>
              <el-button size="small" type="danger" @click="$emit('delete', map)">删除</el-button>
            </div>
          </div>
          <p class="map-description">{{ map.description }}</p>
          <div class="map-meta">
            <el-tag size="small">层级 {{ map.level }}</el-tag>
          </div>
        </div>
      </div>
    </div>
  </div>

  <GenericPreviewPromptModal
    v-model="showPreviewPromptModal"
    :prompt="currentPromptText"
    :readonly="isPromptReadonly"
    title="地图区域生成提示词"
    @generate="handleGenerateMapsFromModal"
    @update:prompt="newPrompt => currentPromptText = newPrompt"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { ElMessage } from 'element-plus';
import GenericPreviewPromptModal from '@/components/shared/GenericPreviewPromptModal.vue';

defineProps({
  worldviewId: {
    type: Number,
    required: true
  },
  maps: {
    type: Array,
    default: () => []
  }
});

const emit = defineEmits(['create', 'update', 'delete', 'refresh']);

// State for the modal
const showPreviewPromptModal = ref(false);
const currentPromptText = ref('');
const isPromptReadonly = ref(true);

const defaultMapPrompt = "为这个世界生成一些独特的地理区域和地标，例如山脉、河流、森林、城市、废墟等。请描述它们的特征和大致位置。";

const openPreviewPromptModal = (promptType: string) => {
  if (promptType === 'defaultMapPrompt') {
    currentPromptText.value = defaultMapPrompt;
  } else {
    // Potentially handle other predefined prompt types or keep it empty
    currentPromptText.value = defaultMapPrompt; // Default to map prompt for now
  }
  isPromptReadonly.value = true; // Modal opens in readonly mode for default prompts
  showPreviewPromptModal.value = true;
};

const handleGenerateMapsWithPrompt = () => {
  // This function opens the modal, allowing the user to customize the prompt if needed.
  // It could start with the default prompt or an empty one.
  currentPromptText.value = defaultMapPrompt; // Pre-fill with default
  isPromptReadonly.value = false; // Modal opens in editable mode
  showPreviewPromptModal.value = true;
};

const handleGenerateMapsFromModal = (promptToUse: string) => {
  console.log('Generating maps with prompt:', promptToUse);
  ElMessage.info('AI生成地图区域（通过提示词）功能开发中...');
  showPreviewPromptModal.value = false;
  // In a real implementation, you would call an API here:
  // try {
  //   const result = await api.generateWorldMaps(props.worldviewId, promptToUse);
  //   emit('refresh'); // Or handle result directly
  //   ElMessage.success('地图区域已开始生成！');
  // } catch (error) {
  //   ElMessage.error('地图区域生成失败。');
  //   console.error("Failed to generate maps:", error);
  // }
};

// const generateMaps = () => { // Old function, replaced by new flow for empty state
//   ElMessage.info('AI生成地图功能开发中...')
// }
</script>

<style scoped>
.world-maps-section {
  padding: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h3 {
  margin: 0;
  font-size: 1.3em; /* Slightly larger */
  font-weight: 600;
}

.actions {
  display: flex;
  gap: 10px; /* Increased gap */
}

.empty-state {
  text-align: center;
  padding: 40px 20px; /* Adjusted padding */
  background-color: #fcfcfc;
  border-radius: 8px;
  border: 1px dashed #dcdfe6;
}

.empty-state-actions {
  margin-top: 20px;
  display: flex;
  justify-content: center;
  gap: 15px;
}

.maps-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.map-item {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 16px;
}

.map-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.map-header h4 {
  margin: 0;
  font-size: 16px;
}

.map-actions {
  display: flex;
  gap: 4px;
}

.map-description {
  margin: 8px 0;
  color: #606266;
  line-height: 1.6;
}

.map-meta {
  display: flex;
  gap: 8px;
}
</style>