import os
import sys

# Tambahkan path folder 'server' agar bisa import main.py
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
server_dir = os.path.join(parent_dir, 'server')

if server_dir not in sys.path:
    sys.path.insert(0, server_dir)

from main import app
