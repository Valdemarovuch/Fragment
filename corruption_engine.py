import os
import random
import logging
import time

class CorruptionStats:
    """Статистика операції пошкодження"""
    def __init__(self):
        self.original_size = 0
        self.corrupted_size = 0
        self.bytes_changed = 0
        self.header_bytes = 0
        self.noise_bytes = 0
        self.truncated_bytes = 0
        self.processing_time = 0.0

class CorruptionEngine:
    """Двигун для пошкодження файлів"""
    
    def __init__(self, mode, custom_params=None):
        """
        Ініціалізація двигуна пошкодження
        
        Args:
            mode: Режим пошкодження (з CorruptionMode)
            custom_params: Словник з кастомними параметрами
        """
        self.mode = mode
        self.custom_params = custom_params or {}
        
    def corrupt_file(self, file_path):
        """
        Застосування вибраного режиму пошкодження до файлу
        
        Args:
            file_path: Шлях до файлу для пошкодження
            
        Returns:
            CorruptionStats: Статистика операції
        """
        from config import CorruptionMode
        
        stats = CorruptionStats()
        start_time = time.time()
        
        stats.original_size = os.path.getsize(file_path)
        
        with open(file_path, "rb+") as f:
            if self.mode == CorruptionMode.FULL:
                self._corrupt_header(f, stats.original_size, stats=stats)
                self._corrupt_noise(f, stats.original_size, stats=stats)
                self._corrupt_truncate(f, stats.original_size, stats=stats)
                
            elif self.mode == CorruptionMode.HEADER_ONLY:
                self._corrupt_header(f, stats.original_size, stats=stats)
                
            elif self.mode == CorruptionMode.NOISE_ONLY:
                self._corrupt_noise(f, stats.original_size, stats=stats)
                
            elif self.mode == CorruptionMode.TRUNCATE_ONLY:
                self._corrupt_truncate(f, stats.original_size, stats=stats)
                
            elif self.mode == CorruptionMode.CUSTOM:
                header_bytes = self.custom_params.get('header_bytes', 16)
                noise_count = self.custom_params.get('noise_count', 5)
                truncate_bytes = self.custom_params.get('truncate_bytes', 30)
                
                self._corrupt_header(f, stats.original_size, header_bytes, stats)
                self._corrupt_noise(f, stats.original_size, noise_count, stats)
                self._corrupt_truncate(f, stats.original_size, 
                                      random.randint(truncate_bytes - 10, truncate_bytes + 10), stats)
        
        stats.corrupted_size = os.path.getsize(file_path)
        stats.bytes_changed = stats.header_bytes + stats.noise_bytes
        stats.processing_time = time.time() - start_time
        
        return stats
    
    def _corrupt_header(self, file_handle, file_size, bytes_count=16, stats=None):
        """
        Перезапис заголовка файлу випадковими даними
        
        Args:
            file_handle: Дескриптор відкритого файлу
            file_size: Розмір файлу
            bytes_count: Кількість байтів для перезапису
            stats: Об'єкт статистики для оновлення
        """
        if file_size < bytes_count:
            bytes_count = file_size
        file_handle.seek(0)
        file_handle.write(os.urandom(bytes_count))
        if stats:
            stats.header_bytes = bytes_count
        logging.debug(f"Header corrupted: {bytes_count} bytes")
    
    def _corrupt_noise(self, file_handle, file_size, noise_count=5, stats=None):
        """
        Інверсія випадкових байтів у файлі
        
        Args:
            file_handle: Дескриптор відкритого файлу
            file_size: Розмір файлу
            noise_count: Кількість байтів для інверсії
            stats: Об'єкт статистики для оновлення
        """
        if file_size > 50:
            actual_count = min(noise_count, file_size // 10)
            for _ in range(actual_count):
                pos = random.randint(20, file_size - 10)
                file_handle.seek(pos)
                byte = file_handle.read(1)
                if byte:
                    int_val = int.from_bytes(byte, "big")
                    inverted = int_val ^ 0xFF
                    file_handle.seek(pos)
                    file_handle.write(inverted.to_bytes(1, "big"))
            if stats:
                stats.noise_bytes = actual_count
            logging.debug(f"Noise added: {actual_count} bytes flipped")
    
    def _corrupt_truncate(self, file_handle, file_size, cut_bytes=None, stats=None):
        """
        Обрізання кінця файлу
        
        Args:
            file_handle: Дескриптор відкритого файлу
            file_size: Розмір файлу
            cut_bytes: Кількість байтів для відрізання (None = випадково)
            stats: Об'єкт статистики для оновлення
        """
        if file_size > 100:
            if cut_bytes is None:
                cut_bytes = random.randint(10, 50)
            cut_bytes = min(cut_bytes, file_size - 50)
            file_handle.truncate(file_size - cut_bytes)
            if stats:
                stats.truncated_bytes = cut_bytes
            logging.debug(f"File truncated: {cut_bytes} bytes removed")
