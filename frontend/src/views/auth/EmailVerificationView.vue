<template>
  <div class="email-verification-container">
    <!-- 页面头部 -->
    <div class="email-verification-header">
      <router-link to="/" class="logo-link">
        <img src="@/assets/logo.svg" alt="AI Writer" class="logo" />
        <span class="app-name">AI Writer</span>
      </router-link>
      <p class="welcome-text">邮箱验证</p>
    </div>

    <!-- 验证状态卡片 -->
    <div class="email-verification-form-container">
      <!-- 验证中状态 -->
      <el-card v-if="verificationStatus === 'loading'" class="verification-card" shadow="always">
        <div class="verification-content">
          <el-icon class="loading-icon" size="48">
            <Loading />
          </el-icon>
          <h3>正在验证您的邮箱...</h3>
          <p>请稍候，我们正在处理您的验证请求</p>
        </div>
      </el-card>

      <!-- 验证成功状态 -->
      <el-card v-else-if="verificationStatus === 'success'" class="verification-card success" shadow="always">
        <div class="verification-content">
          <el-icon class="success-icon" size="60">
            <CircleCheck />
          </el-icon>
          <h3>邮箱验证成功！</h3>
          <p>恭喜您，邮箱验证已完成</p>
          <p class="tips">现在您可以享受 AI Writer 的完整功能了</p>
          
          <div class="user-info" v-if="verifiedUser">
            <el-divider />
            <div class="user-details">
              <p><strong>用户名：</strong>{{ verifiedUser.username }}</p>
              <p><strong>邮箱：</strong>{{ verifiedUser.email }}</p>
              <p><strong>注册时间：</strong>{{ formatDate(verifiedUser.created_at) }}</p>
            </div>
          </div>
          
          <div class="success-actions">
            <el-button type="primary" size="large" @click="goToHome">
              开始创作
            </el-button>
            <el-button size="large" @click="goToLogin" v-if="!isAutoLoggedIn">
              前往登录
            </el-button>
          </div>
        </div>
      </el-card>

      <!-- 验证失败状态 -->
      <el-card v-else-if="verificationStatus === 'error'" class="verification-card error" shadow="always">
        <div class="verification-content">
          <el-icon class="error-icon" size="60">
            <CircleClose />
          </el-icon>
          <h3>验证失败</h3>
          <p>{{ errorMessage }}</p>
          
          <div class="error-actions">
            <el-button type="primary" @click="resendVerification" :loading="resendLoading">
              重新发送验证邮件
            </el-button>
            <el-button @click="goToLogin">
              返回登录
            </el-button>
          </div>
          
          <div class="help-info">
            <el-divider />
            <p><strong>可能的原因：</strong></p>
            <ul>
              <li>验证链接已过期（通常24小时内有效）</li>
              <li>验证链接已被使用</li>
              <li>链接格式不正确</li>
            </ul>
            <p class="contact">
              如果问题持续存在，请
              <router-link to="/help" class="help-link">联系客服</router-link>
            </p>
          </div>
        </div>
      </el-card>

      <!-- 需要邮箱地址的重发表单 -->
      <el-card v-if="showResendForm" class="resend-card" shadow="always">
        <template #header>
          <h3>重新发送验证邮件</h3>
        </template>
        
        <el-form
          ref="resendFormRef"
          :model="resendForm"
          :rules="resendRules"
          @submit.prevent="handleResendSubmit"
          label-width="0"
          size="large"
        >
          <el-form-item prop="email">
            <el-input
              v-model="resendForm.email"
              placeholder="请输入您的邮箱地址"
              prefix-icon="Message"
              clearable
              :disabled="resendLoading"
            />
          </el-form-item>

          <el-form-item>
            <el-button
              type="primary"
              native-type="submit"
              :loading="resendLoading"
              block
            >
              {{ resendLoading ? '发送中...' : '发送验证邮件' }}
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>

    <!-- 页面底部 -->
    <div class="email-verification-footer">
      <div class="footer-links">
        <router-link to="/about">关于我们</router-link>
        <router-link to="/privacy">隐私政策</router-link>
        <router-link to="/terms">用户协议</router-link>
        <router-link to="/help">帮助中心</router-link>
      </div>
      <p class="copyright">© 2025 AI Writer. All rights reserved.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { Loading, CircleCheck, CircleClose } from '@element-plus/icons-vue'
