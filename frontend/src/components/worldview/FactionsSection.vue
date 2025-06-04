<template>
  <div class="factions-section">
    <div class="section-header">
      <h3>阵营势力</h3>
      <div class="header-actions">
        <el-button type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>
          新建势力
        </el-button>
        <el-button @click="generateFactions" :loading="generating">
          <el-icon><MagicStick /></el-icon>
          AI 生成势力
        </el-button>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <el-skeleton :rows="3" animated />
    </div>

    <!-- 主体内容 -->
    <div v-else class="factions-content">
      <!-- 空状态 -->
      <div v-if="factions.length === 0" class="empty-state">
        <el-empty description="暂无阵营势力，点击新建开始创建">
          <el-button type="primary" @click="showCreateDialog = true">
            <el-icon><Plus /></el-icon>
            新建势力
          </el-button>
        </el-empty>
      </div>

      <!-- 势力列表 -->
      <div v-else class="factions-grid">
        <el-card
          v-for="faction in groupedFactions"
          :key="faction.type"
          class="faction-group"
        >
          <template #header>
            <div class="group-header">
              <h4>{{ getTypeLabel(faction.type) }}</h4>
              <el-tag>{{ faction.items.length }}</el-tag>
            </div>
          </template>

          <div class="faction-items">
            <el-collapse>
              <el-collapse-item
                v-for="item in faction.items"
                :key="item.id"
                :title="item.name"
              >
                <template #title>
                  <div class="faction-title">
                    <span>{{ item.name }}</span>
                    <div class="faction-actions">
                      <el-button-group>
                        <el-button size="small" type="primary" @click.stop="handleEdit(item)">
                          编辑
                        </el-button>
                        <el-button size="small" type="danger" @click.stop="handleDelete(item)">
                          删除
                        </el-button>
                      </el-button-group>
                    </div>
                  </div>
                </template>

                <div class="faction-content">
                  <p class="faction-description">{{ item.description }}</p>
                  
                  <div class="faction-details">
                    <div class="detail-item">
                      <strong>领导者：</strong>
                      <span>{{ item.leader || '暂无' }}</span>
                    </div>
                    
                    <div class="detail-item">
                      <strong>势力等级：</strong>
                      <el-tag size="small" :type="getPowerType(item.power_level)">
                        {{ item.power_level || '未知' }}
                      </el-tag>
                    </div>
                    
                    <div class="detail-item">
                      <strong>成员规模：</strong>
                      <span>{{ item.member_count || '未知' }}</span>
                    </div>
                  </div>
                  
                  <div v-if="item.territory" class="detail-block">
                    <strong>控制区域：</strong>
                    <p>{{ item.territory }}</p>
                  </div>
                  
                  <div v-if="item.ideology" class="detail-block">
                    <strong>理念目标：</strong>
                    <p>{{ item.ideology }}</p>
                  </div>
                  
                  <div class="faction-relations">
                    <div v-if="item.allies?.length" class="relation-group">
                      <strong>盟友：</strong>
                      <div class="relation-tags">
                        <el-tag
                          v-for="ally in item.allies"
                          :key="ally"
                          type="success"
                          size="small"
                        >
                          {{ ally }}
                        </el-tag>
                      </div>
                    </div>
                    
                    <div v-if="item.enemies?.length" class="relation-group">
                      <strong>敌对：</strong>
                      <div class="relation-tags">
                        <el-tag
                          v-for="enemy in item.enemies"
                          :key="enemy"
                          type="danger"
                          size="small"
                        >
                          {{ enemy }}
                        </el-tag>
                      </div>
                    </div>
                  </div>
                </div>
              </el-collapse-item>
            </el-collapse>
          </div>
        </el-card>
      </div>
    </div>

    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="isEdit ? '编辑势力' : '新建势力'"
      width="700px"
      @close="resetForm"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="势力名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入势力名称" />
        </el-form-item>

        <el-form-item label="势力类型" prop="faction_type">
          <el-select v-model="form.faction_type" placeholder="选择势力类型">
            <el-option label="宗门" value="sect" />
            <el-option label="帝国" value="empire" />
            <el-option label="组织" value="organization" />
            <el-option label="势力" value="power" />
            <el-option label="部落" value="tribe" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>

        <el-form-item label="势力描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="请描述势力的整体情况"
          />
        </el-form-item>

        <el-form-item label="领导者">
          <el-input v-model="form.leader" placeholder="势力的最高领导者" />
        </el-form-item>

        <el-form-item label="控制区域">
          <el-input
            v-model="form.territory"
            type="textarea"
            :rows="2"
            placeholder="势力控制或影响的地区"
          />
        </el-form-item>

        <el-form-item label="势力等级">
          <el-select v-model="form.power_level" placeholder="选择势力等级">
            <el-option label="超一流" value="supreme" />
            <el-option label="一流" value="top" />
            <el-option label="二流" value="high" />
            <el-option label="三流" value="medium" />
            <el-option label="四流" value="low" />
          </el-select>
        </el-form-item>

        <el-form-item label="理念目标">
          <el-input
            v-model="form.ideology"
            type="textarea"
            :rows="2"
            placeholder="势力的核心理念和追求的目标"
          />
        </el-form-item>

        <el-form-item label="成员规模">
          <el-input v-model="form.member_count" placeholder="势力的人员规模" />
        </el-form-item>

        <el-form-item label="盟友">
          <el-select
            v-model="form.allies"
            multiple
            filterable
            allow-create
            default-first-option
            placeholder="输入或选择盟友势力"
          >
            <el-option
              v-for="faction in otherFactions"
              :key="faction.name"
              :label="faction.name"
              :value="faction.name"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="敌对势力">
          <el-select
            v-model="form.enemies"
            multiple
            filterable
            allow-create
            default-first-option
            placeholder="输入或选择敌对势力"
          >
            <el-option
              v-for="faction in otherFactions"
              :key="faction.name"
              :label="faction.name"
              :value="faction.name"
            />
          </el-select>
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
      title="AI 生成势力"
      width="600px"
    >
      <el-form :model="generateForm" label-width="100px">
        <el-form-item label="势力数量">
          <el-input-number
            v-model="generateForm.count"
            :min="1"
            :max="10"
            controls-position="right"
          />
        </el-form-item>

        <el-form-item label="势力类型">
          <el-select v-model="generateForm.faction_types" multiple placeholder="选择势力类型">
            <el-option label="宗门" value="sect" />
            <el-option label="帝国" value="empire" />
            <el-option label="组织" value="organization" />
            <el-option label="势力" value="power" />
            <el-option label="部落" value="tribe" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>

        <el-form-item label="生成内容">
          <el-checkbox-group v-model="generateForm.include">
            <el-checkbox label="leader">领导者</el-checkbox>
            <el-checkbox label="territory">控制区域</el-checkbox>
            <el-checkbox label="ideology">理念目标</el-checkbox>
            <el-checkbox label="relations">势力关系</el-checkbox>
          </el-checkbox-group>
        </el-form-item>

        <el-form-item label="补充建议">
          <el-input
            v-model="generateForm.suggestion"
            type="textarea"
            :rows="3"
            placeholder="输入你对势力的期望和建议"
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
import type { Faction } from '@/api/worldview'

