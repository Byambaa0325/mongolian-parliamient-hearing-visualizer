#!/usr/bin/env python3
"""
Server entry point - imports API from backend
"""
from backend.api import app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)

