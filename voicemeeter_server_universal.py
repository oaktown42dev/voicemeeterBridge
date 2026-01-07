import asyncio
import json
import websockets
import ctypes
import os
import sys
import threading
import pystray
import logging
from PIL import Image, ImageDraw

# Configure logging to file (accessible for user debugging)
log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bridge.log')
logging.basicConfig(
    filename=log_file,
    level=logging.INFO, # Changed to INFO to reduce debug noise
    format='%(asctime)s - %(levelname)s - %(message)s',
    filemode='w'
)

def log(msg):
    # Print mainly for dev, in EXE this goes nowhere usually (unless console)
    print(msg) 
    logging.info(msg)

def load_config():
    default_config = {
        "server": {"host": "0.0.0.0", "port": 9014},
        "voicemeeter": {"delay": 0.05}
    }
    try:
        if os.path.exists("config.json"):
            with open("config.json", "r") as f:
                loaded = json.load(f)
                if "server" in loaded: default_config["server"].update(loaded["server"])
                if "voicemeeter" in loaded: default_config["voicemeeter"].update(loaded["voicemeeter"])
    except Exception as e:
        log(f"Error loading config: {e}")
    return default_config

def get_vm_dll():
    paths = [
        r"C:\Program Files (x86)\VB\Voicemeeter\VoicemeeterRemote64.dll",
        r"C:\Program Files\VB\Voicemeeter\VoicemeeterRemote64.dll",
        r"C:\Program Files (x86)\VB\Voicemeeter\VoicemeeterRemote.dll",
        r"C:\Program Files\VB\Voicemeeter\VoicemeeterRemote.dll"
    ]
    for p in paths:
        if os.path.exists(p):
            try:
                log(f"Loading DLL from: {p}")
                return ctypes.CDLL(p)
            except Exception as e:
                log(f"Failed to load {p}: {e}")
    return None

config = load_config()
dll = get_vm_dll()
running = True

