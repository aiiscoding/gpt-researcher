# GPT-Researcher 深度学习计划

> 基于 v0.14.6 源码分析，从架构到细节的系统学习路径
> 目标：全面掌握项目架构，具备独立运维和二次开发能力

---

## 阶段一：项目全局认知（基础层）

### 1.1 项目定位与能力边界

- [ ] 理解 GPT-Researcher 是什么：基于 LLM 的自主研究代理，能自动搜索、抓取、分析、生成研究报告
- [ ] 了解核心使用场景：自动化研究报告生成、深度调研、多源信息汇总
- [ ] 掌握 7 种报告类型的区别：
  - `research_report` — 标准综合报告
  - `detailed_report` — 深度分析报告
  - `outline_report` — 结构化大纲
  - `resource_report` — 资源清单
  - `subtopic_report` — 子主题聚焦
  - `deep` — 深度研究（多轮迭代）
  - `custom_report` — 用户自定义
- [ ] 理解 3 种数据源模式：`web`（网页搜索）、`local`（本地文档）、`hybrid`（混合）

**关键文件：**
- `README.md`
- `gpt_researcher/utils/enum.py` — 所有枚举定义

---

### 1.2 技术栈总览

| 层级 | 技术 | 用途 |
|------|------|------|
| 语言 | Python >= 3.11 | 主语言 |
| Web框架 | FastAPI + Uvicorn | REST API & WebSocket |
| 前端 | Next.js 15 + React | Web UI |
| LLM框架 | LangChain v1 | LLM调用抽象 |
| 编排引擎 | LangGraph >= 0.2.76 | 多Agent状态机 |
| LLM抽象 | LiteLLM | 多供应商统一调用 |
| 数据验证 | Pydantic >= 2.5 | Schema验证 |
| 向量存储 | Pinecone / Chroma 等 | 语义检索 |
| 文档处理 | BeautifulSoup / PyMuPDF | 网页与PDF解析 |
| 容器化 | Docker + Compose | 部署方案 |
| IaC | Terraform | 基础设施自动化 |

**需要掌握的前置知识点：**
- [ ] Python 异步编程（async/await）
- [ ] FastAPI 基础（路由、依赖注入、WebSocket）
- [ ] LangChain 核心概念（Chain、LLM、Prompt Template、Document Loader）
- [ ] LangGraph 基础（StateGraph、Node、Edge、Conditional Edge）
- [ ] Pydantic v2 数据模型
- [ ] Docker 基本操作

---

### 1.3 项目目录结构

```
gpt-researcher/
├── gpt_researcher/          # 核心Python包（重点）
│   ├── agent.py             # ★ 核心入口：GPTResearcher 类（719行）
│   ├── prompts.py           # ★ 所有LLM提示词（40000+行）
│   ├── actions/             # 动作执行器
│   ├── skills/              # 技能模块
│   ├── retrievers/          # 搜索提供者（14种）
│   ├── scraper/             # 内容抓取器
│   ├── llm_provider/        # LLM供应商抽象层
│   ├── memory/              # 记忆与向量嵌入
│   ├── vector_store/        # 向量存储封装
│   ├── context/             # 上下文管理
│   ├── config/              # 配置系统
│   ├── document/            # 文档加载器
│   ├── mcp/                 # MCP协议支持
│   └── utils/               # 工具函数
│
├── backend/                 # FastAPI后端服务
│   ├── server/              # 服务器核心
│   └── report_type/         # 各报告类型的Agent实现
│
├── frontend/nextjs/         # Next.js前端
│
├── multi_agents/            # LangGraph多Agent编排
│   ├── agents/              # 各专业Agent定义
│   └── main.py              # 多Agent入口
│
├── main.py                  # FastAPI服务入口
├── cli.py                   # CLI命令行入口
├── tests/                   # 测试套件
├── docs/                    # 文档
├── mcp-server/              # MCP服务器
├── evals/                   # 评估脚本
└── terraform/               # 基础设施代码
```

