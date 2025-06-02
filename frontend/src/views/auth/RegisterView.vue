<template>
  <div class="register-container">
    <!-- 页面头部 -->
    <div class="register-header">
      <router-link to="/" class="logo-link">
        <img src="@/assets/logo.svg" alt="AI Writer" class="logo" />
        <span class="app-name">AI Writer</span>
      </router-link>
      <p class="welcome-text">加入AI Writer，开启智能创作新时代</p>
    </div>

    <!-- 注册表单 -->
    <div class="register-form-container">
      <el-card class="register-card" shadow="always">
        <template #header>
          <div class="form-header">
            <h2>用户注册</h2>
            <div class="tab-switch">
              <el-button 
                :type="registerMode === 'quick' ? 'primary' : 'default'"
                @click="registerMode = 'quick'"
                size="small"
              >
                快速注册
              </el-button>
              <el-button 
                :type="registerMode === 'extended' ? 'primary' : 'default'"
                @click="registerMode = 'extended'"
                size="small"
              >
                完整注册
              </el-button>
            </div>
          </div>
        </template>

        <!-- 快速注册表单 -->
        <el-form
          v-if="registerMode === 'quick'"
          ref="quickFormRef"
          :model="quickForm"
          :rules="quickRules"
          @submit.prevent="handleQuickRegister"
          label-width="0"
          size="large"
        >
          <el-form-item prop="username">
            <el-input
              v-model="quickForm.username"
              placeholder="用户名"
              prefix-icon="User"
              clearable
            />
          </el-form-item>

          <el-form-item prop="email">
            <el-input
              v-model="quickForm.email"
              placeholder="邮箱地址"
              prefix-icon="Message"
              clearable
            />
          </el-form-item>

          <el-form-item prop="password">
            <el-input
              v-model="quickForm.password"
              type="password"
              placeholder="密码"
              prefix-icon="Lock"
              show-password
              clearable
            />
          </el-form-item>

          <el-form-item>
            <el-button
              type="primary"
              native-type="submit"
              :loading="loading"
              class="register-button"
              block
            >
              {{ loading ? '注册中...' : '立即注册' }}
            </el-button>
          </el-form-item>
        </el-form>

        <!-- 完整注册表单 -->
        <el-form
          v-else
          ref="extendedFormRef"
          :model="extendedForm"
          :rules="extendedRules"
          @submit.prevent="handleExtendedRegister"
          label-width="0"
          size="large"
        >
          <el-form-item prop="username">
            <el-input
              v-model="extendedForm.username"
              placeholder="用户名（3-20位字符）"
              prefix-icon="User"
              clearable
            >
              <template #suffix>
                <el-icon v-if="usernameCheckStatus === 'success'" class="check-icon success">
                  <Check />
                </el-icon>
                <el-icon v-else-if="usernameCheckStatus === 'error'" class="check-icon error">
                  <Close />
                </el-icon>
                <el-icon v-else-if="usernameCheckStatus === 'loading'" class="check-icon loading">
                  <Loading />
                </el-icon>
              </template>
            </el-input>
          </el-form-item>

          <el-form-item prop="email">
            <el-input
              v-model="extendedForm.email"
              placeholder="邮箱地址"
              prefix-icon="Message"
              clearable
            >
              <template #suffix>
                <el-icon v-if="emailCheckStatus === 'success'" class="check-icon success">
                  <Check />
                </el-icon>
                <el-icon v-else-if="emailCheckStatus === 'error'" class="check-icon error">
                  <Close />
                </el-icon>
                <el-icon v-else-if="emailCheckStatus === 'loading'" class="check-icon loading">
                  <Loading />
                </el-icon>
              </template>
            </el-input>
          </el-form-item>

          <el-form-item prop="password">
            <el-input
              v-model="extendedForm.password"
              type="password"
              placeholder="密码（8位以上，包含字母和数字）"
              prefix-icon="Lock"
              show-password
              clearable
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
              v-model="extendedForm.confirm_password"
              type="password"
              placeholder="确认密码"
              prefix-icon="Lock"
              show-password
              clearable
            />
          </el-form-item>

          <el-form-item prop="invite_code" v-if="showInviteCode">
            <el-input
              v-model="extendedForm.invite_code"
              placeholder="邀请码（可选）"
              prefix-icon="Gift"
              clearable
            />
          </el-form-item>

          <!-- 验证码 -->
          <el-form-item prop="captcha_token">
            <div class="captcha-container">
              <el-input
                v-model="captchaInput"
                placeholder="验证码"
                prefix-icon="Shield"
                clearable
              />
              <div class="captcha-image" @click="refreshCaptcha">
                <img :src="captchaImageUrl" alt="验证码" />
                <span class="refresh-hint">点击刷新</span>
              </div>
            </div>
          </el-form-item>

          <el-form-item prop="agree_terms">
            <el-checkbox v-model="extendedForm.agree_terms" size="large">
              我已阅读并同意
              <router-link to="/terms" class="terms-link" target="_blank">《用户协议》</router-link>
              和
              <router-link to="/privacy" class="terms-link" target="_blank">《隐私政策》</router-link>
            </el-checkbox>
          </el-form-item>

          <el-form-item>
            <el-button
              type="primary"
              native-type="submit"
              :loading="loading"
              class="register-button"
              block
            >
              {{ loading ? '注册中...' : '创建账户' }}
            </el-button>
          </el-form-item>
        </el-form>

        <!-- 第三方注册 -->
        <div class="third-party-register">
          <el-divider>
            <span class="divider-text">其他注册方式</span>
          </el-divider>
          
          <div class="oauth-buttons">
            <el-button
              class="oauth-button github"
              @click="handleGitHubRegister"
              :loading="githubLoading"
            >
              <svg class="oauth-icon" viewBox="0 0 24 24">
                <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
              </svg>
              GitHub 注册
            </el-button>

            <el-button
              class="oauth-button google"
              @click="handleGoogleRegister"
              :loading="googleLoading"
            >
              <svg class="oauth-icon" viewBox="0 0 24 24">
                <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
                <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
                <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
              </svg>
              Google 注册
            </el-button>
          </div>
        </div>

        <!-- 登录链接 -->
        <div class="login-link">
          <span>已有账号？</span>
          <router-link to="/auth/login" class="link">立即登录</router-link>
        </div>
      </el-card>
    </div>

    <!-- 页面底部 -->
    <div class="register-footer">
      <div class="footer-links">
        <router-link to="/about">关于我们</router-link>
        <router-link to="/privacy">隐私政策</router-link>
        <router-link to="/terms">用户协议</router-link>
        <router-link to="/help">帮助中心</router-link>
      </div>
      <p class="copyright">© 2025 AI Writer. All rights reserved.</p>
    </div>

    <!-- 注册成功对话框 -->
    <el-dialog
      v-model="showSuccessDialog"
      title="注册成功"
      width="500px"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      :show-close="false"
    >
      <div class="success-content">
        <el-icon class="success-icon" size="60">
          <CircleCheck />
        </el-icon>
        <h3>欢迎加入 AI Writer！</h3>
        <p v-if="registerResult">{{ registerResult.message }}</p>
        
        <div v-if="registerResult?.verification_sent" class="verification-info">
          <el-alert
            title="邮箱验证"
            type="warning"
            :closable="false"
            show-icon
          >
            <template #default>
              <p>我们已向您的邮箱发送了验证邮件，请查收并点击验证链接激活账户。</p>
              <div class="next-steps">
                <p><strong>接下来您需要：</strong></p>
                <ol>
                  <li v-for="step in registerResult.next_steps" :key="step">{{ step }}</li>
                </ol>
              </div>
            </template>
          </el-alert>
        </div>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="goToLogin">前往登录</el-button>
          <el-button 
            v-if="registerResult?.verification_sent" 
            type="primary" 
            @click="resendEmail"
            :loading="resendLoading"
          >
            重新发送验证邮件
          </el-button>
          <el-button v-else type="primary" @click="goToLogin">
            开始使用
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { Check, Close, Loading, CircleCheck } from '@element-plus/icons-vue'
import AuthService, { 
  type UserCreate, 
  type RegisterRequestExtended,
  type RegisterResponseExtended 
} from '@/api/auth'

