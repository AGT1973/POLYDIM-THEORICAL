import sqlite3

def query_references():
    con = sqlite3.connect(r'E:\POLYDIM-THEORICAL\POLYDIM_VECDB.sqlite')
    cur = con.cursor()
    
    print("=== Sample Facts related to Authors / Theory ===")
    cur.execute("SELECT id, category, content FROM facts WHERE content LIKE '%author%' OR content LIKE '%paper%' OR content LIKE '%lab%' OR content LIKE '%research%' LIMIT 10")
    for row in cur.fetchall():
        print(f"Fact {row[0]} [{row[1]}]: {row[2][:150]}...")
        
    print("\n=== Sample Theorems ===")
    cur.execute("SELECT id, theorem_name, description FROM polydim_theorems LIMIT 5")
    for row in cur.fetchall():
        print(f"Theorem {row[0]} [{row[1]}]: {str(row[2])[:150]}...")
        
    con.close()

if __name__ == "__main__":
    query_references()
