# Railway 一键部署指南（最简单的方式）

> Railway 是一个 PaaS 平台，不需要你管理服务器，点几下就能部署。
> 自带 HTTPS、自动重启、日志查看，非常适合个人或小团队使用。

---

## 费用说明

- **免费试用**：注册送 $5 额度（大约够用一周体验）
- **Hobby Plan**：$5/月起步，按实际用量计费
- **预估费用**：正常使用约 $10-20/月（取决于研究频率）
- 支持信用卡付款

---

## 部署步骤（10 分钟搞定）

### 第一步：准备工作

确保你有：
- GitHub 账号
- OpenAI API Key（https://platform.openai.com/api-keys）
- Tavily API Key（https://tavily.com 免费注册）

### 第二步：Fork 仓库到你的 GitHub

1. 打开项目地址：https://github.com/aiiscoding/gpt-researcher
2. 点击右上角 **Fork** 按钮
3. 确认 Fork 到你自己的 GitHub 账号下

### 第三步：在 Railway 创建项目

1. 打开 https://railway.app/ 并用 GitHub 账号登录
2. 点击 **New Project**
3. 选择 **Deploy from GitHub repo**
4. 找到并选择你刚 Fork 的 `gpt-researcher` 仓库
5. Railway 会自动检测到 `railway.toml` 和 `Dockerfile.fullstack`

### 第四步：配置环境变量

在 Railway 项目页面，点击你的服务 → **Variables** 标签，添加以下变量：

**必填项（点击 + New Variable 逐个添加）：**

| 变量名 | 值 | 说明 |
|--------|-----|------|
| `OPENAI_API_KEY` | 你的 key | OpenAI API 密钥 |
| `TAVILY_API_KEY` | 你的 key | Tavily 搜索 API 密钥 |
| `AUTH_ENABLED` | `true` | 开启登录认证 |
| `AUTH_SECRET_KEY` | 随机字符串 | 见下方生成方法 |
| `AUTH_USERS` | `admin:你的密码` | 登录账号，多个用逗号隔开 |

**可选项：**

| 变量名 | 值 | 说明 |
|--------|-----|------|
| `OPENAI_BASE_URL` | 自定义地址 | 使用兼容 API 时填写 |
| `AUTH_COOKIE_SECURE` | `true` | Railway 自带 HTTPS，建议开启 |
| `AUTH_TOKEN_EXPIRE_HOURS` | `72` | Token 过期时间（默认 24 小时） |

**生成随机 AUTH_SECRET_KEY：**

在你电脑的终端运行：

```bash
# Mac / Linux
openssl rand -hex 32

# Windows PowerShell
-join ((1..64) | ForEach-Object { '{0:x}' -f (Get-Random -Max 16) })
```

把生成的随机字符串填入 `AUTH_SECRET_KEY`。

**多用户配置示例：**

```
AUTH_USERS=张三:password123,李四:mypass456,admin:admin888
```

### 第五步：等待部署完成

- Railway 会自动开始构建，首次大约需要 **10-15 分钟**
- 在 **Deployments** 标签可以看到构建进度和日志
- 构建成功后会显示绿色的 **Active**

### 第六步：访问你的应用

1. 在项目页面点击 **Settings** 标签
2. 找到 **Networking** → **Public Networking**
3. 点击 **Generate Domain**（生成一个免费的 `.railway.app` 域名）
4. 打开生成的 URL，你会看到登录页面
5. 输入你在 `AUTH_USERS` 中设置的账号密码，登录使用

---

## 绑定自定义域名（可选）

如果你有自己的域名：

1. 在 Railway 项目 → Settings → Networking → Custom Domain
2. 输入你的域名（例如 `research.example.com`）
3. 按提示在你的域名 DNS 管理处添加 CNAME 记录
4. Railway 会自动配置 HTTPS 证书

---

## 日常管理

### 查看日志

在 Railway 项目页面 → **Deployments** → 点击最新的部署 → 可以看到实时日志。

### 重新部署

两种方式：
- **自动**：推送代码到 GitHub，Railway 自动重新部署
- **手动**：在 Deployments 页面点击 **Redeploy**

### 修改环境变量

在 **Variables** 标签直接修改，保存后 Railway 会自动重启服务。

### 暂停/关闭

在 **Settings** 标签可以暂停或删除服务（暂停不计费）。

---

## 数据说明

Railway 容器重启后本地文件会丢失。如果你需要持久化数据：

### 方案 1：添加 Railway Volume（推荐）

1. 在项目页面点击服务
2. 点击 **+ New** → **Volume**
3. Mount Path 填 `/usr/src/app/data`
4. 这样数据库文件就会持久保存

你还可以为报告输出添加第二个 Volume：
- Mount Path: `/usr/src/app/outputs`

### 方案 2：定期导出数据

通过 Railway CLI 连接到容器，手动备份：

```bash
# 安装 Railway CLI
npm install -g @railway/cli

# 登录
railway login

# 连接到项目
railway link

# 下载数据库文件
railway run cat /usr/src/app/data/reports.db > backup.db
```

---

## 常见问题

### Q: 构建失败怎么办？

查看 Deployments 中的日志，常见原因：
- 内存不足：升级到 Hobby Plan 或更高
- 网络超时：点击 Redeploy 重试

### Q: 费用怎么算？

Railway 按 CPU 和内存使用时间计费：
- 空闲时几乎不花钱
- 做一次研究大约消耗 $0.01-0.05 的计算资源
- 主要费用其实是 OpenAI API 调用费

### Q: 和自建服务器比哪个好？

| | Railway | 自建服务器 |
|---|---|---|
| 上手难度 | 非常简单 | 需要一些 Linux 知识 |
| 费用 | $10-20/月 | $20-24/月 |
| HTTPS | 自动配置 | 需要手动配置 |
| 维护 | 零维护 | 需要自己更新/备份 |
| 数据控制 | 在 Railway 上 | 完全在你手里 |
| 适合 | 个人/小团队 | 对数据安全要求高的场景 |

### Q: Vercel 能部署吗？

Vercel 只能部署前端（Next.js），后端（FastAPI）需要单独部署。架构会变复杂，**不推荐**。如果一定要用 Vercel：
- 前端部署到 Vercel
- 后端部署到 Railway
- 需要配置 `NEXT_PUBLIC_GPTR_API_URL` 指向 Railway 后端地址
- 需要额外处理跨域问题

**直接用 Railway 全栈部署是最省事的方案。**
