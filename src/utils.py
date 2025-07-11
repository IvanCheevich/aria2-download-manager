"""
Утилитные функции для форматирования данных
"""

def format_size(bytes_size: int) -> str:
    """Форматирует размер в байтах в человекочитаемый формат"""
    if bytes_size == 0:
        return "0 B"
    
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(bytes_size)
    unit_index = 0
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    if unit_index == 0:
        return f"{int(size)} {units[unit_index]}"
    else:
        return f"{size:.1f} {units[unit_index]}"


def format_speed(bytes_per_second: int) -> str:
    """Форматирует скорость в байтах/сек в человекочитаемый формат"""
    return f"{format_size(bytes_per_second)}/s"


def format_time(seconds: float) -> str:
    """Форматирует время в секундах в человекочитаемый формат"""
    if seconds < 0:
        return "∞"
    
    seconds = int(seconds)
    
    if seconds < 60:
        return f"{seconds}с"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes}м {seconds % 60}с"
    elif seconds < 86400:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}ч {minutes}м"
    else:
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        return f"{days}д {hours}ч"


def is_aria2_installed() -> bool:
    """Проверяет, установлен ли aria2"""
    import subprocess
    import os
    
    # Проверяем несколько возможных путей к aria2c
    possible_paths = [
        "aria2c",  # в PATH
        "/usr/bin/aria2c",  # стандартное расположение
        "/usr/local/bin/aria2c",  # альтернативное расположение
    ]
    
    for path in possible_paths:
        try:
            result = subprocess.run([path, "--version"], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            continue
    
    return False


def get_default_download_dir() -> str:
    """Возвращает папку загрузок по умолчанию"""
    import os
    downloads_dir = os.path.expanduser("~/Downloads")
    if not os.path.exists(downloads_dir):
        os.makedirs(downloads_dir, exist_ok=True)
    return downloads_dir