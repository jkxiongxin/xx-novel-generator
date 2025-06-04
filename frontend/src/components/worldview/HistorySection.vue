<template>
  <div class="history-section">
    <div class="section-header">
      <h3>历史事件</h3>
      <div class="header-actions">
        <el-button type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>
          新建事件
        </el-button>
        <el-button @click="generateHistory" :loading="generating">
          <el-icon><MagicStick /></el-icon>
          AI 生成事件
        </el-button>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <el-skeleton :rows="3" animated />
    </div>

    <!-- 主体内容 -->
    <div v-else class="history-content">
      <!-- 空状态 -->
      <div v-if="histories.length === 0" class="empty-state">
        <el-empty description="暂无历史事件，点击新建开始创建">
          <el-button type="primary" @click="showCreateDialog = true">
            <el-icon><Plus /></el-icon>
            新建历史事件
          </el-button>
        </el-empty>
      </div>

      <!-- 历史事件时间轴 -->
      <div v-else class="history-timeline">
        <el-timeline>
          <el-timeline-item
            v-for="history in sortedHistories"
            :key="history.id"
            :timestamp="history.time_period"
            placement="top"
            :type="getEventType(history.event_type)"
          >
            <el-card>
              <template #header>
                <div class="event-header">
                  <h4>{{ history.event_name }}</h4>
                  <div class="event-actions">
                    <el-button-group>
                      <el-button size="small" type="primary" @click="handleEdit(history)">
                        编辑
                      </el-button>
                      <el-button size="small" type="danger" @click="handleDelete(history)">
                        删除
                      </el-button>
                    </el-button-group>
                  </div>
                </div>
              </template>
              
              <div class="event-content">
                <p class="event-description">{{ history.description }}</p>
                
                <div v-if="history.participants" class="event-detail">
                  <strong>参与者：</strong>
                  <p>{{ history.participants }}</p>
                </div>
                
                <div v-if="history.consequences" class="event-detail">
                  <strong>影响：</strong>
                  <p>{{ history.consequences }}</p>
                </div>
                
                <div v-if="history.related_locations" class="event-detail">
                  <strong>相关地点：</strong>
                  <p>{{ history.related_locations }}</p>
                </div>
              </div>
            </el-card>
          </el-timeline-item>
        </el-timeline>
      </div>
    </div>

    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="isEdit ? '编辑历史事件' : '新建历史事件'"
      width="700px"
      @close="resetForm"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="事件名称" prop="event_name">
          <el-input v-model="form.event_name" placeholder="请输入事件名称" />
        </el-form-item>

        <el-form-item label="时间段" prop="time_period">
          <el-input v-model="form.time_period" placeholder="请输入发生时间" />
        </el-form-item>

        <el-form-item label="事件类型" prop="event_type">
          <el-select v-model="form.event_type" placeholder="选择事件类型">
            <el-option label="重大事件" value="major" />
            <el-option label="战争" value="war" />
            <el-option label="朝代更迭" value="dynasty" />
            <el-option label="文化" value="culture" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>

        <el-form-item label="时间顺序" prop="time_order">
          <el-input-number
            v-model="form.time_order"
            :min="1"
            controls-position="right"
          />
        </el-form-item>

        <el-form-item label="事件描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="请描述事件的经过"
          />
        </el-form-item>

        <el-form-item label="参与者">
          <el-input
            v-model="form.participants"
            type="textarea"
            :rows="2"
            placeholder="列出事件的主要参与者"
          />
        </el-form-item>

        <el-form-item label="影响">
          <el-input
            v-model="form.consequences"
            type="textarea"
            :rows="2"
            placeholder="描述事件造成的影响"
          />
        </el-form-item>

        <el-form-item label="相关地点">
          <el-input
            v-model="form.related_locations"
            type="textarea"
            :rows="2"
            placeholder="列出事件涉及的地点"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitting">
          {{ isEdit ? '保存' : '创建' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- AI生成对话框 -->
    <el-dialog
      v-model="showGenerateDialog"
      title="AI 生成历史事件"
      width="600px"
    >
      <el-form :model="generateForm" label-width="100px">
        <el-form-item label="事件数量">
          <el-input-number
            v-model="generateForm.count"
            :min="1"
            :max="10"
            controls-position="right"
          />
        </el-form-item>

        <el-form-item label="事件类型">
          <el-select v-model="generateForm.event_types" multiple placeholder="选择事件类型">
            <el-option label="重大事件" value="major" />
            <el-option label="战争" value="war" />
            <el-option label="朝代更迭" value="dynasty" />
            <el-option label="文化" value="culture" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>

        <el-form-item label="生成内容">
          <el-checkbox-group v-model="generateForm.include">
            <el-checkbox label="participants">参与者</el-checkbox>
            <el-checkbox label="consequences">影响</el-checkbox>
            <el-checkbox label="related_locations">相关地点</el-checkbox>
          </el-checkbox-group>
        </el-form-item>

        <el-form-item label="补充建议">
          <el-input
            v-model="generateForm.suggestion"
            type="textarea"
            :rows="3"
            placeholder="输入你对历史事件的期望和建议"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showGenerateDialog = false">取消</el-button>
        <el-button type="primary" @click="submitGenerate" :loading="generating">
          开始生成
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, MagicStick } from '@element-plus/icons-vue'
import type { FormInstance } from 'element-plus'
import type { History } from '@/api/worldview'

// Props 类型定义
interface Props {
  worldviewId: number
  histories: History[]
  loading?: boolean
}

// 表单接口
interface HistoryForm {
  event_name: string
  time_period: string
  event_type: string
  time_order: number
  description: string
  participants: string
  consequences: string
  related_locations: string
}

const props = defineProps<Props>()

const emit = defineEmits<{
  create: [data: Omit<History, 'id' | 'user_id' | 'created_at' | 'updated_at'>]
  update: [id: number, data: Partial<History>]
  delete: [id: number]
  refresh: []
}>()

// 状态
const showCreateDialog = ref(false)
const showGenerateDialog = ref(false)
const submitting = ref(false)
const generating = ref(false)
const isEdit = ref(false)
const currentHistoryId = ref<number | null>(null)

// 表单
const formRef = ref<FormInstance>()
const form = reactive<HistoryForm>({
  event_name: '',
  time_period: '',
  event_type: '',
  time_order: 1,
  description: '',
  participants: '',
  consequences: '',
  related_locations: ''
})

const generateForm = reactive({
  count: 3,
  event_types: ['major', 'war'],
  include: ['participants', 'consequences', 'related_locations'],
  suggestion: ''
})

// 验证规则
const rules = {
  event_name: [
    { required: true, message: '请输入事件名称', trigger: 'blur' },
    { max: 200, message: '名称不能超过200个字符', trigger: 'blur' }
  ],
  time_period: [
    { required: true, message: '请输入时间段', trigger: 'blur' }
  ],
  event_type: [
    { required: true, message: '请选择事件类型', trigger: 'change' }
  ],
  time_order: [
    { required: true, message: '请输入时间顺序', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入事件描述', trigger: 'blur' }
  ]
}

// 计算属性
const sortedHistories = computed(() => {
  return [...props.histories].sort((a, b) => a.time_order - b.time_order)
})

// 方法
const resetForm = () => {
  formRef.value?.resetFields()
  Object.assign(form, {
    event_name: '',
    time_period: '',
    event_type: '',
    time_order: 1,
    description: '',
    participants: '',
    consequences: '',
    related_locations: ''
  })
  isEdit.value = false
  currentHistoryId.value = null
}

const submitForm = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    submitting.value = true

    if (isEdit.value && currentHistoryId.value) {
      // 更新
      emit('update', currentHistoryId.value, form)
    } else {
      // 创建
      emit('create', {
        worldview_id: props.worldviewId,
        ...form
      })
    }

    showCreateDialog.value = false
    ElMessage.success(isEdit.value ? '历史事件更新成功' : '历史事件创建成功')
  } catch (error) {
    console.error('表单提交失败:', error)
    if (error !== false) { // 不是验证错误
      ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
    }
  } finally {
    submitting.value = false
  }
}

