import tkinter as tk


class UI:
    @staticmethod
    def center_window(win: tk.Toplevel):
        """center the window"""
        win.update_idletasks()  # 确保窗口尺寸已更新
        width = win.winfo_width()
        height = win.winfo_height()
        screen_width = win.winfo_screenwidth()
        screen_height = win.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        win.geometry(f"+{x}+{y}")
        win.deiconify()
