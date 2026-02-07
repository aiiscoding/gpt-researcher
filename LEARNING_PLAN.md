# GPT-Researcher 学习计划（AI 编程时代版）

> **核心理念：你负责"知道在哪、为什么、要什么"，AI 负责"怎么写"**
> 基于 v0.14.6 源码 | 目标：用 AI 高效运维和二次开发

---

## 学习思路说明

传统学习：逐行读源码 → 理解实现 → 自己写代码
AI 时代学习：**理解架构地图 → 掌握业务语义 → 学会向 AI 精准提需求 → 会验证 AI 的输出**

你不需要记住每个函数的实现细节，但你需要：
1. **知道系统有哪些模块、每个模块干什么**（这样你才知道改哪里）
2. **理解数据怎么流转的**（这样你才能描述清楚需求）
3. **掌握配置和扩展点**（这样你才能用最小代价实现变更）
4. **会读错误日志、定位问题范围**（这样你才能给 AI 精准的上下文）
5. **会验证改动是否正确**（这样你才能判断 AI 的输出质量）

---

## 阶段一：架构地图（大脑中的 GPS）

> 目标：闭上眼能画出系统全貌，任何需求都能 3 秒定位到相关模块

### 1.1 一句话理解项目

- [ ] GPT-Researcher = **用户提问 → AI 自动搜索多个来源 → 抓取内容 → 分析整合 → 生成研究报告**
- [ ] 本质是一个 **LLM 编排系统**，核心价值是串联"搜索-抓取-分析-写作"这条链路

### 1.2 四个入口，一个核心

```
用户怎么触发研究？
├── cli.py              → 命令行直接跑
├── main.py             → 启动 Web 服务（FastAPI）
├── Python API          → from gpt_researcher import GPTResearcher
└── multi_agents/main.py → 多 Agent 模式

所有入口最终都调用 → GPTResearcher 类（gpt_researcher/agent.py）
```

- [ ] 掌握这四个入口的启动方式和适用场景
- [ ] 理解：**agent.py 是唯一需要你建立全局理解的文件**，其他都是它调用的子模块

### 1.3 数据流（最重要的心智模型）

```
用户查询
  │
  ▼
┌─────────────────┐
│ 查询规划         │  LLM 把一个大问题拆成多个子查询
│ query_processing │
└────────┬────────┘
         │  生成 N 个子查询
         ▼
┌─────────────────┐
│ 搜索执行         │  14种搜索引擎任选，每个子查询独立搜索
│ retrievers/      │
└────────┬────────┘
         │  返回 URL 列表
         ▼
┌─────────────────┐
│ 内容抓取         │  并发抓取网页/PDF/论文内容
│ scraper/         │
└────────┬────────┘
         │  返回原始文本
         ▼
┌─────────────────┐
│ 上下文压缩       │  用向量嵌入 + LLM 筛选相关内容
│ context/         │
└────────┬────────┘
         │  精炼后的上下文
         ▼
┌─────────────────┐
│ 报告生成         │  LLM 根据上下文写报告
│ skills/writer    │
└────────┬────────┘
         │
         ▼
    最终报告（Markdown/PDF/DOCX）
```

- [ ] **能用自己的话复述这个流程** — 这是你向 AI 描述需求的基础
- [ ] 理解每个阶段的输入和输出是什么

### 1.4 模块功能速查表

> 当你想改某个功能时，3 秒定位到目录

| 我想改... | 去找... | 路径 |
|-----------|---------|------|
| 研究的主流程/编排逻辑 | GPTResearcher 类 | `gpt_researcher/agent.py` |
| 默认配置/参数 | DEFAULT_CONFIG | `gpt_researcher/config/variables/default.py` |
| 搜索用什么引擎 | Retrievers | `gpt_researcher/retrievers/` |
| 网页怎么抓取解析 | Scrapers | `gpt_researcher/scraper/` |
| 报告怎么写的/写作风格 | Prompts | `gpt_researcher/prompts.py` |
| 用哪个 LLM/怎么调用 | LLM Provider | `gpt_researcher/llm_provider/` |
| 上下文怎么筛选压缩 | Context | `gpt_researcher/context/` |
| 向量嵌入/语义搜索 | Memory | `gpt_researcher/memory/` |
| 深度研究模式 | DeepResearch | `gpt_researcher/skills/deep_research.py` |
| MCP 工具扩展 | MCP | `gpt_researcher/mcp/` |
| 多 Agent 协作模式 | Multi-Agents | `multi_agents/` |
| Web API 接口 | Backend | `backend/server/` |
| 前端 UI | Frontend | `frontend/nextjs/` |
| 部署配置 | Docker/Terraform | 根目录 `Dockerfile`, `terraform/` |