- [ ] 通读目录结构，建立整体心智模型
- [ ] 理解四个入口点：`cli.py`、`main.py`、`gpt_researcher/__init__.py`（Python API）、`multi_agents/main.py`

---

## 阶段二：核心研究流水线（核心层）

### 2.1 GPTResearcher 主Agent

**文件：** `gpt_researcher/agent.py`（全文件精读）

这是整个项目的核心编排器，理解它就理解了 80% 的项目。

**需要掌握的知识点：**

- [ ] GPTResearcher 类的初始化流程
  - 配置加载（Config 对象）
  - LLM Provider 初始化（三级 LLM 策略）
  - Retriever 初始化
  - Memory / Embedding 初始化
- [ ] 研究执行主流程 `conduct_research()`
  1. 查询规划（生成研究大纲）
  2. 搜索执行（Retriever 调度）
  3. 内容抓取（Scraper 调度）
  4. 上下文压缩（ContextCompressor）
  5. 信息汇总存储
- [ ] 报告生成流程 `write_report()`
  1. 根据报告类型选择生成策略
  2. LLM 生成报告内容
  3. 格式化输出（Markdown/PDF/DOCX）
- [ ] 三级 LLM 策略
  - `FAST_LLM`（gpt-4o-mini）— 快速响应
  - `SMART_LLM`（gpt-4.1）— 详细分析
  - `STRATEGIC_LLM`（o4-mini）— 复杂推理
- [ ] 回调与流式输出机制（websocket, on_*callbacks）

---

### 2.2 配置系统

**文件：**
- `gpt_researcher/config/config.py` — Config 类
- `gpt_researcher/config/variables/default.py` — DEFAULT_CONFIG
- `gpt_researcher/config/variables/base.py` — BaseConfig Schema

**需要掌握的知识点：**

- [ ] 配置优先级：环境变量 > JSON配置文件 > 默认值
- [ ] 关键配置项分类：

| 配置类别 | 关键参数 | 默认值 |
|----------|----------|--------|
| LLM | `FAST_LLM`, `SMART_LLM`, `STRATEGIC_LLM` | openai:gpt-4o-mini, openai:gpt-4.1, openai:o4-mini |
| 搜索 | `RETRIEVER`, `MAX_SEARCH_RESULTS_PER_QUERY` | tavily, 5 |
| 抓取 | `SCRAPER`, `MAX_SCRAPER_WORKERS` | bs, 15 |
| 报告 | `REPORT_TYPE`, `TOTAL_WORDS`, `REPORT_FORMAT` | research_report, 1200, APA |
| 深度研究 | `DEEP_RESEARCH_BREADTH`, `DEEP_RESEARCH_DEPTH` | 3, 2 |
| MCP | `MCP_SERVERS`, `MCP_STRATEGY` | [], fast |
| 嵌入 | `EMBEDDING`, `SIMILARITY_THRESHOLD` | openai:text-embedding-3-small, 0.42 |
| 温度 | `TEMPERATURE` | 0.4 |

- [ ] 理解如何通过 `.env` 文件覆盖配置
- [ ] 理解运行时动态配置（通过 Python API 传参）

---

### 2.3 Actions 模块（动作执行层）

**目录：** `gpt_researcher/actions/`

- [ ] `retriever.py` — Retriever 选择与调度逻辑
  - `get_retrievers()` 函数：根据配置返回可用的搜索器列表
  - 支持多 Retriever 混合使用
- [ ] `query_processing.py` — 研究大纲与子查询生成
  - 如何将用户查询拆解为多个子查询
  - 研究大纲的 LLM 生成逻辑
- [ ] `report_generation.py` — 报告写作核心函数
  - 不同报告类型的生成策略
  - 引用与参考文献处理
- [ ] `web_scraping.py` — URL 抓取编排
  - 并发抓取策略
  - 限速与错误处理
