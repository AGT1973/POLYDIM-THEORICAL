"""
POLYDIM Strategic Science & Grants Database Extension
Adds schema for government programs, university prizes, and research excellence initiatives.
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "POLYDIM_OUTREACH.sqlite")

ADDITIONAL_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS strategic_grants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    program_name TEXT NOT NULL,
    agency TEXT NOT NULL, -- DARPA, NSF, ERC, BMBF, NSFC, MOST, NEDO, JST, MSIT, IITP
    region TEXT NOT NULL, -- US, EU, DE, CN, JP, KR, GLOBAL
    principal_investigator TEXT,
    institution TEXT NOT NULL,
    grant_code TEXT,
    topic_thrust TEXT NOT NULL, -- HDC, GEOMETRIC_AI, NEUROMORPHIC, PIM, CLIFFORD, TENSOR_COMPILERS
    budget_range TEXT, -- Scientific scope indicator
    summary TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS academic_awards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    award_name TEXT NOT NULL, -- NeurIPS Best Paper, ERC Synergy, IEEE Pioneer, Test of Time, ACM SIG
    organization_body TEXT NOT NULL,
    recipient TEXT NOT NULL,
    institution TEXT NOT NULL,
    paper_title TEXT,
    domain TEXT NOT NULL,
    year INTEGER,
    significance TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_grants_agency ON strategic_grants(agency);
CREATE INDEX IF NOT EXISTS idx_grants_thrust ON strategic_grants(topic_thrust);
CREATE INDEX IF NOT EXISTS idx_awards_domain ON academic_awards(domain);
"""

def apply_grants_schema(db_path: str = DB_PATH):
    conn = sqlite3.connect(db_path)
    with conn:
        conn.executescript(ADDITIONAL_SCHEMA_SQL)
    conn.close()
    print("Strategic Grants and Academic Awards schema applied successfully.")

if __name__ == "__main__":
    apply_grants_schema()
