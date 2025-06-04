<template>
  <div class="worldview-workspace">
    <!-- 顶部工具栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <el-select
          v-model="selectedWorldviewId"
          placeholder="选择世界观"
          @change="handleWorldviewChange"
          :loading="worldviewStore.loading.worldviews"
        >
          <el-option
            v-for="worldview in worldviewStore.worldviews"
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
        
        <!-- 世界观统计信息 -->
        <div v-if="worldviewStore.worldviewStats" class="worldview-stats">
          <el-tag type="info" size="small">
            地图: {{ worldviewStore.worldviewStats.totalMaps }}
          </el-tag>
          <el-tag type="warning" size="small">
            修炼: {{ worldviewStore.worldviewStats.totalCultivationSystems }}
          </el-tag>
          <el-tag type="success" size="small">
            历史: {{ worldviewStore.worldviewStats.totalHistories }}
          </el-tag>
          <el-tag type="danger" size="small">
            势力: {{ worldviewStore.worldviewStats.totalFactions }}
          </el-tag>
          <el-tag size="small">
            完成度: {{ worldviewStore.worldviewStats.completionPercentage }}%
          </el-tag>
        </div>
      </div>
      
      <div class="toolbar-right">
        <el-button type="primary" @click="showCreateWorldviewDialog = true">
          <el-icon><Plus /></el-icon>
          新建世界观
        </el-button>
        <el-button @click="generateWorldview">
          <el-icon><MagicStick /></el-icon>
          AI生成世界观
        </el-button>
        <el-button @click="refreshData" :loading="refreshing">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>

    <!-- 主体内容 -->
    <div v-if="worldviewStore.currentWorldview" class="main-content">
      <!-- 世界观标签栏 -->
      <el-tabs v-model="activeTab" type="card" class="worldview-tabs">
        <el-tab-pane label="世界概况" name="overview">
          <WorldviewOverview
            :worldview="worldviewStore.currentWorldview"
            @update="handleUpdateWorldview"
            @delete="handleDeleteWorldview"
          />
        </el-tab-pane>
        
        <el-tab-pane name="maps">
          <template #label>
            <span>世界地图 
              <el-badge 
                v-if="worldviewStore.worldMaps.length > 0" 
                :value="worldviewStore.worldMaps.length" 
                class="tab-badge"
              />
            </span>
          </template>
          <WorldMapsSection
            :worldview-id="worldviewStore.currentWorldview.id"
            :maps="worldviewStore.worldMaps"
            :loading="worldviewStore.loading.worldMaps"
            @create="handleCreateWorldMap"
            @update="handleUpdateWorldMap"
            @delete="handleDeleteWorldMap"
            @refresh="worldviewStore.loadWorldMaps"
          />
        </el-tab-pane>
        
        <el-tab-pane name="cultivation">
          <template #label>
            <span>修炼体系 
              <el-badge 
                v-if="worldviewStore.cultivationSystems.length > 0" 
                :value="worldviewStore.cultivationSystems.length" 
                class="tab-badge"
              />
            </span>
          </template>
          <CultivationSection
            :worldview-id="worldviewStore.currentWorldview.id"
            :systems="worldviewStore.cultivationSystems"
            :loading="worldviewStore.loading.cultivationSystems"
            @create="handleCreateCultivation"
            @update="handleUpdateCultivation"
            @delete="handleDeleteCultivation"
            @refresh="worldviewStore.loadCultivationSystems"
          />
        </el-tab-pane>
        
        <el-tab-pane name="history">
          <template #label>
            <span>历史事件 
              <el-badge 
                v-if="worldviewStore.histories.length > 0" 
                :value="worldviewStore.histories.length" 
                class="tab-badge"
              />
            </span>
          </template>
          <HistorySection
            :worldview-id="worldviewStore.currentWorldview.id"
            :histories="worldviewStore.histories"
            :loading="worldviewStore.loading.histories"
            @create="handleCreateHistory"
            @update="handleUpdateHistory"
            @delete="handleDeleteHistory"
            @refresh="worldviewStore.loadHistories"
          />
        </el-tab-pane>
        
        <el-tab-pane name="factions">
          <template #label>
            <span>阵营势力 
              <el-badge 
                v-if="worldviewStore.factions.length > 0" 
                :value="worldviewStore.factions.length" 
                class="tab-badge"
              />
            </span>
          </template>
          <FactionsSection
            :worldview-id="worldviewStore.currentWorldview.id"
            :factions="worldviewStore.factions"
            :loading="worldviewStore.loading.factions"
            @create="handleCreateFaction"
            @update="handleUpdateFaction"
            @delete="handleDeleteFaction"
            @refresh="worldviewStore.loadFactions"
          />
        </el-tab-pane>
      </el-tabs>
    </div>
    
    <!-- 空状态 -->
    <div v-else class="empty-state">
      <el-empty description="请先创建或选择一个世界观">
        <el-button type="primary" @click="showCreateWorldviewDialog = true">
          <el-icon><Plus /></el-icon>
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
        <el-button 
          type="primary" 
          @click="submitWorldviewForm"
          :loading="worldviewStore.loading.worldviews"
        >
          创建
        </el-button>
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
            <el-checkbox label="maps">世界地图</el-checkbox>
            <el-checkbox label="cultivation">修炼体系</el-checkbox>
            <el-checkbox label="history">历史事件</el-checkbox>
            <el-checkbox label="factions">阵营势力</el-checkbox>
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

    <!-- AI生成结果预览对话框 -->
    <el-dialog
      v-model="showPreviewDialog"
      title="AI生成世界观预览"
      width="90%"
      class="preview-dialog"
    >
      <div v-if="generatedData" class="preview-content">
        <!-- 世界观基础信息 -->
        <div class="preview-section">
          <h3>世界观概况</h3>
          <el-card>
            <h4>{{ generatedData.worldview?.name || '未命名世界观' }}</h4>
            <p><strong>描述：</strong>{{ generatedData.worldview?.description || '暂无描述' }}</p>
            <p><strong>背景：</strong>{{ generatedData.worldview?.background || '暂无背景' }}</p>
            
            <div v-if="generatedData.worldview?.rules?.length">
              <h5>世界规则</h5>
              <ul>
                <li v-for="rule in generatedData.worldview.rules" :key="rule">{{ rule }}</li>
              </ul>
            </div>
            
            <div v-if="generatedData.worldview?.characteristics?.length">
              <h5>世界特色</h5>
              <ul>
                <li v-for="char in generatedData.worldview.characteristics" :key="char">{{ char }}</li>
              </ul>
            </div>
          </el-card>
        </div>

        <!-- 世界地图 -->
        <div v-if="generatedData.world_maps?.length" class="preview-section">
          <h3>世界地图 ({{ generatedData.world_maps.length }})</h3>
          <el-row :gutter="16">
            <el-col v-for="map in generatedData.world_maps" :key="map.name" :span="12">
              <el-card>
                <h4>{{ map.name }}</h4>
                <p>{{ map.description }}</p>
                <p v-if="map.climate"><strong>气候：</strong>{{ map.climate }}</p>
                <div v-if="map.notable_features?.length">
                  <strong>特色地点：</strong>
                  <el-tag v-for="feature in map.notable_features" :key="feature" size="small" style="margin: 2px;">
                    {{ feature }}
                  </el-tag>
                </div>
              </el-card>
            </el-col>
          </el-row>
        </div>

        <!-- 特殊地点 -->
        <div v-if="generatedData.special_locations?.length" class="preview-section">
          <h3>特殊地点 ({{ generatedData.special_locations.length }})</h3>
          <el-row :gutter="16">
            <el-col v-for="location in generatedData.special_locations" :key="location.name" :span="12">
              <el-card>
                <h4>{{ location.name }}</h4>
                <p>{{ location.description }}</p>
                <p v-if="location.significance"><strong>重要性：</strong>{{ location.significance }}</p>
                <div v-if="location.mysteries?.length">
                  <strong>神秘之处：</strong>
                  <ul>
                    <li v-for="mystery in location.mysteries" :key="mystery">{{ mystery }}</li>
                  </ul>
                </div>
              </el-card>
            </el-col>
          </el-row>
        </div>

        <!-- 修炼体系 -->
        <div v-if="generatedData.cultivation_system" class="preview-section">
          <h3>修炼体系</h3>
          <el-card>
            <h4>{{ generatedData.cultivation_system.name }}</h4>
            <p>{{ generatedData.cultivation_system.description }}</p>
            
            <div v-if="generatedData.cultivation_system.levels?.length">
              <h5>等级体系</h5>
              <el-table :data="generatedData.cultivation_system.levels" style="width: 100%">
                <el-table-column prop="name" label="等级名称" width="150" />
                <el-table-column prop="description" label="描述" />
              </el-table>
            </div>
            
            <div v-if="generatedData.cultivation_system.unique_features?.length">
              <h5>特色功能</h5>
              <el-tag v-for="feature in generatedData.cultivation_system.unique_features" :key="feature" style="margin: 4px;">
                {{ feature }}
              </el-tag>
            </div>
            
            <div v-if="generatedData.cultivation_system.cultivation_methods?.length">
              <h5>修炼方法</h5>
              <el-tag v-for="method in generatedData.cultivation_system.cultivation_methods" :key="method" type="info" style="margin: 4px;">
                {{ method }}
              </el-tag>
            </div>
          </el-card>
        </div>

        <!-- 历史事件 -->
        <div v-if="generatedData.histories?.length" class="preview-section">
          <h3>历史事件 ({{ generatedData.histories.length }})</h3>
          <el-timeline>
            <el-timeline-item v-for="history in generatedData.histories" :key="history.name">
              <h4>{{ history.name }}</h4>
              <p>{{ history.description }}</p>
              <div v-if="history.major_events?.length">
                <strong>重大事件：</strong>
                <ul>
                  <li v-for="event in history.major_events" :key="event">{{ event }}</li>
                </ul>
              </div>
            </el-timeline-item>
          </el-timeline>
        </div>

        <!-- 神器道具 -->
        <div v-if="generatedData.artifacts?.length" class="preview-section">
          <h3>神器道具 ({{ generatedData.artifacts.length }})</h3>
          <el-row :gutter="16">
            <el-col v-for="artifact in generatedData.artifacts" :key="artifact.name" :span="12">
              <el-card>
                <h4>{{ artifact.name }}</h4>
                <p>{{ artifact.description }}</p>
                <div v-if="artifact.powers?.length">
                  <strong>能力：</strong>
                  <el-tag v-for="power in artifact.powers" :key="power" type="warning" size="small" style="margin: 2px;">
                    {{ power }}
                  </el-tag>
                </div>
                <p v-if="artifact.history"><strong>历史：</strong>{{ artifact.history }}</p>
              </el-card>
            </el-col>
          </el-row>
        </div>

        <!-- 阵营势力 -->
        <div v-if="generatedData.factions?.length" class="preview-section">
          <h3>阵营势力 ({{ generatedData.factions.length }})</h3>
          <el-row :gutter="16">
            <el-col v-for="faction in generatedData.factions" :key="faction.name" :span="12">
              <el-card>
                <h4>{{ faction.name }}</h4>
                <p>{{ faction.description }}</p>
                <p v-if="faction.ideology"><strong>理念：</strong>{{ faction.ideology }}</p>
                <p v-if="faction.alliance"><strong>联盟：</strong>{{ faction.alliance }}</p>
              </el-card>
            </el-col>
          </el-row>
        </div>
      </div>

      <template #footer>
        <el-button @click="showPreviewDialog = false">取消</el-button>
        <el-button type="success" @click="saveGeneratedWorldview" :loading="saving">
          保存到数据库
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRoute } from 'vue-router'
import { 
  Plus, 
  MagicStick, 
  Refresh 
} from '@element-plus/icons-vue'
import apiClient from '@/api/index'
import WorldviewAPI from '@/api/worldview'
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
const refreshing = ref(false)

