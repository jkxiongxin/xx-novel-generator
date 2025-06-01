# AI智能小说创作平台 - 后端服务

这是AI智能小说创作平台的后端服务，基于FastAPI构建，提供RESTful API接口。

## 功能特性

- 🚀 基于FastAPI的高性能异步API
- 🗄️ SQLAlchemy ORM数据库操作
- 🔐 JWT认证和权限管理
- 🤖 AI模型集成支持
- 📝 完整的数据模型设计
- 🔄 Alembic数据库迁移
- 📊 自动化API文档生成
- 🧪 完整的测试覆盖

## 技术栈

- **语言**: Python 3.9+
- **框架**: FastAPI
- **数据库**: SQLite (开发) / PostgreSQL (生产)
- **ORM**: SQLAlchemy
- **迁移**: Alembic
- **认证**: JWT (python-jose)
- **密码**: bcrypt (passlib)
- **依赖管理**: Poetry

## 快速开始

### 环境要求

- Python 3.9+
- Poetry (推荐) 或 pip

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd backend
```

2. **安装依赖**
```bash
# 使用Poetry (推荐)
poetry install

# 或使用pip
pip install -r requirements.txt
```

3. **配置环境变量**
```bash
cp .env.example .env
# 编辑.env文件，配置必要的环境变量
```

4. **初始化数据库**
```bash
# 激活虚拟环境
poetry shell

# 创建数据库迁移
alembic revision --autogenerate -m "Initial migration"

# 执行迁移
alembic upgrade head
```

5. **启动服务**
```bash
# 开发模式
python app/main.py

# 或使用uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 访问服务

- **API文档**: http://localhost:8000/docs
- **ReDoc文档**: http://localhost:8000/redoc
- **健康检查**: http://localhost:8000/health

## 项目结构

```
backend/
├── app/                          # 应用核心代码
│   ├── __init__.py
│   ├── main.py                   # FastAPI应用入口
│   ├── core/                     # 核心配置和基础设施
│   │   ├── __init__.py
│   │   ├── config.py             # 应用配置
│   │   ├── database.py           # 数据库连接
│   │   ├── security.py           # 安全相关
│   │   └── dependencies.py       # 依赖注入
│   ├── models/                   # 数据模型
│   │   ├── __init__.py
│   │   ├── base.py               # 基础模型类
│   │   ├── user.py               # 用户模型
│   │   └── novel.py              # 小说模型
│   ├── schemas/                  # Pydantic模式定义
│   ├── api/                      # API路由
│   │   ├── __init__.py
│   │   └── v1/                   # API版本1
│   │       ├── __init__.py
│   │       └── api.py            # 路由聚合
│   ├── services/                 # 业务逻辑服务
│   └── utils/                    # 工具函数
├── tests/                        # 测试代码
├── alembic/                      # 数据库迁移
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
├── pyproject.toml                # Poetry配置
├── alembic.ini                   # Alembic配置
├── .env.example                  # 环境变量示例
└── README.md
```

## 开发指南

### 代码规范

项目遵循以下代码规范：

- **PEP 8**: Python代码风格指南
- **Type Hints**: 所有函数必须有类型注解
- **Docstring**: 公共函数必须有文档字符串
- **Black**: 代码格式化工具
- **isort**: 导入语句排序

### 数据库迁移

```bash
# 创建新的迁移文件
alembic revision --autogenerate -m "描述迁移内容"

# 执行迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1

# 查看迁移历史
alembic history
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_api/test_users.py

# 生成覆盖率报告
pytest --cov=app --cov-report=html
```

### API开发

1. **创建数据模型** (`app/models/`)
2. **定义Pydantic模式** (`app/schemas/`)
3. **实现业务逻辑** (`app/services/`)
4. **创建API路由** (`app/api/v1/`)
5. **编写测试** (`tests/`)

### 配置管理

所有配置通过环境变量管理，主要配置项：

- `DATABASE_URL`: 数据库连接字符串
- `SECRET_KEY`: JWT签名密钥
- `OPENAI_API_KEY`: OpenAI API密钥
- `DEBUG`: 调试模式开关

## 部署

### Docker部署 (推荐)

```bash
# 构建镜像
docker build -t ai-writer-backend .

# 运行容器
docker run -p 8000:8000 --env-file .env ai-writer-backend
```

### 生产环境部署

1. **设置环境变量**
2. **配置PostgreSQL数据库**
3. **运行数据库迁移**
4. **使用Gunicorn启动服务**

```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## API文档

启动服务后，可以通过以下地址访问API文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

主要API接口：

- `GET /health` - 健康检查
- `GET /api/v1/health` - API健康检查
- 更多接口将在后续开发中添加...

## 许可证

本项目采用 MIT 许可证。

## 贡献指南

1. Fork 项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 联系方式

如有问题，请联系开发团队或创建Issue。