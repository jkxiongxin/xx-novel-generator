<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <div id="app">
    <!-- 顶部导航栏 -->
    <el-header class="app-header">
      <div class="header-content">
        <div class="logo-area">
          <h1 class="app-title">📚 AI智能小说创作平台</h1>
        </div>
        
        <nav class="main-nav">
          <el-menu
            mode="horizontal"
            :default-active="$route.path"
            router
            class="nav-menu"
          >
            <el-menu-item index="/">
              <el-icon><House /></el-icon>
              <span>首页</span>
            </el-menu-item>
            <el-menu-item index="/brain-generator">
              <el-icon><MagicStick /></el-icon>
              <span>脑洞生成器</span>
            </el-menu-item>
            <el-menu-item index="/novel-create">
              <el-icon><EditPen /></el-icon>
              <span>小说创作</span>
            </el-menu-item>
            <el-menu-item index="/about">
              <el-icon><InfoFilled /></el-icon>
              <span>关于</span>
            </el-menu-item>
          </el-menu>
        </nav>
      </div>
    </el-header>

    <!-- 主内容区域 -->
    <el-main class="app-main">
      <RouterView />
    </el-main>

    <!-- 底部信息 -->
    <el-footer class="app-footer">
      <div class="footer-content">
        <p>&copy; 2025 AI智能小说创作平台. 让创意无限延伸</p>
      </div>
    </el-footer>
  </div>
</template>

<style>
/* 全局样式重置 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  height: 100%;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

#app {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

/* 顶部导航样式 */
.app-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  padding: 0;
  height: auto !important;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  height: 60px;
}

.logo-area {
  flex-shrink: 0;
}

.app-title {
  color: white;
  font-size: 1.5rem;
  font-weight: bold;
  margin: 0;
}

.main-nav {
  flex: 1;
  display: flex;
  justify-content: center;
}

.nav-menu {
  background: transparent !important;
  border: none !important;
}

.nav-menu .el-menu-item {
  color: rgba(255, 255, 255, 0.8) !important;
  border-bottom: 2px solid transparent !important;
  height: 60px;
  line-height: 60px;
}

.nav-menu .el-menu-item:hover {
  color: white !important;
  background: rgba(255, 255, 255, 0.1) !important;
}

.nav-menu .el-menu-item.is-active {
  color: white !important;
  border-bottom-color: white !important;
  background: rgba(255, 255, 255, 0.1) !important;
}

.nav-menu .el-menu-item i {
  margin-right: 8px;
}

/* 主内容区域 */
.app-main {
  flex: 1;
  padding: 0;
  overflow-y: auto;
  background: #f5f7fa;
}

/* 底部样式 */
.app-footer {
  background: #2c3e50;
  color: white;
  text-align: center;
  padding: 20px 0;
  height: auto !important;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
}

.footer-content p {
  margin: 0;
  font-size: 0.9rem;
  opacity: 0.8;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    height: auto;
    padding: 10px 20px;
  }
  
  .app-title {
    font-size: 1.2rem;
    margin-bottom: 10px;
  }
  
  .main-nav {
    width: 100%;
  }
  
  .nav-menu .el-menu-item {
    height: 50px;
    line-height: 50px;
    font-size: 0.9rem;
  }
}

/* Element Plus 组件样式调整 */
.el-menu--horizontal > .el-menu-item {
  border-bottom: 2px solid transparent;
}

.el-menu--horizontal > .el-menu-item.is-active {
  border-bottom-color: white;
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>
