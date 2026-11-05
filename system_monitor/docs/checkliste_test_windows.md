# Checkliste: Handtest unter Windows (Version 2.2.0)

Vorher: `py -m pytest -v` (alle grün; 4 GUI-Tests laufen nur mit Bildschirm) und `py main.py`.
Ankreuzen: ✅ geht, ❌ geht nicht (kurz notieren was), ❓ nicht geprüft.

| # | Test | Erwartung | Ergebnis |
|---|---|---|---|
| 1 | Programm starten | Fenster 880×680, dunkles Design, Kopfzeile zeigt CPU/RAM/Platte | |
| 2 | Fenster verschieben | läuft ruckelfrei, Anzeige läuft weiter | |
| 3 | Fenster vergrößern/verkleinern (bis 720×560) | nichts abgeschnitten, kein Ruckeln | |
| 4 | Tabs: Übersicht, Laufwerke, Netzwerk, Bluetooth, Updates | jeder Tab öffnet; Kopfzeile bleibt sichtbar | |
| 5 | Übersicht: Prozessliste | nach ca. 5–10 s gefüllt; danach nur alle ca. 15 s neu | |
| 6 | Anderer Tab öffnen, CPU im Task-Manager ansehen (Prozess `python.exe`) | deutlich unter 5 % eines Kerns | |
| 7 | Fenster minimieren, 30 s warten, wiederherstellen | Werte sofort wieder da, keine Fehlermeldung | |
| 8 | Pause / Fortsetzen | Anzeige friert ein / läuft weiter | |
| 9 | Einstellungen: Wert ändern, speichern, Programm neu starten | Wert bleibt erhalten | |
| 10 | Einstellungen: ungültigen Wert eingeben (z. B. Deckkraft 5) | Fehlermeldung, nichts gespeichert | |
| 11 | Overlay-Knopf drücken | Leiste erscheint oben Mitte, Zahlen laufen; Hauptfenster verschwindet (Standard) | |
| 12 | `Strg+Alt+O` drücken (auch wenn ein anderes Programm vorne ist) | Overlay aus, Hauptfenster wieder da; nochmal: Overlay an | |
| 13 | Overlay an, Maus über die Leiste klicken | Klick geht auf das Fenster darunter (Klick-Durchlässigkeit) | |
| 14 | Overlay an, im Hintergrund tippen | Eingabe bleibt im anderen Programm (kein Fokusklau) | |
| 15 | Spiel im **randlosen Fenster** starten, Overlay an | Leiste sichtbar über dem Spiel | |
| 16 | Spiel im **exklusiven Vollbild** | Overlay vermutlich nicht sichtbar (bekannte Grenze) – bitte notieren | |
| 17 | Einstellungen: Position und Deckkraft ändern | Overlay wechselt sofort | |
| 18 | Tastenkürzel auf ein belegtes ändern, neu starten | Hinweis in der Statuszeile; Hauptfenster bleibt sichtbar | |
| 19 | Last erzeugen (z. B. Video rendern) | Warnung in der Meldungsliste, Signalton | |
| 20 | Updates-Tab: Suche, dann „Ausgewählte aktualisieren“ ohne Auswahl | Hinweis, nichts startet; mit Auswahl: Sicherheitsabfrage | |
| 21 | `py main.py --once`, `--nogui`, `--updates` | Terminal-Ausgaben wie vorher | |
| 22 | `tools\messung_starten.bat` | Werte für „nachher“ in `messungen\` | |
