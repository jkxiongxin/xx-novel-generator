<template>
  <div class="characters-workspace">
    <!-- 顶部工具栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <el-select
          v-model="selectedWorldviewId"
          placeholder="选择世界观"
          clearable
          @change="handleWorldviewChange"
        >
          <el-option
            v-for="worldview in worldviews"
            :key="worldview.id"
            :label="worldview.name"
            :value="worldview.id"
          />
        </el-select>
        <el-button type="primary" @click="showNewWorldviewDialog = true">
          新建世界观
        </el-button>
      </div>
      <div class="toolbar-right">
        <el-button type="success" @click="showCreateDialog = true">
          新建角色
        </el-button>
        <el-button @click="showTemplateDialog = true">
          从角色库选择
        </el-button>
        <el-button type="primary" @click="showGenerateDialog = true">
          AI生成角色
        </el-button>
      </div>
    </div>

    <!-- 主体内容 -->
    <div class="main-content">
      <!-- 左侧角色列表 -->
      <div class="character-list">
        <div class="list-header">
          <h3>角色列表</h3>
          <div class="filter-buttons">
            <el-button
              v-for="type in characterTypes"
              :key="type.value"
              :type="activeFilter === type.value ? 'primary' : 'default'"
              size="small"
              @click="handleFilterChange(type.value)"
            >
              {{ type.label }}
            </el-button>
          </div>
        </div>
        
        <div class="character-items">
          <div
            v-for="character in filteredCharacters"
            :key="character.id"
            class="character-item"
            :class="{ active: selectedCharacter?.id === character.id }"
            @click="selectCharacter(character)"
          >
            <div class="character-name">{{ character.name }}</div>
            <div class="character-meta">
              <el-tag :type="getCharacterTypeColor(character.character_type)" size="small">
                {{ getCharacterTypeLabel(character.character_type) }}
              </el-tag>
              <el-tag v-if="character.gender" size="small">{{ character.gender }}</el-tag>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧角色详情 -->
      <div class="character-detail">
        <div v-if="selectedCharacter" class="detail-content">
          <div class="detail-header">
            <h2>{{ selectedCharacter.name }}</h2>
            <div class="actions">
              <el-button @click="editCharacter">编辑</el-button>
              <el-button @click="generateSummary">生成总结</el-button>
              <el-button type="danger" @click="deleteCharacter">删除</el-button>
            </div>
          </div>

          <div class="detail-body">
            <el-descriptions :column="2" border>
              <el-descriptions-item label="角色类型">
                <el-tag :type="getCharacterTypeColor(selectedCharacter.character_type)">
                  {{ getCharacterTypeLabel(selectedCharacter.character_type) }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="性别">{{ selectedCharacter.gender }}</el-descriptions-item>
              <el-descriptions-item label="标签" :span="2">
                <el-tag
                  v-for="tag in selectedCharacter.tags"
                  :key="tag"
                  type="info"
                  size="small"
                  style="margin-right: 8px;"
                >
                  {{ tag }}
                </el-tag>
              </el-descriptions-item>
            </el-descriptions>

            <div class="section">
              <h4>性格描述</h4>
              <p>{{ selectedCharacter.personality || '暂无描述' }}</p>
            </div>

            <div class="section">
              <h4>角色描述</h4>
              <p>{{ selectedCharacter.description || '暂无描述' }}</p>
            </div>

            <div class="section">
              <h4>角色能力</h4>
              <p>{{ selectedCharacter.abilities || '暂无描述' }}</p>
            </div>

            <div v-if="selectedCharacter.power_system" class="section">
              <h4>力量体系</h4>
              <p>{{ selectedCharacter.power_system }}</p>
            </div>

            <div v-if="selectedCharacter.original_world" class="section">
              <h4>原生世界</h4>
              <p>{{ selectedCharacter.original_world }}</p>
            </div>
          </div>
        </div>
        
        <div v-else class="empty-state">
          <el-empty description="请选择一个角色查看详情" />
        </div>
      </div>
    </div>

    <!-- 创建/编辑角色对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingCharacter ? '编辑角色' : '创建角色'"
      width="600px"
      @close="resetCreateForm"
    >
      <el-form ref="createFormRef" :model="createForm" :rules="createRules" label-width="100px">
        <el-form-item label="角色名称" prop="name">
          <el-input v-model="createForm.name" placeholder="请输入角色名称" />
        </el-form-item>
        
        <el-form-item label="角色类型" prop="character_type">
          <el-select v-model="createForm.character_type" placeholder="请选择角色类型">
            <el-option
              v-for="type in characterTypes"
              :key="type.value"
              :label="type.label"
              :value="type.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="性别" prop="gender">
          <el-radio-group v-model="createForm.gender">
            <el-radio label="male">男性</el-radio>
            <el-radio label="female">女性</el-radio>
            <el-radio label="unknown">未知</el-radio>
            <el-radio label="other">其他</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="所属世界观">
          <el-select v-model="createForm.worldview_id" placeholder="请选择世界观">
            <el-option
              v-for="worldview in worldviews"
              :key="worldview.id"
              :label="worldview.name"
              :value="worldview.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="角色标签">
          <el-input
            v-model="tagInput"
            placeholder="输入标签后按回车添加"
            @keyup.enter="addTag"
          />
          <div class="tags-display">
            <el-tag
              v-for="tag in createForm.tags"
              :key="tag"
              closable
              @close="removeTag(tag)"
              style="margin: 4px;"
            >
              {{ tag }}
            </el-tag>
          </div>
        </el-form-item>

        <el-form-item label="性格描述">
          <el-input
            v-model="createForm.personality"
            type="textarea"
            :rows="3"
            placeholder="请描述角色的性格特征"
          />
        </el-form-item>

        <el-form-item label="角色描述">
          <el-input
            v-model="createForm.description"
            type="textarea"
            :rows="3"
            placeholder="请描述角色的外貌、背景等"
          />
        </el-form-item>

        <el-form-item label="角色能力">
          <el-input
            v-model="createForm.abilities"
            type="textarea"
            :rows="3"
            placeholder="请描述角色的能力和技能"
          />
        </el-form-item>

        <el-form-item label="力量体系">
          <el-input v-model="createForm.power_system" placeholder="如：修仙体系、魔法体系等" />
        </el-form-item>

        <el-form-item label="原生世界">
          <el-input v-model="createForm.original_world" placeholder="角色的原生世界名称" />
        </el-form-item>

        <el-form-item>
          <el-checkbox v-model="createForm.is_template">设为角色模板</el-checkbox>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="submitCreateForm">
          {{ editingCharacter ? '更新' : '创建' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 角色模板选择对话框 -->
    <el-dialog v-model="showTemplateDialog" title="角色模板库" width="80%">
      <div class="template-filters">
        <el-form :inline="true">
          <el-form-item label="角色名称">
            <el-input v-model="templateFilters.name" placeholder="搜索角色名称" />
          </el-form-item>
          <el-form-item label="性别">
            <el-select v-model="templateFilters.gender" placeholder="选择性别" clearable>
              <el-option label="男性" value="male" />
              <el-option label="女性" value="female" />
              <el-option label="未知" value="unknown" />
              <el-option label="其他" value="other" />
            </el-select>
          </el-form-item>
          <el-form-item label="角色类型">
            <el-select v-model="templateFilters.character_type" placeholder="选择角色类型" clearable>
              <el-option
                v-for="type in characterTypes"
                :key="type.value"
                :label="type.label"
                :value="type.value"
              />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="searchTemplates">搜索</el-button>
            <el-button @click="resetTemplateFilters">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <el-table
        ref="templateTableRef"
        :data="templates"
        @selection-change="handleTemplateSelection"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="name" label="角色名称" width="120" />
        <el-table-column prop="character_type" label="角色类型" width="100">
          <template #default="scope">
            <el-tag :type="getCharacterTypeColor(scope.row.character_type)" size="small">
              {{ getCharacterTypeLabel(scope.row.character_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="gender" label="性别" width="80" />
        <el-table-column prop="description" label="描述" show-overflow-tooltip />
        <el-table-column prop="tags" label="标签" width="200">
          <template #default="scope">
            <el-tag
              v-for="tag in scope.row.tags?.slice(0, 3)"
              :key="tag"
              size="small"
              style="margin-right: 4px;"
            >
              {{ tag }}
            </el-tag>
            <span v-if="scope.row.tags?.length > 3">...</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="scope">
            <el-button size="small" @click="addSingleTemplate(scope.row)">添加</el-button>
          </template>
        </el-table-column>
      </el-table>

      <template #footer>
        <el-button @click="showTemplateDialog = false">关闭</el-button>
        <el-button type="primary" @click="batchAddTemplates">批量添加选中</el-button>
      </template>
    </el-dialog>

    <!-- 新建世界观对话框 -->
    <el-dialog v-model="showNewWorldviewDialog" title="新建世界观" width="500px">
      <el-form ref="worldviewFormRef" :model="worldviewForm" :rules="worldviewRules" label-width="100px">
        <el-form-item label="世界名称" prop="name">
          <el-input v-model="worldviewForm.name" placeholder="请输入世界名称" />
        </el-form-item>
        <el-form-item label="世界描述">
          <el-input
            v-model="worldviewForm.description"
            type="textarea"
            :rows="3"
            placeholder="请描述这个世界的特征"
          />
        </el-form-item>
        <el-form-item>
          <el-checkbox v-model="worldviewForm.is_primary">设为主世界</el-checkbox>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showNewWorldviewDialog = false">取消</el-button>
        <el-button type="primary" @click="submitWorldviewForm">创建</el-button>
      </template>
    </el-dialog>

    <!-- AI生成角色对话框 -->
    <el-dialog v-model="showGenerateDialog" title="AI生成角色" width="600px">
      <el-form ref="generateFormRef" :model="generateForm" :rules="generateRules" label-width="120px">
        <el-form-item label="角色类型">
          <el-select v-model="generateForm.character_type" placeholder="选择角色类型">
            <el-option
              v-for="type in characterTypes.filter(t => t.value !== 'all')"
              :key="type.value"
              :label="type.label"
              :value="type.value"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="生成数量" prop="character_count">
          <el-input-number v-model="generateForm.character_count" :min="1" :max="5" />
        </el-form-item>
        
        <el-form-item label="所属世界观">
          <el-select v-model="generateForm.worldview_id" placeholder="选择世界观">
            <el-option
              v-for="worldview in worldviews"
              :key="worldview.id"
              :label="worldview.name"
              :value="worldview.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item>
          <el-checkbox v-model="generateForm.include_worldview">使用世界观信息</el-checkbox>
        </el-form-item>
        
        <el-form-item label="生成建议">
          <el-input
            v-model="generateForm.user_suggestion"
            type="textarea"
            :rows="3"
            placeholder="请描述您希望生成的角色特征或要求"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showGenerateDialog = false">取消</el-button>
        <el-button type="primary" @click="submitGenerateForm" :loading="generating">
          {{ generating ? '生成中...' : '开始生成' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRoute } from 'vue-router'
import * as charactersApi from '@/api/characters'
import * as outlineApi from '@/api/outline'

// 获取路由参数
const route = useRoute()
const novelId = computed(() => parseInt(route.params.novelId))

// 数据状态
const characters = ref([])
const worldviews = ref([])
const templates = ref([])
const selectedCharacter = ref(null)
const selectedWorldviewId = ref(null)
const activeFilter = ref('all')
const loading = ref(false)

// 对话框状态
const showCreateDialog = ref(false)
const showTemplateDialog = ref(false)
const showNewWorldviewDialog = ref(false)
const showGenerateDialog = ref(false)
const editingCharacter = ref(null)
const generating = ref(false)

// 表单数据
const createForm = reactive({
  name: '',
  character_type: 'supporting',
  gender: 'unknown',
  worldview_id: null,
  tags: [],
  personality: '',
  description: '',
  abilities: '',
  power_system: '',
  original_world: '',
  is_template: false
})

const worldviewForm = reactive({
  name: '',
  description: '',
  is_primary: false
})

const templateFilters = reactive({
  name: '',
  gender: '',
  character_type: ''
})

const generateForm = reactive({
  character_type: '',
  character_count: 2,
  worldview_id: null,
  include_worldview: true,
  user_suggestion: ''
})

// 标签输入
const tagInput = ref('')
const selectedTemplates = ref([])

// 角色类型选项
const characterTypes = [
  { value: 'all', label: '全部' },
  { value: 'protagonist', label: '主角' },
  { value: 'supporting', label: '配角' },
  { value: 'antagonist', label: '反派' },
  { value: 'minor', label: '次要角色' },
  { value: 'passerby', label: '路人' }
]

// 表单验证规则
const createRules = {
  name: [{ required: true, message: '请输入角色名称', trigger: 'blur' }],
  character_type: [{ required: true, message: '请选择角色类型', trigger: 'change' }]
}

const worldviewRules = {
  name: [{ required: true, message: '请输入世界名称', trigger: 'blur' }]
}

const generateRules = {
  character_count: [{ required: true, message: '请输入生成数量', trigger: 'blur' }]
}

// 计算属性
const filteredCharacters = computed(() => {
  if (activeFilter.value === 'all') {
    return characters.value
  }
  return characters.value.filter(character => character.character_type === activeFilter.value)
})

// 方法
const loadCharacters = async () => {
  try {
    loading.value = true
    const data = await charactersApi.getCharacters({
      novel_id: novelId.value
    })
    characters.value = data.items || []
  } catch (error) {
    console.error('加载角色列表失败:', error)
    ElMessage.error('加载角色列表失败')
  } finally {
    loading.value = false
  }
}

const loadWorldviews = async () => {
  try {
    const response = await fetch(`/api/v1/worldview/novel/${novelId.value}`)
    const data = await response.json()
    if (data.success !== false) {
      worldviews.value = data.items || []
    }
  } catch (error) {
    console.error('加载世界观列表失败:', error)
  }
}
const loadTemplates = async () => {
  try {
    const params = {
      page: 1,
      page_size: 50
    }
    
    if (templateFilters.name) params.search = templateFilters.name
    if (templateFilters.gender) params.gender = templateFilters.gender
    if (templateFilters.character_type) params.character_type = templateFilters.character_type
    
    const data = await charactersApi.getCharacterTemplates(params)
    templates.value = data.items || []
  } catch (error) {
    console.error('加载角色模板失败:', error)
    ElMessage.error('加载角色模板失败')
  }
}

const selectCharacter = (character) => {
  selectedCharacter.value = character
}

const handleFilterChange = (filter) => {
  activeFilter.value = filter
}

const handleWorldviewChange = (worldviewId) => {
  selectedWorldviewId.value = worldviewId
  // 这里可以根据世界观过滤角色
}

const getCharacterTypeColor = (type) => {
  const colors = {
    protagonist: 'danger',
    supporting: 'primary',
    antagonist: 'warning',
    minor: 'info',
    passerby: 'success'
  }
  return colors[type] || 'info'
}

const getCharacterTypeLabel = (type) => {
  const typeItem = characterTypes.find(item => item.value === type)
  return typeItem ? typeItem.label : type
}

const editCharacter = () => {
  if (!selectedCharacter.value) return
  
  editingCharacter.value = selectedCharacter.value
  Object.assign(createForm, {
    name: selectedCharacter.value.name,
    character_type: selectedCharacter.value.character_type,
    gender: selectedCharacter.value.gender,
    worldview_id: selectedCharacter.value.worldview_id,
    tags: [...(selectedCharacter.value.tags || [])],
    personality: selectedCharacter.value.personality || '',
    description: selectedCharacter.value.description || '',
    abilities: selectedCharacter.value.abilities || '',
    power_system: selectedCharacter.value.power_system || '',
    original_world: selectedCharacter.value.original_world || '',
    is_template: selectedCharacter.value.is_template || false
  })
  showCreateDialog.value = true
}

const deleteCharacter = async () => {
  if (!selectedCharacter.value) return
  
  try {
    await ElMessageBox.confirm('确定要删除这个角色吗？', '确认删除', {
      type: 'warning'
    })
    
    await charactersApi.deleteCharacter(selectedCharacter.value.id)
    ElMessage.success('角色删除成功')
    selectedCharacter.value = null
    await loadCharacters()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除角色失败:', error)
      ElMessage.error('删除角色失败')
    }
  }
}

const generateSummary = () => {
  ElMessage.info('AI总结功能开发中...')
}

const addTag = () => {
  if (tagInput.value && !createForm.tags.includes(tagInput.value)) {
    createForm.tags.push(tagInput.value)
    tagInput.value = ''
  }
}

const removeTag = (tag) => {
  const index = createForm.tags.indexOf(tag)
  if (index > -1) {
    createForm.tags.splice(index, 1)
  }
}

const resetCreateForm = () => {
  editingCharacter.value = null
  Object.assign(createForm, {
    name: '',
    character_type: 'supporting',
    gender: 'unknown',
    worldview_id: null,
    tags: [],
    personality: '',
    description: '',
    abilities: '',
    power_system: '',
    original_world: '',
    is_template: false
  })
  tagInput.value = ''
}

const submitCreateForm = async () => {
  try {
    const requestData = { ...createForm }
    if (!editingCharacter.value) {
      requestData.novel_id = novelId.value
    }
    
    let updatedCharacter
    if (editingCharacter.value) {
      updatedCharacter = await charactersApi.updateCharacter(editingCharacter.value.id, requestData)
      ElMessage.success('角色更新成功')
      selectedCharacter.value = updatedCharacter
    } else {
      await charactersApi.createCharacter(requestData)
      ElMessage.success('角色创建成功')
    }
    
    showCreateDialog.value = false
    await loadCharacters()
  } catch (error) {
    console.error('角色操作失败:', error)
    ElMessage.error('角色操作失败')
  }
}

const submitWorldviewForm = async () => {
  try {
    const response = await fetch('/api/v1/worldview/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        ...worldviewForm,
        novel_id: novelId.value
      })
    })
    
    if (response.ok) {
      ElMessage.success('世界观创建成功')
      showNewWorldviewDialog.value = false
      await loadWorldviews()
      Object.assign(worldviewForm, {
        name: '',
        description: '',
        is_primary: false
      })
    } else {
      throw new Error('创建失败')
    }
  } catch (error) {
    console.error('创建世界观失败:', error)
    ElMessage.error('创建世界观失败')
  }
}

const searchTemplates = () => {
  loadTemplates()
}

const resetTemplateFilters = () => {
  Object.assign(templateFilters, {
    name: '',
    gender: '',
    character_type: ''
  })
  loadTemplates()
}

const handleTemplateSelection = (selection) => {
  selectedTemplates.value = selection
}

const addSingleTemplate = async (template) => {
  try {
    await charactersApi.batchAddCharacters({
      character_ids: [template.id],
      novel_id: novelId.value
    })
    ElMessage.success('角色添加成功')
    await loadCharacters()
  } catch (error) {
    console.error('添加角色失败:', error)
    ElMessage.error('添加角色失败')
  }
}

const batchAddTemplates = async () => {
  if (selectedTemplates.value.length === 0) {
    ElMessage.warning('请选择要添加的角色')
    return
  }
  
  try {
    const result = await charactersApi.batchAddCharacters({
      character_ids: selectedTemplates.value.map(t => t.id),
      novel_id: novelId.value
    })
    ElMessage.success(`成功添加 ${result.added_count} 个角色`)
    showTemplateDialog.value = false
    await loadCharacters()
  } catch (error) {
    console.error('批量添加角色失败:', error)
    ElMessage.error('批量添加角色失败')
  }
}

const submitGenerateForm = async () => {
  try {
    generating.value = true
    const result = await charactersApi.generateCharacters({
      novel_id: novelId.value,
      character_type: generateForm.character_type,
      character_count: generateForm.character_count,
      user_suggestion: generateForm.user_suggestion,
      include_worldview: generateForm.include_worldview,
      worldview_id: generateForm.worldview_id
    })
    
    if (result.success) {
      ElMessage.success(`成功生成 ${result.total_generated} 个角色`)
      showGenerateDialog.value = false
      await loadCharacters()
      
      // 重置表单
      Object.assign(generateForm, {
        character_type: '',
        character_count: 2,
        worldview_id: null,
        include_worldview: true,
        user_suggestion: ''
      })
    } else {
      ElMessage.error(result.message || 'AI生成失败')
    }
  } catch (error) {
    console.error('AI生成角色失败:', error)
    ElMessage.error('AI生成角色失败')
  } finally {
    generating.value = false
  }
}

// 生命周期
onMounted(async () => {
  await Promise.all([
    loadCharacters(),
    loadWorldviews(),
    loadTemplates()
  ])
})

// 监听对话框状态
watch(showTemplateDialog, (newVal) => {
  if (newVal) {
    loadTemplates()
  }
})
</script>

<style scoped>
.characters-workspace {
  padding: 20px;
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 15px;
  background: #f5f5f5;
  border-radius: 8px;
}

.toolbar-left {
  display: flex;
  gap: 12px;
  align-items: center;
}

.toolbar-right {
  display: flex;
  gap: 12px;
}

.main-content {
  flex: 1;
  display: flex;
  gap: 20px;
  overflow: hidden;
}

.character-list {
  width: 300px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
}

.list-header {
  padding: 15px;
  border-bottom: 1px solid #e4e7ed;
  background: #fafafa;
}

.list-header h3 {
  margin: 0 0 10px 0;
  font-size: 16px;
  font-weight: 500;
}

.filter-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.character-items {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
}

.character-item {
  padding: 12px;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.character-item:hover {
  border-color: #409eff;
  background: #f0f9ff;
}

.character-item.active {
  border-color: #409eff;
  background: #409eff;
  color: white;
}

.character-name {
  font-weight: 500;
  margin-bottom: 6px;
}

.character-meta {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.character-detail {
  flex: 1;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
}

.detail-content {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #e4e7ed;
  background: #fafafa;
}

.detail-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 500;
}

.actions {
  display: flex;
  gap: 8px;
}

.detail-body {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.section {
  margin-bottom: 20px;
}

.section h4 {
  margin: 0 0 8px 0;
  font-size: 14px;
  font-weight: 500;
  color: #606266;
}

.section p {
  margin: 0;
  line-height: 1.6;
  color: #303133;
}

.empty-state {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.tags-display {
  margin-top: 8px;
}

.template-filters {
  margin-bottom: 20px;
  padding: 15px;
  background: #f5f5f5;
  border-radius: 6px;
}
</style>