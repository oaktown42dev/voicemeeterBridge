@echo off
echo Building Voicemeeter WebSocket Server...

REM Clean up old build directories
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul

REM PyInstaller Command
pyinstaller ^
    --onefile ^
    --noconsole ^
    --name "VoicemeeterBridge" ^
    --icon=voicemeeter_icon.ico ^
    --add-data "voicemeeter_icon.png;." ^
    --hidden-import=pystray ^
    --hidden-import=PIL ^
    --hidden-import=PIL.Image ^
    --hidden-import=websockets ^
    --hidden-import=asyncio ^
    voicemeeter_push_server_tray_9014_fin.py

echo.
if exist "dist\VoicemeeterBridge.exe" (
    echo Build successful!
    echo EXE file located at: dist\VoicemeeterBridge.exe
) else (
    echo Build FAILED!
)
pause
