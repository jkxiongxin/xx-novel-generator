<template>
  <div class="system-notifications">
    <!-- 全局通知弹窗 -->
    <el-notification
      v-for="notification in activeNotifications"
      :key="notification.id"
      :title="notification.title"
      :message="notification.message"
      :type="notification.type"
      :duration="notification.duration"
      :show-close="notification.showClose"
      :position="notification.position"
      @close="handleNotificationClose(notification.id)"
    />
    
    <!-- 系统公告弹窗 -->
    <el-dialog
      v-model="showAnnouncementDialog"
      :title="currentAnnouncement?.title"
      width="500px"
      :before-close="handleAnnouncementClose"
      class="announcement-dialog"
    >
      <div v-if="currentAnnouncement" class="announcement-content">
        <div class="announcement-meta">
          <el-tag :type="getAnnouncementType(currentAnnouncement.level)" size="small">
            {{ getAnnouncementLevel(currentAnnouncement.level) }}
          </el-tag>
          <span class="announcement-date">
            {{ formatDate(currentAnnouncement.createdAt) }}
          </span>
        </div>
        
        <div class="announcement-body">
          <p v-html="currentAnnouncement.content"></p>
        </div>
        
        <div v-if="currentAnnouncement.actions" class="announcement-actions">
          <el-button
            v-for="action in currentAnnouncement.actions"
            :key="action.text"
            :type="action.type"
            @click="handleAnnouncementAction(action)"
          >
            {{ action.text }}
          </el-button>
        </div>
      </div>
      
      <template #footer>
        <div class="announcement-footer">
          <el-checkbox 
            v-model="dontShowAgain"
            v-if="currentAnnouncement?.allowDismiss"
          >
            不再显示此类通知
          </el-checkbox>
          <el-button @click="handleAnnouncementClose">知道了</el-button>
        </div>
      </template>
    </el-dialog>
    
    <!-- 浮动通知栏 -->
    <transition name="slide-down">
      <div v-if="showFloatingNotice" class="floating-notice">
        <div class="notice-content">
          <el-icon class="notice-icon" :color="floatingNotice.color">
            <component :is="floatingNotice.icon" />
          </el-icon>
          <span class="notice-text">{{ floatingNotice.text }}</span>
        </div>
        <el-button
          text
          @click="dismissFloatingNotice"
          class="notice-close"
        >
          <el-icon><Close /></el-icon>
        </el-button>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { ElNotification, ElMessage } from 'element-plus'
import {
  InfoFilled,
  WarningFilled,
  SuccessFilled,
  CircleCloseFilled,
  Close,
  Bell
} from '@element-plus/icons-vue'
import { HomepageService } from '@/api/homepage'

// 响应式数据
const activeNotifications = ref<any[]>([])
const showAnnouncementDialog = ref(false)
const currentAnnouncement = ref<any>(null)
const dontShowAgain = ref(false)
const showFloatingNotice = ref(false)
const floatingNotice = ref<any>({})

// 通知类型定义
interface SystemNotification {
  id: string
  title: string
  message: string
  type: 'success' | 'warning' | 'info' | 'error'
  duration: number
  showClose: boolean
  position: string
  createdAt: string
}

interface Announcement {
  id: string
  title: string
  content: string
  level: 'info' | 'warning' | 'urgent'
  createdAt: string
  allowDismiss: boolean
  actions?: Array<{
    text: string
    type: string
    action: string
  }>
}

// 检查系统通知
const checkSystemNotifications = async () => {
  try {
    // 检查系统状态
    const systemStatus = await HomepageService.getSystemStatus()
    
    // 根据系统状态生成通知
    generateStatusNotifications(systemStatus)
    
    // 检查是否有新的系统公告
    checkAnnouncements()
    
    // 检查功能更新通知
    checkFeatureUpdates()
    
  } catch (error) {
    console.error('检查系统通知失败:', error)
  }
}

