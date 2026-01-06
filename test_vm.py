import ctypes
import os
import sys
import time

# Helper to load DLL
def load_dll():
    # Try 64-bit
    path64 = os.path.join(os.environ["ProgramFiles(x86)"], "VB", "Voicemeeter", "VoicemeeterRemote64.dll")
    if os.path.exists(path64):
        print(f"Loading 64-bit DLL: {path64}")
        return ctypes.CDLL(path64)
    
    # Try 32-bit
    path32 = os.path.join(os.environ["ProgramFiles(x86)"], "VB", "Voicemeeter", "VoicemeeterRemote.dll")
    if os.path.exists(path32):
        print(f"Loading 32-bit DLL: {path32}")
        return ctypes.CDLL(path32)
    
    print("Error: Could not find Voicemeeter Remote DLL.")
    return None

def test():
    dll = load_dll()
    if not dll:
        return

    # Define function signatures
    dll.VBVMR_Login.restype = ctypes.c_long
    dll.VBVMR_Logout.restype = ctypes.c_long
    dll.VBVMR_GetParameterFloat.restype = ctypes.c_long
    dll.VBVMR_GetParameterFloat.argtypes = [ctypes.c_char_p, ctypes.POINTER(ctypes.c_float)]

    # Login
    print("Attempting Login...")
    res = dll.VBVMR_Login()
    if res != 0:
        print(f"Login failed/warning. Code: {res}")
        # Assuming 0 is OK, 1 might be 'already logged in' which is fine
        if res < 0:
            return
    else:
        print("Login OK.")

    # Check Dirty
    time.sleep(0.5) # Give it a moment to sync
    
    # Read Parameters
    strips = [0, 1, 2, 3, 4, 5, 6, 7]
    for i in strips:
        param_name = f"Strip[{i}].Gain"
        val = ctypes.c_float()
        res = dll.VBVMR_GetParameterFloat(param_name.encode('ascii'), ctypes.byref(val))
        
        if res == 0:
            print(f"Strip[{i}].Gain = {val.value:.2f}")
        else:
            print(f"Strip[{i}].Gain = ERROR ({res})")

    dll.VBVMR_Logout()
    print("Logout done.")

if __name__ == "__main__":
    test()
