import sys
sys.path.insert(0, r"E:\Mantenimiento")
import psycopg
from db_manager import get_connection_string

def check():
    print("=== polydim_vec_db ===")
    with psycopg.connect(get_connection_string("polydim_vec_db")) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
            tables = [r[0] for r in cur.fetchall()]
            print("Tables:", tables)
            for t in ['novelties', 'polydim_theorems', 'session_context', 'permanent_vault']:
                if t in tables:
                    cur.execute(f"SELECT count(*) FROM {t}")
                    print(f"  {t}: {cur.fetchone()[0]} rows")

    print("=== polydim_active_db ===")
    with psycopg.connect(get_connection_string("polydim_active_db")) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
            tables = [r[0] for r in cur.fetchall()]
            print("Tables:", tables)
            for t in ['active_vault', 'outreach_contacts', 'outreach_grants', 'outreach_nodes']:
                if t in tables:
                    cur.execute(f"SELECT count(*) FROM {t}")
                    print(f"  {t}: {cur.fetchone()[0]} rows")

if __name__ == "__main__":
    check()