// 根据系统状态生成通知
const generateStatusNotifications = (status: any) => {
  // AI服务状态通知
  if (status.ai_service === 'unavailable') {
    showNotification({
      id: 'ai-service-down',
      title: 'AI服务提醒',
      message: 'AI生成服务暂时不可用，我们正在紧急修复中',
      type: 'warning',
      duration: 0,
      showClose: true,
      position: 'top-right',
      createdAt: new Date().toISOString()
    })
  } else if (status.ai_service === 'limited') {
    showNotification({
      id: 'ai-service-limited',
      title: 'AI服务提醒',
      message: 'AI服务当前处于限制模式，响应可能较慢',
      type: 'info',
      duration: 5000,
      showClose: true,
      position: 'top-right',
      createdAt: new Date().toISOString()
    })
  }
  
  // 数据库连接状态
  if (status.database !== 'connected') {
    showNotification({
      id: 'database-error',
      title: '系统异常',
      message: '数据库连接异常，部分功能可能无法正常使用',
      type: 'error',
      duration: 0,
      showClose: true,
      position: 'top-right',
      createdAt: new Date().toISOString()
    })
  }
}

// 检查系统公告
const checkAnnouncements = () => {
  // 模拟系统公告数据
  const announcements: Announcement[] = [
    {
      id: 'welcome-new-user',
      title: '🎉 欢迎使用AI智能小说创作平台',
      content: `
        <p>感谢您选择我们的平台！这里有一些快速开始的提示：</p>
        <ul>
          <li>试试<strong>脑洞生成器</strong>，获取创作灵感</li>
          <li>浏览<strong>角色模板库</strong>，寻找完美角色</li>
          <li>查看<strong>创作指南</strong>，学习写作技巧</li>
        </ul>
        <p>如有任何问题，请随时联系客服！</p>
      `,
      level: 'info',
      createdAt: new Date().toISOString(),
      allowDismiss: true,
      actions: [
        { text: '开始体验', type: 'primary', action: 'start-tour' },
        { text: '查看指南', type: 'default', action: 'view-guide' }
      ]
    }
  ]
  
  // 检查用户是否是新用户
  const isNewUser = !localStorage.getItem('user_visited')
  const isLoggedIn = !!localStorage.getItem('access_token')
  
  if (isNewUser && !isLoggedIn) {
    // 显示欢迎公告
    showAnnouncement(announcements[0])
    localStorage.setItem('user_visited', 'true')
  }
}

// 检查功能更新通知
const checkFeatureUpdates = () => {
  const lastUpdateCheck = localStorage.getItem('last_update_check')
  const currentVersion = '1.0.0'
  
  if (!lastUpdateCheck) {
    // 首次访问，显示功能介绍
    displayFloatingNotice({
      text: '新功能上线：AI脑洞生成器现已支持更多创意模式！',
      icon: Bell,
      color: '#67c23a'
    })
    
    localStorage.setItem('last_update_check', currentVersion)
  }
}

// 显示通知
const showNotification = (notification: SystemNotification) => {
  // 检查是否已存在相同通知
  const exists = activeNotifications.value.some(n => n.id === notification.id)
  if (exists) return
  
  activeNotifications.value.push(notification)
  
  // 使用Element Plus的通知组件
  ElNotification({
    title: notification.title,
    message: notification.message,
    type: notification.type,
    duration: notification.duration,
    position: notification.position as any,
    showClose: notification.showClose,
    onClose: () => handleNotificationClose(notification.id)
  })
}

// 显示系统公告
const showAnnouncement = (announcement: Announcement) => {
  const dismissedAnnouncements = JSON.parse(
    localStorage.getItem('dismissed_announcements') || '[]'
  )
  
  if (dismissedAnnouncements.includes(announcement.id)) {
    return
  }
  
  currentAnnouncement.value = announcement
  showAnnouncementDialog.value = true
}

// 显示浮动通知
const displayFloatingNotice = (notice: any) => {
  floatingNotice.value = notice
  showFloatingNotice.value = true
  
  // 自动隐藏
  setTimeout(() => {
    showFloatingNotice.value = false
  }, 8000)
}

// 处理通知关闭
const handleNotificationClose = (notificationId: string) => {
  const index = activeNotifications.value.findIndex(n => n.id === notificationId)
  if (index > -1) {
    activeNotifications.value.splice(index, 1)
  }
}

// 处理公告关闭
const handleAnnouncementClose = () => {
  if (dontShowAgain.value && currentAnnouncement.value) {
    const dismissedAnnouncements = JSON.parse(
      localStorage.getItem('dismissed_announcements') || '[]'
    )
    dismissedAnnouncements.push(currentAnnouncement.value.id)
    localStorage.setItem('dismissed_announcements', JSON.stringify(dismissedAnnouncements))
  }
  
  showAnnouncementDialog.value = false
  currentAnnouncement.value = null
  dontShowAgain.value = false
}

