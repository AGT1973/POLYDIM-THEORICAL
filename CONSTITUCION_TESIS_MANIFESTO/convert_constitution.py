#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Limpia y convierte a DOCX + HTML:
  - POLYDIM_CONSTITUCION_FINAL.md  (170 KB, tiene escapes rotos)
  - POLYDIM_PUBLICATION_KIT.md     (10 KB, tiene bloque POLYDIM_DEST)
"""
import sys, os, re, subprocess
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

PANDOC  = r"C:\Users\eluithi\AppData\Local\Pandoc\pandoc.exe"
BASE    = r"g:\Mi unidad\POLYDIM_v1_1\docs\constitution"

# ════════════════════════════════════════════════════════════
CSS_PROFESIONAL = """
@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,wght@0,400;0,600;1,400&family=Source+Code+Pro:wght@400&display=swap');
@page { size: A4; margin: 2.5cm 2.8cm; }
body { font-family: 'Source Serif 4', Georgia, serif; font-size: 11pt; line-height: 1.6; color: #111; max-width: 17cm; margin: 0 auto; padding: 1cm; background: #fff; }
h1 { font-size: 20pt; font-weight: 600; text-align: center; border-bottom: 2px solid #333; padding-bottom: 0.4em; margin-bottom: 0.3em; }
h2 { font-size: 14pt; font-weight: 600; margin-top: 2em; border-bottom: 1px solid #bbb; padding-bottom: 3px; page-break-after: avoid; color: #1a1a3a; }
h3 { font-size: 12pt; font-weight: 600; margin-top: 1.5em; page-break-after: avoid; color: #2a2a4a; }
h4 { font-size: 11pt; font-style: italic; margin-top: 1em; }
p { margin: 0.6em 0; text-align: justify; orphans: 3; widows: 3; }
pre { font-family: 'Source Code Pro', Consolas, monospace; font-size: 8.5pt; background: #f5f5f5; border: 1px solid #ddd; border-left: 3px solid #444; padding: 8px 12px; white-space: pre-wrap; word-wrap: break-word; page-break-inside: avoid; line-height: 1.4; }
code { font-family: 'Source Code Pro', Consolas, monospace; font-size: 9pt; background: #f0f0f0; padding: 1px 4px; border-radius: 2px; }
table { border-collapse: collapse; width: 100%; font-size: 9.5pt; margin: 1em 0; page-break-inside: avoid; }
th { background: #2a2a4a; color: white; font-weight: 600; text-align: left; padding: 6px 10px; border: 1px solid #999; }
td { padding: 5px 10px; border: 1px solid #bbb; vertical-align: top; }
tr:nth-child(even) { background: #f7f7ff; }
a { color: #1a0dab; }
blockquote { border-left: 4px solid #5e6ad2; margin: 1em 0; padding: 8px 15px; background: #f0f0ff; font-style: italic; border-radius: 0 4px 4px 0; }
hr { border: none; border-top: 1px solid #ccc; margin: 2em 0; }
ul, ol { margin: 0.5em 0; padding-left: 1.8em; }
li { margin: 0.3em 0; }
nav#TOC { background: #f0f0ff; border: 1px solid #5e6ad2; border-radius: 4px; padding: 12px 20px; margin-bottom: 2em; font-size: 10pt; }
nav#TOC ul { padding-left: 1.2em; } nav#TOC > ul { padding-left: 0; }
.author-block { text-align: center; margin: 1em 0 1.5em; padding: 1em; background: #f8f8ff; border-radius: 4px; font-size: 10.5pt; }
@media print { body { padding: 0; } a { color: #111; } pre, table { page-break-inside: avoid; } }
"""
# ════════════════════════════════════════════════════════════

def fix_backslash_escapes(txt):
    """Elimina los \\\\\\ escapes rotos que produce Google Docs export."""
    # Múltiples backslashes antes de _ o * — comunes en docs exportados
    txt = re.sub(r'\\{2,}(_)', r'_', txt)
    txt = re.sub(r'\\{2,}(\*)', r'*', txt)
    txt = re.sub(r'\\{2,}(\[)', r'[', txt)
    txt = re.sub(r'\\{2,}(\])', r']', txt)
    txt = re.sub(r'\\{2,}(\()', r'(', txt)
    txt = re.sub(r'\\{2,}(\))', r')', txt)
    # Escapes simples innecesarios en texto corrido
    txt = re.sub(r'\\([^`\[\]()#*_\\\n])', r'\1', txt)
    return txt

def remove_polydim_dest_header(txt):
    """Elimina el bloque de metadatos # POLYDIM_DEST."""
    txt = re.sub(
        r'^# POLYDIM_DEST.*?(?=^---\s*\n)',
        '',
        txt,
        flags=re.DOTALL | re.MULTILINE
    )
    # Quitar --- huérfano al principio si queda
    txt = re.sub(r'^\s*---\s*\n\s*\n', '', txt, count=1)
    return txt.lstrip('\n')

def make_html(body_html, title, author_block=''):
    header = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="author" content="[ANONYMIZED_AUTHOR] H. Garcia Traba">
<title>{title}</title>
<style>{CSS_PROFESIONAL}</style>
</head>
<body>
"""
    if author_block:
        body_html = body_html.replace(
            f'<h1>{title}</h1>',
            f'<h1>{title}</h1>\n<div class="author-block">{author_block}</div>'
        )
    footer = """
<hr>
<p style="font-size:9pt;color:#666;text-align:center;">
POLYDIM · [ANONYMIZED_AUTHOR] H. Garcia Traba · Buenos Aires, Argentina · 2026<br>
ORCID: 0009-0001-2787-6067 · ariel.garcia.traba@gmail.com · github.com/[ANONYMIZED_AUTHOR]
</p>
</body></html>"""
    return header + body_html + footer

def process_file(md_in, label, title, do_remove_dest=False, do_fix_escapes=False):
    print(f"\n{'='*55}")
    print(f"Procesando: {os.path.basename(md_in)}")

    with open(md_in, encoding='utf-8', errors='replace') as f:
        txt = f.read()

    if do_remove_dest:
        txt = remove_polydim_dest_header(txt)
        print("  OK: bloque POLYDIM_DEST eliminado")

    if do_fix_escapes:
        before = len(re.findall(r'\\{2,}', txt))
        txt = fix_backslash_escapes(txt)
        after = len(re.findall(r'\\{2,}', txt))
        print(f"  OK: backslash escapes rotos: {before} → {after}")

    # Guardar MD limpio
    md_clean = md_in.replace('.md', '_CLEAN.md')
    with open(md_clean, 'w', encoding='utf-8', newline='\n') as f:
        f.write(txt)
    print(f"  MD limpio: {os.path.basename(md_clean)} ({os.path.getsize(md_clean)//1024} KB)")

    # ── DOCX ─────────────────────────────────────────────────
    docx_out = md_in.replace('.md', '_CLEAN.docx')
    cmd = [PANDOC, md_clean, '-o', docx_out,
           '--standalone', '--toc', '--toc-depth=3', '--wrap=none']
    r = subprocess.run(cmd, capture_output=True, encoding='utf-8',
                       errors='replace', timeout=120)
    if r.returncode == 0:
        print(f"  DOCX OK: {os.path.basename(docx_out)} ({os.path.getsize(docx_out)//1024} KB)")
    else:
        print(f"  DOCX ERROR: {r.stderr[:200]}")

    # ── HTML ─────────────────────────────────────────────────
    html_out = md_in.replace('.md', '_CLEAN_PRINT.html')
    cmd2 = [PANDOC, md_clean, '-t', 'html5',
            '--toc', '--toc-depth=3', '--wrap=none']
    r2 = subprocess.run(cmd2, capture_output=True, encoding='utf-8',
                        errors='replace', timeout=120)
    if r2.returncode == 0:
        html = make_html(
            r2.stdout, title,
            author_block=(
                "<strong>[ANONYMIZED_AUTHOR] H. Garcia Traba</strong> · Independent Researcher · "
                "Buenos Aires, Argentina · 2026<br>"
                "ORCID: 0009-0001-2787-6067 · ariel.garcia.traba@gmail.com"
            )
        )
        with open(html_out, 'w', encoding='utf-8', newline='\n') as f:
            f.write(html)
        print(f"  HTML OK: {os.path.basename(html_out)} ({os.path.getsize(html_out)//1024} KB)")
    else:
        print(f"  HTML ERROR: {r2.stderr[:200]}")

    return md_clean, docx_out, html_out

# ════════════════════════════════════════════════════════════
# 1. CONSTITUCIÓN FINAL
# ════════════════════════════════════════════════════════════
process_file(
    md_in         = BASE + r"\POLYDIM_CONSTITUCION_FINAL.md",
    label         = "constitucion",
    title         = "POLYDIM — Constitución Omnicomprensiva V10.0",
    do_remove_dest= False,   # No tiene bloque DEST
    do_fix_escapes= True,    # SÍ tiene escapes rotos
)

# ════════════════════════════════════════════════════════════
# 2. PUBLICATION KIT
# ════════════════════════════════════════════════════════════
process_file(
    md_in         = BASE + r"\POLYDIM_PUBLICATION_KIT.md",
    label         = "pubkit",
    title         = "POLYDIM — Kit de Publicación",
    do_remove_dest= True,    # SÍ tiene bloque DEST
    do_fix_escapes= False,
)

print("\n" + "="*55)
print("RESUMEN ARCHIVOS GENERADOS:")
for f in [
    BASE + r"\POLYDIM_CONSTITUCION_FINAL_CLEAN.docx",
    BASE + r"\POLYDIM_CONSTITUCION_FINAL_CLEAN_PRINT.html",
    BASE + r"\POLYDIM_PUBLICATION_KIT_CLEAN.docx",
    BASE + r"\POLYDIM_PUBLICATION_KIT_CLEAN_PRINT.html",
]:
    if os.path.exists(f):
        print(f"  OK  {os.path.basename(f):50s} {os.path.getsize(f)//1024} KB")
    else:
        print(f"  MISSING  {os.path.basename(f)}")
