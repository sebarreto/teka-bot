#!/bin/bash
set -e  # Detener ejecución si hay un error

echo "🔄 Actualizando paquetes..."
export DEBIAN_FRONTEND=noninteractive  # Evita prompts de instalación
apt-get update -y && apt-get install -y ffmpeg supervisor

echo "📦 Instalando dependencias de Python..."
pip install --upgrade pip
pip install -r /home/site/wwwroot/requirements.txt

# Verificar si el bot ya está corriendo y detenerlo
if pgrep -f "python teka_bot.py"; then
    echo "🔄 El bot ya está corriendo. Matando proceso anterior..."
    pkill -f "python teka_bot.py"
    sleep 3  # Esperar para liberar recursos
fi

echo "🚀 Iniciando el bot con supervisord..."

# Crear configuración de supervisord
cat <<EOF > /home/site/wwwroot/supervisord.conf
[supervisord]
nodaemon=true

[program:teka_bot]
command=python /home/site/wwwroot/teka_bot.py
autostart=true
autorestart=true
startretries=5
stderr_logfile=/dev/stderr
stdout_logfile=/dev/stdout
EOF

# Iniciar supervisord
exec supervisord -c /home/site/wwwroot/supervisord.conf