// 各类型数据
const worldMaps = ref([])
const cultivationSystems = ref([])
const histories = ref([])
const factions = ref([])

// 对话框状态
const showCreateWorldviewDialog = ref(false)
const showGenerateDialog = ref(false)
const showPreviewDialog = ref(false)
const generating = ref(false)
const saving = ref(false)

// 生成的数据
const generatedData = ref(null)

// 表单引用
const worldviewFormRef = ref()
const generateFormRef = ref()

// 表单数据
const worldviewForm = reactive({
  name: '',
  description: '',
  is_primary: false
})

const generateForm = reactive({
  worldview_name: '',
  generation_types: ['maps', 'cultivation', 'history', 'factions'],
  user_suggestion: '',
  include_novel_idea: true,
  include_novel_settings: true
})

// 表单验证规则
const worldviewRules = {
  name: [{ required: true, message: '请输入世界名称', trigger: 'blur' }]
}

// 创建各模块的loading状态
const worldMapsLoading = ref(false)
const cultivationSystemsLoading = ref(false)
const historiesLoading = ref(false)
const factionsLoading = ref(false)

// 模拟 worldviewStore 对象，用于兼容模板
const worldviewStore = reactive({
  worldviews: worldviews,
  currentWorldview: currentWorldview,
  worldMaps: worldMaps,
  cultivationSystems: cultivationSystems,
  histories: histories,
  factions: factions,
  loading: {
    worldviews: loading,
    worldMaps: worldMapsLoading,
    cultivationSystems: cultivationSystemsLoading,
    histories: historiesLoading,
    factions: factionsLoading
  },
  worldviewStats: computed(() => {
    if (!currentWorldview.value) return null
    
    return {
      totalMaps: worldMaps.value.length,
      totalCultivationSystems: cultivationSystems.value.length,
      totalHistories: histories.value.length,
      totalFactions: factions.value.length,
      completionPercentage: calculateCompletionPercentage()
    }
  }),
  loadWorldMaps: loadWorldMaps,
  loadCultivationSystems: loadCultivationSystems,
  loadHistories: loadHistories,
  loadFactions: loadFactions
})

