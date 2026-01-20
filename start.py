#!/usr/bin/env python3
"""
Quick start script for Rinse Repeat Labs Web Dashboard.

Usage:
    python start.py              # Start dashboard
    python start.py --no-browser # Start without opening browser
    python start.py --port 8080  # Use custom port
"""

import argparse
import subprocess
import sys
import time
import webbrowser
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Start Rinse Repeat Labs Web Dashboard")
    parser.add_argument("--no-browser", action="store_true", help="Don't auto-open browser")
    parser.add_argument("--port", type=int, default=5000, help="Port to run on (default: 5000)")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to (default: 127.0.0.1)")
    args = parser.parse_args()

    # Ensure we're in the right directory
    project_root = Path(__file__).parent
    webapp_dir = project_root / "webapp"

    if not webapp_dir.exists():
        print("Error: webapp directory not found")
        sys.exit(1)

    url = f"http://{args.host}:{args.port}"

    print(f"""
╔═══════════════════════════════════════════════════════════╗
║           Rinse Repeat Labs - Web Dashboard               ║
╠═══════════════════════════════════════════════════════════╣
║  Starting server at: {url:<35} ║
║  Press Ctrl+C to stop                                     ║
╚═══════════════════════════════════════════════════════════╝
""")

    # Open browser after a short delay (if not disabled)
    if not args.no_browser:
        def open_browser():
            time.sleep(1.5)
            webbrowser.open(url)

        import threading
        threading.Thread(target=open_browser, daemon=True).start()

    # Start Flask app
    try:
        subprocess.run(
            [sys.executable, "app.py"],
            cwd=webapp_dir,
            env={
                **dict(__import__("os").environ),
                "FLASK_RUN_PORT": str(args.port),
                "FLASK_RUN_HOST": args.host,
            }
        )
    except KeyboardInterrupt:
        print("\nShutting down...")


if __name__ == "__main__":
    main()
