import PyInstaller.__main__
import os
import shutil

# Define paths
work_dir = os.path.dirname(os.path.abspath(__file__))
script = os.path.join(work_dir, 'voicemeeter_server_universal.py')
icon = os.path.join(work_dir, 'icon.ico') 

# FOLDER BUILD (onedir)
# Less likely to trigger AV heuristics because it doesn't unpack into temp memory
build_args = [
    script,
    '--onedir', # Folder mode instead of --onefile
    '--noconsole',
    '--name=VoicemeeterBridge_Folder',
    '--clean',
    '--noconfirm',
    # Add hidden imports due to dynamic internal Logic
    '--hidden-import=pystray', 
    '--hidden-import=PIL',
    '--hidden-import=websockets',
]

if os.path.exists(icon):
    build_args.append(f'--icon={icon}')

print("Starting Folder Build (AV-Safe Mode)...")
PyInstaller.__main__.run(build_args)
print("Build Complete. Check 'dist/VoicemeeterBridge_Folder' folder.")
