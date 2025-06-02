<template>
  <div class="page-header">
    <el-card class="header-card" shadow="never">
      <div class="header-content">
        <!-- 左侧标题和统计 -->
        <div class="header-left">
          <div class="page-title">
            <h1>我的小说</h1>
            <div class="quick-stats" v-if="!loading">
              <span class="stat-item">
                <el-icon><Document /></el-icon>
                {{ stats.totalNovels }} 部作品
              </span>
              <span class="stat-item">
                <el-icon><EditPen /></el-icon>
                {{ stats.totalWords }} 字
              </span>
              <span class="stat-item" v-if="stats.activeNovels > 0">
                <el-icon><Clock /></el-icon>
                {{ stats.activeNovels }} 部进行中
              </span>
            </div>
          </div>
        </div>

        <!-- 右侧操作区 -->
        <div class="header-right">
          <div class="action-buttons">
            <!-- 搜索框 -->
            <div class="search-box">
              <el-input
                v-model="searchKeyword"
                placeholder="搜索小说标题或描述..."
                clearable
                size="default"
                style="width: 280px;"
                :prefix-icon="Search"
                @input="handleSearchInput"
                @clear="handleSearchClear"
                @keyup.enter="handleSearchEnter"
              />
            </div>

            <!-- 刷新按钮 -->
            <el-button 
              :icon="Refresh" 
              @click="$emit('refresh')"
              :loading="loading"
              size="default"
              title="刷新数据"
            />

            <!-- 创建小说按钮 -->
            <el-button 
              type="primary" 
              :icon="Plus"
              @click="$emit('create-novel')"
              size="default"
            >
              创建小说
            </el-button>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { debounce } from 'lodash-es'
import { 
  Document, EditPen, Clock, Search, Refresh, Plus 
} from '@element-plus/icons-vue'
import { NovelService } from '@/api/novels'
import { ElMessage } from 'element-plus'

// Props
interface Props {
  loading?: boolean
}

defineProps<Props>()

// Emits
const emit = defineEmits<{
  'create-novel': []
  'refresh': []
  'search': [keyword: string]
}>()

// 响应式数据
const searchKeyword = ref('')
const stats = ref({
  totalNovels: 0,
  totalWords: 0,
  activeNovels: 0,
  completedNovels: 0
})

// 生命周期
onMounted(async () => {
  await loadStats()
})

// 方法
const loadStats = async () => {
  try {
    const response: any = await NovelService.getNovelStats()
    if (response.status === 'success') {
      stats.value = {
        totalNovels: response.data.total_novels,
        totalWords: response.data.total_words,
        activeNovels: response.data.active_novels,
        completedNovels: response.data.completed_novels
      }
    } else {
      // 兼容直接返回统计数据的格式
      stats.value = {
        totalNovels: response.total_novels || 0,
        totalWords: response.total_word_count || 0,
        activeNovels: 0,
        completedNovels: 0
      }
    }
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

// 搜索相关方法
const handleSearchInput = debounce((value: string) => {
  emit('search', value.trim())
}, 300)

const handleSearchClear = () => {
  emit('search', '')
}

const handleSearchEnter = () => {
  emit('search', searchKeyword.value.trim())
}

// 暴露方法供父组件调用
defineExpose({
  loadStats
})
</script>

<style lang="scss" scoped>
.page-header {
  margin-bottom: 20px;

  .header-card {
    border: 1px solid #e4e7ed;
    
    :deep(.el-card__body) {
      padding: 20px 24px;
    }
  }

  .header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 20px;
  }

  .header-left {
    flex: 1;
    min-width: 300px;

    .page-title {
      h1 {
        margin: 0 0 8px 0;
        font-size: 24px;
        font-weight: 600;
        color: #303133;
        line-height: 1.2;
      }

      .quick-stats {
        display: flex;
        gap: 20px;
        flex-wrap: wrap;

        .stat-item {
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 14px;
          color: #606266;

          .el-icon {
            color: #909399;
          }
        }
      }
    }
  }

  .header-right {
    flex-shrink: 0;

    .action-buttons {
      display: flex;
      align-items: center;
      gap: 12px;

      .search-box {
        :deep(.el-input) {
          .el-input__wrapper {
            border-radius: 6px;
            box-shadow: 0 0 0 1px #dcdfe6 inset;

            &:hover {
              box-shadow: 0 0 0 1px #c0c4cc inset;
            }

            &.is-focus {
              box-shadow: 0 0 0 1px #409eff inset;
            }
          }
        }
      }
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  .page-header {
    .header-content {
      flex-direction: column;
      align-items: stretch;
    }

    .header-left {
      min-width: auto;

      .page-title {
        text-align: center;

        h1 {
          font-size: 20px;
        }

        .quick-stats {
          justify-content: center;
          gap: 16px;

          .stat-item {
            font-size: 13px;
          }
        }
      }
    }

    .header-right {
      .action-buttons {
        flex-direction: column;
        gap: 10px;

        .search-box {
          width: 100%;

          :deep(.el-input) {
            width: 100% !important;
          }
        }
      }
    }
  }
}

// 平板设备
@media (max-width: 1024px) and (min-width: 769px) {
  .page-header {
    .header-right {
      .action-buttons {
        .search-box {
          :deep(.el-input) {
            width: 240px !important;
          }
        }
      }
    }
  }
}

// 超大屏幕
@media (min-width: 1200px) {
  .page-header {
    .header-right {
      .action-buttons {
        .search-box {
          :deep(.el-input) {
            width: 320px !important;
          }
        }
      }
    }
  }
}
</style>