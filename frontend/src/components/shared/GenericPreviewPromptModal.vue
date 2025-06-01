<script setup lang="ts">
import { ref, watch, computed } from 'vue';
import { ElMessage } from 'element-plus';

const props = defineProps({
  modelValue: { // For v-model: visibility
    type: Boolean,
    required: true,
  },
  prompt: { // Initial prompt text
    type: String,
    default: '',
  },
  title: {
    type: String,
    default: '提示词预览',
  },
  readonly: { // Initial readonly state for textarea
    type: Boolean,
    default: true,
  },
});

const emit = defineEmits(['update:modelValue', 'update:prompt', 'generate']);

// Internal state for the dialog visibility
const internalVisible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value),
});

// Internal state for the prompt text
const currentPrompt = ref(props.prompt);
watch(() => props.prompt, (newVal) => {
  // Update internal prompt only if it's different, to avoid loops if parent also watches emitted prompt
  if (newVal !== currentPrompt.value) {
    currentPrompt.value = newVal;
  }
});

const onInput = (value: string) => {
  currentPrompt.value = value; // el-input (type="textarea") emits the value directly for @input
  emit('update:prompt', value);
};

// Internal state for readonly status of the textarea
const isReadonly = ref(props.readonly);
watch(() => props.readonly, (newVal) => {
  isReadonly.value = newVal;
});

const handleClose = () => {
  internalVisible.value = false;
};

const handleCopyPrompt = async () => {
  if (!currentPrompt.value) {
    ElMessage.warning('提示词为空，无需复制。');
    return;
  }
  try {
    await navigator.clipboard.writeText(currentPrompt.value);
    ElMessage.success('提示词已复制到剪贴板！');
  } catch (err) {
    console.error('Failed to copy: ', err);
    ElMessage.error('复制失败，请检查浏览器权限或手动复制。');
  }
};

const toggleEditMode = () => {
  isReadonly.value = !isReadonly.value;
  if (isReadonly.value) {
    ElMessage.info('提示词已锁定。');
    // Optionally emit update:prompt here if saving means confirming the current text
    emit('update:prompt', currentPrompt.value);
  } else {
    ElMessage.info('提示词现在可以编辑。');
  }
};

const handleGenerate = () => {
  emit('generate', currentPrompt.value);
  handleClose(); // Close the dialog after emitting generate
};

</script>

<template>
  <el-dialog
    v-model="internalVisible"
    :title="title"
    width="600px"
    :before-close="handleClose"
    append-to-body
    class="generic-preview-prompt-modal"
  >
    <div class="modal-content">
      <el-input
        :model-value="currentPrompt"
        @update:modelValue="onInput"
        type="textarea"
        :rows="12"
        :readonly="isReadonly"
        placeholder="请输入或编辑提示词..."
        resize="vertical"
      />
    </div>
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleCopyPrompt">复制提示词</el-button>
        <el-button @click="toggleEditMode">
          {{ isReadonly ? '编辑提示词' : '保存提示词' }}
        </el-button>
        <el-button @click="handleClose">关闭</el-button>
        <el-button type="primary" @click="handleGenerate">
          使用此提示词生成
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<style scoped>
.generic-preview-prompt-modal .modal-content {
  padding: 0px 0px 10px 0px; /* Add some padding if el-dialog default is not enough */
}

.generic-preview-prompt-modal .el-textarea__inner {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', 'source-code-pro', monospace;
  font-size: 0.95em;
  line-height: 1.5;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end; /* Aligns buttons to the right */
  gap: 10px; /* Adds space between buttons */
  padding-top: 10px;
}
</style>
