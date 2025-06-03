<template>
  <el-dialog
    v-model="visible"
    title="分享小说"
    width="500px"
    :before-close="handleClose"
  >
    <div class="share-content">
      <p class="share-description">
        分享您的小说给其他人查看，您可以设置访问权限和有效期。
      </p>
      
      <el-form :model="form" label-width="100px">
        <el-form-item label="访问权限">
          <el-radio-group v-model="form.access_level">
            <el-radio label="public">公开访问</el-radio>
            <el-radio label="restricted">限制访问</el-radio>
            <el-radio label="private">私密访问</el-radio>
          </el-radio-group>
          <div class="form-help">
            <div v-if="form.access_level === 'public'">任何人都可以通过链接访问</div>
            <div v-else-if="form.access_level === 'restricted'">需要密码才能访问</div>
            <div v-else>只有您可以访问</div>
          </div>
        </el-form-item>
        
        <el-form-item 
          v-if="form.access_level === 'restricted'" 
          label="访问密码"
        >
          <el-input
            v-model="form.password"
            placeholder="设置访问密码"
            show-password
            maxlength="20"
          />
        </el-form-item>
        
        <el-form-item label="有效期">
          <el-select v-model="form.expires_in" placeholder="选择有效期">
            <el-option label="永久有效" :value="null" />
            <el-option label="1天" :value="1" />
            <el-option label="7天" :value="7" />
            <el-option label="30天" :value="30" />
            <el-option label="90天" :value="90" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="包含内容">
          <el-checkbox-group v-model="form.includes">
            <el-checkbox label="outline">大纲</el-checkbox>
            <el-checkbox label="characters">角色设定</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
      </el-form>
    </div>

    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" @click="handleShare" :loading="sharing">
          生成分享链接
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import type { NovelDetailResponse } from '@/api/novels'

interface Props {
  modelValue: boolean
  novel?: NovelDetailResponse | null
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'share', data: any): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// 响应式数据
const visible = ref(false)
const sharing = ref(false)

const form = reactive({
  access_level: 'public',
  password: '',
  expires_in: null as number | null,
  includes: [] as string[]
})

// 监听显示状态
watch(() => props.modelValue, (newValue) => {
  visible.value = newValue
  if (newValue) {
    resetForm()
  }
})

watch(visible, (newValue) => {
  emit('update:modelValue', newValue)
})

// 方法定义
const resetForm = () => {
  form.access_level = 'public'
  form.password = ''
  form.expires_in = null
  form.includes = []
}

const handleClose = () => {
  visible.value = false
}

const handleShare = () => {
  sharing.value = true
  
  const shareData = {
    access_level: form.access_level,
    password: form.password || undefined,
    expires_in: form.expires_in || undefined,
    include_outline: form.includes.includes('outline'),
    include_characters: form.includes.includes('characters')
  }
  
  emit('share', shareData)
  sharing.value = false
}
</script>

<style scoped lang="scss">
.share-content {
  .share-description {
    margin-bottom: 20px;
    color: #606266;
    font-size: 14px;
    line-height: 1.6;
  }
  
  .form-help {
    margin-top: 5px;
    font-size: 12px;
    color: #909399;
  }
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>