from __future__ import annotations

import tkinter as tk


class SimpleToolTip:
    def __init__(self, widget: tk.Widget, text: str) -> None:
        self.widget = widget
        self.text = text
        self.tip_window: tk.Toplevel | None = None
        widget.bind("<Enter>", self._show)
        widget.bind("<Leave>", self._hide)

    def _show(self, _event: tk.Event) -> None:
        if self.tip_window:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 8
        self.tip_window = tk.Toplevel(self.widget)
        self.tip_window.overrideredirect(True)
        self.tip_window.geometry(f"+{x}+{y}")
        tk.Label(
            self.tip_window,
            text=self.text,
            justify="left",
            bg="#1f1f1f",
            fg="#f2f2f2",
            relief="solid",
            borderwidth=1,
            padx=8,
            pady=6,
        ).pack()

    def _hide(self, _event: tk.Event) -> None:
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None
