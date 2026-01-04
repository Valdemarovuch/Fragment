"""
Тестовий скрипт для демонстрації функціональності Fragment
Показує як corruption, так і secure delete режими
"""
import os
import sys
import tempfile
import logging
from pathlib import Path

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def create_test_file(path, content=b"Test File Content"):
    """Створює тестовий файл"""
    with open(path, 'wb') as f:
        f.write(content)
    logging.info(f"Створено тестовий файл: {path}")

def test_corruption():
    """Демонстрація режиму corruption"""
    logging.info("\n" + "="*60)
    logging.info("ТЕСТ 1: CORRUPTION (Пошкодження файлу)")
    logging.info("="*60)
    
    from corruption_engine import CorruptionEngine, CorruptionMode
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as f:
        test_file = f.name
    
    create_test_file(test_file, b"Secret Data That Will Be Corrupted!" * 100)
    
    original_size = os.path.getsize(test_file)
    logging.info(f"Розмір оригіналу: {original_size} байт")
    
    # Тест 1: Full Destruction
    logging.info("\n--- Тест 1: FULL Destruction ---")
    engine = CorruptionEngine(CorruptionMode.FULL)
    stats = engine.corrupt_file(test_file)
    
    logging.info(f"Header bytes corrupted: {stats.header_bytes}")
    logging.info(f"Noise bytes flipped: {stats.noise_bytes}")
    logging.info(f"Truncated bytes: {stats.truncated_bytes}")
    logging.info(f"Processing time: {stats.processing_time:.4f}s")
    
    corrupted_size = os.path.getsize(test_file)
    logging.info(f"Розмір після corruption: {corrupted_size} байт")
    logging.info(f"Змінено: {stats.bytes_changed} байт")
    
    os.remove(test_file)
    logging.info("✓ Тест corruption завершено успішно\n")

def test_secure_delete():
    """Демонстрація режиму secure delete"""
    logging.info("="*60)
    logging.info("ТЕСТ 2: SECURE DELETE (Безпечне видалення)")
    logging.info("="*60)
    
    from secure_delete import SecureShredder
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as f:
        test_file = f.name
    
    sensitive_data = b"CONFIDENTIAL: Password=secret123 SSN=123-45-6789" * 50
    create_test_file(test_file, sensitive_data)
    
    original_size = os.path.getsize(test_file)
    logging.info(f"Розмір файлу для видалення: {original_size} байт")
    
    # Тест з 1 проходом (Quick)
    logging.info("\n--- Тест 1: Quick (1 прохід) ---")
    shredder = SecureShredder(passes=1)
    stats = shredder.shred_file(test_file)
    
    if stats.success:
        logging.info(f"✓ Файл успішно видалений")
        logging.info(f"  Проходів завершено: {stats.passes_completed}")
        logging.info(f"  Час обробки: {stats.processing_time:.4f}s")
        logging.info(f"  Дані затерти: {stats.file_size} байт")
    else:
        logging.error("✗ Помилка при видаленні")
    
    # Перевірка, що файл видалено
    if not os.path.exists(test_file):
        logging.info("✓ Файл повністю видалено з диска")
    else:
        logging.error("✗ Файл все ще існує!")
    
    # Тест з 3 проходами (Standard DoD)
    logging.info("\n--- Тест 2: Standard DoD (3 проходи) ---")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as f:
        test_file2 = f.name
    
    create_test_file(test_file2, b"Business Secret Data" * 200)
    
    shredder = SecureShredder(passes=3)
    stats = shredder.shred_file(test_file2)
    
    if stats.success:
        logging.info(f"✓ Файл успішно видалений за DoD стандартом")
        logging.info(f"  Проходи: 0x00 (нулі) → 0xFF (одиниці) → Випадок")
        logging.info(f"  Час обробки: {stats.processing_time:.4f}s")
    
    if not os.path.exists(test_file2):
        logging.info("✓ Тест DoD режиму завершено успішно\n")
    
    logging.info("✓ Тест secure delete завершено успішно\n")

def test_metadata_preservation():
    """Демонстрація збереження метаданих у corruption режимі"""
    logging.info("="*60)
    logging.info("ТЕСТ 3: Збереження метаданих при Corruption")
    logging.info("="*60)
    
    import stat
    import time
    from datetime import datetime, timedelta
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as f:
        original_file = f.name
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as f:
        corrupted_file = f.name
    
    # Створюємо оригінальний файл з встановленими метаданими
    create_test_file(original_file, b"Original content with specific metadata")
    
    # Встановлюємо часи створення на 30 днів назад
    past_time = time.time() - (30 * 24 * 3600)
    os.utime(original_file, (past_time, past_time))
    
    logging.info(f"Оригінальний файл створено: {datetime.fromtimestamp(past_time)}")
    
    # Копіюємо та пошкоджуємо
    import shutil
    shutil.copy2(original_file, corrupted_file)
    
    from corruption_engine import CorruptionEngine, CorruptionMode
    engine = CorruptionEngine(CorruptionMode.FULL)
    engine.corrupt_file(corrupted_file)
    
    # Перевіряємо метадані
    orig_stat = os.stat(original_file)
    corr_stat = os.stat(corrupted_file)
    
    orig_time = datetime.fromtimestamp(orig_stat.st_mtime)
    corr_time = datetime.fromtimestamp(corr_stat.st_mtime)
    
    logging.info(f"Пошкоджений файл: {corr_time}")
    
    # Перевіряємо, чи часи однакові (або близькі)
    time_diff = abs(orig_stat.st_mtime - corr_stat.st_mtime)
    
    if time_diff < 2:  # Дозволяємо 2 секунди різниці
        logging.info("✓ Метадані успішно збережені (часи однакові)")
    else:
        logging.warning(f"⚠ Часи розрізняються на {time_diff} секунд")
    
    os.remove(original_file)
    os.remove(corrupted_file)
    
    logging.info("✓ Тест метаданих завершено\n")

def main():
    """Запуск всіх тестів"""
    logging.info("\n" + "="*60)
    logging.info("ФРАГМЕНТ ТЕСТУВАННЯ")
    logging.info("="*60 + "\n")
    
    try:
        test_corruption()
        test_secure_delete()
        test_metadata_preservation()
        
        logging.info("="*60)
        logging.info("✅ ВСІ ТЕСТИ ЗАВЕРШЕНО УСПІШНО!")
        logging.info("="*60)
        
    except Exception as e:
        logging.error(f"❌ Помилка під час тестування: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
