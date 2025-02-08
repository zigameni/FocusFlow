import tkinter as tk
from tkinter import ttk

class ThemeManager:
    def __init__(self):
        self.themes = {
            "dark": {
                "background": "#2E3440",
                "text": "#D8DEE9",
                "accent": "#88C0D0",
                "dim_text": "#4C566A",
                "button_background": "#3B4252",
                "button_text": "#ECEFF4",
                "progress_background": "#3B4252",
                "progress_foreground": "#88C0D0",
                "text_box_background": "#3B4252",
                "text_box_text": "#ECEFF4"
            },
            "light": {
                "background": "#ECEFF4",
                "text": "#2E3440",
                "accent": "#88C0D0",
                "dim_text": "#4C566A",
                "button_background": "#E6E6E6",
                "button_text": "#2E3440",
                "progress_background": "#E6E6E6",
                "progress_foreground": "#2E3440",
                "text_box_background": "#F8F8F8",
                "text_box_text": "#2E3440"
            },
            "sepia": {
                "background": "#F0E6D2",
                "text": "#2E3430",
                "accent": "#A0522D",
                "dim_text": "#6B6B6B",
                "button_background": "#D2B48C",
                "button_text": "#2E3430",
                "progress_background": "#D2B48C",
                "progress_foreground": "#2E3430",
                "text_box_background": "#F5F5DC",
                "text_box_text": "#2E3430"
            }
        }
        self.current_theme = "dark"

    def get_theme(self, name):
        return self.themes.get(name, self.themes["dark"])

    def apply_theme(self, widget):
        theme = self.get_theme(self.current_theme)
        if isinstance(widget, (tk.Tk, tk.Toplevel, tk.Frame)):
            widget.configure(bg=theme["background"])
            for child in widget.winfo_children():
                self.apply_theme(child)
        elif isinstance(widget, tk.Label):
            widget.configure(
                bg=theme["background"],
                fg=theme["text"]
            )
        elif isinstance(widget, ttk.Button):
            widget.configure(
                style=f"{self.current_theme}.TButton"
            )
        elif isinstance(widget, ttk.Progressbar):
            widget.configure(
                style=f"{self.current_theme}.Horizontal.TProgressbar"
            )
        elif isinstance(widget, tk.Text):
            widget.configure(
                bg=theme["text_box_background"],
                fg=theme["text_box_text"],
                insertbackground=theme["text_box_text"]
            )