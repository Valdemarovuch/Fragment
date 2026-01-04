"""
Конфігурація та константи для Fragment Corruptor
"""
import logging

# --- НАЛАШТУВАННЯ ЛОГУВАННЯ ---
def setup_logging():
    """Ініціалізація системи логування"""
    logging.basicConfig(
        level=logging.DEBUG,  # Змінено на DEBUG для детального логування
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('fragment_corruptor.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

class OperationMode:
    """Основний режим операції"""
    CORRUPT = "Corrupt Files"
    SECURE_DELETE = "Secure Delete"


class CorruptionMode:
    """Режими пошкодження файлів"""
    FULL = "Full Destruction (Header + Noise + Truncate)"
    HEADER_ONLY = "Header Overwrite Only"
    NOISE_ONLY = "Bit Flipping Only"
    TRUNCATE_ONLY = "Truncate Only"
    CUSTOM = "Custom"


class DeletionMode:
    """Режими безпечного видалення"""
    STANDARD = "Standard (3 passes - DoD)"
    EXTENDED = "Extended (7 passes - Gutmann)"
    QUICK = "Quick (1 pass)"

class AppConfig:
    """Налаштування додатку"""
    WINDOW_TITLE = "FRAGMENT - File Corruption Utility"
    WINDOW_WIDTH = 900
    WINDOW_HEIGHT = 700
    WINDOW_MIN_WIDTH = 700
    WINDOW_MIN_HEIGHT = 550
    
    # Теми
    APPEARANCE_MODE = "Dark"
    COLOR_THEME = "dark-blue"
    
    # Налаштування UI
    HEADER_TEXT = "FRAGMENT"
    
    # Кольори статусів
    COLOR_READY = "cyan"
    COLOR_PROCESSING = "yellow"
    COLOR_SUCCESS = "#00ff00"
    COLOR_ERROR = "#ff5555"
    COLOR_WARNING = "orange"

class NamingPattern:
    """Шаблони для назв файлів"""
    SAME = "Same as original"
    NUMBERED = "file (1).ext"
    PREFIX = "[BROKEN] file.ext"
    SUFFIX = "file [BROKEN].ext"
    TIMESTAMP = "file_20260103_153045.ext"
    CUSTOM = "Custom"
