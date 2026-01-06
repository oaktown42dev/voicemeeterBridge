@echo off
echo ========================================
echo Cleanup und Neu-Build
echo ========================================
echo.

REM Stelle sicher, dass wir im richtigen Ordner sind
cd /d "C:\voicemeeter-bridge"
echo Arbeitsverzeichnis: %CD%
echo.

REM Schritt 1: Beende alle laufenden Prozesse
echo [1/6] Beende laufende Prozesse...
taskkill /F /IM "VoicemeeterWebSocketServer.exe" 2>nul
taskkill /F /IM "python.exe" 2>nul
timeout /t 2 >nul
echo OK
echo.

REM Schritt 2: Lösche alte Build-Artefakte
echo [2/6] Lösche alte Build-Dateien...
if exist "dist" (
    rmdir /s /q "dist"
    echo   - dist/ gelöscht
)
if exist "build" (
    rmdir /s /q "build"
    echo   - build/ gelöscht
)
if exist "__pycache__" (
    rmdir /s /q "__pycache__"
    echo   - __pycache__/ gelöscht
)
echo OK
echo.

REM Schritt 3: Lösche ALLE .spec Dateien
echo [3/6] Lösche alte .spec Dateien...
for %%f in (*.spec) do (
    del /q "%%f"
    echo   - %%f gelöscht
)
echo OK
echo.

REM Schritt 4: Prüfe welche Python-Datei wir haben
echo [4/6] Prüfe Python-Dateien...
if exist "voicemeeter_server_CORRECT.py" (
    set SCRIPT=voicemeeter_server_CORRECT.py
    echo   [OK] voicemeeter_server_CORRECT.py gefunden
) else (
    echo   [FEHLER] voicemeeter_server_CORRECT.py nicht gefunden!
    pause
    exit /b 1
)
echo.

REM Schritt 5: Version Check
echo [5/6] Prüfe Version...
findstr /C:"current_state" "%SCRIPT%" >nul
if errorlevel 1 (
    echo   [FEHLER] current_state fehlt in %SCRIPT%!
    echo   Diese Datei ist NICHT korrekt!
    pause
    exit /b 1
)
findstr /C:"Sending welcome message" "%SCRIPT%" >nul
if errorlevel 1 (
    echo   [WARNUNG] Logging fehlt, aber current_state vorhanden
) else (
    echo   [OK] Korrekte Version erkannt
)
echo.

REM Schritt 6: Build
echo [6/6] Starte Build mit %SCRIPT%...
echo.
python -m PyInstaller ^
    --clean ^
    --onedir ^
    --windowed ^
    --name "VoicemeeterWebSocketServer" ^
    --icon=voicemeeter_icon.png ^
    --add-data "voicemeeter_icon.png;." ^
    --hidden-import=pystray._win32 ^
    --hidden-import=PIL._tkinter_finder ^
    --collect-all pystray ^
    "%SCRIPT%"

if errorlevel 1 (
    echo.
    echo [FEHLER] Build fehlgeschlagen!
    pause
    exit /b 1
)

echo.
echo ========================================
echo BUILD ERFOLGREICH!
echo ========================================
echo.
echo Die .exe findest du hier:
echo   %CD%\dist\VoicemeeterWebSocketServer\
echo.
echo WICHTIG: Teste jetzt die .exe!
echo   1. Starte: VoicemeeterWebSocketServer.exe
echo   2. Prüfe Log: voicemeeter_service.log
echo   3. Schaue nach: "Sending welcome message"
echo.

explorer "dist\VoicemeeterWebSocketServer"

pause
```

## 🚀 Verwendung

1. **Speichere das Script** im **Hauptordner**: `C:\voicemeeter-bridge\cleanup_and_build.bat`

2. **Führe es aus**:
```
   cleanup_and_build.bat