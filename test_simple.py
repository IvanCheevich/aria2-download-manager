#!/usr/bin/env python3

import sys
import os

# Добавляем путь к src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from aria2_client import Aria2Client
from utils import is_aria2_installed, format_size, format_speed


def test_aria2():
    """Тест работы aria2"""
    print("=== Тест Aria2 Download Manager ===\n")
    
    # Проверка установки aria2
    print("1. Проверка aria2...")
    if is_aria2_installed():
        print("✅ aria2 установлен")
    else:
        print("❌ aria2 не найден")
        return False
    
    # Создание клиента
    print("\n2. Создание клиента...")
    client = Aria2Client()
    
    # Запуск демона
    print("3. Запуск aria2 демона...")
    if client.start_aria2_daemon():
        print("✅ aria2 демон запущен")
    else:
        print("❌ Не удалось запустить aria2 демон")
        return False
    
    # Получение версии
    print("\n4. Проверка подключения...")
    result = client._make_request("getVersion")
    if "result" in result:
        version = result["result"]["version"]
        print(f"✅ Подключение успешно (aria2 {version})")
    else:
        print(f"❌ Ошибка подключения: {result.get('error', 'Unknown')}")
        return False
    
    # Получение статистики
    print("\n5. Получение статистики...")
    stats = client.get_global_stats()
    if stats:
        print(f"✅ Статистика получена:")
        print(f"   Активных загрузок: {stats.get('numActive', 0)}")
        print(f"   Ожидающих: {stats.get('numWaiting', 0)}")
        print(f"   Скорость загрузки: {format_speed(int(stats.get('downloadSpeed', 0)))}")
    
    # Получение списка загрузок
    print("\n6. Получение списка загрузок...")
    downloads = client.get_all_downloads()
    print(f"✅ Найдено загрузок: {len(downloads)}")
    
    if downloads:
        print("\nТекущие загрузки:")
        for download in downloads[:5]:  # Показываем первые 5
            filename = os.path.basename(download.get("files", [{}])[0].get("path", "Unknown"))
            status = download.get("status", "unknown")
            completed = int(download.get("completedLength", 0))
            total = int(download.get("totalLength", 0))
            
            if total > 0:
                progress = (completed / total) * 100
                print(f"  📁 {filename} - {status} ({progress:.1f}%)")
            else:
                print(f"  📁 {filename} - {status}")
    
    print("\n✅ Все тесты пройдены успешно!")
    return True


def test_simple_gui():
    """Тест простого GUI"""
    print("\n=== Тест Simple GUI ===\n")
    
    try:
        import tkinter
        print("✅ tkinter доступен")
        
        # Попробуем запустить простой GUI
        print("\nЗапуск простого GUI...")
        print("Закройте окно для продолжения тестов...")
        
        from simple_gui import SimpleDownloadGUI
        app = SimpleDownloadGUI()
        app.run()
        
        return True
        
    except ImportError as e:
        print(f"❌ tkinter не доступен: {e}")
        return False
    except Exception as e:
        print(f"❌ Ошибка GUI: {e}")
        return False


def main():
    """Главная функция тестирования"""
    print("Aria2 Download Manager - Тест компонентов\n")
    
    success = True
    
    # Тест aria2
    if not test_aria2():
        success = False
    
    # Тест GUI (опционально)
    print("\n" + "="*50)
    choice = input("\nЗапустить тест GUI? (y/N): ").lower().strip()
    if choice in ['y', 'yes', 'да']:
        if not test_simple_gui():
            success = False
    
    print("\n" + "="*50)
    if success:
        print("🎉 Все тесты прошли успешно!")
        print("\nДля запуска простого GUI используйте:")
        print("python3 src/simple_gui.py")
        print("\nИли запустите напрямую:")
        print("./aria2-download-manager")
    else:
        print("❌ Некоторые тесты не прошли")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())