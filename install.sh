#!/bin/bash

# Скрипт установки Aria2 Download Manager

set -e

echo "Установка Aria2 Download Manager..."

# Проверяем права root
if [[ $EUID -ne 0 ]]; then
   echo "Этот скрипт должен быть запущен с правами root (sudo)" 
   exit 1
fi

# Устанавливаем зависимости
echo "Проверка зависимостей..."

# Проверяем aria2
if ! command -v aria2c &> /dev/null; then
    echo "aria2 не найден. Устанавливаем..."
    if command -v apt-get &> /dev/null; then
        apt-get update
        apt-get install -y aria2
    elif command -v dnf &> /dev/null; then
        dnf install -y aria2
    elif command -v pacman &> /dev/null; then
        pacman -S --noconfirm aria2
    else
        echo "Неподдерживаемый пакетный менеджер. Установите aria2 вручную."
        exit 1
    fi
fi

# Проверяем Python и tkinter
if ! python3 -c "import tkinter" &> /dev/null; then
    echo "tkinter не найден. Устанавливаем..."
    if command -v apt-get &> /dev/null; then
        apt-get install -y python3-tk
    elif command -v dnf &> /dev/null; then
        dnf install -y tkinter
    elif command -v pacman &> /dev/null; then
        pacman -S --noconfirm tk
    fi
fi

# Проверяем Python зависимости
echo "Проверяем Python зависимости..."
if ! python3 -c "import requests" &> /dev/null; then
    echo "requests не найден. Устанавливаем через системный пакетный менеджер..."
    if command -v apt-get &> /dev/null; then
        apt-get install -y python3-requests
    elif command -v dnf &> /dev/null; then
        dnf install -y python3-requests
    elif command -v pacman &> /dev/null; then
        pacman -S --noconfirm python-requests
    else
        echo "Установите python3-requests вручную или используйте pip3 install requests --break-system-packages"
    fi
fi

# Копируем файлы
echo "Копируем файлы..."
mkdir -p /opt/aria2-download-manager
cp -r src/ /opt/aria2-download-manager/
cp aria2-download-manager /opt/aria2-download-manager/

# Делаем исполняемым
chmod +x /opt/aria2-download-manager/aria2-download-manager
chmod +x /opt/aria2-download-manager/src/simple_gui.py

# Создаем символическую ссылку
ln -sf /opt/aria2-download-manager/aria2-download-manager /usr/local/bin/aria2-download-manager

# Устанавливаем .desktop файл
cp aria2-download-manager.desktop /usr/share/applications/

# Создаем простую иконку (SVG)
mkdir -p /usr/share/icons/hicolor/scalable/apps
cat > /usr/share/icons/hicolor/scalable/apps/aria2-download-manager.svg << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<svg width="48" height="48" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
  <circle cx="24" cy="24" r="20" fill="#4CAF50" stroke="#2E7D32" stroke-width="2"/>
  <path d="M16 24 L20 28 L32 16" stroke="white" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M12 32 L36 32" stroke="#2E7D32" stroke-width="2" stroke-linecap="round"/>
  <path d="M18 38 L30 38" stroke="#2E7D32" stroke-width="2" stroke-linecap="round"/>
</svg>
EOF

# Обновляем кэш иконок
gtk-update-icon-cache -t /usr/share/icons/hicolor/ || true

# Обновляем базу данных приложений
update-desktop-database /usr/share/applications/ || true

echo "Установка завершена!"
echo "Приложение можно найти в меню приложений или запустить командой: aria2-download-manager"