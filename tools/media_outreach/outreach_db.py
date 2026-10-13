"""
POLYDIM Media & Outreach Database Engine
SQLite structured store for leads, social accounts, academic profiles (Academia.edu), campaigns, and direct publication queues.
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "POLYDIM_OUTREACH.sqlite")

BASE_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    native_name TEXT,
    region TEXT DEFAULT 'GLOBAL',
    organization TEXT,
    role_title TEXT,
    tier TEXT DEFAULT 'PEER_RESEARCHER',
    email TEXT UNIQUE,
    twitter_handle TEXT,
    linkedin_url TEXT,
    academia_edu_url TEXT,
    github_url TEXT,
    scholar_url TEXT,
    website TEXT,
    domain_tags TEXT,
    notes TEXT,
    status TEXT DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS publications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    topic TEXT,
    channel TEXT NOT NULL,
    content_raw TEXT NOT NULL,
    media_paths TEXT,
    status TEXT DEFAULT 'DRAFT',
    post_url TEXT,
    scheduled_at TIMESTAMP,
    published_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS outreach_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contact_id INTEGER,
    publication_id INTEGER,
    channel TEXT NOT NULL,
    action_type TEXT NOT NULL,
    status_code TEXT,
    response_summary TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(contact_id) REFERENCES contacts(id),
    FOREIGN KEY(publication_id) REFERENCES publications(id)
);
"""

def get_connection(db_path: str = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path: str = DB_PATH):
    conn = get_connection(db_path)
    with conn:
        conn.executescript(BASE_SCHEMA_SQL)
        cur = conn.cursor()
        cur.execute("PRAGMA table_info(contacts)")
        cols = [r[1] for r in cur.fetchall()]
        if "native_name" not in cols:
            cur.execute("ALTER TABLE contacts ADD COLUMN native_name TEXT")
        if "region" not in cols:
            cur.execute("ALTER TABLE contacts ADD COLUMN region TEXT DEFAULT 'GLOBAL'")
        if "academia_edu_url" not in cols:
            cur.execute("ALTER TABLE contacts ADD COLUMN academia_edu_url TEXT")
        if "scholar_url" not in cols:
            cur.execute("ALTER TABLE contacts ADD COLUMN scholar_url TEXT")
            
        # Create indices after schema columns are guaranteed
        cur.execute("CREATE INDEX IF NOT EXISTS idx_contacts_tier ON contacts(tier);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_contacts_region ON contacts(region);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_contacts_email ON contacts(email);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_pub_channel ON publications(channel);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_pub_status ON publications(status);")
    conn.close()

def upsert_contact(contact: Dict[str, Any], db_path: str = DB_PATH) -> int:
    conn = get_connection(db_path)
    cur = conn.cursor()
    sql = """
    INSERT INTO contacts (full_name, native_name, region, organization, role_title, tier, email, twitter_handle, linkedin_url, academia_edu_url, github_url, scholar_url, website, domain_tags, notes, status, updated_at)
    VALUES (:full_name, :native_name, :region, :organization, :role_title, :tier, :email, :twitter_handle, :linkedin_url, :academia_edu_url, :github_url, :scholar_url, :website, :domain_tags, :notes, :status, CURRENT_TIMESTAMP)
    ON CONFLICT(email) DO UPDATE SET
        full_name = excluded.full_name,
        native_name = COALESCE(excluded.native_name, contacts.native_name),
        region = COALESCE(excluded.region, contacts.region),
        organization = COALESCE(excluded.organization, contacts.organization),
        role_title = COALESCE(excluded.role_title, contacts.role_title),
        tier = COALESCE(excluded.tier, contacts.tier),
        twitter_handle = COALESCE(excluded.twitter_handle, contacts.twitter_handle),
        linkedin_url = COALESCE(excluded.linkedin_url, contacts.linkedin_url),
        academia_edu_url = COALESCE(excluded.academia_edu_url, contacts.academia_edu_url),
        github_url = COALESCE(excluded.github_url, contacts.github_url),
        scholar_url = COALESCE(excluded.scholar_url, contacts.scholar_url),
        website = COALESCE(excluded.website, contacts.website),
        domain_tags = COALESCE(excluded.domain_tags, contacts.domain_tags),
        notes = COALESCE(excluded.notes, contacts.notes),
        updated_at = CURRENT_TIMESTAMP;
    """
    with conn:
        cur.execute(sql, {
            "full_name": contact.get("full_name", "Unknown"),
            "native_name": contact.get("native_name", ""),
            "region": contact.get("region", "GLOBAL"),
            "organization": contact.get("organization", ""),
            "role_title": contact.get("role_title", ""),
            "tier": contact.get("tier", "PEER_RESEARCHER"),
            "email": contact.get("email"),
            "twitter_handle": contact.get("twitter_handle", ""),
            "linkedin_url": contact.get("linkedin_url", ""),
            "academia_edu_url": contact.get("academia_edu_url", ""),
            "github_url": contact.get("github_url", ""),
            "scholar_url": contact.get("scholar_url", ""),
            "website": contact.get("website", ""),
            "domain_tags": contact.get("domain_tags", ""),
            "notes": contact.get("notes", ""),
            "status": contact.get("status", "ACTIVE")
        })
        row_id = cur.lastrowid
    conn.close()
    return row_id

def list_contacts(tier: Optional[str] = None, region: Optional[str] = None, tag: Optional[str] = None, db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    conn = get_connection(db_path)
    cur = conn.cursor()
    query = "SELECT * FROM contacts WHERE 1=1"
    params = []
    if tier:
        query += " AND tier = ?"
        params.append(tier)
    if region:
        query += " AND region = ?"
        params.append(region)
    if tag:
        query += " AND domain_tags LIKE ?"
        params.append(f"%{tag}%")
    cur.execute(query, params)
    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return rows

def queue_publication(pub: Dict[str, Any], db_path: str = DB_PATH) -> int:
    conn = get_connection(db_path)
    cur = conn.cursor()
    sql = """
    INSERT INTO publications (title, topic, channel, content_raw, media_paths, status, scheduled_at)
    VALUES (:title, :topic, :channel, :content_raw, :media_paths, :status, :scheduled_at)
    """
    with conn:
        cur.execute(sql, {
            "title": pub.get("title", "Untitled"),
            "topic": pub.get("topic", "POLYDIM_CORE"),
            "channel": pub.get("channel", "LINKEDIN"),
            "content_raw": pub.get("content_raw", ""),
            "media_paths": pub.get("media_paths", ""),
            "status": pub.get("status", "DRAFT"),
            "scheduled_at": pub.get("scheduled_at", datetime.now().isoformat())
        })
        pub_id = cur.lastrowid
    conn.close()
    return pub_id

def list_publications(channel: Optional[str] = None, status: Optional[str] = None, db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    conn = get_connection(db_path)
    cur = conn.cursor()
    query = "SELECT * FROM publications WHERE 1=1"
    params = []
    if channel:
        query += " AND channel = ?"
        params.append(channel)
    if status:
        query += " AND status = ?"
        params.append(status)
    cur.execute(query, params)
    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return rows
