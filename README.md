# Voicemeeter Node-RED Bridge

A Python-based bridge to control Voicemeeter from Node-RED, including a standalone executable build.

## Features
- **Two-way Sync**: Adjusts faders in real-time and reflects changes from Voicemeeter back to Node-RED.
- **Robust Connection**: Uses `voicemeeter-remote.dll` for reliable communication.
- **Frontend Dashboard**: Custom UI templates for Node-RED Dashboard showing fader positions and VU meters.
- **Standalone Mode**: Can be built into a single EXE (Tray Application) without requiring Python on the target machine.

## Prerequisites
- Windows OS
- [Voicemeeter](https://vb-audio.com/Voicemeeter/) (Standard, Banana, or Potato) installed.
- [Node-RED](https://nodered.org/) installed.
- Python 3.10+ (only for development/building).

## Installation

### A. Using the Executable (No Python required)
1. Go to `dist/VoicemeeterBridge_Folder` (after building).
2. Run `VoicemeeterBridge_Folder.exe`.
3. An icon will appear in the system tray.

### B. Running from Source
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the server:
   ```bash
   python voicemeeter_server_universal.py
   ```

## Node-RED Setup
1. Import `node-red_voicemeeeter.json` into Node-RED.
2. Deploy the flow.
3. Open the Dashboard (`/ui`).

## Building the Executable
If you modify the Python code, you can rebuild the EXE:

```bash
# Build folder-based (Anti-Virus friendly)
python build_folder.py

# Build single-file (May trigger AV false positives)
python build.py
```

## Troubleshooting
- **Faders reset on load**: Fixed by adding a 1s delay to the sync command in Node-RED.
- **Antivirus blocks EXE**: Use the `build_folder.py` output or whitelist the file.
- **Port Conflict**: Ensure only one instance of the bridge is running (check Task Manager for `python` or `VoicemeeterBridge`).
