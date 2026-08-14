@echo off
setlocal EnableDelayedExpansion
chcp 65001 > nul 2>&1

set "APP_DIR=%~dp0"
set "STARTUP_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "DESKTOP=%USERPROFILE%\Desktop"

echo.
echo  ==========================================
echo   Instalacao - IMPRESSAO ALMOX
echo  ==========================================
echo.

:: Localiza o pythonw.exe a partir do Python atual
for /f "tokens=*" %%i in ('python -c "import sys,os; print(os.path.dirname(sys.executable))"') do set "PY_DIR=%%i"
set "PYTHONW=!PY_DIR!\pythonw.exe"

if not exist "!PYTHONW!" (
    echo AVISO: pythonw.exe nao encontrado, usando python.exe
    set "PYTHONW=!PY_DIR!\python.exe"
)

:: Gera icon.ico a partir do design do favicon
python "!APP_DIR!make_ico.py"
echo [OK] Icone gerado

:: Cria bat no Startup para iniciar servidor silenciosamente no login
(
echo @echo off
echo start "" "!PYTHONW!" "!APP_DIR!launcher.pyw" --no-browser
) > "!STARTUP_DIR!\impressao_almox.bat"
echo [OK] Inicio automatico configurado

:: Remove atalho antigo .url se existir
if exist "!DESKTOP!\IMPRESSAO ALMOX.url" del "!DESKTOP!\IMPRESSAO ALMOX.url"

:: Cria atalho .lnk que executa o launcher (inicia servidor + abre browser)
(
echo $ws = New-Object -ComObject WScript.Shell
echo $s = $ws.CreateShortcut('%DESKTOP%\IMPRESSAO ALMOX.lnk'^)
echo $s.TargetPath = '%PYTHONW%'
echo $s.Arguments = '"%APP_DIR%launcher.pyw"'
echo $s.WorkingDirectory = '%APP_DIR%'
echo $s.IconLocation = '%APP_DIR%icon.ico,0'
echo $s.WindowStyle = 7
echo $s.Save(^)
) > "%TEMP%\make_lnk.ps1"
powershell -NoProfile -ExecutionPolicy Bypass -File "%TEMP%\make_lnk.ps1"
del "%TEMP%\make_lnk.ps1" 2>nul
echo [OK] Atalho criado: IMPRESSAO ALMOX ^(area de trabalho^)

echo.
echo Iniciando servidor...
start "" "!PYTHONW!" "!APP_DIR!launcher.pyw"
timeout /t 3 /nobreak > nul

echo.
echo  ==========================================
echo   Pronto!
echo   Acesse: http://!COMPUTERNAME!:5000/
echo   (compartilhe esse link com a equipe)
echo  ==========================================
echo.
pause
