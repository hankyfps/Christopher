# HANDOFF – System-Monitor 2.1.1 → 2.2.0

Stand: 2026-11-05 · Phase 1 (Analyse): Läufe Übersicht und Netzwerk gemessen, Zusatzmessung (A/B ohne Prozessliste) gemessen, Phase 2 Vorschläge gemacht, Auswahl des Nutzers ausstehend

## Aktueller Stand
- Phase 1: Code gelesen, Messskript `tools/messung_windows.py` geschrieben und unter Linux/Xvfb auf Funktion geprüft (Python 3.12, Tk 8.6.14).
- Programmcode (`monitor/`, `main.py`, Doku): **unverändert**. Version weiter 2.1.1.
- Windows-Messwerte kommen vom Nutzer (Claude-Umgebung ist Linux). Läufe liegen vor, siehe unten. Tests nur unter Python 3.12/3.13 geprüft, Nutzer hat Python 3.14.6.
- `../system_monitor` (v1.1, Cyberpunk-Look) lag der ZIP **nicht** bei. Für Phase 2/3 (Look, Sparmodus-Vorlage) wird sie gebraucht.
- Tests: `pytest` 51/51 grün, **nur unter Linux** (Python 3.12 und 3.13) geprüft.

## Messwerte (vorher/nachher)
Windows 11 (10.0.26300), Python 3.14.6, Tk 8.6, psutil 7.2.2, 14 logische CPUs. Quelle: Nutzer-Läufe `tools/messung_windows.py`, Label `vorher`. Übersicht wurde zweimal gemessen (13:51 und 14:00), Netzwerk einmal (14:04).

| Messwert | Übersicht A / B | Netzwerk | nachher |
|---|---|---|---|
| (a) Timer-Verspätung Max | 708 / 713 ms | 1204 ms | offen |
| (a) Timer >50 ms / >100 ms (60 s) | 216 / 222 x ; 165 / 177 x | 222 x ; 143 x | offen |
| (b) `_top_processes` ohne Fenster, Median / Max | 3847 / 6655 ; 4181 / 6337 ms | 5451 / 6901 ms | offen |
| (b) `_top_processes` im Fenster, Median | 5565 / 5615 ms | 5308 ms | offen |
| (b) step() ohne Prozessliste, ohne Fenster | 1,0 / 1,3 ms | 0,9 ms | offen |
| (b) Messungen in 60 s im Fenster (Soll bei 2 s: 30) | 11 / 9 | 10 | offen |
| (c) `_update_traffic` Median | 162 / 165 ms | 545 ms | offen |
| (c) `_tick` Median | 252 / 213 ms | 610 ms | offen |
| (c) `_show_drives` Median | 95 / 63 ms | 82 ms | offen |
| (c) `_draw_graph` im Betrieb Median | – | 400 ms | offen |
| (c) `_draw_graph` beim Größe ändern Median / P95 | – | 2,1 / 507 ms | offen |
| (c) `_show_snapshot` neue Prozessliste | 0,75 / 1,03 ms | 1,01 ms | offen |
| (c) `_show_snapshot` unverändert | 0,89 ms | – | offen |
| (c) Tab-Wechsel Median (nach Übers./Laufw./Netzw.) | 170/147/594 ; 59/33/47 ms | 270/217/653 ms | offen |
| (c) Fenstergröße ändern Median / P95 | 251 / 1058 ; 344 / 1458 ms | 121 / 1896 ms | offen |
| (d) CPU sichtbar (% eines Kerns) | 77,9 / 84,0 | 75,0 | offen |
| (d) CPU minimiert (% eines Kerns) | 90,3 / 84,0 | 67,8 | offen |
| RAM Working Set Start / nach Idle | 40,9/44,4 ; 40,6/42,3 MB | 41,0/42,2 MB | offen |
| Threads gestartet pro Minute / Einzelkosten | 17 / 15 ; 0,11-0,21 ms | 20 ; 0,12 ms | offen |
| root.bell() | 0,35 ms | – | offen |
| add_message leer / nach 5000 (Median) | 0,03-0,15 / 0,02-0,03 ms | 0,02 / 0,03 ms | offen |

