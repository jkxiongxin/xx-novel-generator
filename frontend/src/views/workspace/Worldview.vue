<template>
  <div class="worldview-workspace">
    <!-- 顶部工具栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <el-select
          v-model="selectedWorldviewId"
          placeholder="选择世界观"
          @change="handleWorldviewChange"
        >
          <el-option
            v-for="worldview in worldviews"
            :key="worldview.id"
            :label="worldview.name"
            :value="worldview.id"
          >
            <span>{{ worldview.name }}</span>
            <el-tag v-if="worldview.is_primary" type="success" size="small" style="margin-left: 8px;">
              主世界
            </el-tag>
          </el-option>
        </el-select>
      </div>
      <div class="toolbar-right">
        <el-button type="primary" @click="showCreateWorldviewDialog = true">
          新建世界观
        </el-button>
        <el-button @click="generateWorldview">
          AI生成世界观
        </el-button>
      </div>
    </div>

    <!-- 主体内容 -->
    <div v-if="currentWorldview" class="main-content">
      <!-- 世界观标签栏 -->
      <el-tabs v-model="activeTab" type="card" class="worldview-tabs">
        <el-tab-pane label="世界概况" name="overview">
          <WorldviewOverview
            :worldview="currentWorldview"
            @update="handleUpdateWorldview"
            @delete="handleDeleteWorldview"
          />
        </el-tab-pane>
        
        <el-tab-pane label="世界地图" name="maps">
          <WorldMapsSection
            :worldview-id="currentWorldview.id"
            :maps="worldMaps"
            @create="handleCreateWorldMap"
            @update="handleUpdateWorldMap"
            @delete="handleDeleteWorldMap"
            @refresh="loadWorldMaps"
          />
        </el-tab-pane>
        
        <el-tab-pane label="修炼体系" name="cultivation">
          <CultivationSection
            :worldview-id="currentWorldview.id"
            :systems="cultivationSystems"
            @create="handleCreateCultivation"
            @update="handleUpdateCultivation"
            @delete="handleDeleteCultivation"
            @refresh="loadCultivationSystems"
          />
        </el-tab-pane>
        
        <el-tab-pane label="历史事件" name="history">
          <HistorySection
            :worldview-id="currentWorldview.id"
            :histories="histories"
            @create="handleCreateHistory"
            @update="handleUpdateHistory"
            @delete="handleDeleteHistory"
            @refresh="loadHistories"
          />
        </el-tab-pane>
        
        <el-tab-pane label="阵营势力" name="factions">
          <FactionsSection
            :worldview-id="currentWorldview.id"
            :factions="factions"
            @create="handleCreateFaction"
            @update="handleUpdateFaction"
            @delete="handleDeleteFaction"
            @refresh="loadFactions"
          />
        </el-tab-pane>
      </el-tabs>
    </div>
    
    <!-- 空状态 -->
    <div v-else class="empty-state">
      <el-empty description="请先创建或选择一个世界观">
        <el-button type="primary" @click="showCreateWorldviewDialog = true">
          创建世界观
        </el-button>
      </el-empty>
    </div>

    <!-- 创建世界观对话框 -->
    <el-dialog
      v-model="showCreateWorldviewDialog"
      title="创建世界观"
      width="600px"
      @close="resetWorldviewForm"
    >
      <el-form ref="worldviewFormRef" :model="worldviewForm" :rules="worldviewRules" label-width="100px">
        <el-form-item label="世界名称" prop="name">
          <el-input v-model="worldviewForm.name" placeholder="请输入世界名称" />
        </el-form-item>
        
        <el-form-item label="世界描述">
          <el-input
            v-model="worldviewForm.description"
            type="textarea"
            :rows="4"
            placeholder="请描述这个世界的特征、背景等"
          />
        </el-form-item>
        
        <el-form-item>
          <el-checkbox v-model="worldviewForm.is_primary">设为主世界</el-checkbox>
          <div class="form-help">主世界将作为小说的主要背景世界</div>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showCreateWorldviewDialog = false">取消</el-button>
        <el-button type="primary" @click="submitWorldviewForm">创建</el-button>
      </template>
    </el-dialog>

    <!-- AI生成世界观对话框 -->
    <el-dialog
      v-model="showGenerateDialog"
      title="AI生成世界观"
      width="700px"
    >
      <el-form ref="generateFormRef" :model="generateForm" label-width="120px">
        <el-form-item label="世界观名称">
          <el-input v-model="generateForm.worldview_name" placeholder="留空将自动生成" />
        </el-form-item>
        
        <el-form-item label="生成内容">
          <el-checkbox-group v-model="generateForm.generation_types">
            <el-checkbox label="map">世界地图</el-checkbox>
            <el-checkbox label="cultivation">修炼体系</el-checkbox>
            <el-checkbox label="history">历史事件</el-checkbox>
            <el-checkbox label="faction">阵营势力</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        
        <el-form-item label="用户建议">
          <el-input
            v-model="generateForm.user_suggestion"
            type="textarea"
            :rows="3"
            placeholder="描述您希望生成的世界观类型、风格等..."
          />
        </el-form-item>
        
        <el-form-item>
          <el-checkbox v-model="generateForm.include_novel_idea">包含小说创意</el-checkbox>
        </el-form-item>
        
        <el-form-item>
          <el-checkbox v-model="generateForm.include_novel_settings">包含小说设定</el-checkbox>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showGenerateDialog = false">取消</el-button>
        <el-button type="primary" @click="submitGenerateForm" :loading="generating">
          开始生成
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRoute } from 'vue-router'
import apiClient from '@/api/index'
import WorldviewOverview from '@/components/worldview/WorldviewOverview.vue'
import WorldMapsSection from '@/components/worldview/WorldMapsSection.vue'
import CultivationSection from '@/components/worldview/CultivationSection.vue'
import HistorySection from '@/components/worldview/HistorySection.vue'
import FactionsSection from '@/components/worldview/FactionsSection.vue'

