"""
POLYDIM — Cruzador de Vectores: Teoría vs _HISTORICO
Lee TEORIA_VECTOR.json + HISTORICO_INVENTORY.json del disco.
Cruza, detecta brechas y genera GAPS_REPORT.md y GAPS_CHAPLIST.json.
Zero tokens de chat — todo a disco.
"""
import json, re
from pathlib import Path
from collections import defaultdict

TEORIA_JSON   = Path(r"E:\POLYDIM-THEORICAL\TEORIA_VECTOR.json")
HIST_JSON     = Path(r"E:\POLYDIM-THEORICAL\CONSTITUCION_TESIS_MANIFESTO\HISTORICO_INVENTORY.json")
GAPS_MD       = Path(r"E:\POLYDIM-THEORICAL\GAPS_REPORT.md")
GAPS_JSON     = Path(r"E:\POLYDIM-THEORICAL\GAPS_CHAPLIST.json")

# ── CARGA ──────────────────────────────────────────────────────────────────────
teoria  = json.loads(TEORIA_JSON.read_text(encoding="utf-8")) if TEORIA_JSON.exists() else []
hist    = json.loads(HIST_JSON.read_text(encoding="utf-8"))   if HIST_JSON.exists()  else []

print(f"Teoría: {len(teoria)} capítulos | Histórico: {len(hist)} archivos")

# ── ÍNDICE DE TEORÍA: keywords + benchmarks + secciones concatenados ─────────
teoria_blob = " ".join(
    v["chapter"] + " " +
    " ".join(v["sections"]) + " " +
    " ".join(v["keywords"]) + " " +
    " ".join(v["benchmarks"]) + " " +
    " ".join(t["body"] for t in v["theorems"])
    for v in teoria
).lower()

# ── TOPIC PATTERNS (igual que vectorizar_historico.py) ───────────────────────
TOPIC_PATTERNS = {
    "telepatia_neural": r"telepath|phi.qwen|qwen.phi|latent.transfer|neural.bridge",
    "pmtp_zerocopy":    r"pmtp|zero.copy|shared.memory|seqlock|triple.buffer",
    "rodrigues":        r"rodrigues|geodesic|s\^{d-1}|sfera|variedad.esferic",
    "cayley_smw":       r"cayley|sherman.morrison|woodbury|stiefel|retrac",
    "clifford":         r"clifford|rotor|geometric.algebra|hodge|blade",
    "betti":            r"betti|topol|homolog|gudhi|union.find|dsu",
    "dpi_teorema":      r"desigualdad.procesamiento|data.processing.inequality|dpi",
    "vector_b_tikhonov":r"tikhonov|dgeqp3|dtrcon|qr.pivot|singular|cond",
    "dart_ffi":         r"dart|ffi|flutter|nativeheap|interop",
    "hardware_probe":   r"hardware.probe|silicon.contract|agnostic|rocm|hip|xla|tpu",
    "openmp":           r"openmp|omp_|parallel|nthreads|mxcsr|ftz|daz",
    "rust_guard":       r"rust|polydim_rust|betti_guard|verify_invariant",
    "triton_gpu":       r"triton|cuda|gpu|t4|a100|rodrigues_pass",
    "latam_tokens":     r"latam|argentina|blood.token|costo|dolar",
    "interlat_rfc":     r"interlat|rfc|protocolo.abierto|estandar",
    "swarm_evolution":  r"swarm|enjambre|evolucion|agente.alumno|multi.agent",
    "cerebras_wse":     r"cerebras|wse|wafer|sram|csx",
    "dart_v764":        r"dart.v76|polydim_ffi_v76|4\.27.ms|standalone.bridge",
    "linux_posix_ipc":  r"posix_ipc|\/dev\/shm|shm_open|linux.native|dev.shm",
    "tpu_jax":          r"jax|tpu|xla|cpu.device.*fallback",
}

# ── COBERTURA: topic en teoría? ───────────────────────────────────────────────
coverage = {}
for topic, pat in TOPIC_PATTERNS.items():
    coverage[topic] = bool(re.search(pat, teoria_blob))

# ── ARCHIVOS DEL HISTÓRICO SIN COBERTURA EN TEORÍA ───────────────────────────
# Para cada archivo del histórico: topics presentes → ¿cuáles sin cobertura?
gaps_by_topic = defaultdict(list)
fully_covered = []
partially_covered = []
not_covered = []

