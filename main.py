"""
Fragment Corruptor - Утиліта для пошкодження файлів
Головний файл запуску додатку
"""
import customtkinter as ctk

from config import AppConfig, setup_logging
from gui import FileBreakerApp


def main():
    """Точка входу в програму"""
    # Налаштування логування
    setup_logging()
    
    # Налаштування теми
    ctk.set_appearance_mode(AppConfig.APPEARANCE_MODE)
    ctk.set_default_color_theme(AppConfig.COLOR_THEME)
    
    # Запуск додатку
    app = FileBreakerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
