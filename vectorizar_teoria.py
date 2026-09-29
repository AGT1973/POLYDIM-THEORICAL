"""
POLYDIM — Vectorizador de Teoría (Tesis LaTeX)
Lee todos los .tex, extrae: capítulo, secciones, teoremas, fórmulas, código, benchmarks.
Genera un índice semántico compacto en JSON + resumen por capítulo en MD.
TODO A DISCO. Zero tokens en chat.
"""
import re, json, hashlib
from pathlib import Path

LATEX_DIR = Path(r"E:\POLYDIM-THEORICAL\CONSTITUCION_TESIS_MANIFESTO\TESIS_DOCTORAL_LATEX")
OUT_JSON  = Path(r"E:\POLYDIM-THEORICAL\TEORIA_VECTOR.json")
OUT_MD    = Path(r"E:\POLYDIM-THEORICAL\TEORIA_SUMMARY.md")
OUT_INDEX = Path(r"E:\POLYDIM-THEORICAL\TEORIA_INDEX.txt")  # índice plano comprimido

def sha6(s): return hashlib.md5(s.encode("utf-8","replace")).hexdigest()[:6]

def extract_chapter(tex):
    m = re.search(r'\\chapter\*?\{([^}]+)\}', tex)
    return m.group(1).strip() if m else "?"

def extract_sections(tex):
    return re.findall(r'\\(?:sub)*section\*?\{([^}]+)\}', tex)

def extract_theorems(tex):
    """Extrae entornos theorem/lemma/definition/proof con su contenido"""
    envs = re.findall(
        r'\\begin\{(theorem|lemma|definition|remark|proof|corollary)\}(.*?)\\end\{\1\}',
        tex, re.DOTALL
    )
    out = []
    for kind, body in envs:
        body_clean = re.sub(r'\s+', ' ', body).strip()[:300]
        out.append({"type": kind, "body": body_clean})
    return out

def extract_equations(tex):
    """Extrae ecuaciones display (\\[ ... \\] y equation env)"""
    eqs = re.findall(r'\\begin\{equation\*?\}(.*?)\\end\{equation\*?\}', tex, re.DOTALL)
    eqs += re.findall(r'\\\[(.*?)\\\]', tex, re.DOTALL)
    return [re.sub(r'\s+',' ', e).strip()[:200] for e in eqs[:20]]  # max 20 por cap

def extract_benchmarks(tex):
    """Detecta números con unidades de medida (ms, GB/s, e-16, etc.)"""
    return re.findall(r'[\d\.]+\s*(?:ms|GB/s|MB/s|µs|ns|×10|\\times10|e-\d+|\\varepsilon)', tex)[:15]

def extract_code_langs(tex):
    """Detecta bloques de código y su lenguaje"""
    return list(set(re.findall(r'\\begin\{lstlisting\}.*?language=(\w+)', tex) +
                    re.findall(r'style=(\w+style)', tex)))

def extract_keywords(tex):
    """Palabras clave POLYDIM de alta densidad semántica"""
    kws = re.findall(r'\\textbf\{([^}]{3,40})\}', tex)
    return list(set(kws))[:30]

def process_file(path):
    raw = path.read_text(encoding="utf-8", errors="replace")
    return {
        "file":       path.name,
        "size_kb":    round(path.stat().st_size / 1024, 1),
        "hash":       sha6(raw),
        "chapter":    extract_chapter(raw),
        "sections":   extract_sections(raw),
        "theorems":   extract_theorems(raw),
        "equations":  extract_equations(raw),
        "benchmarks": extract_benchmarks(raw),
        "code_langs": extract_code_langs(raw),
        "keywords":   extract_keywords(raw),
        "n_lines":    raw.count('\n'),
    }

# ── SCAN ──────────────────────────────────────────────────────────────────────
print("Vectorizando teoría LaTeX...")
tex_files = sorted([f for f in LATEX_DIR.glob("*.tex") if f.name != "main.tex"])
print(f"  Archivos .tex: {len(tex_files)}")