// ============ 方法定义 ============

const calculateCompletionPercentage = () => {
  if (!currentWorldview.value) return 0
  
  let completed = 0
  let total = 4 // 4个主要类别
  
  if (worldMaps.value.length > 0) completed++
  if (cultivationSystems.value.length > 0) completed++
  if (histories.value.length > 0) completed++
  if (factions.value.length > 0) completed++
  
  return Math.round((completed / total) * 100)
}

const loadWorldviews = async () => {
  try {
    loading.value = true
    const data = await WorldviewAPI.getWorldviewsByNovel(novelId.value)
    
    worldviews.value = data.items || []
    
    // 如果没有选中的世界观，自动选择第一个（优先主世界）
    if (!selectedWorldviewId.value && worldviews.value.length > 0) {
      const primaryWorld = worldviews.value.find(w => w.is_primary)
      const autoSelectedId = primaryWorld?.id || worldviews.value[0].id
      
      // 设置选中的世界观ID和当前世界观
      selectedWorldviewId.value = autoSelectedId
      currentWorldview.value = worldviews.value.find(w => w.id === autoSelectedId)
      
      // 手动触发数据加载
      if (currentWorldview.value) {
        await loadWorldviewDetails()
      }
    }
  } catch (error) {
    console.error('加载世界观列表失败:', error)
    ElMessage.error(error.message || '加载世界观列表失败')
  } finally {
    loading.value = false
  }
}

