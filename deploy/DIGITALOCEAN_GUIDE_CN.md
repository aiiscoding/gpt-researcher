# DigitalOcean 部署指南（重视数据安全版）

> 选择 DigitalOcean 的理由：
> - 数据完全在你自己的服务器上，不经过任何第三方
> - 自带「自动备份」功能，每周快照，一键恢复
> - 自带「云防火墙」，图形界面配置，不用敲命令
> - 新加坡机房，国内翻墙连接延迟约 100ms
> - 支持支付宝
> - 月费：约 $28（服务器 $24 + 自动备份 $4.80）

---

## 第一步：注册 DigitalOcean 账号

1. 翻墙打开 https://www.digitalocean.com/
2. 点击右上角 **Sign Up**
3. 用邮箱注册或用 Google/GitHub 账号登录
4. 绑定支付方式：支持 **信用卡** 或 **PayPal**
   - 信用卡：Visa/Mastercard 均可
   - PayPal：可以绑定支付宝
5. 注册后会需要验证邮箱

---

## 第二步：创建服务器（Droplet）

1. 登录后，点击右上角绿色按钮 **Create** → **Droplets**

2. **Choose Region（选择地区）**
   - 选择 **Singapore (SGP1)** — 新加坡，国内连接最快

3. **Choose an image（选择系统）**
   - 选择 **Ubuntu** → **24.04 (LTS) x64**

4. **Choose Size（选择配置）**
   - Droplet Type: **Basic**
   - CPU options: **Regular** (SSD)
   - 选择 **$24/mo** 方案：4 GB 内存 / 2 CPU / 80 GB SSD / 4 TB 流量
   - （如果研究频率高或有多人使用，选 $48/mo 的 8GB 方案）

5. **Choose Authentication Method（选择登录方式）**

   **推荐用 SSH 密钥（更安全）：**
   - 点击 **New SSH Key**
   - 在你自己电脑的终端运行：
     ```bash
     # Mac / Linux
     ssh-keygen -t ed25519 -C "你的邮箱"
     cat ~/.ssh/id_ed25519.pub

     # Windows PowerShell
     ssh-keygen -t ed25519 -C "你的邮箱"
     Get-Content $env:USERPROFILE\.ssh\id_ed25519.pub
     ```
   - 复制输出的公钥内容，粘贴到 DigitalOcean 的输入框
   - 给密钥起个名字（例如 "我的电脑"）

   **或者用密码（简单但安全性略低）：**
   - 选择 **Password**
   - 设置一个强密码（至少 12 位，包含大小写字母和数字）

6. **Backups（自动备份）— 重要！**
   - 勾选 **Enable backups** ✅
   - 费用：每月 $4.80（服务器价格的 20%）
   - DigitalOcean 会每周自动为你的整台服务器做快照
   - 如果出任何问题，可以一键恢复到之前的状态

7. **Hostname（主机名）**
   - 改为容易记住的名字，例如 `gpt-researcher`

8. 点击 **Create Droplet**

9. 等待约 1 分钟，服务器创建完成，页面会显示服务器的 **IP 地址**（例如 `165.22.xxx.xxx`）
   - **记下这个 IP 地址！**

---

## 第三步：配置云防火墙

在 DigitalOcean 控制台配置防火墙（比在服务器上配置更安全、更简单）：

1. 左侧菜单 → **Networking** → **Firewalls**
2. 点击 **Create Firewall**
3. 名称填 `gpt-researcher-fw`
4. **Inbound Rules（入站规则）** 配置如下：

   | Type | Protocol | Port Range | Sources |
   |------|----------|------------|---------|
   | SSH | TCP | 22 | All IPv4, All IPv6 |
   | Custom | TCP | 3000 | All IPv4, All IPv6 |

   > 配置 HTTPS 后可以把 3000 改为 443，删掉 3000

5. **Outbound Rules（出站规则）** 保持默认（允许全部出站）
6. **Apply to Droplets** → 选择你刚创建的 `gpt-researcher`
7. 点击 **Create Firewall**

---

## 第四步：连接服务器并部署

### 连接服务器

```bash
# 用 SSH 密钥登录（如果第二步选的密钥）
ssh root@你的IP地址

# 用密码登录（如果第二步选的密码）
ssh root@你的IP地址
# 然后输入密码
```

### 一键部署

