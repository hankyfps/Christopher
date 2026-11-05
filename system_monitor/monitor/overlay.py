"""Overlay: kleines, immer sichtbares Fenster mit CPU, RAM und Netzwerk (nur tkinter, nur Haupt-Thread).

Grenzen (siehe README): Ein normales Fenster liegt nicht über Spielen im exklusiven Vollbild, nur über
randlosen Fenstern bzw. Spielen mit "Fullscreen Optimizations". Klick-Durchlässigkeit und globales
Tastenkürzel nutzen Windows-Funktionen über ctypes und sind nur unter Windows aktiv.
"""
from __future__ import annotations

import logging
import queue
import threading
import tkinter as tk

from .config import Config
from .overlay_logic import overlay_geometry, parse_hotkey
from .winutil import IS_WINDOWS

log = logging.getLogger("monitor.overlay")

# Windows-Konstanten (Microsoft Learn: Extended Window Styles, RegisterHotKey)
GWL_EXSTYLE = -20
WS_EX_TRANSPARENT, WS_EX_TOOLWINDOW, WS_EX_LAYERED, WS_EX_NOACTIVATE = 0x20, 0x80, 0x80000, 0x08000000
WM_HOTKEY, WM_QUIT, MOD_NOREPEAT = 0x0312, 0x0012, 0x4000
TEXT_WIDTH = 56          # Zeichen; feste Breite, damit das Fenster beim Aktualisieren nicht wandert


def set_ex_style(widget: tk.Misc, add: int, remove: int = 0) -> bool:
    """Erweiterte Fensterstile setzen (nur Windows). Gibt False zurück, wenn es nicht möglich war."""
    if not IS_WINDOWS:
        return False
    try:
        import ctypes
        user32 = ctypes.windll.user32
        wid = widget.winfo_id()
        hwnd = user32.GetParent(wid) or wid           # Tk-Toplevel: das echte Fenster ist meist das Elternfenster
        get = getattr(user32, "GetWindowLongPtrW", user32.GetWindowLongW)
        setter = getattr(user32, "SetWindowLongPtrW", user32.SetWindowLongW)
        get.restype = ctypes.c_ssize_t
        setter.restype = ctypes.c_ssize_t
        setter.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_ssize_t]
        get.argtypes = [ctypes.c_void_p, ctypes.c_int]
        style = (get(hwnd, GWL_EXSTYLE) | add) & ~remove
        setter(hwnd, GWL_EXSTYLE, style)
        return True
    except Exception:                                   # nie die Anwendung wegen des Overlays beenden
        log.exception("Fensterstil konnte nicht gesetzt werden")
        return False


class OverlayWindow:
    """Randloses, halbtransparentes Fenster ganz oben. Wird nur bei neuem Text neu gezeichnet."""

    def __init__(self, root: tk.Tk, config: Config, font, colors: dict[str, str]) -> None:
        self.root, self.config, self.colors = root, config, colors
        self.visible = False
        self._text = ""
        self._color = ""
        self.top = tk.Toplevel(root)
        self.top.withdraw()
        self.top.overrideredirect(True)
        self.top.configure(bg=colors["bg"])
        self.label = tk.Label(self.top, text="", width=TEXT_WIDTH, anchor="w", font=font, fg=colors["cyan"],
                              bg=colors["bg"], padx=10, pady=3)
        self.label.pack()

    def apply_config(self, config: Config) -> None:
        self.config = config
        if self.visible:
            self._place()
            self._apply_styles()

    def _place(self) -> None:
        self.top.update_idletasks()
        w, h = self.top.winfo_reqwidth(), self.top.winfo_reqheight()
        x, y = overlay_geometry(self.config.overlay_position, self.top.winfo_screenwidth(),
                                self.top.winfo_screenheight(), w, h)
        self.top.geometry(f"{w}x{h}+{x}+{y}")

    def _apply_styles(self) -> None:
        try:
            self.top.attributes("-alpha", self.config.overlay_alpha)
        except tk.TclError:
            log.info("Transparenz wird auf diesem System nicht unterstützt")
        try:
            self.top.attributes("-topmost", True)
        except tk.TclError:
            pass
        # kein Fokusklau, nicht in Taskleiste/Alt+Tab; optional Mausklicks durchlassen
        add = WS_EX_TOOLWINDOW | WS_EX_NOACTIVATE | WS_EX_LAYERED
        remove = 0
        if self.config.overlay_click_through:
            add |= WS_EX_TRANSPARENT
        else:
            remove = WS_EX_TRANSPARENT
        set_ex_style(self.top, add, remove)

    def show(self) -> None:
        self.visible = True
        self.top.deiconify()
        self._place()
        self._apply_styles()
        self.top.lift()

    def hide(self) -> None:
        self.visible = False
        self.top.withdraw()

    def update(self, text: str, color: str) -> None:
        if text != self._text:
            self._text = text
            self.label.config(text=text)
        if color != self._color:
            self._color = color
            self.label.config(fg=color)

    def destroy(self) -> None:
        try:
            self.top.destroy()
        except tk.TclError:
            pass


class HotkeyListener:
    """Globales Tastenkürzel (RegisterHotKey) in eigenem Thread. Meldet "toggle" über eine Queue,
    der Haupt-Thread holt sie ab. Nur unter Windows; sonst start() -> False."""

    def __init__(self, hotkey: str, events: "queue.Queue[str]") -> None:
        self.hotkey, self.events = hotkey, events
        self.registered = False
        self._ready = threading.Event()
        self._tid = 0

    def start(self) -> bool:
        if not IS_WINDOWS:
            log.info("Globales Tastenkürzel gibt es nur unter Windows")
            return False
        threading.Thread(target=self._run, name="hotkey", daemon=True).start()
        self._ready.wait(2.0)
        return self.registered

    def _run(self) -> None:
        try:
            import ctypes
            from ctypes import wintypes
            user32, kernel32 = ctypes.windll.user32, ctypes.windll.kernel32
            mods, vk = parse_hotkey(self.hotkey)
            self._tid = kernel32.GetCurrentThreadId()
            self.registered = bool(user32.RegisterHotKey(None, 1, mods | MOD_NOREPEAT, vk))
            self._ready.set()
            if not self.registered:
                log.warning("Tastenkürzel %s konnte nicht registriert werden (vermutlich schon belegt)", self.hotkey)
                return
            msg = wintypes.MSG()
            while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
                if msg.message == WM_HOTKEY:
                    self.events.put("toggle")
            user32.UnregisterHotKey(None, 1)
        except Exception:
            log.exception("Tastenkürzel-Thread beendet")
            self.registered = False
            self._ready.set()

    def stop(self) -> None:
        if IS_WINDOWS and self._tid:
            try:
                import ctypes
                ctypes.windll.user32.PostThreadMessageW(self._tid, WM_QUIT, 0, 0)
            except Exception:
                pass
