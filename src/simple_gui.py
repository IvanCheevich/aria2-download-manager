#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
import os
from aria2_client import Aria2Client
from utils import format_size, format_speed, format_time


class SimpleDownloadGUI:
    """Простой GUI на tkinter для тестирования aria2"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Aria2 Download Manager (Simple)")
        self.root.geometry("800x600")
        
        # Инициализация aria2 клиента
        self.aria2_client = Aria2Client()
        if not self.aria2_client.start_aria2_daemon():
            messagebox.showerror("Ошибка", "Не удалось запустить aria2. Убедитесь, что aria2 установлен.")
            self.root.destroy()
            return
        
        self.downloads = {}
        self.setup_ui()
        self.setup_monitoring()
        
    def setup_ui(self):
        """Настройка интерфейса"""
        # Главный фрейм
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Панель управления
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Кнопки добавления
        ttk.Button(control_frame, text="➕ Добавить URL", 
                  command=lambda: self.add_download_dialog("url")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="🧲 Добавить торрент", 
                  command=lambda: self.add_download_dialog("torrent")).pack(side=tk.LEFT, padx=(0, 10))
        
        # Кнопка обновления
        ttk.Button(control_frame, text="🔄 Обновить", 
                  command=self.refresh_downloads).pack(side=tk.LEFT)
        
        # Список загрузок
        columns = ('file', 'status', 'progress', 'speed', 'size')
        self.tree = ttk.Treeview(main_frame, columns=columns, show='headings', height=15)
        
        # Заголовки
        self.tree.heading('file', text='Файл')
        self.tree.heading('status', text='Статус')
        self.tree.heading('progress', text='Прогресс')
        self.tree.heading('speed', text='Скорость')
        self.tree.heading('size', text='Размер')
        
        # Ширина колонок
        self.tree.column('file', width=300)
        self.tree.column('status', width=100)
        self.tree.column('progress', width=100)
        self.tree.column('speed', width=100)
        self.tree.column('size', width=150)
        
        # Скроллбар
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Размещение
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Контекстное меню
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="⏸️ Пауза/Возобновить", command=self.toggle_download)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="🗑️ Удалить загрузку", command=self.remove_download)
        self.context_menu.add_command(label="🔥 Удалить файл", command=self.delete_file)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="📁 Открыть папку", command=self.open_folder)
        
        self.tree.bind("<Button-3>", self.show_context_menu)
        
        # Статус бар
        self.status_label = ttk.Label(main_frame, text="Готов")
        self.status_label.pack(fill=tk.X, pady=(10, 0))
        
    def setup_monitoring(self):
        """Настройка мониторинга"""
        self.aria2_client.register_callback("downloads_updated", self.on_downloads_updated)
        self.aria2_client.start_monitoring()
        # Первоначальное обновление
        self.refresh_downloads()
        
    def on_downloads_updated(self, downloads):
        """Обработчик обновления загрузок"""
        self.root.after(0, lambda: self.update_downloads_list(downloads))
        
    def update_downloads_list(self, downloads):
        """Обновление списка загрузок"""
        # Очистка дерева
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Добавление загрузок
        active_count = 0
        for download in downloads:
            gid = download.get("gid", "")
            filename = os.path.basename(download.get("files", [{}])[0].get("path", "Неизвестный файл"))
            status = download.get("status", "unknown")
            
            total_length = int(download.get("totalLength", 0))
            completed_length = int(download.get("completedLength", 0))
            download_speed = int(download.get("downloadSpeed", 0))
            
            # Прогресс
            if total_length > 0:
                progress = f"{(completed_length / total_length * 100):.1f}%"
            else:
                progress = "0%"
            
            # Скорость
            speed = format_speed(download_speed) if download_speed > 0 else "-"
            
            # Размер
            if total_length > 0:
                size_text = f"{format_size(completed_length)} / {format_size(total_length)}"
            else:
                size_text = format_size(completed_length)
            
            # Статус
            status_text = {
                "active": "Загружается",
                "paused": "Пауза", 
                "complete": "Завершено",
                "error": "Ошибка",
                "removed": "Удалено"
            }.get(status, status)
            
            if status == "active":
                active_count += 1
            
            # Добавление в дерево
            item = self.tree.insert('', tk.END, values=(filename, status_text, progress, speed, size_text))
            self.downloads[item] = download
        
        # Обновление статуса
        total_count = len(downloads)
        if total_count == 0:
            status_text = "Нет загрузок"
        else:
            status_text = f"Загрузок: {total_count}, активных: {active_count}"
        
        self.status_label.config(text=status_text)
        
    def add_download_dialog(self, default_type="url"):
        """Диалог добавления загрузки"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить загрузку")
        dialog.geometry("600x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Тип загрузки
        type_frame = ttk.LabelFrame(dialog, text="Тип загрузки")
        type_frame.pack(fill=tk.X, padx=10, pady=10)
        
        download_type = tk.StringVar(value=default_type)
        ttk.Radiobutton(type_frame, text="URL ссылка", variable=download_type, 
                       value="url").pack(anchor=tk.W, padx=10, pady=5)
        ttk.Radiobutton(type_frame, text="Торрент файл", variable=download_type, 
                       value="torrent").pack(anchor=tk.W, padx=10, pady=5)
        
        # URL фрейм
        url_frame = ttk.LabelFrame(dialog, text="URL ссылка")
        url_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        url_entry = ttk.Entry(url_frame, width=70)
        url_entry.pack(fill=tk.X, padx=10, pady=10)
        url_entry.focus()
        
        # Торрент фрейм
        torrent_frame = ttk.LabelFrame(dialog, text="Торрент файл")
        torrent_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        torrent_path_frame = ttk.Frame(torrent_frame)
        torrent_path_frame.pack(fill=tk.X, padx=10, pady=10)
        
        torrent_entry = ttk.Entry(torrent_path_frame, width=60)
        torrent_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        def browse_torrent():
            filename = filedialog.askopenfilename(
                title="Выберите торрент файл",
                initialdir=os.path.expanduser("~/Загрузки"),
                filetypes=[("Торрент файлы", "*.torrent"), ("Все файлы", "*.*")]
            )
            if filename:
                torrent_entry.delete(0, tk.END)
                torrent_entry.insert(0, filename)
        
        ttk.Button(torrent_path_frame, text="Обзор...", command=browse_torrent).pack(side=tk.RIGHT)
        
        # Папка загрузки
        folder_frame = ttk.LabelFrame(dialog, text="Папка для загрузки")
        folder_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        folder_path_frame = ttk.Frame(folder_frame)
        folder_path_frame.pack(fill=tk.X, padx=10, pady=10)
        
        folder_entry = ttk.Entry(folder_path_frame, width=60)
        folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        folder_entry.insert(0, os.path.expanduser("~/Загрузки"))
        
        def browse_folder():
            folder = filedialog.askdirectory(
                title="Выберите папку для загрузки",
                initialdir=os.path.expanduser("~/Загрузки")
            )
            if folder:
                folder_entry.delete(0, tk.END)
                folder_entry.insert(0, folder)
        
        ttk.Button(folder_path_frame, text="Обзор...", command=browse_folder).pack(side=tk.RIGHT)
        
        # Функция обновления интерфейса в зависимости от типа
        def update_interface():
            if download_type.get() == "url":
                url_frame.configure(relief=tk.RAISED)
                torrent_frame.configure(relief=tk.FLAT)
                url_entry.configure(state=tk.NORMAL)
                torrent_entry.configure(state=tk.DISABLED)
                url_entry.focus()
            else:
                url_frame.configure(relief=tk.FLAT)
                torrent_frame.configure(relief=tk.RAISED)
                url_entry.configure(state=tk.DISABLED)
                torrent_entry.configure(state=tk.NORMAL)
                torrent_entry.focus()
        
        # Привязка обновления интерфейса к радиокнопкам
        for widget in type_frame.winfo_children():
            if isinstance(widget, ttk.Radiobutton):
                widget.configure(command=update_interface)
        
        update_interface()  # Начальная настройка
        
        # Кнопки
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def on_ok():
            folder = folder_entry.get().strip()
            
            options = {}
            if folder:
                options["dir"] = folder
            
            if download_type.get() == "url":
                url = url_entry.get().strip()
                if not url:
                    messagebox.showerror("Ошибка", "Введите URL")
                    return
                
                gid = self.aria2_client.add_download(url, options)
            else:
                torrent_path = torrent_entry.get().strip()
                if not torrent_path:
                    messagebox.showerror("Ошибка", "Выберите торрент файл")
                    return
                
                if not os.path.exists(torrent_path):
                    messagebox.showerror("Ошибка", "Торрент файл не найден")
                    return
                
                gid = self.aria2_client.add_torrent(torrent_path, options)
            
            if gid:
                messagebox.showinfo("Успех", f"Загрузка добавлена: {gid}")
                dialog.destroy()
            else:
                messagebox.showerror("Ошибка", "Не удалось добавить загрузку")
        
        ttk.Button(button_frame, text="OK", command=on_ok).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Отмена", command=dialog.destroy).pack(side=tk.RIGHT)
        
        # Обработка Enter
        url_entry.bind('<Return>', lambda e: on_ok())
        torrent_entry.bind('<Return>', lambda e: on_ok())
        
    def show_context_menu(self, event):
        """Показ контекстного меню"""
        item = self.tree.selection()[0] if self.tree.selection() else None
        if item:
            self.context_menu.post(event.x_root, event.y_root)
    
    def toggle_download(self):
        """Пауза/возобновление загрузки"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = selection[0]
        download = self.downloads.get(item)
        if not download:
            return
        
        gid = download.get("gid")
        status = download.get("status")
        
        if status == "active":
            self.aria2_client.pause_download(gid)
        else:
            self.aria2_client.unpause_download(gid)
    
    def remove_download(self):
        """Удаление загрузки"""
        selection = self.tree.selection()
        if not selection:
            return
        
        if messagebox.askyesno("Подтверждение", "Удалить загрузку?"):
            item = selection[0]
            download = self.downloads.get(item)
            if download:
                gid = download.get("gid")
                self.aria2_client.remove_download(gid)
    
    def open_folder(self):
        """Открытие папки с файлом"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = selection[0]
        download = self.downloads.get(item)
        if not download:
            return
        
        file_path = download.get("files", [{}])[0].get("path", "")
        if file_path:
            folder_path = os.path.dirname(file_path)
            if os.path.exists(folder_path):
                os.system(f'xdg-open "{folder_path}"')
    
    def delete_file(self):
        """Удаление файла с диска"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = selection[0]
        download = self.downloads.get(item)
        if not download:
            return
        
        files = download.get("files", [])
        if not files:
            messagebox.showerror("Ошибка", "Файл не найден")
            return
            
        file_path = files[0].get("path", "")
        if not file_path or not os.path.exists(file_path):
            messagebox.showerror("Ошибка", "Файл не существует")
            return
        
        filename = os.path.basename(file_path)
        
        # Подтверждение удаления файла
        if messagebox.askyesno("Подтверждение", 
                             f"Удалить файл с диска?\n\n{filename}\n\n⚠️ ВНИМАНИЕ: Файл будет удален навсегда!"):
            try:
                # Сначала удаляем загрузку из aria2
                gid = download.get("gid")
                self.aria2_client.remove_download(gid)
                
                # Затем удаляем файл
                os.remove(file_path)
                messagebox.showinfo("Успех", f"Файл удален:\n{filename}")
                
                # Обновляем список
                self.refresh_downloads()
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить файл:\n{e}")
    
    def refresh_downloads(self):
        """Принудительное обновление списка"""
        downloads = self.aria2_client.get_all_downloads()
        self.update_downloads_list(downloads)
    
    def run(self):
        """Запуск приложения"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            pass
        finally:
            self.aria2_client.shutdown()


def main():
    """Главная функция"""
    app = SimpleDownloadGUI()
    app.run()


if __name__ == "__main__":
    main()