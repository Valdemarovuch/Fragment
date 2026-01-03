"""
Конфігурація та константи для Fragment Corruptor
"""
import logging

# --- НАЛАШТУВАННЯ ЛОГУВАННЯ ---
def setup_logging():
    """Ініціалізація системи логування"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('fragment_corruptor.log'),
            logging.StreamHandler()
        ]
    )

class CorruptionMode:
    """Режими пошкодження файлів"""
    FULL = "Full Destruction (Header + Noise + Truncate)"
    HEADER_ONLY = "Header Overwrite Only"
    NOISE_ONLY = "Bit Flipping Only"
    TRUNCATE_ONLY = "Truncate Only"
    CUSTOM = "Custom"

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
    HEADER_TEXT = "PRISM CORRUPTOR"
    
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
