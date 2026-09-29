"""
POLYDIM — Vectorizador de _HISTORICO (versión rápida)
Límite: 500 KB por archivo, máx 2000 archivos, sólo extensiones texto.
Salida progresiva con flush. Todo a disco.
"""
import os, json, hashlib, re, sys
from pathlib import Path
from collections import defaultdict

ROOT    = Path(r"E:\polydim_einsof\_historico")
OUTPUT  = Path(r"E:\POLYDIM-THEORICAL\CONSTITUCION_TESIS_MANIFESTO\HISTORICO_INVENTORY.json")
REPORT  = Path(r"E:\POLYDIM-THEORICAL\CONSTITUCION_TESIS_MANIFESTO\BRECHAS_HISTORICO.md")

MAX_FILE_KB   = 500    # ignorar archivos > 500 KB
MAX_FILES     = 3000
EXT_OK = {".md",".txt",".py",".rs",".cpp",".h",".json",".tex",".dart",".log",".csv",".bat",".toml",".yaml",".yml"}

TOPIC_PATTERNS = {
    "telepatia_neural": r"telepath|phi.qwen|qwen.phi|latent.transfer|neural.bridge",
    "pmtp_zerocopy":    r"pmtp|zero.copy|shared.memory|seqlock|triple.buffer",
    "rodrigues":        r"rodrigues|geodesic|variedad.esferic|s_d.1",
    "cayley_smw":       r"cayley|sherman.morrison|woodbury|stiefel|retrac",
    "clifford":         r"clifford|rotor|geometric.algebra|hodge|blade",
    "betti":            r"betti|topolog|homolog|gudhi|union.find|dsu",
    "dpi_teorema":      r"desigualdad.procesamiento|data.processing.inequality|dpi",
    "vector_b_tikhonov":r"tikhonov|dgeqp3|dtrcon|qr.pivot",
    "dart_ffi":         r"dart|flutter|nativeheap",
    "hardware_probe":   r"hardware.probe|silicon.contract|rocm|hip",
    "openmp":           r"openmp|omp_get|nthreads|mxcsr|ftz|daz",
    "rust_guard":       r"rust|polydim_rust|verify_invariant",
    "triton_gpu":       r"triton|cuda|t4.gpu|a100|rodrigues_pass",
    "latam_tokens":     r"latam|argentina|blood.token",
    "interlat_rfc":     r"interlat|rfc|protocolo.abierto",
    "swarm_evolution":  r"swarm|enjambre|agente.alumno|multi.agent",
    "cerebras_wse":     r"cerebras|wse|wafer|csx",
    "dart_v764":        r"dart.*v76|polydim_ffi_v76|4\.27.ms",
    "linux_posix_ipc":  r"posix_ipc|dev.shm|shm_open|linux.native",
    "tpu_jax":          r"jax|tpu.*benchmark|xla.device",
    "swarm_v765":       r"v765|vector.b|dgeqp3",
    "auditoria_bg":     r"auditoria.bg|bg0[0-9]|reduccion.jerarquica|cholqr",
    "neumaier":         r"neumaier|compensated.sum|twosum|kahan",
    "bargmann":         r"bargmann|pancharatnam|geometric.phase|berry.phase",
}

def sha6(s): return hashlib.md5(s.encode("utf-8","replace")).hexdigest()[:6]

def extract_topics(text):
    tl = text.lower()
    return [t for t, p in TOPIC_PATTERNS.items() if re.search(p, tl)]

print("Escaneando _HISTORICO (modo rápido)...", flush=True)
inventory = []
skipped_size = skipped_ext = 0
n = 0

for path in sorted(ROOT.rglob("*")):
    if not path.is_file(): continue
    if path.suffix.lower() not in EXT_OK:
        skipped_ext += 1
        continue
    size = path.stat().st_size
    if size > MAX_FILE_KB * 1024:
        skipped_size += 1
        continue
    try:
        raw = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        skipped_ext += 1
        continue
    topics = extract_topics(raw)
    lines  = [l.strip() for l in raw.splitlines() if l.strip()][:2]
    inventory.append({
        "path":     str(path.relative_to(ROOT)),
        "size_kb":  round(size/1024, 1),
        "hash":     sha6(raw),
        "topics":   topics,
        "preview":  " | ".join(lines)[:150],
    })
    n += 1
    if n % 100 == 0:
        print(f"  [{n}] procesados...", flush=True)
    if n >= MAX_FILES:
        print(f"  Límite {MAX_FILES} archivos alcanzado.", flush=True)
        break

print(f"  Total: {n} archivos | >500KB omitidos: {skipped_size} | ext omitidos: {skipped_ext}", flush=True)

# ── JSON ──────────────────────────────────────────────────────────────────────
OUTPUT.write_text(json.dumps(inventory, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"JSON: {OUTPUT}  ({OUTPUT.stat().st_size//1024} KB)", flush=True)

# ── REPORTE RÁPIDO ────────────────────────────────────────────────────────────
topic_files = defaultdict(list)
for item in inventory:
    for t in item["topics"]:
        topic_files[t].append(item["path"])

# Cargar tesis
THESIS = Path(r"E:\POLYDIM-THEORICAL\CONSTITUCION_TESIS_MANIFESTO\TESIS_DOCTORAL_LATEX")
thesis_blob = ""
if THESIS.exists():
    for f in THESIS.glob("*.tex"):
        try: thesis_blob += f.read_text(encoding="utf-8", errors="replace")
        except: pass
thesis_blob = thesis_blob.lower()

coverage = {t: bool(re.search(p, thesis_blob)) for t, p in TOPIC_PATTERNS.items()}
brechas  = [t for t, ok in coverage.items() if not ok]

md = ["# BRECHAS _HISTORICO vs TESIS\n\n"]
md.append(f"Archivos escaneados: {n} | Cobertura topics: {len(TOPIC_PATTERNS)-len(brechas)}/{len(TOPIC_PATTERNS)}\n\n")
md.append("| Topic | Tesis | Archivos _hist |\n|-------|-------|----------------|\n")
for t, p in TOPIC_PATTERNS.items():
    ok = "✅" if coverage[t] else "❌"
    md.append(f"| `{t}` | {ok} | {len(topic_files.get(t,[]))} |\n")

md.append("\n## Top Archivos sin Cobertura\n")
gap_items = [i for i in inventory if any(not coverage.get(t) for t in i["topics"])]
gap_items.sort(key=lambda x: sum(1 for t in x["topics"] if not coverage.get(t)), reverse=True)
for item in gap_items[:30]:
    missing = [t for t in item["topics"] if not coverage.get(t)]
    if not missing: continue
    md.append(f"\n- **`{item['path']}`** ({item['size_kb']} KB) → {', '.join(missing)}\n")
    md.append(f"  *{item['preview'][:120]}*\n")

REPORT.write_text("".join(md), encoding="utf-8")
print(f"REPORT: {REPORT}  ({REPORT.stat().st_size//1024} KB)", flush=True)

print(f"\n{'='*50}")
print(f"BRECHAS DETECTADAS: {len(brechas)}")
for t in brechas:
    print(f"  ❌ {t}: {len(topic_files.get(t,[]))} archivos")
print("Done. Exit Code 0.", flush=True)
