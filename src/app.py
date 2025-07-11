#!/usr/bin/env python3

import sys
import os

# Добавляем путь к модулям  
sys.path.insert(0, os.path.dirname(__file__))

# Пытаемся запустить GTK версию, если не получается - простую версию
try:
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk, Gio, GLib
    
    from main_window import MainWindow
    from utils import is_aria2_installed
    
    class Aria2DownloadManagerApp(Gtk.Application):
        """Главное приложение"""
        
        def __init__(self):
            super().__init__(
                application_id='com.aria2.downloadmanager',
                flags=Gio.ApplicationFlags.FLAGS_NONE
            )
            
        def do_activate(self):
            """Активация приложения"""
            # Проверяем, установлен ли aria2
            if not is_aria2_installed():
                self.show_aria2_not_found_dialog()
                return
                
            # Создаем главное окно
            window = MainWindow(self)
            window.show_all()
            window.present()
            
        def show_aria2_not_found_dialog(self):
            """Показывает диалог об отсутствии aria2"""
            dialog = Gtk.MessageDialog(
                transient_for=None,
                flags=0,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text="aria2 не найден"
            )
            dialog.format_secondary_text(
                "Для работы приложения необходимо установить aria2.\n\n"
                "Ubuntu/Debian: sudo apt install aria2\n"
                "Fedora: sudo dnf install aria2\n"
                "Arch: sudo pacman -S aria2"
            )
            dialog.run()
            dialog.destroy()
            self.quit()
    
    def main():
        """Главная функция GTK версии"""
        app = Aria2DownloadManagerApp()
        return app.run(sys.argv)

except ImportError:
    # GTK не доступен, используем простую версию
    print("GTK не найден, запускаем простую версию...")
    from simple_gui import main

if __name__ == "__main__":
    sys.exit(main())