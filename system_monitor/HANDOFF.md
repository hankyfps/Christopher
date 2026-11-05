# HANDOFF – System-Monitor 2.1.1 → 2.2.0

Stand: 2026-11-05 · Phase 1 (Analyse): Lauf 1 (Übersicht) gemessen, Netzwerk-Lauf und Zusatzmessung ausstehend

## Aktueller Stand
- Phase 1: Code gelesen, Messskript `tools/messung_windows.py` geschrieben und unter Linux/Xvfb auf Funktion geprüft (Python 3.12, Tk 8.6.14).
- Programmcode (`monitor/`, `main.py`, Doku): **unverändert**. Version weiter 2.1.1.
- Windows-Messwerte kommen vom Nutzer (Claude-Umgebung ist Linux). Lauf 1 liegt vor, siehe unten.
- `../system_monitor` (v1.1, Cyberpunk-Look) lag der ZIP **nicht** bei. Für Phase 2/3 (Look, Sparmodus-Vorlage) wird sie gebraucht.
- Tests: `pytest` 51/51 grün, **nur unter Linux** (Python 3.12 und 3.13) geprüft.

## Messwerte (vorher/nachher)
Windows 11 (10.0.26300), Python 3.14.6, Tk 8.6, psutil 7.2.2, 14 logische CPUs. Quelle: Nutzer-Lauf von `tools/messung_windows.py`, Label `vorher`.

| Messwert (Tab Übersicht) | vorher | nachher |
|---|---|---|
| (a) Timer-Verspätung Max / >50 ms / >100 ms (60 s) | 708 ms / 216x / 165x | offen |
| (b) `_top_processes` ohne Fenster, Median / Max | 3847 ms / 6655 ms | offen |
| (b) `_top_processes` im Fenster (Hintergrund-Thread) | 5565 ms / 6528 ms | offen |
| (b) step() ohne Prozessliste | 1,0 ms (ohne Fenster), 8,5 ms (im Fenster) | offen |
| (c) `_update_traffic` (Hauptthread) Median / Max | 162 ms / 239 ms | offen |
| (c) `_tick` Median / Max | 252 ms / 440 ms | offen |
| (c) `_show_drives` Median | 95 ms | offen |
| (c) `_show_snapshot` (neu / unverändert) | 0,75 / 0,89 ms | offen |
| (c) Tab-Wechsel Median nach Übersicht / Laufwerke / Netzwerk | 170 / 147 / 594 ms | offen |
| (c) Fenstergröße ändern Median / Max | 251 / 1356 ms | offen |
| (d) CPU eigener Prozess, sichtbar / minimiert | 77,9 % / 90,3 % eines Kerns (5,6 % / 6,5 % gesamt) | offen |
| RAM Working Set Start / nach Idle | 40,9 / 44,4 MB | offen |
| Threads gestartet pro Minute | 17 (Einzelkosten 0,11 ms) | offen |
| root.bell() | 0,35 ms | offen |
| Meldungsliste: add_message leer / nach 5000 | 0,03 / 0,02 ms (Median) | offen |

Tab Netzwerk: Lauf wurde vom Nutzer versehentlich geschlossen, wird wiederholt. Ausstehend.

Einschränkung: Die GUI-Werte (c) wurden gemessen, während die Prozessliste im Hintergrund 4-7 s lief. Sie sind dadurch vermutlich verfälscht (unter Linux liegen dieselben Funktionen bei ~1 ms). Ob das an der Prozessliste liegt, klärt die Zusatzmessung (`tools/zusatzmessung_starten.bat`: Diagnose + Lauf mit `--prozess-intervall 3600`).

## Entscheidungen des Nutzers
- noch keine (Phase 2 steht aus: Performance-Maßnahmen, Overlay-Variante, Layout, Design hell/Cyberpunk)

## Geänderte Dateien
- neu: `tools/messung_windows.py`, `tools/messung_starten.bat`, `tools/prozess_diagnose.py`, `tools/zusatzmessung_starten.bat` (temporär, nicht Teil des Programms)
- neu: `HANDOFF.md`

## Offene Punkte
- Nutzer wiederholt Lauf 2 (Netzwerk, `messung_starten.bat`), danach `tools/zusatzmessung_starten.bat`; schickt die Ausgabe.
- v1.1-Ordner (`system_monitor` mit Cyberpunk-Look) als ZIP nachreichen, falls Look/Sparmodus daraus übernommen werden sollen.
- Ursachen-Tabelle (Phase 1) mit Messwerten füllen; ohne Messung gilt keine Ursache als belegt.

## Nächster Schritt
1. Nutzer-Messung auswerten → Ursachen-Tabelle (gemessen ja/nein, ms, Aufwand, Risiko).
2. Phase 2: Vorschläge (Performance, Overlay mit ASCII-Skizzen, Layout, Design-Frage), max. 4 Fragen, auf Auswahl warten.
3. Erst danach Phase 3 (vorher Backup `../system_monitor_v2.1.1_backup`).