- [ ] `markdown_processing.py` — 报告格式化
  - Markdown 输出
  - 表格与引用格式
- [ ] `agent_creator.py` — Agent 选择逻辑

---

### 2.4 Skills 模块（技能层）

**目录：** `gpt_researcher/skills/`

- [ ] `researcher.py` — **ResearchConductor**
  - 研究执行的核心编排
  - 子查询生成 → 并行搜索 → 结果聚合
- [ ] `writer.py` — **ReportGenerator**
  - 报告撰写引擎
  - 分节写作与合并
- [ ] `context_manager.py` — **ContextManager**
  - 上下文窗口管理
  - 相关性过滤
  - Token 限制处理
- [ ] `curator.py` — **SourceCurator**
  - 来源质量评估
  - 来源去重与排序
- [ ] `browser.py` — **BrowserManager**
  - 浏览器自动化
  - 动态页面处理
- [ ] `deep_research.py` — **DeepResearchSkill**
  - 多轮迭代研究
  - 广度与深度控制（BREADTH/DEPTH 参数）
  - 并发控制（CONCURRENCY 参数）
- [ ] `image_generator.py` — **ImageGenerator**
  - 图片生成集成（Gemini API）

---

## 阶段三：搜索与抓取子系统（数据层）

### 3.1 Retriever 搜索器体系

**目录：** `gpt_researcher/retrievers/`

**需要掌握的知识点：**

- [ ] Retriever 插件架构设计模式
  - 每个 Retriever 是独立子目录
  - 统一接口：`search(query, max_results)` → `List[Dict]`
- [ ] 14 种内置 Retriever 的定位与适用场景：

| Retriever | 适用场景 | 需要API Key |
|-----------|---------|-------------|
| `tavily` | 通用搜索（默认推荐） | 是 |
| `duckduckgo` | 免费通用搜索 | 否 |
| `arxiv` | 学术论文搜索 | 否 |
| `google` | Google搜索 | 是 |
| `serpapi` | Google搜索(SerpAPI) | 是 |
| `serper` | Google搜索(Serper) | 是 |
| `bing` | Bing搜索 | 是 |
| `exa` | 高级语义搜索 | 是 |
| `semantic_scholar` | 学术语义搜索 | 否 |
| `pubmed_central` | 医学文献 | 否 |
| `searchapi` | 通用搜索API | 是 |
| `searx` | 自建元搜索引擎 | 否（需部署实例） |
| `custom` | 自定义扩展基类 | 视实现而定 |
| `mcp` | MCP协议工具集成 | 视配置而定 |

- [ ] 如何编写自定义 Retriever（继承 `CustomRetriever`）
- [ ] 多 Retriever 混合搜索的实现方式

---

### 3.2 Scraper 抓取器体系

**目录：** `gpt_researcher/scraper/`

**需要掌握的知识点：**

- [ ] Scraper 分发架构（`scraper.py` 主调度器）
- [ ] 各抓取器的实现与适用场景：
  - `beautiful_soup/` — 静态 HTML 解析（默认，最轻量）
  - `browser/` — Selenium 浏览器自动化（动态页面）
  - `pymupdf/` — PDF 文档内容提取
  - `arxiv/` — Arxiv 论文专用抓取
  - `tavily_extract/` — Tavily 提取服务
  - `firecrawl/` — Firecrawl 云服务
  - `web_base_loader/` — LangChain 文档加载器
- [ ] 并发抓取策略
  - `MAX_SCRAPER_WORKERS` 配置（默认 15）
  - `SCRAPER_RATE_LIMIT_DELAY` 限速配置
- [ ] 错误处理与降级策略
- [ ] 内容清洗与标准化流程

---

### 3.3 上下文管理与向量嵌入

**文件：**
- `gpt_researcher/context/compression.py` — ContextCompressor
- `gpt_researcher/context/retriever.py` — SearchAPIRetriever
- `gpt_researcher/memory/embeddings.py` — Memory 类
- `gpt_researcher/vector_store/vector_store.py` — VectorStoreWrapper

