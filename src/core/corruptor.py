"""
Core corruption engine - handles file manipulation and corruption logic
"""
import os
import random
import shutil
import stat
import subprocess
import platform
from datetime import datetime


class FileCorruptor:
    """Handles file corruption with smart header preservation"""
    
    def __init__(self, corruption_intensity=0.005, header_safe_zone=128):
        self.corruption_intensity = corruption_intensity
        self.header_safe_zone = header_safe_zone
    
    def corrupt_file(self, file_path, safety_mode=True):
        """
        Corrupts file while preserving header
        
        Args:
            file_path: Path to the file to corrupt
            safety_mode: If True, append "_corrupted" to filename
            
        Returns:
            dict with 'success' and 'new_path' or 'error'
        """
        try:
            if not os.path.exists(file_path):
                return {'success': False, 'error': 'Target missing'}

            # Setup paths
            dirname = os.path.dirname(file_path)
            filename = os.path.basename(file_path)
            name, ext = os.path.splitext(filename)
            
            suffix = "_corrupted" if safety_mode else "_fragment"
            new_filename = f"{name}{suffix}{ext}"
            new_path = os.path.join(dirname, new_filename)

            # Get original file stats
            stats = os.stat(file_path)
            file_size = stats.st_size

            # Smart corruption with header retention
            chunk_size = 64 * 1024  # 64KB blocks
            written = 0

            with open(new_path, 'wb') as f_dst:
                # Copy header to preserve file signature
                header_len = min(self.header_safe_zone, file_size)
                
                with open(file_path, 'rb') as f_src:
                    header_data = f_src.read(header_len)
                    f_dst.write(header_data)
                    written += header_len

                # Fill rest with cryptographic noise
                while written < file_size:
                    remaining = file_size - written
                    current_chunk = min(chunk_size, remaining)
                    f_dst.write(os.urandom(current_chunk))
                    written += current_chunk

            # METADATA CLONING - copy all file attributes
            
            # 1. Copy birthtime (creation time) on macOS - MUST BE FIRST
            if platform.system() == 'Darwin' and hasattr(stats, 'st_birthtime'):
                try:
                    birth_dt = datetime.fromtimestamp(stats.st_birthtime)
                    # Format: MM/DD/YYYY HH:MM:SS
                    birth_str = birth_dt.strftime('%m/%d/%Y %H:%M:%S')
                    subprocess.run(
                        ['SetFile', '-d', birth_str, new_path],
                        check=True,
                        capture_output=True
                    )
                except (subprocess.SubprocessError, OSError, ValueError) as e:
                    pass  # Silently continue if SetFile fails
            
            # 2. Copy timestamps (atime, mtime) - AFTER birthtime
            os.utime(new_path, (stats.st_atime, stats.st_mtime))
            
            # 3. Copy file permissions
            os.chmod(new_path, stat.S_IMODE(stats.st_mode))
            
            # 4. Copy owner and group (only works with proper permissions)
            try:
                os.chown(new_path, stats.st_uid, stats.st_gid)
            except (PermissionError, OSError, AttributeError):
                pass
            
            # 5. Copy extended attributes (macOS/Linux)
            try:
                if hasattr(os, 'listxattr'):
                    for attr in os.listxattr(file_path):
                        try:
                            value = os.getxattr(file_path, attr)
                            os.setxattr(new_path, attr, value)
                        except (OSError, IOError):
                            pass
            except (AttributeError, OSError):
                pass
            
            return {'success': True, 'new_path': new_path}

        except Exception as e:
            return {'success': False, 'error': str(e)}
