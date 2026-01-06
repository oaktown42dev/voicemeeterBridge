import PyInstaller.__main__
import os
import shutil

# Define paths
work_dir = os.path.dirname(os.path.abspath(__file__))
script = os.path.join(work_dir, 'voicemeeter_server_universal.py')
icon = os.path.join(work_dir, 'icon.ico') # Optional, might check if exists

build_args = [
    script,
    '--onefile',
    '--noconsole',
    '--name=VoicemeeterBridge',
    '--clean',
    '--noconfirm',
    # Add hidden imports if necessary
    '--hidden-import=pystray', 
    '--hidden-import=PIL',
    '--hidden-import=websockets',
]

if os.path.exists(icon):
    build_args.append(f'--icon={icon}')

print("Starting Build...")
PyInstaller.__main__.run(build_args)
print("Build Complete. Check 'dist' folder.")