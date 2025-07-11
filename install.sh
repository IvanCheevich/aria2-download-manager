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
echo "🔧 Устанавливаем все необходимые зависимости..."

# Определяем дистрибутив и устанавливаем зависимости
if command -v apt-get &> /dev/null; then
    echo "📦 Обнаружен Debian/Ubuntu. Устанавливаем пакеты..."
    apt-get update
    apt-get install -y aria2 python3 python3-tk python3-pip python3-requests curl wget
    echo "✅ Пакеты Debian/Ubuntu установлены"
elif command -v dnf &> /dev/null; then
    echo "📦 Обнаружен Fedora. Устанавливаем пакеты..."
    dnf install -y aria2 python3 python3-tkinter python3-pip python3-requests curl wget
    echo "✅ Пакеты Fedora установлены"
elif command -v yum &> /dev/null; then
    echo "📦 Обнаружен CentOS/RHEL. Устанавливаем пакеты..."
    yum install -y epel-release
    yum install -y aria2 python3 python3-tkinter python3-pip curl wget
    pip3 install requests
    echo "✅ Пакеты CentOS/RHEL установлены"
elif command -v pacman &> /dev/null; then
    echo "📦 Обнаружен Arch Linux. Устанавливаем пакеты..."
    pacman -Syu --noconfirm aria2 python python-pip curl wget tk
    pip3 install requests
    echo "✅ Пакеты Arch Linux установлены"
elif command -v zypper &> /dev/null; then
    echo "📦 Обнаружен openSUSE. Устанавливаем пакеты..."
    zypper refresh
    zypper install -y aria2 python3 python3-tk python3-pip python3-requests curl wget
    echo "✅ Пакеты openSUSE установлены"
else
    echo "❌ Неподдерживаемый дистрибутив. Установите следующие пакеты вручную:"
    echo "   • aria2"
    echo "   • python3"
    echo "   • python3-tk (или python3-tkinter)"
    echo "   • python3-requests"
    echo "   • curl"
    echo "   • wget"
    exit 1
fi

# Проверяем установку всех компонентов
echo "🔍 Проверяем установленные компоненты..."

if ! command -v aria2c &> /dev/null; then
    echo "❌ ОШИБКА: aria2 не установлен"
    exit 1
fi
echo "✅ aria2c найден: $(aria2c --version | head -1)"

if ! command -v python3 &> /dev/null; then
    echo "❌ ОШИБКА: python3 не установлен" 
    exit 1
fi
echo "✅ python3 найден: $(python3 --version)"

# Проверяем tkinter
if ! python3 -c "import tkinter" &> /dev/null; then
    echo "❌ ОШИБКА: tkinter не установлен"
    echo "Попробуйте установить: python3-tk или python3-tkinter"
    exit 1
fi
echo "✅ tkinter доступен"

# Проверяем requests
if ! python3 -c "import requests" &> /dev/null; then
    echo "⚠️  requests не найден, устанавливаем через pip..."
    pip3 install requests
    if ! python3 -c "import requests" &> /dev/null; then
        echo "❌ ОШИБКА: не удалось установить requests"
        exit 1
    fi
fi
echo "✅ requests доступен"

echo "🎉 Все зависимости установлены успешно!"

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

echo ""
echo "🎉 Установка завершена успешно!"
echo ""
echo "📋 Способы запуска приложения:"
echo "   • Через меню приложений (раздел 'Интернет')"
echo "   • Команда в терминале: aria2-download-manager"
echo "   • Напрямую: python3 /opt/aria2-download-manager/src/simple_gui.py"
echo ""
echo "🛠️  Основные функции:"
echo "   • ➕ Добавление URL загрузок"
echo "   • 🧲 Поддержка торрент файлов"
echo "   • ⏸️ Пауза/возобновление загрузок"
echo "   • 🗑️ Удаление загрузок"
echo "   • 📁 Быстрый доступ к папке загрузок"
echo "   • 🔄 Автоматическое обновление списка"
echo ""
echo "🗂️  Файлы загружаются в: ~/Downloads"
echo "📦 Aria2 Download Manager готов к использованию!"