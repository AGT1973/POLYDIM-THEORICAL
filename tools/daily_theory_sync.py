"""
POLYDIM DAILY THEORY SYNC DISPATCHER (POSTGRESQL 16 NATIVE)
Exclusivity: PostgreSQL 16.4 (polydim_vec_db, polydim_active_db) - Zero SQLite
"""

import sys
from pathlib import Path

# Agregar directorio actual al sys.path
tools_dir = Path(__file__).resolve().parent
if str(tools_dir) not in sys.path:
    sys.path.insert(0, str(tools_dir))

from generate_paper_whitebook_v1550 import run_sync

if __name__ == "__main__":
    run_sync()