**需要掌握的知识点：**

- [ ] ContextCompressor 工作原理
  - 将大量抓取内容压缩为相关摘要
  - LLM 辅助的相关性判断
- [ ] 向量嵌入系统
  - 默认使用 OpenAI text-embedding-3-small
  - 相似度阈值：0.42
  - 用于语义搜索和去重
- [ ] VectorStoreWrapper 集成
  - 支持 Pinecone、Chroma 等外部向量数据库
  - 过滤能力（metadata filtering）

---

## 阶段四：LLM 供应商抽象层

### 4.1 GenericLLMProvider

**文件：** `gpt_researcher/llm_provider/generic/base.py`

**需要掌握的知识点：**

- [ ] `provider:model` 语法解析
  - 示例：`openai:gpt-4o-mini`、`anthropic:claude-3-5-sonnet`、`ollama:llama3`
- [ ] 22+ 供应商支持列表：

| 供应商 | 标识 | 说明 |
|--------|------|------|
| OpenAI | `openai` | GPT系列 |
| Anthropic | `anthropic` | Claude系列 |
| Azure OpenAI | `azure_openai` | Azure托管版 |
| Google | `google` | Gemini系列 |
| Ollama | `ollama` | 本地部署 |
| Mistral | `mistral` | Mistral AI |
| HuggingFace | `huggingface` | 开源模型 |
| Groq | `groq` | 快速推理 |
| AWS Bedrock | `bedrock` | AWS云服务 |
| LiteLLM | `litellm` | 统一代理 |
| Cohere | `cohere` | Cohere模型 |
| Together | `together` | Together AI |
| DeepSeek | `deepseek` | DeepSeek模型 |
| 更多... | ... | ... |

- [ ] 动态 Provider 加载机制（基于 LangChain）
- [ ] 不同 Provider 的特殊参数处理
- [ ] Token 计数与限制管理（Tiktoken）
- [ ] 如何添加新的 LLM Provider

---

## 阶段五：提示词工程

### 5.1 Prompts 体系

**文件：** `gpt_researcher/prompts.py`（40000+ 行，最大单文件）

**需要掌握的知识点：**

- [ ] Prompt Family 架构
  - `get_prompt_family(family_name, config)` — 提示词族加载
  - 支持自定义提示词族（`PROMPT_FAMILY` 配置）
- [ ] 核心提示词分类：

| 用途 | 说明 |
|------|------|
| 查询规划 | 将用户查询拆解为子查询 |
| 搜索优化 | 生成搜索引擎友好的查询词 |
| 内容摘要 | 从抓取内容提取关键信息 |
| 报告写作 | 各类报告类型的写作提示 |
| 来源评估 | 评估来源可信度和相关性 |
| 大纲生成 | 生成报告结构大纲 |
| 引用格式 | APA/MLA 等引用格式化 |

- [ ] 提示词模板的变量注入机制
- [ ] 15 种写作语调（Tone）的提示词差异：
  - Objective / Formal / Analytical / Persuasive / Informative
  - Explanatory / Descriptive / Critical / Comparative / Speculative
  - Reflective / Narrative / Humorous / Optimistic / Pessimistic
- [ ] 如何自定义和扩展提示词

---

## 阶段六：多Agent编排系统（高级层）

### 6.1 LangGraph 多Agent架构

**目录：** `multi_agents/`

**需要掌握的知识点：**

- [ ] LangGraph StateGraph 核心概念
  - State 定义（`ResearchState`）
  - Node（Agent 节点）
  - Edge（节点连接）
  - Conditional Edge（条件路由）
- [ ] 多Agent工作流程：

```
Start → Browser(初始调研)
      → Planner(规划方案)
      → Human(人工审核) ──┐
      → Researcher(并行研究)  │ (拒绝则回到Planner)
      → Writer(撰写报告)   ←─┘
      → Publisher(发布)
      → End
```