class VMBridge:
    def __init__(self):
        if not dll: 
            log("CRITICAL: Voicemeeter DLL not found!")
            raise Exception("Voicemeeter DLL nicht gefunden!")
        
        # Setup Argtypes for safety
        try:
            dll.VBVMR_Login.restype = ctypes.c_long
            dll.VBVMR_GetParameterFloat.restype = ctypes.c_long
            dll.VBVMR_GetParameterFloat.argtypes = [ctypes.c_char_p, ctypes.POINTER(ctypes.c_float)]
        except Exception as e:
            log(f"Warning setting argtypes: {e}")

        res = dll.VBVMR_Login()
        log(f"VBVMR_Login result: {res}")
        self.cache = {}
        
    def get_param(self, name):
        val = ctypes.c_float()
        res = dll.VBVMR_GetParameterFloat(name.encode('ascii'), ctypes.byref(val))
        if res == 0:
            return val.value
        else:
            log(f"READ ERROR {name} -> Code {res}")
            return None

    def set_param(self, name, val):
        # Feedback prevention: Ignore updates that are very close to the current cached value
        current_val = self.cache.get(name)
        if current_val is not None and abs(current_val - val) < 0.1:
            # log(f"Ignored feedback/jitter for {name}: cur={current_val} new={val}")
            return
            
        log(f"SET {name} -> {val}")
        dll.VBVMR_SetParameterFloat(name.encode('ascii'), ctypes.c_float(val))
        # Optimistically update cache to prevent immediate echo handling issues
        self.cache[name] = val

    def get_all_states(self):
        """Sammelt den aktuellen Zustand aller überwachten Parameter."""
        state = {}
        for i in range(8):
            for p in ["Gain", "Mute", "Solo"]:
                name = f"Strip[{i}].{p}"
                v = self.get_param(name)
                if v is not None: 
                    state[name] = v
                    self.cache[name] = v  # Update cache
                    # Log initial gain for debugging startup
                    if p == "Gain": log(f"Init State {name} = {v}")
            for p in ["Gain", "Mute"]:
                name = f"Bus[{i}].{p}"
                v = self.get_param(name)
                if v is not None: 
                    state[name] = v
                    self.cache[name] = v  # Update cache
        return state

    def get_levels(self):
        levels = []
        for i in range(16):
            val = ctypes.c_float()
            dll.VBVMR_GetLevel(0, i, ctypes.byref(val))
            levels.append(val.value)
        return levels

    async def send_initial_state(self, ws):
        log("Sending Initial State...")
        st = self.get_all_states()
        await ws.send(json.dumps({
            "type": "welcome",
            "current_state": st
        }))
        log("Initial State Sent.")

    async def handle(self, ws):
        log(f"New Client Connected: {ws.remote_address}")
        await self.send_initial_state(ws)

        async def send_loop():
            while running:
                try:
                    is_dirty = dll.VBVMR_IsParametersDirty()
                    if is_dirty == 1:
                        changes = []
                        for i in range(8):
                            for p in ["Gain", "Mute", "Solo"]:
                                name = f"Strip[{i}].{p}"
                                v = self.get_param(name)
                                if self.cache.get(name) != v:
                                    self.cache[name] = v
                                    changes.append({"parameter": name, "value": v})
                                    # Log changes to valid parameters
                                    log(f"Changed: {name} = {v}")
                            # Bus logic...
                            for p in ["Gain", "Mute"]:
                                name = f"Bus[{i}].{p}"
                                v = self.get_param(name)
                                if v is not None:
                                    if self.cache.get(name) != v:
                                        self.cache[name] = v
                                        changes.append({"parameter": name, "value": v})
                        if changes:
                            await ws.send(json.dumps({"type": "parameter_update", "changes": changes}))
                    elif is_dirty < 0:
                        log(f"Target Dirty Error: {is_dirty}")
                    
                    # PRODUCTION: Enable level updates, but DO NOT log them (spam prevention)
                    await ws.send(json.dumps({"type": "level_update", "levels": self.get_levels()}))
                    
                    await asyncio.sleep(config['voicemeeter']['delay'])
                except Exception as e:
                    log(f"Error in send_loop: {e}")
                    await asyncio.sleep(1)

        async def recv_loop():
            try:
                async for msg in ws:
                    # Log commands (low frequency)
                    log(f"Received: {msg}")
                    data = json.loads(msg)
                    if "command" in data:
                        if data["command"] == "sync":
                            log("Command: SYNC")
                            await self.send_initial_state(ws)
                            continue
                            
                        # Handle Set Commands
                        t = "Strip" if "Strip" in data['command'] else "Bus"
                        idx = data.get('strip') if t == "Strip" else data.get('bus')
                        val = data.get('value', 0)
                        param = data['command'].replace(f"set{t}", "")
                        self.set_param(f"{t}[{idx}].{param}", val)
            except Exception as e:
                log(f"Client Disconnected/Error: {e}")

        await asyncio.gather(send_loop(), recv_loop())

def setup_tray():
    try:
        # Simple Tray Icon
        img = Image.new('RGB', (64, 64), (30, 30, 30))
        ImageDraw.Draw(img).ellipse((10, 10, 54, 54), fill=(0, 200, 100))
        
        def exit_app(icon, item):
            global running
            running = False
            icon.stop()
            os._exit(0)

        icon = pystray.Icon("VM", img, "VM Bridge", menu=pystray.Menu(pystray.MenuItem("Exit", exit_app)))
        icon.run()
    except Exception as e:
        log(f"Tray Error: {e}")

async def main():
    bridge = VMBridge()
    log(f"Starting Server on {config['server']['host']}:{config['server']['port']}")
    # Use 0.0.0.0 explicitly if configured
    host = config['server']['host']
    port = config['server']['port']
    async with websockets.serve(bridge.handle, host, port):
        while running: 
            await asyncio.sleep(1)

if __name__ == "__main__":
    # Start Tray in separate thread
    threading.Thread(target=setup_tray, daemon=True).start()
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log("Stopping...")
    except Exception as e:
        log(f"Fatal Error: {e}")