const handleEdit = (history: History) => {
  isEdit.value = true
  currentHistoryId.value = history.id
  Object.assign(form, {
    event_name: history.event_name,
    time_period: history.time_period || '',
    event_type: history.event_type || '',
    time_order: history.time_order,
    description: history.description,
    participants: history.participants || '',
    consequences: history.consequences || '',
    related_locations: history.related_locations || ''
  })
  showCreateDialog.value = true
}

const handleDelete = async (history: History) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除这个历史事件吗？',
      '确认删除',
      {
        type: 'warning'
      }
    )
    emit('delete', history.id)
    ElMessage.success('历史事件删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

const getEventType = (type?: string): '' | 'primary' | 'success' | 'warning' | 'danger' => {
  switch (type) {
    case 'major':
      return 'danger'
    case 'war':
      return 'warning'
    case 'dynasty':
      return 'primary'
    case 'culture':
      return 'success'
    default:
      return ''
  }
}

const generateHistory = () => {
  showGenerateDialog.value = true
}

const submitGenerate = async () => {
  try {
    generating.value = true
    // TODO: 实现AI生成逻辑
    ElMessage.warning('AI生成功能开发中...')
  } catch (error) {
    console.error('生成失败:', error)
    ElMessage.error('生成失败')
  } finally {
    generating.value = false
    showGenerateDialog.value = false
  }
}
</script>

<style scoped lang="scss">
.history-section {
  padding: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;

  h3 {
    margin: 0;
    font-size: 18px;
  }

  .header-actions {
    display: flex;
    gap: 12px;
  }
}

.history-content {
  background: white;
  border-radius: 8px;
  min-height: 200px;
  padding: 20px;
}

.loading-state {
  padding: 20px;
}

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 200px;
}

.history-timeline {
  .event-header {
    display: flex;
    justify-content: space-between;
    align-items: center;

    h4 {
      margin: 0;
      font-size: 16px;
    }
  }

  .event-content {
    .event-description {
      margin: 0 0 16px;
      font-size: 14px;
      color: #606266;
    }

    .event-detail {
      margin: 8px 0;
      font-size: 13px;

      strong {
        color: #303133;
      }

      p {
        margin: 4px 0;
        color: #606266;
      }
    }
  }
}

:deep(.el-timeline) {
  padding: 0;
  margin: 0;
}

:deep(.el-timeline-item__node) {
  &.is-primary {
    background-color: var(--el-color-primary);
  }
  &.is-success {
    background-color: var(--el-color-success);
  }
  &.is-warning {
    background-color: var(--el-color-warning);
  }
  &.is-danger {
    background-color: var(--el-color-danger);
  }
}

:deep(.el-timeline-item__timestamp) {
  color: #909399;
  font-size: 13px;
  margin-bottom: 8px;
}

:deep(.el-card) {
  border-radius: 8px;
  margin-bottom: 16px;
}
</style>