import AuthService, { 
  type VerifyEmailRequest, 
  type ResendVerificationRequest,
  type UserInfo 
} from '@/api/auth'

// 路由
const router = useRouter()
const route = useRoute()

// 表单引用
const resendFormRef = ref<FormInstance>()

// 状态管理
const verificationStatus = ref<'loading' | 'success' | 'error'>('loading')
const resendLoading = ref(false)
const showResendForm = ref(false)
const isAutoLoggedIn = ref(false)
const errorMessage = ref('')
const verifiedUser = ref<UserInfo | null>(null)

// 重发表单数据
const resendForm = reactive<ResendVerificationRequest>({
  email: ''
})

// 表单验证规则
const resendRules: FormRules = {
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' }
  ]
}

// 方法
const verifyEmail = async (token: string) => {
  try {
    verificationStatus.value = 'loading'
    
    const response = await AuthService.verifyEmail({ token })
    
    if (response.success) {
      verificationStatus.value = 'success'
      verifiedUser.value = response.user || null
      
      // 如果返回了访问token，说明已自动登录
      if (response.access_token) {
        isAutoLoggedIn.value = true
        ElMessage.success('邮箱验证成功，已自动登录！')
      } else {
        ElMessage.success('邮箱验证成功！')
      }
    } else {
      verificationStatus.value = 'error'
      errorMessage.value = response.message
    }
    
  } catch (error: any) {
    console.error('Email verification error:', error)
    verificationStatus.value = 'error'
    
    if (error.response?.status === 400) {
      errorMessage.value = '验证链接已过期或无效'
    } else if (error.response?.status === 409) {
      errorMessage.value = '该邮箱已经验证过了'
    } else {
      errorMessage.value = error.response?.data?.detail || '验证失败，请重试'
    }
  }
}

const resendVerification = () => {
  showResendForm.value = true
}

const handleResendSubmit = async () => {
  if (!resendFormRef.value) return
  
  try {
    await resendFormRef.value.validate()
    resendLoading.value = true
    
    const response = await AuthService.resendVerification(resendForm)
    
    if (response.success) {
      ElMessage.success('验证邮件已重新发送，请查收')
      showResendForm.value = false
    } else {
      ElMessage.error(response.message || '发送失败，请重试')
    }
    
  } catch (error: any) {
    console.error('Resend verification error:', error)
    
    if (error.response?.status === 429) {
      ElMessage.error('发送频率过高，请稍后再试')
    } else {
      ElMessage.error('发送失败，请重试')
    }
  } finally {
    resendLoading.value = false
  }
}

const goToHome = () => {
  router.push('/')
}

const goToLogin = () => {
  router.push('/auth/login')
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleString('zh-CN')
}

// 生命周期
onMounted(() => {
  // 获取验证token
  const token = route.query.token as string
  if (!token) {
    verificationStatus.value = 'error'
    errorMessage.value = '验证链接无效，缺少验证token'
    return
  }
  
  // 开始验证
  verifyEmail(token)
})
</script>

<style scoped lang="scss">
.email-verification-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  position: relative;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    /* background: url('@/assets/bg-pattern.svg') repeat; */
    opacity: 0.1;
    z-index: 0;
  }
}

.email-verification-header {
  text-align: center;
  margin-bottom: 40px;
  z-index: 1;
  
  .logo-link {
    display: inline-flex;
    align-items: center;
    gap: 12px;
    text-decoration: none;
    color: white;
    margin-bottom: 16px;
    
    .logo {
      width: 48px;
      height: 48px;
    }
    
    .app-name {
      font-size: 32px;
      font-weight: bold;
      letter-spacing: 1px;
    }
  }
  
  .welcome-text {
    color: rgba(255, 255, 255, 0.9);
    font-size: 18px;
    margin: 0;
  }
}