// 获取路由参数
const route = useRoute()
const novelId = computed(() => parseInt(route.params.novelId))

// 数据状态
const worldviews = ref([])
const selectedWorldviewId = ref(null)
const currentWorldview = ref(null)
const activeTab = ref('overview')
const loading = ref(false)

// 各类型数据
const worldMaps = ref([])
const cultivationSystems = ref([])
const histories = ref([])
const factions = ref([])

// 对话框状态
const showCreateWorldviewDialog = ref(false)
const showGenerateDialog = ref(false)
const generating = ref(false)

// 表单数据
const worldviewForm = reactive({
  name: '',
  description: '',
  is_primary: false
})

const generateForm = reactive({
  worldview_name: '',
  generation_types: ['map', 'cultivation', 'history', 'faction'],
  user_suggestion: '',
  include_novel_idea: true,
  include_novel_settings: true
})

// 表单验证规则
const worldviewRules = {
  name: [{ required: true, message: '请输入世界名称', trigger: 'blur' }]
}

// 方法
const loadWorldviews = async () => {
  try {
    loading.value = true
    const response = await apiClient.get(`/worldview/novel/${novelId.value}`)
    const data = response.data
    if (data.success !== false) {
      worldviews.value = data.items || []
      
      // 如果没有选中的世界观，自动选择第一个（优先主世界）
      if (!selectedWorldviewId.value && worldviews.value.length > 0) {
        const primaryWorld = worldviews.value.find(w => w.is_primary)
        selectedWorldviewId.value = primaryWorld?.id || worldviews.value[0].id
      }
    }
  } catch (error) {
    console.error('加载世界观列表失败:', error)
    ElMessage.error('加载世界观列表失败')
  } finally {
    loading.value = false
  }
}

const loadWorldMaps = async () => {
  if (!selectedWorldviewId.value) return
  
  try {
    const response = await apiClient.get(`/worldview/${selectedWorldviewId.value}/maps`)
    const data = response.data
    if (data.success !== false) {
      worldMaps.value = data.items || []
    }
  } catch (error) {
    console.error('加载世界地图失败:', error)
  }
}

const loadCultivationSystems = async () => {
  if (!selectedWorldviewId.value) return
  
  try {
    const response = await apiClient.get(`/worldview/${selectedWorldviewId.value}/cultivation`)
    const data = response.data
    if (data.success !== false) {
      cultivationSystems.value = data.items || []
    }
  } catch (error) {
    console.error('加载修炼体系失败:', error)
  }
}

const loadHistories = async () => {
  if (!selectedWorldviewId.value) return
  
  try {
    const response = await apiClient.get(`/worldview/${selectedWorldviewId.value}/history`)
    const data = response.data
    if (data.success !== false) {
      histories.value = data.items || []
    }
  } catch (error) {
    console.error('加载历史事件失败:', error)
  }
}

const loadFactions = async () => {
  if (!selectedWorldviewId.value) return
  
  try {
    const response = await apiClient.get(`/worldview/${selectedWorldviewId.value}/factions`)
    const data = response.data
    if (data.success !== false) {
      factions.value = data.items || []
    }
  } catch (error) {
    console.error('加载阵营势力失败:', error)
  }
}

const loadWorldviewDetails = async () => {
  await Promise.all([
    loadWorldMaps(),
    loadCultivationSystems(),
    loadHistories(),
    loadFactions()
  ])
}