vector = []
for f in tex_files:
    try:
        v = process_file(f)
        vector.append(v)
        thm_n = len(v["theorems"])
        eq_n  = len(v["equations"])
        print(f"  [{v['hash']}] {f.name:40s} | {v['size_kb']:6.1f} KB | "
              f"§{len(v['sections'])} thm={thm_n} eq={eq_n} bm={len(v['benchmarks'])}")
    except Exception as e:
        print(f"  ERROR {f.name}: {e}")

# ── JSON VECTOR ────────────────────────────────────────────────────────────────
OUT_JSON.write_text(json.dumps(vector, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\nVector JSON: {OUT_JSON}  ({OUT_JSON.stat().st_size//1024} KB)")

# ── SUMMARY MD ────────────────────────────────────────────────────────────────
md = ["# POLYDIM — Vector Semántico de la Tesis\n\n"]
md.append(f"**Capítulos:** {len(vector)} | **Generado:** 2026-09-21\n\n")
md.append("| # | Archivo | Cap | §§ | Thm | Eq | BM | KB |\n")
md.append("|---|---------|-----|----|----|----|----|----|\n")
for i, v in enumerate(vector, 1):
    cap = v["chapter"][:40]
    md.append(f"| {i} | `{v['file']}` | {cap} | "
              f"{len(v['sections'])} | {len(v['theorems'])} | "
              f"{len(v['equations'])} | {len(v['benchmarks'])} | {v['size_kb']} |\n")

md.append("\n## Detalle por Capítulo\n")
for v in vector:
    md.append(f"\n### `{v['file']}` — {v['chapter']}\n")
    if v["sections"]:
        md.append(f"**Secciones:** {' | '.join(v['sections'][:6])}\n")
    if v["theorems"]:
        md.append(f"**Teoremas/Lemas:** {len(v['theorems'])}\n")
        for t in v["theorems"][:2]:
            md.append(f"  - *{t['type']}*: {t['body'][:120]}...\n")
    if v["benchmarks"]:
        md.append(f"**Benchmarks:** {', '.join(v['benchmarks'][:6])}\n")
    if v["keywords"]:
        md.append(f"**Keywords:** {', '.join(v['keywords'][:10])}\n")

OUT_MD.write_text("".join(md), encoding="utf-8")
print(f"Summary MD:  {OUT_MD}  ({OUT_MD.stat().st_size//1024} KB)")

# ── ÍNDICE PLANO COMPRIMIDO ────────────────────────────────────────────────────
# Formato ultra-compacto para referencia rápida sin abrir archivos
idx_lines = []
for v in vector:
    secs = ";".join(v["sections"][:4])
    kws  = ";".join(v["keywords"][:5])
    bms  = ";".join(v["benchmarks"][:4])
    idx_lines.append(
        f"{v['file']}|{v['hash']}|{v['size_kb']}|{v['chapter']}|"
        f"s={len(v['sections'])}|thm={len(v['theorems'])}|eq={len(v['equations'])}|"
        f"SECS=[{secs}]|KWS=[{kws}]|BMS=[{bms}]"
    )
OUT_INDEX.write_text("\n".join(idx_lines), encoding="utf-8")
print(f"Index TXT:   {OUT_INDEX}  ({OUT_INDEX.stat().st_size//1024} KB)")

# ── ESTADÍSTICAS GLOBALES ──────────────────────────────────────────────────────
total_thm = sum(len(v["theorems"]) for v in vector)
total_eq  = sum(len(v["equations"]) for v in vector)
total_bm  = sum(len(v["benchmarks"]) for v in vector)
total_kb  = sum(v["size_kb"] for v in vector)
total_ln  = sum(v["n_lines"] for v in vector)

print(f"\n{'='*60}")
print(f"TEORÍA VECTORIZADA — TOTALES")
print(f"  Capítulos:   {len(vector)}")
print(f"  Líneas LaTeX:{total_ln:,}")
print(f"  Tamaño:      {total_kb:.0f} KB")
print(f"  Teoremas:    {total_thm}")
print(f"  Ecuaciones:  {total_eq}")
print(f"  Benchmarks:  {total_bm} referencias numéricas")
print(f"{'='*60}")
print("Done. Exit Code 0.")