- [ ] **打印或收藏这张表** — 这是你与 AI 协作时最常用的"导航"

---

## 阶段二：配置即控制（不写代码就能改行为）

> 目标：80% 的需求变更可以通过改配置解决，不需要碰代码

### 2.1 配置系统原理

- [ ] 配置优先级：**环境变量 > JSON 配置文件 > 代码默认值**
- [ ] 配置文件位置：`.env`（主要）、`gpt_researcher/config/variables/default.py`（默认值参考）

### 2.2 必须熟记的配置项

**不需要记值，记住"有这个开关"就行，具体改的时候让 AI 帮你：**

| 类别 | 配置项 | 你要知道的 |
|------|--------|-----------|
| **LLM 选择** | `FAST_LLM` / `SMART_LLM` / `STRATEGIC_LLM` | 三级模型策略，不同任务用不同模型控制成本和质量 |
| **搜索引擎** | `RETRIEVER` | 切换搜索来源（tavily/duckduckgo/google/bing 等 14 种） |
| **抓取方式** | `SCRAPER` | 换抓取器（bs=静态页面 / browser=动态页面 / pymupdf=PDF） |
| **报告类型** | `REPORT_TYPE` | 7 种报告类型，决定输出格式和深度 |
| **字数控制** | `TOTAL_WORDS` | 报告长度 |
| **搜索结果数** | `MAX_SEARCH_RESULTS_PER_QUERY` | 每个子查询取多少条结果 |
| **并发数** | `MAX_SCRAPER_WORKERS` | 同时抓取多少网页 |
| **深度研究** | `DEEP_RESEARCH_BREADTH` / `DEPTH` / `CONCURRENCY` | 控制深度研究的广度、深度和并发 |
| **温度** | `TEMPERATURE` | LLM 创造性程度 |
| **嵌入模型** | `EMBEDDING` | 向量嵌入模型选择 |
| **提示词族** | `PROMPT_FAMILY` | 切换整套提示词风格 |

- [ ] 实操练习：**只改 `.env`，分别用不同的 LLM、不同的搜索引擎、不同的报告类型跑一遍**
- [ ] 理解：大部分"我想让报告更长/更短/换个模型/换个搜索引擎"的需求 → 改配置就行

### 2.3 AI 协作话术示例

> 当你需要改配置时，这样跟 AI 说：

```
"帮我把搜索引擎从 tavily 换成 duckduckgo，我不想付 API 费用"
"我想让深度研究更深入一些，帮我调整 DEEP_RESEARCH_DEPTH 和 BREADTH"
"帮我看看 .env 里哪些配置可以优化 LLM 调用成本"
```

---

## 阶段三：扩展点地图（知道在哪里插入新能力）

> 目标：知道系统的"插槽"在哪里，需要扩展时能精准告诉 AI 该怎么加

### 3.1 六大扩展点

| 扩展点 | 场景 | 怎么扩展 | 你要知道的 |
|--------|------|---------|-----------|
| **新搜索引擎** | 想接入企业内部搜索 | 在 `retrievers/` 下新建目录，继承 `CustomRetriever` | 接口只有一个 `search()` 方法 |
| **新抓取器** | 需要抓取特殊格式 | 在 `scraper/` 下新建目录 | 输入 URL，输出纯文本 |
| **新 LLM** | 换模型供应商 | 改 `provider:model` 配置 | 大部分 LangChain 支持的都能直接用 |
| **新提示词** | 想改研究/写作风格 | 自定义 `PROMPT_FAMILY` | 提示词在 `prompts.py` |
| **新报告类型** | 需要特殊输出格式 | 在 `backend/report_type/` 扩展 | 每种类型一个 Agent |
| **MCP 工具** | 接入外部数据源/工具 | 配置 MCP Server | 最灵活的扩展方式 |

- [ ] 理解每个扩展点的"输入→输出契约"（接口长什么样）
- [ ] 不需要记住实现细节，但要知道**扩展点在哪个目录、接口叫什么名字**

