<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { ElDialog, ElButton, ElInput, ElForm, ElFormItem, ElSelect, ElOption, ElCheckboxGroup, ElCheckbox, ElMessage } from 'element-plus';

// --- Props ---
const props = defineProps({
  modelValue: { // For v-model: visibility
    type: Boolean,
    required: true,
  },
  title: {
    type: String,
    default: '内容总结',
  },
  summaryText: { // Initial or generated summary text
    type: String,
    default: '',
  },
  purposeDescription: {
    type: String,
    default: '此总结将用作生成下一部分的提示词参考。',
  },
  loading: { // For loading state (e.g., when re-generating)
    type: Boolean,
    default: false,
  },
});

// --- Emits ---
const emit = defineEmits([
  'update:modelValue',
  'update:summaryText', // If textarea is directly editable and changes need to be synced
  'regenerate',
  'saveSummary',
  'applyToNextStep',
]);

// --- Dialog Visibility ---
const internalVisible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value),
});

const closeModal = () => {
  internalVisible.value = false;
};

// --- Summary Text ---
const currentSummaryText = ref(props.summaryText);
watch(() => props.summaryText, (newVal) => {
  // Update internal summary only if it's different
  if (newVal !== currentSummaryText.value) {
    currentSummaryText.value = newVal;
  }
});

const onSummaryInput = (value: string) => {
  currentSummaryText.value = value;
  emit('update:summaryText', value); // Emit changes if parent needs to know immediately
};

// --- Summary Settings ---
const summaryLength = ref<'简要' | '详细' | '完整'>('详细'); // Default value
const summaryFocus = ref<string[]>([]); // Array for checkbox group

const summaryLengthOptions = ['简要', '详细', '完整'];
const summaryFocusOptions = ['情节', '角色', '世界观', '其他'];

// --- Footer Actions ---
const handleRegenerate = () => {
  const options = {
    length: summaryLength.value,
    focus: summaryFocus.value,
  };
  emit('regenerate', options);
};

const handleSaveSummary = () => {
  emit('saveSummary', currentSummaryText.value);
  ElMessage.success('总结已保存！(模拟)'); // Provide feedback
  closeModal();
};

const handleApplyToNextStep = () => {
  emit('applyToNextStep', currentSummaryText.value);
  ElMessage.info('总结已准备应用到下一步。(模拟)'); // Provide feedback
  closeModal();
};

</script>

<template>
  <el-dialog
    v-model="internalVisible"
    :title="title"
    width="650px"
    :before-close="closeModal"
    append-to-body
    class="generic-generate-summary-modal"
  >
    <div class="modal-content">
      <h4>总结内容:</h4>
      <el-input
        :model-value="currentSummaryText"
        @update:modelValue="onSummaryInput"
        type="textarea"
        :rows="8"
        placeholder="AI生成的总结内容将显示在这里，您也可以直接编辑..."
        resize="vertical"
      />
      <p class="purpose-description">{{ purposeDescription }}</p>

      <div class="settings-section">
        <h4>总结设置:</h4>
        <el-form label-position="top" label-width="100px">
          <el-form-item label="总结长度:">
            <el-select v-model="summaryLength" placeholder="选择总结长度" style="width: 100%;">
              <el-option v-for="len in summaryLengthOptions" :key="len" :label="len" :value="len" />
            </el-select>
          </el-form-item>
          <el-form-item label="侧重点 (可多选):">
            <el-checkbox-group v-model="summaryFocus">
              <el-checkbox v-for="focus in summaryFocusOptions" :key="focus" :label="focus">
                {{ focus }}
              </el-checkbox>
            </el-checkbox-group>
          </el-form-item>
        </el-form>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="closeModal">关闭</el-button>
        <el-button @click="handleRegenerate" :loading="loading">
          重新生成总结
        </el-button>
        <el-button type="success" @click="handleSaveSummary">
          保存总结
        </el-button>
        <el-button type="primary" @click="handleApplyToNextStep">
          应用到下一步
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<style scoped>
.generic-generate-summary-modal .modal-content {
  padding: 0 10px;
}

.modal-content h4 {
  margin-top: 0;
  margin-bottom: 8px;
  font-size: 1em;
  font-weight: 600;
  color: #303133;
}

.purpose-description {
  font-size: 0.85em;
  color: #909399;
  margin-top: 5px;
  margin-bottom: 15px;
  line-height: 1.4;
}

.settings-section {
  margin-top: 20px;
  padding-top: 15px;
  border-top: 1px solid #e4e7ed;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding-top: 10px;
}

:deep(.el-dialog__body) {
  padding-top: 10px;
  padding-bottom: 15px;
}

.el-form-item {
   margin-bottom: 12px; /* Reduce bottom margin for form items */
}

.el-checkbox-group {
  display: flex;
  gap: 15px; /* Spacing between checkboxes */
  flex-wrap: wrap;
}
</style>
