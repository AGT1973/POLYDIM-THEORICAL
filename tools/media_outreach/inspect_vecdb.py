import sqlite3

def check_db():
    con = sqlite3.connect(r'E:\POLYDIM-THEORICAL\POLYDIM_VECDB.sqlite')
    cur = con.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [r[0] for r in cur.fetchall()]
    print("Tables in POLYDIM_VECDB.sqlite:", tables)
    for t in tables:
        try:
            cur.execute(f"SELECT count(*) FROM {t}")
            print(f"- {t}: {cur.fetchone()[0]} rows")
        except Exception as e:
            print(f"- {t}: error ({e})")
    con.close()

if __name__ == "__main__":
    check_db()
