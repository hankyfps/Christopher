# HANDOFF – System-Monitor 2.1.1 → 2.2.0

Stand: 2026-11-05 · Phase 1 (Analyse): Läufe Übersicht und Netzwerk gemessen, Zusatzmessung (A/B ohne Prozessliste) gemessen, Phase 2 Vorschläge gemacht, Auswahl des Nutzers ausstehend

## Aktueller Stand
- Version **2.2.0**, Branch `claude/epic-cannon-mzki1z`. Alle Wünsche umgesetzt: Prozessliste nur bei Bedarf, Overlay in **drei Stilen** (A Leiste `bar`, B Mini-Kachel `tile`, C nur Zahlen `numbers`), **Cyberpunk-Komplettumbau**.
- Basis der Oberfläche ist jetzt die Cyberpunk-`gui.py` des Nutzers (Seitenleiste, NeonButton/NeonBar, rechte Spalte). Mein Zwischenstand "helle/dunkle ttk-Oberfläche mit Kopfzeile (L3)" ist ersetzt (nicht im Repo; nur im Git-Verlauf, Commit `2262309`).
- Aus meinem Teil in die Cyberpunk-GUI übernommen: Prozessliste nur bei sichtbarer Ansicht Übersicht (`skip_processes`, Intervall jetzt 30 s, Knopf JETZT AKTUALISIEREN mit "Stand"-Anzeige; die Messung unten lief noch mit 15 s), Netzwerkzähler im Mess-Thread (`_measure`), Overlay-Knopf + globales Tastenkürzel, Overlay-Einstellungen (zweispaltiger Dialog), Overlay-Daten (`OverlayData`).
- **Mindestgröße jetzt 1020×640** (Vorgabe 720×560 gilt nicht mehr; Seitenleiste + rechte Spalte).
- Tests: 96 grün unter Linux mit Bildschirm (Xvfb, Python 3.12), 88 grün + 8 übersprungen ohne Bildschirm. Windows/Python 3.14: **nicht ausgeführt**.
- **Auf Windows gemessen:** Performance von 2.2.0 (siehe unten). **Handtest vom Nutzer gemeldet (05.11.2026, `docs/handtest_ergebnis_2026-11-05.md`):** alle Punkte ✅ außer 17b (Lesbarkeit `numbers`, nicht geprüft). Unklar: Punkt 16 (exklusiver Vollbild, ✅ gemeldet, erwartet war "nicht sichtbar"), welches Spiel/Anti-Cheat, welche ZIP-Version (Checkliste mit "15 s" -> vermutlich vor Option A).
- Backup 2.1.1: `../system_monitor_v2.1.1_backup` (nur lokal in der Claude-Umgebung), Git-Stand `8efb310`. Beim Nutzer: Ordner `system_monitor_komplett_neu` = 2.1.1.

## Messwerte (vorher/nachher)
Windows 11 (10.0.26300), Python 3.14.6, Tk 8.6, psutil 7.2.2, 14 logische CPUs, 500 Prozesse. Quelle: Nutzer-Läufe von `tools/messung_windows.py`. Vorher = 2.1.1 (Label `vorher`, 13:51/14:00/14:04), nachher = 2.2.0 Cyberpunk (Label `nachher`, 14:52/14:55). Rohdaten (beim Nutzer): `nachher_uebersicht_20261105-145218.json`, `nachher_netzwerk_20261105-145522.json`.

| Messwert (Übersicht / Netzwerk) | 2.1.1 | 2.2.0 |
|---|---|---|
| CPU sichtbar (% eines Kerns) | 84 / 75 | 34,4 / 1,0 |
| CPU minimiert (% eines Kerns) | 84 / 68 | 6,4 / 0,6 |
| Timer Max | 713 / 1204 ms | 376 / 23 ms |
| Timer >50 ms / >100 ms | 222 / 222 ; 177 / 143 | 124 / 0 ; 69 / 0 |
| Messungen in 60 s (Soll 30) | 9 / 10 | 21 / 30 |
| `_tick` Median | 213 / 610 ms | 2,4 / 1,5 ms |
| `_update_traffic` Median | 165 / 545 ms | 0,08 / 1,45 ms |
| `_show_drives` P95 (Übersicht) | 140 ms | 140 ms |
| Tab-Wechsel Median | 33-59 / 217-653 ms | 20-38 / 19-36 ms |
| Fenstergröße ändern Median / P95 | 344 / 1458 ; 121 / 1896 ms | 144 / 1254 ; 135 / 149 ms |
| `_top_processes` im Fenster Median | 5565 ms (9x) | 5315 ms (4x in 60 s) |
| RAM nach Idle | 42 MB | 42 MB |

