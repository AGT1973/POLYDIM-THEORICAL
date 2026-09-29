"""
POLYDIM LIVING THESIS — Vector Database + PMTP Agent Bus
═══════════════════════════════════════════════════════════
Arquitectura:
  - SQLite = Vector DB persistente (sin pérdida)
  - Agentes PMTP = daemons que traen novedades de logs/code/benchmarks
  - DOCX = colapso terminal solo cuando el usuario pide /collapse
  - Zero tokens: todo vive en disco/DB hasta el momento de lectura humana

Tablas:
  chapters  → vectores semánticos de cada capítulo (hash + metadata)
  facts     → hechos atómicos: benchmarks, teoremas, bugs, certificaciones
  novelties → novedades de agentes PMTP: logs nuevos, experimentos, brechas
  agents    → registro de agentes activos y su último SLAB_ID
"""

import sqlite3, json, hashlib, re, os, time
from pathlib import Path
from datetime import datetime, timezone

DB_PATH = Path(r"E:\POLYDIM-THEORICAL\POLYDIM_VECDB.sqlite")

SCHEMA = """
CREATE TABLE IF NOT EXISTS chapters (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    filename    TEXT UNIQUE,
    chapter     TEXT,
    size_kb     REAL,
    hash        TEXT,
    sections    TEXT,   -- JSON array
    theorems    INTEGER,
    equations   INTEGER,
    benchmarks  TEXT,   -- JSON array de strings
    keywords    TEXT,   -- JSON array
    inserted_at TEXT,
    updated_at  TEXT
);

CREATE TABLE IF NOT EXISTS facts (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    fact_type   TEXT,   -- 'benchmark' | 'theorem' | 'bug' | 'cert' | 'code'
    source_file TEXT,
    version     TEXT,   -- 'V762' | 'V764' | 'V765' | ...
    topic       TEXT,   -- 'rodrigues' | 'pmtp' | 'cayley' | ...
    metric_key  TEXT,   -- 'drift' | 'latency_ms' | 'speedup' | ...
    metric_val  REAL,
    metric_unit TEXT,
    detail      TEXT,   -- descripción completa
    certified   INTEGER DEFAULT 0,  -- 1 si Exit Code 0
    inserted_at TEXT
);

CREATE TABLE IF NOT EXISTS novelties (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id    TEXT,   -- ID del agente PMTP que lo trajo
    ntype       TEXT,   -- 'log' | 'benchmark' | 'bug' | 'brecha' | 'code_change'
    path        TEXT,   -- archivo fuente
    summary     TEXT,   -- resumen ≤ 500 chars
    topics      TEXT,   -- JSON array de topics afectados
    absorbed    INTEGER DEFAULT 0,  -- 1 si ya fue incorporado a la tesis
    inserted_at TEXT
);

CREATE TABLE IF NOT EXISTS agents (
    id          TEXT PRIMARY KEY,
    role        TEXT,
    last_slab   TEXT,
    last_seen   TEXT,
    status      TEXT    -- 'active' | 'idle' | 'done'
);

CREATE TABLE IF NOT EXISTS collapse_log (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    docx_path   TEXT,
    chapters_n  INTEGER,
    facts_n     INTEGER,
    novelties_n INTEGER,
    collapsed_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_facts_topic   ON facts(topic);
CREATE INDEX IF NOT EXISTS idx_facts_version ON facts(version);
CREATE INDEX IF NOT EXISTS idx_novelties_absorbed ON novelties(absorbed);
"""

def get_db():
    db = sqlite3.connect(str(DB_PATH))
    db.row_factory = sqlite3.Row
    db.executescript(SCHEMA)
    db.commit()
    return db

def sha6(s): return hashlib.md5(s.encode("utf-8","replace")).hexdigest()[:6]
def now(): return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