.email-verification-form-container {
  width: 100%;
  max-width: 520px;
  z-index: 1;
  
  .verification-card, .resend-card {
    border-radius: 16px;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
    overflow: hidden;
    margin-bottom: 20px;
    
    &.success {
      border-left: 4px solid #67c23a;
    }
    
    &.error {
      border-left: 4px solid #f56c6c;
    }
    
    :deep(.el-card__header) {
      background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
      padding: 24px 32px;
      border-bottom: none;
      
      h3 {
        margin: 0;
        color: #2c3e50;
        font-weight: 600;
      }
    }
    
    :deep(.el-card__body) {
      padding: 32px;
    }
  }
}

.verification-content {
  text-align: center;
  
  .loading-icon {
    color: #409eff;
    margin-bottom: 16px;
    animation: rotate 1s linear infinite;
  }
  
  .success-icon {
    color: #67c23a;
    margin-bottom: 16px;
  }
  
  .error-icon {
    color: #f56c6c;
    margin-bottom: 16px;
  }
  
  h3 {
    margin: 0 0 16px 0;
    color: #2c3e50;
    font-weight: 600;
  }
  
  p {
    margin: 0 0 12px 0;
    color: #606266;
    line-height: 1.6;
    
    &.tips {
      font-size: 14px;
      color: #909399;
    }
  }
  
  .user-info {
    margin: 24px 0;
    
    .user-details {
      text-align: left;
      background: #f8f9fa;
      padding: 16px;
      border-radius: 8px;
      
      p {
        margin: 8px 0;
        font-size: 14px;
        
        strong {
          color: #2c3e50;
        }
      }
    }
  }
  
  .success-actions, .error-actions {
    margin: 24px 0;
    display: flex;
    gap: 12px;
    justify-content: center;
    flex-wrap: wrap;
  }
  
  .help-info {
    margin-top: 32px;
    text-align: left;
    
    p {
      margin: 8px 0;
      
      &:first-child {
        font-weight: 500;
        color: #2c3e50;
      }
      
      &.contact {
        margin-top: 12px;
        text-align: center;
      }
    }
    
    ul {
      margin: 8px 0;
      padding-left: 20px;
      
      li {
        margin: 4px 0;
        color: #606266;
        font-size: 14px;
        line-height: 1.5;
      }
    }
    
    .help-link {
      color: #409eff;
      text-decoration: none;
      
      &:hover {
        text-decoration: underline;
      }
    }
  }
}

.email-verification-footer {
  margin-top: auto;
  padding-top: 40px;
  text-align: center;
  color: rgba(255, 255, 255, 0.8);
  z-index: 1;
  
  .footer-links {
    display: flex;
    gap: 24px;
    justify-content: center;
    margin-bottom: 16px;
    
    a {
      color: rgba(255, 255, 255, 0.8);
      text-decoration: none;
      font-size: 14px;
      
      &:hover {
        color: white;
        text-decoration: underline;
      }
    }
  }
  
  .copyright {
    font-size: 12px;
    margin: 0;
    opacity: 0.7;
  }
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

// 响应式设计
@media (max-width: 768px) {
  .email-verification-container {
    padding: 12px;
  }
  
  .email-verification-header {
    margin-bottom: 24px;
    
    .logo-link {
      .logo {
        width: 40px;
        height: 40px;
      }
      
      .app-name {
        font-size: 24px;
      }
    }
    
    .welcome-text {
      font-size: 16px;
    }
  }
  
  .verification-card, .resend-card {
    :deep(.el-card__body) {
      padding: 24px 20px;
    }
  }
  
  .success-actions, .error-actions {
    flex-direction: column;
    align-items: stretch;
  }
  
  .footer-links {
    flex-wrap: wrap;
    gap: 16px;
  }
}
</style>