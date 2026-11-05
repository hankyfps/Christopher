"""GUI-freie Logik des Overlays: Position, Text, Farbstufe und Tastenkürzel (ohne tkinter testbar)."""
from __future__ import annotations

from dataclasses import dataclass

from .network import format_rate

OVERLAY_STYLES = ("bar", "tile", "numbers")      # A Leiste, B Mini-Kachel, C nur Zahlen
POSITIONS = ("top-left", "top-center", "top-right", "bottom-left", "bottom-center", "bottom-right")

# Werte wie bei der Windows-Funktion RegisterHotKey (MOD_ALT, MOD_CONTROL, MOD_SHIFT, MOD_WIN)
MOD_ALT, MOD_CONTROL, MOD_SHIFT, MOD_WIN = 0x1, 0x2, 0x4, 0x8
_MODIFIERS = {"alt": MOD_ALT, "ctrl": MOD_CONTROL, "strg": MOD_CONTROL, "shift": MOD_SHIFT,
              "umschalt": MOD_SHIFT, "win": MOD_WIN}
_MOD_ORDER = ("ctrl", "alt", "shift", "win")
_MOD_NAME = {MOD_CONTROL: "ctrl", MOD_ALT: "alt", MOD_SHIFT: "shift", MOD_WIN: "win"}


def overlay_geometry(position: str, screen_w: int, screen_h: int, w: int, h: int, margin: int = 12) -> tuple[int, int]:
    """Linke obere Ecke des Overlays. Passt es nicht auf den Bildschirm, bleibt es bei 0."""
    if position not in POSITIONS:
        raise ValueError(f"Unbekannte Position: {position!r}")
    vert, horiz = position.split("-")
    x = {"left": margin, "center": (screen_w - w) // 2, "right": screen_w - w - margin}[horiz]
    y = margin if vert == "top" else screen_h - h - margin
    return max(0, x), max(0, y)


def format_overlay_text(cpu: float, ram: float, down_bps: float, up_bps: float, clock: str) -> str:
    return (f"CPU {min(100, round(cpu)):3d}%  RAM {min(100, round(ram)):3d}%  "
            f"↓ {format_rate(down_bps)}  ↑ {format_rate(up_bps)}  {clock}")


def level_for(value: float, threshold: float) -> str:
    """'alarm' ab der Schwelle, 'nah' innerhalb von 10 Punkten darunter, sonst 'normal'."""
    if value >= threshold:
        return "alarm"
    if value >= threshold - 10:
        return "nah"
    return "normal"


def _split(hotkey: str) -> tuple[int, str]:
    parts = [p.strip().lower() for p in str(hotkey).split("+")]
    mods = 0
    for p in parts[:-1]:
        if p not in _MODIFIERS:
            raise ValueError(f"Unbekannte Taste im Kürzel: {p!r}")
        bit = _MODIFIERS[p]
        if mods & bit:
            raise ValueError(f"Taste doppelt im Kürzel: {p!r}")
        mods |= bit
    key = parts[-1]
    if key in _MODIFIERS:
        raise ValueError("Das Kürzel braucht eine Haupttaste (Buchstabe, Ziffer oder F1-F12)")
    return mods, key


def parse_hotkey(hotkey: str) -> tuple[int, int]:
    """'ctrl+alt+o' -> (Modifikator-Maske, virtueller Tastencode). Mindestens ein Modifikator ist Pflicht,
    sonst würde eine normale Taste systemweit blockiert."""
    mods, key = _split(hotkey)
    if not mods:
        raise ValueError("Das Kürzel braucht mindestens Strg, Alt, Umschalt oder Win")
    if len(key) == 1 and key.isascii() and key.isalnum():
        return mods, ord(key.upper())
    if key.startswith("f") and key[1:].isdigit() and 1 <= int(key[1:]) <= 12:
        return mods, 0x70 + int(key[1:]) - 1
    raise ValueError(f"Ungültige Haupttaste: {key!r} (erlaubt: A-Z, 0-9, F1-F12)")


def normalize_hotkey(hotkey: str) -> str:
    """Einheitliche Schreibweise, z. B. 'Strg+ALT+o' -> 'ctrl+alt+o'."""
    mods, vk = parse_hotkey(hotkey)
    key = _split(hotkey)[1]
    return "+".join([_MOD_NAME[m] for m in (MOD_CONTROL, MOD_ALT, MOD_SHIFT, MOD_WIN) if mods & m] + [key])


_ORDER = {"normal": 0, "nah": 1, "alarm": 2}


@dataclass(frozen=True)
class OverlayData:
    """Alles, was das Overlay anzeigt. levels = Stufen von (CPU, RAM, Festplatte)."""
    cpu: float
    ram: float
    down_bps: float
    up_bps: float
    clock: str
    levels: tuple[str, str, str] = ("normal", "normal", "normal")

    def worst_level(self) -> str:
        return max(self.levels, key=_ORDER.get)


def compact_rate(bps: float) -> str:
    """Kurzform für den Stil 'nur Zahlen': 1.2M, 340K."""
    if bps >= 1024 ** 2:
        return f"{bps / 1024 ** 2:.1f}M"
    return f"{bps / 1024:.0f}K"


def tile_lines(d: OverlayData) -> tuple[str, str]:
    return f"↓ {format_rate(d.down_bps)}", f"↑ {format_rate(d.up_bps)}"


def overlay_text(style: str, d: OverlayData) -> str:
    """Text je Stil (die Kachel zeigt die Balken zusätzlich grafisch)."""
    if style == "bar":
        return format_overlay_text(d.cpu, d.ram, d.down_bps, d.up_bps, d.clock)
    if style == "numbers":
        return f"{min(100, round(d.cpu))}% · {min(100, round(d.ram))}% · ↓{compact_rate(d.down_bps)}"
    if style == "tile":
        down, up = tile_lines(d)
        return "\n".join((f"CPU {min(100, round(d.cpu)):3d}%", f"RAM {min(100, round(d.ram)):3d}%", down, up))
    raise ValueError(f"Unbekannter Overlay-Stil: {style!r}")