async function loadWorldMaps() {
  if (!selectedWorldviewId.value) return
  
  try {
    worldMapsLoading.value = true
    const data = await WorldviewAPI.getWorldMaps(selectedWorldviewId.value)
    worldMaps.value = data.items || []
  } catch (error) {
    console.error('加载世界地图失败:', error)
  } finally {
    worldMapsLoading.value = false
  }
}

async function loadCultivationSystems() {
  if (!selectedWorldviewId.value) return
  
  try {
    cultivationSystemsLoading.value = true
    const data = await WorldviewAPI.getCultivationSystems(selectedWorldviewId.value)
    cultivationSystems.value = data.items || []
  } catch (error) {
    console.error('加载修炼体系失败:', error)
  } finally {
    cultivationSystemsLoading.value = false
  }
}

async function loadHistories() {
  if (!selectedWorldviewId.value) return
  
  try {
    historiesLoading.value = true
    const data = await WorldviewAPI.getHistories(selectedWorldviewId.value)
    histories.value = data.items || []
  } catch (error) {
    console.error('加载历史事件失败:', error)
  } finally {
    historiesLoading.value = false
  }
}

async function loadFactions() {
  if (!selectedWorldviewId.value) return
  
  try {
    factionsLoading.value = true
    const data = await WorldviewAPI.getFactions(selectedWorldviewId.value)
    factions.value = data.items || []
  } catch (error) {
    console.error('加载阵营势力失败:', error)
  } finally {
    factionsLoading.value = false
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

const refreshData = async () => {
  try {
    refreshing.value = true
    await loadWorldviews()
    if (currentWorldview.value) {
      await loadWorldviewDetails()
    }
    ElMessage.success('数据刷新成功')
  } catch (error) {
    console.error('刷新数据失败:', error)
    ElMessage.error('刷新数据失败')
  } finally {
    refreshing.value = false
  }
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
    const updatedWorldview = await WorldviewAPI.updateWorldview(currentWorldview.value.id, updatedData)
    
    currentWorldview.value = updatedWorldview
    await loadWorldviews()
    ElMessage.success('世界观更新成功')
  } catch (error) {
    console.error('更新世界观失败:', error)
    ElMessage.error(error.message || '更新世界观失败')
  }
}

const handleDeleteWorldview = async () => {
  if (!currentWorldview.value) return
  
  try {
    await ElMessageBox.confirm('确定要删除这个世界观吗？这将删除所有相关数据。', '确认删除', {
      type: 'warning'
    })
    
    await WorldviewAPI.deleteWorldview(currentWorldview.value.id)
    
    ElMessage.success('世界观删除成功')
    currentWorldview.value = null
    selectedWorldviewId.value = null
    await loadWorldviews()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除世界观失败:', error)
      ElMessage.error(error.message || '删除世界观失败')
    }
  }
}

