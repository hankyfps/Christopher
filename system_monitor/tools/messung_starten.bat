@echo off
rem Messung vorher: Uebersicht + Netzwerk (ca. 5 Minuten). Maus/Tastatur nicht benutzen!
cd /d "%~dp0\.."
if exist ".venv\Scripts\python.exe" (set PY=".venv\Scripts\python.exe") else (set PY=py)
echo Lauf 1 von 2: Tab Uebersicht (3 kurze Toene sind normal)
%PY% tools\messung_windows.py --tab uebersicht --label vorher
echo.
echo Lauf 2 von 2: Tab Netzwerk
%PY% tools\messung_windows.py --tab netzwerk --label vorher --ohne-bell
echo.
echo FERTIG. Ergebnisse liegen im Ordner messungen\ . Bitte die Ausgabe oben oder die .json-Dateien schicken.
pause
