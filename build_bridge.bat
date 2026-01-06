batch@echo off
echo Building Voicemeeter WebSocket Server...

REM Lösche alte Build-Verzeichnisse
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul

REM PyInstaller Befehl
pyinstaller ^
    --onefile ^
    --noconsole ^
    --name "VoicemeeterWebSocketServer" ^
    --icon=voicemeeter_icon.png ^
    --add-data "voicemeeter_icon.png;." ^
    --hidden-import=pystray ^
    --hidden-import=PIL ^
    --hidden-import=PIL.Image ^
    --hidden-import=websockets ^
    --hidden-import=asyncio ^
    voicemeeter_push_server_tray_9014.py

echo.
echo Build abgeschlossen!
echo EXE-Datei: dist\VoicemeeterWebSocketServer.exe
pause