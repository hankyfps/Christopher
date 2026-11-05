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
from .overlay_logic import OverlayData, overlay_geometry, overlay_text, parse_hotkey, tile_lines
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


class MiniBar(tk.Canvas):
    """Kleiner Balken für die Mini-Kachel; zeichnet nur bei geändertem Wert oder geänderter Farbe."""

    def __init__(self, parent, width: int, height: int, track: str, bg: str) -> None:
        super().__init__(parent, width=width, height=height, bg=bg, bd=0, highlightthickness=0)
        self._bw, self._bh = width, height               # nicht _w: das ist tkinters interner Widget-Pfad
        self._pct, self._color = -1.0, ""
        self.create_rectangle(0, 0, width - 1, height - 1, fill=track, outline="")
        self._fill = self.create_rectangle(0, 0, 0, height - 1, fill=track, outline="")

    def set(self, pct: float, color: str) -> None:
        if abs(pct - self._pct) < 0.5 and color == self._color:
            return
        self._pct = pct
        if color != self._color:
            self._color = color
            self.itemconfig(self._fill, fill=color)
        self.coords(self._fill, 0, 0, max(0.0, min(100.0, pct)) / 100 * (self._bw - 1), self._bh - 1)


class OverlayWindow:
    """Randloses, halbtransparentes Fenster ganz oben in einem von drei Stilen:
    bar = Leiste, tile = Mini-Kachel mit Balken, numbers = nur Zahlen ohne Hintergrund.
    Gezeichnet wird nur, wenn sich ein Text oder eine Farbe ändert."""

    TRANSPARENT_KEY = "#010203"          # Farbe, die im Stil "numbers" durchsichtig wird (Windows)

    def __init__(self, root: tk.Tk, config: Config, font, colors: dict[str, str],
                 state_colors: dict[str, str]) -> None:
        self.root, self.config, self.font = root, config, font
        self.colors, self.state_colors = colors, state_colors
        self.visible = False
        self._style = ""
        self._cache: dict[str, str] = {}
        self.top = tk.Toplevel(root)
        self.top.withdraw()
        self.top.overrideredirect(True)
        self.body: tk.Frame | None = None
        self._build()

    # ------------------------------------------------------------ Aufbau je Stil
    def _build(self) -> None:
        style = self.config.overlay_style
        if self.body is not None:
            self.body.destroy()
        self._style, self._cache = style, {}
        bg = self.TRANSPARENT_KEY if style == "numbers" else self.colors["bg"]
        self.top.configure(bg=bg)
        self.body = tk.Frame(self.top, bg=bg)
        self.body.pack()
        c = self.colors
        if style == "tile":
            self.name_lbl, self.bar, self.pct_lbl = {}, {}, {}
            for row, name in enumerate(("CPU", "RAM")):
                tk.Label(self.body, text=name, font=self.font, fg=c["muted"], bg=bg, anchor="w").grid(
                    row=row, column=0, sticky="w", padx=(10, 6), pady=(6 if row == 0 else 0, 0))
                self.bar[name] = MiniBar(self.body, 80, 10, c["track"], bg)
                self.bar[name].grid(row=row, column=1, pady=(6 if row == 0 else 0, 0))
                self.pct_lbl[name] = tk.Label(self.body, text="", font=self.font, fg=c["cyan"], bg=bg, width=5,
                                              anchor="e")
                self.pct_lbl[name].grid(row=row, column=2, padx=(6, 10), pady=(6 if row == 0 else 0, 0))
            self.down_lbl = tk.Label(self.body, text="", font=self.font, fg=c["cyan"], bg=bg, anchor="w")
            self.down_lbl.grid(row=2, column=0, columnspan=3, sticky="w", padx=10)
            self.up_lbl = tk.Label(self.body, text="", font=self.font, fg=c["pink"], bg=bg, anchor="w")
            self.up_lbl.grid(row=3, column=0, columnspan=3, sticky="w", padx=10, pady=(0, 6))
        else:
            width = 22 if style == "numbers" else TEXT_WIDTH
            self.label = tk.Label(self.body, text="", width=width, anchor="w", font=self.font, fg=c["cyan"], bg=bg,
                                  padx=10 if style == "bar" else 2, pady=3 if style == "bar" else 0)
            self.label.pack()

    def _set(self, widget, key: str, **kw) -> None:
        """Nur ändern, wenn sich etwas geändert hat."""
        sig = repr(sorted(kw.items()))
        if self._cache.get(key) != sig:
            self._cache[key] = sig
            widget.config(**kw)

    # ------------------------------------------------------------ Steuerung
    def apply_config(self, config: Config) -> None:
        self.config = config
        if config.overlay_style != self._style:
            self._build()
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
        for attr, value in (("-alpha", self.config.overlay_alpha), ("-topmost", True),
                            ("-transparentcolor", self.TRANSPARENT_KEY if self._style == "numbers" else "")):
            try:
                self.top.attributes(attr, value)
            except tk.TclError:             # z. B. -transparentcolor gibt es nur unter Windows
                log.info("Fensterattribut %s wird auf diesem System nicht unterstützt", attr)
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

    def update(self, d: OverlayData) -> None:
        sc = self.state_colors
        if self._style == "tile":
            cpu_c, ram_c = sc[d.levels[0]], sc[d.levels[1]]
            self.bar["CPU"].set(d.cpu, cpu_c)
            self.bar["RAM"].set(d.ram, ram_c)
            self._set(self.pct_lbl["CPU"], "cpu", text=f"{min(100, round(d.cpu))}%", fg=cpu_c)
            self._set(self.pct_lbl["RAM"], "ram", text=f"{min(100, round(d.ram))}%", fg=ram_c)
            down, up = tile_lines(d)
            self._set(self.down_lbl, "down", text=down)
            self._set(self.up_lbl, "up", text=up)
        else:
            self._set(self.label, "label", text=overlay_text(self._style, d), fg=sc[d.worst_level()])

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