// 路由
const router = useRouter()
const route = useRoute()

// 表单引用
const quickFormRef = ref<FormInstance>()
const extendedFormRef = ref<FormInstance>()

// 状态管理
const loading = ref(false)
const githubLoading = ref(false)
const googleLoading = ref(false)
const resendLoading = ref(false)
const registerMode = ref<'quick' | 'extended'>('quick')
const showInviteCode = ref(false)
const showSuccessDialog = ref(false)
const registerResult = ref<RegisterResponseExtended | null>(null)

// 实时验证状态
const usernameCheckStatus = ref<'success' | 'error' | 'loading' | null>(null)
const emailCheckStatus = ref<'success' | 'error' | 'loading' | null>(null)
const captchaInput = ref('')
const captchaImageUrl = ref('/api/captcha/image?t=' + Date.now())

// 快速注册表单
const quickForm = reactive<UserCreate>({
  username: '',
  email: '',
  password: '',
  full_name: ''
})

// 完整注册表单
const extendedForm = reactive<RegisterRequestExtended>({
  username: '',
  email: '',
  password: '',
  confirm_password: '',
  agree_terms: false,
  invite_code: '',
  captcha_token: undefined
})

// 密码强度计算
const passwordStrength = computed(() => {
  const password = extendedForm.password
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
const quickRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度为3-20位', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_-]+$/, message: '用户名只能包含字母、数字、下划线和短划线', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 8, message: '密码长度不能少于8位', trigger: 'blur' },
    { pattern: /(?=.*[a-zA-Z])(?=.*\d)/, message: '密码必须包含字母和数字', trigger: 'blur' }
  ]
}

const extendedRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度为3-20位', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_-]+$/, message: '用户名只能包含字母、数字、下划线和短划线', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 8, message: '密码长度不能少于8位', trigger: 'blur' },
    { pattern: /(?=.*[a-zA-Z])(?=.*\d)/, message: '密码必须包含字母和数字', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== extendedForm.password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  agree_terms: [
    {
      validator: (rule, value, callback) => {
        if (!value) {
          callback(new Error('请同意用户协议和隐私政策'))
        } else {
          callback()
        }
      },
      trigger: 'change'
    }
  ]
}

// 监听用户名变化进行实时验证
let usernameCheckTimeout: number | null = null
watch(
  () => extendedForm.username,
  async (newUsername) => {
    if (usernameCheckTimeout) {
      clearTimeout(usernameCheckTimeout)
    }
    
    if (!newUsername || newUsername.length < 3) {
      usernameCheckStatus.value = null
      return
    }
    
    usernameCheckStatus.value = 'loading'
    
    usernameCheckTimeout = setTimeout(async () => {
      try {
        // TODO: 实现用户名可用性检查API
        await new Promise(resolve => setTimeout(resolve, 500))
        usernameCheckStatus.value = 'success'
      } catch (error) {
        usernameCheckStatus.value = 'error'
      }
    }, 300)
  }
)

// 监听邮箱变化进行实时验证
let emailCheckTimeout: number | null = null
watch(
  () => extendedForm.email,
  async (newEmail) => {
    if (emailCheckTimeout) {
      clearTimeout(emailCheckTimeout)
    }
    
    if (!newEmail || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(newEmail)) {
      emailCheckStatus.value = null
      return
    }
    
    emailCheckStatus.value = 'loading'
    
    emailCheckTimeout = setTimeout(async () => {
      try {
        // TODO: 实现邮箱可用性检查API
        await new Promise(resolve => setTimeout(resolve, 500))
        emailCheckStatus.value = 'success'
      } catch (error) {
        emailCheckStatus.value = 'error'
      }
    }, 300)
  }
)

