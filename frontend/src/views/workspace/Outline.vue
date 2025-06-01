<template>
  <div class="outline-workspace">
    <!-- 顶部标签栏 -->
    <el-tabs v-model="activeTab" type="card" class="outline-tabs">
      <el-tab-pane label="粗略大纲" name="rough">
        <div class="outline-content">
          <!-- 粗略大纲子标签 -->
          <el-tabs v-model="activeRoughTab" type="border-card">
            <el-tab-pane label="故事线" name="storyline">
              <OutlineSection
                :items="storylines"
                type="storyline"
                title="故事线"
                @create="handleCreateRoughOutline"
                @update="handleUpdateRoughOutline"
                @delete="handleDeleteRoughOutline"
                @generate="handleGenerateRoughOutline"
              />
            </el-tab-pane>
            
            <el-tab-pane label="角色成长路线" name="character_growth">
              <OutlineSection
                :items="characterGrowths"
                type="character_growth"
                title="角色成长路线"
                @create="handleCreateRoughOutline"
                @update="handleUpdateRoughOutline"
                @delete="handleDeleteRoughOutline"
                @generate="handleGenerateRoughOutline"
              />
            </el-tab-pane>
            
            <el-tab-pane label="重大事件" name="major_event">
              <OutlineSection
                :items="majorEvents"
                type="major_event"
                title="重大事件"
                @create="handleCreateRoughOutline"
                @update="handleUpdateRoughOutline"
                @delete="handleDeleteRoughOutline"
                @generate="handleGenerateRoughOutline"
              />
            </el-tab-pane>
            
            <el-tab-pane label="大情节点" name="plot_point">
              <PlotPointSection
                :items="plotPoints"
                @create="handleCreateRoughOutline"
                @update="handleUpdateRoughOutline"
                @delete="handleDeleteRoughOutline"
                @generate="handleGenerateRoughOutline"
                @generate-detailed="handleGenerateDetailedFromPlot"
              />
            </el-tab-pane>
          </el-tabs>
        </div>
      </el-tab-pane>
      
      <el-tab-pane label="详细大纲" name="detailed">
        <DetailedOutlineSection
          :items="detailedOutlines"
          :characters="characters"
          @create="handleCreateDetailedOutline"
          @update="handleUpdateDetailedOutline"
          @delete="handleDeleteDetailedOutline"
          @generate="handleGenerateDetailedOutline"
          @ai-review="handleAIReview"
          @generate-summary="handleGenerateSummary"
        />
      </el-tab-pane>
    </el-tabs>

    <!-- 创建/编辑粗略大纲对话框 -->
    <el-dialog
      v-model="showRoughDialog"
      :title="editingRoughOutline ? '编辑大纲' : '创建大纲'"
      width="600px"
      @close="resetRoughForm"
    >
      <el-form ref="roughFormRef" :model="roughForm" :rules="roughRules" label-width="120px">
        <el-form-item label="大纲类型" prop="outline_type">
          <el-select v-model="roughForm.outline_type" placeholder="请选择大纲类型" disabled>
            <el-option label="故事线" value="storyline" />
            <el-option label="角色成长路线" value="character_growth" />
            <el-option label="重大事件" value="major_event" />
            <el-option label="大情节点" value="plot_point" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="标题" prop="title">
          <el-input v-model="roughForm.title" placeholder="请输入大纲标题" />
        </el-form-item>
        
        <el-form-item label="内容描述" prop="content">
          <el-input
            v-model="roughForm.content"
            type="textarea"
            :rows="6"
            placeholder="请详细描述大纲内容"
          />
        </el-form-item>
        
        <el-form-item v-if="roughForm.outline_type === 'plot_point'" label="开始章节">
          <el-input-number v-model="roughForm.start_chapter" :min="1" placeholder="开始章节数" />
        </el-form-item>
        
        <el-form-item v-if="roughForm.outline_type === 'plot_point'" label="结束章节">
          <el-input-number v-model="roughForm.end_chapter" :min="1" placeholder="结束章节数" />
        </el-form-item>
        
        <el-form-item label="排序索引">
          <el-input-number v-model="roughForm.order_index" :min="0" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showRoughDialog = false">取消</el-button>
        <el-button type="primary" @click="submitRoughForm">
          {{ editingRoughOutline ? '更新' : '创建' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 创建/编辑详细大纲对话框 -->
    <el-dialog
      v-model="showDetailedDialog"
      :title="editingDetailedOutline ? '编辑详细大纲' : '创建详细大纲'"
      width="800px"
      @close="resetDetailedForm"
    >
      <el-form ref="detailedFormRef" :model="detailedForm" :rules="detailedRules" label-width="120px">
        <el-form-item label="章节号" prop="chapter_number">
          <el-input-number v-model="detailedForm.chapter_number" :min="1" placeholder="章节号" />
        </el-form-item>
        
        <el-form-item label="章节标题">
          <el-input v-model="detailedForm.chapter_title" placeholder="请输入章节标题" />
        </el-form-item>
        
        <el-form-item label="情节点" prop="plot_points">
          <el-input
            v-model="detailedForm.plot_points"
            type="textarea"
            :rows="4"
            placeholder="请描述本章节的主要情节点"
          />
        </el-form-item>
        
        <el-form-item label="参与角色">
          <el-select
            v-model="detailedForm.participating_characters"
            multiple
            placeholder="选择参与角色"
            style="width: 100%"
          >
            <el-option
              v-for="character in characters"
              :key="character.id"
              :label="character.name"
              :value="character.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="入场角色">
          <el-select
            v-model="detailedForm.entering_characters"
            multiple
            placeholder="选择入场角色"
            style="width: 100%"
          >
            <el-option
              v-for="character in characters"
              :key="character.id"
              :label="character.name"
              :value="character.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="离场角色">
          <el-select
            v-model="detailedForm.exiting_characters"
            multiple
            placeholder="选择离场角色"
            style="width: 100%"
          >
            <el-option
              v-for="character in characters"
              :key="character.id"
              :label="character.name"
              :value="character.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="章节简介">
          <el-input
            v-model="detailedForm.chapter_summary"
            type="textarea"
            :rows="3"
            placeholder="请输入章节简介"
          />
        </el-form-item>
        
        <el-form-item>
          <el-checkbox v-model="detailedForm.is_plot_end">是否剧情结束</el-checkbox>
        </el-form-item>
        
        <el-form-item>
          <el-checkbox v-model="detailedForm.is_new_plot">是否新剧情开始</el-checkbox>
        </el-form-item>
        
        <el-form-item v-if="detailedForm.is_new_plot" label="新剧情简介">
          <el-input
            v-model="detailedForm.new_plot_summary"
            type="textarea"
            :rows="3"
            placeholder="请描述新剧情的内容"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showDetailedDialog = false">取消</el-button>
        <el-button type="primary" @click="submitDetailedForm">
          {{ editingDetailedOutline ? '更新' : '创建' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- AI审核结果对话框 -->
    <el-dialog v-model="showAIReviewDialog" title="AI审核结果" width="700px">
      <div class="ai-review-content">
        <div class="review-status">
          <el-tag :type="reviewResult.status === 'passed' ? 'success' : 'warning'">
            {{ reviewResult.status === 'passed' ? '审核通过' : '发现问题' }}
          </el-tag>
        </div>
        
        <div v-if="reviewResult.issues && reviewResult.issues.length > 0" class="issues-list">
          <h4>发现的问题：</h4>
          <div v-for="(issue, index) in reviewResult.issues" :key="index" class="issue-item">
            <div class="issue-header">
              <el-tag :type="getIssueTypeColor(issue.type)" size="small">
                {{ issue.type }}
              </el-tag>
              <span class="issue-position" v-if="issue.position">{{ issue.position }}</span>
            </div>
            <div class="issue-description">{{ issue.description }}</div>
            <div class="issue-suggestion" v-if="issue.suggestion">
              <strong>建议修改：</strong>{{ issue.suggestion }}
            </div>
          </div>
        </div>
        
        <div class="user-feedback">
          <h4>修改意见：</h4>
          <el-input
            v-model="userFeedback"
            type="textarea"
            :rows="3"
            placeholder="请描述您的修改要求..."
          />
        </div>
      </div>
      
      <template #footer>
        <el-button @click="submitFeedback" type="primary">提交修改意见</el-button>
        <el-button @click="ignoreIssues">忽略所有问题</el-button>
        <el-button @click="showAIReviewDialog = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 生成总结对话框 -->
    <el-dialog v-model="showSummaryDialog" title="内容总结" width="600px">
      <div class="summary-content">
        <el-form label-width="100px">
          <el-form-item label="总结长度">
            <el-select v-model="summarySettings.length">
              <el-option label="简要" value="brief" />
              <el-option label="详细" value="detailed" />
              <el-option label="完整" value="complete" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="侧重点">
            <el-checkbox-group v-model="summarySettings.focus_points">
              <el-checkbox label="情节">情节</el-checkbox>
              <el-checkbox label="角色">角色</el-checkbox>
              <el-checkbox label="世界观">世界观</el-checkbox>
              <el-checkbox label="其他">其他</el-checkbox>
            </el-checkbox-group>
          </el-form-item>
        </el-form>
        
        <div class="summary-result">
          <h4>总结内容：</h4>
          <el-input
            v-model="summaryResult"
            type="textarea"
            :rows="8"
            placeholder="总结内容将在这里显示..."
            readonly
          />
        </div>
      </div>
      
      <template #footer>
        <el-button @click="generateSummary" type="primary">重新生成总结</el-button>
        <el-button @click="saveSummary" type="success">保存总结</el-button>
        <el-button @click="showSummaryDialog = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRoute } from 'vue-router'
import OutlineSection from '@/components/outline/OutlineSection.vue'
import PlotPointSection from '@/components/outline/PlotPointSection.vue'
import DetailedOutlineSection from '@/components/outline/DetailedOutlineSection.vue'

// 获取路由参数
const route = useRoute()
const novelId = computed(() => parseInt(route.params.novelId))

// 数据状态
const activeTab = ref('rough')
const activeRoughTab = ref('storyline')
const roughOutlines = ref([])
const detailedOutlines = ref([])
const characters = ref([])
const loading = ref(false)

// 对话框状态
const showRoughDialog = ref(false)
const showDetailedDialog = ref(false)
const showAIReviewDialog = ref(false)
const showSummaryDialog = ref(false)
const editingRoughOutline = ref(null)
const editingDetailedOutline = ref(null)

// 表单数据
const roughForm = reactive({
  outline_type: 'storyline',
  title: '',
  content: '',
  order_index: 0,
  start_chapter: null,
  end_chapter: null
})

const detailedForm = reactive({
  chapter_number: 1,
  chapter_title: '',
  plot_points: '',
  participating_characters: [],
  entering_characters: [],
  exiting_characters: [],
  chapter_summary: '',
  is_plot_end: false,
  is_new_plot: false,
  new_plot_summary: ''
})

// AI审核相关
const reviewResult = ref({
  status: 'passed',
  issues: []
})
const userFeedback = ref('')

// 总结相关
const summarySettings = reactive({
  length: 'detailed',
  focus_points: ['情节']
})
const summaryResult = ref('')
const currentSummaryItem = ref(null)

// 表单验证规则
const roughRules = {
  title: [{ required: true, message: '请输入标题', trigger: 'blur' }],
  content: [{ required: true, message: '请输入内容描述', trigger: 'blur' }]
}

const detailedRules = {
  chapter_number: [{ required: true, message: '请输入章节号', trigger: 'blur' }],
  plot_points: [{ required: true, message: '请输入情节点', trigger: 'blur' }]
}

// 计算属性 - 按类型分组的粗略大纲
const storylines = computed(() => 
  roughOutlines.value.filter(item => item.outline_type === 'storyline')
)

const characterGrowths = computed(() => 
  roughOutlines.value.filter(item => item.outline_type === 'character_growth')
)

const majorEvents = computed(() => 
  roughOutlines.value.filter(item => item.outline_type === 'major_event')
)

const plotPoints = computed(() => 
  roughOutlines.value.filter(item => item.outline_type === 'plot_point')
)

// 方法
const loadRoughOutlines = async () => {
  try {
    loading.value = true
    const response = await fetch(`/api/v1/outline/rough/novel/${novelId.value}`)
    const data = await response.json()
    if (data.success !== false) {
      roughOutlines.value = data.items || []
    }
  } catch (error) {
    console.error('加载粗略大纲失败:', error)
    ElMessage.error('加载粗略大纲失败')
  } finally {
    loading.value = false
  }
}

const loadDetailedOutlines = async () => {
  try {
    const response = await fetch(`/api/v1/outline/detailed/novel/${novelId.value}`)
    const data = await response.json()
    if (data.success !== false) {
      detailedOutlines.value = data.items || []
    }
  } catch (error) {
    console.error('加载详细大纲失败:', error)
    ElMessage.error('加载详细大纲失败')
  }
}

const loadCharacters = async () => {
  try {
    const response = await fetch(`/api/v1/characters/?novel_id=${novelId.value}`)
    const data = await response.json()
    if (data.success !== false) {
      characters.value = data.items || []
    }
  } catch (error) {
    console.error('加载角色列表失败:', error)
  }
}

const handleCreateRoughOutline = (type) => {
  editingRoughOutline.value = null
  roughForm.outline_type = type
  resetRoughForm()
  showRoughDialog.value = true
}

const handleUpdateRoughOutline = (item) => {
  editingRoughOutline.value = item
  Object.assign(roughForm, {
    outline_type: item.outline_type,
    title: item.title,
    content: item.content,
    order_index: item.order_index,
    start_chapter: item.start_chapter,
    end_chapter: item.end_chapter
  })
  showRoughDialog.value = true
}

const handleDeleteRoughOutline = async (item) => {
  try {
    await ElMessageBox.confirm('确定要删除这个大纲吗？', '确认删除', {
      type: 'warning'
    })
    
    const response = await fetch(`/api/v1/outline/rough/${item.id}`, {
      method: 'DELETE'
    })
    
    if (response.ok) {
      ElMessage.success('大纲删除成功')
      await loadRoughOutlines()
    } else {
      throw new Error('删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除大纲失败:', error)
      ElMessage.error('删除大纲失败')
    }
  }
}

const handleGenerateRoughOutline = (type) => {
  ElMessage.info('AI生成功能开发中...')
}

const handleGenerateDetailedFromPlot = (plotPoint) => {
  ElMessage.info('根据大情节点生成详细大纲功能开发中...')
}

const handleCreateDetailedOutline = () => {
  editingDetailedOutline.value = null
  resetDetailedForm()
  showDetailedDialog.value = true
}

const handleUpdateDetailedOutline = (item) => {
  editingDetailedOutline.value = item
  Object.assign(detailedForm, {
    chapter_number: item.chapter_number,
    chapter_title: item.chapter_title || '',
    plot_points: item.plot_points,
    participating_characters: item.participating_characters || [],
    entering_characters: item.entering_characters || [],
    exiting_characters: item.exiting_characters || [],
    chapter_summary: item.chapter_summary || '',
    is_plot_end: item.is_plot_end || false,
    is_new_plot: item.is_new_plot || false,
    new_plot_summary: item.new_plot_summary || ''
  })
  showDetailedDialog.value = true
}

const handleDeleteDetailedOutline = async (item) => {
  try {
    await ElMessageBox.confirm('确定要删除这个详细大纲吗？', '确认删除', {
      type: 'warning'
    })
    
    const response = await fetch(`/api/v1/outline/detailed/${item.id}`, {
      method: 'DELETE'
    })
    
    if (response.ok) {
      ElMessage.success('详细大纲删除成功')
      await loadDetailedOutlines()
    } else {
      throw new Error('删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除详细大纲失败:', error)
      ElMessage.error('删除详细大纲失败')
    }
  }
}

const handleGenerateDetailedOutline = () => {
  ElMessage.info('AI生成功能开发中...')
}

const handleAIReview = (item) => {
  // 模拟AI审核结果
  reviewResult.value = {
    status: 'has_issues',
    issues: [
      {
        type: '逻辑问题',
        position: '章节情节点',
        description: '角色动机不够明确，缺乏推动情节发展的内在驱动力',
        suggestion: '建议增加角色的内心冲突或外在压力，明确其行动目标'
      },
      {
        type: '内容问题',
        description: '章节结尾过于突兀，与下一章节的衔接不够自然',
        suggestion: '建议增加过渡性描述或设置悬念，为下一章节做铺垫'
      }
    ]
  }
  userFeedback.value = ''
  showAIReviewDialog.value = true
}

const handleGenerateSummary = (item) => {
  currentSummaryItem.value = item
  summaryResult.value = ''
  showSummaryDialog.value = true
  generateSummary()
}

const resetRoughForm = () => {
  Object.assign(roughForm, {
    outline_type: activeRoughTab.value,
    title: '',
    content: '',
    order_index: 0,
    start_chapter: null,
    end_chapter: null
  })
}

const resetDetailedForm = () => {
  Object.assign(detailedForm, {
    chapter_number: 1,
    chapter_title: '',
    plot_points: '',
    participating_characters: [],
    entering_characters: [],
    exiting_characters: [],
    chapter_summary: '',
    is_plot_end: false,
    is_new_plot: false,
    new_plot_summary: ''
  })
}

const submitRoughForm = async () => {
  try {
    const method = editingRoughOutline.value ? 'PUT' : 'POST'
    const url = editingRoughOutline.value 
      ? `/api/v1/outline/rough/${editingRoughOutline.value.id}`
      : '/api/v1/outline/rough'
    
    const requestData = { ...roughForm }
    if (!editingRoughOutline.value) {
      requestData.novel_id = novelId.value
    }
    
    const response = await fetch(url, {
      method,
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(requestData)
    })
    
    if (response.ok) {
      ElMessage.success(editingRoughOutline.value ? '大纲更新成功' : '大纲创建成功')
      showRoughDialog.value = false
      await loadRoughOutlines()
    } else {
      throw new Error('操作失败')
    }
  } catch (error) {
    console.error('大纲操作失败:', error)
    ElMessage.error('大纲操作失败')
  }
}

const submitDetailedForm = async () => {
  try {
    const method = editingDetailedOutline.value ? 'PUT' : 'POST'
    const url = editingDetailedOutline.value 
      ? `/api/v1/outline/detailed/${editingDetailedOutline.value.id}`
      : '/api/v1/outline/detailed'
    
    const requestData = { ...detailedForm }
    if (!editingDetailedOutline.value) {
      requestData.novel_id = novelId.value
    }
    
    const response = await fetch(url, {
      method,
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(requestData)
    })
    
    if (response.ok) {
      ElMessage.success(editingDetailedOutline.value ? '详细大纲更新成功' : '详细大纲创建成功')
      showDetailedDialog.value = false
      await loadDetailedOutlines()
    } else {
      throw new Error('操作失败')
    }
  } catch (error) {
    console.error('详细大纲操作失败:', error)
    ElMessage.error('详细大纲操作失败')
  }
}

const getIssueTypeColor = (type) => {
  const colors = {
    '逻辑问题': 'danger',
    '语法问题': 'warning',
    '内容问题': 'info',
    '其他': 'default'
  }
  return colors[type] || 'default'
}

const submitFeedback = () => {
  if (!userFeedback.value.trim()) {
    ElMessage.warning('请输入修改意见')
    return
  }
  
  ElMessage.info('修改意见已提交，AI正在处理中...')
  showAIReviewDialog.value = false
}

const ignoreIssues = () => {
  ElMessage.success('已忽略所有问题')
  showAIReviewDialog.value = false
}

const generateSummary = () => {
  // 模拟生成总结
  setTimeout(() => {
    summaryResult.value = `这是${currentSummaryItem.value?.title || '大纲'}的${summarySettings.length}总结。主要涉及${summarySettings.focus_points.join('、')}等方面的内容。\n\n总结内容将根据AI分析生成...`
  }, 1000)
}

const saveSummary = () => {
  if (!summaryResult.value.trim()) {
    ElMessage.warning('请先生成总结内容')
    return
  }
  
  ElMessage.success('总结已保存')
  showSummaryDialog.value = false
}

// 生命周期
onMounted(async () => {
  await Promise.all([
    loadRoughOutlines(),
    loadDetailedOutlines(),
    loadCharacters()
  ])
})
</script>

<style scoped>
.outline-workspace {
  padding: 20px;
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.outline-tabs {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.outline-tabs :deep(.el-tab-pane) {
  height: 100%;
}

.outline-content {
  height: calc(100vh - 200px);
}

.ai-review-content {
  max-height: 500px;
  overflow-y: auto;
}

.review-status {
  margin-bottom: 20px;
}

.issues-list {
  margin-bottom: 20px;
}

.issue-item {
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  padding: 15px;
  margin-bottom: 12px;
}

.issue-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.issue-position {
  font-size: 12px;
  color: #909399;
}

.issue-description {
  margin-bottom: 8px;
  color: #303133;
}

.issue-suggestion {
  font-size: 14px;
  color: #606266;
  background: #f5f7fa;
  padding: 8px;
  border-radius: 4px;
}

.user-feedback h4 {
  margin-bottom: 10px;
  font-size: 14px;
  font-weight: 500;
}

.summary-content {
  max-height: 600px;
  overflow-y: auto;
}

.summary-result {
  margin-top: 20px;
}

.summary-result h4 {
  margin-bottom: 10px;
  font-size: 14px;
  font-weight: 500;
}
</style>