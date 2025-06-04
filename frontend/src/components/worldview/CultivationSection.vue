<template>
  <div class="cultivation-section">
    <div class="section-header">
      <h3>修炼体系</h3>
      <div class="header-actions">
        <el-button type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>
          新建体系
        </el-button>
        <el-button @click="generateSystem" :loading="generating">
          <el-icon><MagicStick /></el-icon>
          AI 生成体系
        </el-button>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <el-skeleton :rows="3" animated />
    </div>

    <!-- 主体内容 -->
    <div v-else class="cultivation-content">
      <!-- 空状态 -->
      <div v-if="systems.length === 0" class="empty-state">
        <el-empty description="暂无修炼体系，点击新建开始创建">
          <el-button type="primary" @click="showCreateDialog = true">
            <el-icon><Plus /></el-icon>
            新建修炼体系
          </el-button>
        </el-empty>
      </div>

      <!-- 修炼体系列表 -->
      <div v-else class="systems-list">
        <el-collapse v-model="activeNames">
          <el-collapse-item
            v-for="system in groupedSystems"
            :key="system.name"
            :title="system.name"
            :name="system.name"
          >
            <template #title>
              <div class="system-header">
                <span>{{ system.name }}</span>
                <el-tag type="success" size="small">
                  {{ system.levels.length }} 个等级
                </el-tag>
              </div>
            </template>

            <el-table :data="system.levels" stripe>
              <el-table-column prop="level_order" label="序号" width="80" />
              <el-table-column prop="level_name" label="等级名称" />
              <el-table-column prop="description" label="描述" show-overflow-tooltip />
              <el-table-column prop="cultivation_method" label="修炼方法" show-overflow-tooltip />
              <el-table-column label="操作" width="150" fixed="right">
                <template #default="{ row }">
                  <el-button-group>
                    <el-button size="small" type="primary" @click="handleEdit(row)">
                      编辑
                    </el-button>
                    <el-button size="small" type="danger" @click="handleDelete(row)">
                      删除
                    </el-button>
                  </el-button-group>
                </template>
              </el-table-column>
            </el-table>
          </el-collapse-item>
        </el-collapse>
      </div>
    </div>

    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="isEdit ? '编辑修炼等级' : '新建修炼等级'"
      width="700px"
      @close="resetForm"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="120px"
      >
        <el-form-item label="体系名称" prop="system_name">
          <el-input v-model="form.system_name" placeholder="请输入修炼体系名称" />
        </el-form-item>

        <el-form-item label="等级名称" prop="level_name">
          <el-input v-model="form.level_name" placeholder="请输入等级名称" />
        </el-form-item>

        <el-form-item label="等级顺序" prop="level_order">
          <el-input-number
            v-model="form.level_order"
            :min="1"
            controls-position="right"
          />
        </el-form-item>

        <el-form-item label="等级描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="请描述该境界的特点"
          />
        </el-form-item>

        <el-form-item label="修炼方法">
          <el-input
            v-model="form.cultivation_method"
            type="textarea"
            :rows="3"
            placeholder="描述达到该境界的修炼方法"
          />
        </el-form-item>

        <el-form-item label="所需资源">
          <el-input
            v-model="form.required_resources"
            type="textarea"
            :rows="2"
            placeholder="列出达到该境界所需的资源"
          />
        </el-form-item>

        <el-form-item label="突破条件">
          <el-input
            v-model="form.breakthrough_condition"
            type="textarea"
            :rows="2"
            placeholder="描述突破到该境界的条件"
          />
        </el-form-item>

        <el-form-item label="力量描述">
          <el-input
            v-model="form.power_description"
            type="textarea"
            :rows="2"
            placeholder="描述该境界拥有的力量"
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
      title="AI 生成修炼体系"
      width="600px"
    >
      <el-form :model="generateForm" label-width="120px">
        <el-form-item label="体系名称">
          <el-input v-model="generateForm.system_name" placeholder="留空则自动生成" />
        </el-form-item>

        <el-form-item label="等级数量">
          <el-input-number
            v-model="generateForm.level_count"
            :min="1"
            :max="15"
            controls-position="right"
          />
        </el-form-item>

        <el-form-item label="生成内容">
          <el-checkbox-group v-model="generateForm.include">
            <el-checkbox label="cultivation_method">修炼方法</el-checkbox>
            <el-checkbox label="required_resources">所需资源</el-checkbox>
            <el-checkbox label="breakthrough_condition">突破条件</el-checkbox>
            <el-checkbox label="power_description">力量描述</el-checkbox>
          </el-checkbox-group>
        </el-form-item>

        <el-form-item label="补充建议">
          <el-input
            v-model="generateForm.suggestion"
            type="textarea"
            :rows="3"
            placeholder="输入你对修炼体系的期望和建议"
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
import type { CultivationSystem } from '@/api/worldview'

