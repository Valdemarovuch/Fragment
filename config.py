"""
Configuration settings for Fragment
"""

# Window settings
WINDOW_WIDTH = 500
WINDOW_HEIGHT = 700
WINDOW_RESIZABLE = False
WINDOW_BACKGROUND = '#050505'

# Corruption settings
CORRUPTION_INTENSITY = 0.005  # 0.5% of bytes
HEADER_SAFE_ZONE = 128  # First 128 bytes preserved

# File processing
CHUNK_SIZE = 64 * 1024  # 64KB blocks for optimal I/O
