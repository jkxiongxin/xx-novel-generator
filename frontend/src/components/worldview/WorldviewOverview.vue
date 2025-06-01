<template>
  <div class="worldview-overview">
    <div class="overview-header">
      <h3>{{ worldview.name }}</h3>
      <div class="actions">
        <el-button @click="editMode = !editMode">
          {{ editMode ? '取消编辑' : '编辑' }}
        </el-button>
        <el-button type="danger" @click="$emit('delete')">删除</el-button>
      </div>
    </div>

    <div class="overview-content">
      <div v-if="!editMode" class="display-mode">
        <div class="info-section">
          <h4>世界描述</h4>
          <p>{{ worldview.description || '暂无描述' }}</p>
        </div>
        
        <div class="status-section">
          <el-tag v-if="worldview.is_primary" type="success" size="large">
            主世界
          </el-tag>
        </div>
      </div>
      
      <div v-else class="edit-mode">
        <el-form :model="editForm" label-width="100px">
          <el-form-item label="世界名称">
            <el-input v-model="editForm.name" />
          </el-form-item>
          
          <el-form-item label="世界描述">
            <el-input
              v-model="editForm.description"
              type="textarea"
              :rows="4"
            />
          </el-form-item>
          
          <el-form-item>
            <el-checkbox v-model="editForm.is_primary">设为主世界</el-checkbox>
          </el-form-item>
          
          <el-form-item>
            <el-button type="primary" @click="saveChanges">保存</el-button>
            <el-button @click="cancelEdit">取消</el-button>
          </el-form-item>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'

const props = defineProps({
  worldview: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['update', 'delete'])

const editMode = ref(false)
const editForm = reactive({
  name: '',
  description: '',
  is_primary: false
})

const saveChanges = () => {
  emit('update', { ...editForm })
  editMode.value = false
}

const cancelEdit = () => {
  resetForm()
  editMode.value = false
}

const resetForm = () => {
  editForm.name = props.worldview.name
  editForm.description = props.worldview.description || ''
  editForm.is_primary = props.worldview.is_primary || false
}

// 监听worldview变化，重置表单
watch(() => props.worldview, resetForm, { immediate: true })
</script>

<style scoped>
.worldview-overview {
  padding: 20px;
}

.overview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.overview-header h3 {
  margin: 0;
  font-size: 24px;
  font-weight: 500;
}

.actions {
  display: flex;
  gap: 8px;
}

.info-section {
  margin-bottom: 20px;
}

.info-section h4 {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 500;
  color: #606266;
}

.info-section p {
  margin: 0;
  line-height: 1.6;
  color: #303133;
}

.status-section {
  margin-bottom: 20px;
}
</style>