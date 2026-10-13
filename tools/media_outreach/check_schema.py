import sqlite3

con = sqlite3.connect(r'E:\POLYDIM-THEORICAL\POLYDIM_VECDB.sqlite')
cur = con.cursor()
for t in ['facts', 'polydim_theorems', 'novelties', 'permanent_vault']:
    cur.execute(f"PRAGMA table_info({t});")
    print(f"Schema of {t}:", [r[1] for r in cur.fetchall()])
con.close()
