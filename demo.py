"""Main executable demo launcher for AI-Agent-OS.

Boots the universal kernel, loads Genesis_Harness assets, and serves the UI Dashboard.
"""

import os
import sys
import time
import webbrowser
from http.server import HTTPServer

from src.runtime.demo_server import DemoHTTPRequestHandler, system_state

BANNER = r"""
    ___    I - A g e n t - O S
   /   |  ____  ____  ____  ______   ____  _____
  / /| | / __ \/ __ \/ __ \/ ___/  / __ \/ ___/
 / ___ |/ /_/ / /_/ / /_/ (__  )  / /_/ (__  ) 
/_/  |_/ .___/\____/ .___/____/   \____/____/  
      /_/         /_/                          
  Universal Autonomous Agent Platform v0.2.0
"""


def main():
    print(BANNER)
    print("=" * 60)
    print(" Booting AI-Agent-OS Kernel...")
    print(f" • Loaded Genesis_Harness Agents: {system_state.agent_registry.count()}")
    print(f" • Loaded Genesis_Harness Skills: {len(system_state.skill_registry.list_skills())}")
    print(f" • Event Bus & Memory Systems: ACTIVE")
    print(f" • Model Router Active Provider: {system_state.active_provider.upper()}")
    print("=" * 60)

    host = "127.0.0.1"
    port = 8000
    server_address = (host, port)

    httpd = HTTPServer(server_address, DemoHTTPRequestHandler)
    url = f"http://{host}:{port}"
    print(f"\n[+] AI-Agent-OS Dashboard is running at: {url}")
    print("    Press Ctrl+C to stop the server.\n")


    # Optionally open browser
    if "--open" in sys.argv or "-o" in sys.argv:
        webbrowser.open(url)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down AI-Agent-OS Kernel...")
        httpd.server_close()
        print("Server stopped cleanly.")


if __name__ == "__main__":
    main()
