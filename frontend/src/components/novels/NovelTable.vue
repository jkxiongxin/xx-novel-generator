<template>
  <div class="novel-table">
    <el-table
      :data="novels"
      v-loading="loading"
      @selection-change="handleSelectionChange"
      @row-click="handleRowClick"
      stripe
      style="width: 100%"
      :row-class-name="getRowClassName"
    >
      <!-- 选择列 -->
      <el-table-column 
        type="selection" 
        width="50"
        :selectable="() => true"
      />

      <!-- 小说标题 -->
      <el-table-column 
        prop="title" 
        label="小说标题" 
        min-width="200"
        show-overflow-tooltip
      >
        <template #default="{ row }">
          <div class="title-cell">
            <div class="title-content">
              <span class="novel-title">{{ row.title }}</span>
              <el-tag 
                :type="getStatusTagType(row.status)" 
                size="small"
                effect="light"
                style="margin-left: 8px;"
              >
                {{ NovelUtils.getStatusText(row.status) }}
              </el-tag>
            </div>
            <div class="title-meta" v-if="row.last_chapter_title">
              <span class="last-chapter">最新：{{ row.last_chapter_title }}</span>
            </div>
          </div>
        </template>
      </el-table-column>

      <!-- 类型 -->
      <el-table-column 
        prop="genre" 
        label="类型" 
        width="100"
        align="center"
      >
        <template #default="{ row }">
          {{ NovelUtils.getGenreText(row.genre) }}
        </template>
      </el-table-column>

      <!-- 字数统计 -->
      <el-table-column 
        label="字数统计" 
        width="120"
        align="center"
      >
        <template #default="{ row }">
          <div class="word-stats">
            <div class="word-count">{{ NovelUtils.formatWordCount(row.word_count) }}</div>
            <div class="chapter-count">{{ row.chapter_count }} 章</div>
          </div>
        </template>
      </el-table-column>

      <!-- 进度 -->
      <el-table-column 
        label="进度" 
        width="150"
        align="center"
      >
        <template #default="{ row }">
          <div class="progress-cell" v-if="row.target_words && row.target_words > 0">
            <div class="progress-info">
              <span class="progress-text">{{ NovelUtils.formatProgress(row.progress_percentage) }}</span>
              <span class="target-words">/{{ NovelUtils.formatWordCount(row.target_words) }}</span>
            </div>
            <el-progress 
              :percentage="row.progress_percentage" 
              :stroke-width="6"
              :color="NovelUtils.getProgressColor(row.progress_percentage)"
              :show-text="false"
            />
          </div>
          <span v-else class="no-target">未设目标</span>
        </template>
      </el-table-column>

      <!-- 更新时间 -->
      <el-table-column 
        label="更新时间" 
        width="120"
        align="center"
      >
        <template #default="{ row }">
          <div class="time-cell">
            <div class="relative-time">{{ NovelUtils.formatRelativeTime(row.updated_at) }}</div>
            <div class="absolute-time">{{ NovelUtils.formatDate(row.updated_at) }}</div>
          </div>
        </template>
      </el-table-column>

      <!-- 操作 -->
      <el-table-column 
        label="操作" 
        width="180"
        align="center"
        fixed="right"
      >
        <template #default="{ row }">
          <div class="action-buttons">
            <el-button
              type="primary"
              size="small"
              @click.stop="$emit('enter-workspace', row.id)"
            >
              工作台
            </el-button>

            <el-button
              size="small"
              @click.stop="$emit('view-detail', row.id)"
            >
              <el-icon><View /></el-icon>
              详情
            </el-button>

            <el-dropdown
              @click.stop
              trigger="click"
              placement="bottom-end"
            >
              <el-button
                type="default"
                size="small"
                :icon="MoreFilled"
              >
                更多
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item divided @click="$emit('export-novel', row)">
                    <el-icon><Download /></el-icon>
                    导出小说
                  </el-dropdown-item>
                  <el-dropdown-item @click="$emit('delete-novel', row)">
                    <el-icon><Delete /></el-icon>
                    <span style="color: #f56c6c;">删除小说</span>
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </template>
      </el-table-column>
    </el-table>

    <!-- 空状态 -->
    <div v-if="!loading && novels.length === 0" class="empty-state">
      <el-empty 
        description="暂无小说数据"
        :image-size="120"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import { 
  MoreFilled, View, Download, Delete 
} from '@element-plus/icons-vue'
import type { NovelListItem } from '@/api/novels'
import { NovelUtils } from '@/api/novels'

