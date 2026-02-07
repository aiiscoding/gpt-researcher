# GPT-Researcher 技术栈学习路线

> 适合已掌握 Python 基础语法的学习者，通过 gpt-researcher 项目系统学习全栈 + AI 技术栈。

## 项目技术栈全景

```
┌─────────────────────────────────────────────────────────────┐
│                    GPT-Researcher 技术全景                    │
├──────────────┬──────────────┬───────────────┬───────────────┤
│  Python 后端  │   AI / LLM   │    前端开发     │    DevOps     │
├──────────────┼──────────────┼───────────────┼───────────────┤
│ FastAPI      │ LangChain    │ Next.js       │ Docker        │
│ Pydantic     │ OpenAI API   │ React         │ Docker Compose│
│ asyncio      │ LangGraph    │ TypeScript    │ Nginx         │
│ WebSocket    │ RAG/FAISS    │ Tailwind CSS  │ Terraform     │
│ httpx        │ Prompt Eng.  │ Axios         │ Git           │
│ BeautifulSoup│ MCP Protocol │ Framer Motion │               │
└──────────────┴──────────────┴───────────────┴───────────────┘
```

---

## 第一阶段：Python 进阶

夯实 Python 核心特性，这些在项目中被大量使用。

### 学习目标

| 技术点 | 项目中的体现 | 关键文件 |
|--------|-------------|---------|
| 面向对象编程 (OOP) | `GPTResearcher` 类设计 | `gpt_researcher/agent.py` |
| 异步编程 (asyncio/await) | 整个项目 async-first 架构 | `gpt_researcher/agent.py` |
| 类型注解 (Type Hints) | Pydantic 模型、函数签名 | `gpt_researcher/config/config.py` |
| 装饰器 (Decorators) | FastAPI 路由 `@app.get()` | `backend/server/app.py` |
| 模块与包管理 | pyproject.toml、包结构 | 项目根目录 |

### 练习任务

- [ ] 阅读 `gpt_researcher/agent.py`，画出 `GPTResearcher` 类的方法调用关系图
- [ ] 将一个同步函数改写为异步函数，理解 `async/await` 的工作原理
- [ ] 阅读 `pyproject.toml`，理解项目依赖管理方式

---

## 第二阶段：Web 后端开发 (FastAPI)

### 学习目标

| 技术点 | 项目中的体现 | 关键文件 |
|--------|-------------|---------|
| FastAPI 框架 | REST API 服务 | `backend/server/app.py` |
| Pydantic 数据验证 | 请求/响应模型 | `gpt_researcher/config/config.py` |
| WebSocket 实时通信 | 研究进度实时推送 | `backend/server/app.py` |
| SSE (Server-Sent Events) | 流式更新 | sse-starlette 相关代码 |
| HTTP 客户端 (httpx) | 网页抓取、API 调用 | `gpt_researcher/scraper/` |

### 练习任务

- [ ] 启动后端服务，访问 `/docs` 查看自动生成的 API 文档
- [ ] 跟踪一次完整的研究请求：从 API 入口到结果返回
- [ ] 尝试添加一个新的 API 端点（比如返回系统状态）
- [ ] 理解 WebSocket 连接的建立和消息推送流程

---

## 第三阶段：AI / LLM 核心技术（项目核心）

这是本项目最核心的部分，建议投入最多时间。

### 学习路线

```
LLM API 基础调用
    │
    ▼
Prompt Engineering（提示词工程）
    │
    ▼
LangChain 框架
    │
    ▼
RAG（检索增强生成）
    │
    ▼
Agent 架构
    │
    ▼
多 Agent 协作 (LangGraph)
```

### 学习目标

| 技术点 | 项目中的体现 | 关键文件 |
|--------|-------------|---------|
| LLM API 调用 | 多模型提供商支持 | `gpt_researcher/llm_provider/` |
| Prompt Engineering | 研究提示词设计 | `gpt_researcher/prompts/` |
| LangChain | LLM 编排框架 | 全局使用 |
| 文档分割 | 长文档切分处理 | langchain-text-splitters 相关 |
| 向量存储 (RAG) | FAISS 向量检索 | `gpt_researcher/vector_store/` |
| Embedding | 文本向量化 | tiktoken 相关代码 |
| LangGraph | 多智能体协作 | `multi_agents/` |
| MCP 协议 | 工具/资源共享 | `mcp-server/` |

