# 金融投资智能助手

基于RAG（检索增强生成）的金融投资智能助手，通过爬取东方财富网数据，结合通义千问大模型提供投资问答服务。

## 技术架构

- **前端**: Vue3 + Element Plus + Pinia
- **后端**: FastAPI + SQLite + ChromaDB
- **向量检索**: LangChain + ChromaDB
- **大模型**: 通义千问 (DashScope)
- **爬虫**: Playwright + requests
- **定时任务**: APScheduler

## 项目结构

```
finance-assistant/
├── backend/                # FastAPI后端
│   ├── app/
│   │   ├── api/           # API路由
│   │   ├── core/          # 配置、数据库、安全
│   │   ├── models/        # 数据模型
│   │   └── services/      # 业务逻辑
│   ├── crawler/           # 爬虫和向量化
│   ├── data/              # 数据存储
│   ├── db/                # SQLite数据库
│   ├── main.py            # 入口
│   └── requirements.txt
│
└── frontend/              # Vue3前端
    ├── src/
    │   ├── api/          # API接口
    │   ├── stores/       # Pinia状态
    │   ├── views/        # 页面
    │   └── router/       # 路由
    └── package.json
```

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
python main.py
```

后端服务将运行在 http://localhost:8000

### 3. 前端启动

```bash
cd frontend

# 安装依赖
npm install

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

## 注意事项

1. 需要配置有效的 DashScope API Key
2. 首次运行会自动创建数据库和目录结构
3. 向量数据需要时间积累，首次使用可能检索不到历史数据

## License

MIT
