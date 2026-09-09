@echo off
rem Remove o doubleclickfix da inicializacao e encerra o processo.
del "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\doubleclickfix.cmd" 2>nul
powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'pythonw.exe' -and $_.CommandLine -like '*doubleclickfix.py*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }" >nul 2>&1
echo Removido. O mouse volta a se comportar como antes (com o duplo clique fantasma).
pause
