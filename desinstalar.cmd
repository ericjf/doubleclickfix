@echo off
rem Remove o doubleclickfix da inicializacao e encerra o processo.
del "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\doubleclickfix.cmd" 2>nul
wmic process where "name='pythonw.exe' and commandline like '%%doubleclickfix.py%%'" call terminate >nul 2>&1
echo Removido. O mouse volta a se comportar como antes (com o duplo clique fantasma).
pause
