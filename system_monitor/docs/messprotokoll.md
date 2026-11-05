# Messprotokoll (Windows, 05.11.2026)

Rohmessungen aus `HANDOFF.md` ausgelagert. Alle Werte stammen aus Läufen des Nutzers mit `tools/messung_windows.py`
(Windows 11 Build 10.0.26300, Python 3.14.6, Tk 8.6, psutil 7.2.2, 14 logische CPUs, 500 Prozesse, 60 s je Lauf).
Die Rohdaten (`*.json`) liegen beim Nutzer in `messungen\` und sind nicht im Repository.

Läufe: 2.1.1 mit Prozessliste (Label `vorher`, 13:51 / 14:00 / 14:04), Zusatzmessung ohne Prozessliste
(14:11–14:17), 2.2.0 mit Intervall 15 s (Label `nachher`, 14:52 / 14:55), 2.2.0 mit Intervall 30 s (Label `optionA`, 15:12, nur Übersicht).

## Vergleich 2.1.1 gegen 2.2.0 (Intervall 15 s)
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

