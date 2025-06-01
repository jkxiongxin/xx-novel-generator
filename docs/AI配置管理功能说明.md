# AI配置管理功能说明

## 概述

AI配置管理是AI Writer系统的核心功能之一，允许用户管理和配置多种AI模型，支持自定义API端点、参数配置和提示词模板。本功能提供了灵活的AI模型接入方案，用户可以根据需要配置不同的AI服务。

## 功能特性

### 1. 多模型支持
- **OpenAI兼容**: 支持OpenAI API格式的模型服务
- **Claude兼容**: 支持Anthropic Claude API格式
- **自定义HTTP**: 支持任意HTTP API端点
- **HuggingFace**: 支持HuggingFace推理API
- **Ollama**: 支持本地Ollama服务
- **OpenRouter**: 支持OpenRouter代理服务

### 2. 配置管理
- **CRUD操作**: 创建、读取、更新、删除AI配置
- **批量操作**: 支持批量启用、禁用、删除配置
- **优先级管理**: 配置优先级排序
- **默认配置**: 设置默认使用的AI配置
- **模板创建**: 从预设模板快速创建配置

### 3. 高级功能
- **自定义请求头**: 支持添加自定义HTTP请求头
- **参数映射**: 自定义请求参数映射
- **响应映射**: 配置响应数据解析路径
- **提示词模板**: 自定义系统消息和提示词模板
- **使用限制**: 设置每日/每月调用限制
- **连接测试**: 实时测试AI配置连接状态

## 技术架构

### 后端架构

#### 1. 数据模型 (`AIModelConfig`)
```python
class AIModelConfig(Base):
    # 基础信息
    name: str                    # 配置名称
    description: str             # 配置描述
    model_type: ModelType        # 模型类型
    is_active: bool             # 是否启用
    is_default: bool            # 是否默认
    
    # API配置
    api_endpoint: str           # API端点URL
    api_key: str               # API密钥
    model_name: str            # 模型名称
    request_format: RequestFormat # 请求格式
    
    # 请求参数
    max_tokens: int            # 最大Token数
    temperature: Decimal       # 温度参数
    timeout: int              # 超时时间
    retry_count: int          # 重试次数
    
    # 高级配置
    request_headers: dict      # 自定义请求头
    request_params: dict       # 请求参数映射
    response_mapping: dict     # 响应映射
    prompt_template: str       # 提示词模板
    system_message: str        # 系统消息
    
    # 使用限制
    daily_limit: int          # 每日限制
    monthly_limit: int        # 每月限制
    priority: int             # 优先级
```

#### 2. API接口 (`/api/v1/ai-configs/`)
- `GET /` - 获取配置列表（支持筛选、分页）
- `POST /` - 创建新配置
- `GET /{id}` - 获取配置详情
- `PUT /{id}` - 更新配置
- `DELETE /{id}` - 删除配置
- `POST /{id}/test` - 测试配置连接
- `PATCH /{id}/toggle` - 切换配置状态
- `PATCH /{id}/set-default` - 设置默认配置
- `POST /batch` - 批量操作
- `GET /stats/overview` - 获取统计信息
- `GET /templates/list` - 获取配置模板
- `POST /templates/{name}` - 从模板创建配置

#### 3. 服务层架构
```python
# HTTP适配器 - 通用HTTP API调用
class HTTPAdapter(AIModelAdapter):
    def __init__(self, config: AIModelConfig)
    async def generate_text(...)
    async def generate_structured_response(...)
    async def test_connection(...)

# 适配器工厂 - 根据配置创建适配器
class AdapterFactory:
    @staticmethod
    def create_adapter(config: AIModelConfig) -> AIModelAdapter

# AI服务 - 统一的AI调用接口
class AIService:
    def load_user_adapters(user_id, db)
    async def generate_text(..., user_id, db)
    async def generate_structured_response(..., user_id, db)
```

### 前端架构

#### 1. API客户端 (`ai-configs.ts`)
```typescript
export interface AIModelConfig {
    id: number
    name: string
    model_type: string
    api_endpoint: string
    // ... 其他字段
}

export const aiConfigsApi = {
    getConfigs(params): Promise<AIModelConfigListResponse>
    createConfig(data): Promise<AIModelConfig>
    updateConfig(id, data): Promise<AIModelConfig>
    deleteConfig(id): Promise<{success: boolean}>
    testConfig(id, testData): Promise<AIModelConfigTestResponse>
    // ... 其他方法
}
```

