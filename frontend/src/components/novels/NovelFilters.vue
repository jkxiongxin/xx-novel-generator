<template>
  <div class="novel-filters">
    <el-card class="filter-card" shadow="never">
      <div class="filter-content">
        <!-- 左侧筛选器 -->
        <div class="filter-left">
          <div class="filter-item">
            <label class="filter-label">状态筛选：</label>
            <el-select 
              v-model="localFilters.status" 
              placeholder="选择状态" 
              clearable
              size="default"
              style="width: 120px;"
              @change="emitFiltersChange"
            >
              <el-option label="草稿" value="draft" />
              <el-option label="进行中" value="ongoing" />
              <el-option label="已完成" value="completed" />
              <el-option label="暂停" value="paused" />
            </el-select>
          </div>

          <div class="filter-item">
            <label class="filter-label">类型筛选：</label>
            <el-select 
              v-model="localFilters.genre" 
              placeholder="选择类型" 
              clearable
              size="default"
              style="width: 120px;"
              @change="emitFiltersChange"
            >
              <el-option label="奇幻" value="fantasy" />
              <el-option label="言情" value="romance" />
              <el-option label="悬疑" value="mystery" />
              <el-option label="科幻" value="scifi" />
              <el-option label="历史" value="historical" />
              <el-option label="现代" value="modern" />
              <el-option label="武侠" value="martial_arts" />
              <el-option label="都市" value="urban" />
              <el-option label="游戏" value="game" />
              <el-option label="其他" value="other" />
            </el-select>
          </div>

          <div class="filter-item">
            <label class="filter-label">创建时间：</label>
            <el-date-picker
              v-model="dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              size="default"
              style="width: 220px;"
              @change="handleDateChange"
            />
          </div>

          <div class="filter-item">
            <label class="filter-label">排序：</label>
            <el-select 
              v-model="localSortConfig.sortBy" 
              placeholder="排序字段" 
              size="default"
              style="width: 120px;"
              @change="emitSortChange"
            >
              <el-option label="更新时间" value="updated_at" />
              <el-option label="创建时间" value="created_at" />
              <el-option label="标题" value="title" />
              <el-option label="字数" value="word_count" />
            </el-select>
            <el-select 
              v-model="localSortConfig.sortOrder" 
              placeholder="排序方向" 
              size="default"
              style="width: 100px; margin-left: 8px;"
              @change="emitSortChange"
            >
              <el-option label="降序" value="desc" />
              <el-option label="升序" value="asc" />
            </el-select>
          </div>

          <div class="filter-item" v-if="hasActiveFilters">
            <el-button 
              type="info" 
              text 
              size="default"
              @click="handleReset"
              :icon="RefreshLeft"
            >
              重置筛选
            </el-button>
          </div>
        </div>

        <!-- 右侧操作区 -->
        <div class="filter-right">
          <div class="view-mode-switch">
            <el-button-group>
              <el-button
                :type="viewMode === 'grid' ? 'primary' : 'default'"
                :icon="Grid"
                @click="handleViewModeChange('grid')"
                size="default"
              >
                网格
              </el-button>
              <el-button
                :type="viewMode === 'table' ? 'primary' : 'default'"
                :icon="List"
                @click="handleViewModeChange('table')"
                size="default"
              >
                列表
              </el-button>
            </el-button-group>
          </div>

          <el-button 
            :icon="Refresh" 
            @click="$emit('refresh')"
            :loading="loading"
            size="default"
            title="刷新数据"
          />
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { RefreshLeft, Refresh, Grid, List } from '@element-plus/icons-vue'

// Props
interface Props {
  filters: {
    status: string | null
    genre: string | null
    dateFrom: string | null
    dateTo: string | null
  }
  sortConfig: {
    sortBy: string
    sortOrder: string
  }
  viewMode: 'grid' | 'table'
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  loading: false
})

// Emits
const emit = defineEmits<{
  'update:filters': [filters: typeof props.filters]
  'update:sortConfig': [sortConfig: typeof props.sortConfig]
  'update:viewMode': [viewMode: 'grid' | 'table']
  'reset': []
  'refresh': []
}>()

// 本地状态
const localFilters = ref({ ...props.filters })
const localSortConfig = ref({ ...props.sortConfig })
const dateRange = ref<[Date, Date] | null>(null)

// 计算属性
const hasActiveFilters = computed(() => {
  return !!(
    localFilters.value.status ||
    localFilters.value.genre ||
    localFilters.value.dateFrom ||
    localFilters.value.dateTo
  )
})

// 监听props变化
watch(() => props.filters, (newFilters) => {
  localFilters.value = { ...newFilters }
  // 更新日期范围
  if (newFilters.dateFrom && newFilters.dateTo) {
    dateRange.value = [new Date(newFilters.dateFrom), new Date(newFilters.dateTo)]
  } else {
    dateRange.value = null
  }
}, { deep: true })

watch(() => props.sortConfig, (newSortConfig) => {
  localSortConfig.value = { ...newSortConfig }
}, { deep: true })

// 方法
const emitFiltersChange = () => {
  emit('update:filters', { ...localFilters.value })
}

const emitSortChange = () => {
  emit('update:sortConfig', { ...localSortConfig.value })
}

const handleDateChange = (dates: [Date, Date] | null) => {
  if (dates) {
    localFilters.value.dateFrom = dates[0].toISOString().split('T')[0]
    localFilters.value.dateTo = dates[1].toISOString().split('T')[0]
  } else {
    localFilters.value.dateFrom = null
    localFilters.value.dateTo = null
  }
  emitFiltersChange()
}

const handleViewModeChange = (mode: 'grid' | 'table') => {
  emit('update:viewMode', mode)
}

const handleReset = () => {
  localFilters.value = {
    status: null,
    genre: null,
    dateFrom: null,
    dateTo: null
  }
  dateRange.value = null
  emit('reset')
}
</script>

<style lang="scss" scoped>
.novel-filters {
  margin-bottom: 20px;

  .filter-card {
    border: 1px solid #e4e7ed;
    
    :deep(.el-card__body) {
      padding: 16px 20px;
    }
  }

  .filter-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 16px;
  }

  .filter-left {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 16px;
    flex: 1;
  }

  .filter-item {
    display: flex;
    align-items: center;
    gap: 8px;

    .filter-label {
      font-size: 14px;
      color: #606266;
      white-space: nowrap;
      font-weight: 500;
    }
  }

  .filter-right {
    display: flex;
    align-items: center;
    gap: 12px;
    flex-shrink: 0;
  }

  .view-mode-switch {
    :deep(.el-button-group) {
      .el-button {
        border-color: #dcdfe6;
        
        &.el-button--primary {
          background-color: #409eff;
          border-color: #409eff;
        }
      }
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  .novel-filters {
    .filter-content {
      flex-direction: column;
      align-items: stretch;
    }

    .filter-left {
      flex-direction: column;
      align-items: stretch;
    }

    .filter-item {
      flex-direction: column;
      align-items: flex-start;
      
      .filter-label {
        margin-bottom: 4px;
      }
    }

    .filter-right {
      justify-content: space-between;
      margin-top: 12px;
    }
  }
}
</style>