for item in hist:
    if not item["topics"]:
        continue
    covered_topics   = [t for t in item["topics"] if coverage.get(t, False)]
    uncovered_topics = [t for t in item["topics"] if not coverage.get(t, False)]
    if not uncovered_topics:
        fully_covered.append(item)
    elif not covered_topics:
        not_covered.append(item)
        for t in uncovered_topics:
            gaps_by_topic[t].append(item["path"])
    else:
        partially_covered.append(item)
        for t in uncovered_topics:
            gaps_by_topic[t].append(item["path"])

# ── REPORTE MD ────────────────────────────────────────────────────────────────
md = ["# GAPS REPORT — _HISTORICO vs TESIS POLYDIM V765\n\n"]
md.append(f"**Teoría:** {len(teoria)} capítulos | **Histórico:** {len(hist)} archivos\n\n")

md.append("## Estado de Cobertura por Topic\n\n")
md.append("| Topic | En Tesis | Archivos en _historico |\n")
md.append("|-------|----------|------------------------|\n")
for topic, pat in TOPIC_PATTERNS.items():
    ok    = "✅" if coverage[topic] else "❌ BRECHA"
    n     = len(gaps_by_topic.get(topic, []))
    md.append(f"| `{topic}` | {ok} | {n} archivos con evidencia |\n")

md.append(f"\n## Resumen\n\n")
md.append(f"- ✅ Archivos del histórico completamente cubiertos: **{len(fully_covered)}**\n")
md.append(f"- ⚠️  Parcialmente cubiertos: **{len(partially_covered)}**\n")
md.append(f"- ❌ Sin ninguna cobertura en tesis: **{len(not_covered)}**\n\n")

md.append("## Top Brechas: Archivos con Más Topics Faltantes\n\n")
uncov_sorted = sorted(not_covered + partially_covered,
                      key=lambda x: len([t for t in x["topics"] if not coverage.get(t)]),
                      reverse=True)[:30]
for item in uncov_sorted:
    missing = [t for t in item["topics"] if not coverage.get(t)]
    if not missing: continue
    md.append(f"\n### `{item['path']}` ({item['size_kb']} KB)\n")
    md.append(f"- **Topics sin cubrir:** {', '.join(missing)}\n")
    md.append(f"- **Preview:** {item['preview'][:180]}\n")

md.append("\n## Brechas por Topic (archivos fuente)\n\n")
for topic, files in sorted(gaps_by_topic.items(), key=lambda x: -len(x[1])):
    md.append(f"\n### ❌ `{topic}` ({len(files)} archivos)\n")
    for f in files[:8]:
        md.append(f"  - `{f}`\n")

GAPS_MD.write_text("".join(md), encoding="utf-8")
print(f"GAPS_REPORT.md: {GAPS_MD}  ({GAPS_MD.stat().st_size//1024} KB)")

# ── GAPS JSON (para uso programático futuro) ──────────────────────────────────
gaps_out = {
    "coverage": coverage,
    "not_covered_count": len(not_covered),
    "partially_covered_count": len(partially_covered),
    "gaps_by_topic": {k: v[:10] for k, v in gaps_by_topic.items()},
    "top_gap_files": [
        {"path": x["path"], "size_kb": x["size_kb"],
         "missing_topics": [t for t in x["topics"] if not coverage.get(t)]}
        for x in uncov_sorted[:20]
    ]
}
GAPS_JSON.write_text(json.dumps(gaps_out, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"GAPS_CHAPLIST.json: {GAPS_JSON}  ({GAPS_JSON.stat().st_size//1024} KB)")

# ── RESUMEN A CONSOLA (mínimo) ────────────────────────────────────────────────
brechas = [t for t, ok in coverage.items() if not ok]
print(f"\n{'='*55}")
print(f"TOPICS SIN COBERTURA EN TESIS: {len(brechas)}")
for t in brechas:
    print(f"  ❌ {t}: {len(gaps_by_topic.get(t,[]))} archivos en _historico")
print(f"\nArchivos sin cubrir:      {len(not_covered)}")
print(f"Archivos parcial:         {len(partially_covered)}")
print(f"{'='*55}")
print("Done. Exit Code 0.")
