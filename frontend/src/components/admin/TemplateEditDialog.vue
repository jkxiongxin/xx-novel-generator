<template>
  <el-dialog
    v-model="visible"
    :title="isEditing ? '编辑角色模板' : '创建角色模板'"
    width="800px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="formRules"
      label-width="120px"
      label-position="left"
    >
      <!-- 基础信息 -->
      <el-card shadow="never" style="margin-bottom: 20px;">
        <template #header>
          <div class="card-header">
            <span>基础信息</span>
          </div>
        </template>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="角色名称" prop="name">
              <el-input v-model="formData.name" placeholder="请输入角色名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="性别" prop="gender">
              <el-select v-model="formData.gender" placeholder="请选择性别">
                <el-option label="男性" value="male" />
                <el-option label="女性" value="female" />
                <el-option label="未知" value="unknown" />
                <el-option label="其他" value="other" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="角色类型" prop="character_type">
              <el-select v-model="formData.character_type" placeholder="请选择角色类型">
                <el-option label="主角" value="protagonist" />
                <el-option label="配角" value="supporting" />
                <el-option label="反派" value="antagonist" />
                <el-option label="次要角色" value="minor" />
                <el-option label="路人" value="passerby" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="力量体系">
              <el-input v-model="formData.power_system" placeholder="如：修真、魔法、武功等" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row>
          <el-col :span="24">
            <el-form-item label="原生世界">
              <el-input v-model="formData.original_world" placeholder="角色来源的世界或背景设定" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row>
          <el-col :span="24">
            <el-form-item label="角色标签">
              <el-select
                v-model="formData.tags"
                multiple
                filterable
                allow-create
                placeholder="添加角色标签"
                style="width: 100%"
              >
                <el-option
                  v-for="tag in predefinedTags"
                  :key="tag"
                  :label="tag"
                  :value="tag"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row>
          <el-col :span="24">
            <el-form-item label="角色描述">
              <el-input
                v-model="formData.description"
                type="textarea"
                :rows="3"
                placeholder="简要描述角色特点、背景等"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row>
          <el-col :span="24">
            <el-form-item label="性格描述">
              <el-input
                v-model="formData.personality"
                type="textarea"
                :rows="3"
                placeholder="描述角色的性格特征"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row>
          <el-col :span="24">
            <el-form-item label="角色能力">
              <el-input
                v-model="formData.abilities"
                type="textarea"
                :rows="3"
                placeholder="描述角色的特殊能力、技能等"
              />
            </el-form-item>
          </el-col>
        </el-row>
      </el-card>

      <!-- 详细信息 -->
      <el-card shadow="never">
        <template #header>
          <div class="card-header">
            <span>详细信息</span>
            <el-switch
              v-model="showDetailForm"
              active-text="显示详细信息"
              inactive-text="隐藏详细信息"
            />
          </div>
        </template>

        <div v-show="showDetailForm">
          <el-row>
            <el-col :span="24">
              <el-form-item label="详细描述">
                <el-input
                  v-model="formData.template_detail!.detailed_description"
                  type="textarea"
                  :rows="4"
                  placeholder="更详细的角色描述"
                />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row>
            <el-col :span="24">
              <el-form-item label="背景故事">
                <el-input
                  v-model="formData.template_detail!.background_story"
                  type="textarea"
                  :rows="4"
                  placeholder="角色的背景故事和经历"
                />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row>
            <el-col :span="24">
              <el-form-item label="人际关系">
                <el-input
                  v-model="formData.template_detail!.relationships"
                  type="textarea"
                  :rows="3"
                  placeholder="角色的重要人际关系"
                />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="优势特点">
                <el-select
                  v-model="formData.template_detail!.strengths"
                  multiple
                  filterable
                  allow-create
                  placeholder="添加优势特点"
                  style="width: 100%"
                >
                  <el-option
                    v-for="strength in predefinedStrengths"
                    :key="strength"
                    :label="strength"
                    :value="strength"
                  />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="弱点缺陷">
                <el-select
                  v-model="formData.template_detail!.weaknesses"
                  multiple
                  filterable
                  allow-create
                  placeholder="添加弱点缺陷"
                  style="width: 100%"
                >
                  <el-option
                    v-for="weakness in predefinedWeaknesses"
                    :key="weakness"
                    :label="weakness"
                    :value="weakness"
                  />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>

          <el-row>
            <el-col :span="24">
              <el-form-item label="动机目标">
                <el-input
                  v-model="formData.template_detail!.motivation"
                  type="textarea"
                  :rows="3"
                  placeholder="角色的动机和目标"
                />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row>
            <el-col :span="24">
              <el-form-item label="角色发展弧">
                <el-input
                  v-model="formData.template_detail!.character_arc"
                  type="textarea"
                  :rows="3"
                  placeholder="角色在故事中的成长和变化"
                />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row>
            <el-col :span="24">
              <el-form-item label="对话风格">
                <el-input
                  v-model="formData.template_detail!.dialogue_style"
                  type="textarea"
                  :rows="2"
                  placeholder="角色的说话方式和语言特点"
                />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row>
            <el-col :span="24">
              <el-form-item label="战斗风格">
                <el-input
                  v-model="formData.template_detail!.combat_style"
                  type="textarea"
                  :rows="2"
                  placeholder="角色的战斗方式和风格"
                />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="装备道具">
                <el-select
                  v-model="formData.template_detail!.equipment"
                  multiple
                  filterable
                  allow-create
                  placeholder="添加装备道具"
                  style="width: 100%"
                >
                  <el-option
                    v-for="item in predefinedEquipment"
                    :key="item"
                    :label="item"
                    :value="item"
                  />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="特殊能力">
                <el-select
                  v-model="formData.template_detail!.special_abilities"
                  multiple
                  filterable
                  allow-create
                  placeholder="添加特殊能力"
                  style="width: 100%"
                >
                  <el-option
                    v-for="ability in predefinedAbilities"
                    :key="ability"
                    :label="ability"
                    :value="ability"
                  />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
        </div>
      </el-card>
    </el-form>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          {{ isEditing ? '更新' : '创建' }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import AdminCharacterTemplateService, {
  type CharacterTemplateResponse,
  type CharacterTemplateCreateRequest,
  type CharacterTemplateUpdateRequest
} from '@/api/admin-character-templates'

// === Props & Emits ===
const props = defineProps<{
  modelValue: boolean
  template?: CharacterTemplateResponse | null
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  success: []
}>()

// === 响应式数据 ===
const formRef = ref<FormInstance>()
const submitting = ref(false)
const showDetailForm = ref(false)

const formData = reactive<CharacterTemplateCreateRequest>({
  name: '',
  gender: '',
  personality: '',
  character_type: '',
  tags: [],
  description: '',
  abilities: '',
  power_system: '',
  original_world: '',
  template_detail: {
    detailed_description: '',
    background_story: '',
    relationships: '',
    strengths: [],
    weaknesses: [],
    motivation: '',
    character_arc: '',
    dialogue_style: '',
    combat_style: '',
    equipment: [],
    special_abilities: []
  }
})

// 预定义选项
const predefinedTags = [
  '勇敢', '智慧', '善良', '冷酷', '神秘', '强大', '弱小', '正义', '邪恶', '中立',
  '法师', '战士', '刺客', '治疗者', '坦克', '射手', '盗贼', '牧师', '德鲁伊', '巫师'
]

const predefinedStrengths = [
  '坚强意志', '聪明才智', '超强体质', '魅力非凡', '洞察力强', '反应敏捷',
  '领导能力', '战斗天赋', '魔法天赋', '社交能力', '学习能力', '适应能力'
]

const predefinedWeaknesses = [
  '冲动鲁莽', '过于信任', '恐惧黑暗', '体质虚弱', '缺乏耐心', '固执己见',
  '社交恐惧', '记忆缺失', '情感脆弱', '魔法抗性低', '容易上当', '优柔寡断'
]

const predefinedEquipment = [
  '长剑', '法杖', '弓箭', '盾牌', '魔法戒指', '治疗药水', '隐身斗篷',
  '火焰宝石', '冰霜护甲', '神圣符文', '暗影匕首', '雷电法球'
]

const predefinedAbilities = [
  '火球术', '治愈术', '隐身术', '瞬间移动', '心灵感应', '预知未来',
  '操控元素', '召唤术', '变身术', '时间停止', '空间撕裂', '生命汲取'
]

// === 表单验证规则 ===
const formRules: FormRules = {
  name: [
    { required: true, message: '请输入角色名称', trigger: 'blur' },
    { min: 1, max: 100, message: '角色名称长度在 1 到 100 个字符', trigger: 'blur' }
  ],
  gender: [
    { required: true, message: '请选择性别', trigger: 'change' }
  ],
  character_type: [
    { required: true, message: '请选择角色类型', trigger: 'change' }
  ]
}

// === 计算属性 ===
const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const isEditing = computed(() => !!props.template)

// === 方法 ===

/**
 * 重置表单
 */
const resetForm = () => {
  Object.assign(formData, {
    name: '',
    gender: '',
    personality: '',
    character_type: '',
    tags: [],
    description: '',
    abilities: '',
    power_system: '',
    original_world: '',
    template_detail: {
      detailed_description: '',
      background_story: '',
      relationships: '',
      strengths: [],
      weaknesses: [],
      motivation: '',
      character_arc: '',
      dialogue_style: '',
      combat_style: '',
      equipment: [],
      special_abilities: []
    }
  })
  showDetailForm.value = false
  formRef.value?.clearValidate()
}

// === 监听器 ===
watch(() => props.template, (template) => {
  if (template) {
    // 编辑模式，填充表单数据
    Object.assign(formData, {
      name: template.name,
      gender: template.gender,
      personality: template.personality || '',
      character_type: template.character_type,
      tags: template.tags || [],
      description: template.description || '',
      abilities: template.abilities || '',
      power_system: template.power_system || '',
      original_world: template.original_world || '',
      template_detail: {
        detailed_description: template.template_detail?.detailed_description || '',
        background_story: template.template_detail?.background_story || '',
        relationships: template.template_detail?.relationships || '',
        strengths: template.template_detail?.strengths || [],
        weaknesses: template.template_detail?.weaknesses || [],
        motivation: template.template_detail?.motivation || '',
        character_arc: template.template_detail?.character_arc || '',
        dialogue_style: template.template_detail?.dialogue_style || '',
        combat_style: template.template_detail?.combat_style || '',
        equipment: template.template_detail?.equipment || [],
        special_abilities: template.template_detail?.special_abilities || []
      }
    })
    showDetailForm.value = !!template.template_detail
  } else {
    // 创建模式，重置表单
    resetForm()
  }
}, { immediate: true })

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
  try {
    // 验证表单
    await formRef.value?.validate()
    
    submitting.value = true
    
    // 准备提交数据
    const submitData = { ...formData }
    
    // 如果没有详细信息，不发送template_detail
    if (!showDetailForm.value) {
      delete submitData.template_detail
    }
    
    if (isEditing.value && props.template) {
      // 更新模式
      await AdminCharacterTemplateService.update(props.template.id, submitData as CharacterTemplateUpdateRequest)
      ElMessage.success('角色模板更新成功')
    } else {
      // 创建模式
      await AdminCharacterTemplateService.create(submitData)
      ElMessage.success('角色模板创建成功')
    }
    
    emit('success')
  } catch (error) {
    console.error('提交失败:', error)
    ElMessage.error(isEditing.value ? '更新失败' : '创建失败')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

:deep(.el-card__body) {
  padding: 20px;
}

:deep(.el-form-item__label) {
  font-weight: 500;
}
</style>