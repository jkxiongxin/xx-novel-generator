<template>
  <el-dialog
    v-model="visible"
    title="批量设置模板状态"
    width="500px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <div class="batch-info">
      <el-alert
        :title="`将为 ${templateIds.length} 个模板设置状态`"
        type="info"
        :closable="false"
        show-icon
      />
    </div>

    <el-form
      ref="formRef"
      :model="formData"
      label-width="100px"
      label-position="left"
      style="margin-top: 20px;"
    >
      <el-form-item label="热门状态">
        <el-radio-group v-model="formData.is_popular">
          <el-radio :label="undefined">不修改</el-radio>
          <el-radio :label="true">设为热门</el-radio>
          <el-radio :label="false">取消热门</el-radio>
        </el-radio-group>
      </el-form-item>

      <el-form-item label="新增状态">
        <el-radio-group v-model="formData.is_new">
          <el-radio :label="undefined">不修改</el-radio>
          <el-radio :label="true">设为新增</el-radio>
          <el-radio :label="false">取消新增</el-radio>
        </el-radio-group>
      </el-form-item>

      <el-form-item label="评分">
        <div class="rating-input">
          <el-radio-group v-model="ratingMode">
            <el-radio label="keep">不修改</el-radio>
            <el-radio label="set">设置评分</el-radio>
          </el-radio-group>
          <div v-if="ratingMode === 'set'" style="margin-top: 8px;">
            <el-rate
              v-model="formData.rating"
              :max="5"
              :precision="0.5"
              show-score
              score-template="评分: {value}"
            />
          </div>
        </div>
      </el-form-item>
    </el-form>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button 
          type="primary" 
          @click="handleSubmit" 
          :loading="submitting"
          :disabled="!hasChanges"
        >
          确定设置
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'
import { ElMessage, ElNotification, type FormInstance } from 'element-plus'
import AdminCharacterTemplateService, {
  type TemplateStatusUpdateRequest
} from '@/api/admin-character-templates'

// === Props & Emits ===
const props = defineProps<{
  modelValue: boolean
  templateIds: number[]
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  success: []
}>()

// === 响应式数据 ===
const formRef = ref<FormInstance>()
const submitting = ref(false)
const ratingMode = ref<'keep' | 'set'>('keep')

const formData = reactive<TemplateStatusUpdateRequest>({
  is_popular: undefined,
  is_new: undefined,
  rating: undefined
})

// === 计算属性 ===
const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const hasChanges = computed(() => {
  return formData.is_popular !== undefined || 
         formData.is_new !== undefined || 
         (ratingMode.value === 'set' && formData.rating !== undefined)
})

// === 监听器 ===
watch(ratingMode, (mode) => {
  if (mode === 'keep') {
    formData.rating = undefined
  } else if (mode === 'set' && formData.rating === undefined) {
    formData.rating = 5 // 默认5星
  }
})

// === 方法 ===

/**
 * 重置表单
 */
const resetForm = () => {
  formData.is_popular = undefined
  formData.is_new = undefined
  formData.rating = undefined
  ratingMode.value = 'keep'
}

/**
 * 处理关闭
 */
const handleClose = () => {
  visible.value = false
  resetForm()
}

/**
 * 处理提交
 */
const handleSubmit = async () => {
  if (!hasChanges.value) {
    ElMessage.warning('请至少修改一项状态')
    return
  }

  try {
    submitting.value = true
    
    // 准备提交数据
    const statusUpdates: TemplateStatusUpdateRequest = {}
    
    if (formData.is_popular !== undefined) {
      statusUpdates.is_popular = formData.is_popular
    }
    
    if (formData.is_new !== undefined) {
      statusUpdates.is_new = formData.is_new
    }
    
    if (ratingMode.value === 'set' && formData.rating !== undefined) {
      statusUpdates.rating = formData.rating
    }
    
    // 调用批量更新API
    const response = await AdminCharacterTemplateService.batchUpdateStatus({
      template_ids: props.templateIds,
      status_updates: statusUpdates
    })
    
    // 显示结果
    if (response.success_count > 0) {
      ElNotification.success({
        title: '批量设置完成',
        message: `成功设置 ${response.success_count} 个模板${response.failed_count > 0 ? `，失败 ${response.failed_count} 个` : ''}`
      })
    }
    
    if (response.failed_count > 0 && response.failed_items.length > 0) {
      console.warn('批量设置失败项:', response.failed_items)
      ElMessage.warning(`部分模板设置失败，请检查控制台日志`)
    }
    
    emit('success')
  } catch (error) {
    console.error('批量设置状态失败:', error)
    ElMessage.error('批量设置状态失败')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.batch-info {
  margin-bottom: 20px;
}

.rating-input {
  width: 100%;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

:deep(.el-form-item__label) {
  font-weight: 500;
}

:deep(.el-radio-group) {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

:deep(.el-radio) {
  margin-right: 0;
}
</style>