### 练习任务

- [ ] 阅读 `gpt_researcher/prompts/` 中的提示词，理解 Prompt 设计思路
- [ ] 阅读 `gpt_researcher/llm_provider/`，理解如何统一调用不同 LLM
- [ ] 阅读 `gpt_researcher/vector_store/`，理解 RAG 检索流程
- [ ] 阅读 `multi_agents/` 中的代码，理解 LangGraph 状态机工作原理
- [ ] 尝试修改一个 Prompt，观察输出变化

---

## 第四阶段：网页抓取与数据处理

### 学习目标

| 技术点 | 项目中的体现 | 关键文件 |
|--------|-------------|---------|
| BeautifulSoup4 | HTML 解析 | `gpt_researcher/scraper/` |
| 搜索引擎 API | Tavily、DuckDuckGo 等 | `gpt_researcher/retrievers/` |
| PDF/DOCX 处理 | 文档生成与解析 | PyMuPDF、python-docx 相关 |
| Markdown 处理 | 报告生成 | `gpt_researcher/utils/` |
| Jinja2 模板 | 报告模板渲染 | 模板文件 |

### 练习任务

- [ ] 阅读 `gpt_researcher/retrievers/`，理解不同搜索源的实现
- [ ] 尝试添加一个新的搜索数据源（retriever）
- [ ] 阅读 scraper 代码，理解网页内容提取流程
- [ ] 尝试添加一种新的报告输出格式

---

## 第五阶段：前端开发（可选）

### 学习路线

```
HTML/CSS/JavaScript 基础
    │
    ▼
TypeScript
    │
    ▼
React 组件化开发
    │
    ▼
Next.js 全栈框架
    │
    ▼
Tailwind CSS 样式
```

### 学习目标

| 技术点 | 关键文件 |
|--------|---------|
| React 组件 | `frontend/nextjs/components/` |
| Next.js 路由与 SSR | `frontend/nextjs/app/` |
| TypeScript 类型系统 | `frontend/nextjs/` 中的 `.tsx` 文件 |
| Tailwind CSS | 组件中的 className |
| WebSocket 客户端 | 前端与后端的实时通信 |

### 练习任务

- [ ] 阅读前端组件代码，理解 React 组件结构
- [ ] 尝试修改 UI 样式或添加一个新的展示组件
- [ ] 理解前后端通过 WebSocket 通信的完整流程

---

## 第六阶段：DevOps 与部署（可选）

### 学习目标

| 技术点 | 关键文件 |
|--------|---------|
| Docker | `Dockerfile`, `Dockerfile.fullstack` |
| Docker Compose | `docker-compose.yml` |
| 多阶段构建 | `Dockerfile.fullstack`（前端构建 + 后端部署） |
| Nginx | 反向代理配置 |
| Terraform | `terraform/` |

### 练习任务

- [ ] 用 `docker-compose up` 启动整个项目
- [ ] 阅读 Dockerfile，理解多阶段构建
- [ ] 尝试修改 docker-compose.yml 添加新的服务

---

## 核心文件阅读顺序

建议按以下顺序阅读项目核心代码：

```
1. gpt_researcher/agent.py          ← 核心 Agent，理解整体架构
2. gpt_researcher/config/config.py  ← 配置系统，理解可配置项
3. backend/server/app.py            ← API 入口，理解请求流程
4. gpt_researcher/llm_provider/     ← LLM 调用，理解模型交互
5. gpt_researcher/prompts/          ← 提示词，理解 AI 指令设计
6. gpt_researcher/retrievers/       ← 搜索源，理解数据获取
7. gpt_researcher/scraper/          ← 爬虫，理解网页处理
8. gpt_researcher/vector_store/     ← 向量存储，理解 RAG
9. multi_agents/                    ← 多 Agent，理解高级编排
10. frontend/nextjs/                ← 前端，理解用户界面
```

## 实践建议

1. **先跑起来** — 用 Docker 或直接运行把项目跑通，直观感受功能
2. **跟踪请求流** — 从 API 入口跟踪一次完整的研究请求
3. **每阶段做小改动** — 添加搜索源、修改 Prompt、新增报告格式等
4. **写学习笔记** — 每学完一个模块记录关键概念和心得
5. **提交代码** — 每次改动都用 Git 提交，养成版本控制习惯