### 3.2 AI 协作话术示例

```
"帮我新建一个 Retriever，接入我们公司的 Elasticsearch，
参考 gpt_researcher/retrievers/tavily/ 的结构"

"帮我写一个 MCP Server，把我们的内部知识库暴露给 GPT-Researcher 使用"

"我想加一种新的报告类型叫 brief_report，只输出要点摘要，
参考 backend/report_type/ 下现有的实现"
```

---

## 阶段四：数据流与接口边界（精准描述需求的基础）

> 目标：理解模块间如何通信，这样你才能精准告诉 AI "从 A 到 B 中间要加个 C"

### 4.1 核心接口契约

**你不需要看实现代码，只需要知道每个模块的"输入→输出"：**

| 模块 | 输入 | 输出 |
|------|------|------|
| **QueryProcessing** | 用户原始查询（字符串） | 子查询列表 + 研究大纲 |
| **Retriever** | 查询字符串 + max_results | `List[Dict]`（URL + 标题 + 摘要） |
| **Scraper** | URL 列表 | 纯文本内容列表 |
| **ContextCompressor** | 大量原始文本 + 查询 | 精炼后的相关上下文 |
| **ReportGenerator** | 上下文 + 查询 + 报告类型 | Markdown 格式报告 |
| **Memory/Embedding** | 文本 | 向量 → 相似度匹配 |

- [ ] 理解这些接口，你就能对 AI 说"我想在 Scraper 输出之后、ContextCompressor 之前加一个过滤步骤"

### 4.2 三级 LLM 策略（成本控制的关键）

```
FAST_LLM    → 子查询生成、简单判断     → 便宜、快
SMART_LLM   → 报告撰写、内容分析       → 中等
STRATEGIC_LLM → 复杂推理、研究规划      → 贵、强
```

- [ ] 理解哪些步骤用哪个级别的 LLM（直接影响成本和质量）
- [ ] 知道可以通过调整这三个配置来平衡成本和质量

---

## 阶段五：故障定位能力（运维的核心技能）

> 目标：出问题时能快速缩小范围，给 AI 精准的错误上下文

### 5.1 故障定位决策树

```
报告生成失败
├── 搜索阶段失败？
│   ├── API Key 问题 → 检查 .env 中对应的 KEY
│   ├── 网络问题 → 检查代理/防火墙
│   └── Retriever 不支持 → 检查 RETRIEVER 配置
│
├── 抓取阶段失败？
│   ├── 网站反爬 → 换 SCRAPER=browser 或 firecrawl
│   ├── 超时 → 调大 timeout 或减少 MAX_SCRAPER_WORKERS
│   └── 内容为空 → 检查 URL 可达性
│
├── LLM 调用失败？
│   ├── API Key/额度 → 检查 Provider 配置
│   ├── Token 超限 → 减少上下文或换更大窗口的模型
│   └── 模型不存在 → 检查 provider:model 格式
│
└── 报告质量差？
    ├── 搜索结果不相关 → 调整 RETRIEVER 或加 query_domains
    ├── 上下文被过度压缩 → 调整 SIMILARITY_THRESHOLD
    └── 写作风格不对 → 调整 TONE 或 PROMPT_FAMILY
```

- [ ] **收藏这棵决策树** — 出问题时按图索骥，缩小范围后再让 AI 帮你修

### 5.2 日志与调试

- [ ] 掌握日志查看方式（Loguru 输出在控制台）
- [ ] 了解 LangSmith 追踪：
  ```bash
  LANGCHAIN_TRACING_V2=true
  LANGCHAIN_API_KEY=xxx
  ```
  开启后可以在 LangSmith 网页上看到每一步 LLM 调用的详情
- [ ] 理解：出问题时最有效的方式是 **复制错误日志 + 指出你认为的故障阶段 → 发给 AI**

### 5.3 AI 协作话术示例

```
"报告生成的时候在抓取阶段卡住了，这是错误日志：[粘贴日志]，
帮我看看是什么原因，相关代码在 gpt_researcher/scraper/"

"LLM 调用返回 429 错误，帮我看看 gpt_researcher/llm_provider/ 里
有没有重试机制，如果没有帮我加上"
```

---

## 阶段六：多 Agent 模式（理解即可）

> 目标：知道多 Agent 是什么、什么时候用、怎么定制

### 6.1 概念理解

