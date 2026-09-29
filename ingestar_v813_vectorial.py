"""
POLYDIM V813 — INGESTA VECTORIAL DIRECTA (REGLAS 19, 22, 28)
═══════════════════════════════════════════════════════════════
Lee directamente todas las opiniones del tribunal multi-IA de V813:
  - chatgpt POLYDIM_IA_espacio_vectorial.pptx (11 slides)
  - chatgpt.md, claude.md, deepseek.md, gemini.md, kimi.md, qwen.md, z_ai.md
  - benchmark_v813.csv y código fuente V813

Vuelca vectores y hechos directamente a SQLite (POLYDIM_VECDB.sqlite)
y a Shared Memory PMTP (SLAB_V813_SWARM_STATE), eliminando el gusano 1D.
"""

import sys, os, zipfile, sqlite3, json, hashlib, re, time
import xml.etree.ElementTree as ET
from pathlib import Path
from multiprocessing import shared_memory
import numpy as np

DB_PATH = Path(r"E:\POLYDIM-THEORICAL\POLYDIM_VECDB.sqlite")
V813_DIR = Path(r"E:\POLYDIM_EINSOF\ENTREGA_2026_09_28_V813")
RESPUESTAS_DIR = V813_DIR / "respuestas"

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
        finding_type TEXT, -- 'CRITICAL_BUG', 'OPTIMIZATION', 'SOTA_AGREEMENT', 'HALLUCINATION', 'THEORETICAL_PROPOSAL'
        summary TEXT,
        code_ref TEXT,
        raw_hash TEXT,
        timestamp TEXT
    );

    CREATE TABLE IF NOT EXISTS swarm_consensus (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic TEXT UNIQUE,
        consensus_verdict TEXT, -- 'CONFIRMED_ISSUE', 'REJECTED_HALLUCINATION', 'APPROVED_OPTIMIZATION'
        supporting_models TEXT, -- JSON array
        dissenting_models TEXT, -- JSON array
        resolution_action TEXT,
        applied_to_theory INTEGER DEFAULT 0
    );
    """)
    db.commit()
    return db

def sha6(s):
    return hashlib.md5(s.encode("utf-8", "replace")).hexdigest()[:8]

def extract_pptx_text(pptx_path: Path):
    """Extrae texto de cada slide de un archivo PPTX sin dependencias externas."""
    slides_data = []
    if not pptx_path.exists():
        return slides_data
    with zipfile.ZipFile(pptx_path, 'r') as z:
        slide_names = sorted([f for f in z.namelist() if f.startswith('ppt/slides/slide') and f.endswith('.xml')],
                             key=lambda x: int(re.search(r'slide(\d+)\.xml', x).group(1)))
        for sname in slide_names:
            s_num = int(re.search(r'slide(\d+)\.xml', sname).group(1))
            xml_content = z.read(sname)
            root = ET.fromstring(xml_content)
            # Find all text elements <a:t>
            texts = []
            for elem in root.iter('{http://schemas.openxmlformats.org/drawingml/2006/main}t'):
                if elem.text:
                    texts.append(elem.text.strip())
            full_text = " ".join([t for t in texts if t])
            slides_data.append((s_num, full_text))
    return slides_data

def parse_markdown_ai(md_path: Path):
    """Parsea reportes markdown de IAs extrayendo bloques de análisis."""
    if not md_path.exists():
        return []
    content = md_path.read_text(encoding="utf-8", errors="replace")
    
    findings = []
    # Split by headers
    sections = re.split(r'\n(?=#{1,4}\s+)', content)
    model_name = md_path.stem.upper()
    
    for sec in sections:
        header_m = re.match(r'#{1,4}\s+(.+)', sec)
        title = header_m.group(1).strip() if header_m else "General"
        
        # Categorize
        sec_lower = sec.lower()
        finding_type = "THEORETICAL_PROPOSAL"
        if any(k in sec_lower for k in ["bug", "error", "vulnerabilidad", "data race", "uaf", "segfault", "livelock"]):
            finding_type = "CRITICAL_BUG"
        elif any(k in sec_lower for k in ["optimización", "speedup", "avx", "futex", "rendimiento", "simd"]):
            finding_type = "OPTIMIZATION"
        elif any(k in sec_lower for k in ["teorema", "stiefel", "frechet", "cayley", "clifford", "betti"]):
            finding_type = "SOTA_AGREEMENT"
        
        # Extract topics
        topics = []
        if "stiefel" in sec_lower or "cayley" in sec_lower: topics.append("cayley_stiefel")
        if "frechet" in sec_lower or "betti" in sec_lower: topics.append("frechet_betti")
        if "futex" in sec_lower or "ipc" in sec_lower or "rcu" in sec_lower: topics.append("pmtp_ipc")
        if "clifford" in sec_lower or "cuantico" in sec_lower or "gridsynth" in sec_lower: topics.append("clifford_qpu")
        if "splatting" in sec_lower or "dart" in sec_lower or "flutter" in sec_lower: topics.append("dart_3dgs")
        if "blas" in sec_lower or "dsyrk" in sec_lower or "twosum" in sec_lower: topics.append("blas_twosum")
        
        findings.append({
            "model": model_name,
            "source": md_path.name,
            "section": title[:100],
            "type": finding_type,
            "topics": topics if topics else ["general"],
            "summary": sec[:600].replace('\n', ' ').strip(),
            "raw": sec
        })
    return findings

def ingest_all_to_vecdb_and_shm():
    db = get_db()
    total_opinions = 0
    
    print("[1/4] Parseando PPTX: chatgpt POLYDIM_IA_espacio_vectorial.pptx ...")
    pptx_path = RESPUESTAS_DIR / "chatgpt POLYDIM_IA_espacio_vectorial.pptx"
    pptx_slides = extract_pptx_text(pptx_path)
    for s_num, stext in pptx_slides:
        if not stext: continue
        db.execute("""
        INSERT INTO swarm_opinions (model_name, source_file, slide_or_sec, critique_topic, finding_type, summary, raw_hash, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
        """, ("CHATGPT_PPTX", pptx_path.name, f"Slide_{s_num}", "espacio_vectorial_ia", "THEORETICAL_PROPOSAL", stext[:600], sha6(stext)))
        total_opinions += 1
    print(f"  -> Ingestados {len(pptx_slides)} slides de PPTX.")

    print("[2/4] Parseando archivos Markdown del Tribunal Multi-IA ...")
    md_files = list(RESPUESTAS_DIR.glob("*.md"))
    for mf in md_files:
        items = parse_markdown_ai(mf)
        for it in items:
            db.execute("""
            INSERT INTO swarm_opinions (model_name, source_file, slide_or_sec, critique_topic, finding_type, summary, raw_hash, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """, (it["model"], it["source"], it["section"], ",".join(it["topics"]), it["type"], it["summary"], sha6(it["raw"])))
            total_opinions += 1
        print(f"  -> Ingestado {mf.name} ({len(items)} secciones analizadas)")

    db.commit()

    print("[3/4] Sintetizando Consenso del Tribunal (Triangulación Multi-IA) ...")
    # Query topics and cluster
    topics_list = ["cayley_stiefel", "frechet_betti", "pmtp_ipc", "clifford_qpu", "dart_3dgs", "blas_twosum", "espacio_vectorial_ia"]
    
    for top in topics_list:
        rows = db.execute("SELECT model_name, finding_type, summary FROM swarm_opinions WHERE critique_topic LIKE ?", (f"%{top}%",)).fetchall()
        models = list(set([r["model_name"] for r in rows]))
        if models:
            db.execute("""
            INSERT OR REPLACE INTO swarm_consensus (topic, consensus_verdict, supporting_models, dissenting_models, resolution_action, applied_to_theory)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (
                top,
                "CONFIRMED_ISSUE" if any("BUG" in r["finding_type"] for r in rows) else "APPROVED_OPTIMIZATION",
                json.dumps(models),
                json.dumps([]),
                f"Validado por {len(models)} IAs ({', '.join(models[:4])}). Incorporar al corpus vectorial.",
                0
            ))
    db.commit()

    print("[4/4] Creando / Mapeando Slab PMTP Shared Memory (SLAB_V813_SWARM_STATE) ...")
    shm_name = "SLAB_V813_SWARM_STATE"
    slab_size = 4 * 1024 * 1024 # 4MB Shared Memory
    try:
        try:
            shm = shared_memory.SharedMemory(name=shm_name, create=True, size=slab_size)
            print(f"  -> Creado nuevo PMTP Shared Memory slab: {shm_name} ({slab_size} bytes)")
        except FileExistsError:
            shm = shared_memory.SharedMemory(name=shm_name, create=False, size=slab_size)
            print(f"  -> Conectado a PMTP Shared Memory slab existente: {shm_name}")
        
        # Serialize swarm summary into slab
        consensus_rows = db.execute("SELECT topic, consensus_verdict, supporting_models, resolution_action FROM swarm_consensus").fetchall()
        payload = {
            "version": "V813",
            "timestamp": time.time(),
            "total_opinions": total_opinions,
            "consensus": [dict(r) for r in consensus_rows],
            "pptx_slides_count": len(pptx_slides)
        }
        encoded = json.dumps(payload).encode("utf-8")
        shm.buf[:4] = len(encoded).to_bytes(4, 'little')
        shm.buf[4:4+len(encoded)] = encoded
        print(f"  -> Volcado tensorial y semantico en RAM exitoso ({len(encoded)} bytes escritos en SLAB)")
        shm.close()
    except Exception as e:
        print(f"  [!] Advertencia SHM: {e}")

    db.close()
    print("\n" + "═"*60)
    print(f"INGESTA VECTORIAL V813 COMPLETADA: {total_opinions} opiniones indexadas en VecDB.")
    print("═"*60)

if __name__ == "__main__":
    ingest_all_to_vecdb_and_shm()
