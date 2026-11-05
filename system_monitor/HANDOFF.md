# HANDOFF – System-Monitor 2.1.1 → 2.2.0

Stand: 2026-11-05 · Phase 1 (Analyse) vorbereitet, **Windows-Messung steht aus**

## Aktueller Stand
- Phase 1: Code gelesen, Messskript `tools/messung_windows.py` geschrieben und unter Linux/Xvfb auf Funktion geprüft (Python 3.12, Tk 8.6.14).
- Programmcode (`monitor/`, `main.py`, Doku): **unverändert**. Version weiter 2.1.1.
- Keine Windows-Messwerte vorhanden. Die Claude-Umgebung ist Linux; Windows-Zahlen kann nur der Nutzer liefern.
- `../system_monitor` (v1.1, Cyberpunk-Look) lag der ZIP **nicht** bei. Für Phase 2/3 (Look, Sparmodus-Vorlage) wird sie gebraucht.
- Tests: `pytest` 51/51 grün, **nur unter Linux** (Python 3.12 und 3.13) geprüft.

## Messwerte (vorher/nachher)
| Messwert | vorher (Windows) | nachher (Windows) |
|---|---|---|
| (a) Timer-Verspätung Max / >50 ms / >100 ms | offen | – |
| (b) step() mit / ohne Prozessliste | offen | – |
| (c) GUI-Updates, Tab-Wechsel, Fenstergröße | offen | – |
| (d) CPU im Leerlauf sichtbar / minimiert, RAM | offen | – |

Die Linux-Probeläufe sind nur Funktionstests des Skripts und gelten nicht als Messwerte.

## Entscheidungen des Nutzers
- noch keine (Phase 2 steht aus: Performance-Maßnahmen, Overlay-Variante, Layout, Design hell/Cyberpunk)

## Geänderte Dateien
- neu: `tools/messung_windows.py` (temporär, nicht Teil des Programms)
- neu: `HANDOFF.md`

## Offene Punkte
- Nutzer führt Messskript auf Windows aus: Tab `uebersicht` und `netzwerk`, je mit `--label vorher`; schickt die Ausgabe bzw. `messungen/*.json`.
- v1.1-Ordner (`system_monitor` mit Cyberpunk-Look) als ZIP nachreichen, falls Look/Sparmodus daraus übernommen werden sollen.
- Ursachen-Tabelle (Phase 1) mit Messwerten füllen; ohne Messung gilt keine Ursache als belegt.

## Nächster Schritt
1. Nutzer-Messung auswerten → Ursachen-Tabelle (gemessen ja/nein, ms, Aufwand, Risiko).
2. Phase 2: Vorschläge (Performance, Overlay mit ASCII-Skizzen, Layout, Design-Frage), max. 4 Fragen, auf Auswahl warten.
3. Erst danach Phase 3 (vorher Backup `../system_monitor_v2.1.1_backup`).