```
单 Agent 模式（默认）：
  GPTResearcher 一个人干所有事

多 Agent 模式（LangGraph）：
  ChiefEditor 指挥一组专业 Agent 协作
  ├── ResearchAgent  → 负责搜索和调研
  ├── WriterAgent    → 负责写作
  ├── EditorAgent    → 负责规划和编辑
  ├── ReviewerAgent  → 负责质量审查
  ├── ReviserAgent   → 负责修订
  ├── PublisherAgent  → 负责发布
  └── HumanAgent     → 人工审批节点
```

- [ ] 理解单 Agent vs 多 Agent 的区别和适用场景
- [ ] 理解 LangGraph 的核心概念：**StateGraph = 状态 + 节点 + 边**
- [ ] 知道多 Agent 模式的状态容器 `ResearchState` 包含什么字段
- [ ] 了解 Human-in-the-Loop：可以在流程中插入人工审批节点

### 6.2 你需要知道的程度

**不需要会写 LangGraph 代码**，但要能对 AI 说：
```
"帮我在多 Agent 流程中，Writer 和 Publisher 之间加一个翻译 Agent，
把报告翻译成中文，参考 multi_agents/agents/ 下现有 Agent 的写法"
```

---

## 阶段七：前端与部署（运维层面）

### 7.1 部署方式选择

| 方式 | 适用场景 | 命令 |
|------|---------|------|
| CLI 直接跑 | 本地测试、脚本调用 | `python cli.py "查询"` |
| FastAPI 服务 | Web 服务、API 调用 | `python main.py` |
| Docker | 标准化部署 | `docker compose up` |
| Terraform | 云端生产环境 | `terraform apply` |

- [ ] 掌握 Docker 部署的基本流程
- [ ] 理解 `.env` 文件在 Docker 中如何注入
- [ ] 了解前端 Next.js 通过 WebSocket 与后端通信

### 7.2 AI 协作话术示例

```
"帮我配置 docker-compose.yml，让 GPT-Researcher 跑在 8080 端口，
使用 Ollama 本地模型代替 OpenAI"

"帮我写一个健康检查接口，加到 backend/server/app.py 里"
```

---

## 阶段八：AI 协作效率提升（元技能）

> 这是 AI 编程时代最关键的能力：**如何与 AI 高效协作**

### 8.1 向 AI 描述需求的模板

```markdown
## 需求
[一句话说清楚要做什么]

## 上下文
- 项目：GPT-Researcher
- 相关模块：[从阶段一的模块速查表定位]
- 相关文件：[具体文件路径]

## 约束
- [不要改动哪些文件]
- [要兼容哪些现有功能]
- [性能/成本要求]

## 参考
- 参考现有的 [xxx] 实现方式
```

- [ ] 练习使用这个模板向 AI（Claude Code 等）提需求

### 8.2 验证 AI 输出的检查清单

AI 写完代码后，你需要检查：

- [ ] **功能正确性**：改动是否解决了你的需求？
- [ ] **影响范围**：改了哪些文件？有没有意外修改其他模块？
- [ ] **配置兼容**：新代码是否遵循了 Config 系统的约定？
- [ ] **接口一致**：新模块的输入输出是否与上下游模块兼容？
- [ ] **错误处理**：边界情况和异常是否有处理？
- [ ] **可回滚**：如果出问题，能否快速回退？（git 习惯）

### 8.3 高效 Prompt 技巧

| 场景 | 低效 Prompt | 高效 Prompt |
|------|------------|------------|
| 加功能 | "帮我加个搜索引擎" | "帮我在 `gpt_researcher/retrievers/` 下新建一个 `my_search/` 目录，实现 CustomRetriever 接口，接入 xxx API" |
| 改 Bug | "报告生成有问题" | "报告生成时 `report_generation.py:L120` 附近的引用格式不对，应该是 APA 格式但输出的是 MLA" |
| 理解代码 | "解释一下这个项目" | "解释 `agent.py` 中 `conduct_research()` 方法的执行流程，重点说明 Retriever 是如何被调度的" |
| 运维排障 | "跑不起来了" | "启动 `main.py` 时报错 [错误信息]，我的 `.env` 配置是 [配置]，帮我排查" |

- [ ] 练习用精准的 Prompt 而不是模糊的描述

---

## 阶段九：Git 与上游同步（持续维护）