Befund 2.2.0: Außer in der Übersicht alles im grünen Bereich. In der Übersicht läuft die Prozessliste ca. 35 % der Zeit (4 x 5,3 s je 60 s); dabei stockt die GUI (Timer bis 376 ms, `_show_drives` P95 140 ms) und es entfallen Messungen (21 statt 30). Ursache der Stocker nicht bewiesen. Minimiert 6,4 % vermutlich Rest eines Scans aus der Phase davor (nicht belegt; Messskript wartet nicht darauf). Fenstergröße ändern ist auch ohne Scan träge (135-144 ms je Schritt, Neon-Oberfläche, nicht untersucht).

## Nachmessung Option A (Intervall 30 s, 15:12, nur Übersicht, Label `optionA`)
CPU sichtbar 16,6 % (vorher 15 s: 34,4 %; 2.1.1: 84 %), minimiert 0,6 %, Timer Max 285 ms (>50 ms: 63, >100 ms: 34), Messungen 25/60 s, 2 Scans je 5,1 s (= 17 % der Zeit, passt zu 16,6 % CPU), Tab-Wechsel 22-40 ms, Fenstergröße ändern 143 ms (P95 181), RAM 43 MB. Ruckeln nur noch während eines Scans (`_show_drives` bis 83 ms statt 0,3 ms -> Hauptthread wartet; GIL-Festhalten durch psutil-Aufrufe wahrscheinlich, nicht bewiesen).

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

## Geänderte Dateien (gegenüber 2.1.1)
- `monitor/gui.py` (Cyberpunk-Oberfläche + Overlay-Anbindung), `monitor/overlay.py` (neu: OverlayWindow mit 3 Stilen, MiniBar, HotkeyListener), `monitor/overlay_logic.py` (neu), `monitor/config.py`, `monitor/core.py`, `monitor/collector.py`, `monitor/__init__.py`, `config.json`
- Tests: `tests/test_overlay.py`, `tests/test_gui_smoke.py` (neu)
- Doku: `README.md`, `docs/checkliste_test_windows.md`, Klassendiagramm (dot/png/svg), PAP 1, `docs/Diagramme.pdf`, Screenshots `tab_uebersicht.png`, `einstellungen.png`, `overlay_bar|tile|numbers.png`
- temporär: `tools/messung_windows.py` (läuft mit beiden Oberflächen), `tools/messung_starten.bat` (Label `nachher`), `tools/prozess_diagnose.py`, `tools/zusatzmessung_starten.bat`

## Offene Punkte
- Entscheidung Nutzer: Spiele sind egal, es ist ein Mini-Projekt im Rahmen einer Umschulung -> Spiel/Anti-Cheat/Punkt 16 werden nicht weiter verfolgt. Rest-Ruckeln beim Prozess-Scan: Option D (so lassen); B (eigener Prozess) und C (ctypes-Prototyp) nicht umgesetzt.
- Ursache der ~7 ms je Prozess unbekannt; schneller Weg per ctypes nur Hypothese, ungemessen.
- Handtest Punkt 17b (Lesbarkeit `numbers`) nicht geprüft.
- Screenshots der Ansichten Laufwerke/Netzwerk/Bluetooth/Updates zeigen noch das helle Design von 2.1.
- Ungeklärt: einmalige "CPU 100 %"-Warnung beim Start im Messlauf; Fenstergröße ändern 143 ms je Schritt (Neon-Layout), nicht untersucht.
- Tests liefen nicht unter Python 3.14 (Nutzer-Version); Handtest unter Windows wurde vom Nutzer gemeldet, Programmversion nicht bestätigt.
- `tools/` enthält temporäre Messskripte (nicht Teil des Programms).

## Nächster Schritt
Keiner offen. Projekt ist auf Stand 2.2.0 (Branch `claude/epic-cannon-mzki1z`).
