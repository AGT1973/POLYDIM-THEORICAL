import os
import shutil

scratch_dir = r"H:\Mi unidad\POLYDIM_CLA\scratch"
book_dir = r"H:\Mi unidad\POLYDIM_CLA\POLYDIM_THE_BOOK"

files_to_merge = [
    "EXP_VOL_1.md",
    "EXP_VOL_2.md",
    "EXP_VOL_3.md",
    "EXP_VOL_4.md",
    "EXP_VOL_5.md"
]

output_md = os.path.join(book_dir, "POLYDIM_CONSTITUCION_sp.md")
output_doc = os.path.join(book_dir, "POLYDIM_CONSTITUCION_sp.docx")

# Merge
with open(output_md, "w", encoding="utf-8") as outfile:
    outfile.write("# CONSTITUCIÓN POLYDIM-CLA (Libro Blanco)\n\n")
    outfile.write("*Edición Extendida 2026 - 100 Carillas*\n\n")
    outfile.write("---\n\n")
    
    for f_name in files_to_merge:
        f_path = os.path.join(scratch_dir, f_name)
        if os.path.exists(f_path):
            with open(f_path, "r", encoding="utf-8") as infile:
                outfile.write(f"<!-- BEGIN {f_name} -->\n")
                outfile.write(infile.read())
                outfile.write(f"\n<!-- END {f_name} -->\n\n")
        else:
            print(f"Warning: {f_path} not found.")

print(f"Constitucion MD generada en {output_md}")

# Since Word opens HTML natively, we convert the MD to HTML and save as .doc
# or if pypandoc is there, to .docx
try:
    import markdown
    html_text = markdown.markdown(open(output_md, encoding='utf-8').read(), extensions=['tables', 'fenced_code'])
    html_content = f"<html><head><meta charset='utf-8'></head><body>{html_text}</body></html>"
    # Overwrite the empty .docx with this fake doc
    with open(output_doc, "w", encoding="utf-8") as d:
        d.write(html_content)
    print(f"Documento DOCX generado (como HTML wrapper) en {output_doc}")
except ImportError:
    print("Markdown module not found. Copying .md to .docx for basic fallback.")
    shutil.copy2(output_md, output_doc)
