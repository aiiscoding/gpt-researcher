# GPT Researcher 云端部署指南（小白版）

> 本教程手把手教你把 GPT Researcher 部署到云服务器上，让你随时随地通过浏览器使用。

---

## 目录

1. [你需要准备什么](#1-你需要准备什么)
2. [购买云服务器](#2-购买云服务器)
3. [连接到服务器](#3-连接到服务器)
4. [一键部署](#4-一键部署)
5. [访问你的应用](#5-访问你的应用)
6. [日常维护](#6-日常维护)
7. [配置 HTTPS（可选）](#7-配置-https可选)
8. [数据安全](#8-数据安全)
9. [常见问题](#9-常见问题)

---

## 1. 你需要准备什么

在开始之前，你需要：

| 项目 | 说明 | 在哪里获取 |
|------|------|-----------|
| OpenAI API Key | 用于 AI 研究能力 | https://platform.openai.com/api-keys |
| Tavily API Key | 用于网络搜索 | https://tavily.com （免费注册） |
| 云服务器 | 运行应用的机器 | 见下一节 |
| SSH 客户端 | 连接服务器的工具 | Windows 用 PowerShell，Mac/Linux 用终端 |

---

## 2. 购买云服务器

### 推荐配置

| 配置项 | 最低要求 | 推荐配置 |
|--------|---------|---------|
| CPU | 2 核 | 4 核 |
| 内存 | 4 GB | 8 GB |
| 硬盘 | 40 GB | 60 GB |
| 系统 | Ubuntu 22.04 / 24.04 | Ubuntu 24.04 |
| 带宽 | 5 Mbps | 10 Mbps |

### 各云平台推荐（按易用度排序）

#### 方案 A：国内服务器（适合在国内使用）

**阿里云 ECS：**
1. 打开 https://ecs.console.aliyun.com/
2. 点击「创建实例」
3. 选择：
   - 地域：离你最近的城市
   - 实例规格：ecs.c7.xlarge（4核8G）或更小
   - 镜像：Ubuntu 22.04 64位
   - 系统盘：ESSD 60GB
   - 带宽：按量付费 10Mbps
4. 设置登录密码（记住它！）
5. **安全组**：开放 3000 端口（重要！见下方说明）
6. 确认订单并购买

**腾讯云 CVM：**
1. 打开 https://console.cloud.tencent.com/cvm
2. 步骤类似阿里云

> **国内服务器注意**：如果使用 OpenAI 官方 API，需要配置代理地址（OPENAI_BASE_URL），
> 或使用兼容 OpenAI 接口的国内大模型（如通义千问、DeepSeek 等）。

#### 方案 B：海外服务器（推荐！直接用 OpenAI/Tavily，无需代理）

> **为什么推荐海外服务器？**
> - Tavily 搜索 API 在国内无法直接访问
> - OpenAI API 在国内也需要代理
> - 海外服务器省去所有网络问题，开箱即用

**推荐 1：DigitalOcean（最适合新手）**
1. 打开 https://www.digitalocean.com/ 注册账号
2. 点击 Create → Droplets
3. 配置选择：
   - **地区**：Singapore（新加坡）— 国内连接延迟最低
   - **镜像**：Ubuntu 24.04 LTS
   - **规格**：Basic → Regular，$24/月（4GB 内存）即可
   - **认证**：选 Password，设置 root 密码
4. 点击 Create Droplet
5. 等待创建完成，记下显示的 IP 地址
6. 支持支付宝付款

**推荐 2：Vultr（性价比高）**
1. 打开 https://www.vultr.com/ 注册
2. 点击 Deploy New Server
3. 配置：
   - **类型**：Cloud Compute - Shared CPU
   - **地区**：Tokyo（东京）或 Singapore（新加坡）
   - **镜像**：Ubuntu 24.04
   - **规格**：$24/月（4GB 内存）
4. 支持支付宝/微信付款

**推荐 3：AWS Lightsail（稳定可靠）**
1. 打开 https://lightsail.aws.amazon.com/
2. 创建实例 → Linux → Ubuntu 24.04
3. 选择 $20/月（4GB 内存）套餐
4. 地区选 ap-southeast-1（新加坡）

**价格对比：**

| 平台 | 4GB 内存方案 | 月费 | 支付宝 | 推荐地区 |
|------|-------------|------|--------|---------|
| DigitalOcean | Basic Regular | $24 | 支持 | 新加坡 |
| Vultr | Cloud Compute | $24 | 支持 | 东京/新加坡 |
| AWS Lightsail | 4GB | $20 | 支持 | 新加坡 |
| Linode | Shared 4GB | $24 | 不支持 | 东京 |

### 开放端口（所有平台都需要！）

部署后需要通过 3000 端口访问，务必在云平台的**安全组/防火墙**中开放：

| 端口 | 协议 | 用途 |
|------|------|------|
| 22 | TCP | SSH 远程登录 |
| 3000 | TCP | GPT Researcher 应用 |
| 443 | TCP | HTTPS（可选） |

**阿里云开放端口方法：**
1. 进入 ECS 控制台 → 安全组
2. 点击「配置规则」→「添加安全组规则」
3. 方向：入方向，协议：TCP，端口：3000，授权对象：0.0.0.0/0

---

## 3. 连接到服务器

### Windows 用户

打开 PowerShell（按 Win+X 选择「Windows PowerShell」），输入：

```bash
ssh root@你的服务器IP地址
```

输入你购买时设置的密码，回车即可连接。

### Mac / Linux 用户

打开终端，输入：

```bash
ssh root@你的服务器IP地址
```

> 首次连接会提示 "Are you sure you want to continue connecting?"，输入 `yes` 回车。

---

## 4. 一键部署

连接到服务器后，按顺序运行以下命令：

### 第一步：下载项目代码

```bash
# 安装 git（如果服务器没有的话）
apt update && apt install -y git

# 下载代码
git clone https://github.com/aiiscoding/gpt-researcher.git
cd gpt-researcher

# 切换到包含登录功能的分支
git checkout claude/cloud-deploy-login-qpHry
```

### 第二步：运行一键部署脚本

```bash
bash deploy/setup.sh
```

脚本会自动：
1. 安装 Docker
2. 提示你输入 API 密钥
3. 提示你设置登录账号和密码
4. 构建并启动应用

**首次构建需要 10-20 分钟**，请耐心等待。

### 部署成功后你会看到：

```
==========================================
  部署成功！
==========================================

  访问地址: http://你的IP:3000

  登录账号信息已保存在 .env 文件中
```

---

## 5. 访问你的应用

1. 打开浏览器
2. 输入 `http://你的服务器IP:3000`
3. 看到登录页面 → 输入你在部署时设置的用户名和密码
4. 登录成功后就可以开始使用了！

---

## 6. 日常维护

### 查看应用日志

```bash
cd /root/gpt-researcher
docker compose -f docker-compose.cloud.yml logs -f
```

按 `Ctrl+C` 退出日志查看。

### 重启应用

```bash
cd /root/gpt-researcher
docker compose -f docker-compose.cloud.yml restart
```

### 停止应用

```bash
cd /root/gpt-researcher
docker compose -f docker-compose.cloud.yml down
```

### 更新到最新版本

```bash
cd /root/gpt-researcher
git pull
docker compose -f docker-compose.cloud.yml up -d --build
```

### 修改登录密码

编辑 .env 文件：

```bash
nano .env
```

找到 `AUTH_USERS=` 这一行，修改密码：

```
AUTH_USERS=admin:新密码
```

如果要添加多个用户：

```
AUTH_USERS=admin:密码1,张三:密码2,李四:密码3
```

保存（Ctrl+O 回车），退出（Ctrl+X），然后重启：

```bash
docker compose -f docker-compose.cloud.yml restart
```

---

## 7. 配置 HTTPS（可选）

如果你有域名，建议配置 HTTPS 加密访问。最简单的方式是使用 Caddy 反向代理：

```bash
# 安装 Caddy
apt install -y debian-keyring debian-archive-keyring apt-transport-https curl
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | tee /etc/apt/sources.list.d/caddy-stable.list
apt update && apt install -y caddy

# 配置反向代理（把 your-domain.com 换成你的域名）
cat > /etc/caddy/Caddyfile << 'EOF'
your-domain.com {
    reverse_proxy localhost:3000
}
EOF

# 启动 Caddy（会自动申请 HTTPS 证书）
systemctl restart caddy
```

配置好后，更新 .env 中的：

```
AUTH_COOKIE_SECURE=true
```

然后重启应用。之后就可以通过 `https://your-domain.com` 安全访问了。

---

## 8. 数据安全

### 数据如何存储？

系统使用 **SQLite 数据库** 存储聊天记录和研究报告（文件：`data/reports.db`）：
- **WAL 模式**：即使服务器突然断电，数据也不会损坏
- **ACID 事务**：每次写入都是原子操作，不会出现半截数据
- **文件锁**：多个请求同时访问也不会冲突

### 定时备份

**手动备份：**

```bash
cd /root/gpt-researcher
bash deploy/backup.sh
```

备份文件保存在 `backups/` 目录，包含数据库和研究报告。

**设置自动备份（每天凌晨 3 点）：**

```bash
crontab -e
```

添加这一行：

```
0 3 * * * cd /root/gpt-researcher && bash deploy/backup.sh
```

### 下载备份到本地

```bash
# 在你自己的电脑上运行（不是服务器上）
scp root@你的服务器IP:/root/gpt-researcher/backups/最新的备份文件.tar.gz ./
```

### 安全建议清单

| 建议 | 重要性 | 说明 |
|------|--------|------|
| 配置 HTTPS | 必须 | 加密传输，防止密码被窃听 |
| 修改默认密码 | 必须 | 不要用默认的 admin:admin123 |
| 修改 AUTH_SECRET_KEY | 必须 | 部署脚本会自动生成随机密钥 |
| 定时备份 | 强烈建议 | 防止数据丢失 |
| 限制 SSH 登录 | 建议 | 使用 SSH 密钥登录，禁用密码登录 |
| 配置防火墙 | 建议 | 只开放必要端口（22、443） |

### 加固 SSH 安全（可选）

```bash
# 生成 SSH 密钥（在你自己电脑上执行）
ssh-keygen -t ed25519

# 复制公钥到服务器
ssh-copy-id root@你的服务器IP

# 测试密钥登录成功后，禁用密码登录
# 编辑服务器上的 /etc/ssh/sshd_config：
#   PasswordAuthentication no
# 然后重启 SSH：systemctl restart sshd
```

---

## 9. 常见问题

### Q: 构建失败，提示网络超时怎么办？

国内服务器可能无法访问某些国外资源，解决方法：

```bash
# 重新构建，Docker 会从断点继续
docker compose -f docker-compose.cloud.yml up -d --build
```

如果多次失败，考虑使用海外服务器或配置 Docker 镜像加速。

### Q: 访问 http://IP:3000 打不开？

1. 检查安全组/防火墙是否开放了 3000 端口
2. 检查服务是否在运行：
   ```bash
   docker compose -f docker-compose.cloud.yml ps
   ```
3. 查看日志找错误原因：
   ```bash
   docker compose -f docker-compose.cloud.yml logs
   ```

### Q: 忘记密码了怎么办？

```bash
# 查看当前配置的账号密码
cat .env | grep AUTH_USERS
```

### Q: 如何使用国内大模型（如通义千问、DeepSeek）？

在 .env 中设置：

```bash
# DeepSeek 示例
OPENAI_API_KEY=你的DeepSeek API Key
OPENAI_BASE_URL=https://api.deepseek.com/v1

# 通义千问示例
OPENAI_API_KEY=你的通义千问 API Key
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
```

然后重启应用。

### Q: 数据保存在哪里？

| 目录 | 内容 |
|------|------|
| `outputs/` | 生成的研究报告（PDF、Word） |
| `data/` | 报告元数据 |
| `my-docs/` | 你上传的本地文档 |
| `logs/` | 应用日志 |

这些目录通过 Docker volume 持久化，重启不会丢失。

### Q: 服务器重启后应用会自动启动吗？

会的。docker-compose.cloud.yml 中配置了 `restart: always`，服务器重启后 Docker 会自动拉起应用。

### Q: 怎么彻底删除？

```bash
cd /root/gpt-researcher
docker compose -f docker-compose.cloud.yml down -v  # 停止并删除数据
cd /root && rm -rf gpt-researcher                    # 删除代码
```
