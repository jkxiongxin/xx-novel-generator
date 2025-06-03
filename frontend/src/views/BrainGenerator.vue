<template>
  <div class="brain-generator">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="container">
        <div class="header-content">
          <h1 class="page-title">
            <el-icon class="title-icon"><Sunny /></el-icon>
            脑洞生成器
          </h1>
          <p class="page-subtitle">释放想象力，让AI帮你打开脑洞世界的大门！</p>
          <div class="header-stats" v-if="stats">
            <div class="stat-item">
              <span class="stat-value">{{ stats.total_generations }}</span>
              <span class="stat-label">总生成次数</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ stats.total_ideas }}</span>
              <span class="stat-label">创意总数</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ stats.average_ideas_per_generation.toFixed(1) }}</span>
              <span class="stat-label">平均创意数</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="container">
      <div class="generator-layout">
        <!-- 左侧控制面板 -->
        <div class="control-panel">
          <el-card class="generator-panel">
            <template #header>
              <div class="panel-title">
                <el-icon class="icon"><MagicStick /></el-icon>
                创意生成控制台
              </div>
            </template>

            <!-- 主题输入区域 -->
            <div class="input-section">
              <label class="input-label">
                <el-icon><Edit /></el-icon>
                主题关键词 *
              </label>
              <el-input
                v-model="form.topic"
                class="topic-input"
                type="textarea"
                :rows="3"
                placeholder="输入你的创作主题，比如：穿越时空的咖啡师、会读心术的图书管理员..."
                maxlength="500"
                show-word-limit
                @input="onTopicInput"
              />
              <!-- 主题建议 -->
              <div v-if="topicSuggestions.length > 0" class="topic-suggestions">
                <div class="suggestions-title">💡 主题建议：</div>
                <el-tag
                  v-for="suggestion in topicSuggestions"
                  :key="suggestion.topic"
                  class="suggestion-tag"
                  @click="selectTopicSuggestion(suggestion.topic)"
                >
                  {{ suggestion.topic }}
                </el-tag>
              </div>
            </div>

            <!-- 参数设置区域 -->
            <div class="parameter-section">
              <div class="parameter-group">
                <div class="group-title">生成参数</div>
                
                <!-- 创意程度 -->
                <div class="parameter-item">
                  <div class="item-label">
                    <el-icon><Star /></el-icon>
                    创意程度：{{ creativityDescription }}
                  </div>
                  <div class="item-control">
                    <el-slider
                      v-model="form.creativity_level"
                      :min="1"
                      :max="10"
                      :step="1"
                      :marks="creativityMarks"
                      class="creativity-slider"
                      @change="onCreativityChange"
                    />
                  </div>
                </div>

                <!-- 生成数量 -->
                <div class="parameter-item">
                  <div class="item-label">
                    <el-icon><Grid /></el-icon>
                    生成数量
                  </div>
                  <div class="item-control">
                    <el-select v-model="form.idea_count" style="width: 100%">
                      <el-option label="5个创意" :value="5" />
                      <el-option label="10个创意" :value="10" />
                      <el-option label="15个创意" :value="15" />
                      <el-option label="20个创意" :value="20" />
                    </el-select>
                  </div>
                </div>

                <!-- 创意类型 -->
                <div class="parameter-item">
                  <div class="item-label">
                    <el-icon><Collection /></el-icon>
                    创意类型
                  </div>
                  <div class="item-control">
                    <el-checkbox-group v-model="form.idea_type">
                      <el-checkbox value="plot">情节创意</el-checkbox>
                      <el-checkbox value="character">角色创意</el-checkbox>
                      <el-checkbox value="worldview">世界观创意</el-checkbox>
                      <el-checkbox value="mixed">混合创意</el-checkbox>
                    </el-checkbox-group>
                  </div>
                </div>

                <!-- 风格选择 -->
                <div class="parameter-item">
                  <div class="item-label">
                    <el-icon><Brush /></el-icon>
                    创作风格
                  </div>
                  <div class="item-control">
                    <el-select v-model="form.style" placeholder="选择风格" style="width: 100%">
                      <el-option label="幽默轻松" value="humorous" />
                      <el-option label="严肃深刻" value="serious" />
                      <el-option label="浪漫温馨" value="romantic" />
                      <el-option label="悬疑紧张" value="suspense" />
                      <el-option label="奇幻冒险" value="fantasy" />
                      <el-option label="科幻未来" value="scifi" />
                    </el-select>
                  </div>
                </div>
              </div>

              <!-- 要素标签 -->
              <div class="parameter-group">
                <div class="group-title">要素标签</div>
                <div class="elements-container">
                  <div v-for="category in elementCategories" :key="category.category" class="element-category">
                    <div class="category-name">{{ category.display_name }}</div>
                    <div class="element-tags">
                      <el-tag
                        v-for="element in category.elements.slice(0, 8)"
                        :key="element.name"
                        :type="(form.elements || []).includes(element.name) ? 'primary' : ''"
                        class="element-tag"
                        @click="toggleElement(element.name)"
                      >
                        {{ element.name }}
                      </el-tag>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 补充说明 -->
              <div class="parameter-group">
                <div class="group-title">补充说明</div>
                <el-input
                  v-model="form.user_input"
                  type="textarea"
                  :rows="2"
                  placeholder="补充你的想法或特殊要求..."
                  maxlength="1000"
                  show-word-limit
                />
              </div>
            </div>

            <!-- 生成按钮区域 -->
            <div class="generate-section">
              <el-button
                type="primary"
                size="large"
                class="generate-btn"
                :class="{ loading: isGenerating }"
                :loading="isGenerating"
                :disabled="!canGenerate"
                @click="generateIdeas"
              >
                <el-icon class="icon"><MagicStick /></el-icon>
                {{ isGenerating ? currentStep : '生成脑洞' }}
              </el-button>
              
              <!-- 生成进度 -->
              <div v-if="isGenerating" class="progress-info">
                <el-progress :percentage="progress" :show-text="false" />
                <div class="progress-text">{{ currentStep }}</div>
              </div>
            </div>

            <!-- 用户偏好设置 -->
            <div class="preferences-section">
              <el-button
                text
                type="primary"
                @click="showPreferencesDialog = true"
              >
                <el-icon><Setting /></el-icon>
                偏好设置
              </el-button>
            </div>
          </el-card>

          <!-- 历史记录面板 -->
          <el-card class="history-panel" v-if="!isMobile">
            <template #header>
              <div class="panel-title">
                <el-icon class="icon"><Clock /></el-icon>
                历史记录
                <el-button
                  text
                  type="danger"
                  size="small"
                  @click="clearHistory"
                  style="margin-left: auto;"
                >
                  清空
                </el-button>
              </div>
            </template>

            <div class="history-list">
              <div
                v-for="item in recentHistory"
                :key="item.id"
                class="history-item"
                @click="applyHistoryParams(item)"
              >
                <div class="history-topic">{{ item.topic }}</div>
                <div class="history-meta">
                  <span>{{ item.ideas_count }}个创意</span>
                  <span>{{ formatDate(item.created_at) }}</span>
                </div>
              </div>
              
              <div v-if="recentHistory.length === 0" class="empty-history">
                <el-icon><DocumentAdd /></el-icon>
                <span>暂无历史记录</span>
              </div>
            </div>
          </el-card>
        </div>

        <!-- 右侧结果展示区域 -->
        <div class="results-area">
          <!-- 结果头部 -->
          <div class="results-header" v-if="generatedIdeas.length > 0">
            <div class="results-title">
              <el-icon><Trophy /></el-icon>
              生成结果 ({{ generatedIdeas.length }}个创意)
            </div>
            <div class="results-actions">
              <el-button size="small" @click="copyAllIdeas">
                <el-icon><DocumentCopy /></el-icon>
                全部复制
              </el-button>
              <el-dropdown @command="exportIdeas">
                <el-button size="small">
                  <el-icon><Download /></el-icon>
                  导出
                  <el-icon class="el-icon--right"><ArrowDown /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="txt">导出为TXT</el-dropdown-item>
                    <el-dropdown-item command="json">导出为JSON</el-dropdown-item>
                    <el-dropdown-item command="csv">导出为CSV</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
              <el-button size="small" type="warning" @click="regenerateIdeas">
                <el-icon><Refresh /></el-icon>
                重新生成
              </el-button>
            </div>
          </div>

          <!-- 创意卡片网格 -->
          <div v-if="generatedIdeas.length > 0" class="ideas-grid">
            <div
              v-for="(idea, index) in generatedIdeas"
              :key="idea.id"
              class="idea-card"
              :class="{ 'idea-card--copied': copiedStates[index] }"
            >
              <div class="card-header">
                <div class="idea-index">{{ index + 1 }}</div>
                <div class="card-actions">
                  <el-tooltip content="复制创意" placement="top">
                    <el-button
                      size="small"
                      text
                      @click="copyIdea(idea.content, index)"
                    >
                      <el-icon><DocumentCopy /></el-icon>
                    </el-button>
                  </el-tooltip>
                  <el-tooltip content="应用到创作" placement="top">
                    <el-button
                      size="small"
                      text
                      type="primary"
                      @click="applyIdea(idea)"
                    >
                      <el-icon><Plus /></el-icon>
                    </el-button>
                  </el-tooltip>
                </div>
              </div>
              
              <div class="idea-content">
                <p>{{ idea.content }}</p>
              </div>
              
              <div class="card-footer">
                <div class="idea-tags">
                  <el-tag
                    v-for="tag in idea.tags.slice(0, 3)"
                    :key="tag"
                    size="small"
                    class="tag"
                  >
                    {{ tag }}
                  </el-tag>
                </div>
                
                <div class="idea-scores">
                  <el-tooltip content="创意指数" placement="top">
                    <div class="score-item">
                      <el-icon><Star /></el-icon>
                      {{ idea.creativity_score.toFixed(1) }}
                    </div>
                  </el-tooltip>
                  <el-tooltip content="实用指数" placement="top">
                    <div class="score-item">
                      <el-icon><Tools /></el-icon>
                      {{ idea.practical_score.toFixed(1) }}
                    </div>
                  </el-tooltip>
                </div>
              </div>
              
              <!-- 复制成功反馈 -->
              <div v-if="copiedStates[index]" class="copy-feedback">
                <el-icon><Check /></el-icon>
                已复制
              </div>
            </div>
          </div>

          <!-- 空状态 -->
          <div v-else class="empty-state">
            <div class="empty-icon">
              <el-icon><Sunny /></el-icon>
            </div>
            <div class="empty-text">还没有生成创意</div>
            <div class="empty-description">
              输入一个有趣的主题，点击"生成脑洞"开始创作吧！
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 用户偏好设置对话框 -->
    <el-dialog
      v-model="showPreferencesDialog"
      title="偏好设置"
      width="500px"
      :before-close="savePreferences"
    >
      <el-form :model="preferences" label-width="120px">
        <el-form-item label="默认创意程度">
          <el-slider
            v-model="preferences.default_creativity_level"
            :min="1"
            :max="10"
            show-input
          />
        </el-form-item>
        
        <el-form-item label="默认生成数量">
          <el-select v-model="preferences.default_idea_count">
            <el-option label="5个" :value="5" />
            <el-option label="10个" :value="10" />
            <el-option label="15个" :value="15" />
            <el-option label="20个" :value="20" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="偏好类型">
          <el-checkbox-group v-model="preferences.preferred_types">
            <el-checkbox value="plot">情节创意</el-checkbox>
            <el-checkbox value="character">角色创意</el-checkbox>
            <el-checkbox value="worldview">世界观创意</el-checkbox>
            <el-checkbox value="mixed">混合创意</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        
        <el-form-item label="自动保存历史">
          <el-switch v-model="preferences.auto_save_history" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showPreferencesDialog = false">取消</el-button>
        <el-button type="primary" @click="savePreferences">保存</el-button>
      </template>
    </el-dialog>

    <!-- 错误提示 -->
    <div v-if="errorMessage" class="error-banner">
      <el-alert
        :title="errorMessage"
        type="error"
        show-icon
        :closable="true"
        @close="errorMessage = ''"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import {
  Sunny,
  MagicStick,
  Edit,
  Star,
  Grid,
  Collection,
  Brush,
  Setting,
  Clock,
  DocumentAdd,
  Trophy,
  DocumentCopy,
  Download,
  ArrowDown,
  Refresh,
  Plus,
  Tools,
  Check
} from '@element-plus/icons-vue'

import { useBrainGenerator } from './BrainGenerator'

// 使用组合式函数
const {
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
} = useBrainGenerator()
</script>

<style scoped lang="scss">
@import './BrainGenerator.scss';
</style>