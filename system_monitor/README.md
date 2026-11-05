# System-Monitor (Python) – Version 2.2.0

Überwacht **CPU, Arbeitsspeicher und Festplatten**, zeigt die Prozesse mit der höchsten Last und warnt, wenn ein Schwellwert überschritten wird. Version 2 ergänzt:

- **externe Speichermedien** (USB-Stick, externe Festplatte, SD-Karte) mit Speicherplatz
- **Software-Updates über winget**
- **WLAN-Verbindung** und **Bluetooth-Geräte**
- **Datenverkehr (Up & Down)** mit Verlaufsdiagramm

Version 2.2 bringt die **Cyberpunk-Oberfläche** (Kopfzeile, Seitenleiste, Neon-Reiter, rechte Spalte mit Meldungen), ein **Overlay** in drei Stilen (Leiste, Mini-Kachel, nur Zahlen) und deutlich weniger CPU-Last (siehe „Performance“).

Das Programm läuft mit Fenster (tkinter, 5 Tabs) oder im Terminal.

![Übersicht](docs/screenshots/tab_uebersicht.png)

**Mindestgröße des Fensters:** 1020×640 (Seitenleiste und rechte Spalte brauchen die Breite). Die frühere Vorgabe 720×560 gilt für die Cyberpunk-Oberfläche nicht mehr.

> Die Screenshots in `docs/screenshots/` stammen aus Testläufen unter Linux (Linux-Schrift). `tab_uebersicht.png`, `einstellungen.png` und `overlay_*.png` zeigen die Version 2.2. Die Bilder der übrigen Tabs zeigen noch das helle Design von 2.1; ihre Windows-Ausgaben (netsh, Bluetooth, winget) waren aus Beispieltexten nachgestellt.

## Funktionen

| Tab | Inhalt | Datenquelle |
|---|---|---|
| **Seitenleiste** (immer sichtbar) | Pause, Einstellungen, Overlay, Meldungen leeren, Beenden; Schwellen und Systemwerte | – |
| **Rechte Spalte** (immer sichtbar) | Meldungen (höchstens 500) und Farblegende | – |
| **Übersicht** | CPU, RAM, Systemlaufwerk als Neon-Balken mit Schwellenstrich; Top-Prozesse (nur hier erstellt) | `psutil` |
| **Laufwerke** | alle Laufwerke mit belegtem, freiem und gesamtem Speicher; externe Medien blau markiert; Meldung beim Anstecken und Entfernen | `psutil.disk_partitions`, Bus-Typ über PowerShell `Get-Disk` |
| **Netzwerk / WLAN** | Adapter, Status, SSID, Signalstärke, Standard, Band, Kanal, Datenrate, Sicherheit | `netsh wlan show interfaces`, ersatzweise `Get-NetAdapter` |
| | Download/Upload je Sekunde, Summen seit Start, Diagramm der letzten 60 Messungen, Netzwerkkarte wählbar | `psutil.net_io_counters` |
| **Bluetooth** | Adapter, gekoppelte Geräte (Classic/LE), Verbindungsstatus | PowerShell `Get-PnpDevice` / `Get-PnpDeviceProperty` |
| **Updates** | verfügbare Updates (Name, ID, installierte und neue Version); markierte oder alle installieren | `winget upgrade` |

Weitere Funktionen:
- **Warnungs-Pause (Cooldown):** Dieselbe Warnung kommt höchstens alle 60 s.
- **Hysterese:** Die Entwarnung kommt erst, wenn der Wert 5 %-Punkte unter der Schwelle liegt.
- **Protokolle:** Warnungen und Ereignisse stehen in `logs/monitor.log` (rotierend), die Messwerte in `logs/messwerte.csv` (für Excel).
- **Flüssige Bedienung:** Messung und Abfragen laufen im Hintergrund (Details unter „Performance“).

## Overlay

Eine kleine, randlose Anzeige ganz oben auf dem Bildschirm, z. B. über einem Spiel im randlosen Fenstermodus. Es gibt drei Stile (`overlay_style`, auch im Einstellungsdialog):

