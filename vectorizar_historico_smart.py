"""
POLYDIM — Vectorizador Inteligente de _HISTORICO (v2)
Estrategia: priorizar por fecha reciente + nombre relevante + subdirectorio.
Saltea archivos ya escaneados (via hash cache). Max 500 por subdirectorio.
Genera un resumen ejecutivo compacto a disco. Zero tokens de chat.
"""
import os, json, hashlib, re, sys
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timezone

ROOT      = Path(r"E:\polydim_einsof\_historico")
OUT_JSON  = Path(r"E:\POLYDIM-THEORICAL\HISTORICO_SMART.json")
OUT_MD    = Path(r"E:\POLYDIM-THEORICAL\HISTORICO_SMART_REPORT.md")
CACHE     = Path(r"E:\POLYDIM-THEORICAL\HISTORICO_HASH_CACHE.json")

MAX_PER_SUBDIR = 50    # max archivos por subdirectorio
MAX_TOTAL      = 5000  # tope global
MAX_FILE_KB    = 300   # ignorar > 300 KB
MIN_FILE_B     = 50    # ignorar < 50 bytes (vacíos)

# Subdirectorios prioritarios (los más relevantes para la tesis)
PRIORITY_DIRS = [
    "auditoria", "AUDITORIA", "entrega", "ENTREGA", "v76", "v77",
    "kernel", "pmtp", "stiefel", "rodrigues", "telepathy", "telepatia",
    "linux", "tpu", "gpu", "dart", "rust", "triton", "benchmark",
    "reportes", "REPORTES", "hallazgos", "HALLAZGOS",
]

EXT_OK = {".md",".txt",".py",".rs",".cpp",".h",".json",".tex",
          ".dart",".log",".csv",".bat",".toml"}

TOPIC_PATTERNS = {
    "telepatia":        r"telepath|phi.*qwen|qwen.*phi|latent.*transfer|neural.*bridge|telepat",
    "pmtp":             r"pmtp|zero.copy|shared.memory|seqlock|triple.buffer|shm_open",
    "rodrigues":        r"rodrigues|geodesic|variedad.*esfer",
    "cayley_smw":       r"cayley|sherman.*morrison|woodbury|stiefel.*retrac",
    "clifford":         r"clifford|geometric.*algebra|hodge.*star",
    "betti":            r"betti|homolog|gudhi|union.*find",
    "dpi":              r"data.processing.inequality|dpi.*theorem|desigualdad.*procesamiento",
    "tikhonov":         r"tikhonov|dgeqp3|dtrcon|qr.*pivot.*column",
    "dart_ffi":         r"dart.*ffi|polydim_ffi|nativeheap.*dart",
    "hardware_probe":   r"hardware.*probe|silicon.*contract|hardwareprobe",
    "neumaier":         r"neumaier|compensated.*sum|kahan.*babuska",
    "rust_guard":       r"rust.*guard|polydim_rust|verify_invariant",
    "triton":           r"triton.*kernel|@triton.jit|rodrigues_pass",
    "latam":            r"latam|blood.*token|argentina.*ia",
    "swarm":            r"swarm.*agent|enjambre|multi.*agent.*pmtp",
    "cerebras":         r"cerebras|wse.*3|wafer.*scale",
    "linux_ipc":        r"posix_ipc|/dev/shm|shm_open|linux.*native.*pmtp",
    "tpu_xla":          r"tpu.*rodrigues|xla.*kernel|jax.*benchmark",
    "auditoria_bg":     r"auditoria.*bg|bg0[0-9]|reduccion.*jerarquica|cholqr",
    "vector_b":         r"vector.*b.*protocol|dgeqp3.*tikhonov|solver.*adaptativo",
    "seqlock":          r"seqlock.*hardened|write_ticket|memory_order.*release",
    "dart_v764":        r"dart.*v764|polydim_ffi_v764|4\.27.*ms|dart.*standalone",
    "swarm_evolucion":  r"swarm.*evolucion|evolucion.*swarm|documento.*tesis.*swarm",
}

def sha6(s): return hashlib.md5(s.encode("utf-8","replace")).hexdigest()[:6]
def extract_topics(text):
    tl = text.lower()
    return [t for t, p in TOPIC_PATTERNS.items() if re.search(p, tl)]

def is_priority(path):
    p = str(path).lower()
    return any(d.lower() in p for d in PRIORITY_DIRS)

# ── Cargar cache de hashes ya procesados ──────────────────────────────────────
cache = {}
if CACHE.exists():
    try: cache = {x["hash"]: True for x in json.loads(CACHE.read_text(encoding="utf-8"))}
    except: pass
print(f"Cache: {len(cache)} hashes previos", flush=True)

# ── Recolectar archivos candidatos ────────────────────────────────────────────
print("Recolectando candidatos...", flush=True)
candidates = []
per_subdir = defaultdict(int)

def collect_entries(root):
    stack = [str(root)]
    while stack:
        curr = stack.pop()
        try:
            with os.scandir(curr) as it:
                for entry in it:
                    try:
                        if entry.is_dir(follow_symlinks=False):
                            stack.append(entry.path)
                        elif entry.is_file(follow_symlinks=False):
                            ext = os.path.splitext(entry.name)[1].lower()
                            if ext in EXT_OK:
                                st = entry.stat(follow_symlinks=False)
                                if MIN_FILE_B <= st.st_size <= MAX_FILE_KB * 1024:
                                    yield Path(entry.path), st.st_mtime, st.st_size
                    except OSError:
                        continue
        except OSError:
            continue

