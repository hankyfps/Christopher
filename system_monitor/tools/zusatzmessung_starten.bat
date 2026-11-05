@echo off
rem Zusatzmessung: Diagnose Prozessliste + Lauf ohne Prozessliste (ca. 6 Minuten). Maus/Tastatur nicht benutzen!
cd /d "%~dp0\.."
if exist ".venv\Scripts\python.exe" (set PY=".venv\Scripts\python.exe") else (set PY=py)
echo Teil 1 von 3: Diagnose Prozessliste
%PY% tools\prozess_diagnose.py
echo.
echo Teil 2 von 3: Uebersicht OHNE Prozessliste
%PY% tools\messung_windows.py --tab uebersicht --label ohneprozess --prozess-intervall 3600 --ohne-bell
echo.
echo Teil 3 von 3: Netzwerk OHNE Prozessliste
%PY% tools\messung_windows.py --tab netzwerk --label ohneprozess --prozess-intervall 3600 --ohne-bell
echo.
echo FERTIG. Bitte die Ausgabe oben schicken (alles markieren, kopieren) oder die .json-Dateien aus messungen\ .
pause