Einschränkung: Die GUI-Werte (c) entstanden, während die Prozessliste im Hintergrund fast dauernd lief (5,3-5,6 s bei 5 s Intervall). Ob sie dadurch verfälscht sind, klärt der A/B-Lauf mit `--prozess-intervall 3600` (`tools/zusatzmessung_starten.bat`). Indiz dafür: `_draw_graph` beim Größe ändern Median 2,1 ms, im Betrieb Median 400 ms.
Zusätzliche Auffälligkeit (nicht untersucht): einmal "WARNUNG CPU 100 %" beim Start im Einzeltest.

## Zusatzmessung (14:11-14:17): Prozessliste-Diagnose und A/B ohne Prozessliste
Diagnose (500 Prozesse, `tools/prozess_diagnose.py`): process_iter nur pid/name: 2,2-2,5 ms. Jeder Wert, der pro Prozess etwas abfragt (cpu_percent, cpu_times, memory_info): 3,7-3,9 s. memory_info einzeln: Summe 3680 ms bei 496 Prozessen, also ~7 ms je Prozess gleichmäßig (langsamster 69 ms). Kein Prozess ohne Zugriff. Ursache der 7 ms je Prozess: NICHT ermittelt.
Hauptthread-Aufrufe ruhig vs. während Prozessliste läuft: net_io_counters 6,2 -> 24,7 ms; disk_usage 0,0 -> 19,1 ms.

| Messwert | mit Prozessliste (Übers./Netzw.) | ohne Prozessliste (Übers./Netzw.) |
|---|---|---|
| Timer Max | 713 / 1204 ms | 25,6 / 25,3 ms |
| Timer >50 ms / >100 ms | 222 / 222 x ; 177 / 143 x | 0 / 0 |
| CPU sichtbar (% eines Kerns) | 84,0 / 75,0 | 0,99 / 0,94 |
| CPU minimiert (% eines Kerns) | 84,0 / 67,8 | 1,02 / 0,94 |
| Messungen in 60 s (Soll 30) | 9 / 10 | 30 / 29 |
| `_tick` Median | 213 / 610 ms | 12,6 / 13,1 ms |
| `_update_traffic` Median | 165 / 545 ms | 11,0 / 11,6 ms |
| `_show_drives` Median | 63 / 82 ms | 0,26 / 0,28 ms |
| `_draw_graph` im Betrieb | 400 ms (Netzw.) | 0,94 ms |
| Tab-Wechsel Median | 33-59 / 217-653 ms | 24-41 / 24-39 ms |
| Fenstergröße Median / P95 | 344 / 1458 ; 121 / 1896 ms | 111 / 121 ; 72 / 99 ms |
| RAM nach Idle | 42,3 / 42,2 MB | 42,2 / 41,3 MB |

Fazit: Prozessliste ist Ursache für CPU, Timer-Verspätung, ausgebremste Hauptthread-Aufrufe und das zu seltene Messen (9-10 statt 30 Messungen/min). Restkosten ohne Liste: `_update_traffic` 11 ms, Fenstergröße ändern 72-111 ms/Schritt (Tk-Layout, Diagramm nur ~1 ms).

## Entscheidungen des Nutzers
- noch keine (Phase 2 steht aus: Performance-Maßnahmen, Overlay-Variante, Layout, Design hell/Cyberpunk)

## Geänderte Dateien
- neu: `tools/messung_windows.py`, `tools/messung_starten.bat`, `tools/prozess_diagnose.py`, `tools/zusatzmessung_starten.bat` (temporär, nicht Teil des Programms)
- neu: `HANDOFF.md`

## Offene Punkte
- Antworten des Nutzers auf die 4 Phase-2-Fragen (Prozessliste, Overlay-Variante, Layout, Design).
- Ursache für ~7 ms je Prozess unbekannt; schneller Weg per ctypes (eine Abfrage für alle Prozesse) ist Hypothese, ungemessen, nur als Prototyp mit Messung.
- v1.1-Ordner (`system_monitor` mit Cyberpunk-Look) als ZIP nachreichen, falls Look/Sparmodus daraus übernommen werden sollen.
- Ursachen-Tabelle (Phase 1) mit Messwerten füllen; ohne Messung gilt keine Ursache als belegt.

## Nächster Schritt
1. Auf Auswahl des Nutzers warten (nichts am Programmcode ändern bis dahin).
2. Dann Phase 3 (vorher Backup `../system_monitor_v2.1.1_backup`).
