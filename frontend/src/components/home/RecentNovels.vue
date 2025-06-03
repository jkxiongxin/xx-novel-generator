<template>
  <section class="recent-novels-section">
    <div class="novels-container">
      <!-- 标题区域 -->
      <div class="section-header">
        <h2 class="section-title">📚 最近编辑</h2>
        <div class="header-actions">
          <el-button 
            type="primary" 
            @click="navigateToNovels"
            plain
            class="view-all-btn"
          >
            查看全部
          </el-button>
        </div>
      </div>
      
      <!-- 加载状态 -->
      <div v-if="loading" class="loading-container">
        <div class="skeleton-grid">
          <el-skeleton 
            v-for="i in 6" 
            :key="i"
            animated
            class="skeleton-card"
          >
            <template #template>
              <el-skeleton-item variant="image" style="width: 100%; height: 200px;" />
              <div style="padding: 16px;">
                <el-skeleton-item variant="h3" style="width: 80%;" />
                <el-skeleton-item variant="text" style="width: 100%; margin-top: 8px;" />
                <el-skeleton-item variant="text" style="width: 60%; margin-top: 8px;" />
              </div>
            </template>
          </el-skeleton>
        </div>
      </div>
      
      <!-- 小说列表 -->
      <div v-else-if="novels.length > 0" class="novels-grid">
        <div 
          v-for="(novel, index) in novels" 
          :key="novel.id"
          class="novel-card"
          :class="{ 'animate': showAnimation }"
          :style="{ 'animation-delay': `${index * 0.1}s` }"
          @click="handleNovelClick(novel)"
        >
          <!-- 封面图片 -->
          <div class="novel-cover">
            <img 
              v-if="novel.cover_image" 
              :src="novel.cover_image" 
              :alt="novel.title"
              class="cover-image"
              @error="handleImageError"
            />
            <div v-else class="default-cover">
              <el-icon :size="40" class="cover-icon">
                <Document />
              </el-icon>
              <span class="cover-genre">{{ getGenreText(novel.genre) }}</span>
            </div>
            
            <!-- 状态标签 -->
            <div class="status-badge">
              <el-tag 
                :type="getStatusType(novel.status)" 
                size="small"
                round
              >
                {{ getStatusText(novel.status) }}
              </el-tag>
            </div>
            
            <!-- 悬停操作 -->
            <div class="cover-overlay">
              <div class="overlay-actions">
                <el-button 
                  type="primary" 
                  size="small"
                  @click.stop="handleContinueEdit(novel)"
                  circle
                >
                  <el-icon><EditPen /></el-icon>
                </el-button>
                <el-button 
                  size="small"
                  @click.stop="handleViewDetail(novel)"
                  circle
                >
                  <el-icon><View /></el-icon>
                </el-button>
              </div>
            </div>
          </div>
          
          <!-- 小说信息 -->
          <div class="novel-info">
            <h3 class="novel-title" :title="novel.title">
              {{ novel.title }}
            </h3>
            
            <p class="novel-description" :title="novel.description">
              {{ novel.description || '暂无简介' }}
            </p>
            
            <!-- 统计信息 -->
            <div class="novel-stats">
              <span class="stat-item">
                <el-icon><Document /></el-icon>
                {{ novel.chapter_count || 0 }}章
              </span>
              <span class="stat-item">
                <el-icon><EditPen /></el-icon>
                {{ formatWordCount(novel.word_count || 0) }}
              </span>
            </div>
            
            <!-- 最后编辑信息 -->
            <div class="last-edit">
              <span class="edit-time">
                {{ formatDate(novel.updated_at) }}
              </span>
              <span v-if="novel.last_chapter_title" class="last-chapter">
                最后编辑：{{ novel.last_chapter_title }}
              </span>
            </div>
            
            <!-- 操作按钮 -->
            <div class="novel-actions">
              <el-button
                type="primary"
                size="small"
                @click.stop="handleContinueEdit(novel)"
                class="continue-btn"
              >
                继续编辑
              </el-button>
              <el-button
                size="small"
                @click.stop="handleViewDetail(novel)"
                class="detail-btn"
              >
                <el-icon><View /></el-icon>
                详情
              </el-button>
              <el-dropdown
                @command="(command: string) => handleDropdownCommand(command, novel)"
                trigger="click"
                @click.stop
              >
                <el-button size="small" class="more-btn">
                  <el-icon><MoreFilled /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="workspace">
                      <el-icon><FolderOpened /></el-icon>
                      进入工作台
                    </el-dropdown-item>
                    <el-dropdown-item command="export" divided>
                      <el-icon><Download /></el-icon>
                      导出小说
                    </el-dropdown-item>
                    <el-dropdown-item command="delete" class="danger-item">
                      <el-icon><Delete /></el-icon>
                      删除
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 空状态 -->
      <div v-else class="empty-state">
        <div class="empty-illustration">
          <el-icon :size="80" color="#c0c4cc">
            <DocumentAdd />
          </el-icon>
        </div>
        <h3 class="empty-title">还没有创作任何小说</h3>
        <p class="empty-description">
          开始你的第一部作品，让AI成为你的创作伙伴
        </p>
        <el-button 
          type="primary" 
          size="large"
          @click="handleCreateFirst"
          class="create-first-btn"
        >
          <el-icon><EditPen /></el-icon>
          创建我的第一部小说
        </el-button>
      </div>
      
      <!-- 错误状态 -->
      <div v-if="error" class="error-state">
        <div class="error-illustration">
          <el-icon :size="80" color="#f56c6c">
            <WarningFilled />
          </el-icon>
        </div>
        <h3 class="error-title">加载失败</h3>
        <p class="error-description">
          {{ error }}
        </p>
        <el-button 
          type="primary" 
          @click="loadRecentNovels"
          class="retry-btn"
        >
          重新加载
        </el-button>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Document,
  EditPen,
  View,
  MoreFilled,
  FolderOpened,
  Download,
  Delete,
  DocumentAdd,
  WarningFilled
} from '@element-plus/icons-vue'
import { 
  HomepageService, 
  HomepageUtils, 
  type RecentNovel 
} from '@/api/homepage'

