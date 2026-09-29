r"""
POLYDIM Watchdog — Monitor persistente via Windows Task Scheduler.
Escanea cambios en el workspace práctico y genera entradas en INBOX_TEORIA.md.
Se ejecuta cada 30 minutos via schtasks, sobrevive reinicios.

Instalación (una sola vez, desde PowerShell como admin):
  schtasks /create /tn "POLYDIM_Watchdog" /tr "python E:\POLYDIM-THEORICAL\polydim_watchdog.py" /sc MINUTE /mo 30 /f

Desinstalación:
  schtasks /delete /tn "POLYDIM_Watchdog" /f
"""
import os
import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path

# === CONFIGURACIÓN ===
WORKSPACE = Path(r"E:\POLYDIM_EINSOF")
THEORY_DIR = Path(r"E:\POLYDIM-THEORICAL")
INBOX = THEORY_DIR / "INBOX_TEORIA.md"
STATE_FILE = THEORY_DIR / ".watchdog_state.json"

# Extensiones a monitorear en el workspace práctico
WATCH_EXTENSIONS = {".py", ".cpp", ".rs", ".h", ".toml", ".log", ".json"}

# Patrones que indican descubrimientos teóricos
THEORY_KEYWORDS = [
    "drift", "torn_read", "betti", "neumaier", "rodrigues", "cayley",
    "pmtp", "seqlock", "epsilon", "norm", "convergence", "diverge",
    "bug", "fix", "hallazgo", "benchmark", "certified", "exit code",
    "subnormal", "flush", "ftz", "arm64", "tpu", "tikhonov",
]


def load_state():
    """Carga el estado anterior (hashes de archivos)."""
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {}


def save_state(state):
    """Guarda el estado actual."""
    STATE_FILE.write_text(
        json.dumps(state, indent=2, default=str), encoding="utf-8"
    )


def hash_file(path):
    """SHA-256 de un archivo."""
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()[:12]
    except (OSError, PermissionError):
        return None


def scan_workspace():
    """Escanea archivos relevantes en el workspace práctico."""
    files = {}
    for ext in WATCH_EXTENSIONS:
        for p in WORKSPACE.rglob(f"*{ext}"):
            # Ignorar directorios pesados
            parts = p.parts
            if any(skip in parts for skip in [
                "__pycache__", ".git", "node_modules", "site-packages",
                "_HISTORICO", ".agents"
            ]):
                continue
            rel = str(p.relative_to(WORKSPACE))
            h = hash_file(p)
            if h:
                files[rel] = {"hash": h, "size": p.stat().st_size}
    return files


def detect_theory_relevance(filepath, content_sample=""):
    """Detecta si un cambio es relevante para la teoría."""
    text = (filepath + " " + content_sample).lower()
    hits = [kw for kw in THEORY_KEYWORDS if kw in text]
    return hits


def generate_inbox_entry(filepath, change_type, keywords):
    """Genera una entrada para INBOX_TEORIA.md."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    kw_str = ", ".join(keywords) if keywords else "general"
    entry = f"""
## PENDIENTE: {change_type} en `{filepath}`
- **Fecha:** {now}
- **Tipo:** {"NOVEDAD" if change_type == "new" else "CAMBIO"}
- **Keywords detectadas:** {kw_str}
- **Fuente:** `E:\\POLYDIM_EINSOF\\{filepath}`
- **Acción sugerida:** Evaluar si requiere formalización teórica (remark, proposición o teorema) en el capítulo correspondiente.

---
"""
    return entry


def main():
    old_state = load_state()
    current_files = scan_workspace()
    new_entries = []

    for rel, info in current_files.items():
        old_info = old_state.get(rel)
        if old_info is None:
            # Archivo nuevo
            keywords = detect_theory_relevance(rel)
            if keywords:
                new_entries.append(generate_inbox_entry(rel, "new", keywords))
        elif (old_info.get("hash") if isinstance(old_info, dict) else old_info) != info["hash"]:
            # Archivo modificado
            try:
                sample = Path(WORKSPACE / rel).read_text(
                    encoding="utf-8", errors="ignore"
                )[:2000]
            except Exception:
                sample = ""
            keywords = detect_theory_relevance(rel, sample)
            if keywords:
                new_entries.append(
                    generate_inbox_entry(rel, "modified", keywords)
                )

    # Escribir al inbox si hay novedades
    if new_entries:
        header = ""
        if not INBOX.exists():
            header = "# INBOX Teoría — Buzón Automático del Watchdog\n\n"
            header += "> Generado automáticamente por polydim_watchdog.py\n"
            header += "> Cada entrada fue detectada como cambio práctico "
            header += "con relevancia teórica.\n\n---\n"

        with open(INBOX, "a", encoding="utf-8") as f:
            if header:
                f.write(header)
            for entry in new_entries:
                f.write(entry)

        print(f"[WATCHDOG] {len(new_entries)} entradas escritas en INBOX")
    else:
        print("[WATCHDOG] Sin cambios teóricos relevantes")

    # Guardar estado
    save_state(current_files)


if __name__ == "__main__":
    main()