// Props 类型定义
interface Props {
  worldviewId: number
  factions: Faction[]
  loading?: boolean
}

// 表单接口
interface FactionForm {
  name: string
  faction_type: string
  description: string
  leader: string
  territory: string
  power_level: string
  ideology: string
  member_count: string
  allies: string[]
  enemies: string[]
}

const props = defineProps<Props>()

const emit = defineEmits<{
  create: [data: Omit<Faction, 'id' | 'user_id' | 'created_at' | 'updated_at'>]
  update: [id: number, data: Partial<Faction>]
  delete: [id: number]
  refresh: []
}>()

// 状态
const showCreateDialog = ref(false)
const showGenerateDialog = ref(false)
const submitting = ref(false)
const generating = ref(false)
const isEdit = ref(false)
const currentFactionId = ref<number | null>(null)

// 表单
const formRef = ref<FormInstance>()
const form = reactive<FactionForm>({
  name: '',
  faction_type: '',
  description: '',
  leader: '',
  territory: '',
  power_level: '',
  ideology: '',
  member_count: '',
  allies: [],
  enemies: []
})

const generateForm = reactive({
  count: 3,
  faction_types: ['sect', 'empire'],
  include: ['leader', 'territory', 'ideology', 'relations'],
  suggestion: ''
})

