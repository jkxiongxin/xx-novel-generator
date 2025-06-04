<template>
  <div class="reset-password-container">
    <!-- 页面头部 -->
    <div class="reset-password-header">
      <router-link to="/" class="logo-link">
        <img src="@/assets/logo.svg" alt="AI Writer" class="logo" />
        <span class="app-name">AI Writer</span>
      </router-link>
      <p class="welcome-text">设置您的新密码</p>
    </div>

    <!-- 重置密码表单 -->
    <div class="reset-password-form-container">
      <el-card class="reset-password-card" shadow="always">
        <template #header>
          <div class="form-header">
            <h2>重置密码</h2>
            <p class="description">请输入您的新密码</p>
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
          <el-form-item prop="password">
            <el-input
              v-model="form.password"
              type="password"
              placeholder="新密码（8位以上，包含字母和数字）"
              prefix-icon="Lock"
              show-password
              clearable
              :disabled="loading"
            />
            <div class="password-strength">
              <div class="strength-bar">
                <div 
                  class="strength-fill" 
                  :class="passwordStrength.level"
                  :style="{ width: passwordStrength.percentage + '%' }"
                ></div>
              </div>
              <span class="strength-text">{{ passwordStrength.text }}</span>
            </div>
          </el-form-item>

          <el-form-item prop="confirm_password">
            <el-input
              v-model="form.confirm_password"
              type="password"
              placeholder="确认新密码"
              prefix-icon="Lock"
              show-password
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
              {{ loading ? '重置中...' : '重置密码' }}
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
          <h3>密码重置成功！</h3>
          <p>您的密码已成功重置</p>
          <p class="tips">现在您可以使用新密码登录账户了</p>
          
          <div class="success-actions">
            <el-button type="primary" @click="goToLogin">
              立即登录
            </el-button>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 页面底部 -->
    <div class="reset-password-footer">
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
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { ArrowLeft, CircleCheck } from '@element-plus/icons-vue'
import AuthService, { type ResetPasswordRequest } from '@/api/auth'

// 路由
const router = useRouter()
const route = useRoute()

// 表单引用
const formRef = ref<FormInstance>()

// 状态管理
const loading = ref(false)
const showSuccess = ref(false)

// 表单数据
const form = reactive<ResetPasswordRequest>({
  token: '',
  password: '',
  confirm_password: ''
})

// 密码强度计算
const passwordStrength = computed(() => {
  const password = form.password
  if (!password) {
    return { level: 'weak', percentage: 0, text: '请输入密码' }
  }
  
  let score = 0
  let checks = []
  
  // 长度检查
  if (password.length >= 8) {
    score += 25
    checks.push('长度充足')
  }
  
  // 包含数字
  if (/\d/.test(password)) {
    score += 25
    checks.push('包含数字')
  }
  
  // 包含字母
  if (/[a-zA-Z]/.test(password)) {
    score += 25
    checks.push('包含字母')
  }
  
  // 包含特殊字符
  if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
    score += 25
    checks.push('包含特殊字符')
  }
  
  if (score <= 25) {
    return { level: 'weak', percentage: score, text: '弱' }
  } else if (score <= 50) {
    return { level: 'medium', percentage: score, text: '中等' }
  } else if (score <= 75) {
    return { level: 'strong', percentage: score, text: '强' }
  } else {
    return { level: 'very-strong', percentage: score, text: '很强' }
  }
})

// 表单验证规则
const rules: FormRules = {
  password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 8, message: '密码长度不能少于8位', trigger: 'blur' },
    { pattern: /(?=.*[a-zA-Z])(?=.*\d)/, message: '密码必须包含字母和数字', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== form.password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

// 方法
const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    loading.value = true
    
    const response = await AuthService.resetPassword(form)
    
    // 由于响应拦截器已经处理了success判断，这里直接处理成功情况
    showSuccess.value = true
    ElMessage.success('密码重置成功！')
    
    // 如果支持自动登录，可以直接跳转
    if (response.auto_login) {
      setTimeout(() => {
        router.push('/')
      }, 2000)
    }
    
  } catch (error: any) {
    console.error('Reset password error:', error)
    
    if (error.response?.status === 400) {
      ElMessage.error('重置链接已过期或无效，请重新申请')
    } else if (error.response?.status === 422) {
      ElMessage.error('密码格式不正确')
    } else {
      ElMessage.error(error.response?.data?.detail || '密码重置失败，请重试')
    }
  } finally {
    loading.value = false
  }
}

const goToLogin = () => {
  router.push('/auth/login')
}

// 生命周期
onMounted(() => {
  // 获取重置token
  const token = route.query.token as string
  if (!token) {
    ElMessage.error('重置链接无效')
    router.push('/auth/forgot-password')
    return
  }
  
  form.token = token
  
  // 如果已经登录，直接跳转到首页
  if (AuthService.isAuthenticated() && AuthService.isTokenValid()) {
    router.push('/')
  }
})
</script>

<style scoped lang="scss">
.reset-password-container {
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

.reset-password-header {
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

.reset-password-form-container {
  width: 100%;
  max-width: 480px;
  z-index: 1;
  
  .reset-password-card, .success-card {
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

.password-strength {
  margin-top: 8px;
  
  .strength-bar {
    width: 100%;
    height: 4px;
    background: #f0f2f5;
    border-radius: 2px;
    overflow: hidden;
    margin-bottom: 4px;
    
    .strength-fill {
      height: 100%;
      transition: all 0.3s;
      
      &.weak {
        background: #f56c6c;
      }
      
      &.medium {
        background: #e6a23c;
      }
      
      &.strong {
        background: #409eff;
      }
      
      &.very-strong {
        background: #67c23a;
      }
    }
  }
  
  .strength-text {
    font-size: 12px;
    color: #909399;
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
}

.reset-password-footer {
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
  .reset-password-container {
    padding: 12px;
  }
  
  .reset-password-header {
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
  
  .reset-password-card, .success-card {
    :deep(.el-card__body) {
      padding: 24px 20px;
    }
  }
  
  .footer-links {
    flex-wrap: wrap;
    gap: 16px;
  }
}
</style>