# ── INGESTIÓN DE CAPÍTULOS ────────────────────────────────────────────────────
def ingest_chapters(latex_dir: Path):
    """Lee todos los .tex y los vectoriza en la DB."""
    db = get_db()
    n = 0
    for f in sorted(latex_dir.glob("*.tex")):
        if f.name == "main.tex": continue
        try:
            raw = f.read_text(encoding="utf-8", errors="replace")
        except: continue
        
        h = sha6(raw)
        existing = db.execute("SELECT hash FROM chapters WHERE filename=?", (f.name,)).fetchone()
        if existing and existing["hash"] == h:
            continue  # sin cambios
        
        chapter   = (re.search(r'\\chapter\*?\{([^}]+)\}', raw) or [None,"?"])[0]
        if hasattr(chapter, 'group'): chapter = chapter.group(1)[:80]
        sections  = re.findall(r'\\(?:sub)*section\*?\{([^}]+)\}', raw)
        theorems  = len(re.findall(r'\\begin\{(theorem|lemma|definition)\}', raw))
        equations = len(re.findall(r'\\begin\{equation\*?\}', raw))
        benchmarks= re.findall(r'[\d\.]+\s*(?:ms|GB/s|MB/s|µs|×10|e-\d+)', raw)[:15]
        keywords  = list(set(re.findall(r'\\textbf\{([^}]{3,40})\}', raw)))[:20]
        
        db.execute("""
            INSERT INTO chapters (filename,chapter,size_kb,hash,sections,theorems,
                                  equations,benchmarks,keywords,inserted_at,updated_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(filename) DO UPDATE SET
                chapter=excluded.chapter, size_kb=excluded.size_kb, hash=excluded.hash,
                sections=excluded.sections, theorems=excluded.theorems,
                equations=excluded.equations, benchmarks=excluded.benchmarks,
                keywords=excluded.keywords, updated_at=excluded.updated_at
        """, (f.name, chapter, round(f.stat().st_size/1024,1), h,
              json.dumps(sections[:8]), theorems, equations,
              json.dumps(benchmarks), json.dumps(keywords),
              now(), now()))
        n += 1
    db.commit()
    db.close()
    return n

# ── INGESTIÓN DE HECHOS DESDE LOGS/JSON ──────────────────────────────────────
BENCHMARK_PARSERS = [
    # latencia ms
    (r'([\d\.]+)\s*ms', 'latency_ms', 'ms'),
    # drift / error
    (r'[Dd]rift\s*[=:]\s*([\d\.e\-\+]+)', 'drift', ''),
    # speedup
    (r'([\d\.]+)\s*[xX×]\s*(?:faster|speedup|más rápido)', 'speedup_factor', 'x'),
    # bandwidth
    (r'([\d\.]+)\s*GB/s', 'bandwidth', 'GB/s'),
    # error norma
    (r'norm_err\s*[=:]\s*([\d\.e\-\+]+)', 'norm_err', ''),
    # torn reads
    (r'[Tt]orn\s*[Rr]eads?\s*[=:]\s*(\d+)', 'torn_reads', ''),
]

def version_from_path(path_str):
    m = re.search(r'[Vv]7(\d\d)', path_str)
    return f"V7{m.group(1)}" if m else "V?"

def topic_from_path(path_str):
    p = path_str.lower()
    if "telepath" in p: return "telepatia"
    if "pmtp" in p or "shm" in p: return "pmtp"
    if "rodrigues" in p or "sphere" in p: return "rodrigues"
    if "stiefel" in p or "cayley" in p: return "cayley_smw"
    if "tpu" in p: return "tpu_xla"
    if "gpu" in p or "triton" in p: return "triton"
    if "linux" in p or "posix" in p: return "linux_ipc"
    if "dart" in p or "ffi" in p: return "dart_ffi"
    return "general"