const handleWorldviewChange = (worldviewId) => {
  selectedWorldviewId.value = worldviewId
  currentWorldview.value = worldviews.value.find(w => w.id === worldviewId)
  if (currentWorldview.value) {
    loadWorldviewDetails()
  }
}

const handleUpdateWorldview = async (updatedData) => {
  try {
    const response = await apiClient.put(`/worldview/${currentWorldview.value.id}`, updatedData)
    
    currentWorldview.value = response.data
    await loadWorldviews()
    ElMessage.success('世界观更新成功')
  } catch (error) {
    console.error('更新世界观失败:', error)
    ElMessage.error('更新世界观失败')
  }
}

const handleDeleteWorldview = async () => {
  if (!currentWorldview.value) return
  
  try {
    await ElMessageBox.confirm('确定要删除这个世界观吗？这将删除所有相关数据。', '确认删除', {
      type: 'warning'
    })
    
    const response = await apiClient.delete(`/worldview/${currentWorldview.value.id}`)
    
    ElMessage.success('世界观删除成功')
    currentWorldview.value = null
    selectedWorldviewId.value = null
    await loadWorldviews()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除世界观失败:', error)
      ElMessage.error('删除世界观失败')
    }
  }
}

const handleCreateWorldMap = () => {
  ElMessage.info('创建世界地图功能开发中...')
}

const handleUpdateWorldMap = () => {
  ElMessage.info('编辑世界地图功能开发中...')
}

const handleDeleteWorldMap = () => {
  ElMessage.info('删除世界地图功能开发中...')
}

const handleCreateCultivation = () => {
  ElMessage.info('创建修炼体系功能开发中...')
}

const handleUpdateCultivation = () => {
  ElMessage.info('编辑修炼体系功能开发中...')
}

const handleDeleteCultivation = () => {
  ElMessage.info('删除修炼体系功能开发中...')
}

const handleCreateHistory = () => {
  ElMessage.info('创建历史事件功能开发中...')
}

const handleUpdateHistory = () => {
  ElMessage.info('编辑历史事件功能开发中...')
}

const handleDeleteHistory = () => {
  ElMessage.info('删除历史事件功能开发中...')
}

const handleCreateFaction = () => {
  ElMessage.info('创建阵营势力功能开发中...')
}

const handleUpdateFaction = () => {
  ElMessage.info('编辑阵营势力功能开发中...')
}

const handleDeleteFaction = () => {
  ElMessage.info('删除阵营势力功能开发中...')
}

const resetWorldviewForm = () => {
  Object.assign(worldviewForm, {
    name: '',
    description: '',
    is_primary: false
  })
}

const submitWorldviewForm = async () => {
  try {
    const response = await apiClient.post('/worldview/', {
      ...worldviewForm,
      novel_id: novelId.value
    })
    
    const newWorldview = response.data
    ElMessage.success('世界观创建成功')
    showCreateWorldviewDialog.value = false
    await loadWorldviews()
    
    // 自动选择新创建的世界观
    selectedWorldviewId.value = newWorldview.id
    currentWorldview.value = newWorldview
  } catch (error) {
    console.error('创建世界观失败:', error)
    ElMessage.error('创建世界观失败')
  }
}

const generateWorldview = () => {
  showGenerateDialog.value = true
}

const submitGenerateForm = async () => {
  try {
    generating.value = true
    const response = await apiClient.post('/worldview/generate', {
      ...generateForm,
      novel_id: novelId.value
    })
    
    const result = response.data
    
    if (result.success) {
      ElMessage.success(`世界观生成成功，共生成 ${result.total_generated} 个项目`)
      showGenerateDialog.value = false
      await loadWorldviews()
      
      if (result.worldview) {
        selectedWorldviewId.value = result.worldview.id
        currentWorldview.value = result.worldview
        await loadWorldviewDetails()
      }
    } else {
      ElMessage.warning(result.message || 'AI生成功能暂未实现')
    }
  } catch (error) {
    console.error('生成世界观失败:', error)
    ElMessage.error('生成世界观失败')
  } finally {
    generating.value = false
  }
}

// 监听选中的世界观变化
watch(selectedWorldviewId, (newId) => {
  if (newId) {
    currentWorldview.value = worldviews.value.find(w => w.id === newId)
    if (currentWorldview.value) {
      loadWorldviewDetails()
    }
  } else {
    currentWorldview.value = null
  }
})

// 生命周期
onMounted(async () => {
  await loadWorldviews()
})
</script>

<style scoped>
.worldview-workspace {
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
  overflow: hidden;
}

.worldview-tabs {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.worldview-tabs :deep(.el-tab-pane) {
  height: 100%;
  overflow-y: auto;
}

.empty-state {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.form-help {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}
</style>