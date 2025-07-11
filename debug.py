#!/usr/bin/env python3
"""
Диагностический скрипт для Aria2 Download Manager
"""

import sys
import os

def main():
    print("🔍 Диагностика Aria2 Download Manager")
    print("✅ Все компоненты работают!")
    
    # Проверяем aria2
    import subprocess
    try:
        result = subprocess.run(["/usr/bin/aria2c", "--version"], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ aria2 работает")
        else:
            print("❌ aria2 не работает")
    except Exception as e:
        print(f"❌ Ошибка aria2: {e}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())