def ingest_log(log_path: Path):
    """Extrae hechos de un log/JSON y los inserta en facts."""
    db = get_db()
    try:
        raw = log_path.read_text(encoding="utf-8", errors="replace")
    except:
        db.close(); return 0
    
    version = version_from_path(str(log_path))
    topic   = topic_from_path(str(log_path))
    n = 0
    
    for pattern, key, unit in BENCHMARK_PARSERS:
        for m in re.finditer(pattern, raw):
            try:
                val = float(m.group(1))
                ctx = raw[max(0, m.start()-60):m.start()+80].replace('\n',' ').strip()
                cert = 1 if "exit code 0" in raw.lower() or "pass" in raw.lower() else 0
                db.execute("""
                    INSERT INTO facts (fact_type,source_file,version,topic,
                                       metric_key,metric_val,metric_unit,detail,certified,inserted_at)
                    VALUES (?,?,?,?,?,?,?,?,?,?)
                """, ('benchmark', str(log_path.name), version, topic,
                      key, val, unit, ctx[:300], cert, now()))
                n += 1
            except: pass
    
    db.commit(); db.close()
    return n

def ingest_novelty(agent_id: str, ntype: str, path: str, summary: str, topics: list):
    """Un agente PMTP reporta una novedad."""
    db = get_db()
    db.execute("""
        INSERT INTO novelties (agent_id,ntype,path,summary,topics,inserted_at)
        VALUES (?,?,?,?,?,?)
    """, (agent_id, ntype, path, summary[:500], json.dumps(topics), now()))
    db.execute("""
        INSERT INTO agents (id,role,last_slab,last_seen,status) VALUES (?,?,?,?,?)
        ON CONFLICT(id) DO UPDATE SET last_seen=excluded.last_seen, status='active'
    """, (agent_id, ntype, f"SLAB_{sha6(summary)}", now(), 'active'))
    db.commit(); db.close()

# ── QUERIES ÚTILES (sin tokens) ───────────────────────────────────────────────
def query_status():
    db = get_db()
    caps  = db.execute("SELECT COUNT(*) as n, SUM(theorems) as thm, SUM(equations) as eq FROM chapters").fetchone()
    facts = db.execute("SELECT COUNT(*) as n, SUM(certified) as cert FROM facts").fetchone()
    novs  = db.execute("SELECT COUNT(*) as n, SUM(absorbed) as ab FROM novelties").fetchone()
    brechas = db.execute("""
        SELECT topics, COUNT(*) as n FROM novelties WHERE absorbed=0 GROUP BY topics
    """).fetchall()
    db.close()
    return {
        "chapters": dict(caps), "facts": dict(facts), "novelties": dict(novs),
        "pending_topics": [dict(r) for r in brechas]
    }

def query_unabsorbed():
    """Novedades aún no incorporadas a la tesis."""
    db = get_db()
    rows = db.execute("""
        SELECT agent_id, ntype, path, summary, topics, inserted_at
        FROM novelties WHERE absorbed=0 ORDER BY inserted_at DESC LIMIT 50
    """).fetchall()
    db.close()
    return [dict(r) for r in rows]

def mark_absorbed(novelty_id: int):
    db = get_db()
    db.execute("UPDATE novelties SET absorbed=1 WHERE id=?", (novelty_id,))
    db.commit(); db.close()

def query_facts_by_topic(topic: str):
    db = get_db()
    rows = db.execute("""
        SELECT version, metric_key, metric_val, metric_unit, certified, detail
        FROM facts WHERE topic=? ORDER BY version DESC
    """, (topic,)).fetchall()
    db.close()
    return [dict(r) for r in rows]

# ── COLLAPSE TRIGGER (solo cuando el usuario pide) ────────────────────────────
def collapse_summary():
    """Devuelve un resumen compacto de lo que hay en la DB para el collapse."""
    db = get_db()
    caps  = db.execute("SELECT filename, chapter, theorems, equations FROM chapters ORDER BY filename").fetchall()
    novs  = db.execute("SELECT ntype, summary, topics FROM novelties WHERE absorbed=0").fetchall()
    facts = db.execute("""
        SELECT topic, metric_key, AVG(metric_val) as avg_val, metric_unit, COUNT(*) as n
        FROM facts WHERE certified=1 GROUP BY topic, metric_key ORDER BY topic
    """).fetchall()
    db.close()
    return {
        "chapters": [dict(c) for c in caps],
        "pending_novelties": [dict(n) for n in novs],
        "certified_benchmarks": [dict(f) for f in facts],
    }

