"""
POLYDIM V815 — INGESTA VECTORIAL DIRECTA (REGLAS 19, 22, 28)
═══════════════════════════════════════════════════════════════
Lee directamente todas las opiniones del tribunal multi-IA de V815 y V816:
  - 05_TRIBUNAL_MULTI_IA_Y_SINTESIS_SOTA.md
  - SOTA_V816_CEREBRAS_BLOCK_LDLT_ROOK_QSBR.md
  - SOTA_ADAPTIVE_MIXED_PRECISION_STIEFEL_2026.md
  - SOTA_LOCKFREE_ARENA_QSBR_2026.md
  - SOTA_QUANTUM_CLIFFORD_T_PHASE_2026.md
  - SOTA_STIEFEL_SPECTRAL_STABILITY_2026.md
  - Respuestas individuales: cerebras, kimi, chatgpt, deepseek, etc.

Vuelca vectores y hechos directamente a SQLite (POLYDIM_VECDB.sqlite)
y a Shared Memory PMTP (SLAB_V815_SWARM_STATE), eliminando el gusano 1D.
"""

import sys, os, zipfile, sqlite3, json, hashlib, re, time
import xml.etree.ElementTree as ET
from pathlib import Path
from multiprocessing import shared_memory
import numpy as np

DB_PATH = Path(r"E:\POLYDIM-THEORICAL\POLYDIM_VECDB.sqlite")
V815_DIR = Path(r"E:\POLYDIM_EINSOF\ENTREGA_2026_09_28_V815")
AUDITORIA_DIR = V815_DIR / "auditoria_externa"
RESPUESTAS_DIR = V815_DIR / "respuestas"

def get_db():
    db = sqlite3.connect(str(DB_PATH))
    db.row_factory = sqlite3.Row
    db.executescript("""
    CREATE TABLE IF NOT EXISTS swarm_opinions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        model_name TEXT,
        source_file TEXT,
        slide_or_sec TEXT,
        critique_topic TEXT,
        finding_type TEXT,
        summary TEXT,
        code_ref TEXT,
        raw_hash TEXT,
        timestamp TEXT
    );

    CREATE TABLE IF NOT EXISTS swarm_consensus (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic TEXT UNIQUE,
        consensus_verdict TEXT,
        supporting_models TEXT,
        dissenting_models TEXT,
        resolution_action TEXT,
        applied_to_theory INTEGER DEFAULT 0
    );
    """)
    db.commit()
    return db

def sha6(s):
    return hashlib.md5(s.encode("utf-8", "replace")).hexdigest()[:8]

def parse_markdown_ai(md_path: Path):
    if not md_path.exists():
        return []
    content = md_path.read_text(encoding="utf-8", errors="replace")
    
    findings = []
    sections = re.split(r'\n(?=#{1,4}\s+)', content)
    model_name = md_path.stem.upper()
    
    for sec in sections:
        header_m = re.match(r'#{1,4}\s+(.+)', sec)
        title = header_m.group(1).strip() if header_m else "General"
        
        sec_lower = sec.lower()
        finding_type = "THEORETICAL_PROPOSAL"
        if any(k in sec_lower for k in ["bug", "error", "vulnerabilidad", "data race", "uaf", "segfault", "livelock", "cache-line", "under-flow", "overflow"]):
            finding_type = "CRITICAL_BUG"
        elif any(k in sec_lower for k in ["optimización", "speedup", "avx", "futex", "rendimiento", "simd", "ldlt", "qsbr"]):
            finding_type = "OPTIMIZATION"
        elif any(k in sec_lower for k in ["teorema", "stiefel", "frechet", "cayley", "clifford", "betti", "schur"]):
            finding_type = "SOTA_AGREEMENT"
        
        paragraphs = [p.strip() for p in sec.split("\n\n") if p.strip()]
        summary = paragraphs[0] if paragraphs else title
        if len(summary) > 400:
            summary = summary[:397] + "..."
            
        code_match = re.search(r'```(?:cpp|rust|python|c)?\n(.*?)```', sec, re.DOTALL)
        code_ref = code_match.group(1).strip()[:500] if code_match else ""
        
        findings.append({
            "model_name": model_name,
            "source_file": md_path.name,
            "slide_or_sec": title,
            "critique_topic": title[:60],
            "finding_type": finding_type,
            "summary": summary,
            "code_ref": code_ref,
            "raw_hash": sha6(sec),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        })
    return findings

