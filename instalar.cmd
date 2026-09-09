@echo off
setlocal
rem Instala o doubleclickfix para iniciar junto com o Windows (so para o seu usuario, sem admin).
set "DIR=%~dp0"
set "PYW="
for /f "delims=" %%p in ('where pythonw.exe 2^>nul') do if not defined PYW set "PYW=%%p"
if not defined PYW (
  for /f "delims=" %%p in ('py -3 -c "import sys,os;print(os.path.join(os.path.dirname(sys.executable),'pythonw.exe'))" 2^>nul') do set "PYW=%%p"
)
if not defined PYW (
  echo Python 3 nao encontrado. Instale em https://www.python.org/downloads/ marcando "Add python.exe to PATH" e rode de novo.
  pause & exit /b 1
)
set "STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
> "%STARTUP%\doubleclickfix.cmd" echo @start "" "%PYW%" "%DIR%doubleclickfix.py"
start "" "%PYW%" "%DIR%doubleclickfix.py"
echo.
echo Instalado. Esta rodando agora e vai abrir sozinho a cada login.
echo Atalho criado em: %STARTUP%\doubleclickfix.cmd
echo Para remover, rode desinstalar.cmd
echo.
pause
