"""ttk wrapper module needed when using sun valley theme"""
from tkinter import ttk
from typing import Optional

import sv_ttk


def set_my_theme(font: Optional[str] = None):
    """Used to set the theme for all ttk items"""
    sv_ttk.set_theme("dark")
    my_theme = ttk.Style()
    my_theme.configure('.', font=font)
