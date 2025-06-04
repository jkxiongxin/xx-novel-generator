<template>
  <div class="world-maps-section">
    <div class="section-header">
      <h3>世界地图</h3>
      <div class="header-actions">
        <el-button-group>
          <el-button 
            :type="viewMode === 'tree' ? 'primary' : 'default'" 
            @click="viewMode = 'tree'"
            size="small"
          >
            <el-icon><Grid /></el-icon>
            树形视图
          </el-button>
          <el-button 
            :type="viewMode === 'card' ? 'primary' : 'default'" 
            @click="viewMode = 'card'"
            size="small"
          >
            <el-icon><Menu /></el-icon>
            卡片视图
          </el-button>
        </el-button-group>
        <el-button type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>
          新建地图
        </el-button>
        <el-dropdown @command="handleGenerateCommand">
          <el-button :loading="generating">
            <el-icon><MagicStick /></el-icon>
            AI 生成地图
            <el-icon class="el-icon--right"><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="generate-root">生成顶级区域</el-dropdown-item>
              <el-dropdown-item command="generate-child" :disabled="!selectedParentRegion">
                生成子区域{{ selectedParentRegion ? `（${selectedParentRegion.region_name}）` : '' }}
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <el-skeleton :rows="3" animated />
    </div>

    <!-- 主体内容 -->
    <div v-else class="maps-content">
      <!-- 空状态 -->
      <div v-if="maps.length === 0" class="empty-state">
        <el-empty description="暂无世界地图，点击新建开始创建">
          <el-button type="primary" @click="showCreateDialog = true">
            <el-icon><Plus /></el-icon>
            新建世界地图
          </el-button>
        </el-empty>
      </div>

      <!-- 树形视图 -->
      <div v-else-if="viewMode === 'tree'" class="tree-view">
        <!-- 调试信息 -->
        <div v-if="debugMode" class="debug-info">
          <p>原始数据数量: {{ maps.length }}</p>
          <p>树形数据数量: {{ mapsTreeData.length }}</p>
          <details>
            <summary>查看详细数据</summary>
            <pre>{{ JSON.stringify(mapsTreeData, null, 2) }}</pre>
          </details>
        </div>

        <!-- 树形组件 -->
        <el-tree
          v-if="mapsTreeData.length > 0"
          :data="mapsTreeData"
          :props="treeProps"
          :expand-on-click-node="false"
          :default-expand-all="true"
          node-key="id"
          class="world-maps-tree"
        >
          <template #default="{ node, data }">
            <div class="tree-node-wrapper">
              <div class="tree-node-content">
                <div class="node-header">
                  <div class="node-title">
                    <span class="node-name">{{ data.region_name }}</span>
                    <el-tag :type="getLevelType(data.level)" size="small" class="level-tag">
                      {{ getLevelText(data.level) }}
                    </el-tag>
                  </div>
                  <div class="node-actions">
                    <el-button @click.stop="handleEdit(data)" type="primary" size="small" circle>
                      <el-icon><Edit /></el-icon>
                    </el-button>
                    <el-button @click.stop="generateChildMaps(data)" type="success" size="small" circle :loading="generating">
                      <el-icon><Plus /></el-icon>
                    </el-button>
                    <el-button @click.stop="handleDelete(data)" type="danger" size="small" circle>
                      <el-icon><Delete /></el-icon>
                    </el-button>
                  </div>
                </div>
                
                <div class="node-body">
                  <div v-if="data.description" class="node-description">
                    {{ data.description }}
                  </div>
                  
                  <div v-if="showNodeDetails(data)" class="node-details">
                    <div v-if="data.climate" class="detail-item">
                      <el-icon><Sunny /></el-icon>
                      <span class="detail-label">气候：</span>
                      <span class="detail-value">{{ data.climate }}</span>
                    </div>
                    <div v-if="data.terrain" class="detail-item">
                      <el-icon><Location /></el-icon>
                      <span class="detail-label">地形：</span>
                      <span class="detail-value">{{ data.terrain }}</span>
                    </div>
                    <div v-if="data.population" class="detail-item">
                      <el-icon><User /></el-icon>
                      <span class="detail-label">人口：</span>
                      <span class="detail-value">{{ data.population }}</span>
                    </div>
                    <div v-if="data.resources" class="detail-item">
                      <el-icon><Box /></el-icon>
                      <span class="detail-label">资源：</span>
                      <span class="detail-value">{{ data.resources }}</span>
                    </div>
                    <div v-if="data.culture" class="detail-item">
                      <el-icon><Star /></el-icon>
                      <span class="detail-label">文化：</span>
                      <span class="detail-value">{{ data.culture }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </template>
        </el-tree>

        <!-- 开发调试按钮 -->
        <div class="debug-controls">
          <el-button @click="debugMode = !debugMode" size="small" type="info">
            {{ debugMode ? '隐藏' : '显示' }}调试信息
          </el-button>
        </div>
      </div>

      <!-- 卡片视图 -->
      <div v-else class="card-view">
        <!-- 层级导航 -->
        <div class="level-navigation">
          <el-radio-group v-model="selectedLevel" @change="filterByLevel">
            <el-radio-button :value="0">全部</el-radio-button>
            <el-radio-button :value="1">大陆</el-radio-button>
            <el-radio-button :value="2">国家</el-radio-button>
            <el-radio-button :value="3">省份</el-radio-button>
            <el-radio-button :value="4">城市</el-radio-button>
            <el-radio-button :value="5">区域</el-radio-button>
          </el-radio-group>
        </div>

        <!-- 卡片网格 -->
        <div class="maps-grid">
          <el-row :gutter="16">
            <el-col v-for="map in filteredMaps" :key="map.id" :span="8">
              <el-card
                class="map-card"
                shadow="hover"
                :class="{ 'selected': selectedParentRegion?.id === map.id }"
                @click="selectParentRegion(map)"
              >
                <template #header>
                  <div class="card-header">
                    <span class="card-title">{{ map.region_name }}</span>
                    <div class="card-header-right">
                      <el-tag :type="getLevelType(map.level)" size="small">
                        {{ getLevelText(map.level) }}
                      </el-tag>
                      <el-icon v-if="selectedParentRegion?.id === map.id" class="selected-icon">
                        <Check />
                      </el-icon>
                    </div>
                  </div>
                  <!-- 父区域信息 -->
                  <div v-if="map.parent_region_id" class="parent-info">
                    <el-icon><ArrowUp /></el-icon>
                    <span>属于：{{ getParentName(map.parent_region_id) }}</span>
                  </div>
                </template>
                
                <div class="map-details">
                  <p v-if="map.description" class="map-description">
                    {{ map.description }}
                  </p>
                  <div class="map-meta-grid">
                    <div v-if="map.climate" class="meta-item">
                      <el-icon><Sunny /></el-icon>
                      <span>{{ map.climate }}</span>
                    </div>
                    <div v-if="map.terrain" class="meta-item">
                      <el-icon><Location /></el-icon>
                      <span>{{ map.terrain }}</span>
                    </div>
                    <div v-if="map.population" class="meta-item">
                      <el-icon><User /></el-icon>
                      <span>{{ map.population }}</span>
                    </div>
                    <div v-if="map.resources" class="meta-item">
                      <el-icon><Box /></el-icon>
                      <span>{{ map.resources }}</span>
                    </div>
                  </div>
                  
                  <!-- 子区域数量 -->
                  <div v-if="getChildrenCount(map.id) > 0" class="children-info">
                    <el-tag type="info" size="small">
                      包含 {{ getChildrenCount(map.id) }} 个子区域
                    </el-tag>
                  </div>
                </div>
                
                <template #footer>
                  <el-button-group>
                    <el-button size="small" type="primary" @click.stop="handleEdit(map)">
                      编辑
                    </el-button>
                    <el-button size="small" type="success" @click.stop="generateChildMaps(map)" :loading="generating">
                      添加子区域
                    </el-button>
                    <el-button size="small" type="danger" @click.stop="handleDelete(map)">
                      删除
                    </el-button>
                  </el-button-group>
                </template>
              </el-card>
            </el-col>
          </el-row>
        </div>
      </div>
    </div>

    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="isEdit ? '编辑地图区域' : '新建地图区域'"
      width="700px"
      @close="resetForm"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="120px"
      >
        <el-form-item label="区域名称" prop="region_name">
          <el-input v-model="form.region_name" placeholder="请输入区域名称" />
        </el-form-item>

        <el-form-item label="父级区域">
          <el-cascader
            v-model="form.parent_region_path"
            :options="parentRegionOptions"
            :props="cascaderProps"
            placeholder="选择父级区域（可选）"
            clearable
            :show-all-levels="false"
            @change="handleParentRegionChange"
          />
          <div class="form-help">选择父级区域会自动设置对应的层级</div>
        </el-form-item>

        <el-form-item label="区域等级" prop="level">
          <el-select v-model="form.level" placeholder="选择区域等级">
            <el-option :value="1" label="1级 - 大陆" />
            <el-option :value="2" label="2级 - 国家" />
            <el-option :value="3" label="3级 - 省份" />
            <el-option :value="4" label="4级 - 城市" />
            <el-option :value="5" label="5级 - 区域" />
          </el-select>
          <div class="form-help">层级决定了区域在地图中的位置关系</div>
        </el-form-item>

        <el-form-item label="区域描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="4"
            placeholder="请描述该区域的特点、历史等"
          />
        </el-form-item>

        <el-form-item label="气候特征">
          <el-input v-model="form.climate" placeholder="如：温带海洋性气候" />
        </el-form-item>

        <el-form-item label="地形地貌">
          <el-input v-model="form.terrain" placeholder="如：山地、平原、丘陵等" />
        </el-form-item>

        <el-form-item label="自然资源">
          <el-input
            v-model="form.resources"
            type="textarea"
            :rows="2"
            placeholder="列出该区域的主要资源"
          />
        </el-form-item>

        <el-form-item label="人口分布">
          <el-input v-model="form.population" placeholder="描述人口数量和分布情况" />
        </el-form-item>

        <el-form-item label="文化特色">
          <el-input
            v-model="form.culture"
            type="textarea"
            :rows="2"
            placeholder="描述该区域的文化特色"
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
      :title="selectedParentRegion ? `生成子区域 - ${selectedParentRegion.region_name}` : 'AI 生成世界地图'"
      width="650px"
    >
      <!-- 父区域信息显示 -->
      <div v-if="selectedParentRegion" class="parent-region-info">
        <el-alert
          :title="generateDialogTitle"
          type="info"
          :closable="false"
          show-icon
        >
          <template #default>
            <p><strong>父区域描述：</strong>{{ selectedParentRegion.description }}</p>
            <p v-if="selectedParentRegion.climate"><strong>气候：</strong>{{ selectedParentRegion.climate }}</p>
            <p v-if="selectedParentRegion.terrain"><strong>地形：</strong>{{ selectedParentRegion.terrain }}</p>
          </template>
        </el-alert>
      </div>

      <el-form :model="generateForm" label-width="120px" style="margin-top: 20px;">
        <el-form-item label="生成数量">
          <el-input-number
            v-model="generateForm.count"
            :min="1"
            :max="10"
            controls-position="right"
          />
          <div class="form-help">
            {{ selectedParentRegion ? '将生成该区域的子区域' : '将生成顶级地图区域' }}
          </div>
        </el-form-item>

        <!-- 自定义区域名称 -->
        <el-form-item label="区域名称">
          <div class="custom-names-container">
            <div v-for="(name, index) in generateForm.customNames" :key="index" class="custom-name-item">
              <el-input
                v-model="generateForm.customNames[index]"
                :placeholder="`区域 ${index + 1} 名称（可选）`"
                clearable
              >
                <template #prepend>{{ index + 1 }}.</template>
              </el-input>
              <el-button 
                v-if="generateForm.customNames.length > 1" 
                @click="removeCustomName(index)" 
                type="danger" 
                size="small" 
                circle
              >
                <el-icon><Close /></el-icon>
              </el-button>
            </div>
            <div class="custom-names-actions">
              <el-button 
                @click="addCustomName" 
                type="primary" 
                size="small" 
                :disabled="generateForm.customNames.length >= generateForm.count"
              >
                <el-icon><Plus /></el-icon>
                添加自定义名称
              </el-button>
              <el-button @click="clearCustomNames" size="small">
                清空全部
              </el-button>
            </div>
          </div>
          <div class="form-help">
            可为部分或全部区域指定名称，留空的区域将由AI自动命名
          </div>
        </el-form-item>

        <el-form-item label="生成内容">
          <el-checkbox-group v-model="generateForm.include">
            <el-checkbox label="climate">气候特征</el-checkbox>
            <el-checkbox label="terrain">地形地貌</el-checkbox>
            <el-checkbox label="resources">自然资源</el-checkbox>
            <el-checkbox label="population">人口分布</el-checkbox>
            <el-checkbox label="culture">文化特色</el-checkbox>
          </el-checkbox-group>
        </el-form-item>

        <el-form-item label="补充建议">
          <el-input
            v-model="generateForm.suggestion"
            type="textarea"
            :rows="3"
            :placeholder="selectedParentRegion ? `描述你希望 ${selectedParentRegion.region_name} 包含什么样的子区域` : '输入你对世界地图的期望和建议'"
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
import { ref, computed, reactive, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Plus, MagicStick, ArrowDown, Check, Edit, Delete, 
  Grid, Menu, Location, User, Box, Sunny, ArrowUp, Star, Close
} from '@element-plus/icons-vue'
import type { FormInstance } from 'element-plus'
import type { WorldMap } from '@/api/worldview'
import WorldviewAPI from '@/api/worldview'

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
  parent_region_path: number[]
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
const viewMode = ref<'tree' | 'card'>('tree')
const selectedLevel = ref(0)
const showCreateDialog = ref(false)
const showGenerateDialog = ref(false)
const submitting = ref(false)
const generating = ref(false)
const isEdit = ref(false)
const currentMapId = ref<number | null>(null)
const selectedParentRegion = ref<WorldMap | null>(null)
const debugMode = ref(false)

// 表单
const formRef = ref<FormInstance>()
const form = reactive<MapForm>({
  region_name: '',
  parent_region_id: undefined,
  parent_region_path: [],
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
  customNames: [''] as string[], // 自定义区域名称数组
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

// 树形配置
const treeProps = {
  children: 'children',
  label: 'region_name'
}

// 级联选择器配置
const cascaderProps = {
  value: 'id',
  label: 'region_name',
  children: 'children',
  checkStrictly: true
}

// 计算属性
const mapsTreeData = computed(() => {
  if (!props.maps || props.maps.length === 0) {
    return []
  }

  const buildTree = (parentId: number | null = null): any[] => {
    return props.maps
      .filter(map => {
        // 处理 parent_region_id 为 null 或 undefined 的情况
        if (parentId === null) {
          return map.parent_region_id === null || map.parent_region_id === undefined
        }
        return map.parent_region_id === parentId
      })
      .map(map => ({
        ...map,
        children: buildTree(map.id)
      }))
      .sort((a, b) => a.level - b.level || a.region_name.localeCompare(b.region_name))
  }
  
  return buildTree(null)
})

const parentRegionOptions = computed(() => {
  return mapsTreeData.value
})

const filteredMaps = computed(() => {
  if (selectedLevel.value === 0) {
    return props.maps.sort((a, b) => a.level - b.level || a.region_name.localeCompare(b.region_name))
  }
  return props.maps
    .filter(map => map.level === selectedLevel.value)
    .sort((a, b) => a.region_name.localeCompare(b.region_name))
})

const generateDialogTitle = computed(() => {
  if (selectedParentRegion.value) {
    return `将为「${selectedParentRegion.value.region_name}」生成子区域`
  }
  return 'AI 生成世界地图'
})

// 监听生成数量变化，自动调整自定义名称数组
watch(() => generateForm.count, (newCount) => {
  // 如果数量增加，补充空字符串
  while (generateForm.customNames.length < newCount) {
    generateForm.customNames.push('')
  }
  // 如果数量减少，移除多余的项
  if (generateForm.customNames.length > newCount) {
    generateForm.customNames = generateForm.customNames.slice(0, newCount)
  }
})

// 方法
const getLevelType = (level: number): string => {
  switch (level) {
    case 1: return 'success'   // 大陆
    case 2: return 'warning'   // 国家
    case 3: return 'danger'    // 省份
    case 4: return 'info'      // 城市
    case 5: return 'primary'   // 区域
    default: return 'info'
  }
}

const getLevelText = (level: number): string => {
  switch (level) {
    case 1: return '大陆'
    case 2: return '国家'
    case 3: return '省份'
    case 4: return '城市'
    case 5: return '区域'
    default: return `${level}级`
  }
}

const getParentName = (parentId: number): string => {
  const parent = props.maps.find(map => map.id === parentId)
  return parent ? parent.region_name : '未知'
}

const getChildrenCount = (parentId: number): number => {
  return props.maps.filter(map => map.parent_region_id === parentId).length
}

const showNodeDetails = (data: WorldMap): boolean => {
  return !!(data.terrain || data.population || data.resources || data.climate || data.culture)
}

const filterByLevel = () => {
  // 切换层级时的逻辑
}

// 自定义名称管理方法
const addCustomName = () => {
  if (generateForm.customNames.length < generateForm.count) {
    generateForm.customNames.push('')
  }
}

const removeCustomName = (index: number) => {
  if (generateForm.customNames.length > 1) {
    generateForm.customNames.splice(index, 1)
  }
}

const clearCustomNames = () => {
  generateForm.customNames = ['']
}

const handleParentRegionChange = (value: number[]) => {
  if (value && value.length > 0) {
    const parentId = value[value.length - 1]
    form.parent_region_id = parentId
    const parent = props.maps.find(map => map.id === parentId)
    if (parent) {
      form.level = parent.level + 1
    }
  } else {
    form.parent_region_id = undefined
    form.level = 1
  }
}

const resetForm = () => {
  formRef.value?.resetFields()
  Object.assign(form, {
    region_name: '',
    parent_region_id: undefined,
    parent_region_path: [],
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
      emit('update', currentMapId.value, submitData)
    } else {
      emit('create', {
        worldview_id: props.worldviewId,
        ...submitData
      })
    }

    showCreateDialog.value = false
    ElMessage.success(isEdit.value ? '地图更新成功' : '地图创建成功')
  } catch (error) {
    console.error('表单提交失败:', error)
    if (error !== false) {
      ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
    }
  } finally {
    submitting.value = false
  }
}

const handleEdit = (map: WorldMap) => {
  isEdit.value = true
  currentMapId.value = map.id
  
  // 构建父区域路径
  const buildParentPath = (mapId: number): number[] => {
    const currentMap = props.maps.find(m => m.id === mapId)
    if (!currentMap || !currentMap.parent_region_id) return []
    return [...buildParentPath(currentMap.parent_region_id), currentMap.parent_region_id]
  }

  Object.assign(form, {
    region_name: map.region_name,
    parent_region_id: map.parent_region_id,
    parent_region_path: map.parent_region_id ? buildParentPath(map.id) : [],
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
  const childrenCount = getChildrenCount(map.id)
  const confirmText = childrenCount > 0 
    ? `确定要删除区域「${map.region_name}」吗？这将同时删除其下的 ${childrenCount} 个子区域。`
    : `确定要删除区域「${map.region_name}」吗？`

  try {
    await ElMessageBox.confirm(confirmText, '确认删除', {
      type: 'warning'
    })
    emit('delete', map.id)
    ElMessage.success('地图区域删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 父区域选择
const selectParentRegion = (map: WorldMap) => {
  if (selectedParentRegion.value?.id === map.id) {
    selectedParentRegion.value = null
  } else {
    selectedParentRegion.value = map
  }
}

// 处理生成命令
const handleGenerateCommand = (command: string) => {
  if (command === 'generate-root') {
    generateMaps()
  } else if (command === 'generate-child') {
    if (selectedParentRegion.value) {
      generateChildMaps(selectedParentRegion.value)
    }
  }
}

// 生成顶级地图区域
const generateMaps = () => {
  selectedParentRegion.value = null
  // 重置自定义名称
  generateForm.customNames = ['']
  showGenerateDialog.value = true
}

// 生成子区域
const generateChildMaps = (parentMap: WorldMap) => {
  selectedParentRegion.value = parentMap
  // 重置自定义名称
  generateForm.customNames = ['']
  showGenerateDialog.value = true
}

const submitGenerate = async () => {
  try {
    generating.value = true
    
    // 过滤掉空的自定义名称
    const customNames = generateForm.customNames.filter(name => name.trim() !== '')
    
    const params = {
      parent_region_id: selectedParentRegion.value?.id,
      count: generateForm.count,
      custom_names: customNames.length > 0 ? customNames : undefined,
      include: generateForm.include,
      suggestion: generateForm.suggestion
    }
    
    const response = await WorldviewAPI.generateWorldMaps(props.worldviewId, params)
    const generatedMaps = response.generated_maps || []
    
    if (generatedMaps.length > 0) {
      await showGeneratedMapsPreview(generatedMaps, selectedParentRegion.value?.id)
    } else {
      ElMessage.warning('没有生成任何地图区域')
    }
  } catch (error) {
    console.error('生成失败:', error)
    ElMessage.error('生成失败')
  } finally {
    generating.value = false
    showGenerateDialog.value = false
  }
}

// 显示生成结果预览
const showGeneratedMapsPreview = async (generatedMaps: any[], parentRegionId?: number) => {
  try {
    const result = await ElMessageBox.confirm(
      `AI成功生成了 ${generatedMaps.length} 个地图区域，是否保存到世界观中？`,
      '生成完成',
      {
        type: 'success',
        confirmButtonText: '保存',
        cancelButtonText: '取消'
      }
    )
    
    if (result === 'confirm') {
      await saveGeneratedMaps(generatedMaps, parentRegionId)
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('预览失败:', error)
    }
  }
}

// 保存生成的地图
const saveGeneratedMaps = async (generatedMaps: any[], parentRegionId?: number) => {
  try {
    const saveData = {
      generated_maps: generatedMaps,
      parent_region_id: parentRegionId
    }
    
    const response = await WorldviewAPI.saveGeneratedMaps(props.worldviewId, saveData)
    ElMessage.success(response.message || '保存成功')
    emit('refresh')
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败')
  }
}
</script>

<style scoped lang="scss">
.world-maps-section {
  padding: 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
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
    align-items: center;
  }
}

.maps-content {
  flex: 1;
  background: white;
  border-radius: 8px;
  min-height: 200px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
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

.debug-info {
  background: #f5f7fa;
  padding: 16px;
  border-radius: 4px;
  margin-bottom: 16px;
  border: 1px solid #dcdfe6;
  
  details {
    margin-top: 8px;
    
    summary {
      cursor: pointer;
      color: #409eff;
      font-weight: 500;
      
      &:hover {
        text-decoration: underline;
      }
    }
  }
  
  pre {
    max-height: 300px;
    overflow-y: auto;
    background: white;
    padding: 12px;
    border-radius: 4px;
    font-size: 12px;
    margin-top: 8px;
    border: 1px solid #e4e7ed;
  }
}

.debug-controls {
  margin-top: 20px;
  text-align: center;
  padding: 16px;
  border-top: 1px solid #e4e7ed;
}

// 自定义名称容器样式
.custom-names-container {
  .custom-name-item {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 8px;
    
    .el-input {
      flex: 1;
    }
  }
  
  .custom-names-actions {
    display: flex;
    gap: 8px;
    margin-top: 12px;
    padding-top: 8px;
    border-top: 1px solid #f0f0f0;
  }
}

// 树形视图样式
.tree-view {
  flex: 1;
  padding: 20px;
  overflow-y: auto;

  .world-maps-tree {
    // 重置 Element Plus 树组件的默认样式
    :deep(.el-tree-node) {
      position: relative;
      
      .el-tree-node__content {
        position: relative;
        height: auto;
        min-height: 26px;
        padding: 0;
        background: transparent;
        
        &:hover {
          background: transparent;
        }
      }
      
      .el-tree-node__expand-icon {
        padding: 6px;
        color: #409eff;
        
        &.is-leaf {
          color: transparent;
        }
      }
      
      .el-tree-node__label {
        display: none; // 隐藏默认的标签，使用我们自定义的内容
      }
    }
    
    .tree-node-wrapper {
      width: 100%;
      margin-bottom: 16px;
    }
    
    .tree-node-content {
      background: #fafafa;
      border: 1px solid #e4e7ed;
      border-radius: 8px;
      padding: 16px;
      transition: all 0.3s ease;
      
      &:hover {
        background: #f5f7fa;
        border-color: #409eff;
        box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
      }
    }
    
    .node-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 12px;
      
      .node-title {
        display: flex;
        align-items: center;
        gap: 12px;
        flex: 1;
        
        .node-name {
          font-weight: 600;
          font-size: 16px;
          color: #303133;
        }
        
        .level-tag {
          flex-shrink: 0;
        }
      }
      
      .node-actions {
        display: flex;
        gap: 8px;
        opacity: 0;
        transition: opacity 0.3s ease;
      }
    }
    
    .tree-node-content:hover .node-actions {
      opacity: 1;
    }
    
    .node-body {
      .node-description {
        color: #606266;
        font-size: 14px;
        line-height: 1.6;
        margin-bottom: 12px;
        background: #f8f9fa;
        padding: 12px;
        border-radius: 4px;
        border-left: 4px solid #409eff;
      }
      
      .node-details {
        // 改为垂直布局，每个属性一行
        display: flex;
        flex-direction: column;
        gap: 8px;
        
        .detail-item {
          display: flex;
          align-items: flex-start;
          gap: 8px;
          padding: 10px 12px;
          background: white;
          border-radius: 4px;
          border: 1px solid #f0f0f0;
          
          .el-icon {
            font-size: 14px;
            color: #909399;
            margin-top: 2px;
            flex-shrink: 0;
          }
          
          .detail-label {
            font-weight: 500;
            color: #606266;
            font-size: 13px;
            flex-shrink: 0;
            min-width: 40px;
          }
          
          .detail-value {
            color: #303133;
            font-size: 13px;
            line-height: 1.5;
            word-break: break-word;
            flex: 1;
          }
        }
      }
    }
  }
}

// 卡片视图样式
.card-view {
  flex: 1;
  padding: 20px;
  overflow-y: auto;

  .level-navigation {
    margin-bottom: 20px;
    text-align: center;
  }

  .maps-grid {
    .map-card {
      margin-bottom: 16px;
      cursor: pointer;
      transition: all 0.3s;

      &.selected {
        border-color: #409eff;
        box-shadow: 0 2px 12px 0 rgba(64, 158, 255, 0.3);
      }

      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 20px 0 rgba(0, 0, 0, 0.1);
      }

      .card-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;

        .card-title {
          font-weight: 600;
          font-size: 16px;
        }

        .card-header-right {
          display: flex;
          align-items: center;
          gap: 8px;

          .selected-icon {
            color: #409eff;
            font-size: 18px;
          }
        }
      }

      .parent-info {
        display: flex;
        align-items: center;
        gap: 4px;
        margin-top: 8px;
        font-size: 12px;
        color: #909399;
      }

      .map-description {
        color: #606266;
        margin-bottom: 12px;
        line-height: 1.5;
      }

      .map-meta-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 8px;
        margin-bottom: 12px;

        .meta-item {
          display: flex;
          align-items: center;
          gap: 4px;
          font-size: 13px;
          color: #909399;

          .el-icon {
            font-size: 14px;
            flex-shrink: 0;
          }

          span {
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
          }
        }
      }

      .children-info {
        margin-top: 8px;
      }
    }
  }
}

.parent-region-info {
  margin-bottom: 20px;
}

.form-help {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}
</style>