// 处理公告操作
const handleAnnouncementAction = (action: any) => {
  switch (action.action) {
    case 'start-tour':
      // 开始产品导览
      ElMessage.success('产品导览功能即将推出')
      break
    case 'view-guide':
      // 查看使用指南
      window.open('/help/guide', '_blank')
      break
    default:
      console.log('未知操作:', action.action)
  }
  
  handleAnnouncementClose()
}

// 获取公告类型
const getAnnouncementType = (level: string) => {
  const typeMap = {
    'info': 'primary',
    'warning': 'warning',
    'urgent': 'danger'
  }
  return typeMap[level as keyof typeof typeMap] || 'primary'
}

// 获取公告级别文本
const getAnnouncementLevel = (level: string) => {
  const levelMap = {
    'info': '信息',
    'warning': '重要',
    'urgent': '紧急'
  }
  return levelMap[level as keyof typeof levelMap] || '信息'
}

// 格式化日期
const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 关闭浮动通知
const dismissFloatingNotice = () => {
  showFloatingNotice.value = false
}

// 定期检查通知
let notificationTimer: number

const startNotificationCheck = () => {
  // 立即检查一次
  checkSystemNotifications()
  
  // 每5分钟检查一次
  notificationTimer = window.setInterval(() => {
    checkSystemNotifications()
  }, 5 * 60 * 1000)
}

const stopNotificationCheck = () => {
  if (notificationTimer) {
    clearInterval(notificationTimer)
  }
}

// 生命周期
onMounted(() => {
  startNotificationCheck()
})

onUnmounted(() => {
  stopNotificationCheck()
})
</script>

<style scoped>
.system-notifications {
  /* 通知组件不需要占用空间 */
}

/* 公告对话框样式 */
.announcement-dialog :deep(.el-dialog__header) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px;
  margin: 0;
}

.announcement-dialog :deep(.el-dialog__title) {
  color: white;
  font-weight: 600;
}

.announcement-content {
  padding: 0;
}

.announcement-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e2e8f0;
}

.announcement-date {
  font-size: 12px;
  color: #a0aec0;
}

.announcement-body {
  margin-bottom: 20px;
  line-height: 1.6;
}

.announcement-body :deep(ul) {
  margin: 16px 0;
  padding-left: 20px;
}

.announcement-body :deep(li) {
  margin-bottom: 8px;
}

.announcement-body :deep(strong) {
  color: #667eea;
  font-weight: 600;
}

.announcement-actions {
  display: flex;
  gap: 12px;
  margin-top: 20px;
}

.announcement-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 浮动通知栏样式 */
.floating-notice {
  position: fixed;
  top: 80px;
  left: 50%;
  transform: translateX(-50%);
  background: white;
  border-radius: 12px;
  padding: 16px 20px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  border: 1px solid #e2e8f0;
  z-index: 2000;
  display: flex;
  align-items: center;
  gap: 12px;
  max-width: 600px;
  animation: slideDown 0.3s ease-out;
}

.notice-content {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.notice-icon {
  flex-shrink: 0;
}

.notice-text {
  font-size: 14px;
  color: #4a5568;
  line-height: 1.4;
}

.notice-close {
  color: #a0aec0;
  padding: 4px;
}

.notice-close:hover {
  color: #718096;
}

/* 动画效果 */
.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.3s ease;
}

.slide-down-enter-from {
  opacity: 0;
  transform: translateX(-50%) translateY(-20px);
}

.slide-down-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(-20px);
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateX(-50%) translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .floating-notice {
    left: 16px;
    right: 16px;
    transform: none;
    max-width: none;
  }
  
  .announcement-dialog :deep(.el-dialog) {
    width: 90% !important;
    margin: 5vh auto;
  }
  
  .announcement-footer {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .announcement-actions {
    flex-direction: column;
  }
}

/* 深色模式支持 */
@media (prefers-color-scheme: dark) {
  .floating-notice {
    background: #2d3748;
    border-color: #4a5568;
    color: #e2e8f0;
  }
  
  .notice-text {
    color: #e2e8f0;
  }
}
</style>