// Props 类型定义
interface Props {
  worldviewId: number
  systems: CultivationSystem[]
  loading?: boolean
}

// 表单接口
interface SystemForm {
  system_name: string
  level_name: string
  level_order: number
  description: string
  cultivation_method: string
  required_resources: string
  breakthrough_condition: string
  power_description: string
}

const props = defineProps<Props>()

const emit = defineEmits<{
  create: [data: Omit<CultivationSystem, 'id' | 'user_id' | 'created_at' | 'updated_at'>]
  update: [id: number, data: Partial<CultivationSystem>]
  delete: [id: number]
  refresh: []
}>()

// 状态
const showCreateDialog = ref(false)
const showGenerateDialog = ref(false)
const submitting = ref(false)
const generating = ref(false)
const isEdit = ref(false)
const currentSystemId = ref<number | null>(null)
const activeNames = ref<string[]>([])

// 表单
const formRef = ref<FormInstance>()
const form = reactive<SystemForm>({
  system_name: '',
  level_name: '',
  level_order: 1,
  description: '',
  cultivation_method: '',
  required_resources: '',
  breakthrough_condition: '',
  power_description: ''
})

const generateForm = reactive({
  system_name: '',
  level_count: 9,
  include: ['cultivation_method', 'required_resources', 'breakthrough_condition', 'power_description'],
  suggestion: ''
})

// 验证规则
const rules = {
  system_name: [
    { required: true, message: '请输入体系名称', trigger: 'blur' },
    { max: 100, message: '名称不能超过100个字符', trigger: 'blur' }
  ],
  level_name: [
    { required: true, message: '请输入等级名称', trigger: 'blur' },
    { max: 100, message: '名称不能超过100个字符', trigger: 'blur' }
  ],
  level_order: [
    { required: true, message: '请输入等级顺序', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入等级描述', trigger: 'blur' }
  ]
}

// 计算属性
const groupedSystems = computed(() => {
  const groups: Record<string, CultivationSystem[]> = {}
  
  props.systems.forEach(system => {
    if (!groups[system.system_name]) {
      groups[system.system_name] = []
    }
    groups[system.system_name].push(system)
  })
  
  return Object.entries(groups).map(([name, levels]) => ({
    name,
    levels: levels.sort((a, b) => a.level_order - b.level_order)
  }))
})

// 方法
const resetForm = () => {
  formRef.value?.resetFields()
  Object.assign(form, {
    system_name: '',
    level_name: '',
    level_order: 1,
    description: '',
    cultivation_method: '',
    required_resources: '',
    breakthrough_condition: '',
    power_description: ''
  })
  isEdit.value = false
  currentSystemId.value = null
}

const submitForm = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    submitting.value = true

    if (isEdit.value && currentSystemId.value) {
      // 更新
      emit('update', currentSystemId.value, form)
    } else {
      // 创建
      emit('create', {
        worldview_id: props.worldviewId,
        ...form
      })
    }

    showCreateDialog.value = false
    ElMessage.success(isEdit.value ? '修炼等级更新成功' : '修炼等级创建成功')
  } catch (error) {
    console.error('表单提交失败:', error)
    if (error !== false) { // 不是验证错误
      ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
    }
  } finally {
    submitting.value = false
  }
}

const handleEdit = (system: CultivationSystem) => {
  isEdit.value = true
  currentSystemId.value = system.id
  Object.assign(form, {
    system_name: system.system_name,
    level_name: system.level_name,
    level_order: system.level_order,
    description: system.description,
    cultivation_method: system.cultivation_method || '',
    required_resources: system.required_resources || '',
    breakthrough_condition: system.breakthrough_condition || '',
    power_description: system.power_description || ''
  })
  showCreateDialog.value = true
}

