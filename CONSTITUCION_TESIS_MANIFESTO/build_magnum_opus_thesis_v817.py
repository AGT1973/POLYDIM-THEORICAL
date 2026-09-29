import os
import re
import subprocess

latex_dir = "CONSTITUCION_TESIS_MANIFESTO/TESIS_DOCTORAL_LATEX"
output_md = "CONSTITUCION_TESIS_MANIFESTO/TESIS_DOCTORAL_POLYDIM_V817_MAGNA.md"
output_docx = "CONSTITUCION_TESIS_MANIFESTO/TESIS_DOCTORAL_POLYDIM_V817.docx"

chapter_order = [
    "cap01_prefacio.tex",
    "cap02_dogma_no_worm.tex",
    "cap03_dpi_formal.tex",
    "cap04_variedad_esferica.tex",
    "cap05_clifford_rotores.tex",
    "cap06_rodrigues.tex",
    "cap07_cayley_smw.tex",
    "cap08_betti_topologia.tex",
    "cap09_clifford_qpu.tex",
    "cap10_bargmann_pancharatnam.tex",
    "cap11_pmtp_protocolo.tex",
    "cap12_seqlock_hardened.tex",
    "cap13_latent_os.tex",
    "cap14_ffi_abi.tex",
    "cap15_hardware_heterogeneo.tex",
    "cap16_kernel_cpp.tex",
    "cap17_kernel_rust.tex",
    "cap18_triton_gpu.tex",
    "cap19_orquestador_python.tex",
    "cap20_fases_certificadas.tex",
    "cap21_metodologia_red_team.tex",
    "cap22_resultados_silicio.tex",
    "cap23_escalabilidad.tex",
    "cap24_impacto_termodinamico.tex",
    "cap25_latam_tokens.tex",
    "cap26_futuro_interlat.tex",
    "cap_v764_auditoria.tex",
    "cap_v765_telepathy.tex",
    "cap_v765_vector_b.tex",
    "cap_v814_tribunal_espacio_vectorial.tex",
    "cap_v815_estabilidad_espectral.tex",
    "apendice_a_codigo_fuente.tex",
    "apendice_b_telemetria.tex",
    "apendice_c_demostraciones.tex"
]

header = """# POLYDIM: Magnum Opus Doctoral Thesis (Kernel Series 800 — V817)
## Continuous High-Dimensional Manifold Computing and Heterogeneous Silicon Isometry

**Author:** Ariel García Traba  
**Affiliation:** Independent Researcher — Lecturer at Universidad Tecnológica Nacional (UTN-FRBA)  
**Initiative:** POLYDIM / EinsofOS Research Initiative  
**Contact:** `ariel.garcia.traba@gmail.com` | `polydim-cla@gmail.com`  
**Date:** September 2026 — Master Release V817  

---

"""

merged_content = [header]

for ch in chapter_order:
    path = os.path.join(latex_dir, ch)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            tex = f.read()
        # Clean basic latex commands to markdown
        tex_clean = re.sub(r'\\chapter\{([^}]+)\}', r'# \1', tex)
        tex_clean = re.sub(r'\\section\{([^}]+)\}', r'## \1', tex_clean)
        tex_clean = re.sub(r'\\subsection\{([^}]+)\}', r'### \1', tex_clean)
        tex_clean = re.sub(r'\\subsubsection\{([^}]+)\}', r'#### \1', tex_clean)
        tex_clean = re.sub(r'\\textbf\{([^}]+)\}', r'**\1**', tex_clean)
        tex_clean = re.sub(r'\\textit\{([^}]+)\}', r'*\1*', tex_clean)
        tex_clean = re.sub(r'\\texttt\{([^}]+)\}', r'`\1`', tex_clean)
        tex_clean = re.sub(r'\\begin\{itemize\}', r'', tex_clean)
        tex_clean = re.sub(r'\\end\{itemize\}', r'', tex_clean)
        tex_clean = re.sub(r'\\begin\{enumerate\}', r'', tex_clean)
        tex_clean = re.sub(r'\\end\{enumerate\}', r'', tex_clean)
        tex_clean = re.sub(r'\\item\s+', r'- ', tex_clean)
        tex_clean = re.sub(r'\\begin\{lstlisting\}(?:\[.*?\])?', r'```python', tex_clean)
        tex_clean = re.sub(r'\\end\{lstlisting\}', r'```', tex_clean)
        tex_clean = re.sub(r'\\begin\{verbatim\}', r'```', tex_clean)
        tex_clean = re.sub(r'\\end\{verbatim\}', r'```', tex_clean)
        tex_clean = re.sub(r'\\cite\{[^}]+\}', r'[Ref]', tex_clean)
        
        merged_content.append(f"\n\n<!-- CHAPTER: {ch} -->\n\n" + tex_clean)

with open(output_md, "w", encoding="utf-8") as f:
    f.write("\n".join(merged_content))

print(f"Generated {output_md} ({os.path.getsize(output_md)} bytes)")

pandoc_exe = r"C:\Users\eluithi\AppData\Local\Pandoc\pandoc.exe"
if os.path.exists(pandoc_exe):
    cmd = [pandoc_exe, output_md, "-o", output_docx]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0:
        print(f"Compiled {output_docx} ({os.path.getsize(output_docx)} bytes)")
    else:
        print(f"Pandoc error: {res.stderr}")
