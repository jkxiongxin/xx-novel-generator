<template>
  <div class="pagination-bar">
    <div class="pagination-info">
      <span class="info-text">
        共 <strong>{{ total }}</strong> 项，
        第 <strong>{{ currentPage }}</strong> / <strong>{{ totalPages }}</strong> 页
      </span>
    </div>

    <div class="pagination-controls">
      <el-pagination
        :current-page="currentPage"
        :page-size="pageSize"
        :page-sizes="pageSizeOptions"
        :total="total"
        :layout="layout"
        :small="isSmallScreen"
        @current-change="handlePageChange"
        @size-change="handleSizeChange"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

// Props
interface Props {
  currentPage: number
  pageSize: number
  total: number
  totalPages: number
  pageSizeOptions?: number[]
  layout?: string
  small?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  pageSizeOptions: () => [10, 20, 50, 100],
  layout: 'total, sizes, prev, pager, next, jumper',
  small: false
})

// Emits
const emit = defineEmits<{
  'page-change': [page: number]
  'size-change': [size: number]
}>()

// 计算属性
const isSmallScreen = computed(() => {
  if (props.small) return true
  return window.innerWidth < 768
})

const layout = computed(() => {
  if (isSmallScreen.value) {
    return 'prev, pager, next'
  }
  return props.layout
})

// 方法
const handlePageChange = (page: number) => {
  emit('page-change', page)
}

const handleSizeChange = (size: number) => {
  emit('size-change', size)
}
</script>

<style lang="scss" scoped>
.pagination-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 0;
  margin-top: 20px;
  border-top: 1px solid #f0f2f5;
  background: white;

  .pagination-info {
    .info-text {
      font-size: 14px;
      color: #606266;

      strong {
        color: #303133;
        font-weight: 600;
      }
    }
  }

  .pagination-controls {
    :deep(.el-pagination) {
      .el-pagination__total {
        color: #606266;
        font-size: 14px;
      }

      .el-pagination__sizes {
        .el-select {
          .el-input {
            .el-input__inner {
              font-size: 14px;
            }
          }
        }
      }

      .el-pager {
        li {
          background-color: transparent;
          color: #606266;
          font-size: 14px;
          min-width: 32px;
          height: 32px;
          line-height: 30px;

          &:hover {
            color: #409eff;
          }

          &.active {
            background-color: #409eff;
            color: #fff;
            border-radius: 4px;
          }
        }
      }

      .btn-prev,
      .btn-next {
        background-color: transparent;
        color: #606266;
        border-radius: 4px;
        width: 32px;
        height: 32px;

        &:hover {
          color: #409eff;
        }

        &.disabled {
          color: #c0c4cc;
          cursor: not-allowed;
        }
      }

      .el-pagination__jump {
        color: #606266;
        font-size: 14px;

        .el-input {
          .el-input__inner {
            font-size: 14px;
            height: 32px;
            line-height: 32px;
          }
        }
      }
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  .pagination-bar {
    flex-direction: column;
    gap: 16px;
    align-items: center;

    .pagination-info {
      order: 2;
    }

    .pagination-controls {
      order: 1;

      :deep(.el-pagination) {
        .el-pagination__sizes,
        .el-pagination__total,
        .el-pagination__jump {
          display: none;
        }

        .el-pager {
          li {
            min-width: 28px;
            height: 28px;
            line-height: 26px;
            font-size: 12px;
          }
        }

        .btn-prev,
        .btn-next {
          width: 28px;
          height: 28px;
          font-size: 12px;
        }
      }
    }
  }
}

// 平板设备
@media (max-width: 1024px) and (min-width: 769px) {
  .pagination-bar {
    .pagination-controls {
      :deep(.el-pagination) {
        .el-pagination__jump {
          display: none;
        }
      }
    }
  }
}

// 超小屏幕
@media (max-width: 480px) {
  .pagination-bar {
    .pagination-info {
      .info-text {
        font-size: 12px;
      }
    }

    .pagination-controls {
      :deep(.el-pagination) {
        .el-pager {
          li {
            min-width: 24px;
            height: 24px;
            line-height: 22px;
            font-size: 11px;
          }
        }

        .btn-prev,
        .btn-next {
          width: 24px;
          height: 24px;
          font-size: 11px;
        }
      }
    }
  }
}
</style>