# HANDOFF – System-Monitor 2.1.1 → 2.2.0

Stand: 2026-11-05 · Phase 1 (Analyse): Läufe Übersicht und Netzwerk gemessen, Zusatzmessung (A/B ohne Prozessliste) gemessen, Phase 2 Vorschläge gemacht, Auswahl des Nutzers ausstehend

## Aktueller Stand
- Version **2.2.0** umgesetzt (Phase 3), Branch `claude/epic-cannon-mzki1z`. Phase 1/2 abgeschlossen, Messwerte unten.
- Umgesetzt: Prozessliste nur bei sichtbarer Übersicht (`skip_processes`), Intervall 15 s; Netzwerkzähler im Mess-Thread; Meldungsliste max. 500; Overlay Variante **A (kompakte Leiste)** mit Position/Deckkraft/Klick-Durchlässigkeit/Tastenkürzel (`overlay.py`, `overlay_logic.py`); Layout **L3** (Kopfzeile mit Kennzahlen auf allen Tabs, Netzrate in Statuszeile); Design: Farbpalette der Cyberpunk-Version auf ttk-Styles übertragen (kein NeonButton/NeonBar).
- Annahmen (Nutzer hatte bei "umsetzen" nichts gewählt): Overlay-Variante A statt B/C; hell/dunkel -> dunkel mit Palette aus `system_monitor_v2_2_cyberpunk.zip`. Änderbar.
- Cyberpunk-ZIP des Nutzers hat Mindestgröße 1020×640 (Seitenleiste) und passt nicht zur Vorgabe 720×560; ihr `skip_processes`-Name wurde übernommen.
- Tests: 84 grün unter Linux mit Bildschirm (Xvfb, Python 3.12), 80 grün + 4 übersprungen ohne Bildschirm. Windows/Python 3.14: **nicht ausgeführt**.
- **Nicht auf Windows getestet:** Klick-Durchlässigkeit, globales Tastenkürzel, Overlay über Spiel, Verhalten von 2.2.0 insgesamt, Messwerte "nachher". Checkliste: `docs/checkliste_test_windows.md`.
- Backup: `../system_monitor_v2.1.1_backup` (lokal in der Claude-Umgebung, nicht im Repo), Git-Stand `8efb310` / Tag `v2.1.1-vor-2.2.0` (Tag-Push scheiterte am Proxy, nur lokal). Beim Nutzer: der alte entpackte Ordner `system_monitor_komplett_neu` ist der 2.1.1-Stand.

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
- "umsetzen" ohne Einzelwahl -> Empfehlungen aus Phase 2 umgesetzt (siehe Annahmen oben).
- Cyberpunk-Version geschickt mit Hinweis "vielleicht können wir die Farben entnehmen" -> nur Farben/Schriften übernommen.

## Geänderte Dateien
- geändert: `monitor/gui.py` (komplett neu aufgebaut), `monitor/config.py` (overlay_*, process_interval_s 15), `monitor/core.py`, `monitor/collector.py` (skip_processes), `monitor/__init__.py` (2.2.0), `config.json`
- neu: `monitor/overlay.py`, `monitor/overlay_logic.py`, `tests/test_overlay.py`, `tests/test_gui_smoke.py`, `docs/checkliste_test_windows.md`, `docs/screenshots/overlay.png`
- Doku: `README.md`, `docs/src/klassendiagramm.dot` (+png/svg), `docs/src/pap_hauptprogramm.dot` (+png/svg), `docs/Diagramme.pdf` (Seiten 1 und 4 neu)
- temporär: `tools/messung_windows.py`, `tools/messung_starten.bat` (Label jetzt `nachher`), `tools/prozess_diagnose.py`, `tools/zusatzmessung_starten.bat`

## Offene Punkte
- Nutzer: Windows-Test per Checkliste und `tools\messung_starten.bat` (nachher), Ergebnis schicken -> README-Abschnitt "Performance" mit 2.2.0-Werten ergänzen.
- Ursache der ~7 ms je Prozess unbekannt; schneller Weg (ein Systemaufruf für alle Prozesse per ctypes) nur Hypothese, ungemessen.
- Overlay B/C, Cyberpunk-Komplettumbau (NeonButton/NeonBar, Seitenleiste) nicht umgesetzt.
- Screenshots der Tabs Laufwerke/Netzwerk/Bluetooth/Updates zeigen noch das helle Design.
- Ungeklärt: einmalige "CPU 100 %"-Warnung beim Start im Messlauf.
- Python 3.14 (Nutzer) bisher nur dort gelaufen, Tests nicht.

## Nächster Schritt
Ergebnisse des Windows-Tests auswerten, Fehler beheben, Performance-Abschnitt in README mit echten 2.2.0-Zahlen füllen.
