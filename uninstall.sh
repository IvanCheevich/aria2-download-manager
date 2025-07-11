#!/bin/bash

# Скрипт деинсталляции Aria2 Download Manager

set -e

echo "Деинсталляция Aria2 Download Manager..."

# Проверяем права root
if [[ $EUID -ne 0 ]]; then
   echo "Этот скрипт должен быть запущен с правами root (sudo)" 
   exit 1
fi

# Удаляем файлы
echo "Удаление файлов..."

# Удаляем исполняемый файл
rm -f /usr/local/bin/aria2-download-manager

# Удаляем папку приложения
rm -rf /opt/aria2-download-manager

# Удаляем .desktop файл
rm -f /usr/share/applications/aria2-download-manager.desktop

# Удаляем иконку
rm -f /usr/share/icons/hicolor/scalable/apps/aria2-download-manager.svg

# Обновляем кэш иконок
gtk-update-icon-cache -t /usr/share/icons/hicolor/ || true

# Обновляем базу данных приложений
update-desktop-database /usr/share/applications/ || true

echo "Деинсталляция завершена!"