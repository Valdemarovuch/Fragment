"""
Модуль для безпечного видалення файлів з затиранням метаданих
Реалізує DoD 5220.22-M стандарт
"""
import os
import random
import string
import logging
import time


class DeletionStats:
    """Статистика операції безпечного видалення"""
    def __init__(self):
        self.file_size = 0
        self.passes_completed = 0
        self.total_passes = 0
        self.processing_time = 0.0
        self.success = False


class SecureShredder:
    """Безпечне видалення файлів з багатопрохідним перезаписом"""
    
    def __init__(self, passes=3):
        """
        Ініціалізація SecureShredder
        
        Args:
            passes: Кількість проходів перезапису (за замовчуванням 3 = DoD стандарт)
        """
        self.passes = passes
        logging.info(f"SecureShredder ініціалізований з {passes} проходами")
    
    def _generate_random_name(self, length=10):
        """
        Генерує випадкове ім'я для затирання сліду в MFT
        
        Args:
            length: Довжина імені
            
        Returns:
            str: Випадкове ім'я з букв і цифр
        """
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(length))
    
    def _flush_data(self, f):
        """
        Примусовий запис з RAM на фізичний диск
        
        Args:
            f: Дескриптор відкритого файлу
        """
        try:
            f.flush()
            os.fsync(f.fileno())
        except Exception as e:
            logging.warning(f"Не вдалося примусово скинути дані: {e}")
    
    def shred_file(self, path):
        """
        Безпечне видалення файлу з багатопрохідним перезаписом
        
        Args:
            path: Шлях до файлу для видалення
            
        Returns:
            DeletionStats: Статистика операції
        """
        stats = DeletionStats()
        start_time = time.time()
        stats.total_passes = self.passes
        
        if not os.path.exists(path):
            logging.warning(f"Файл не знайдено: {path}")
            return stats
        
        try:
            stats.file_size = os.path.getsize(path)
            logging.info(f"Почато безпечне видалення: {path} ({stats.file_size} bytes)")
            
            with open(path, "rb+") as f:
                # ЕТАП 1: Багатопрохідний перезапис (Алгоритм DoD)
                for i in range(self.passes):
                    f.seek(0)
                    
                    if i == 0:
                        # Прохід 1: Всі нулі (0x00)
                        pattern = b'\x00'
                        pattern_name = "Нулі (0x00)"
                    elif i == 1:
                        # Прохід 2: Всі одиниці (0xFF)
                        pattern = b'\xFF'
                        pattern_name = "Одиниці (0xFF)"
                    else:
                        # Прохід 3+: Випадкові дані (найважливіший)
                        pattern = None
                        pattern_name = "Випадкові дані"
                    
                    # Записуємо блоками, щоб не забити RAM на великих файлах
                    written = 0
                    block_size = 1024 * 1024  # 1 MB
                    
                    while written < stats.file_size:
                        chunk = min(block_size, stats.file_size - written)
                        
                        if pattern:
                            data = pattern * chunk
                        else:
                            data = os.urandom(chunk)
                        
                        f.write(data)
                        written += chunk
                    
                    self._flush_data(f)  # Примусовий скид на диск
                    stats.passes_completed += 1
                    logging.debug(f"Прохід {i+1}/{self.passes} завершено: {pattern_name}")
            
            # ЕТАП 2: Атака на метадані (MFT - Master File Table)
            # Перейменовуємо файл кілька разів, щоб затерти його ім'я в файловій таблиці
            directory = os.path.dirname(path) or '.'
            current_path = path
            
            logging.debug("Розпочато затирання метаданих (MFT)")
            for _ in range(3):
                try:
                    new_name = self._generate_random_name(random.randint(5, 15))
                    new_path = os.path.join(directory, new_name)
                    
                    # Перевіряємо, що новий шлях не існує
                    while os.path.exists(new_path):
                        new_name = self._generate_random_name(random.randint(5, 15))
                        new_path = os.path.join(directory, new_name)
                    
                    os.rename(current_path, new_path)
                    current_path = new_path
                    logging.debug(f"Ім'я змінено на: {new_name}")
                except Exception as e:
                    logging.warning(f"Не вдалося перейменувати файл: {e}")
                    break
            
            # ЕТАП 3: Фінальне видалення
            try:
                os.remove(current_path)
                stats.success = True
                logging.info(f"Файл успішно анігільовано: {path}")
            except Exception as e:
                logging.error(f"Помилка при фінальному видаленні: {e}")
        
        except PermissionError as e:
            logging.error(f"Відмовлено у доступі при видаленні: {path} - {e}")
        except IOError as e:
            logging.error(f"Помилка I/O при видаленні: {path} - {e}")
        except Exception as e:
            logging.error(f"Неочікувана помилка при видаленні: {path} - {e}")
        
        stats.processing_time = time.time() - start_time
        return stats
