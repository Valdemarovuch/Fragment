"""
PyWebView API bridge - connects UI with core logic
"""
import webview
from src.core.corruptor import FileCorruptor


class WebViewApi:
    """API bridge for webview communication"""
    
    def __init__(self):
        self.corruptor = FileCorruptor()
    
    def pick_file(self):
        """Open native file dialog and return selected file path"""
        result = webview.windows[0].create_file_dialog(
            webview.OPEN_DIALOG, 
            allow_multiple=False
        )
        return result[0] if result else None
    
    def corrupt_file(self, file_path, safety_mode):
        """
        Corrupt file using core engine
        
        Args:
            file_path: Path to file to corrupt
            safety_mode: Whether to use safe filename suffix
            
        Returns:
            Result dict from FileCorruptor
        """
        return self.corruptor.corrupt_file(file_path, safety_mode)
