#!/usr/bin/env python3

import os
import subprocess

print("=== ТЕСТ ARIA2 ===")
print(f"PATH: {os.environ.get('PATH')}")

# Проверяем основные пути
paths = ["aria2c", "/usr/bin/aria2c"]

for path in paths:
    print(f"\nТестирую: {path}")
    try:
        result = subprocess.run([path, "--version"], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"✅ {path} работает!")
            print(f"Версия: {result.stdout.split()[2]}")
        else:
            print(f"❌ Ошибка: {result.stderr}")
    except Exception as e:
        print(f"❌ Исключение: {e}")

print("\nПроверка завершена.")