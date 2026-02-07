#!/bin/bash
# Entrypoint script for Railway/PaaS deployment
# Dynamically configures nginx to listen on $PORT (required by Railway)

set -e

# Railway provides a $PORT env var; default to 3000 for other platforms
LISTEN_PORT="${PORT:-3000}"

echo "=== GPT Researcher Starting ==="
echo "Listening port: ${LISTEN_PORT}"
echo "Auth enabled: ${AUTH_ENABLED:-false}"

# Replace the nginx listen port with the Railway-assigned port
if [ -f /etc/nginx/nginx.conf ]; then
    sed -i "s/listen 3000;/listen ${LISTEN_PORT};/" /etc/nginx/nginx.conf
    echo "Nginx configured to listen on port ${LISTEN_PORT}"
fi

# Ensure data directories exist
mkdir -p /usr/src/app/outputs /usr/src/app/data /usr/src/app/logs /usr/src/app/my-docs

# Start supervisord (manages backend + frontend + nginx)
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