| Stil | Aussehen | Größe (Linux, JetBrains Mono; unter Windows je nach Schrift anders) |
|---|---|---|
| `bar` – kompakte Leiste (Standard) | `CPU  23%  RAM  61%  ↓ 1.20 MB/s  ↑ 0.10 MB/s  14:32` | 470×28 px |
| `tile` – Mini-Kachel | CPU und RAM mit kleinem Balken und Prozent, darunter ↓ und ↑ | 184×108 px |
| `numbers` – nur Zahlen | `23% · 61% · ↓1.2M`, ohne Hintergrund (Windows: durchsichtiger Hintergrund über `-transparentcolor`) | 182×22 px |

![Leiste](docs/screenshots/overlay_bar.png) ![Kachel](docs/screenshots/overlay_tile.png) ![Zahlen](docs/screenshots/overlay_numbers.png)

- **Ein-/Ausschalten:** Knopf **OVERLAY** in der Seitenleiste oder das globale Tastenkürzel (Standard `Strg+Alt+O`, funktioniert auch, wenn ein Spiel im Vordergrund ist). Das Kürzel ist nur unter Windows verfügbar und ändert sich erst nach einem Neustart.
- **Farbe:** Cyan = normal, gelb = innerhalb von 10 Punkten unter einer Schwelle, rot = Schwelle erreicht (bei der Kachel je Balken).
- **Kein Prozess-Scan:** Das Overlay zeigt nie die Prozessliste. Ist es an und das Hauptfenster versteckt, wird nichts im Hauptfenster gezeichnet.
- **Hauptfenster verstecken** (`overlay_hide_main`): nur, wenn das Tastenkürzel wirklich registriert werden konnte. Sonst bleibt das Hauptfenster sichtbar, weil man sonst nicht mehr zurückkäme.
- **Klick-Durchlässigkeit** (`overlay_click_through`): Mausklicks gehen durch das Overlay hindurch (`WS_EX_LAYERED` + `WS_EX_TRANSPARENT`); außerdem kein Fokusklau und kein Eintrag in Taskleiste/Alt+Tab (`WS_EX_NOACTIVATE`, `WS_EX_TOOLWINDOW`).
- **Einstellungen:** Stil, Position (6 Ecken/Mitten), Deckkraft 0,2–1, Tastenkürzel, „beim Start anzeigen“ – im Einstellungsdialog (rechte Spalte) und in `config.json`.

**Grenzen (nicht verschweigen):**

