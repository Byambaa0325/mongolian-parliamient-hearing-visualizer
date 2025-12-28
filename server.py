#!/usr/bin/env python3
"""
Server entry point - imports API from backend
"""
import os
from backend.api import app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"Starting Flask server on http://0.0.0.0:{port}")
    print(f"API available at http://localhost:{port}/api/transcripts")
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)

