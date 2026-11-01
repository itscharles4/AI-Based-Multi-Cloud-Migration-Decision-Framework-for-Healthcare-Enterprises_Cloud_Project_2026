"""
show_database.py - Inspect and display Healthcare Cloud Framework Database
Usage:
    python show_database.py
    python show_database.py --table telemetry_events
    python show_database.py --table audit_log --limit 5
"""

import argparse
import sqlite3
from pathlib import Path

DB_PATH = Path("runtime/app.db")

def main():
    parser = argparse.ArgumentParser(description="Inspect Healthcare Database")
    parser.add_argument("--table", type=str, default="", help="Specific table to view")
    parser.add_argument("--limit", type=int, default=5, help="Number of rows to preview")
    args = parser.parse_args()

    if not DB_PATH.exists():
        print(f"Error: Database file not found at {DB_PATH.resolve()}")
        print("Run 'python 01_initialize_database.py' to create and migrate it.")
        return

    print("=" * 70)
    print(" HEALTHCARE CLOUD FRAMEWORK - DATABASE INSPECTION")
    print("=" * 70)
    print(f"Database File: {DB_PATH.resolve()}")
    print(f"File Size:     {DB_PATH.stat().st_size / 1024:.2f} KB\n")

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    tables = [row[0] for row in cur.fetchall() if not row[0].startswith("sqlite_")]

    print("--- 1. Tables & Row Counts ---")
    for t in tables:
        count = cur.execute(f'SELECT COUNT(*) FROM "{t}";').fetchone()[0]
        print(f"  • {t:<24} : {count:>5} rows")

    target_tables = [args.table] if args.table else ["telemetry_events", "routing_decisions", "predictions", "audit_log", "alerts"]
    target_tables = [t for t in target_tables if t in tables]

    print("\n--- 2. Sample Data Previews ---")
    for t in target_tables:
        print(f"\n[ Table: {t} ]")
        cur.execute(f'PRAGMA table_info("{t}");')
        cols = [c[1] for c in cur.fetchall()]
        print("Columns: " + ", ".join(cols))

        cur.execute(f'SELECT * FROM "{t}" ORDER BY 1 DESC LIMIT {args.limit};')
        rows = cur.fetchall()
        if not rows:
            print("  (Table is currently empty)")
        else:
            for r in rows:
                row_str = " | ".join(str(v)[:30] for v in r)
                print(f"  -> {row_str}")

    con.close()
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()