raw_candidates = []
for p, mtime, sz in collect_entries(ROOT):
    try:
        subdir = str(p.parent.relative_to(ROOT))
    except ValueError:
        subdir = ""
    if per_subdir[subdir] >= MAX_PER_SUBDIR and not is_priority(p):
        continue
    raw_candidates.append((p, mtime, sz))
    per_subdir[subdir] += 1
    if len(raw_candidates) >= MAX_TOTAL * 2:
        break

# Priorizar: primero los de directorios prioritarios, luego por fecha
raw_candidates.sort(key=lambda item: (0 if is_priority(item[0]) else 1, -item[1]))
candidates = [item[0] for item in raw_candidates[:MAX_TOTAL]]
print(f"Candidatos seleccionados: {len(candidates)}", flush=True)

# ── Procesar ──────────────────────────────────────────────────────────────────
inventory = []
new_topics_found = defaultdict(list)

for i, path in enumerate(candidates):
    try:
        raw = path.read_text(encoding="utf-8", errors="replace")
    except: continue
    
    h = sha6(raw)
    if h in cache: continue  # ya procesado
    
    topics = extract_topics(raw)
    mtime  = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).strftime("%Y-%m-%d")
    lines  = [l.strip() for l in raw.splitlines() if l.strip()][:2]
    
    item = {
        "path":    str(path.relative_to(ROOT)),
        "size_kb": round(path.stat().st_size/1024, 1),
        "hash":    h,
        "mtime":   mtime,
        "topics":  topics,
        "preview": " | ".join(lines)[:150],
        "priority": is_priority(path),
    }
    inventory.append(item)
    for t in topics:
        new_topics_found[t].append(item["path"])
    
    if (i+1) % 200 == 0:
        print(f"  [{i+1}/{len(candidates)}] topics activos: {len(new_topics_found)}", flush=True)

print(f"Procesados: {len(inventory)} archivos nuevos", flush=True)

# ── Guardar JSON ──────────────────────────────────────────────────────────────
OUT_JSON.write_text(json.dumps(inventory, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"JSON: {OUT_JSON} ({OUT_JSON.stat().st_size//1024} KB)", flush=True)

# ── Actualizar cache ──────────────────────────────────────────────────────────
all_items = inventory
if CACHE.exists():
    try: all_items = json.loads(CACHE.read_text(encoding="utf-8")) + inventory
    except: pass
CACHE.write_text(json.dumps([{"hash": x["hash"]} for x in all_items], indent=1), encoding="utf-8")

# ── Cruzar con tesis ──────────────────────────────────────────────────────────
THESIS = Path(r"E:\POLYDIM-THEORICAL\CONSTITUCION_TESIS_MANIFESTO\TESIS_DOCTORAL_LATEX")
thesis_blob = ""
for f in THESIS.glob("*.tex"):
    try: thesis_blob += f.read_text(encoding="utf-8", errors="replace")
    except: pass
thesis_blob = thesis_blob.lower()

coverage = {t: bool(re.search(p, thesis_blob)) for t, p in TOPIC_PATTERNS.items()}
brechas  = {t: new_topics_found.get(t, []) for t, ok in coverage.items() if not ok}

# ── Reporte MD ────────────────────────────────────────────────────────────────
md = [f"# HISTORICO SMART SCAN — {len(inventory)} archivos\n\n"]
md.append(f"**_historico total:** 107,950 archivos / 29.2 GB | **Escaneados:** {len(inventory)}\n\n")

md.append("## Cobertura de Topics\n\n")
md.append("| Topic | En Tesis | Archivos encontrados |\n|-------|----------|---------------------|\n")
for t in TOPIC_PATTERNS:
    ok = "✅" if coverage[t] else "❌ BRECHA"
    n  = len(new_topics_found.get(t, []))
    md.append(f"| `{t}` | {ok} | {n} |\n")

md.append(f"\n## BRECHAS ({len(brechas)} topics sin cobertura en tesis)\n\n")
for t, files in brechas.items():
    md.append(f"\n### ❌ `{t}`\n")
    for f in files[:6]:
        item = next((x for x in inventory if x["path"] == f), None)
        if item:
            md.append(f"- `{f}` ({item['size_kb']} KB, {item['mtime']})\n")
            md.append(f"  *{item['preview'][:120]}*\n")

md.append("\n## Top 20 Archivos Más Relevantes (por topics)\n\n")
top = sorted(inventory, key=lambda x: (len(x["topics"]), x["priority"]), reverse=True)[:20]
for item in top:
    md.append(f"- **`{item['path']}`** ({item['size_kb']} KB, {item['mtime']})\n")
    md.append(f"  Topics: {', '.join(item['topics'][:5])}\n")
    md.append(f"  *{item['preview'][:100]}*\n\n")

OUT_MD.write_text("".join(md), encoding="utf-8")
print(f"REPORT: {OUT_MD} ({OUT_MD.stat().st_size//1024} KB)", flush=True)

print(f"\n{'='*55}")
print(f"BRECHAS REALES: {len(brechas)}")
for t, files in brechas.items():
    print(f"  ❌ {t}: {len(files)} archivos con evidencia")
print(f"Topics cubiertos en tesis: {sum(coverage.values())}/{len(TOPIC_PATTERNS)}")
print("Done. Exit Code 0.", flush=True)