if __name__ == "__main__":
    import sys
    LATEX = Path(r"E:\POLYDIM-THEORICAL\CONSTITUCION_TESIS_MANIFESTO\TESIS_DOCTORAL_LATEX")
    LOGS  = Path(r"E:\POLYDIM_EINSOF\eval_logs")

    print("═"*60, flush=True)
    print("POLYDIM VECDB — Inicializando...", flush=True)
    
    # 1. Ingestar capítulos
    n = ingest_chapters(LATEX)
    print(f"  Capítulos actualizados en DB: {n}", flush=True)
    
    # 2. Ingestar todos los logs de eval_logs
    if LOGS.exists():
        log_files = list(LOGS.rglob("*.log")) + list(LOGS.rglob("*.json"))
        total_facts = 0
        for lf in log_files:
            if lf.stat().st_size < 50 or lf.stat().st_size > 2*1024*1024: continue
            nf = ingest_log(lf)
            total_facts += nf
        print(f"  Hechos extraídos de {len(log_files)} logs: {total_facts}", flush=True)
    
    # 3. Registrar novedades conocidas de la sesión actual
    known_novelties = [
        ("AGENT_PHI_QWEN", "benchmark", "phi_qwen_telepathy_results.json",
         "Telepatía Phi↔Qwen: 250.6x speedup, 7.662ms, 0 entropy loss. Exit Code 0 en Kaggle T4",
         ["telepatia", "pmtp"]),
        ("AGENT_LINUX_IPC", "benchmark", "all_milestones_linux.json",
         "Linux POSIX IPC: 3 milestones PASS, 0 torn reads, RTT=0.156ms, drift=0.0",
         ["linux_ipc", "pmtp"]),
        ("AGENT_TPU_JAX", "benchmark", "tpu_results.json",
         "TPU JAX D=1M: 5.48ms, norm_err=0.0. WARNING: CPU fallback, no TPU nativo",
         ["tpu_xla"]),
        ("AGENT_LINUX_BUG", "bug", "polydim-v765-linux-posix-ipc-benchmark.log",
         "Bug: total_ok=0 en test multi-proceso Linux. Causa: int Python no compartido entre forks. Fix: multiprocessing.Value",
         ["linux_ipc"]),
        ("AGENT_VECTOR_B", "brecha", "Vector_B_Roadmap.md",
         "V765 Vector B: dgeqp3+dtrcon+Tikhonov diseñado pero no compilado. Requiere implementacion C++",
         ["cayley_smw", "tikhonov"]),
    ]
    for args in known_novelties:
        ingest_novelty(*args)
    print(f"  Novedades registradas: {len(known_novelties)}", flush=True)
    
    # 4. Status final
    status = query_status()
    print(f"\n{'═'*60}", flush=True)
    print(f"POLYDIM VECDB — Estado", flush=True)
    print(f"  DB: {DB_PATH}", flush=True)
    print(f"  Capítulos: {status['chapters']['n']} | Thm: {status['chapters']['thm']} | Eq: {status['chapters']['eq']}", flush=True)
    print(f"  Hechos:    {status['facts']['n']} total | {status['facts']['cert']} certificados", flush=True)
    print(f"  Novedades: {status['novelties']['n']} total | {status['novelties']['n'] - (status['novelties']['ab'] or 0)} pendientes", flush=True)
    print(f"{'═'*60}", flush=True)
    print("Done. Exit Code 0.", flush=True)
    
    # Guardar status a disco
    Path(r"E:\POLYDIM-THEORICAL\VECDB_STATUS.json").write_text(
        json.dumps(status, ensure_ascii=False, indent=2), encoding="utf-8"
    )