// 验证规则
const rules = {
  name: [
    { required: true, message: '请输入势力名称', trigger: 'blur' },
    { max: 100, message: '名称不能超过100个字符', trigger: 'blur' }
  ],
  faction_type: [
    { required: true, message: '请选择势力类型', trigger: 'change' }
  ],
  description: [
    { required: true, message: '请输入势力描述', trigger: 'blur' }
  ]
}

// 计算属性
const groupedFactions = computed(() => {
  const groups: Record<string, Faction[]> = {}
  
  props.factions.forEach(faction => {
    if (!groups[faction.faction_type]) {
      groups[faction.faction_type] = []
    }
    groups[faction.faction_type].push(faction)
  })
  
  return Object.entries(groups).map(([type, items]) => ({
    type,
    items: items.sort((a, b) => a.name.localeCompare(b.name))
  }))
})

const otherFactions = computed(() => {
  return props.factions.filter(f => f.id !== currentFactionId.value)
})

// 方法
const resetForm = () => {
  formRef.value?.resetFields()
  Object.assign(form, {
    name: '',
    faction_type: '',
    description: '',
    leader: '',
    territory: '',
    power_level: '',
    ideology: '',
    member_count: '',
    allies: [],
    enemies: []
  })
  isEdit.value = false
  currentFactionId.value = null
}

const submitForm = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    submitting.value = true

    if (isEdit.value && currentFactionId.value) {
      // 更新
      emit('update', currentFactionId.value, form)
    } else {
      // 创建
      emit('create', {
        worldview_id: props.worldviewId,
        ...form
      })
    }

    showCreateDialog.value = false
    ElMessage.success(isEdit.value ? '势力更新成功' : '势力创建成功')
  } catch (error) {
    console.error('表单提交失败:', error)
    if (error !== false) { // 不是验证错误
      ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
    }
  } finally {
    submitting.value = false
  }
}

const handleEdit = (faction: Faction) => {
  isEdit.value = true
  currentFactionId.value = faction.id
  Object.assign(form, {
    name: faction.name,
    faction_type: faction.faction_type,
    description: faction.description || '',
    leader: faction.leader || '',
    territory: faction.territory || '',
    power_level: faction.power_level || '',
    ideology: faction.ideology || '',
    member_count: faction.member_count || '',
    allies: faction.allies || [],
    enemies: faction.enemies || []
  })
  showCreateDialog.value = true
}

const handleDelete = async (faction: Faction) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除这个势力吗？',
      '确认删除',
      {
        type: 'warning'
      }
    )
    emit('delete', faction.id)
    ElMessage.success('势力删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

const getTypeLabel = (type: string): string => {
  const typeMap: Record<string, string> = {
    sect: '宗门',
    empire: '帝国',
    organization: '组织',
    power: '势力',
    tribe: '部落',
    other: '其他'
  }
  return typeMap[type] || type
}

const getPowerType = (level?: string): string => {
  switch (level) {
    case 'supreme':
      return 'danger'
    case 'top':
      return 'warning'
    case 'high':
      return 'success'
    case 'medium':
      return 'info'
    case 'low':
      return ''
    default:
      return ''
  }
}

const generateFactions = () => {
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
.factions-section {
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

.factions-content {
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

.factions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  padding: 20px;
}

.faction-group {
  .group-header {
    display: flex;
    justify-content: space-between;
    align-items: center;

    h4 {
      margin: 0;
      font-size: 16px;
    }
  }
}

.faction-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.faction-content {
  .faction-description {
    margin: 0 0 16px;
    font-size: 14px;
    color: #606266;
  }

  .faction-details {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 12px;
    margin-bottom: 16px;

    .detail-item {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 13px;

      strong {
        color: #303133;
      }
    }
  }

  .detail-block {
    margin: 12px 0;
    font-size: 13px;

    strong {
      color: #303133;
    }

    p {
      margin: 4px 0;
      color: #606266;
    }
  }

  .faction-relations {
    margin-top: 16px;
    display: flex;
    flex-direction: column;
    gap: 12px;

    .relation-group {
      strong {
        display: block;
        margin-bottom: 8px;
        color: #303133;
        font-size: 13px;
      }

      .relation-tags {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
      }
    }
  }
}

:deep(.el-collapse) {
  border: none;
}

:deep(.el-collapse-item__header) {
  background: #f5f7fa;
  border-radius: 4px;
  padding: 0 12px;
}

:deep(.el-collapse-item__content) {
  padding: 20px;
}
</style>