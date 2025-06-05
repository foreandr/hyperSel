import time
import json
import random
import requests
import urllib.parse
import subprocess
import os
from ppadb.client import Client
from websocket import create_connection

# Seconds to wait between each major step (2 – 3 s)
PAUSE = lambda: time.sleep(random.uniform(2, 3))

# ──────────────────────────────────────────────────────────────────────────────
# 🛠 STEP 0: Start ADB server (if it isn’t already running)
# ──────────────────────────────────────────────────────────────────────────────
print("🛠 STEP 0: Starting ADB server (if not running)…")
platform_tools_path = r"C:\Users\forea\Documents\platform-tools"
adb_path = os.path.join(platform_tools_path, "adb.exe")
subprocess.run([adb_path, "start-server"],
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
PAUSE()

# ──────────────────────────────────────────────────────────────────────────────
# 📡 STEP 1: Connect to the emulator via ADB
# ──────────────────────────────────────────────────────────────────────────────
print("📡 STEP 1: Connecting to emulator via ADB…")
adb = Client(host="127.0.0.1", port=5037)
device = adb.device("10.0.0.172:5555")
if device is None:
    raise Exception("❌ Unable to connect to device at 10.0.0.172:5555.")
print(f"✅ Connected to device: {device.serial}")
PAUSE()

# ──────────────────────────────────────────────────────────────────────────────
# 🔁 STEP 2: Forward Chrome DevTools port 9222 to the host
# ──────────────────────────────────────────────────────────────────────────────
print("🔁 STEP 2: Forwarding port 9222 for DevTools access…")
subprocess.run([adb_path, "forward",
                "tcp:9222", "localabstract:chrome_devtools_remote"],
               check=True)
PAUSE()

# ──────────────────────────────────────────────────────────────────────────────
# 🌐 STEP 3: Launch Chrome in “view-source:” mode
# ──────────────────────────────────────────────────────────────────────────────
zillow_url  = "view-source:https://www.zillow.com/toronto-on/"
encoded_url = urllib.parse.quote(zillow_url, safe=":/?&=")

chrome_command = (
    'am start -n com.android.chrome/com.google.android.apps.chrome.Main '
    '--es args "--remote-debugging-port=9222 --remote-allow-origins=*" '
    f'-d "{encoded_url}"'
)
print(f"🌐 STEP 3: Launching Chrome to URL: {zillow_url} (remote debugging ON)")
device.shell(chrome_command)
PAUSE()

# ──────────────────────────────────────────────────────────────────────────────
# 🔌 STEP 3 bis: Attach to Chrome DevTools & pull the FULL page source
# ──────────────────────────────────────────────────────────────────────────────
print("🔌 STEP 3 bis: Connecting to Chrome DevTools…")
try:
    tabs = requests.get("http://127.0.0.1:9222/json").json()
except Exception:
    raise Exception("❌ Could not connect to DevTools — is Chrome alive?")

if not tabs:
    raise Exception("❌ Chrome returned zero tabs!")

# We’ll grab the first tab (index 0). You can refine this later.
ws_url = tabs[0]["webSocketDebuggerUrl"]
ws     = create_connection(ws_url)

# Ask DevTools to evaluate JS: document.documentElement.outerHTML
ws.send(json.dumps({
    "id": 1,
    "method": "Runtime.evaluate",
    "params": {
        "expression": "document.documentElement.outerHTML",
        "returnByValue": True,
    }
}))
reply       = json.loads(ws.recv())
html_source = reply["result"]["result"]["value"]

# Print to console (so you literally “copy-paste” if you want)
print("\n───── BEGIN PAGE SOURCE ─────")
print(html_source)
print("─────  END PAGE SOURCE  ─────\n")
PAUSE()

# ──────────────────────────────────────────────────────────────────────────────
# 📄 STEP 4: (legacy) use DOM.getOuterHTML for comparison
# ──────────────────────────────────────────────────────────────────────────────
print("📄 STEP 4: Fetching outerHTML via DOM domain (legacy method)…")
ws.send(json.dumps({"id": 2, "method": "DOM.getDocument"}))
root_id = json.loads(ws.recv())["result"]["root"]["nodeId"]

ws.send(json.dumps({
    "id"    : 3,
    "method": "DOM.getOuterHTML",
    "params": { "nodeId": root_id }
}))
outer_html = json.loads(ws.recv())["result"]["outerHTML"]
PAUSE()

# ──────────────────────────────────────────────────────────────────────────────
# 💾 STEP 5: Write whichever version you prefer to disk
# ──────────────────────────────────────────────────────────────────────────────
print("💾 STEP 5: Writing HTML to zillow_page.html …")
with open("zillow_page.html", "w", encoding="utf-8") as fh:
    fh.write(html_source)          # ← full evaluated source
    # fh.write(outer_html)         # ← or use DOM version instead

ws.close()
print("✅ Done — file saved and source echoed above.")


'''
1. download mumu
2. run as root,
3. download the adp thing
4. add it to path
5. download chrome on mumu
'''
