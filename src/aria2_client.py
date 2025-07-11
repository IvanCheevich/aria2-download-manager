import json
import requests
import subprocess
import time
import threading
from typing import Dict, List, Optional, Callable, Any
import os
import signal


class Aria2Client:
    """Клиент для взаимодействия с aria2 через JSON-RPC"""
    
    def __init__(self, host: str = "http://localhost", port: int = 6800, secret: str = "test123"):
        self.host = host
        self.port = port
        self.secret = secret
        self.base_url = f"{host}:{port}/jsonrpc"
        self.aria2_process = None
        self.callbacks: Dict[str, List[Callable]] = {}
        
    def start_aria2_daemon(self) -> bool:
        """Запускает aria2c демон если он не запущен"""
        # Сначала останавливаем любые запущенные процессы aria2c
        self._kill_existing_aria2()
        
        try:
            # Проверяем, запущен ли уже рабочий aria2 с токеном
            test_payload = {
                "jsonrpc": "2.0", 
                "id": "test", 
                "method": "aria2.getVersion",
                "params": [f"token:{self.secret}"] if self.secret else []
            }
            response = requests.post(
                self.base_url,
                json=test_payload,
                timeout=2
            )
            if response.status_code == 200:
                result = response.json()
                if "result" in result:
                    print("aria2 уже запущен и работает")
                    return True
        except requests.exceptions.RequestException:
            pass
        
        # Ищем aria2c - сначала в абсолютных путях
        aria2_path = None
        
        # Список путей для поиска (начинаем с абсолютных путей)
        search_paths = [
            "/usr/bin/aria2c",
            "/usr/local/bin/aria2c", 
            "/bin/aria2c",
            "aria2c"  # в PATH последним
        ]
        
        for path in search_paths:
            try:
                if path.startswith("/"):
                    # Абсолютный путь - проверяем существование и исполняемость
                    if os.path.exists(path) and os.access(path, os.X_OK):
                        # Тестируем запуск
                        test_result = subprocess.run([path, "--version"], 
                                                   capture_output=True, timeout=2)
                        if test_result.returncode == 0:
                            aria2_path = path
                            break
                else:
                    # Относительный путь - используем which
                    import shutil
                    which_result = shutil.which(path)
                    if which_result:
                        test_result = subprocess.run([which_result, "--version"], 
                                                   capture_output=True, timeout=2)
                        if test_result.returncode == 0:
                            aria2_path = which_result
                            break
            except (subprocess.TimeoutExpired, OSError, FileNotFoundError):
                continue
        
        if not aria2_path:
            print("Ошибка: aria2c не найден ни в одном из путей")
            print(f"Проверенные пути: {search_paths}")
            return False
        
        print(f"Найден aria2c: {aria2_path}")
        
        # Запускаем aria2c
        try:
            cmd = [
                aria2_path,
                "--enable-rpc",
                f"--rpc-listen-port={self.port}",
                "--rpc-allow-origin-all",
                "--rpc-listen-all",
                f"--rpc-secret={self.secret}",
                "--daemon=true",
                "--continue=true",
                "--max-connection-per-server=16",
                "--min-split-size=1M",
                "--split=16"
            ]
            
            print(f"Запуск команды: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                print(f"Ошибка запуска aria2: {result.stderr}")
                return False
                
            # Ждем запуска
            for i in range(15):  # Увеличиваем время ожидания
                try:
                    test_payload = {
                        "jsonrpc": "2.0", 
                        "id": "test", 
                        "method": "aria2.getVersion",
                        "params": [f"token:{self.secret}"] if self.secret else []
                    }
                    response = requests.post(
                        self.base_url,
                        json=test_payload,
                        timeout=2
                    )
                    if response.status_code == 200:
                        print("aria2 демон успешно запущен")
                        return True
                except requests.exceptions.RequestException:
                    time.sleep(0.5)
            
            print("Тайм-аут подключения к aria2")
            return False
            
        except Exception as e:
            print(f"Ошибка запуска aria2: {e}")
            return False
    
    def _kill_existing_aria2(self):
        """Останавливает все запущенные процессы aria2c"""
        try:
            import subprocess
            # Находим и убиваем все процессы aria2c
            subprocess.run(["killall", "aria2c"], 
                         capture_output=True, timeout=5)
            time.sleep(1)  # Даем время процессам остановиться
        except Exception:
            pass  # Игнорируем ошибки если процессы не найдены
    
    def _make_request(self, method: str, params: Optional[List[Any]] = None) -> Dict:
        """Выполняет JSON-RPC запрос к aria2"""
        if params is None:
            params = []
            
        if self.secret:
            params.insert(0, f"token:{self.secret}")
        
        payload = {
            "jsonrpc": "2.0",
            "id": str(time.time()),
            "method": f"aria2.{method}",
            "params": params
        }
        
        try:
            response = requests.post(self.base_url, json=payload, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def add_download(self, url: str, options: Optional[Dict] = None) -> Optional[str]:
        """Добавляет новую загрузку по URL"""
        params = [[url]]  # URL должен быть в массиве
        if options:
            params.append(options)
        
        result = self._make_request("addUri", params)
        if "result" in result:
            return result["result"]
        return None
    
    def add_torrent(self, torrent_path: str, options: Optional[Dict] = None) -> Optional[str]:
        """Добавляет новую загрузку из торрент файла"""
        import base64
        
        try:
            # Читаем торрент файл и кодируем в base64
            with open(torrent_path, 'rb') as f:
                torrent_data = base64.b64encode(f.read()).decode('utf-8')
            
            # Правильный формат: aria2.addTorrent([secret], torrent, [uris], [options])
            params = [torrent_data, []]  # Пустой массив URIs обязателен
            if options:
                params.append(options)
            
            result = self._make_request("addTorrent", params)
            
            if "result" in result:
                return result["result"]
            elif "error" in result:
                print(f"Ошибка aria2 при добавлении торрента: {result['error']}")
                return None
            else:
                return None
        except Exception as e:
            print(f"Ошибка добавления торрента: {e}")
            return None
    
    def pause_download(self, gid: str) -> bool:
        """Ставит загрузку на паузу"""
        result = self._make_request("pause", [gid])
        return "result" in result
    
    def unpause_download(self, gid: str) -> bool:
        """Возобновляет загрузку"""
        result = self._make_request("unpause", [gid])
        return "result" in result
    
    def remove_download(self, gid: str) -> bool:
        """Удаляет загрузку"""
        result = self._make_request("remove", [gid])
        return "result" in result
    
    def get_download_status(self, gid: str) -> Dict:
        """Получает статус загрузки"""
        result = self._make_request("tellStatus", [gid])
        if "result" in result:
            return result["result"]
        return {}
    
    def get_all_downloads(self) -> List[Dict]:
        """Получает список всех загрузок"""
        active = self._make_request("tellActive")
        waiting = self._make_request("tellWaiting", [0, 100])
        stopped = self._make_request("tellStopped", [0, 100])
        
        downloads = []
        for response in [active, waiting, stopped]:
            if "result" in response:
                downloads.extend(response["result"])
        
        return downloads
    
    def get_global_stats(self) -> Dict:
        """Получает глобальную статистику"""
        result = self._make_request("getGlobalStat")
        if "result" in result:
            return result["result"]
        return {}
    
    def shutdown(self) -> bool:
        """Завершает работу aria2"""
        result = self._make_request("shutdown")
        return "result" in result
    
    def register_callback(self, event: str, callback: Callable):
        """Регистрирует callback для событий"""
        if event not in self.callbacks:
            self.callbacks[event] = []
        self.callbacks[event].append(callback)
    
    def start_monitoring(self):
        """Запускает мониторинг загрузок в отдельном потоке"""
        def monitor():
            while True:
                try:
                    downloads = self.get_all_downloads()
                    for callback in self.callbacks.get("downloads_updated", []):
                        callback(downloads)
                    time.sleep(1)
                except Exception as e:
                    print(f"Ошибка мониторинга: {e}")
                    time.sleep(5)
        
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()