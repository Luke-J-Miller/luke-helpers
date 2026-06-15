import time
import sys
import hashlib
import numpy as np
from io import StringIO
from IPython.core.magic import register_cell_magic
from IPython.display import Audio, display

# =====================================================================
# GLOBAL FOOTPRINT CONFIGURATION
# =====================================================================
OUTPUT_CACHE = {}
VALID_STATES = {'run', 'log', 'log_and_lock', 'lock'}

# =====================================================================
# UTILITY 1: NATIVE SINE-WAVE BEEP
# =====================================================================
def play_beep(duration=0.4, frequency=523.25):
    """Plays a pure sine wave tone directly through the browser frontend."""
    sample_rate = 22050
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    wave_data = np.sin(2 * np.pi * frequency * t)
    display(Audio(wave_data, rate=sample_rate, autoplay=True))

# =====================================================================
# UTILITY 2: NETWORK CHIME SOUND
# =====================================================================
def play_chime():
    """Triggers a clean, professional web notification sound asset."""
    chime_url = "https://actions.google.com/sounds/v1/notifications/giggle_short.ogg"
    display(Audio(url=chime_url, autoplay=True))

# =====================================================================
# CELL MAGIC: THE CORE PROCESS ENGINE
# =====================================================================
@register_cell_magic
def process(line, cell):
    """Unified cell controller utilizing cryptographic content hashing."""
    clean_line = line.split('#')[0].strip()
    tokens = clean_line.split()
    state = tokens[0].lower() if tokens else 'log_and_lock'

    if state not in VALID_STATES:
        raise ValueError(f"❌ Invalid state '{state}'. Choose from {list(VALID_STATES)}")

    cell_hash = hashlib.sha256(cell.encode('utf-8')).hexdigest()[:8]
    key = f"hash_{cell_hash}"
    ip = get_ipython()

    def _execute_and_capture():
        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()
        t0 = time.perf_counter()
        try:
            ip.run_cell(cell)
        finally:
            sys.stdout = old_stdout
        return captured_output.getvalue(), time.perf_counter() - t0

    # State Matrix Router
    if state == 'lock':
        if key not in OUTPUT_CACHE:
            print(f"⚠️ [LOCK WARNING] No cached data found. Run as 'log' first.")
            return None
        cached_text, orig_dur = OUTPUT_CACHE[key]
        print(f"🔒 [OUTPUT LOCKED - RESTORED BLOCK ID: {key}]")
        print(cached_text.strip())
        print(f"⏱️ [LOCK] Restored Original Execution Time: {orig_dur:.4f} seconds")
        return None

    elif state == 'log_and_lock' and key in OUTPUT_CACHE:
        cached_text, orig_dur = OUTPUT_CACHE[key]
        print(f"🔒 [LOG_AND_LOCK] Stable code signature '{key}' recognized. Bypassing execution.")
        print(cached_text.strip())
        print(f"⏱️ [LOG_AND_LOCK] Restored Original Execution Time: {orig_dur:.4f} seconds")
        return None

    elif state == 'run':
        t0 = time.perf_counter()
        ip.run_cell(cell)
        print(f"⏱️ [RUN - SIGNATURE: {key}] Current Execution Time: {time.perf_counter() - t0:.4f} seconds")
        return None

    elif state == 'log' or (state == 'log_and_lock' and key not in OUTPUT_CACHE):
        output_text, duration = _execute_and_capture()
        OUTPUT_CACHE[key] = (output_text, duration)
        print(output_text.strip())
        print(f"⏱️ [{state.upper()} - SIGNATURE: {key}] Compute Time: {duration:.4f} seconds (💾 Cached successfully)")
        return None

# =====================================================================
# THE EXTENSION BOOTSTRAPPING ENGINE
# =====================================================================
def load_ipython_extension(ipython):
    """Called by IPython natively via %load_ext luke_helpers"""
    # 1. Register the cell magic engine
    ipython.register_magic_function(process, magic_kind='cell')
    
    # 2. Inject your utility functions straight into the user's global namespace
    ipython.push({
        'play_beep': play_beep,
        'play_chime': play_chime
    })
    
    print("💎 Luke's Helpers Loaded: `%%process`, `play_beep()`, and `play_chime()` are armed.")



```
# Pull down the comprehensive suite from your GitHub repo
!curl -O https://raw.githubusercontent.com/YOUR_GITHUB_USERNAME/YOUR_REPO_NAME/main/luke_helpers.py

# Initialize the extension
%load_ext luke_helpers
```