| Punkt | Stand | Quelle |
|---|---|---|
| Spiele im **exklusiven Vollbild** | Ein normales Fenster liegt dort nicht darüber. Laufen Spiele mit „Fullscreen Optimizations“ (randlos-ähnlich), können Overlays gezeichnet werden. Welcher Modus bei einem Spiel gilt, hängt vom Spiel ab. | [DirectX Developer Blog, 17.12.2019](https://devblogs.microsoft.com/directx/demystifying-full-screen-optimizations/) |
| `-topmost` | „über allen Nicht-Topmost-Fenstern“; ein anderes Topmost-Fenster kann darüber liegen. | [Microsoft Learn: Extended Window Styles](https://learn.microsoft.com/en-us/windows/win32/winmsg/extended-window-styles) |
| Klick-Durchlässigkeit | Bei einem Layered Window mit `WS_EX_TRANSPARENT` gehen Mausereignisse an die Fenster darunter. | [Microsoft Learn: Window Features](https://learn.microsoft.com/en-us/windows/win32/winmsg/window-features) |
| `-alpha`, `-topmost` | in Tk auf allen Plattformen vorgesehen, `-transparentcolor` nur Windows. | [Tk-Handbuch `wm`](https://www.tcl-lang.org/man/tcl8.6/TkCmd/wm.htm) |
| Anti-Cheat | Das Overlay ist ein normales Fenster und hakt sich nicht in das Spiel ein. Ob ein bestimmtes Spiel/Anti-Cheat es toleriert, ist **nicht geprüft**. | – |
| Für exklusiven Vollbild | Nur Tools, die sich in die Grafikausgabe einklinken (z. B. RTSS/MSI Afterburner). Das ist Fremdsoftware mit eigenem Risiko; manche Spiele blockieren sie (z. B. [Roblox](https://devforum.roblox.com/t/rtss-msi-afterburner-blocked-by-hyperion/3274953)). | – |

**Getestet:** Anzeige aller drei Stile, Texte, Position und Ein-/Ausschalten unter Linux (Xvfb) per Test. **Nicht getestet** (nur unter Windows prüfbar): Klick-Durchlässigkeit, durchsichtiger Hintergrund im Stil `numbers`, Tastenkürzel, Verhalten über einem echten Spiel.

## Wichtige Hinweise (Windows)

| Thema | Hinweis |
|---|---|
| **WLAN-Name (SSID)** | Seit Windows 11 24H2 gibt `netsh wlan` WLAN-Daten nur mit Standortberechtigung heraus. Ohne sie zeigt das Programm Adapter, Status und Linkgeschwindigkeit (über `Get-NetAdapter`) und einen Hinweis. Zum Freischalten: *Einstellungen › Datenschutz und Sicherheit › Standort* → Standortdienste und „Desktop-Apps Zugriff erlauben“ einschalten. |
| **Bluetooth-Verbindungsstatus** | Windows bietet dafür keine dokumentierte Abfrage. Das Programm nutzt die Geräteeigenschaft `{83DA6326-97A6-4088-9453-A1923F573B29} 15`, die laut Praxistests bei Verbindung `True` ist. Die Quellen widersprechen sich teilweise, deshalb einmal mit einem Gerät prüfen (verbinden/trennen → „Aktualisieren“). Die Abfrage dauert einige Sekunden. |
| **Externe Laufwerke** | Externe USB-Festplatten melden sich bei Windows als „fixed“. Sie werden über den Bus-Typ (`Get-Disk`) als extern erkannt. Schlägt diese Abfrage fehl, gelten nur Wechseldatenträger (USB-Sticks, SD-Karten) als extern. |
| **Updates installieren** | Die Installation läuft über winget in einem eigenen Konsolenfenster. Vorher kommt eine Sicherheitsabfrage. Manche Installer fragen per **Benutzerkontensteuerung nach Admin-Rechten**. Auf verwalteten Rechnern (Schule, Firma) kann die Installation durch Richtlinien blockiert sein. |
| **winget fehlt** | winget gehört zum „App-Installer“ aus dem Microsoft Store. Ohne winget zeigt der Tab einen Hinweis, der Rest funktioniert normal. |

## Performance

Gemessen auf Windows 11 (Build 10.0.26300), Python 3.14.6, 14 logische CPUs, 500 laufende Prozesse, mit `tools/messung_windows.py` (Messdauer 60 s je Lauf, Fenster 880×680, nichts bedient). Quelle: eigene Läufe am 05.11.2026, Rohdaten als JSON im Ordner `messungen/` (nicht im Projekt enthalten).

**Befund in Version 2.1.1:** Die Prozessliste war die dominante Last. Jede Abfrage pro Prozess (CPU-Zeit oder Speicher) kostet auf diesem Rechner ca. 7 ms, bei 500 Prozessen **3,7 bis 5,5 s** je Aufbau. Warum es 7 ms je Prozess sind, wurde nicht untersucht. Dadurch rechnete das Programm fast dauernd, und der Hauptthread wurde ausgebremst (auch sonst schnelle Aufrufe wie `disk_usage` stiegen von 0,0 auf 19 ms).

| Messwert (Tab Übersicht / Netzwerk) | 2.1.1 mit Prozessliste | Prozessliste aus (A/B-Test) |
|---|---|---|
| CPU des Programms (% eines Kerns) | 84 / 75 | **1,0 / 0,9** |
| Timer-Verspätung, Maximum | 713 / 1204 ms | **26 / 25 ms** |
| Timer über 100 ms (in 60 s) | 177 / 143 | **0 / 0** |
| Messungen in 60 s (Soll bei 2 s: 30) | 9 / 10 | **30 / 29** |
| `_tick` im Hauptthread, Median | 213 / 610 ms | **13 / 13 ms** |
| Tab-Wechsel, Median | 33–653 ms | **24–41 ms** |
| RAM (Working Set) | 42 MB | 42 MB |

Nicht ursächlich (gemessen, jeweils unter 2 ms): Prozesstabelle neu füllen, Labels und Balken setzen, Meldungsliste (auch nach 5000 Einträgen), neuer Thread je Messung (0,1–0,2 ms), `root.bell()`, Diagramm neu zeichnen (ca. 1 ms, wenn die Prozessliste nicht stört).

**Maßnahmen in 2.2.0:**

| Maßnahme | Wirkung |
|---|---|
| Prozessliste nur, wenn das Fenster sichtbar und die Ansicht **Übersicht** offen ist (`skip_processes`); Intervall **30 s** statt 5 s (seit der Messung unten; gemessen wurde mit 15 s) und Knopf **JETZT AKTUALISIEREN** mit Anzeige „Stand hh:mm:ss“ | in jeder anderen Ansicht gemessen ca. 1 % eines Kerns. Für 30 s erwarte ich in der Übersicht rund 18 % statt 35 % Scan-Anteil (Rechnung: 5,3 s von 30 s) – **noch nicht gemessen**. |
| Netzwerkzähler werden im Mess-Thread gelesen | `_update_traffic` im Hauptthread: 0,1–1,5 ms statt 162–545 ms |
| Minimiert oder Overlay-Modus (Hauptfenster versteckt): nichts zeichnen | Messung, Warnungen und CSV laufen weiter |
| Meldungsliste auf 500 Einträge begrenzt | begrenzt den Speicher im Dauerbetrieb |
| Texte, Balken und Tabellenzeilen nur bei Änderung setzen (Neon-Oberfläche), Overlay ebenso | spart Neuzeichnen |

**Messung 2.2.0 auf Windows** (gleicher Rechner und gleiche Messung wie oben, Fenster 1220×760, Läufe vom 05.11.2026 14:52 und 14:55, **mit Prozessliste-Intervall 15 s**; der Standard ist seitdem 30 s, dazu gibt es noch keine Messung):

| Messwert (Übersicht / Netzwerk) | 2.1.1 | **2.2.0** |
|---|---|---|
| CPU sichtbar (% eines Kerns) | 84 / 75 | **34,4 / 1,0** |
| CPU minimiert (% eines Kerns) | 84 / 68 | **6,4 / 0,6** |
| Timer-Verspätung, Maximum | 713 / 1204 ms | **376 / 23 ms** |
| Timer über 50 ms (in 60 s) | 222 / 222 | **124 / 0** |
| Timer über 100 ms (in 60 s) | 177 / 143 | **69 / 0** |
| Messungen in 60 s (Soll 30) | 9 / 10 | **21 / 30** |
| `_tick` im Hauptthread, Median | 213 / 610 ms | **2,4 / 1,5 ms** |
| Tab-Wechsel, Median | 33–59 / 217–653 ms | **20–38 / 19–36 ms** |
| Fenstergröße ändern (40 Schritte), Median | 344 / 121 ms | **144 / 135 ms** |
| RAM (Working Set) | 42 MB | **42–44 MB** |

**Nachmessung mit Standardintervall 30 s** (Option A, nur Ansicht Übersicht, 05.11.2026 15:12):

| Messwert (Übersicht) | 2.1.1 | 2.2.0 mit 15 s | **2.2.0 mit 30 s** |
|---|---|---|---|
| CPU sichtbar (% eines Kerns) | 84 | 34,4 | **16,6** |
| CPU minimiert (% eines Kerns) | 84 | 6,4 | **0,6** |
| Timer-Verspätung, Maximum | 713 ms | 376 ms | **285 ms** |
| Timer über 50 ms / über 100 ms | 222 / 177 | 124 / 69 | **63 / 34** |
| Messungen in 60 s (Soll 30) | 9 | 21 | **25** |
| Prozess-Scans in 60 s (je Median) | 9 (5,6 s) | 4 (5,3 s) | **2 (5,1 s)** |
| Tab-Wechsel, Median | 33–59 ms | 20–38 ms | **22–40 ms** |
| Fenstergröße ändern, Median / P95 | 344 / 1458 ms | 144 / 1254 ms | **143 / 181 ms** |

2 Scans × 5,1 s = 10 s von 60 s, also etwa 17 %; gemessen wurden 16,6 % eines Kerns. Das passt zusammen. Die Oberfläche ruckelt nur noch, **während** ein Scan läuft (Timer bis 285 ms, `_show_drives` bis 83 ms statt 0,3 ms); außerhalb davon ist alles unter 30 ms. Das spricht dafür, dass die Scan-Abfragen Python während des Scans zeitweise festhalten. Bewiesen ist das nicht.

**Einordnung:**
- **Netzwerk-Ansicht (und jede Ansicht außer Übersicht):** deutlich besser, 1 % eines Kerns, keine Verspätung über 50 ms, volle 30 Messungen pro Minute.
- **Übersicht:** CPU von 84 % auf 34 % eines Kerns gesenkt, Ruckler aber nicht weg. Die Prozessliste lief im Test viermal in 60 s und dauerte jeweils ca. 5,3 s (Median). 4 × 5,3 s = 21 s, also etwa 35 % der Zeit; das passt zur gemessenen CPU. Während dieser Zeit stockt die Oberfläche (Timer bis 376 ms, `_show_drives` bis 140 ms) und es werden weniger Messungen gemacht (21 statt 30). Die Ursache der Stocker ist **nicht bewiesen**; vermutlich halten die Abfragen pro Prozess Python lange fest.
- **Minimiert 6,4 % in der Übersicht (15 s):** In der Nachmessung mit 30 s waren es 0,6 %. Das passt zu einem auslaufenden Scan aus der Phase davor, ist aber nicht bewiesen.
- **Fenstergröße ändern:** 135–144 ms je Schritt (Tk-Layout der Neon-Oberfläche). In der Übersicht bis 1,3 s, wenn dabei gerade ein Prozess-Scan läuft. Ursache nicht untersucht.

Früher eingebaut (ab 2.1, weiter aktiv): Messung im Hintergrund-Thread, Threadwechsel 1 ms (`sys.setswitchinterval`), WLAN/Bluetooth nur bei geöffnetem Tab, winget erst beim Öffnen des Updates-Tabs, CSV gebündelt alle 30 s, `memory_percent` selbst berechnet.

**Korrektur in 2.1.1:** In 2.1 zeigte die CPU-Anzeige dauerhaft 0 %. Ursache: `psutil.cpu_percent()` merkt sich seinen Vergleichswert pro Thread, und jede Messung läuft in einem neuen Hintergrund-Thread. Die Auslastung wird jetzt selbst aus den CPU-Zeiten berechnet (`collector.cpu_percent_between`).

**Auf deinem Rechner prüfen:** In der Statusleiste steht die **Messdauer** jedes Zyklus. Dauert ein Zyklus länger als 1 s, steht zusätzlich eine Warnung in `logs/monitor.log`. Wenn die Prozessliste weiter stört, `process_interval_s` erhöhen.

## Voraussetzungen

- Windows 10/11 (alle Funktionen). Unter Linux/macOS laufen nur Übersicht, Laufwerke und Datenverkehr.
- Python **3.10 oder neuer** (getestet mit 3.12 und 3.13)
- Bibliothek `psutil`
- `tkinter` für das Fenster (bei Python von python.org dabei)

## Installation (Windows)

Im Ordner, in dem `main.py` liegt:

```bat
py -m pip install -r requirements.txt
```

Bei „Zugriff verweigert“: `py -m pip install --user -r requirements.txt`. Admin-Rechte sind nicht nötig.

## Start

```bat
start.bat                 :: per Doppelklick: Fenster
py main.py                :: Fenster
py main.py --nogui        :: Terminal (Auslastung, Laufwerke, Datenverkehr), Beenden mit Strg+C
py main.py --once         :: einmalige Ausgabe inkl. WLAN und Bluetooth
py main.py --updates      :: verfügbare winget-Updates auflisten
```

## Konfiguration (`config.json`)

| Schlüssel | Standard | Bedeutung |
|---|---|---|
| `interval_s` | 2.0 | Messintervall in Sekunden (0,5 – 3600) |
| `cpu_threshold` / `ram_threshold` / `disk_threshold` | 85 / 85 / 90 | Warnschwellen in % |
| `hysteresis` | 5 | Abstand zur Schwelle für die Entwarnung |
| `disk_path` | `""` | Laufwerk für die Übersicht; leer = Systemlaufwerk |
| `alert_cooldown_s` | 60 | Mindestabstand gleicher Warnungen in s |
| `top_processes` | 10 | Anzahl angezeigter Prozesse |
| `process_interval_s` | 30 | Prozessliste neu erstellen alle n s (teuerster Teil der Messung, nur bei sichtbarer Übersicht); sofort per Knopf **JETZT AKTUALISIEREN** |
| `csv_logging` | true | Messwerte in CSV schreiben |
| `csv_flush_s` | 30 | CSV gebündelt alle n s schreiben (0 = sofort) |
| `log_dir` | `"logs"` | Ordner für Log und CSV |
| `net_interface` | `""` | Netzwerkkarte für den Datenverkehr, z. B. `"Ethernet"`; leer = WLAN automatisch |
| `drive_refresh_s` | 10 | Laufwerke neu einlesen alle n s |
| `wlan_refresh_s` | 15 | WLAN-Status neu abfragen alle n s |
| `bt_refresh_s` | 60 | Bluetooth neu abfragen alle n s (nur bei geöffnetem Tab) |
| `check_updates_on_start` | false | sofort beim Start nach Updates suchen; sonst beim ersten Öffnen des Tabs |
| `overlay_enabled` | false | Overlay beim Start anzeigen |
| `overlay_style` | `"bar"` | `bar` (Leiste), `tile` (Mini-Kachel), `numbers` (nur Zahlen) |
| `overlay_position` | `"top-center"` | `top-`/`bottom-` + `left`/`center`/`right` |
| `overlay_alpha` | 0.7 | Deckkraft 0,2 – 1 |
| `overlay_click_through` | true | Mausklicks gehen durch das Overlay |
| `overlay_hotkey` | `"ctrl+alt+o"` | globales Kürzel (mind. ein Modifikator + A–Z, 0–9 oder F1–F12); wirkt nach Neustart |
| `overlay_hide_main` | true | Hauptfenster verstecken, solange das Overlay an ist (nur bei funktionierendem Kürzel) |

Die meisten Werte lassen sich auch im Programm unter **Einstellungen** ändern.

## Projektstruktur

```
system_monitor/
├── main.py              Einstiegspunkt: Parameter, Konfiguration, Moduswahl
├── config.json, requirements.txt, start.bat
├── monitor/
│   ├── config.py        Config: laden, prüfen, speichern
│   ├── collector.py     SystemCollector: CPU, RAM, Festplatte, Prozesse → Snapshot
│   ├── alerts.py        AlertManager: Grenzwerte mit Cooldown und Hysterese
│   ├── storage.py       Logdatei und CsvWriter
│   ├── core.py          Monitor: ein Messzyklus (step mit skip_processes)
│   ├── drives.py        NEU: DriveScanner – alle Laufwerke, extern/intern
│   ├── network.py       NEU: WLAN (netsh-Parser) und TrafficMeter
│   ├── bluetooth.py     NEU: Bluetooth-Adapter und -Geräte
│   ├── updates.py       NEU: winget-Parser und Update-Start
│   ├── winutil.py       NEU: Befehle ausführen, Codepage, PowerShell-JSON
│   ├── tasks.py         NEU: BackgroundRunner (Threads + Queue)
│   ├── gui.py           Cyberpunk-Oberfläche: MonitorApp, NeonButton, NeonBar, SettingsDialog
│   ├── overlay.py       NEU 2.2: OverlayWindow (3 Stile), MiniBar, HotkeyListener (nur Windows)
│   ├── overlay_logic.py NEU 2.2: Position, Texte, Stile, Tastenkürzel (ohne tkinter testbar)
│   └── cli.py           Terminal-Ausgabe
├── tests/               pytest (96 Tests, 8 davon brauchen einen Bildschirm)
├── tools/               temporäre Messskripte für Windows (nicht Teil des Programms)
└── docs/
    ├── pap_hauptprogramm.*   PAP 1: Hauptprogramm
    ├── pap_grenzwerte.*      PAP 2: Unterprogramm „Grenzwerte prüfen“
    ├── pap_updates.*         PAP 3: Updates suchen und installieren
    ├── klassendiagramm.*     UML-Klassendiagramm
    ├── Diagramme.pdf         alle vier Diagramme
    ├── screenshots/          ein Bild pro Tab
    └── src/*.dot             Quellen (Graphviz)
```

## Funktionsweise der Erweiterungen

**Hintergrundabfragen (`tasks.py`):** tkinter darf nur aus dem Haupt-Thread bedient werden. Die Messung und alle langsamen Abfragen laufen deshalb in einem eigenen Thread und legen ihr Ergebnis in eine `queue.Queue`. Das Fenster holt die Ergebnisse alle 100 ms mit `poll()` ab und aktualisiert dann den Tab. Pro Abfrage läuft höchstens ein Thread gleichzeitig.

**Datenverkehr (`network.TrafficMeter`):** Rate = (Bytezähler jetzt − Bytezähler vorher) / vergangene Zeit. Ein Zählersprung nach unten, z. B. nach einem Adapter-Neustart, ergibt 0 statt eines negativen Werts.

**WLAN (`network.parse_netsh_interfaces`):** Die Zeilen `Schlüssel : Wert` werden ausgewertet, für deutsche und englische Ausgaben. netsh gibt Text in der OEM-Codepage (cp850) aus. `winutil.decode_output` versucht zuerst UTF-8 und sonst die OEM-Codepage, damit „Übertragungsrate“ richtig erkannt wird.

**Updates (`updates.parse_winget_upgrade`):** winget hat ohne Zusatzmodul keine maschinenlesbare Ausgabe. Der Parser entfernt deshalb die Fortschrittszeichen, sucht die Trennlinie `-----` und bestimmt die Spaltenanfänge aus der Kopfzeile. Das funktioniert unabhängig von der Sprache. Zeilen ohne gültige ID, etwa die Zusammenfassung „3 Aktualisierungen verfügbar.“, werden übersprungen. Paket-IDs werden vor dem Start geprüft (nur `A–Z 0–9 . - _ +`), damit keine fremden Befehle eingeschleust werden können.

**Laufwerke (`drives.DriveScanner`):** `psutil` liefert die Laufwerke sofort. Die langsamere PowerShell-Abfrage des Bus-Typs (USB, NVMe, SATA) läuft nur, wenn ein Laufwerk hinzukommt oder wegfällt.

## Tests

```bat
py -m pip install pytest
py -m pytest -v
```

Getestet werden außerdem das Overlay (Position, Text, Tastenkürzel), die neuen Einstellungen, das Überspringen der Prozessliste und ein Rauchtest der Oberfläche (übersprungen ohne Bildschirm). Getestet werden die Parser (netsh deutsch/englisch inkl. cp850, winget deutsch/englisch inkl. Fortschrittsanzeige, Bluetooth-JSON), die Traffic-Berechnung mit simulierten Zählern, die Laufwerkserkennung, die Hintergrund-Threads, die Grenzwertlogik und die Konfiguration.

**Nicht getestet:** Die Tests liefen unter Linux (Python 3.12/3.13), die Messungen unter Windows (Python 3.14). Die echten Windows-Befehle (netsh, PowerShell, winget) und die Update-Installation konnten dort nicht ausgeführt werden. Die Parser sind nur gegen nachgestellte Beispielausgaben geprüft.

## Erweiterungsideen

- Verfügbare WLAN-Netze in der Umgebung auflisten (`netsh wlan show networks`, braucht ebenfalls Standortrecht)
- Ping/Latenz zum Router und ins Internet
- Benachrichtigung als Windows-Toast oder per E-Mail
- Autostart über die Aufgabenplanung