const resetWorldviewForm = () => {
  Object.assign(worldviewForm, {
    name: '',
    description: '',
    is_primary: false
  })
  nextTick(() => {
    worldviewFormRef.value?.clearValidate()
  })
}

const submitWorldviewForm = async () => {
  try {
    await worldviewFormRef.value?.validate()
    
    const newWorldview = await WorldviewAPI.createWorldview({
      ...worldviewForm,
      novel_id: novelId.value
    })
    
    ElMessage.success('世界观创建成功')
    showCreateWorldviewDialog.value = false
    await loadWorldviews()
    
    // 自动选择新创建的世界观
    selectedWorldviewId.value = newWorldview.id
    currentWorldview.value = newWorldview
  } catch (error) {
    console.error('创建世界观失败:', error)
    if (error !== false) { // 不是验证错误
      ElMessage.error(error.message || '创建世界观失败')
    }
  }
}

const generateWorldview = () => {
  showGenerateDialog.value = true
}

const submitGenerateForm = async () => {
  try {
    generating.value = true
    const result = await apiClient.post('/worldview/generate', {
      ...generateForm,
      novel_id: novelId.value
    })
    
    if (result.success) {
      ElMessage.success(`世界观生成成功，共生成 ${result.total_generated} 个项目`)
      
      // 保存生成的数据
      generatedData.value = result
      
      // 关闭生成对话框，显示预览对话框
      showGenerateDialog.value = false
      showPreviewDialog.value = true
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

// 保存生成的世界观到数据库
const saveGeneratedWorldview = async () => {
  if (!generatedData.value) {
    ElMessage.error('没有可保存的数据')
    return
  }
  
  try {
    saving.value = true
    
    // 使用专门的API方法
    const result = await WorldviewAPI.saveGeneratedWorldview(novelId.value, generatedData.value)
    
    if (result.success) {
      ElMessage.success(result.message || '世界观已保存到数据库')
      showPreviewDialog.value = false
      generatedData.value = null
      
      // 刷新数据
      await loadWorldviews()
      
      // 自动选择新保存的世界观
      if (result.worldview) {
        selectedWorldviewId.value = result.worldview.id
        currentWorldview.value = result.worldview
        await loadWorldviewDetails()
      }
    } else {
      ElMessage.error(result.message || '保存失败')
    }
  } catch (error) {
    console.error('保存世界观失败:', error)
    ElMessage.error(error?.response?.data?.detail || '保存世界观失败')
  } finally {
    saving.value = false
  }
}

// ============ 各模块的处理方法 ============

const handleCreateWorldMap = () => {
  activeTab.value = 'maps'
}

const handleUpdateWorldMap = () => {
  // 组件内部处理
}

const handleDeleteWorldMap = () => {
  // 组件内部处理
}

const handleCreateCultivation = () => {
  activeTab.value = 'cultivation'
}

const handleUpdateCultivation = () => {
  // 组件内部处理
}

const handleDeleteCultivation = () => {
  // 组件内部处理
}

const handleCreateHistory = () => {
  activeTab.value = 'history'
}

const handleUpdateHistory = () => {
  // 组件内部处理
}

const handleDeleteHistory = () => {
  // 组件内部处理
}

const handleCreateFaction = () => {
  activeTab.value = 'factions'
}

const handleUpdateFaction = () => {
  // 组件内部处理
}

const handleDeleteFaction = () => {
  // 组件内部处理
}

// ============ 监听器 ============

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

// ============ 生命周期 ============

onMounted(async () => {
  await loadWorldviews()
})
</script>

<style scoped lang="scss">
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
  flex: 1;
}

.worldview-stats {
  display: flex;
  gap: 8px;
  margin-left: 16px;
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
  
  :deep(.el-tabs__content) {
    flex: 1;
    overflow: hidden;
  }
  
  :deep(.el-tab-pane) {
    height: 100%;
    overflow-y: auto;
  }
}

.tab-badge {
  :deep(.el-badge__content) {
    background-color: #409eff;
    border-color: #409eff;
  }
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

// 响应式设计
@media (max-width: 1023px) {
  .worldview-workspace {
    padding: 16px;
  }
  
  .toolbar {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .toolbar-left {
    justify-content: space-between;
  }
  
  .worldview-stats {
    margin-left: 0;
    flex-wrap: wrap;
  }
}

@media (max-width: 767px) {
  .worldview-workspace {
    padding: 12px;
  }
  
  .toolbar-left,
  .toolbar-right {
    flex-direction: column;
    gap: 8px;
  }
  
  .worldview-stats {
    order: 3;
    justify-content: center;
  }
}

// 预览对话框样式
.preview-dialog {
  :deep(.el-dialog) {
    max-height: 90vh;
  }
  
  :deep(.el-dialog__body) {
    max-height: 70vh;
    overflow-y: auto;
  }
}

.preview-content {
  .preview-section {
    margin-bottom: 24px;
    
    h3 {
      color: #409eff;
      margin-bottom: 12px;
      border-bottom: 2px solid #409eff;
      padding-bottom: 4px;
    }
    
    h4 {
      color: #303133;
      margin-bottom: 8px;
    }
    
    h5 {
      color: #606266;
      margin: 12px 0 8px 0;
      font-size: 14px;
    }
    
    .el-card {
      margin-bottom: 12px;
    }
    
    .el-table {
      margin-top: 12px;
    }
  }
}
</style>