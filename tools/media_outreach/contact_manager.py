"""
POLYDIM Contact & Lead Manager
Handles ingestion, enrichment, filtering, and export of high-profile researchers, engineers, and partners.
"""

import csv
import json
import os
import re
from typing import List, Dict, Any
from outreach_db import init_db, upsert_contact, list_contacts

def sanitize_email(email: str) -> str:
    if not email:
        return ""
    email = email.strip().lower()
    match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", email)
    return match.group(0) if match else ""

def sanitize_handle(handle: str) -> str:
    if not handle:
        return ""
    handle = handle.strip()
    if handle.startswith("@"):
        return handle
    if "twitter.com/" in handle or "x.com/" in handle:
        parts = handle.rstrip("/").split("/")
        return "@" + parts[-1]
    return "@" + handle if handle else ""

def import_from_csv(csv_path: str) -> int:
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    
    count = 0
    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            contact = {
                "full_name": row.get("name") or row.get("full_name") or "Unknown",
                "organization": row.get("organization") or row.get("institution") or "",
                "role_title": row.get("role") or row.get("role_title") or "",
                "tier": row.get("tier") or "PEER_RESEARCHER",
                "email": sanitize_email(row.get("email", "")),
                "twitter_handle": sanitize_handle(row.get("twitter") or row.get("twitter_handle", "")),
                "linkedin_url": row.get("linkedin") or row.get("linkedin_url", ""),
                "github_url": row.get("github") or row.get("github_url", ""),
                "website": row.get("website", ""),
                "domain_tags": row.get("tags") or row.get("domain_tags", ""),
                "notes": row.get("notes") or row.get("papers", "")
            }
            if contact["email"] or contact["twitter_handle"] or contact["linkedin_url"]:
                upsert_contact(contact)
                count += 1
    return count

def export_to_json(output_path: str, tier: str = None) -> int:
    contacts = list_contacts(tier=tier)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(contacts, f, indent=2, ensure_ascii=False)
    return len(contacts)

def export_to_csv(output_path: str, tier: str = None) -> int:
    contacts = list_contacts(tier=tier)
    if not contacts:
        return 0
    fieldnames = list(contacts[0].keys())
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(contacts)
    return len(contacts)

if __name__ == "__main__":
    init_db()
    print("Contact Manager Ready.")
