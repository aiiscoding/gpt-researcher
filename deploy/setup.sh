#!/bin/bash
# ============================================================
# GPT Researcher 云端一键部署脚本
# 适用于全新的 Ubuntu/Debian 服务器
# ============================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_step() { echo -e "\n${GREEN}[步骤 $1] $2${NC}\n"; }
print_warn() { echo -e "${YELLOW}[提示] $1${NC}"; }
print_error() { echo -e "${RED}[错误] $1${NC}"; }

# ---- Step 0: 检查是否在项目目录 ----
if [ ! -f "docker-compose.cloud.yml" ]; then
    print_error "请在 gpt-researcher 项目根目录下运行此脚本！"
    echo "  cd /path/to/gpt-researcher"
    echo "  bash deploy/setup.sh"
    exit 1
fi

# ---- Step 1: 安装 Docker ----
print_step 1 "检查并安装 Docker..."

if command -v docker &> /dev/null; then
    echo "Docker 已安装: $(docker --version)"
else
    echo "正在安装 Docker..."
    curl -fsSL https://get.docker.com | sh
    sudo systemctl enable docker
    sudo systemctl start docker
    echo "Docker 安装完成: $(docker --version)"
fi

# 确保当前用户可以运行 docker（不需要 sudo）
if ! docker ps &> /dev/null 2>&1; then
    sudo usermod -aG docker "$USER"
    print_warn "已将当前用户加入 docker 组，请重新登录后再运行此脚本"
    print_warn "运行: exit 然后重新 SSH 登录，再执行 bash deploy/setup.sh"
    exit 0
fi

# ---- Step 2: 检查 Docker Compose ----
print_step 2 "检查 Docker Compose..."

if docker compose version &> /dev/null 2>&1; then
    echo "Docker Compose 已就绪: $(docker compose version)"
else
    print_error "Docker Compose 未安装，请更新 Docker 到最新版本"
    exit 1
fi

# ---- Step 3: 创建 .env 文件 ----
print_step 3 "配置环境变量..."

if [ -f ".env" ]; then
    print_warn ".env 文件已存在，跳过创建（如需重新配置，请删除 .env 后重新运行）"
else
    echo ""
    echo "=========================================="
    echo "  请输入你的 API 密钥"
    echo "=========================================="
    echo ""

    # OpenAI API Key
    read -p "请输入 OPENAI_API_KEY（必填）: " OPENAI_API_KEY
    if [ -z "$OPENAI_API_KEY" ]; then
        print_error "OPENAI_API_KEY 不能为空！"
        exit 1
    fi

    # Tavily API Key
    read -p "请输入 TAVILY_API_KEY（必填，去 tavily.com 免费获取）: " TAVILY_API_KEY
    if [ -z "$TAVILY_API_KEY" ]; then
        print_error "TAVILY_API_KEY 不能为空！"
        exit 1
    fi

    # OpenAI Base URL (optional)
    read -p "自定义 OpenAI API 地址（留空使用官方地址，国内用户可填代理地址）: " OPENAI_BASE_URL

    echo ""
    echo "=========================================="
    echo "  配置登录账号"
    echo "=========================================="
    echo ""

    # Auth users
    read -p "管理员用户名（默认 admin）: " AUTH_USERNAME
    AUTH_USERNAME=${AUTH_USERNAME:-admin}

    read -s -p "管理员密码（默认 admin123）: " AUTH_PASSWORD
    AUTH_PASSWORD=${AUTH_PASSWORD:-admin123}
    echo ""

    # 是否添加更多用户
    AUTH_USERS="${AUTH_USERNAME}:${AUTH_PASSWORD}"
    while true; do
        read -p "是否添加更多用户？(y/n，默认 n): " ADD_MORE
        ADD_MORE=${ADD_MORE:-n}
        if [ "$ADD_MORE" = "y" ] || [ "$ADD_MORE" = "Y" ]; then
            read -p "  用户名: " EXTRA_USER
            read -s -p "  密码: " EXTRA_PASS
            echo ""
            if [ -n "$EXTRA_USER" ] && [ -n "$EXTRA_PASS" ]; then
                AUTH_USERS="${AUTH_USERS},${EXTRA_USER}:${EXTRA_PASS}"
            fi
        else
            break
        fi
    done

    # 生成随机密钥
    AUTH_SECRET_KEY=$(openssl rand -hex 32 2>/dev/null || head -c 64 /dev/urandom | od -An -tx1 | tr -d ' \n')

    # 写入 .env 文件
    cat > .env << ENVEOF
# GPT Researcher 环境配置
# 由 deploy/setup.sh 自动生成于 $(date)

# API 密钥（必填）
OPENAI_API_KEY=${OPENAI_API_KEY}
TAVILY_API_KEY=${TAVILY_API_KEY}
ENVEOF

    # 只有填了才写入
    if [ -n "$OPENAI_BASE_URL" ]; then
        echo "OPENAI_BASE_URL=${OPENAI_BASE_URL}" >> .env
    fi

    cat >> .env << ENVEOF

# 认证配置
AUTH_ENABLED=true
AUTH_SECRET_KEY=${AUTH_SECRET_KEY}
AUTH_TOKEN_EXPIRE_HOURS=24
AUTH_COOKIE_SECURE=false
AUTH_USERS=${AUTH_USERS}

# 其他配置
DOC_PATH=./my-docs
LOGGING_LEVEL=INFO
ENVEOF

    echo ""
    print_warn ".env 文件已创建"
    echo ""
fi

# ---- Step 4: 创建必要目录 ----
print_step 4 "创建数据目录..."
mkdir -p outputs data logs my-docs
echo "目录创建完成: outputs/ data/ logs/ my-docs/"

# ---- Step 5: 构建并启动 ----
print_step 5 "构建 Docker 镜像并启动服务（首次可能需要 10-20 分钟）..."
echo ""
print_warn "正在构建中，请耐心等待..."
echo ""

docker compose -f docker-compose.cloud.yml up -d --build

# ---- Step 6: 检查状态 ----
print_step 6 "检查服务状态..."
sleep 5

if docker compose -f docker-compose.cloud.yml ps | grep -q "running"; then
    echo ""
    echo -e "${GREEN}=========================================="
    echo "  部署成功！"
    echo "==========================================${NC}"
    echo ""

    # 获取服务器 IP
    SERVER_IP=$(curl -s --connect-timeout 5 ifconfig.me 2>/dev/null || hostname -I | awk '{print $1}')

    echo "  访问地址: http://${SERVER_IP}:3000"
    echo ""
    echo "  登录账号信息已保存在 .env 文件中"
    echo ""
    echo "  常用命令:"
    echo "    查看日志:   docker compose -f docker-compose.cloud.yml logs -f"
    echo "    停止服务:   docker compose -f docker-compose.cloud.yml down"
    echo "    重启服务:   docker compose -f docker-compose.cloud.yml restart"
    echo "    更新部署:   git pull && docker compose -f docker-compose.cloud.yml up -d --build"
    echo ""
else
    print_error "服务启动可能有问题，请查看日志:"
    echo "  docker compose -f docker-compose.cloud.yml logs"
fi