def ingest_all_v815():
    print("=" * 65)
    print("POLYDIM V815 — INGESTA VECTORIAL EN ESPACIO TENSORIAL Y VECDB")
    print("=" * 65)
    
    db = get_db()
    total_findings = 0
    
    # 1. Ingestar documentos SOTA en auditoria_externa
    if AUDITORIA_DIR.exists():
        for sota_file in AUDITORIA_DIR.glob("*.md"):
            findings = parse_markdown_ai(sota_file)
            for f in findings:
                exists = db.execute("SELECT id FROM swarm_opinions WHERE raw_hash = ?", (f["raw_hash"],)).fetchone()
                if not exists:
                    db.execute("""
                        INSERT INTO swarm_opinions 
                        (model_name, source_file, slide_or_sec, critique_topic, finding_type, summary, code_ref, raw_hash, timestamp)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (f["model_name"], f["source_file"], f["slide_or_sec"], f["critique_topic"],
                          f["finding_type"], f["summary"], f["code_ref"], f["raw_hash"], f["timestamp"]))
                    total_findings += 1
            print(f"  [SOTA] Ingestado: {sota_file.name} ({len(findings)} hallazgos)")

    # 2. Ingestar respuestas de IAs
    if RESPUESTAS_DIR.exists():
        for resp_file in RESPUESTAS_DIR.glob("*.md"):
            findings = parse_markdown_ai(resp_file)
            for f in findings:
                exists = db.execute("SELECT id FROM swarm_opinions WHERE raw_hash = ?", (f["raw_hash"],)).fetchone()
                if not exists:
                    db.execute("""
                        INSERT INTO swarm_opinions 
                        (model_name, source_file, slide_or_sec, critique_topic, finding_type, summary, code_ref, raw_hash, timestamp)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (f["model_name"], f["source_file"], f["slide_or_sec"], f["critique_topic"],
                          f["finding_type"], f["summary"], f["code_ref"], f["raw_hash"], f["timestamp"]))
                    total_findings += 1
            print(f"  [RESPUESTA] Ingestado: {resp_file.name} ({len(findings)} hallazgos)")

    # 3. Consolidar consensos clave V815 / V816
    consensuses = [
        {
            "topic": "Cayley-SMW Schur Reciprocal Condition & Spectral Scaling",
            "verdict": "CONFIRMED_ISSUE",
            "support": ["CEREBRAS_120B", "KIMI", "DEEPSEEK"],
            "dissent": [],
            "action": "Implementar Spectral Scaling alpha <- alpha / max(1, |alpha|*sigma_max) y Factorizacion LDLt Pivoteada por Bloques (Rook-QSBR)."
        },
        {
            "topic": "FWHT AVX-512 Underflow Protection",
            "verdict": "APPROVED_OPTIMIZATION",
            "support": ["CEREBRAS_120B", "CHATGPT"],
            "dissent": [],
            "action": "Reemplazar factor fijo 2^-8 por renormalizacion dinamica por capas para prevenir subnormales en IEEE-754."
        },
        {
            "topic": "SPSC Ring Pointer Wrap & Memory Order Fencing",
            "verdict": "CONFIRMED_ISSUE",
            "support": ["CEREBRAS_120B", "CLAUDE"],
            "dissent": [],
            "action": "Forzar offsets a uint64_t y memoria acquire/release en transicion RCU SUSPECT -> RECLAIMED."
        },
        {
            "topic": "Ross-Selinger Quantum Bridge Phase Restoration",
            "verdict": "CONFIRMED_ISSUE",
            "support": ["CEREBRAS_120B", "QWEN"],
            "dissent": [],
            "action": "Reinyectar fase relativa eliminada por F2 mediante diagonal correction antes de compilacion Clifford+T."
        }
    ]

    for c in consensuses:
        db.execute("""
            INSERT INTO swarm_consensus (topic, consensus_verdict, supporting_models, dissenting_models, resolution_action, applied_to_theory)
            VALUES (?, ?, ?, ?, ?, 1)
            ON CONFLICT(topic) DO UPDATE SET
                consensus_verdict=excluded.consensus_verdict,
                supporting_models=excluded.supporting_models,
                resolution_action=excluded.resolution_action,
                applied_to_theory=1
        """, (c["topic"], c["verdict"], json.dumps(c["support"]), json.dumps(c["dissent"]), c["action"]))

    db.commit()

    # 4. Volcar a Memoria Compartida PMTP (SLAB_V815_SWARM_STATE)
    shm_name = "SLAB_V815_SWARM_STATE"
    total_ops = db.execute("SELECT COUNT(*) FROM swarm_opinions").fetchone()[0]
    total_cons = db.execute("SELECT COUNT(*) FROM swarm_consensus").fetchone()[0]
    
    # Tensor de estado: [total_ops, total_cons, critical_bugs, optimizations, timestamp_hash]
    crit_bugs = db.execute("SELECT COUNT(*) FROM swarm_opinions WHERE finding_type='CRITICAL_BUG'").fetchone()[0]
    opts = db.execute("SELECT COUNT(*) FROM swarm_opinions WHERE finding_type='OPTIMIZATION'").fetchone()[0]
    
    state_vector = np.array([float(total_ops), float(total_cons), float(crit_bugs), float(opts), float(time.time())], dtype=np.float64)
    shm_size = state_vector.nbytes
    
    try:
        shm = shared_memory.SharedMemory(name=shm_name, create=True, size=shm_size)
    except FileExistsError:
        shm = shared_memory.SharedMemory(name=shm_name)
        
    buf = np.ndarray(state_vector.shape, dtype=np.float64, buffer=shm.buf)
    buf[:] = state_vector[:]
    shm.close()
    
    print("-" * 65)
    print(f"  Total nuevos hallazgos ingresados: {total_findings}")
    print(f"  Total opiniones en VecDB:          {total_ops}")
    print(f"  Consensos certificados:            {total_cons}")
    print(f"  Bugs Críticos detectados/mitigados:{crit_bugs}")
    print(f"  Optimizaciones incorporadas:       {opts}")
    print(f"  PMTP Vector Slab:                  {shm_name} (Ready, Zero-Copy)")
    print("=" * 65)

if __name__ == "__main__":
    ingest_all_v815()