const router = useRouter()

// 响应式数据
const loading = ref(true)
const novels = ref<RecentNovel[]>([])
const error = ref<string>('')
const showAnimation = ref(false)

// 工具函数
const formatWordCount = HomepageUtils.formatWordCount
const formatDate = HomepageUtils.formatDate
const getStatusColor = HomepageUtils.getStatusColor
const getStatusText = HomepageUtils.getStatusText
const getGenreText = HomepageUtils.getGenreText

// 获取状态类型
const getStatusType = (status: string) => {
  const typeMap = {
    'draft': 'info',
    'ongoing': 'primary',
    'completed': 'success'
  }
  return typeMap[status as keyof typeof typeMap] || 'info'
}

// 加载最近小说
const loadRecentNovels = async () => {
  try {
    loading.value = true
    error.value = ''
    
    const response = await HomepageService.getRecentNovels(6)
    novels.value = response.novels
    
    // 启动动画
    setTimeout(() => {
      showAnimation.value = true
    }, 100)
    
  } catch (err: any) {
    console.error('加载最近小说失败:', err)
    error.value = err.response?.data?.message || '网络错误，请重试'
  } finally {
    loading.value = false
  }
}

// 处理图片加载错误
const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  img.style.display = 'none'
}

// 处理小说卡片点击
const handleNovelClick = (novel: RecentNovel) => {
  router.push(`/novels/${novel.id}`)
}

// 处理继续编辑
const handleContinueEdit = (novel: RecentNovel) => {
  router.push(`/workspace/${novel.id}/chapters`)
}

// 处理查看详情
const handleViewDetail = (novel: RecentNovel) => {
  router.push(`/novels/${novel.id}`)
}

// 处理下拉菜单命令
const handleDropdownCommand = (command: string, novel: RecentNovel) => {
  switch (command) {
    case 'view':
      handleViewDetail(novel)
      break
    case 'workspace':
      router.push(`/workspace/${novel.id}`)
      break
    case 'export':
      handleExportNovel(novel)
      break
    case 'delete':
      handleDeleteNovel(novel)
      break
  }
}

// 处理导出小说
const handleExportNovel = (novel: RecentNovel) => {
  ElMessage.info('导出功能即将推出')
}

