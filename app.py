"""
Women Safety & Emergency Assistance Platform
Primary Application Entry Point (app.py)
"""

import os
import sys
from app import create_app

env = os.environ.get("FLASK_ENV", "development")
app = create_app(env)

def main():
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "127.0.0.1")
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    print(f"[*] Starting Women Safety Platform on http://{host}:{port} ({env} mode)")
    app.run(host=host, port=port, debug=debug, use_reloader=False)

if __name__ == "__main__":
    main()
