#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sys
import os

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(__file__))

from aria2_client import Aria2Client


class DebugDownloadGUI:
    """Отладочная версия GUI с подробным логированием"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Aria2 Download Manager (Debug)")
        self.root.geometry("900x700")
        
        # Создаем лог область
        self.setup_debug_ui()
        
        # Инициализация aria2 клиента
        self.log("Инициализация aria2 клиента...")
        self.aria2_client = Aria2Client()
        
        self.log("Попытка запуска aria2 демона...")
        if not self.aria2_client.start_aria2_daemon():
            self.log("ОШИБКА: Не удалось запустить aria2")
            messagebox.showerror("Ошибка", "Не удалось запустить aria2. Проверьте лог для деталей.")
        else:
            self.log("✅ aria2 демон запущен успешно")
            self.setup_main_ui()
        
    def setup_debug_ui(self):
        """Настройка отладочного интерфейса"""
        # Главный фрейм
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Лог область
        log_frame = ttk.LabelFrame(main_frame, text="Лог отладки")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Текстовое поле для лога
        self.log_text = tk.Text(log_frame, height=15, wrap=tk.WORD)
        log_scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Кнопки тестирования
        test_frame = ttk.Frame(main_frame)
        test_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(test_frame, text="Тест aria2", command=self.test_aria2).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(test_frame, text="Очистить лог", command=self.clear_log).pack(side=tk.LEFT, padx=(0, 5))
        
        # Переключатель автообновления
        self.auto_refresh_var = tk.BooleanVar(value=True)
        auto_check = ttk.Checkbutton(test_frame, text="🔄 Авто-обновление", 
                                   variable=self.auto_refresh_var,
                                   command=self.toggle_auto_refresh)
        auto_check.pack(side=tk.LEFT, padx=(10, 5))
        
        # Статус
        self.status_label = ttk.Label(main_frame, text="Загрузка...")
        self.status_label.pack(fill=tk.X)
        
    def setup_main_ui(self):
        """Настройка основного интерфейса после успешного запуска aria2"""
        # Добавляем кнопки управления
        control_frame = ttk.Frame(self.root)
        control_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ttk.Button(control_frame, text="➕ Добавить URL", 
                  command=self.add_url_dialog).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="🧪 Тест загрузка", 
                  command=self.add_download).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="🧲 Добавить торрент", 
                  command=self.add_torrent_dialog).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="Обновить список", 
                  command=self.refresh_downloads).pack(side=tk.LEFT, padx=(0, 10))
        
        # Кнопки управления загрузками
        ttk.Button(control_frame, text="⏸️ Пауза/Возобновить", 
                  command=self.toggle_last_download).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="🗑️ Удалить загрузку", 
                  command=self.remove_last_download).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="📁 Открыть папку", 
                  command=self.open_downloads_folder).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(control_frame, text="🔥 Удалить файл", 
                  command=self.delete_last_file).pack(side=tk.LEFT)
        
        # Список загрузок (простой)
        downloads_frame = ttk.LabelFrame(self.root, text="Загрузки")
        downloads_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        self.downloads_text = tk.Text(downloads_frame, height=8, font=("Consolas", 10))
        downloads_scroll = ttk.Scrollbar(downloads_frame, orient=tk.VERTICAL, command=self.downloads_text.yview)
        self.downloads_text.configure(yscrollcommand=downloads_scroll.set)
        
        self.downloads_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0), pady=5)
        downloads_scroll.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 5), pady=5)
        
        self.status_label.config(text="Готов к работе")
        
        # Запускаем автоматическое обновление
        self.start_auto_refresh()
        
    def log(self, message):
        """Добавляет сообщение в лог"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        if hasattr(self, 'log_text'):
            self.log_text.insert(tk.END, log_message)
            self.log_text.see(tk.END)
        
        # Также выводим в консоль
        print(log_message.strip())
        
    def clear_log(self):
        """Очищает лог"""
        self.log_text.delete(1.0, tk.END)
        
    def test_aria2(self):
        """Тестирует aria2"""
        self.log("=== ТЕСТ ARIA2 ===")
        
        import subprocess
        paths = ["/usr/bin/aria2c", "aria2c"]
        
        for path in paths:
            self.log(f"Тестирую: {path}")
            try:
                result = subprocess.run([path, "--version"], 
                                      capture_output=True, text=True, timeout=3)
                if result.returncode == 0:
                    version = result.stdout.split()[2] if len(result.stdout.split()) > 2 else "unknown"
                    self.log(f"✅ {path} работает, версия: {version}")
                else:
                    self.log(f"❌ Ошибка: {result.stderr}")
            except Exception as e:
                self.log(f"❌ Исключение: {e}")
        
        # Тест подключения к демону
        try:
            import requests
            response = requests.post(
                "http://localhost:6800/jsonrpc",
                json={"jsonrpc": "2.0", "id": "test", "method": "aria2.getVersion"},
                timeout=3
            )
            if response.status_code == 200:
                self.log("✅ Подключение к демону работает")
            else:
                self.log(f"❌ Ошибка подключения: {response.status_code}")
        except Exception as e:
            self.log(f"❌ Ошибка подключения: {e}")
            
    def add_url_dialog(self):
        """Диалог для ввода URL пользователем"""
        from tkinter import simpledialog, filedialog
        
        self.log("=== ДОБАВЛЕНИЕ URL ===")
        
        # Запрашиваем URL
        url = simpledialog.askstring(
            "Добавить загрузку",
            "Введите URL для загрузки:",
            parent=self.root
        )
        
        if not url:
            self.log("❌ URL не введен")
            return
            
        self.log(f"Введен URL: {url}")
        
        # Запрашиваем папку
        folder = filedialog.askdirectory(
            title="Выберите папку для загрузки",
            initialdir=os.path.expanduser("~/Downloads")
        )
        
        if not folder:
            folder = os.path.expanduser("~/Downloads")
            self.log(f"Использую папку по умолчанию: {folder}")
        else:
            self.log(f"Выбрана папка: {folder}")
        
        try:
            options = {"dir": folder}
            self.log(f"Опции загрузки: {options}")
            
            gid = self.aria2_client.add_download(url, options)
            if gid:
                self.log(f"✅ Загрузка добавлена: {gid}")
                self.refresh_downloads()
            else:
                self.log("❌ Не удалось добавить загрузку")
        except Exception as e:
            self.log(f"❌ Ошибка добавления загрузки: {e}")
            import traceback
            self.log(f"Детали ошибки: {traceback.format_exc()}")

    def add_download(self):
        """Добавляет тестовую загрузку"""
        url = "http://httpbin.org/bytes/1024"  # Простой тестовый файл
        self.log(f"Добавляю тестовую загрузку: {url}")
        
        try:
            # Тестируем с опциями
            options = {"dir": os.path.expanduser("~/Downloads")}
            self.log(f"Опции загрузки: {options}")
            
            gid = self.aria2_client.add_download(url, options)
            if gid:
                self.log(f"✅ Загрузка добавлена: {gid}")
                self.refresh_downloads()
            else:
                self.log("❌ Не удалось добавить загрузку")
        except Exception as e:
            self.log(f"❌ Ошибка добавления загрузки: {e}")
            import traceback
            self.log(f"Детали ошибки: {traceback.format_exc()}")
    
    def add_torrent_dialog(self):
        """Диалог добавления торрента"""
        from tkinter import filedialog, messagebox
        
        self.log("=== ДОБАВЛЕНИЕ ТОРРЕНТА ===")
        
        # Выбираем торрент файл
        torrent_path = filedialog.askopenfilename(
            title="Выберите торрент файл",
            initialdir=os.path.expanduser("~/Загрузки"),
            filetypes=[("Торрент файлы", "*.torrent"), ("Все файлы", "*.*")]
        )
        
        if not torrent_path:
            self.log("❌ Торрент файл не выбран")
            return
        
        self.log(f"Выбран торрент: {torrent_path}")
        
        if not os.path.exists(torrent_path):
            self.log("❌ Торрент файл не найден")
            messagebox.showerror("Ошибка", "Торрент файл не найден")
            return
        
        # Выбираем папку для загрузки
        folder = filedialog.askdirectory(
            title="Выберите папку для загрузки",
            initialdir=os.path.expanduser("~/Загрузки")
        )
        
        if not folder:
            folder = os.path.expanduser("~/Загрузки")
            self.log(f"Использую папку по умолчанию: {folder}")
        else:
            self.log(f"Выбрана папка: {folder}")
        
        try:
            # Добавляем опции
            options = {"dir": folder}
            self.log(f"Опции загрузки: {options}")
            
            # Проверяем размер файла
            file_size = os.path.getsize(torrent_path)
            self.log(f"Размер торрент файла: {file_size} байт")
            
            # Пробуем прочитать первые байты файла для проверки
            with open(torrent_path, 'rb') as f:
                first_bytes = f.read(10)
                self.log(f"Первые байты файла: {first_bytes}")
            
            self.log("Вызываю aria2_client.add_torrent...")
            gid = self.aria2_client.add_torrent(torrent_path, options)
            self.log(f"Результат add_torrent: {gid}")
            
            if gid:
                self.log(f"✅ Торрент добавлен: {gid}")
                messagebox.showinfo("Успех", f"Торрент добавлен: {gid}")
                self.refresh_downloads()
            else:
                self.log("❌ Не удалось добавить торрент - aria2 вернул None")
                messagebox.showerror("Ошибка", "Не удалось добавить торрент")
        except Exception as e:
            self.log(f"❌ Ошибка добавления торрента: {e}")
            import traceback
            self.log(f"Трассировка: {traceback.format_exc()}")
            messagebox.showerror("Ошибка", f"Ошибка добавления торрента:\n{e}")
    
    def test_torrent(self):
        """Тестирует добавление торрента (старая функция)"""
        from tkinter import filedialog
        
        self.log("=== ТЕСТ ТОРРЕНТА ===")
        
        # Просим выбрать торрент файл
        torrent_path = filedialog.askopenfilename(
            title="Выберите торрент файл для теста",
            filetypes=[("Торрент файлы", "*.torrent"), ("Все файлы", "*.*")]
        )
        
        if not torrent_path:
            self.log("❌ Торрент файл не выбран")
            return
        
        self.log(f"Выбран торрент: {torrent_path}")
        
        try:
            gid = self.aria2_client.add_torrent(torrent_path)
            if gid:
                self.log(f"✅ Торрент добавлен: {gid}")
                self.refresh_downloads()
            else:
                self.log("❌ Не удалось добавить торрент")
        except Exception as e:
            self.log(f"❌ Ошибка добавления торрента: {e}")
            
    def refresh_downloads(self):
        """Обновляет список загрузок с прогрессом"""
        try:
            downloads = self.aria2_client.get_all_downloads()
            self.downloads_text.delete(1.0, tk.END)
            
            if downloads:
                self.downloads_text.insert(tk.END, "=" * 80 + "\n")
                self.downloads_text.insert(tk.END, "📋 АКТИВНЫЕ ЗАГРУЗКИ\n")
                self.downloads_text.insert(tk.END, "=" * 80 + "\n\n")
                
                active_count = 0
                for download in downloads:
                    gid = download.get("gid", "")[:8]
                    status = download.get("status", "unknown")
                    files = download.get("files", [])
                    filename = "unknown"
                    if files:
                        filename = os.path.basename(files[0].get("path", "unknown"))
                    
                    # Получаем детальную информацию
                    total_length = int(download.get("totalLength", 0))
                    completed_length = int(download.get("completedLength", 0))
                    download_speed = int(download.get("downloadSpeed", 0))
                    
                    # Форматируем размеры
                    def format_size(bytes_num):
                        for unit in ['B', 'KB', 'MB', 'GB']:
                            if bytes_num < 1024.0:
                                return f"{bytes_num:.1f} {unit}"
                            bytes_num /= 1024.0
                        return f"{bytes_num:.1f} TB"
                    
                    def format_speed(bytes_per_sec):
                        return format_size(bytes_per_sec) + "/s"
                    
                    # Вычисляем прогресс
                    if total_length > 0:
                        progress = (completed_length / total_length) * 100
                        progress_bar = "█" * int(progress / 5) + "░" * (20 - int(progress / 5))
                        size_info = f"{format_size(completed_length)} / {format_size(total_length)}"
                    else:
                        progress = 0
                        progress_bar = "░" * 20
                        size_info = format_size(completed_length)
                    
                    # Скорость и ETA
                    if download_speed > 0:
                        speed_info = format_speed(download_speed)
                        if total_length > completed_length:
                            eta_seconds = (total_length - completed_length) / download_speed
                            eta_info = f"ETA: {int(eta_seconds//60)}:{int(eta_seconds%60):02d}"
                        else:
                            eta_info = "Завершено"
                    else:
                        speed_info = "0 B/s"
                        eta_info = "∞"
                    
                    # Статус
                    status_emoji = {
                        "active": "🔄",
                        "paused": "⏸️", 
                        "complete": "✅",
                        "error": "❌",
                        "removed": "🗑️"
                    }.get(status, "❓")
                    
                    if status == "active":
                        active_count += 1
                    
                    # Выводим информацию о загрузке
                    self.downloads_text.insert(tk.END, f"📁 {filename}\n")
                    self.downloads_text.insert(tk.END, f"🆔 {gid} | {status_emoji} {status.upper()}\n")
                    self.downloads_text.insert(tk.END, f"📊 [{progress_bar}] {progress:.1f}%\n")
                    self.downloads_text.insert(tk.END, f"💾 {size_info}\n")
                    self.downloads_text.insert(tk.END, f"⚡ {speed_info} | ⏱️ {eta_info}\n")
                    self.downloads_text.insert(tk.END, "-" * 60 + "\n\n")
                
                # Итоговая статистика
                self.downloads_text.insert(tk.END, f"📈 ИТОГО: {len(downloads)} загрузок, активных: {active_count}\n")
            else:
                self.downloads_text.insert(tk.END, "📭 Нет загрузок\n")
                
            self.log(f"Обновлен список: {len(downloads)} загрузок")
        except Exception as e:
            self.log(f"❌ Ошибка обновления списка: {e}")
    
    def toggle_last_download(self):
        """Переключает паузу/возобновление последней загрузки"""
        try:
            downloads = self.aria2_client.get_all_downloads()
            if not downloads:
                self.log("❌ Нет загрузок для управления")
                return
            
            # Берем последнюю активную загрузку
            last_download = None
            for download in downloads:
                if download.get("status") in ["active", "paused"]:
                    last_download = download
                    break
            
            if not last_download:
                self.log("❌ Нет активных загрузок")
                return
            
            gid = last_download.get("gid")
            status = last_download.get("status")
            filename = "unknown"
            files = last_download.get("files", [])
            if files:
                filename = os.path.basename(files[0].get("path", "unknown"))
            
            if status == "active":
                self.aria2_client.pause_download(gid)
                self.log(f"⏸️ Пауза: {filename} ({gid[:8]})")
            elif status == "paused":
                self.aria2_client.unpause_download(gid)
                self.log(f"▶️ Возобновлено: {filename} ({gid[:8]})")
                
        except Exception as e:
            self.log(f"❌ Ошибка управления загрузкой: {e}")
    
    def remove_last_download(self):
        """Удаляет последнюю загрузку"""
        try:
            downloads = self.aria2_client.get_all_downloads()
            if not downloads:
                self.log("❌ Нет загрузок для удаления")
                return
            
            # Берем последнюю загрузку
            last_download = downloads[0]
            gid = last_download.get("gid")
            filename = "unknown"
            files = last_download.get("files", [])
            if files:
                filename = os.path.basename(files[0].get("path", "unknown"))
            
            # Подтверждение удаления
            from tkinter import messagebox
            if messagebox.askyesno("Подтверждение", 
                                 f"Удалить загрузку?\n{filename}\n\nЭто остановит загрузку, но файл останется."):
                self.aria2_client.remove_download(gid)
                self.log(f"🗑️ Удалена загрузка: {filename} ({gid[:8]})")
            else:
                self.log("❌ Удаление отменено")
                
        except Exception as e:
            self.log(f"❌ Ошибка удаления загрузки: {e}")
    
    def open_downloads_folder(self):
        """Открывает папку загрузок"""
        try:
            downloads_folder = os.path.expanduser("~/Загрузки")
            os.system(f'xdg-open "{downloads_folder}"')
            self.log(f"📁 Открыта папка: {downloads_folder}")
        except Exception as e:
            self.log(f"❌ Ошибка открытия папки: {e}")
    
    def delete_last_file(self):
        """Удаляет файл последней загрузки"""
        try:
            downloads = self.aria2_client.get_all_downloads()
            if not downloads:
                self.log("❌ Нет загрузок")
                return
            
            # Берем последнюю завершенную загрузку
            last_download = None
            for download in downloads:
                if download.get("status") == "complete":
                    last_download = download
                    break
            
            if not last_download:
                self.log("❌ Нет завершенных загрузок для удаления файла")
                return
            
            files = last_download.get("files", [])
            if not files:
                self.log("❌ Файл не найден")
                return
                
            file_path = files[0].get("path", "")
            if not file_path or not os.path.exists(file_path):
                self.log("❌ Файл не существует")
                return
            
            filename = os.path.basename(file_path)
            gid = last_download.get("gid", "")
            
            # Подтверждение удаления файла
            from tkinter import messagebox
            if messagebox.askyesno("Подтверждение", 
                                 f"Удалить файл с диска?\n{filename}\n\n⚠️ ВНИМАНИЕ: Файл будет удален навсегда!"):
                
                # Сначала удаляем загрузку из aria2
                self.aria2_client.remove_download(gid)
                
                # Затем удаляем файл
                os.remove(file_path)
                self.log(f"🔥 Удален файл: {filename}")
                self.log(f"📁 Путь: {file_path}")
            else:
                self.log("❌ Удаление файла отменено")
                
        except Exception as e:
            self.log(f"❌ Ошибка удаления файла: {e}")
            import traceback
            self.log(f"Детали: {traceback.format_exc()}")
    
    def start_auto_refresh(self):
        """Запускает автоматическое обновление прогресса"""
        self.auto_refresh_active = True
        self.schedule_refresh()
    
    def schedule_refresh(self):
        """Планирует следующее обновление"""
        if hasattr(self, 'auto_refresh_active') and self.auto_refresh_active:
            self.refresh_downloads()
            # Планируем следующее обновление через 2 секунды
            self.root.after(2000, self.schedule_refresh)
    
    def stop_auto_refresh(self):
        """Останавливает автоматическое обновление"""
        self.auto_refresh_active = False
    
    def toggle_auto_refresh(self):
        """Переключает автоматическое обновление"""
        if self.auto_refresh_var.get():
            self.log("🔄 Автоматическое обновление включено")
            self.start_auto_refresh()
        else:
            self.log("⏸️ Автоматическое обновление выключено")
            self.stop_auto_refresh()
    
    def run(self):
        """Запуск приложения"""
        self.log("Запуск GUI...")
        try:
            self.root.mainloop()
        except Exception as e:
            self.log(f"❌ Ошибка GUI: {e}")


def main():
    """Главная функция"""
    app = DebugDownloadGUI()
    app.run()


if __name__ == "__main__":
    main()