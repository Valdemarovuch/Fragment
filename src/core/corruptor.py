"""
Core corruption engine - handles file manipulation and corruption logic
"""
import os
import random


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

            # Timestomping - copy original timestamps
            os.utime(new_path, (stats.st_atime, stats.st_mtime))
            
            return {'success': True, 'new_path': new_path}

        except Exception as e:
            return {'success': False, 'error': str(e)}