// 处理删除小说
const handleDeleteNovel = async (novel: RecentNovel) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除小说《${novel.title}》吗？此操作不可恢复。`,
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }
    )
    
    // TODO: 调用删除API
    ElMessage.success('删除成功')
    
    // 重新加载列表
    loadRecentNovels()
    
  } catch {
    // 用户取消操作
  }
}

// 处理创建第一部小说
const handleCreateFirst = () => {
  router.push('/novels/create')
}

// 跳转到小说列表
const navigateToNovels = () => {
  router.push('/novels')
}

// 生命周期
onMounted(() => {
  // 检查登录状态
  const isLoggedIn = !!localStorage.getItem('access_token')
  if (isLoggedIn) {
    loadRecentNovels()
  } else {
    loading.value = false
  }
})
</script>

<style scoped>
.recent-novels-section {
  padding: 80px 0;
  background: #f8fafc;
}

.novels-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 40px;
}

.section-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: #2d3748;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.view-all-btn {
  border-radius: 8px;
}

/* 加载状态 */
.loading-container {
  margin-top: 20px;
}

.skeleton-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 24px;
}

.skeleton-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
}

/* 小说网格 */
.novels-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
}

.novel-card {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transform: translateY(20px);
  opacity: 0;
}

.novel-card.animate {
  transform: translateY(0);
  opacity: 1;
}

.novel-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
}

/* 封面区域 */
.novel-cover {
  position: relative;
  height: 200px;
  background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
  overflow: hidden;
}

.cover-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.default-cover {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #a0aec0;
}

.cover-icon {
  margin-bottom: 8px;
}

.cover-genre {
  font-size: 14px;
  font-weight: 500;
}

.status-badge {
  position: absolute;
  top: 12px;
  left: 12px;
}

.cover-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.novel-card:hover .cover-overlay {
  opacity: 1;
}

.overlay-actions {
  display: flex;
  gap: 12px;
}

/* 小说信息 */
.novel-info {
  padding: 20px;
}

.novel-title {
  font-size: 1.2rem;
  font-weight: 600;
  color: #2d3748;
  margin: 0 0 8px 0;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.novel-description {
  color: #718096;
  font-size: 14px;
  line-height: 1.5;
  margin: 0 0 12px 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.novel-stats {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #a0aec0;
}

.last-edit {
  font-size: 12px;
  color: #a0aec0;
  margin-bottom: 16px;
}

.edit-time {
  margin-right: 8px;
}

.last-chapter {
  display: block;
  margin-top: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.novel-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.continue-btn {
  flex: 1;
  border-radius: 8px;
}

.detail-btn {
  border-radius: 8px;
}

.more-btn {
  width: 32px;
  height: 32px;
  border-radius: 8px;
}

/* 下拉菜单样式 */
:deep(.danger-item) {
  color: #f56c6c !important;
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 60px 20px;
  background: white;
  border-radius: 16px;
  margin-top: 20px;
}

.empty-illustration {
  margin-bottom: 24px;
}

.empty-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #4a5568;
  margin: 0 0 12px 0;
}

.empty-description {
  color: #718096;
  margin: 0 0 32px 0;
  line-height: 1.6;
}

.create-first-btn {
  border-radius: 12px;
  padding: 12px 24px;
}

/* 错误状态 */
.error-state {
  text-align: center;
  padding: 60px 20px;
  background: white;
  border-radius: 16px;
  margin-top: 20px;
}

.error-illustration {
  margin-bottom: 24px;
}

.error-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #e53e3e;
  margin: 0 0 12px 0;
}

.error-description {
  color: #718096;
  margin: 0 0 32px 0;
}

.retry-btn {
  border-radius: 12px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .recent-novels-section {
    padding: 60px 0;
  }
  
  .novels-container {
    padding: 0 16px;
  }
  
  .section-title {
    font-size: 2rem;
  }
  
  .section-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .novels-grid {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .novel-cover {
    height: 160px;
  }
  
  .novel-info {
    padding: 16px;
  }
  
  .empty-state,
  .error-state {
    padding: 40px 20px;
  }
}

@media (max-width: 480px) {
  .novel-stats {
    flex-direction: column;
    gap: 8px;
  }
  
  .novel-actions {
    flex-direction: column;
    gap: 12px;
  }
  
  .continue-btn,
  .detail-btn {
    width: 100%;
  }
  
  .more-btn {
    width: 100%;
    height: 32px;
  }
}

/* 动画效果 */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.novel-card.animate {
  animation: fadeInUp 0.6s ease-out forwards;
}
</style>