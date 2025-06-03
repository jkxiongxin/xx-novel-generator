<template>
  <div class="login-container">
    <!-- 页面头部 -->
    <div class="login-header">
      <router-link to="/" class="logo-link">
        <img src="@/assets/logo.svg" alt="AI Writer" class="logo" />
        <span class="app-name">AI Writer</span>
      </router-link>
      <p class="welcome-text">欢迎回来，开启你的AI创作之旅</p>
    </div>

    <!-- 登录表单 -->
    <div class="login-form-container">
      <el-card class="login-card" shadow="always">
        <template #header>
          <div class="form-header">
            <h2>用户登录</h2>
            <div class="tab-switch">
              <el-button 
                :type="loginMode === 'quick' ? 'primary' : 'default'"
                @click="loginMode = 'quick'"
                size="small"
              >
                快速登录
              </el-button>
              <el-button 
                :type="loginMode === 'extended' ? 'primary' : 'default'"
                @click="loginMode = 'extended'"
                size="small"
              >
                高级登录
              </el-button>
            </div>
          </div>
        </template>

        <!-- 快速登录表单 -->
        <el-form
          v-if="loginMode === 'quick'"
          ref="quickFormRef"
          :model="quickForm"
          :rules="quickRules"
          @submit.prevent="handleQuickLogin"
          label-width="0"
          size="large"
        >
          <el-form-item prop="email">
            <el-input
              v-model="quickForm.email"
              placeholder="邮箱地址"
              prefix-icon="User"
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
              class="login-button"
              block
            >
              {{ loading ? '登录中...' : '立即登录' }}
            </el-button>
          </el-form-item>
        </el-form>

        <!-- 扩展登录表单 -->
        <el-form
          v-else
          ref="extendedFormRef"
          :model="extendedForm"
          :rules="extendedRules"
          @submit.prevent="handleExtendedLogin"
          label-width="0"
          size="large"
        >
          <el-form-item prop="username">
            <el-input
              v-model="extendedForm.username"
              placeholder="用户名或邮箱"
              prefix-icon="User"
              clearable
            />
          </el-form-item>

          <el-form-item prop="password">
            <el-input
              v-model="extendedForm.password"
              type="password"
              placeholder="密码"
              prefix-icon="Lock"
              show-password
              clearable
            />
          </el-form-item>

          <el-form-item>
            <div class="form-options">
              <el-checkbox v-model="extendedForm.remember_me">
                记住我
              </el-checkbox>
              <router-link to="/auth/forgot-password" class="forgot-link">
                忘记密码？
              </router-link>
            </div>
          </el-form-item>

          <!-- 验证码（可选） -->
          <el-form-item v-if="showCaptcha" prop="captcha_token">
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

          <el-form-item>
            <el-button
              type="primary"
              native-type="submit"
              :loading="loading"
              class="login-button"
              block
            >
              {{ loading ? '登录中...' : '登录' }}
            </el-button>
          </el-form-item>
        </el-form>

        <!-- 第三方登录 -->
        <div class="third-party-login">
          <el-divider>
            <span class="divider-text">其他登录方式</span>
          </el-divider>
          
          <div class="oauth-buttons">
            <el-button
              class="oauth-button github"
              @click="handleGitHubLogin"
              :loading="githubLoading"
            >
              <svg class="oauth-icon" viewBox="0 0 24 24">
                <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
              </svg>
              GitHub
            </el-button>

            <el-button
              class="oauth-button google"
              @click="handleGoogleLogin"
              :loading="googleLoading"
            >
              <svg class="oauth-icon" viewBox="0 0 24 24">
                <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
                <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
                <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
              </svg>
              Google
            </el-button>
          </div>
        </div>

        <!-- 注册链接 -->
        <div class="register-link">
          <span>还没有账号？</span>
          <router-link to="/auth/register" class="link">立即注册</router-link>
        </div>
      </el-card>
    </div>

    <!-- 页面底部 -->
    <div class="login-footer">
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
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import AuthService, { 
  type UserLogin, 
  type LoginRequestExtended,
  type LoginResponseExtended 
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
const loginMode = ref<'quick' | 'extended'>('quick')
const showCaptcha = ref(false)
const captchaInput = ref('')
const captchaImageUrl = ref('/api/captcha/image?t=' + Date.now())

// 快速登录表单
const quickForm = reactive<UserLogin>({
  email: '',
  password: ''
})

// 扩展登录表单
const extendedForm = reactive<LoginRequestExtended>({
  username: '846762278@qq.com',
  password: '214wochusheng',
  remember_me: false,
  captcha_token: undefined
})

// 表单验证规则
const quickRules: FormRules = {
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ]
}

const extendedRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名或邮箱', trigger: 'blur' },
    { min: 3, message: '用户名长度不能少于3位', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ]
}

// 计算属性
const redirectPath = computed(() => {
  return (route.query.redirect as string) || '/'
})

