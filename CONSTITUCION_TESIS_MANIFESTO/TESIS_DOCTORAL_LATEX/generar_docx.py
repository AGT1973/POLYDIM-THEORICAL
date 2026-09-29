"""
Generador de TESIS DOCTORAL POLYDIM en formato DOCX con fórmulas Word (OMML)
Usa pandoc para conversión LaTeX -> DOCX capitulo por capitulo, luego une con python-docx
"""
import subprocess
import sys
import os
from pathlib import Path

LATEX_DIR = Path(r"E:\POLYDIM-THEORICAL\CONSTITUCION_TESIS_MANIFESTO\TESIS_DOCTORAL_LATEX")
OUTPUT_DIR = Path(r"E:\POLYDIM-THEORICAL\CONSTITUCION_TESIS_MANIFESTO")
OUTPUT_DOCX = OUTPUT_DIR / "TESIS_DOCTORAL_POLYDIM_V764.docx"
TEMP_DIR = LATEX_DIR / "_pandoc_temp"
TEMP_DIR.mkdir(exist_ok=True)

# Orden de capítulos según main.tex
CAPITULOS = [
    "cap01_prefacio",
    "cap02_dogma_no_worm",
    "cap03_dpi_formal",
    "cap04_variedad_esferica",
    "cap05_clifford_rotores",
    "cap06_rodrigues",
    "cap07_cayley_smw",
    "cap08_betti_topologia",
    "cap09_clifford_qpu",
    "cap10_bargmann_pancharatnam",
    "cap11_pmtp_protocolo",
    "cap12_seqlock_hardened",
    "cap13_latent_os",
    "cap14_ffi_abi",
    "cap15_hardware_heterogeneo",
    "cap16_kernel_cpp",
    "cap17_kernel_rust",
    "cap18_triton_gpu",
    "cap19_orquestador_python",
    "cap_v764_auditoria",
    "cap20_fases_certificadas",
    "cap21_metodologia_red_team",
    "cap22_resultados_silicio",
    "cap23_escalabilidad",
    "cap24_impacto_termodinamico",
    "cap25_latam_tokens",
    "cap26_futuro_interlat",
    "apendice_a_codigo_fuente",
    "apendice_b_telemetria",
    "apendice_c_demostraciones",
]

PANDOC = r"C:\Users\eluithi\AppData\Local\Pandoc\pandoc.exe"

def tex_to_docx(cap_name):
    """Convierte un .tex individual a .docx via pandoc"""
    src = LATEX_DIR / f"{cap_name}.tex"
    dst = TEMP_DIR / f"{cap_name}.docx"
    
    if not src.exists():
        print(f"  [WARN] {cap_name}.tex no existe, saltando")
        return None
    
    cmd = [
        PANDOC,
        str(src),
        "-f", "latex",
        "-t", "docx",
        "--mathml",          # fórmulas como MathML/OMML en Word
        "-o", str(dst),
        "--resource-path", str(LATEX_DIR),
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if result.returncode == 0:
        size_kb = dst.stat().st_size / 1024
        print(f"  [OK] {cap_name}.docx ({size_kb:.1f} KB)")
        return dst
    else:
        print(f"  [WARN] {cap_name}: {result.stderr[:120]}")
        return None

def merge_docx(docs):
    """Une múltiples DOCX en uno solo usando python-docx"""
    from docx import Document
    from docx.shared import Pt, RGBColor, Inches
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
    import copy
    
    def add_page_break(doc):
        p = doc.add_paragraph()
        run = p.add_run()
        br = OxmlElement('w:br')
        br.set(qn('w:type'), 'page')
        run._r.append(br)
    
    # Crear documento maestro con portada
    master = Document()
    
    # Configurar márgenes
    from docx.shared import Cm
    for section in master.sections:
        section.top_margin = Cm(3)
        section.bottom_margin = Cm(3)
        section.left_margin = Cm(3.5)
        section.right_margin = Cm(2.5)
    
    # ---- PORTADA ----
    master.add_heading("DIMENSION IS ALL YOU NEED", level=0)
    p = master.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("Fundamentación Matemática, Arquitectura de Sistema Operativo Latente\n"
                    "y Protocolo PMTP Zero-Copy para la Comunicación Nativa en S^(D-1)")
    run.font.size = Pt(14)
    run.font.italic = True
    
    master.add_paragraph()
    p = master.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("Ariel García Traba\nPOLYDIM / EinsofOS Research Initiative\nSeptiembre de 2026")
    run.font.size = Pt(16)
    run.font.bold = True
    
    master.add_paragraph()
    p = master.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("Kernel V764 Certificado: Exit Code 0, 5/5 Suites PASS\n"
                    "Drift ≤ 4.44 × 10⁻¹⁶ | PMTP Max Bit Diff = 0")
    run.font.size = Pt(11)
    run.font.color.rgb = RGBColor(0, 91, 170)
    
    add_page_break(master)
    
    # ---- RESUMEN ----
    master.add_heading("Resumen", level=1)
    master.add_paragraph(
        "El paradigma hegemónico del Procesamiento del Lenguaje Natural impone que la "
        "comunicación entre agentes inteligentes transite por secuencias unidimensionales "
        "de tokens discretos. Esta tesis demuestra teórica y empíricamente que este colapso "
        "constituye una Paradoja del Gusano 1D que destruye irreversiblemente información "
        "geométrica bajo la Desigualdad de Procesamiento de Datos (DPI).\n\n"
        "Para erradicar este colapso, se presenta POLYDIM / Latent_OS y el protocolo "
        "PMTP V764: una arquitectura donde los agentes de IA se comunican nativamente "
        "mediante tensores en S^(D-1) (D = 10^6) vía Memoria Compartida Zero-Copy.\n\n"
        "Resultados certificados en silicio: 35.06 ms con deriva ≤ 4.44×10⁻¹⁶; "
        "transferencia PMTP 10.69 ms con cero distorsión de bits; 100% de ataques "
        "adversariales bloqueados. Auditoría posterior V764: 12 hallazgos A1-A12 cerrados."
    )
    add_page_break(master)
    
    # ---- FUSIONAR CAPÍTULOS ----
    total_ok = 0
    for doc_path in docs:
        if doc_path is None:
            continue
        try:
            src_doc = Document(str(doc_path))
            # Agregar separador de capítulo
            for element in src_doc.element.body:
                # Copiar cada elemento del cuerpo al documento maestro
                master.element.body.append(copy.deepcopy(element))
            add_page_break(master)
            total_ok += 1
        except Exception as e:
            print(f"  [MERGE WARN] {doc_path.name}: {e}")
    
    master.save(str(OUTPUT_DOCX))
    size_mb = OUTPUT_DOCX.stat().st_size / (1024*1024)
    print(f"\n{'='*60}")
    print(f"DOCX GENERADO: {OUTPUT_DOCX}")
    print(f"Capítulos fusionados: {total_ok}/{len(docs)}")
    print(f"Tamaño: {size_mb:.2f} MB")
    print(f"{'='*60}")

# ---- MAIN ----
print("POLYDIM TESIS DOCTORAL — Generador DOCX con fórmulas Word")
print("="*60)
print(f"Pandoc: {PANDOC}")
print(f"Capítulos a procesar: {len(CAPITULOS)}")
print()

converted = []
for cap in CAPITULOS:
    print(f"Convirtiendo {cap}...")
    result = tex_to_docx(cap)
    converted.append(result)

print(f"\nConversión completa: {sum(1 for c in converted if c)} / {len(CAPITULOS)}")
print("\nFusionando en DOCX final...")
merge_docx(converted)
