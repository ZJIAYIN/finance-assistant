# 金融投资智能助手

基于RAG（检索增强生成）的金融投资智能助手，通过爬取东方财富网数据，结合通义千问大模型提供投资问答服务。

## 技术架构

- **前端**: Vue3 + Element Plus + Pinia
- **后端**: FastAPI + SQLite + ChromaDB
- **向量检索**: LangChain + ChromaDB
- **大模型**: 通义千问 (DashScope)
- **爬虫**: requests + APScheduler
- **架构模式**: Repository + Service + API 分层架构

## 项目结构

```
finance-assistant/
├── backend/                     # FastAPI后端
│   ├── app/
│   │   ├── main.py             # 应用入口
│   │   ├── api/                # API路由层
│   │   │   ├── deps.py         # 依赖注入
│   │   │   └── v1/             # API版本1
│   │   │       ├── auth.py     # 认证接口
│   │   │       ├── chat.py     # 对话接口
│   │   │       ├── crawler.py  # 爬虫接口
│   │   │       ├── health.py   # 健康检查
│   │   │       └── session.py  # 会话接口
│   │   ├── core/               # 核心配置
│   │   │   ├── config.py       # 应用配置
│   │   │   ├── database.py     # 数据库连接
│   │   │   ├── security.py     # 安全工具
│   │   │   └── exceptions.py   # 业务异常
│   │   ├── models/             # ORM数据模型
│   │   ├── repositories/       # 数据访问层 (Repository模式)
│   │   │   ├── base.py         # 通用CRUD基类
│   │   │   ├── user.py         # 用户仓库
│   │   │   ├── session.py      # 会话仓库
│   │   │   └── conversation.py # 对话仓库
│   │   ├── schemas/            # Pydantic DTO
│   │   │   ├── auth.py
│   │   │   ├── chat.py
│   │   │   ├── crawler.py
│   │   │   └── session.py
│   │   └── services/           # 业务逻辑层
│   │       ├── embedding_service.py   # 文本嵌入
│   │       ├── llm_service.py         # LLM调用
│   │       ├── rag_service.py         # 向量检索
│   │       ├── agent_service.py       # 对话编排
│   │       ├── auth_service.py        # 认证服务
│   │       ├── crawler/               # 爬虫模块
│   │       │   ├── base.py
│   │       │   ├── eastmoney.py
│   │       │   ├── scheduler.py
│   │       │   └── vectorize.py
│   │       └── notification/          # 消息推送
│   ├── data/                   # 数据存储
│   │   ├── raw/                # 原始爬取数据
│   │   └── chroma/             # 向量数据库
│   ├── db/                     # SQLite数据库
│   └── requirements.txt
│
└── frontend/                   # Vue3前端
    ├── src/
    │   ├── api/               # API接口
    │   ├── stores/            # Pinia状态管理
    │   ├── views/             # 页面
    │   └── router/            # 路由
    └── package.json
```

## 架构特点

### 1. 分层架构
- **API层**: 处理HTTP请求/响应，使用 Pydantic Schemas 验证数据
- **Service层**: 业务逻辑处理，实现业务用例
- **Repository层**: 数据访问抽象，解耦数据库操作
- **Core层**: 基础设施（配置、数据库、安全）

### 2. 依赖注入
- 使用 FastAPI 的 Depends 实现依赖注入
- 集中在 `api/deps.py` 管理所有依赖

### 3. API 版本化
- 所有接口位于 `/api/v1/*` 路径下
- 便于后续版本迭代

### 4. 业务异常体系
- 自定义异常类统一处理业务错误
- 全局异常处理器自动转换 HTTP 响应

## 快速开始

### 1. 环境要求

- Python 3.8+
- Node.js 16+
- DashScope API Key (通义千问)

### 2. 后端启动

```bash
cd backend

# 创建虚拟环境
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
copy .env.example .env
# 编辑 .env 填入你的 DASHSCOPE_API_KEY

# 启动服务
uvicorn app.main:app --reload
```

后端服务将运行在 http://localhost:8000

**注意**: 重构后入口文件位于 `app/main.py`，启动命令已更新为 `uvicorn app.main:app`

### 3. 前端启动

```bash
cd frontend

# 安装依赖
npm install

# 更新 API 路径（添加 /v1 前缀）
# 修改 src/api/request.js 中的 baseURL

# 启动开发服务器
npm run dev
```

前端将运行在 http://localhost:3000

## 使用说明

1. **注册/登录**: 首次使用需要注册账号
2. **新建会话**: 点击"新建会话"开始对话
3. **提问**: 输入金融相关问题，如"新能源板块怎么样？"
4. **查看历史**: 左侧列表显示所有会话，点击可切换

## 数据更新机制

- **每日09:00**: 自动爬取东方财富网数据并更新向量库
- **t-1数据策略**: 使用昨日收盘后的数据进行检索增强
- **数据保留**: 向量数据默认保留7天，原始文件长期保留

## API文档

启动后端后访问: http://localhost:8000/docs

### API 路径变更
重构后所有 API 添加了版本前缀：`/api/v1/*`

| 旧路径 | 新路径 |
|--------|--------|
| `/api/auth/login` | `/api/v1/auth/login` |
| `/api/chat` | `/api/v1/chat` |
| `/api/sessions` | `/api/v1/sessions` |
| `/api/crawler/*` | `/api/v1/crawler/*` |

## 开发指南

### 添加新功能

1. **添加新接口**:
   - 在 `app/schemas/` 定义请求/响应模型
   - 在 `app/api/v1/` 添加路由
   - 在 `app/services/` 实现业务逻辑（如需要）

2. **添加数据访问**:
   - 在 `app/repositories/` 继承 BaseRepository
   - 添加特定查询方法

3. **添加业务逻辑**:
   - 在 `app/services/` 创建服务类
   - 通过依赖注入使用 Repository

## 注意事项

1. 需要配置有效的 DashScope API Key
2. 首次运行会自动创建数据库和目录结构
3. 向量数据需要时间积累，首次使用可能检索不到历史数据
4. **前端需要更新 API 路径**，添加 `/v1` 前缀

## License

MIT