> 你 fork 了项目并做了大量自定义，必须掌握与上游同步的能力

### 9.1 Fork 维护策略

- [ ] 理解 Git 分支策略：
  ```
  upstream/master  ← 原始仓库（定期拉取更新）
  origin/master    ← 你的 fork（合并上游 + 自定义）
  feature/*        ← 你的功能分支
  ```
- [ ] 掌握同步上游的操作：
  ```bash
  git remote add upstream <原始仓库URL>
  git fetch upstream
  git merge upstream/master
  # 解决冲突
  ```
- [ ] 理解冲突集中在哪些文件（你改动多的文件 = 冲突高发区）

### 9.2 AI 协作话术

```
"帮我把上游最新的更新合并到我的 fork，
我主要修改了 [列出你改过的文件]，帮我解决冲突"

"帮我看看上游最近的 commit，有哪些变更会影响我的自定义功能"
```

---

## 学习优先级总览

| 优先级 | 阶段 | 内容 | 学习方式 | 预期效果 |
|--------|------|------|---------|---------|
| P0 | 阶段一 | 架构地图 | 看目录 + 画图 | 任何需求 3 秒定位模块 |
| P0 | 阶段二 | 配置即控制 | 动手改 .env 跑实验 | 80% 需求不碰代码 |
| P0 | 阶段五 | 故障定位 | 收藏决策树 + 实际排障 | 出问题能快速定位 |
| P1 | 阶段三 | 扩展点地图 | 看接口不看实现 | 知道从哪里扩展 |
| P1 | 阶段四 | 数据流与接口 | 理解输入输出 | 能精准描述需求 |
| P1 | 阶段八 | AI 协作技能 | 反复练习 Prompt | 与 AI 协作效率翻倍 |
| P2 | 阶段六 | 多 Agent 模式 | 概念理解即可 | 知道什么时候用 |
| P2 | 阶段七 | 部署运维 | 按需查阅 | 能独立部署维护 |
| P2 | 阶段九 | Git 与上游同步 | 建立流程 | 持续维护能力 |

---

## 快速参考卡片

### 关键环境变量

```bash
# === 必须 ===
OPENAI_API_KEY=xxx
TAVILY_API_KEY=xxx

# === LLM 选择（成本控制核心）===
FAST_LLM=openai:gpt-4o-mini          # 快速任务，便宜
SMART_LLM=openai:gpt-4.1             # 报告写作，中等
STRATEGIC_LLM=openai:o4-mini          # 复杂推理，按需

# === 搜索与抓取 ===
RETRIEVER=tavily                      # 搜索引擎
SCRAPER=bs                            # 抓取方式
MAX_SEARCH_RESULTS_PER_QUERY=5        # 结果数量
MAX_SCRAPER_WORKERS=15                # 并发数

# === 报告 ===
REPORT_TYPE=research_report           # 报告类型
TOTAL_WORDS=1200                      # 字数
TEMPERATURE=0.4                       # 创造性

# === 调试 ===
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=xxx
```

### 目录定位速记

```
要改搜索？     → gpt_researcher/retrievers/
要改抓取？     → gpt_researcher/scraper/
要改提示词？   → gpt_researcher/prompts.py
要改配置？     → .env 或 gpt_researcher/config/
要改 LLM？    → gpt_researcher/llm_provider/
要改 API？    → backend/server/
要改流程？     → gpt_researcher/agent.py
要加 Agent？  → multi_agents/agents/
要加 MCP？    → gpt_researcher/mcp/
```

### 七种报告类型

| 类型 | 用途 | 何时选 |
|------|------|--------|
| `research_report` | 标准综合报告 | 默认选这个 |
| `detailed_report` | 深度分析 | 需要详尽分析时 |
| `deep` | 多轮深度研究 | 复杂课题深挖时 |
| `outline_report` | 结构大纲 | 快速了解框架时 |
| `resource_report` | 资源清单 | 收集参考资料时 |
| `subtopic_report` | 子主题聚焦 | 专注某个细分方向时 |
| `custom_report` | 用户自定义 | 有特殊格式要求时 |

### 14 种搜索引擎

| 免费 | 付费 |
|------|------|
| duckduckgo, arxiv, semantic_scholar, pubmed_central | tavily(默认), google, serpapi, serper, bing, exa, searchapi |
| searx(需自建) | custom(自定义), mcp(协议扩展) |
