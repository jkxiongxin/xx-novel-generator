<template>
  <div class="forgot-password-container">
    <!-- 页面头部 -->
    <div class="forgot-password-header">
      <router-link to="/" class="logo-link">
        <img src="@/assets/logo.svg" alt="AI Writer" class="logo" />
        <span class="app-name">AI Writer</span>
      </router-link>
      <p class="welcome-text">忘记密码？不用担心，我们来帮您找回</p>
    </div>

    <!-- 忘记密码表单 -->
    <div class="forgot-password-form-container">
      <el-card class="forgot-password-card" shadow="always">
        <template #header>
          <div class="form-header">
            <h2>找回密码</h2>
            <p class="description">输入您注册时使用的邮箱地址，我们将发送重置链接给您</p>
          </div>
        </template>

        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          @submit.prevent="handleSubmit"
          label-width="0"
          size="large"
        >
          <el-form-item prop="email">
            <el-input
              v-model="form.email"
              placeholder="请输入注册邮箱"
              prefix-icon="Message"
              clearable
              :disabled="loading"
            />
          </el-form-item>

          <el-form-item>
            <el-button
              type="primary"
              native-type="submit"
              :loading="loading"
              class="submit-button"
              block
            >
              {{ loading ? '发送中...' : '发送重置邮件' }}
            </el-button>
          </el-form-item>
        </el-form>

        <!-- 返回登录 -->
        <div class="back-to-login">
          <router-link to="/auth/login" class="link">
            <el-icon><ArrowLeft /></el-icon>
            返回登录
          </router-link>
        </div>
      </el-card>

      <!-- 成功提示卡片 -->
      <el-card v-if="showSuccess" class="success-card" shadow="always">
        <div class="success-content">
          <el-icon class="success-icon" size="48">
            <CircleCheck />
          </el-icon>
          <h3>邮件已发送</h3>
          <p>我们已向 <strong>{{ form.email }}</strong> 发送了密码重置邮件</p>
          <p class="tips">请查收您的邮箱，点击邮件中的重置链接来设置新密码</p>
          
          <div class="success-actions">
            <el-button 
              type="primary" 
              @click="resendEmail"
              :loading="resendLoading"
              :disabled="resendCountdown > 0"
            >
              {{ resendCountdown > 0 ? `${resendCountdown}秒后可重发` : '重新发送' }}
            </el-button>
            <el-button @click="goToLogin">前往登录</el-button>
          </div>
          
          <div class="help-info">
            <p><strong>没有收到邮件？</strong></p>
            <ul>
              <li>请检查您的垃圾邮件箱</li>
              <li>确认邮箱地址是否正确</li>
              <li>邮件可能需要几分钟才能送达</li>
            </ul>
            <p class="contact">
              如果仍有问题，请
              <router-link to="/help" class="help-link">联系客服</router-link>
            </p>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 页面底部 -->
    <div class="forgot-password-footer">
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
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { ArrowLeft, CircleCheck } from '@element-plus/icons-vue'
import AuthService, { type ForgotPasswordRequest } from '@/api/auth'

// 路由
const router = useRouter()

// 表单引用
const formRef = ref<FormInstance>()

// 状态管理
const loading = ref(false)
const resendLoading = ref(false)
const showSuccess = ref(false)
const resendCountdown = ref(0)

// 表单数据
const form = reactive<ForgotPasswordRequest>({
  email: ''
})

// 表单验证规则
const rules: FormRules = {
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' }
  ]
}

// 倒计时定时器
let countdownTimer: number | null = null

// 方法
const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    loading.value = true
    
    const response = await AuthService.forgotPassword(form)
    
    // 由于响应拦截器已经处理了success判断，这里直接处理成功情况
    showSuccess.value = true
    ElMessage.success('密码重置邮件已发送')
    startResendCountdown()
    
  } catch (error: any) {
    console.error('Forgot password error:', error)
    
    if (error.response?.status === 404) {
      ElMessage.error('该邮箱未注册')
    } else if (error.response?.status === 429) {
      ElMessage.error('发送频率过高，请稍后再试')
      startResendCountdown(60) // 1分钟冷却
    } else {
      ElMessage.error(error.response?.data?.detail || '发送失败，请重试')
    }
  } finally {
    loading.value = false
  }
}

const resendEmail = async () => {
  if (resendCountdown.value > 0) return
  
  try {
    resendLoading.value = true
    
    const response = await AuthService.forgotPassword(form)
    
    // 由于响应拦截器已经处理了success判断，这里直接处理成功情况
    ElMessage.success('邮件已重新发送')
    startResendCountdown()
    
  } catch (error: any) {
    console.error('Resend email error:', error)
    ElMessage.error('发送失败，请稍后重试')
  } finally {
    resendLoading.value = false
  }
}

const startResendCountdown = (seconds: number = 60) => {
  resendCountdown.value = seconds
  
  countdownTimer = setInterval(() => {
    resendCountdown.value--
    if (resendCountdown.value <= 0) {
      clearInterval(countdownTimer!)
      countdownTimer = null
    }
  }, 1000)
}

const goToLogin = () => {
  router.push('/auth/login')
}

// 生命周期
onMounted(() => {
  // 如果已经登录，直接跳转到首页
  if (AuthService.isAuthenticated() && AuthService.isTokenValid()) {
    router.push('/')
  }
})

onUnmounted(() => {
  if (countdownTimer) {
    clearInterval(countdownTimer)
  }
})
</script>

<style scoped lang="scss">
.forgot-password-container {
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

.forgot-password-header {
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

.forgot-password-form-container {
  width: 100%;
  max-width: 480px;
  z-index: 1;
  
  .forgot-password-card, .success-card {
    border-radius: 16px;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
    overflow: hidden;
    margin-bottom: 20px;
    
    :deep(.el-card__header) {
      background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
      padding: 24px 32px;
      border-bottom: none;
    }
    
    :deep(.el-card__body) {
      padding: 32px;
    }
  }
}

.form-header {
  text-align: center;
  
  h2 {
    margin: 0 0 12px 0;
    color: #2c3e50;
    font-weight: 600;
  }
  
  .description {
    margin: 0;
    color: #606266;
    font-size: 14px;
    line-height: 1.5;
  }
}

.submit-button {
  height: 48px;
  font-size: 16px;
  font-weight: 500;
  letter-spacing: 1px;
  border-radius: 8px;
}

.back-to-login {
  text-align: center;
  margin-top: 24px;
  
  .link {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    color: #409eff;
    text-decoration: none;
    font-size: 14px;
    
    &:hover {
      text-decoration: underline;
    }
  }
}

.success-content {
  text-align: center;
  
  .success-icon {
    color: #67c23a;
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
  
  .success-actions {
    margin: 24px 0;
    display: flex;
    gap: 12px;
    justify-content: center;
    flex-wrap: wrap;
  }
  
  .help-info {
    margin-top: 32px;
    padding: 20px;
    background: #f8f9fa;
    border-radius: 8px;
    text-align: left;
    
    p {
      margin: 0 0 8px 0;
      
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
      margin: 8px 0 0 0;
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

.forgot-password-footer {
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

// 响应式设计
@media (max-width: 768px) {
  .forgot-password-container {
    padding: 12px;
  }
  
  .forgot-password-header {
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
  
  .forgot-password-card, .success-card {
    :deep(.el-card__body) {
      padding: 24px 20px;
    }
  }
  
  .success-actions {
    flex-direction: column;
    align-items: stretch;
  }
  
  .footer-links {
    flex-wrap: wrap;
    gap: 16px;
  }
}
</style>