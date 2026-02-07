#!/bin/bash
# ============================================================
# GPT Researcher 数据备份脚本
# 用法: bash deploy/backup.sh [备份目录]
# 默认备份到 ./backups/ 目录
# 建议配合 crontab 定时运行
# ============================================================

set -e

BACKUP_DIR="${1:-./backups}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="gptr_backup_${TIMESTAMP}"
BACKUP_PATH="${BACKUP_DIR}/${BACKUP_NAME}"

echo "=== GPT Researcher 数据备份 ==="
echo "备份时间: $(date)"
echo "备份目录: ${BACKUP_PATH}"

# 创建备份目录
mkdir -p "${BACKUP_PATH}"

# 备份 SQLite 数据库（使用 .backup 命令确保一致性）
if [ -f "data/reports.db" ]; then
    echo "正在备份数据库..."
    sqlite3 data/reports.db ".backup '${BACKUP_PATH}/reports.db'"
    echo "  数据库备份完成"
elif [ -f "data/reports.json" ]; then
    echo "正在备份 JSON 数据..."
    cp data/reports.json "${BACKUP_PATH}/reports.json"
    echo "  JSON 数据备份完成"
else
    echo "  没有找到数据文件，跳过"
fi

# 备份环境配置（脱敏处理）
if [ -f ".env" ]; then
    echo "正在备份配置..."
    # 只保留非敏感配置项
    grep -v -E "(API_KEY|SECRET_KEY|PASSWORD|AUTH_USERS)" .env > "${BACKUP_PATH}/env_config.txt" 2>/dev/null || true
    echo "  配置备份完成（已脱敏）"
fi

# 备份输出文件（研究报告 PDF/DOCX）
if [ -d "outputs" ] && [ "$(ls -A outputs 2>/dev/null)" ]; then
    echo "正在备份研究报告..."
    cp -r outputs "${BACKUP_PATH}/outputs"
    echo "  报告备份完成"
fi

# 压缩备份
echo "正在压缩..."
cd "${BACKUP_DIR}"
tar -czf "${BACKUP_NAME}.tar.gz" "${BACKUP_NAME}"
rm -rf "${BACKUP_NAME}"
cd - > /dev/null

FINAL_PATH="${BACKUP_DIR}/${BACKUP_NAME}.tar.gz"
SIZE=$(du -h "${FINAL_PATH}" | cut -f1)

echo ""
echo "=== 备份完成 ==="
echo "文件: ${FINAL_PATH}"
echo "大小: ${SIZE}"
echo ""

# 清理旧备份（保留最近 30 个）
BACKUP_COUNT=$(ls -1 "${BACKUP_DIR}"/gptr_backup_*.tar.gz 2>/dev/null | wc -l)
if [ "${BACKUP_COUNT}" -gt 30 ]; then
    echo "清理旧备份（保留最近 30 个）..."
    ls -1t "${BACKUP_DIR}"/gptr_backup_*.tar.gz | tail -n +31 | xargs rm -f
    echo "清理完成"
fi

echo ""
echo "提示: 建议设置定时备份 (每天凌晨 3 点):"
echo "  crontab -e"
echo "  添加: 0 3 * * * cd $(pwd) && bash deploy/backup.sh"
