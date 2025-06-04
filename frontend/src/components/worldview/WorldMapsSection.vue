<template>
  <!-- Template content remains the same -->
</template>

<script setup lang="ts">
import { ref, computed, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, MagicStick } from '@element-plus/icons-vue'
import type { FormInstance } from 'element-plus'
import type { WorldMap } from '@/api/worldview'

// Props type definition
interface Props {
  worldviewId: number
  maps: WorldMap[]
  loading?: boolean
}

// Form interface
interface MapForm {
  region_name: string
  parent_region_id: number | undefined
  description: string
  level: number
  climate: string
  terrain: string
  resources: string
  population: string
  culture: string
}

const props = defineProps<Props>()

const emit = defineEmits<{
  create: [data: Omit<WorldMap, 'id' | 'user_id' | 'created_at' | 'updated_at'>]
  update: [id: number, data: Partial<WorldMap>]
  delete: [id: number]
  refresh: []
}>()

// 状态
const showCreateDialog = ref(false)
const showGenerateDialog = ref(false)
const submitting = ref(false)
const generating = ref(false)
const isEdit = ref(false)
const currentMapId = ref<number | null>(null)

// 表单
const formRef = ref<FormInstance>()
const form = reactive<MapForm>({
  region_name: '',
  parent_region_id: undefined,
  description: '',
  level: 1,
  climate: '',
  terrain: '',
  resources: '',
  population: '',
  culture: ''
})

const generateForm = reactive({
  count: 3,
  include: ['climate', 'terrain', 'resources', 'population', 'culture'] as string[],
  suggestion: ''
})

// 验证规则
const rules = {
  region_name: [
    { required: true, message: '请输入区域名称', trigger: 'blur' },
    { max: 100, message: '名称不能超过100个字符', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入区域描述', trigger: 'blur' }
  ]
}

// 默认树形配置
const defaultProps = {
  children: 'children',
  label: 'region_name'
}

// 计算属性
const mapsTreeData = computed(() => {
  const buildTree = (parentId: number | undefined = undefined): any[] => {
    return props.maps
      .filter(map => map.parent_region_id === parentId)
      .map(map => ({
        ...map,
        children: buildTree(map.id)
      }))
  }
  return buildTree()
})

// 方法
const resetForm = () => {
  formRef.value?.resetFields()
  Object.assign(form, {
    region_name: '',
    parent_region_id: undefined,
    description: '',
    level: 1,
    climate: '',
    terrain: '',
    resources: '',
    population: '',
    culture: ''
  })
  isEdit.value = false
  currentMapId.value = null
}

const submitForm = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    submitting.value = true

    const submitData = {
      ...form,
      parent_region_id: form.parent_region_id || undefined
    }

    if (isEdit.value && currentMapId.value) {
      // 更新
      emit('update', currentMapId.value, submitData)
    } else {
      // 创建
      emit('create', {
        worldview_id: props.worldviewId,
        ...submitData
      })
    }

    showCreateDialog.value = false
    ElMessage.success(isEdit.value ? '地图更新成功' : '地图创建成功')
  } catch (error) {
    console.error('表单提交失败:', error)
    if (error !== false) { // 不是验证错误
      ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
    }
  } finally {
    submitting.value = false
  }
}

const handleEdit = (map: WorldMap) => {
  isEdit.value = true
  currentMapId.value = map.id
  Object.assign(form, {
    region_name: map.region_name,
    parent_region_id: map.parent_region_id,
    description: map.description,
    level: map.level,
    climate: map.climate,
    terrain: map.terrain,
    resources: map.resources,
    population: map.population,
    culture: map.culture
  })
  showCreateDialog.value = true
}

const handleDelete = async (map: WorldMap) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除这个地图区域吗？如果有子区域也会被删除。',
      '确认删除',
      {
        type: 'warning'
      }
    )
    emit('delete', map.id)
    ElMessage.success('地图区域删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

const getLevelType = (level: number): string => {
  switch (level) {
    case 1:
      return 'success'
    case 2:
      return 'warning'
    case 3:
      return 'danger'
    default:
      return 'info'
  }
}

const generateMaps = () => {
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
.world-maps-section {
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

.maps-content {
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

.maps-tree {
  .map-node {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-right: 24px;
  }

  .map-info {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .map-name {
    font-weight: 500;
  }

  .map-actions {
    opacity: 0;
    transition: opacity 0.2s;
  }

  :deep(.el-tree-node__content:hover) {
    .map-actions {
      opacity: 1;
    }
  }
}
</style>