// Props
interface Props {
  novels: NovelListItem[]
  loading?: boolean
  selected: number[]
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  selected: () => []
})

// Emits
const emit = defineEmits<{
  'update:selected': [selected: number[]]
  'view-detail': [novelId: number]
  'enter-workspace': [novelId: number]
  'export-novel': [novel: NovelListItem]
  'delete-novel': [novel: NovelListItem]
}>()

// 表格引用
const tableRef = ref()

// 监听选中状态变化，同步表格选择
watch(() => props.selected, async (newSelected) => {
  await nextTick()
  if (tableRef.value) {
    // 清除当前选择
    tableRef.value.clearSelection()
    // 设置新的选择
    props.novels.forEach(novel => {
      if (newSelected.includes(novel.id)) {
        tableRef.value.toggleRowSelection(novel, true)
      }
    })
  }
}, { deep: true })

// 方法
const handleSelectionChange = (selection: NovelListItem[]) => {
  const selectedIds = selection.map(novel => novel.id)
  emit('update:selected', selectedIds)
}

const handleRowClick = (row: NovelListItem) => {
  // 行点击查看详情
  emit('view-detail', row.id)
}

const getRowClassName = ({ row }: { row: NovelListItem }) => {
  const isSelected = props.selected.includes(row.id)
  return isSelected ? 'selected-row' : ''
}

const getStatusTagType = (status: string): string => {
  const typeMap: Record<string, string> = {
    'draft': 'info',
    'ongoing': 'warning',
    'completed': 'success',
    'paused': 'danger'
  }
  return typeMap[status] || 'info'
}
</script>

<style lang="scss" scoped>
.novel-table {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);

  :deep(.el-table) {
    .el-table__header {
      background-color: #fafbfc;
      
      th {
        background-color: #fafbfc !important;
        color: #606266;
        font-weight: 600;
        border-bottom: 1px solid #ebeef5;
      }
    }

    .el-table__body {
      tr {
        cursor: pointer;
        transition: background-color 0.3s ease;

        &:hover {
          background-color: #f8f9fa !important;
        }

        &.selected-row {
          background-color: #ecf5ff !important;
        }

        td {
          border-bottom: 1px solid #f0f2f5;
          padding: 12px 0;
        }
      }
    }
  }

  .title-cell {
    .title-content {
      display: flex;
      align-items: center;
      margin-bottom: 4px;

      .novel-title {
        font-weight: 600;
        color: #303133;
        font-size: 14px;
      }
    }

    .title-meta {
      .last-chapter {
        font-size: 12px;
        color: #909399;
        display: inline-block;
        max-width: 200px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
    }
  }

  .word-stats {
    text-align: center;

    .word-count {
      font-weight: 600;
      color: #303133;
      font-size: 14px;
      margin-bottom: 2px;
    }

    .chapter-count {
      font-size: 12px;
      color: #909399;
    }
  }

  .progress-cell {
    .progress-info {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 4px;
      font-size: 12px;

      .progress-text {
        font-weight: 600;
        color: #303133;
      }

      .target-words {
        color: #909399;
      }
    }
  }

  .no-target {
    color: #c0c4cc;
    font-size: 12px;
  }

  .time-cell {
    text-align: center;

    .relative-time {
      font-weight: 500;
      color: #303133;
      font-size: 13px;
      margin-bottom: 2px;
    }

    .absolute-time {
      font-size: 11px;
      color: #909399;
    }
  }

  .action-buttons {
    display: flex;
    justify-content: center;
    gap: 8px;
  }

  .empty-state {
    padding: 60px 0;
    text-align: center;
    background: white;
  }
}

// 响应式设计
@media (max-width: 768px) {
  .novel-table {
    :deep(.el-table) {
      .el-table__header,
      .el-table__body {
        th, td {
          padding: 8px 4px;
          font-size: 12px;
        }
      }
    }

    .title-cell {
      .title-content .novel-title {
        font-size: 13px;
      }
    }

    .action-buttons {
      flex-direction: column;
      gap: 4px;

      .el-button {
        font-size: 11px;
        padding: 4px 8px;
      }
    }
  }
}
</style>