- [ ] 7 种专业Agent的职责：

| Agent | 职责 | 文件位置 |
|-------|------|----------|
| ChiefEditorAgent | 总编排，创建和管理工作流 | `multi_agents/agents/` |
| ResearchAgent | 执行具体研究任务 | `multi_agents/agents/` |
| WriterAgent | 撰写报告章节 | `multi_agents/agents/` |
| EditorAgent | 规划和编辑内容 | `multi_agents/agents/` |
| PublisherAgent | 最终发布输出 | `multi_agents/agents/` |
| ReviewerAgent | 质量审查 | `multi_agents/agents/` |
| ReviserAgent | 根据反馈修订 | `multi_agents/agents/` |

- [ ] Human-in-the-Loop 集成
  - 人工审批节点
  - 条件边：accept → 继续 / revise → 回退
- [ ] ResearchState 状态容器结构：
  - `task` — 任务配置
  - `initial_research` — 初始研究结果
  - `research_plan` — 研究计划
  - `sections` — 报告章节
  - `human_feedback` — 人工反馈
  - `final_report` — 最终报告
- [ ] 并行执行能力（多个 Researcher 并行研究不同子主题）

---

## 阶段七：后端服务与API

### 7.1 FastAPI 服务

**文件：**
- `main.py` — 服务入口
- `backend/server/app.py` — FastAPI 应用定义

**需要掌握的知识点：**

- [ ] API 端点设计
  - REST API 端点（研究请求、报告下载）
  - WebSocket 端点（实时流式输出）
- [ ] WebSocket 通信机制
  - 研究进度实时推送
  - 中间结果流式展示
- [ ] 报告存储机制（内存存储 / 持久化）
- [ ] 文件上传/下载端点

---

### 7.2 后端报告类型实现

**目录：** `backend/report_type/`

- [ ] 各报告类型的 Agent 模式
  - 每种报告类型有独立的 Agent 实现
  - 理解各类型的数据流差异

---

## 阶段八：MCP 协议集成

### 8.1 Model Context Protocol

**目录：** `gpt_researcher/mcp/`

**需要掌握的知识点：**

- [ ] MCP 协议基础概念
  - 什么是 MCP（Model Context Protocol）
  - MCP Server vs MCP Client
- [ ] MCP 组件：
  - `MCPClientManager` — 管理 MCP 服务器连接
  - `MCPToolSelector` — LLM 辅助的工具选择
  - `MCPResearchSkill` — 通过 MCP 执行研究
  - `MCPStreamer` — 实时流式传输
- [ ] 3 种连接方式：
  - `stdio` — 子进程命令行通信
  - `websocket` — WebSocket 连接
  - `http` — HTTP/SSE 连接
- [ ] MCP 策略配置：
  - `fast` — 快速模式
  - `deep` — 深度模式
  - `disabled` — 禁用
- [ ] MCP Server 配置示例：
```python
mcp_configs = [
    {"command": "python", "args": ["server.py"], "name": "my_tool"},
    {"connection_url": "ws://localhost:8080/mcp", "connection_type": "websocket"},
    {"connection_url": "https://api.example.com/mcp", "connection_type": "http"}
]
```

---

## 阶段九：前端与部署

### 9.1 Next.js 前端

**目录：** `frontend/nextjs/`

- [ ] Next.js 15 App Router 结构
- [ ] 核心组件：
  - Settings 组件（配置面板）
  - Research 组件（研究交互界面）
- [ ] WebSocket 客户端通信
- [ ] 前端与后端的数据流

---

### 9.2 部署方案

- [ ] Docker 部署
  - `Dockerfile` — 单容器构建
  - `docker-compose.yml` — 多容器编排
  - 环境变量注入
- [ ] Terraform 部署
  - `terraform/` — 云基础设施定义
  - 适用于 AWS/GCP/Azure 部署