```bash
# 1. 安装 git
apt update && apt install -y git

# 2. 下载代码
git clone https://github.com/aiiscoding/gpt-researcher.git
cd gpt-researcher
git checkout claude/cloud-deploy-login-qpHry

# 3. 一键部署（会交互式提示你输入 API Key 和登录密码）
bash deploy/setup.sh
```

部署脚本会问你：
- `OPENAI_API_KEY`：你的 OpenAI 密钥
- `TAVILY_API_KEY`：你的 Tavily 密钥
- 管理员用户名和密码
- 是否添加更多用户

**等待 10-15 分钟构建完成。**

---

## 第五步：验证部署

在浏览器打开 `http://你的IP:3000`，你应该看到登录页面。

用你设置的账号密码登录，开始使用。

---

## 第六步：配置自动数据备份（双重保障）

DigitalOcean 的自动备份是整机快照（每周一次）。我们再加一个每天的数据库备份：

```bash
# 设置每天凌晨 3 点自动备份数据库
crontab -e
```

选择编辑器（新手选 `nano`），添加这一行：

```
0 3 * * * cd /root/gpt-researcher && bash deploy/backup.sh >> /root/gpt-researcher/logs/backup.log 2>&1
```

按 `Ctrl+O` 保存，`Ctrl+X` 退出。

这样你有**两层备份**：
1. DigitalOcean 每周整机快照（可恢复整台服务器）
2. 每天的数据库备份（可精确恢复数据）

---

## 第七步：配置 HTTPS（强烈建议）

### 方案 A：有自己的域名

```bash
# 安装 Caddy（自动 HTTPS）
apt install -y debian-keyring debian-archive-keyring apt-transport-https curl
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | tee /etc/apt/sources.list.d/caddy-stable.list
apt update && apt install -y caddy

# 配置（把 your-domain.com 换成你的域名）
cat > /etc/caddy/Caddyfile << 'EOF'
your-domain.com {
    reverse_proxy localhost:3000
}
EOF

systemctl restart caddy
```

然后去你的域名 DNS 管理添加 A 记录：`your-domain.com` → `你的服务器IP`

### 方案 B：没有域名，用 IP 访问

可以用自签名证书（浏览器会有安全警告，但数据是加密的）：

```bash
# 安装 Caddy
apt install -y debian-keyring debian-archive-keyring apt-transport-https curl
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | tee /etc/apt/sources.list.d/caddy-stable.list
apt update && apt install -y caddy

cat > /etc/caddy/Caddyfile << 'EOF'
:443 {
    tls internal
    reverse_proxy localhost:3000
}
EOF

systemctl restart caddy
```

配好 HTTPS 后更新 .env：

```bash
cd /root/gpt-researcher
nano .env
# 把 AUTH_COOKIE_SECURE=false 改为 AUTH_COOKIE_SECURE=true
# 保存退出

docker compose -f docker-compose.cloud.yml restart
```

然后在 DigitalOcean 防火墙里：
- 添加 443 端口规则
- 删除 3000 端口规则（不再需要）

---

## 数据安全总结

| 保护层 | 方式 | 说明 |
|--------|------|------|
| **传输加密** | HTTPS (Caddy) | 所有数据传输经过 TLS 加密 |
| **登录保护** | JWT + 暴力破解防护 | 5 次错误锁定 IP 15 分钟 |
| **数据存储** | SQLite WAL 模式 | 断电不丢数据，事务保护 |
| **网络防护** | DigitalOcean 云防火墙 | 只开放必要端口 |
| **整机备份** | DigitalOcean 自动快照 | 每周一次，可一键恢复 |
| **数据备份** | crontab 定时脚本 | 每天备份数据库 |
| **访问控制** | 预设账号，无注册入口 | 只有你授权的人能用 |

---

## 费用明细

| 项目 | 月费 |
|------|------|
| Droplet (4GB) | $24.00 |
| 自动备份 | $4.80 |
| **合计** | **$28.80/月** |

> 这还不包括 OpenAI API 调用费用（取决于你的使用量，通常 $5-20/月）。

---

## 出问题怎么办？

### 服务器挂了

1. 去 DigitalOcean 控制台
2. 点击你的 Droplet → **Recovery** → **Boot from Recovery ISO**
3. 或者直接从备份恢复：**Backups** → 选择一个快照 → **Restore Droplet**

### 要看日志

```bash
ssh root@你的IP
cd /root/gpt-researcher
docker compose -f docker-compose.cloud.yml logs -f
```

### 更新代码

```bash
ssh root@你的IP
cd /root/gpt-researcher
git pull
docker compose -f docker-compose.cloud.yml up -d --build
```
