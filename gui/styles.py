"""
Configurações de estilo e cores
"""
import tkinter as tk
from tkinter import ttk

COLORS = {
    'primary': '#2c3e50',
    'secondary': '#34495e',
    'accent': '#3498db',
    'success': '#27ae60',
    'warning': '#f39c12',
    'danger': '#e74c3c',
    'light': '#ecf0f1',
    'dark': '#2c3e50',
    'text': '#2c3e50',
    'text_light': '#7f8c8d'
}

def setup_styles():
    """Configura os estilos do Tkinter"""
    style = ttk.Style()
    style.theme_use('clam')
    
    # Configurar cores
    style.configure('TFrame', background=COLORS['light'])
    style.configure('TLabel', background=COLORS['light'], foreground=COLORS['text'])
    style.configure('TLabelframe', background=COLORS['light'], foreground=COLORS['primary'])
    style.configure('TLabelframe.Label', background=COLORS['light'], foreground=COLORS['primary'])
    style.configure('TButton', padding=(10, 5))
    
    return style