#### 2. 页面组件 (`AIConfigs.vue`)
- **配置列表**: 支持列表视图和卡片视图
- **筛选搜索**: 按名称、类型、状态筛选
- **统计展示**: 配置数量统计和类型分布
- **操作功能**: 创建、编辑、删除、测试、批量操作

#### 3. 子组件
- `AIConfigDialog.vue` - 配置编辑对话框
- `AIConfigTemplateDialog.vue` - 模板选择对话框
- `AIConfigDetailDialog.vue` - 配置详情对话框
- `AIConfigTestDialog.vue` - 配置测试对话框

## 预设模板

系统提供以下预设模板：

### 1. OpenAI GPT-3.5
```python
{
    "name": "OpenAI GPT-3.5 Turbo",
    "model_type": "openai_compatible",
    "api_endpoint": "https://api.openai.com/v1/chat/completions",
    "model_name": "gpt-3.5-turbo",
    "request_format": "openai_chat",
    "max_tokens": 2000,
    "temperature": "0.7"
}
```

### 2. Claude 3
```python
{
    "name": "Claude 3 Sonnet",
    "model_type": "claude_compatible", 
    "api_endpoint": "https://api.anthropic.com/v1/messages",
    "model_name": "claude-3-sonnet-20240229",
    "request_format": "claude_messages",
    "max_tokens": 2000,
    "temperature": "0.7"
}
```

### 3. OpenRouter
```python
{
    "name": "OpenRouter Multi-Model",
    "model_type": "openrouter",
    "api_endpoint": "https://openrouter.ai/api/v1/chat/completions", 
    "model_name": "anthropic/claude-3-sonnet",
    "request_format": "openai_chat",
    "max_tokens": 2000,
    "temperature": "0.7"
}
```

## 使用流程

### 1. 创建配置
1. 访问AI配置管理页面
2. 点击"新建配置"或"从模板创建"
3. 填写配置信息（名称、API端点、密钥等）
4. 设置请求参数和高级选项
5. 测试连接确保配置正确
6. 保存配置

### 2. 管理配置
1. 查看配置列表和统计信息
2. 筛选和搜索特定配置
3. 编辑或删除现有配置
4. 启用/禁用配置
5. 设置默认配置
6. 批量操作多个配置

### 3. 使用配置
1. AI配置会自动集成到生成服务中
2. 系统优先使用用户的默认配置
3. 如果用户配置不可用，回退到系统默认配置
4. 支持在生成时指定特定配置

## 安全考虑

### 1. 数据保护
- API密钥加密存储
- 敏感信息不在日志中输出
- 配置详情页面不显示完整密钥

### 2. 访问控制
- 配置仅对创建用户可见
- 用户只能操作自己的配置
- API接口有身份验证和权限检查

### 3. 使用限制
- 支持设置每日/每月调用限制
- 防止API滥用和成本失控
- 可配置超时和重试机制

## 扩展性

### 1. 新模型支持
- 通过添加新的`ModelType`枚举值支持新模型
- 实现对应的适配器逻辑
- 添加预设模板

### 2. 自定义字段
- 数据模型支持JSON字段存储自定义配置
- 前端界面可扩展自定义字段编辑
- API接口保持向后兼容

### 3. 插件机制
- 未来可支持插件形式的自定义适配器
- 动态加载和配置第三方AI服务
- 社区贡献的模型适配器

## 监控和日志

### 1. 使用统计
- 记录API调用次数和成功率
- 统计Token使用量和成本
- 生成使用报告和分析

### 2. 错误监控
- 记录连接失败和错误日志
- 提供故障排除建议
- 自动重试和降级机制

### 3. 性能监控
- 监控API响应时间
- 统计并发请求量
- 优化资源使用

## 后续规划

### 1. 高级功能
- [ ] 配置版本管理和回滚
- [ ] 配置导入导出功能
- [ ] 团队配置共享
- [ ] 配置模板市场

### 2. 智能优化
- [ ] 自动配置推荐
- [ ] 成本优化建议
- [ ] 性能基准测试
- [ ] 智能负载均衡

### 3. 集成增强
- [ ] Webhook集成
- [ ] 第三方认证
- [ ] 配置API文档生成
- [ ] SDK和CLI工具

---

本文档描述了AI配置管理功能的完整架构和实现细节。该功能为AI Writer系统提供了灵活、安全、可扩展的AI模型管理能力，是系统的核心基础设施之一。