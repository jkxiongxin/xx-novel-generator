import { fileURLToPath, URL } from 'node:url'

import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  // 加载环境变量
  const env = loadEnv(mode, process.cwd(), '')
  
  return {
    plugins: [
      vue(),
      vueDevTools(),
    ],
    
    server: {
      port: parseInt(env.VITE_DEV_PORT) || 5173,
      host: true, // 允许外部访问
      
      // 代理配置
      proxy: {
        '/api': {
          target: env.VITE_PROXY_TARGET || 'http://localhost:8001',
          changeOrigin: true,
          secure: false,
          configure: (proxy, options) => {
            proxy.on('proxyReq', (proxyReq, req, res) => {
              if (env.VITE_DEBUG === 'true') {
                console.log(`[代理请求] ${req.method} ${req.url} -> ${options.target}${req.url}`)
              }
            })
            
            proxy.on('proxyRes', (proxyRes, req, res) => {
              if (env.VITE_DEBUG === 'true') {
                console.log(`[代理响应] ${proxyRes.statusCode} ${req.url}`)
              }
            })
            
            proxy.on('error', (err, req, res) => {
              console.error(`[代理错误] ${req.url}:`, err.message)
            })
          }
        }
      }
    },
    
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url))
      },
    },
    
    // 构建配置
    build: {
      sourcemap: mode === 'development',
      outDir: 'dist',
      rollupOptions: {
        output: {
          manualChunks: {
            'vendor': ['vue', 'vue-router', 'pinia'],
            'element-plus': ['element-plus'],
          }
        }
      }
    },
    
    // 预览服务器配置（用于预览构建后的应用）
    preview: {
      port: 4173,
      proxy: {
        '/api': {
          target: env.VITE_PROXY_TARGET || 'http://localhost:8001',
          changeOrigin: true,
          secure: false,
        }
      }
    }
  }
})
