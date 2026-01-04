"""
Fragment - Data Corruption Tool
Main entry point
"""
import webview
import os
from src.api.bridge import WebViewApi


def load_html():
    """Load HTML interface from file"""
    html_path = os.path.join('src', 'ui', 'interface.html')
    with open(html_path, 'r', encoding='utf-8') as f:
        return f.read()


def main():
    """Launch the application"""
    api = WebViewApi()
    html_content = load_html()
    
    window = webview.create_window(
        'Fragment // Data Corruptor', 
        html=html_content, 
        js_api=api,
        width=500, 
        height=700,
        resizable=False,
        background_color='#050505'
    )
    
    webview.start()


if __name__ == '__main__':
    main()