const handleDelete = async (system: CultivationSystem) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除这个修炼等级吗？',
      '确认删除',
      {
        type: 'warning'
      }
    )
    emit('delete', system.id)
    ElMessage.success('修炼等级删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

const generateSystem = () => {
  showGenerateDialog.value = true
}

const submitGenerate = async () => {
  try {
    generating.value = true
    
    // 验证参数
    if (generateForm.level_count < 1 || generateForm.level_count > 15) {
      ElMessage.error('等级数量必须在1-15之间')
      return
    }
    
    // 调用AI生成接口
    const { WorldviewAPI } = await import('@/api/worldview')
    const result = await WorldviewAPI.generateCultivationSystem(props.worldviewId, {
      system_name: generateForm.system_name,
      level_count: generateForm.level_count,
      include: generateForm.include,
      suggestion: generateForm.suggestion
    })
    
    // 检查响应格式 - API拦截器返回完整的 {success, data, message} 对象
    if (result && result.success && result.data?.generated_systems?.length > 0) {
      console.log("进入预览逻辑")
      // 显示生成结果预览
      await showGenerationPreview(result.data.generated_systems)
      
      // 保存生成的数据
      const saveResult = await WorldviewAPI.saveGeneratedCultivation(props.worldviewId, {
        generated_systems: result.data.generated_systems
      })
      
      if (saveResult && saveResult.success && saveResult.data?.saved_count > 0) {
        ElMessage.success(`AI生成成功！共生成 ${saveResult.data.saved_count || result.data.total_levels || result.data.generated_systems.reduce((sum: number, sys: any) => sum + (sys.levels?.length || 0), 0)} 个修炼等级`)
        emit('refresh')
        showGenerateDialog.value = false
      } else {
        ElMessage.error(saveResult?.message || '保存失败')
      }
    } else {
      // 更详细的错误信息
      console.error('生成失败，响应数据:', result)
      ElMessage.error(result?.message || 'AI生成失败，请重试')
    }
    
  } catch (error) {
    console.error('生成失败:', error)
    ElMessage.error('生成失败，请稍后重试')
  } finally {
    generating.value = false
  }
}

const showGenerationPreview = async (generatedSystems: any[]) => {
  // 构建预览内容
  let previewContent = ''
  
  generatedSystems.forEach((system, systemIndex) => {
    previewContent += `【${system.system_name}】\n`
    if (system.description) {
      previewContent += `${system.description}\n\n`
    }
    
    system.levels.forEach((level: any, levelIndex: number) => {
      previewContent += `${levelIndex + 1}. ${level.name}\n`
      previewContent += `   ${level.description}\n`
      
      if (level.cultivation_method && generateForm.include.includes('cultivation_method')) {
        previewContent += `   修炼方法：${level.cultivation_method}\n`
      }
      if (level.required_resources && generateForm.include.includes('required_resources')) {
        previewContent += `   所需资源：${level.required_resources}\n`
      }
      if (level.breakthrough_condition && generateForm.include.includes('breakthrough_condition')) {
        previewContent += `   突破条件：${level.breakthrough_condition}\n`
      }
      if (level.power_description && generateForm.include.includes('power_description')) {
        previewContent += `   力量描述：${level.power_description}\n`
      }
      
      previewContent += '\n'
    })
    
    if (systemIndex < generatedSystems.length - 1) {
      previewContent += '\n---\n\n'
    }
  })
  
  // 显示预览对话框
  try {
    await ElMessageBox.confirm(
      previewContent,
      `AI生成预览 - 共${generatedSystems.reduce((sum, sys) => sum + sys.levels.length, 0)}个等级`,
      {
        confirmButtonText: '确认保存',
        cancelButtonText: '重新生成',
        type: 'info',
        customClass: 'generation-preview-dialog'
      }
    )
  } catch (error) {
    if (error === 'cancel') {
      throw new Error('用户取消保存')
    }
    throw error
  }
}
</script>

<style scoped lang="scss">
.cultivation-section {
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

.cultivation-content {
  background: white;
  border-radius: 8px;
  min-height: 200px;
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

.systems-list {
  .system-header {
    display: flex;
    align-items: center;
    gap: 12px;
    font-size: 16px;
    font-weight: 500;
  }
}

:deep(.el-collapse) {
  border: none;
}

:deep(.el-collapse-item__header) {
  font-size: 16px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 4px;
}

:deep(.el-collapse-item__content) {
  padding: 20px;
}

:deep(.el-table) {
  margin: 12px 0;
}

// 生成预览对话框样式
:deep(.generation-preview-dialog) {
  .el-message-box__content {
    max-height: 60vh;
    overflow-y: auto;
  }
  
  .el-message-box__message {
    white-space: pre-line;
    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
    font-size: 14px;
    line-height: 1.6;
    color: #333;
  }
}
</style>