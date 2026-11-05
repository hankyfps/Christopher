# HANDOFF – System-Monitor 2.2.0

Stand: 2026-11-05 · Projekt abgeschlossen auf Version 2.2.0 · Branch `claude/epic-cannon-mzki1z` (Repository `hankyfps/Christopher`, Ordner `system_monitor/`)

## Aktueller Stand
- **Ziel:** (1) wenig CPU/RAM und kein spürbares Ruckeln unter Windows, (2) Overlay, (3) besseres Layout. Alle drei umgesetzt.
- **Umgesetzt:** Prozessliste nur in der sichtbaren Ansicht Übersicht (Intervall 30 s, Knopf JETZT AKTUALISIEREN, „Stand“-Anzeige); Netzwerkzähler im Mess-Thread; Meldungen höchstens 500; Overlay in drei Stilen (`bar` Leiste, `tile` Mini-Kachel, `numbers` nur Zahlen) mit Position, Deckkraft, Klick-Durchlässigkeit und globalem Tastenkürzel `Strg+Alt+O`; Cyberpunk-Oberfläche (Seitenleiste, rechte Spalte) als Basis.
- **Mindestgröße des Fensters jetzt 1020×640** (früher 720×560).
- **Tests:** 98 grün unter Linux mit Bildschirm (Python 3.12), 88 grün + 10 übersprungen ohne Bildschirm. **Nicht** unter Windows und **nicht** unter Python 3.14 ausgeführt.
- **Handtest auf Windows:** vom Nutzer gemeldet, alle Punkte ✅ außer 17b (nicht geprüft). Siehe `docs/handtest_ergebnis_2026-11-05.md`. Programmversion des Handtests nicht bestätigt.
- **Rückfall auf 2.1.1:** Git-Commit `8efb310` (lokaler Tag `v2.1.1-vor-2.2.0`, ließ sich nicht pushen).

## Messwerte (Windows, vorher/nachher; Details in `docs/messprotokoll.md`)
| Messwert (Übersicht / Netzwerk) | 2.1.1 | 2.2.0 (Intervall 30 s)* |
|---|---|---|
| CPU sichtbar (% eines Kerns) | 84 / 75 | **16,6** / 1,0 |
| CPU minimiert (% eines Kerns) | 84 / 68 | **0,6** / 0,6 |
| Timer-Verspätung, Maximum | 713 / 1204 ms | **285** / 23 ms |
| Timer über 100 ms (in 60 s) | 177 / 143 | **34** / 0 |
| Messungen in 60 s (Soll 30) | 9 / 10 | **25** / 30 |
| `_tick` im Hauptthread, Median | 213 / 610 ms | 11 / 1,5 ms |
| Tab-Wechsel, Median | 33–653 ms | 19–40 ms |
| RAM (Working Set) | 42 MB | 43 MB |

\* Übersicht: Läufe mit 30 s (15:12). Netzwerk: nur mit 15 s gemessen (14:55), die Ansicht erstellt keine Prozessliste, das Intervall ist dort ohne Einfluss.
Ursache der Last: die Prozessliste (500 Prozesse, ca. 7 ms je Prozess, ca. 5 s je Aufbau). Ohne sie: ca. 1 % eines Kerns.

## Entscheidungen des Nutzers
- Sparmaßnahmen nach Messung statt nach Vermutung; Prozessliste als Hauptursache bestätigt.
- „umsetzen“ ohne Einzelwahl → Empfehlungen umgesetzt; danach ausdrücklich: Overlay B und C sowie der Cyberpunk-Komplettumbau.
- Rest-Ruckeln beim Prozess-Scan: **Option A** (30 s + Knopf), danach **Option D** (so lassen).
- Spiele/Anti-Cheat sind unerheblich (Mini-Projekt im Rahmen einer Umschulung).

## Geänderte Dateien (gegenüber 2.1.1)
- Programm: `monitor/gui.py` (Cyberpunk-Oberfläche, Overlay-Anbindung, Prozess-Knopf), `monitor/overlay.py` (neu), `monitor/overlay_logic.py` (neu), `monitor/config.py`, `monitor/core.py`, `monitor/collector.py` (`skip_processes`), `monitor/__init__.py`, `config.json`
- Tests: `tests/test_overlay.py`, `tests/test_gui_smoke.py` (neu)
- Doku: `README.md`, `docs/checkliste_test_windows.md`, `docs/handtest_ergebnis_2026-11-05.md`, `docs/messprotokoll.md`, Klassendiagramm (dot/png/svg), PAP 1, `docs/Diagramme.pdf`, Screenshots
- Nicht Teil des Programms: `tools/` (Messskripte und `.bat`-Starter)

## So prüfst du den Stand
```bat
py -m pip install -r requirements.txt
py -m pytest -v
py main.py
py tools\messung_windows.py --tab uebersicht --label test
```

## Offene Punkte
- Ursache der ~7 ms je Prozess unbekannt; schneller Weg per `ctypes` nur Hypothese, ungemessen.
- Während eines Prozess-Scans (alle 30 s, ca. 5 s) stockt die Oberfläche kurz (Timer bis 285 ms). Ursache vermutlich Festhalten von Python durch psutil, **nicht bewiesen**.
- Fenstergröße ändern kostet 143 ms je Schritt (Neon-Layout), nicht untersucht.
- Overlay Lesbarkeit im Stil `numbers` (Punkt 17b) nicht geprüft. Overlay-Größen in README sind Linux-Werte.
- Screenshots der Ansichten Laufwerke/Netzwerk/Bluetooth/Updates zeigen noch das helle Design von 2.1.
- Einmalige „CPU 100 %“-Warnung beim Start im Messlauf nicht untersucht.
- Tests auf Python 3.14 und Windows nicht ausgeführt.

## Nächster Schritt
Keiner offen. Falls weitergearbeitet wird: zuerst Handtest mit der gelieferten Version wiederholen (Punkt 5, 5a, 17b), dann Option B oder C nur nach neuer Messung.