- [ ] CLI 模式部署（直接运行 `cli.py`）
- [ ] 生产环境注意事项
  - API Key 安全管理
  - 并发限制配置
  - 日志与监控（LangSmith 集成）

---

## 阶段十：可观测性与测试

### 10.1 日志与追踪

- [ ] Loguru 结构化日志
- [ ] LangSmith 集成（LangChain 生态监控）
  ```bash
  LANGCHAIN_TRACING_V2=true
  LANGCHAIN_API_KEY=xxx
  LANGCHAIN_PROJECT="gpt-researcher"
  ```
- [ ] 回调机制追踪研究过程

---

### 10.2 测试体系

**目录：** `tests/`

- [ ] Pytest 异步测试配置
- [ ] 核心测试类型：
  - 研究流程端到端测试（`research_test.py`）
  - MCP 集成测试（`test_mcp.py`）
  - 安全测试（`test_security_fix.py`）
  - 向量存储测试（`vector-store.py`）
  - 各组件单元测试（LLM/Retriever/Embedding）
- [ ] Docker 内运行测试
  ```bash
  docker compose --profile test up
  ```

---

## 阶段十一：扩展开发能力

### 11.1 自定义扩展点

掌握项目提供的所有扩展接口，方便二次开发：

- [ ] **自定义 Retriever**
  ```python
  class MyRetriever(CustomRetriever):
      async def search(self, query, max_results):
          return results
  ```
- [ ] **自定义 Scraper** — 配置 `SCRAPER` 环境变量
- [ ] **自定义 LLM Provider** — `provider:model` 语法
- [ ] **自定义提示词** — `PROMPT_FAMILY` 配置
- [ ] **自定义报告类型** — 扩展 `backend/report_type/`
- [ ] **MCP 工具扩展** — 通过 MCP Server 集成外部能力
- [ ] **自定义文档加载器** — 通过 `document_urls` 或 LangChain Document 对象

---

## 推荐学习顺序与时间分配

| 优先级 | 阶段 | 内容 | 重要度 |
|--------|------|------|--------|
| ★★★★★ | 阶段一 | 项目全局认知 | 基础必修 |
| ★★★★★ | 阶段二 | 核心研究流水线 | 核心必修 |
| ★★★★☆ | 阶段三 | 搜索与抓取子系统 | 核心必修 |
| ★★★★☆ | 阶段四 | LLM供应商抽象层 | 核心必修 |
| ★★★☆☆ | 阶段五 | 提示词工程 | 深度理解 |
| ★★★☆☆ | 阶段六 | 多Agent编排 | 高级进阶 |
| ★★☆☆☆ | 阶段七 | 后端服务与API | 运维必修 |
| ★★☆☆☆ | 阶段八 | MCP协议集成 | 扩展进阶 |
| ★☆☆☆☆ | 阶段九 | 前端与部署 | 运维参考 |
| ★★☆☆☆ | 阶段十 | 可观测性与测试 | 运维必修 |
| ★★★☆☆ | 阶段十一 | 扩展开发能力 | 二次开发 |

---

## 源码精读清单（按优先级）

### 第一梯队（必读）
1. `gpt_researcher/agent.py` — 核心 Agent，全文精读
2. `gpt_researcher/config/variables/default.py` — 所有默认配置
3. `gpt_researcher/skills/researcher.py` — 研究执行核心
4. `gpt_researcher/skills/writer.py` — 报告生成核心
5. `gpt_researcher/actions/retriever.py` — 搜索调度

### 第二梯队（重点读）
6. `gpt_researcher/llm_provider/generic/base.py` — LLM 抽象层
7. `gpt_researcher/skills/context_manager.py` — 上下文管理
8. `gpt_researcher/context/compression.py` — 上下文压缩
9. `gpt_researcher/actions/query_processing.py` — 查询规划
10. `gpt_researcher/actions/report_generation.py` — 报告生成

