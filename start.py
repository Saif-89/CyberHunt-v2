#!/usr/bin/env python3
"""
CyberHunt v2 — Cybersecurity Internship Intelligence
Startup script: installs deps then launches the server
"""
import subprocess, sys, os

def install():
    print("📦 Installing dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install",
        "flask", "flask-cors", "requests", "beautifulsoup4", "lxml", "fake-useragent",
        "--quiet", "--break-system-packages"
    ])
    print("✅ Dependencies ready\n")

def run():
    os.makedirs("data", exist_ok=True)
    print("=" * 52)
    print("  🔐  CyberHunt v2 — Internship Intelligence")
    print("=" * 52)
    print("  🌐  Open in browser: http://localhost:5050")
    print("  📡  LAN access:      http://<your-ip>:5050")
    print("  🛑  Stop:            Ctrl+C")
    print("=" * 52 + "\n")
    # Import here after pip install
    from app import app
    app.run(host="0.0.0.0", port=5050, debug=False, threaded=True)

if __name__ == "__main__":
    install()
    run()
