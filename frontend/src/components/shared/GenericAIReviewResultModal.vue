<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { ElMessage, ElTag, ElDialog, ElButton, ElInput, ElTable, ElTableColumn, ElAlert, ElScrollbar } from 'element-plus';

// --- Props ---
interface Issue {
  id: string | number;
  type: string; // '逻辑问题' | '语法问题' | '内容问题' | '其他'
  location?: string;
  description: string;
  suggestion: string;
}

interface ReviewResult {
  status: '通过' | '有问题' | string; // Allow other strings for flexibility
  issues?: Issue[];
}

const props = defineProps({
  modelValue: { // For v-model: visibility
    type: Boolean,
    required: true,
  },
  title: {
    type: String,
    default: 'AI审核结果',
  },
  reviewResult: {
    type: Object as () => ReviewResult | null,
    default: () => null,
  },
  loading: { // For loading state on feedback submission
    type: Boolean,
    default: false,
  },
});

// --- Emits ---
const emit = defineEmits(['update:modelValue', 'submitFeedback', 'ignoreAllIssues', 'processIssue']);

// --- Dialog Visibility ---
const internalVisible = computed({
  get: () = > props.modelValue,
  set: (value) = > emit('update:modelValue', value),
});

const closeModal = () => {
  internalVisible.value = false;
};

// --- Feedback ---
const feedbackText = ref('');

const handleSubmitFeedback = () => {
  if (!feedbackText.value.trim()) {
    ElMessage.warning('反馈意见不能为空！');
    return;
  }
  emit('submitFeedback', feedbackText.value);
  feedbackText.value = ''; // Clear after submit
  // closeModal(); // Optionally close modal after submitting feedback
};

// --- Issue Handling ---
const handleIgnoreAllIssues = () => {
  emit('ignoreAllIssues');
  closeModal();
};

const handleProcessIssues = () => {
  // For now, this emits a general event. Specific issue ID can be passed if UI supports it.
  emit('processIssue');
  ElMessage.info('请在文本编辑器中逐个处理或修正问题。');
  closeModal();
};

// --- Computed for easier template logic ---
const hasIssues = computed(() => {
  return props.reviewResult && props.reviewResult.status === '有问题' && props.reviewResult.issues && props.reviewResult.issues.length > 0;
});

const noDetailedIssuesMessage = "暂未发现具体问题，但AI标记内容可能存在风险，请人工复核。";

</script>

<template>
  <el-dialog
    v-model="internalVisible"
    :title="title"
    width="75%"
    :before-close="closeModal"
    append-to-body
    class="generic-ai-review-result-modal"
  >
    <div v-if="!reviewResult" class="review-loading">
      <p>正在加载审核结果...</p>
    </div>

    <div v-else class="review-content">
      <div class="result-status-section">
        <span style="margin-right: 8px;">审核状态:</span>
        <el-tag
          :type="reviewResult.status === '通过' ? 'success' : (reviewResult.status === '有问题' ? 'danger' : 'warning')"
        >
          {{ reviewResult.status }}
        </el-tag>
      </div>

      <el-scrollbar v-if="hasIssues" max-height="300px" class="issues-list-section">
        <h4>问题列表:</h4>
        <el-table :data="reviewResult.issues" stripe border size="small">
          <el-table-column type="index" label="序号" width="60" align="center" />
          <el-table-column prop="type" label="问题类型" width="120" />
          <el-table-column prop="location" label="问题位置" width="150" />
          <el-table-column prop="description" label="问题描述" min-width="200" />
          <el-table-column prop="suggestion" label="建议修改方案" min-width="200" />
          <!--
          <el-table-column label="操作" width="100" align="center">
            <template #default="scope">
              <el-button size="small" @click="emit('processIssue', scope.row.id)">处理</el-button>
            </template>
          </el-table-column>
          -->
        </el-table>
      </el-scrollbar>
      <el-alert
        v-else-if="reviewResult.status === '有问题' && (!reviewResult.issues || reviewResult.issues.length === 0)"
        :title="noDetailedIssuesMessage"
        type="warning"
        show-icon
        :closable="false"
        class="no-issues-alert"
      />
       <el-alert
        v-if="reviewResult.status === '通过'"
        title="AI审核通过，内容符合基本规范。"
        type="success"
        show-icon
        :closable="false"
        class="pass-alert"
      />


      <div class="feedback-section">
        <h4>用户反馈与修改要求:</h4>
        <el-input
          v-model="feedbackText"
          type="textarea"
          :rows="4"
          placeholder="如果您对审核结果有疑问，或希望AI进行特定修改，请在此处描述您的要求..."
          resize="vertical"
        />
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="closeModal">关闭</el-button>
        <el-button
          @click="handleIgnoreAllIssues"
          v-if="hasIssues"
          type="warning"
          plain
        >
          忽略所有问题
        </el-button>
        <el-button
          @click="handleProcessIssues"
          v-if="hasIssues"
          type="info"
          plain
        >
          逐个处理指引
        </el-button>
        <el-button
          @click="handleSubmitFeedback"
          :loading="loading"
          type="primary"
          :disabled="!feedbackText.trim()"
        >
          提交修改意见
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<style scoped>
.generic-ai-review-result-modal .review-content {
  padding: 0 10px;
}

.review-loading p {
  text-align: center;
  color: #606266;
  padding: 20px;
}

.result-status-section {
  margin-bottom: 20px;
  font-size: 1.1em;
  display: flex;
  align-items: center;
}

.issues-list-section {
  margin-bottom: 20px;
}

.issues-list-section h4,
.feedback-section h4 {
  margin-top: 0;
  margin-bottom: 10px;
  font-size: 1em;
  font-weight: 600;
  color: #303133;
}

.no-issues-alert, .pass-alert {
  margin-bottom: 20px;
}

.feedback-section {
  margin-top: 20px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding-top: 10px;
}

:deep(.el-dialog__body) {
  padding-top: 10px;
  padding-bottom: 10px;
}
</style>