// 方法
const handleQuickRegister = async () => {
  if (!quickFormRef.value) return
  
  try {
    await quickFormRef.value.validate()
    loading.value = true
    
    const response = await AuthService.register(quickForm)
    
    ElMessage.success('注册成功！')
    
    // 跳转到登录页面
    await router.push('/auth/login')
    
  } catch (error: any) {
    console.error('Quick register error:', error)
    
    if (error.response?.status === 409) {
      const detail = error.response.data.detail
      if (detail.conflict_field === 'email') {
        ElMessage.error('邮箱已被注册')
      } else if (detail.conflict_field === 'username') {
        ElMessage.error('用户名已被使用')
      } else {
        ElMessage.error('注册失败，请检查输入信息')
      }
    } else {
      ElMessage.error(error.response?.data?.detail || '注册失败，请重试')
    }
  } finally {
    loading.value = false
  }
}

const handleExtendedRegister = async () => {
  if (!extendedFormRef.value) return
  
  try {
    await extendedFormRef.value.validate()
    loading.value = true
    
    extendedForm.captcha_token = captchaInput.value
    
    const response = await AuthService.registerExtended(extendedForm)
    
    registerResult.value = response
    showSuccessDialog.value = true
    
  } catch (error: any) {
    console.error('Extended register error:', error)
    
    if (error.response?.status === 409) {
      const detail = error.response.data.detail
      if (detail.conflict_field === 'email') {
        ElMessage.error('邮箱已被注册')
        emailCheckStatus.value = 'error'
      } else if (detail.conflict_field === 'username') {
        ElMessage.error('用户名已被使用')
        usernameCheckStatus.value = 'error'
      } else {
        ElMessage.error('注册失败，请检查输入信息')
      }
    } else {
      ElMessage.error(error.response?.data?.detail || '注册失败，请重试')
    }
    
    // 刷新验证码
    refreshCaptcha()
  } finally {
    loading.value = false
  }
}

const handleGitHubRegister = () => {
  githubLoading.value = true
  try {
    AuthService.initiateGitHubLogin()
  } catch (error) {
    console.error('GitHub register error:', error)
    ElMessage.error('GitHub注册失败')
    githubLoading.value = false
  }
}

const handleGoogleRegister = async () => {
  googleLoading.value = true
  try {
    // TODO: 集成Google OAuth
    ElMessage.info('Google注册功能开发中...')
  } catch (error) {
    console.error('Google register error:', error)
    ElMessage.error('Google注册失败')
  } finally {
    googleLoading.value = false
  }
}

const refreshCaptcha = () => {
  captchaImageUrl.value = '/api/captcha/image?t=' + Date.now()
  captchaInput.value = ''
}

const goToLogin = () => {
  showSuccessDialog.value = false
  router.push('/auth/login')
}

const resendEmail = async () => {
  if (!registerResult.value?.user.email) return
  
  try {
    resendLoading.value = true
    await AuthService.resendVerification({ email: registerResult.value.user.email })
    ElMessage.success('验证邮件已重新发送')
  } catch (error: any) {
    console.error('Resend email error:', error)
    ElMessage.error('发送失败，请稍后重试')
  } finally {
    resendLoading.value = false
  }
}

// 生命周期
onMounted(() => {
  // 如果已经登录，直接跳转到首页
  if (AuthService.isAuthenticated() && AuthService.isTokenValid()) {
    router.push('/')
  }
  
  // 检查是否有邀请码
  const inviteCode = route.query.invite as string
  if (inviteCode) {
    showInviteCode.value = true
    extendedForm.invite_code = inviteCode
    registerMode.value = 'extended'
  }
})
</script>