### 第三梯队（选读）
11. `gpt_researcher/retrievers/tavily/tavily.py` — 默认搜索器实现
12. `gpt_researcher/scraper/scraper.py` — 抓取器调度
13. `multi_agents/agents/` — 各专业 Agent
14. `gpt_researcher/skills/deep_research.py` — 深度研究
15. `gpt_researcher/mcp/client.py` — MCP 客户端
16. `gpt_researcher/prompts.py` — 提示词（按需查阅）

---

## 关键架构图

```
                    ┌──────────────────────────────────────┐
                    │           用户入口                     │
                    │  CLI │ FastAPI │ Python API │ Web UI  │
                    └─────────────────┬────────────────────┘
                                      │
                    ┌─────────────────▼────────────────────┐
                    │        GPTResearcher Agent            │
                    │   (agent.py - 核心编排器)              │
                    │                                       │
                    │  Config → LLM初始化 → Retriever初始化  │
                    └──┬──────────┬──────────┬─────────────┘
                       │          │          │
              ┌────────▼──┐  ┌───▼────┐  ┌──▼──────────┐
              │ Research   │  │Scraper │  │ Context     │
              │ Conductor  │  │Manager │  │ Manager     │
              │ (搜索执行)  │  │(内容抓取)│  │ (上下文管理) │
              └────┬───────┘  └───┬────┘  └──┬──────────┘
                   │              │           │
           ┌───────▼───────┐     │    ┌──────▼────────┐
           │  14种Retriever │     │    │ Memory &      │
           │  搜索引擎      │     │    │ Embeddings    │
           │  ┌──────────┐ │     │    │ (向量嵌入)     │
           │  │ Tavily   │ │     │    └───────────────┘
           │  │ DuckDDG  │ │     │
           │  │ Arxiv    │ │  ┌──▼──────────┐
           │  │ Google   │ │  │  7种Scraper  │
           │  │ MCP...   │ │  │  ┌────────┐ │
           │  └──────────┘ │  │  │ BS4    │ │
           └───────────────┘  │  │ Browser│ │
                              │  │ PDF    │ │
                              │  └────────┘ │
    ┌─────────────────────┐   └─────────────┘
    │  Report Generator   │
    │  (报告生成器)        │
    │                     │
    │  Prompts + LLM      │──→ 最终报告输出
    │  → Markdown/PDF/DOCX│    (research_report,
    └─────────────────────┘     detailed, deep...)

    ┌─────────────────────────────────────────────┐
    │     LLM Provider 抽象层 (22+ 供应商)          │
    │  OpenAI │ Anthropic │ Ollama │ Azure │ ...   │
    └─────────────────────────────────────────────┘

    ┌─────────────────────────────────────────────┐
    │     多Agent模式 (LangGraph 可选)              │
    │  ChiefEditor → Researcher → Writer           │
    │  → Editor → Reviewer → Publisher             │
    └─────────────────────────────────────────────┘
```

---

## 运维速查

### 常见问题排查

| 问题 | 排查方向 | 关键文件 |
|------|---------|---------|
| 搜索无结果 | 检查 Retriever 配置和 API Key | `config/`, `retrievers/` |
| LLM 调用失败 | 检查 Provider 配置和 API Key | `llm_provider/` |
| 报告质量差 | 检查 Prompts 和 LLM 选择 | `prompts.py`, `config/` |
| 抓取超时 | 调整 Worker 数和限速 | `scraper/`, Config |
| 内存溢出 | 调整并发和上下文窗口 | `context/`, Config |
| WebSocket 断开 | 检查后端服务状态 | `backend/server/` |

### 关键环境变量清单

```bash
# 必须配置
OPENAI_API_KEY=xxx          # 或其他LLM Provider的Key
TAVILY_API_KEY=xxx          # 默认搜索引擎

# 常用可选
FAST_LLM=openai:gpt-4o-mini
SMART_LLM=openai:gpt-4.1
RETRIEVER=tavily
SCRAPER=bs
REPORT_TYPE=research_report

# 调试
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=xxx
```
