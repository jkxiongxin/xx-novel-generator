import { ref, reactive, computed, onMounted, watch, nextTick } from 'vue'
import { ElMessage, ElMessageBox, ElNotification } from 'element-plus'
import { useRouter } from 'vue-router'
import { debounce } from 'lodash-es'
import {
  BrainStormService,
  type BrainStormRequest,
  type GeneratedIdea,
  type HistoryItem,
  type ElementCategory,
  type TopicSuggestion,
  type UserPreferences,
  type GenerationStatsResponse
} from '../api/generation'

// 类型定义
type IdeaType = 'plot' | 'character' | 'worldview' | 'mixed'

// 响应式断点检测
export const useResponsive = () => {
  const isMobile = ref(window.innerWidth < 768)
  const isTablet = ref(window.innerWidth >= 768 && window.innerWidth < 1024)
  const isDesktop = ref(window.innerWidth >= 1024)

  const updateBreakpoints = () => {
    const width = window.innerWidth
    isMobile.value = width < 768
    isTablet.value = width >= 768 && width < 1024
    isDesktop.value = width >= 1024
  }

  onMounted(() => {
    window.addEventListener('resize', updateBreakpoints)
  })

  return {
    isMobile,
    isTablet,
    isDesktop
  }
}

// 脑洞生成器组合式函数
export const useBrainGenerator = () => {
  const router = useRouter()
  const { isMobile } = useResponsive()

  // 表单数据
  const form = reactive<BrainStormRequest>({
    topic: '',
    creativity_level: 7,
    idea_count: 10,
    idea_type: ['mixed'] as IdeaType[],
    elements: [] as string[],
    style: '',
    user_input: '',
    language: 'zh-CN'
  })

  // 状态管理
  const isGenerating = ref(false)
  const progress = ref(0)
  const currentStep = ref('')
  const errorMessage = ref('')
  const showPreferencesDialog = ref(false)

  // 数据存储
  const generatedIdeas = ref<GeneratedIdea[]>([])
  const recentHistory = ref<HistoryItem[]>([])
  const elementCategories = ref<ElementCategory[]>([])
  const topicSuggestions = ref<TopicSuggestion[]>([])
  const stats = ref<GenerationStatsResponse | null>(null)
  const preferences = ref<UserPreferences>({
    default_creativity_level: 7,
    default_idea_count: 10,
    preferred_types: ['mixed'],
    favorite_elements: [],
    default_style: '',
    auto_save_history: true,
    updated_at: ''
  })

  // 复制状态管理
  const copiedStates = ref<boolean[]>([])

  // 计算属性
  const canGenerate = computed(() => {
    return form.topic.trim().length > 0 && !isGenerating.value
  })

  const creativityDescription = computed(() => {
    const level = form.creativity_level || 7
    if (level >= 9) return '极具创意 🚀'
    if (level >= 7) return '富有创意 🌟'
    if (level >= 5) return '中等创意 💡'
    if (level >= 3) return '比较保守 📝'
    return '非常保守 🏠'
  })

  const creativityMarks = computed(() => ({
    1: '保守',
    3: '稳重',
    5: '平衡',
    7: '创新',
    10: '极限'
  }))

  // 监听生成结果变化，初始化复制状态
  watch(generatedIdeas, (ideas) => {
    copiedStates.value = new Array(ideas.length).fill(false)
  })

  // 防抖的主题输入处理
  const debouncedTopicInput = debounce(async (query: string) => {
    if (query.length >= 2) {
      try {
        const response = await BrainStormService.getTopicSuggestions(query, 5)
        topicSuggestions.value = response.suggestions
      } catch (error) {
        console.warn('获取主题建议失败:', error)
      }
    } else {
      topicSuggestions.value = []
    }
  }, 300)

  // 事件处理函数
  const onTopicInput = (value: string) => {
    form.topic = value
    debouncedTopicInput(value)
  }

  const onCreativityChange = (value: number) => {
    form.creativity_level = value
  }

  const selectTopicSuggestion = (topic: string) => {
    form.topic = topic
    topicSuggestions.value = []
  }

  const toggleElement = (elementName: string) => {
    if (!form.elements) {
      form.elements = []
    }
    const index = form.elements.indexOf(elementName)
    if (index > -1) {
      form.elements.splice(index, 1)
    } else {
      form.elements.push(elementName)
    }
  }

  // 生成进度模拟
  const simulateProgress = () => {
    const steps = [
      '正在分析主题内容...',
      '构建创意生成框架...',
      '调用AI引擎生成创意...',
      '优化和筛选创意内容...',
      '完成创意生成处理...'
    ]

    let stepIndex = 0
    const progressInterval = setInterval(() => {
      if (stepIndex < steps.length && isGenerating.value) {
        currentStep.value = steps[stepIndex]
        progress.value = ((stepIndex + 1) / steps.length) * 100
        stepIndex++
      } else {
        clearInterval(progressInterval)
      }
    }, 800)

    return progressInterval
  }

  // 核心生成功能
  const generateIdeas = async () => {
    if (!canGenerate.value) {
      ElMessage.warning('请先输入主题关键词')
      return
    }

    try {
      isGenerating.value = true
      progress.value = 0
      currentStep.value = '开始生成创意...'
      errorMessage.value = ''

      // 启动进度模拟
      const progressInterval = simulateProgress()

      const response = await BrainStormService.generateBrainStorm(form)

      // 清除进度模拟
      clearInterval(progressInterval)

      // 由于响应拦截器已经处理了success判断，这里直接处理成功情况
      generatedIdeas.value = response.ideas
      
      // 保存到历史记录
      if (preferences.value.auto_save_history) {
        await loadRecentHistory()
      }

      progress.value = 100
      currentStep.value = '生成完成！'
      
      ElMessage.success(`成功生成 ${response.ideas.length} 个创意！`)
      
      // 滚动到结果区域
      nextTick(() => {
        const resultsArea = document.querySelector('.results-area')
        if (resultsArea) {
          resultsArea.scrollIntoView({ behavior: 'smooth' })
        }
      })
    } catch (error: any) {
      handleGenerationError(error)
    } finally {
      isGenerating.value = false
      setTimeout(() => {
        progress.value = 0
        currentStep.value = ''
      }, 2000)
    }
  }

  // 错误处理
  const handleGenerationError = (error: any) => {
    const { status, data } = error.response || {}
    
    switch (status) {
      case 400:
        errorMessage.value = '请求参数错误，请检查输入内容'
        ElMessage.error('请求参数错误')
        break
      case 401:
        errorMessage.value = '请先登录后再使用生成功能'
        ElMessage.error('需要登录')
        break
      case 429:
        errorMessage.value = '请求过于频繁，请稍后再试'
        ElMessage.warning('请求频率限制')
        break
      case 503:
        errorMessage.value = 'AI服务暂时不可用，请稍后重试'
        ElMessage.error('服务暂时不可用')
        break
      default:
        errorMessage.value = error.message || '生成失败，请稍后重试'
        ElMessage.error('生成失败')
    }
  }

  // 复制功能
  const copyIdea = async (content: string, index: number) => {
    try {
      await navigator.clipboard.writeText(content)
      copiedStates.value[index] = true
      
      ElMessage.success('创意已复制到剪贴板')
      
      // 2秒后重置状态
      setTimeout(() => {
        copiedStates.value[index] = false
      }, 2000)
    } catch (error) {
      // 降级处理
      fallbackCopyText(content)
      ElMessage.success('创意已复制')
    }
  }

  const copyAllIdeas = async () => {
    if (generatedIdeas.value.length === 0) {
      ElMessage.warning('没有可复制的创意')
      return
    }

    const formattedText = generatedIdeas.value
      .map((idea, index) => `${index + 1}. ${idea.content}`)
      .join('\n\n')

    try {
      await navigator.clipboard.writeText(formattedText)
      ElMessage.success(`已复制 ${generatedIdeas.value.length} 个创意`)
    } catch (error) {
      fallbackCopyText(formattedText)
    }
  }

  // 降级复制方法
  const fallbackCopyText = (text: string) => {
    const textArea = document.createElement('textarea')
    textArea.value = text
    textArea.style.position = 'fixed'
    textArea.style.opacity = '0'
    document.body.appendChild(textArea)
    textArea.select()
    document.execCommand('copy')
    document.body.removeChild(textArea)
  }

  // 导出功能
  const exportIdeas = (format: 'txt' | 'json' | 'csv') => {
    if (generatedIdeas.value.length === 0) {
      ElMessage.warning('没有可导出的创意')
      return
    }

    let content = ''
    let filename = ''
    let mimeType = ''

    const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-')

    switch (format) {
      case 'txt':
        content = formatAsText(generatedIdeas.value)
        filename = `脑洞创意_${timestamp}.txt`
        mimeType = 'text/plain'
        break
      case 'json':
        content = JSON.stringify({
          topic: form.topic,
          generated_at: new Date().toISOString(),
          ideas: generatedIdeas.value
        }, null, 2)
        filename = `脑洞创意_${timestamp}.json`
        mimeType = 'application/json'
        break
      case 'csv':
        content = formatAsCSV(generatedIdeas.value)
        filename = `脑洞创意_${timestamp}.csv`
        mimeType = 'text/csv'
        break
    }

    downloadFile(content, filename, mimeType)
    ElMessage.success('导出成功')
  }

  // 格式化函数
  const formatAsText = (ideas: GeneratedIdea[]) => {
    return ideas
      .map((idea, index) => 
        `${index + 1}. ${idea.content}\n   标签：${idea.tags.join(', ')}\n   创意指数：${idea.creativity_score}\n   实用指数：${idea.practical_score}\n`
      )
      .join('\n')
  }

  const formatAsCSV = (ideas: GeneratedIdea[]) => {
    const headers = ['序号', '内容', '类型', '标签', '创意指数', '实用指数', '总结']
    const rows = ideas.map((idea, index) => [
      index + 1,
      `"${idea.content.replace(/"/g, '""')}"`,
      idea.type,
      `"${idea.tags.join(', ')}"`,
      idea.creativity_score,
      idea.practical_score,
      `"${idea.summary.replace(/"/g, '""')}"`
    ])
    
    return [headers.join(','), ...rows.map(row => row.join(','))].join('\n')
  }

  const downloadFile = (content: string, filename: string, mimeType: string) => {
    const blob = new Blob([content], { type: mimeType })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    link.click()
    URL.revokeObjectURL(url)
  }

  // 重新生成
  const regenerateIdeas = async () => {
    if (generatedIdeas.value.length > 0) {
      const confirmed = await ElMessageBox.confirm(
        '重新生成将覆盖当前结果，是否继续？',
        '确认重新生成',
        {
          confirmButtonText: '重新生成',
          cancelButtonText: '取消',
          type: 'warning'
        }
      ).catch(() => false)

      if (!confirmed) return
    }

    await generateIdeas()
  }

  // 应用创意
  const applyIdea = async (idea: GeneratedIdea) => {
    try {
      const confirmed = await ElMessageBox.confirm(
        '是否将此创意应用到小说创建页面？',
        '应用创意',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'info'
        }
      )

      if (confirmed) {
        // 跳转到小说创建页面，传递创意数据
        router.push({
          path: '/novels/create',
          query: {
            idea: encodeURIComponent(idea.content),
            type: idea.type,
            tags: idea.tags.join(',')
          }
        })
      }
    } catch {
      // 用户取消
    }
  }

  // 历史记录管理
  const loadRecentHistory = async () => {
    try {
      const response = await BrainStormService.getHistory(10, 0)
      recentHistory.value = response.history
    } catch (error) {
      console.warn('加载历史记录失败:', error)
    }
  }

  const applyHistoryParams = (historyItem: HistoryItem) => {
    form.topic = historyItem.topic
    form.creativity_level = historyItem.parameters.creativity_level || 7
    form.idea_count = historyItem.parameters.idea_count || 10
    form.idea_type = (historyItem.parameters.idea_type as IdeaType[]) || ['mixed']
    form.elements = [...(historyItem.parameters.elements || [])]
    form.style = historyItem.parameters.style || ''
    form.user_input = historyItem.parameters.user_input || ''

    ElMessage.success('历史参数已应用')
  }

  const clearHistory = async () => {
    try {
      await ElMessageBox.confirm(
        '确定要清空所有历史记录吗？此操作不可恢复。',
        '清空历史记录',
        {
          confirmButtonText: '确定清空',
          cancelButtonText: '取消',
          type: 'warning'
        }
      )

      // 这里需要后端实现清空历史记录的接口
      recentHistory.value = []
      ElMessage.success('历史记录已清空')
    } catch {
      // 用户取消
    }
  }

  // 偏好设置
  const loadUserPreferences = async () => {
    try {
      const userPrefs = await BrainStormService.getUserPreferences()
      preferences.value = userPrefs
      
      // 应用用户偏好到表单
      form.creativity_level = userPrefs.default_creativity_level
      form.idea_count = userPrefs.default_idea_count
      form.idea_type = userPrefs.preferred_types as IdeaType[]
      form.style = userPrefs.default_style
    } catch (error) {
      console.warn('加载用户偏好失败:', error)
    }
  }

  const savePreferences = async () => {
    try {
      await BrainStormService.saveUserPreferences({
        default_creativity_level: preferences.value.default_creativity_level,
        default_idea_count: preferences.value.default_idea_count,
        preferred_types: preferences.value.preferred_types,
        favorite_elements: preferences.value.favorite_elements,
        default_style: preferences.value.default_style,
        auto_save_history: preferences.value.auto_save_history
      })

      showPreferencesDialog.value = false
      ElMessage.success('偏好设置已保存')
    } catch (error) {
      ElMessage.error('保存失败')
    }
  }

  // 加载要素建议
  const loadElementSuggestions = async () => {
    try {
      const response = await BrainStormService.getElementSuggestions()
      elementCategories.value = response.categories
    } catch (error) {
      console.warn('加载要素建议失败:', error)
    }
  }

  // 加载统计数据
  const loadStats = async () => {
    try {
      const statsData = await BrainStormService.getStats()
      stats.value = statsData
    } catch (error) {
      console.warn('加载统计数据失败:', error)
    }
  }

  // 时间格式化
  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    
    if (diff < 60000) return '刚刚'
    if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
    if (diff < 604800000) return `${Math.floor(diff / 86400000)}天前`
    
    return date.toLocaleDateString()
  }

  // 初始化
  const initialize = async () => {
    try {
      // 并行加载初始数据
      await Promise.all([
        loadUserPreferences(),
        loadElementSuggestions(),
        loadRecentHistory(),
        loadStats()
      ])
    } catch (error) {
      console.warn('初始化失败:', error)
    }
  }

  // 组件挂载时初始化
  onMounted(() => {
    initialize()
  })

  return {
    // 响应式数据
    form,
    isGenerating,
    progress,
    currentStep,
    errorMessage,
    showPreferencesDialog,
    generatedIdeas,
    recentHistory,
    elementCategories,
    topicSuggestions,
    stats,
    preferences,
    copiedStates,
    isMobile,

    // 计算属性
    canGenerate,
    creativityDescription,
    creativityMarks,

    // 方法
    onTopicInput,
    onCreativityChange,
    selectTopicSuggestion,
    toggleElement,
    generateIdeas,
    copyIdea,
    copyAllIdeas,
    exportIdeas,
    regenerateIdeas,
    applyIdea,
    applyHistoryParams,
    clearHistory,
    savePreferences,
    formatDate
  }
}