<style scoped lang="scss">
.register-container {
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

.register-header {
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

.register-form-container {
  width: 100%;
  max-width: 520px;
  z-index: 1;
  
  .register-card {
    border-radius: 16px;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
    overflow: hidden;
    
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
    margin: 0 0 20px 0;
    color: #2c3e50;
    font-weight: 600;
  }
  
  .tab-switch {
    display: flex;
    gap: 8px;
    justify-content: center;
  }
}

.register-button {
  height: 48px;
  font-size: 16px;
  font-weight: 500;
  letter-spacing: 1px;
  border-radius: 8px;
}

.check-icon {
  &.success {
    color: #67c23a;
  }
  
  &.error {
    color: #f56c6c;
  }
  
  &.loading {
    color: #409eff;
    animation: rotate 1s linear infinite;
  }
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
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

.captcha-container {
  display: flex;
  gap: 12px;
  align-items: stretch;
  
  .el-input {
    flex: 1;
  }
  
  .captcha-image {
    width: 120px;
    height: 40px;
    border: 1px solid #dcdfe6;
    border-radius: 4px;
    cursor: pointer;
    position: relative;
    overflow: hidden;
    
    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
    
    .refresh-hint {
      position: absolute;
      bottom: 0;
      left: 0;
      right: 0;
      background: rgba(0, 0, 0, 0.7);
      color: white;
      font-size: 10px;
      text-align: center;
      padding: 2px;
      transform: translateY(100%);
      transition: transform 0.3s;
    }
    
    &:hover .refresh-hint {
      transform: translateY(0);
    }
  }
}

.terms-link {
  color: #409eff;
  text-decoration: none;
  margin: 0 2px;
  
  &:hover {
    text-decoration: underline;
  }
}

.third-party-register {
  margin-top: 32px;
  
  .divider-text {
    color: #909399;
    font-size: 14px;
  }
  
  .oauth-buttons {
    display: flex;
    gap: 16px;
    margin-top: 20px;
    
    .oauth-button {
      flex: 1;
      height: 44px;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      border-radius: 8px;
      font-weight: 500;
      
      .oauth-icon {
        width: 20px;
        height: 20px;
      }
      
      &.github {
        background: #24292e;
        border-color: #24292e;
        color: white;
        
        &:hover {
          background: #1a1e22;
          border-color: #1a1e22;
        }
      }
      
      &.google {
        background: white;
        border-color: #dadce0;
        color: #3c4043;
        
        &:hover {
          background: #f8f9fa;
          border-color: #dadce0;
        }
      }
    }
  }
}

.login-link {
  text-align: center;
  margin-top: 24px;
  color: #606266;
  
  .link {
    color: #409eff;
    text-decoration: none;
    font-weight: 500;
    margin-left: 8px;
    
    &:hover {
      text-decoration: underline;
    }
  }
}

.register-footer {
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

.success-content {
  text-align: center;
  padding: 20px;
  
  .success-icon {
    color: #67c23a;
    margin-bottom: 16px;
  }
  
  h3 {
    margin: 0 0 16px 0;
    color: #2c3e50;
  }
  
  .verification-info {
    margin-top: 20px;
    text-align: left;
    
    .next-steps {
      margin-top: 12px;
      
      p {
        margin: 8px 0 4px 0;
        font-weight: 500;
      }
      
      ol {
        margin: 0;
        padding-left: 20px;
        
        li {
          margin: 4px 0;
          line-height: 1.5;
        }
      }
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  .register-container {
    padding: 12px;
  }
  
  .register-header {
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
  
  .register-card {
    :deep(.el-card__body) {
      padding: 24px 20px;
    }
  }
  
  .oauth-buttons {
    flex-direction: column;
  }
  
  .footer-links {
    flex-wrap: wrap;
    gap: 16px;
  }
}

@media (max-width: 480px) {
  .captcha-container {
    flex-direction: column;
    
    .captcha-image {
      width: 100%;
      height: 50px;
    }
  }
}
</style>