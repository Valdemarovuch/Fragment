"""
Графічний інтерфейс для Fragment Corruptor
"""
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import shutil
import threading
import logging
from datetime import datetime
import subprocess
import stat

from config import CorruptionMode, AppConfig, NamingPattern
from corruption_engine import CorruptionEngine


class FileBreakerApp(ctk.CTk):
    """Основний клас додатку"""
    
    def __init__(self):
        super().__init__()
        
        # Налаштування вікна
        self.title(AppConfig.WINDOW_TITLE)
        self.geometry(f"{AppConfig.WINDOW_WIDTH}x{AppConfig.WINDOW_HEIGHT}")
        self.minsize(AppConfig.WINDOW_MIN_WIDTH, AppConfig.WINDOW_MIN_HEIGHT)
        
        # Дані додатку
        self.selected_files = []
        self.file_rows = {}
        
        # Параметри
        self.corruption_mode = tk.StringVar(value=CorruptionMode.FULL)
        self.output_directory = tk.StringVar(value="")
        self.custom_header_bytes = tk.IntVar(value=16)
        self.custom_noise_count = tk.IntVar(value=5)
        self.custom_truncate_bytes = tk.IntVar(value=30)
        
        # Налаштування імен файлів
        self.naming_pattern = tk.StringVar(value=NamingPattern.SAME)
        self.custom_prefix = tk.StringVar(value="")
        self.custom_suffix = tk.StringVar(value="")
        
        # Статистика
        self.total_stats = {
            'total_files': 0,
            'total_bytes_changed': 0,
            'total_time': 0.0,
            'original_total_size': 0,
            'corrupted_total_size': 0
        }
        
        logging.info("Application started")
        
        # Побудова інтерфейсу
        self._build_ui()
    
    def _build_ui(self):
        """Побудова інтерфейсу користувача"""
        self._create_header()
        self._create_controls()
        self._create_file_list()
        self._create_footer()
    
    def _create_header(self):
        """Створення заголовку"""
        header_frame = ctk.CTkFrame(self, height=60, corner_radius=0, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 0))
        
        logo_label = ctk.CTkLabel(header_frame, text=AppConfig.HEADER_TEXT, 
                                 font=("Roboto Medium", 20))
        logo_label.pack(side="top")
    
    def _create_controls(self):
        """Створення панелі керування"""
        controls_frame = ctk.CTkFrame(self, height=50, corner_radius=0, fg_color="transparent")
        controls_frame.pack(fill="x", padx=20, pady=10)
        
        # Кнопки додавання
        btn_add = ctk.CTkButton(controls_frame, text="+ Add Files", width=120, height=35,
                               fg_color="white", text_color="black", hover_color="#e0e0e0",
                               command=self.add_files)
        btn_add.pack(side="left")
        
        btn_add_folder = ctk.CTkButton(controls_frame, text="+ Add Folder", width=120, height=35,
                                      fg_color="white", text_color="black", hover_color="#e0e0e0",
                                      command=self.add_folder)
        btn_add_folder.pack(side="left", padx=(10, 0))
        
        # Статус
        self.lbl_status = ctk.CTkLabel(controls_frame, text="0 files loaded", text_color="gray")
        self.lbl_status.pack(side="left", padx=20)
        
        # Кнопка очищення
        btn_clear = ctk.CTkButton(controls_frame, text="🗑 Clear All", width=80,
                                 fg_color="transparent", border_width=1, border_color="gray",
                                 text_color="gray", hover_color="#333333",
                                 command=self.clear_list)
        btn_clear.pack(side="right")
    
    def _create_file_list(self):
        """Створення списку файлів"""
        self.file_list_frame = ctk.CTkScrollableFrame(self, fg_color="#1a1a1a", corner_radius=10)
        self.file_list_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Заголовки таблиці
        self.list_header = ctk.CTkFrame(self.file_list_frame, height=30, fg_color="transparent")
        self.list_header.pack(fill="x", pady=(0, 5))
        
        ctk.CTkLabel(self.list_header, text="FILENAME", font=("Roboto", 12, "bold"),
                    text_color="gray", anchor="w").pack(side="left", padx=10, fill="x", expand=True)
        ctk.CTkLabel(self.list_header, text="SIZE", font=("Roboto", 12, "bold"),
                    text_color="gray", width=80).pack(side="left", padx=5)
        ctk.CTkLabel(self.list_header, text="STATUS", font=("Roboto", 12, "bold"),
                    text_color="gray", width=100).pack(side="left", padx=5)
        ctk.CTkLabel(self.list_header, text="", width=30).pack(side="right", padx=5)
    
    def _create_footer(self):
        """Створення підвалу з налаштуваннями"""
        footer_frame = ctk.CTkFrame(self, height=160, corner_radius=0, fg_color="#111111")
        footer_frame.pack(fill="x", side="bottom")
        
        # Прогрес-бар
        self.progress_bar = ctk.CTkProgressBar(footer_frame, height=3)
        self.progress_bar.pack(fill="x", side="top")
        self.progress_bar.set(0)
        
        footer_inner = ctk.CTkFrame(footer_frame, fg_color="transparent")
        footer_inner.pack(fill="both", expand=True, padx=20, pady=15)
        
        # Налаштування (ліва частина)
        settings_frame = ctk.CTkFrame(footer_inner, fg_color="transparent")
        settings_frame.pack(side="left", fill="both", expand=True)
        
        # Перший рядок - режим corruption
        ctk.CTkLabel(settings_frame, text="Corruption Mode:", text_color="gray",
                    font=("Roboto", 11)).pack(anchor="w")
        
        mode_menu = ctk.CTkOptionMenu(
            settings_frame,
            variable=self.corruption_mode,
            values=[CorruptionMode.FULL, CorruptionMode.HEADER_ONLY, 
                   CorruptionMode.NOISE_ONLY, CorruptionMode.TRUNCATE_ONLY, 
                   CorruptionMode.CUSTOM],
            width=300,
            command=self.on_mode_change
        )
        mode_menu.pack(anchor="w", pady=(5, 10))
        
        # Другий рядок - naming pattern
        naming_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        naming_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(naming_frame, text="File Naming:", text_color="gray",
                    font=("Roboto", 11)).pack(side="left")
        
        self.naming_menu = ctk.CTkOptionMenu(
            naming_frame,
            variable=self.naming_pattern,
            values=[NamingPattern.SAME, NamingPattern.NUMBERED, NamingPattern.PREFIX,
                   NamingPattern.SUFFIX, NamingPattern.TIMESTAMP, NamingPattern.CUSTOM],
            width=180,
            command=self.on_naming_change
        )
        self.naming_menu.pack(side="left", padx=(10, 5))
        
        # Поля для кастомних prefix/suffix
        self.prefix_entry = ctk.CTkEntry(naming_frame, placeholder_text="Prefix", width=80)
        self.suffix_entry = ctk.CTkEntry(naming_frame, placeholder_text="Suffix", width=80)
        
        # Третій рядок - вибір output папки
        output_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        output_frame.pack(fill="x")
        
        ctk.CTkLabel(output_frame, text="Output:", text_color="gray",
                    font=("Roboto", 11)).pack(side="left")
        self.lbl_output = ctk.CTkLabel(output_frame, text="Same as original",
                                      text_color="#00aaff", font=("Roboto", 10))
        self.lbl_output.pack(side="left", padx=(5, 10))
        
        btn_output = ctk.CTkButton(output_frame, text="Change", width=80, height=25,
                                  fg_color="transparent", border_width=1, border_color="gray",
                                  command=self.select_output_directory)
        btn_output.pack(side="left")
        
        # Кнопка запуску (права частина)
        self.btn_run = ctk.CTkButton(footer_inner, text="Corrupt All →", width=150, height=40,
                                     font=("Roboto Medium", 14),
                                     command=self.start_corruption_thread)
        self.btn_run.pack(side="right", anchor="e")
    
    # --- МЕТОДИ КЕРУВАННЯ ФАЙЛАМИ ---
    
    def add_files(self):
        """Додавання файлів через діалог"""
        files = filedialog.askopenfilenames(
            title="Select files to corrupt",
            filetypes=[("All Files", "*.*"), ("Word Documents", "*.docx"),
                      ("Images", "*.jpg *.png"), ("PDFs", "*.pdf")]
        )
        if files:
            for file_path in files:
                self.add_file_to_list(file_path)
    
    def add_folder(self):
        """Додавання всіх файлів з папки"""
        folder = filedialog.askdirectory(title="Select folder")
        if folder:
            added_count = 0
            for root, dirs, files in os.walk(folder):
                for file in files:
                    if not file.startswith('.'):
                        file_path = os.path.join(root, file)
                        if self.add_file_to_list(file_path):
                            added_count += 1
            logging.info(f"Added {added_count} files from folder: {folder}")
    
    def add_file_to_list(self, file_path):
        """Додавання одного файлу до списку"""
        if not os.path.exists(file_path):
            logging.warning(f"File does not exist: {file_path}")
            return False
        
        if file_path in self.selected_files:
            logging.debug(f"File already in list: {file_path}")
            return False
        
        if not os.access(file_path, os.R_OK):
            logging.warning(f"Cannot read file: {file_path}")
            messagebox.showwarning("Warning", f"Cannot read file:\n{os.path.basename(file_path)}")
            return False
        
        self.selected_files.append(file_path)
        self.create_file_row(file_path)
        self.update_status_label()
        return True
    
    def create_file_row(self, file_path):
        """Створення рядка файлу в списку"""
        filename = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        size_str = self.format_file_size(file_size)
        
        row_frame = ctk.CTkFrame(self.file_list_frame, height=40, fg_color="#2b2b2b", corner_radius=5)
        row_frame.pack(fill="x", pady=2)
        
        lbl_name = ctk.CTkLabel(row_frame, text=filename, anchor="w", padx=10)
        lbl_name.pack(side="left", fill="x", expand=True)
        
        lbl_size = ctk.CTkLabel(row_frame, text=size_str, text_color="gray", width=80)
        lbl_size.pack(side="left", padx=5)
        
        lbl_status = ctk.CTkLabel(row_frame, text="Ready", text_color=AppConfig.COLOR_READY, width=100)
        lbl_status.pack(side="left", padx=5)
        
        btn_remove = ctk.CTkButton(row_frame, text="×", width=30, height=30,
                                  fg_color="transparent", hover_color="#ff5555",
                                  command=lambda: self.remove_file(file_path))
        btn_remove.pack(side="right", padx=5)
        
        row_frame.status_label = lbl_status
        row_frame.file_path = file_path
        self.file_rows[file_path] = row_frame
    
    def remove_file(self, file_path):
        """Видалення файлу зі списку"""
        if file_path in self.selected_files:
            self.selected_files.remove(file_path)
        
        if file_path in self.file_rows:
            self.file_rows[file_path].destroy()
            del self.file_rows[file_path]
        
        self.update_status_label()
        logging.info(f"Removed file: {file_path}")
    
    def clear_list(self):
        """Очищення списку файлів"""
        self.selected_files = []
        self.file_rows = {}
        for widget in self.file_list_frame.winfo_children():
            if isinstance(widget, ctk.CTkFrame) and widget != self.list_header:
                widget.destroy()
        self.update_status_label()
        self.progress_bar.set(0)
        logging.info("Cleared all files")
    
    def update_status_label(self):
        """Оновлення лічильника файлів"""
        count = len(self.selected_files)
        self.lbl_status.configure(text=f"{count} file{'s' if count != 1 else ''} loaded")
    
    @staticmethod
    def format_file_size(size_bytes):
        """Форматування розміру файлу"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def select_output_directory(self):
        """Вибір вихідної директорії"""
        directory = filedialog.askdirectory(title="Select output directory")
        if directory:
            self.output_directory.set(directory)
            self.lbl_output.configure(text=os.path.basename(directory))
            logging.info(f"Output directory set to: {directory}")
        else:
            self.output_directory.set("")
            self.lbl_output.configure(text="Same as original")
    
    def on_mode_change(self, choice):
        """Обробка зміни режиму"""
        logging.info(f"Corruption mode changed to: {choice}")
    
    def on_naming_change(self, choice):
        """Обробка зміни шаблону імен"""
        # Показуємо/приховуємо поля для custom
        if choice == NamingPattern.CUSTOM:
            self.prefix_entry.pack(side="left", padx=2)
            self.suffix_entry.pack(side="left", padx=2)
        else:
            self.prefix_entry.pack_forget()
            self.suffix_entry.pack_forget()
        logging.info(f"Naming pattern changed to: {choice}")
    
    def generate_output_filename(self, original_path, directory):
        """
        Генерація імені вихідного файлу на основі обраного шаблону
        
        Args:
            original_path: Шлях до оригінального файлу
            directory: Директорія для збереження
            
        Returns:
            str: Повний шлях до нового файлу
        """
        filename = os.path.basename(original_path)
        name, ext = os.path.splitext(filename)
        pattern = self.naming_pattern.get()
        
        if pattern == NamingPattern.SAME:
            new_filename = filename
        elif pattern == NamingPattern.NUMBERED:
            new_filename = filename
        elif pattern == NamingPattern.PREFIX:
            new_filename = f"[BROKEN] {filename}"
        elif pattern == NamingPattern.SUFFIX:
            new_filename = f"{name} [BROKEN]{ext}"
        elif pattern == NamingPattern.TIMESTAMP:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_filename = f"{name}_{timestamp}{ext}"
        elif pattern == NamingPattern.CUSTOM:
            prefix = self.prefix_entry.get()
            suffix = self.suffix_entry.get()
            new_filename = f"{prefix}{name}{suffix}{ext}"
        else:
            new_filename = filename
        
        new_path = os.path.join(directory, new_filename)
        
        # Якщо файл існує і pattern не TIMESTAMP, додаємо номер
        if os.path.exists(new_path) and pattern != NamingPattern.TIMESTAMP:
            counter = 1
            while os.path.exists(new_path):
                if pattern == NamingPattern.CUSTOM:
                    prefix = self.prefix_entry.get()
                    suffix = self.suffix_entry.get()
                    new_filename = f"{prefix}{name} ({counter}){suffix}{ext}"
                else:
                    new_filename = f"{name} ({counter}){ext}"
                new_path = os.path.join(directory, new_filename)
                counter += 1
        
        return new_path
    
    def preserve_metadata(self, source_path, target_path):
        """
        Копіює ВСІ метадані з оригіналу на цільовий файл, включно з датою створення (macOS)
        
        Args:
            source_path: Шлях до оригінального файлу
            target_path: Шлях до цільового файлу
        """
        try:
            # Отримуємо stat оригіналу
            source_stat = os.stat(source_path)
            
            # Копіюємо права доступу
            os.chmod(target_path, stat.S_IMODE(source_stat.st_mode))
            
            # Копіюємо modification time та access time з наносекундною точністю
            os.utime(target_path, ns=(source_stat.st_atime_ns, source_stat.st_mtime_ns))
            
            # Для macOS - копіюємо також birthtime (дату створення) через SetFile
            if hasattr(source_stat, 'st_birthtime'):
                try:
                    # Конвертуємо timestamp у формат для touch
                    birthtime = datetime.fromtimestamp(source_stat.st_birthtime)
                    birthtime_str = birthtime.strftime("%Y%m%d%H%M.%S")
                    
                    # Використовуємо touch -t для встановлення birthtime
                    subprocess.run(['touch', '-t', birthtime_str, target_path], 
                                 check=False, capture_output=True)
                except Exception as e:
                    logging.debug(f"Could not set birthtime: {e}")
            
            logging.debug(f"Metadata preserved for {target_path}")
            
        except Exception as e:
            logging.warning(f"Failed to preserve some metadata: {e}")
    
    # --- ОБРОБКА ФАЙЛІВ ---
    
    def start_corruption_thread(self):
        """Запуск процесу пошкодження у окремому потоці"""
        if not self.selected_files:
            messagebox.showwarning("Warning", "No files added!")
            return
        
        self.btn_run.configure(state="disabled", text="Processing...")
        self.progress_bar.set(0)
        
        logging.info(f"Starting corruption process for {len(self.selected_files)} files")
        logging.info(f"Mode: {self.corruption_mode.get()}")
        
        threading.Thread(target=self.process_files, daemon=True).start()
    
    def process_files(self):
        """Обробка файлів (виконується в окремому потоці)"""
        total = len(self.selected_files)
        step = 1 / total if total > 0 else 0
        current_progress = 0
        
        success_count = 0
        error_count = 0
        
        # Скидання статистики
        self.total_stats = {
            'total_files': 0,
            'total_bytes_changed': 0,
            'total_time': 0.0,
            'original_total_size': 0,
            'corrupted_total_size': 0
        }
        
        # Створення corruption engine
        custom_params = {
            'header_bytes': self.custom_header_bytes.get(),
            'noise_count': self.custom_noise_count.get(),
            'truncate_bytes': self.custom_truncate_bytes.get()
        }
        engine = CorruptionEngine(self.corruption_mode.get(), custom_params)
        
        for file_path in self.selected_files:
            try:
                # Визначення шляху для нового файлу
                if self.output_directory.get():
                    directory = self.output_directory.get()
                else:
                    directory = os.path.dirname(file_path)
                
                # Генерація імені за шаблоном
                new_path = self.generate_output_filename(file_path, directory)
                
                # Оновлення статусу
                self.after(0, self.update_file_status, file_path, "Processing...", 
                          AppConfig.COLOR_PROCESSING)
                
                # Копіювання БЕЗ метаданих (просто байти)
                with open(file_path, 'rb') as src:
                    content = src.read()
                with open(new_path, 'wb') as dst:
                    dst.write(content)
                
                logging.info(f"Created copy: {new_path}")
                
                # Застосування пошкодження та збір статистики
                stats = engine.corrupt_file(new_path)
                
                # ПІСЛЯ corruption відновлюємо метадані з оригіналу
                self.preserve_metadata(file_path, new_path)
                
                # Оновлення загальної статистики
                self.total_stats['total_files'] += 1
                self.total_stats['total_bytes_changed'] += stats.bytes_changed
                self.total_stats['total_time'] += stats.processing_time
                self.total_stats['original_total_size'] += stats.original_size
                self.total_stats['corrupted_total_size'] += stats.corrupted_size
                
                success_count += 1
                
                # Детальна інформація у статусі
                status_text = f"✓ {stats.processing_time:.2f}s"
                self.after(0, self.update_file_status, file_path, status_text, 
                          AppConfig.COLOR_SUCCESS)
                
                logging.info(f"Successfully corrupted: {new_path} | "
                           f"Changed: {stats.bytes_changed}B | Time: {stats.processing_time:.3f}s")
            
            except PermissionError as e:
                error_count += 1
                self.after(0, self.update_file_status, file_path, "Access Denied", 
                          AppConfig.COLOR_ERROR)
                logging.error(f"Permission denied: {file_path} - {e}")
            
            except IOError as e:
                error_count += 1
                self.after(0, self.update_file_status, file_path, "I/O Error", 
                          AppConfig.COLOR_ERROR)
                logging.error(f"I/O error: {file_path} - {e}")
            
            except Exception as e:
                error_count += 1
                self.after(0, self.update_file_status, file_path, "Error", 
                          AppConfig.COLOR_WARNING)
                logging.error(f"Unexpected error processing {file_path}: {e}", exc_info=True)
            
            current_progress += step
            self.after(0, self.progress_bar.set, current_progress)
        
        # Завершення
        self.after(0, self.on_processing_complete, success_count, error_count)
    
    def update_file_status(self, file_path, status_text, color):
        """Оновлення статусу файлу"""
        if file_path in self.file_rows:
            self.file_rows[file_path].status_label.configure(text=status_text, text_color=color)
    
    def on_processing_complete(self, success_count, error_count):
        """Завершення обробки"""
        self.btn_run.configure(state="normal", text="Corrupt All →")
        
        # Формування детального звіту
        stats = self.total_stats
        avg_time = stats['total_time'] / stats['total_files'] if stats['total_files'] > 0 else 0
        size_diff = stats['original_total_size'] - stats['corrupted_total_size']
        
        message = f"Processing complete!\n\n"
        message += f"✓ Success: {success_count}\n"
        message += f"✗ Errors: {error_count}\n\n"
        message += f"📊 Statistics:\n"
        message += f"• Total bytes changed: {self.format_file_size(stats['total_bytes_changed'])}\n"
        message += f"• Original size: {self.format_file_size(stats['original_total_size'])}\n"
        message += f"• Corrupted size: {self.format_file_size(stats['corrupted_total_size'])}\n"
        message += f"• Size reduced: {self.format_file_size(size_diff)}\n"
        message += f"• Total time: {stats['total_time']:.2f}s\n"
        message += f"• Avg per file: {avg_time:.3f}s"
        
        if error_count == 0:
            message += "\n\n✅ All files processed successfully!"
        
        logging.info(f"Processing complete: {success_count} success, {error_count} errors")
        logging.info(f"Statistics: {stats['total_bytes_changed']} bytes changed, "
                    f"{stats['total_time']:.2f}s total, {avg_time:.3f}s avg")
        
        messagebox.showinfo("Done", message)