// 方法
const handleQuickLogin = async () => {
  if (!quickFormRef.value) return
  
  try {
    await quickFormRef.value.validate()
    loading.value = true
    
    const response = await AuthService.login(quickForm)
    
    ElMessage.success('登录成功！')
    
    // 触发全局用户状态更新
    triggerUserStateUpdate()
    
    // 跳转到目标页面
    await router.push(redirectPath.value)
    
  } catch (error: any) {
    console.error('Login error:', error)
    
    if (error.response?.status === 401) {
      ElMessage.error('邮箱或密码错误')
    } else if (error.response?.status === 403) {
      ElMessage.error('账户已被禁用，请联系管理员')
    } else {
      ElMessage.error(error.response?.data?.detail || '登录失败，请重试')
    }
  } finally {
    loading.value = false
  }
}

const handleExtendedLogin = async () => {
  if (!extendedFormRef.value) return
  
  try {
    await extendedFormRef.value.validate()
    loading.value = true
    
    if (showCaptcha.value) {
      extendedForm.captcha_token = captchaInput.value
    }
    
    const response = await AuthService.loginExtended(extendedForm)
    
    ElMessage.success('登录成功！')
    
    // 触发全局用户状态更新
    triggerUserStateUpdate()
    
    // 检查邮箱验证状态
    if (!response.user.email_verified) {
      await ElMessageBox.confirm(
        '您的邮箱尚未验证，是否现在进行验证？验证后可以享受完整功能。',
        '邮箱验证提醒',
        {
          confirmButtonText: '发送验证邮件',
          cancelButtonText: '稍后验证',
          type: 'warning'
        }
      )
      
      try {
        await AuthService.resendVerification({ email: response.user.email })
        ElMessage.success('验证邮件已发送，请查收')
      } catch (error) {
        console.error('Resend verification error:', error)
      }
    }
    
    // 跳转到目标页面
    await router.push(redirectPath.value)
    
  } catch (error: any) {
    console.error('Extended login error:', error)
    
    if (error.response?.status === 401) {
      ElMessage.error('用户名或密码错误')
      // 连续失败可能需要验证码
      if (!showCaptcha.value) {
        showCaptcha.value = true
        refreshCaptcha()
      }
    } else if (error.response?.status === 403) {
      ElMessage.error('账户已被禁用，请联系管理员')
    } else {
      ElMessage.error(error.response?.data?.detail || '登录失败，请重试')
    }
  } finally {
    loading.value = false
  }
}

const handleGitHubLogin = () => {
  githubLoading.value = true
  try {
    AuthService.initiateGitHubLogin()
  } catch (error) {
    console.error('GitHub login error:', error)
    ElMessage.error('GitHub登录失败')
    githubLoading.value = false
  }
}

const handleGoogleLogin = async () => {
  googleLoading.value = true
  try {
    // TODO: 集成Google OAuth
    ElMessage.info('Google登录功能开发中...')
  } catch (error) {
    console.error('Google login error:', error)
    ElMessage.error('Google登录失败')
  } finally {
    googleLoading.value = false
  }
}

const refreshCaptcha = () => {
  captchaImageUrl.value = '/api/captcha/image?t=' + Date.now()
  captchaInput.value = ''
}

// 生命周期
onMounted(() => {
  // 如果已经登录，直接跳转
  if (AuthService.isAuthenticated() && AuthService.isTokenValid()) {
    router.push(redirectPath.value)
  }
  
  // 处理OAuth回调
  const code = route.query.code as string
  const state = route.query.state as string
  
  if (code && route.path.includes('/auth/callback/github')) {
    handleGitHubCallback(code, state)
  }
})

const handleGitHubCallback = async (code: string, state?: string) => {
  try {
    loading.value = true
    const response = await AuthService.handleGitHubCallback(code, state)
    
    ElMessage.success('GitHub登录成功！')
    
    // 触发全局用户状态更新
    triggerUserStateUpdate()
    
    await router.push(redirectPath.value)
    
  } catch (error: any) {
    console.error('GitHub callback error:', error)
    ElMessage.error('GitHub登录失败：' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

// 触发用户状态更新
const triggerUserStateUpdate = () => {
  // 触发storage change事件来通知其他组件
  window.dispatchEvent(new StorageEvent('storage', {
    key: 'access_token',
    newValue: localStorage.getItem('access_token'),
    oldValue: null
  }))
  
  // 如果全局刷新方法存在，也调用它
  if (typeof (window as any).refreshUserInfo === 'function') {
    (window as any).refreshUserInfo()
  }
}
</script>

<style scoped lang="scss">
.login-container {
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

.login-header {
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

.login-form-container {
  width: 100%;
  max-width: 480px;
  z-index: 1;
  
  .login-card {
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

.login-button {
  height: 48px;
  font-size: 16px;
  font-weight: 500;
  letter-spacing: 1px;
  border-radius: 8px;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  
  .forgot-link {
    color: #409eff;
    text-decoration: none;
    font-size: 14px;
    
    &:hover {
      text-decoration: underline;
    }
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

.third-party-login {
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

.register-link {
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

.login-footer {
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
  .login-container {
    padding: 12px;
  }
  
  .login-header {
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
  
  .login-card {
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
  .form-options {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
  
  .captcha-container {
    flex-direction: column;
    
    .captcha-image {
      width: 100%;
      height: 50px;
    }
  }
}
</style>