<template>
  <div class="batch-operation-bar" v-if="selectedCount > 0">
    <el-card class="operation-card" shadow="always">
      <div class="operation-content">
        <!-- 左侧选择信息 -->
        <div class="selection-info">
          <el-icon class="info-icon"><Select /></el-icon>
          <span class="selection-text">已选择 <strong>{{ selectedCount }}</strong> 项</span>
          <el-button 
            type="text" 
            size="small"
            @click="$emit('clear-selection')"
            class="clear-btn"
          >
            取消选择
          </el-button>
        </div>

        <!-- 右侧操作按钮 -->
        <div class="operation-buttons">
          <el-button-group>
            <!-- 批量修改状态 -->
            <el-dropdown 
              @command="handleStatusChange"
              placement="top"
            >
              <el-button 
                size="default"
                :icon="Edit"
                :loading="loading"
              >
                修改状态
                <el-icon class="el-icon--right"><ArrowDown /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="draft">
                    <el-tag type="info" size="small" effect="light">草稿</el-tag>
                    <span style="margin-left: 8px;">设为草稿</span>
                  </el-dropdown-item>
                  <el-dropdown-item command="ongoing">
                    <el-tag type="warning" size="small" effect="light">进行中</el-tag>
                    <span style="margin-left: 8px;">设为进行中</span>
                  </el-dropdown-item>
                  <el-dropdown-item command="completed">
                    <el-tag type="success" size="small" effect="light">已完成</el-tag>
                    <span style="margin-left: 8px;">设为已完成</span>
                  </el-dropdown-item>
                  <el-dropdown-item command="paused">
                    <el-tag type="danger" size="small" effect="light">暂停</el-tag>
                    <span style="margin-left: 8px;">设为暂停</span>
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>

            <!-- 批量导出 -->
            <el-dropdown 
              @command="handleExport"
              placement="top"
            >
              <el-button 
                size="default"
                :icon="Download"
                :loading="loading"
              >
                批量导出
                <el-icon class="el-icon--right"><ArrowDown /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="txt">
                    <el-icon><Document /></el-icon>
                    <span style="margin-left: 8px;">导出为 TXT</span>
                  </el-dropdown-item>
                  <el-dropdown-item command="docx">
                    <el-icon><Document /></el-icon>
                    <span style="margin-left: 8px;">导出为 DOCX</span>
                  </el-dropdown-item>
                  <el-dropdown-item command="pdf">
                    <el-icon><Document /></el-icon>
                    <span style="margin-left: 8px;">导出为 PDF</span>
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>

            <!-- 批量删除 -->
            <el-button 
              type="danger"
              size="default"
              :icon="Delete"
              :loading="loading"
              @click="handleDelete"
            >
              批量删除
            </el-button>
          </el-button-group>
        </div>
      </div>
    </el-card>

    <!-- 确认删除对话框 -->
    <el-dialog
      v-model="showDeleteConfirm"
      title="批量删除确认"
      width="450px"
      align-center
    >
      <div class="delete-confirm-content">
        <div class="warning-icon">
          <el-icon :size="48" color="#E6A23C"><WarningFilled /></el-icon>
        </div>
        <div class="confirm-text">
          <p class="main-text">确定要删除选中的 <strong>{{ selectedCount }}</strong> 部小说吗？</p>
          <p class="sub-text">此操作不可恢复，请谨慎操作。</p>
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showDeleteConfirm = false">取消</el-button>
          <el-button 
            type="danger" 
            @click="confirmDelete"
            :loading="loading"
          >
            确定删除
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { 
  Select, Edit, Download, Delete, ArrowDown, 
  Document, WarningFilled 
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// Props
interface Props {
  selectedCount: number
  loading?: boolean
}

defineProps<Props>()

// Emits
const emit = defineEmits<{
  'batch-delete': []
  'batch-export': [format: string]
  'batch-status-change': [status: string]
  'clear-selection': []
}>()

// 响应式数据
const showDeleteConfirm = ref(false)

// 方法
const handleStatusChange = (status: string) => {
  emit('batch-status-change', status)
}

const handleExport = (format: string) => {
  emit('batch-export', format)
}

const handleDelete = () => {
  showDeleteConfirm.value = true
}

const confirmDelete = () => {
  showDeleteConfirm.value = false
  emit('batch-delete')
}
</script>

<style lang="scss" scoped>
.batch-operation-bar {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 1000;
  max-width: 1200px;
  width: calc(100% - 40px);

  .operation-card {
    border-radius: 12px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
    border: 1px solid #e4e7ed;

    :deep(.el-card__body) {
      padding: 16px 24px;
    }
  }

  .operation-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 20px;
  }

  .selection-info {
    display: flex;
    align-items: center;
    gap: 8px;
    color: #606266;

    .info-icon {
      color: #409eff;
    }

    .selection-text {
      font-size: 14px;
      
      strong {
        color: #409eff;
        font-weight: 600;
      }
    }

    .clear-btn {
      color: #909399;
      padding: 0;
      
      &:hover {
        color: #409eff;
      }
    }
  }

  .operation-buttons {
    :deep(.el-button-group) {
      .el-button {
        border-color: #dcdfe6;
        
        &:not(.el-button--danger) {
          &:hover {
            border-color: #409eff;
            color: #409eff;
          }
        }
      }
    }
  }
}

.delete-confirm-content {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 20px 0;

  .warning-icon {
    flex-shrink: 0;
  }

  .confirm-text {
    flex: 1;

    .main-text {
      font-size: 16px;
      color: #303133;
      margin: 0 0 8px 0;
      line-height: 1.4;

      strong {
        color: #E6A23C;
      }
    }

    .sub-text {
      font-size: 14px;
      color: #909399;
      margin: 0;
      line-height: 1.4;
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  .batch-operation-bar {
    bottom: 10px;
    width: calc(100% - 20px);

    .operation-content {
      flex-direction: column;
      gap: 12px;
      align-items: stretch;
    }

    .selection-info {
      justify-content: center;
    }

    .operation-buttons {
      :deep(.el-button-group) {
        width: 100%;
        display: flex;

        .el-button {
          flex: 1;
          font-size: 12px;
          padding: 8px 12px;
        }
      }

      :deep(.el-dropdown) {
        flex: 1;

        .el-button {
          width: 100%;
        }
      }
    }
  }

  .delete-confirm-content {
    flex-direction: column;
    text-align: center;
    gap: 12px;
  }
}

// 平板设备
@media (max-width: 1024px) and (min-width: 769px) {
  .batch-operation-bar {
    .operation-buttons {
      :deep(.el-button-group) {
        .el-button {
          font-size: 13px;
          padding: 8px 16px;
        }
      }
    }
  }
}
</style>