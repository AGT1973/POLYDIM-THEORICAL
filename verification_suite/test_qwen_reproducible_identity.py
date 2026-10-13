"""
SUITE DE VERIFICACIÓN FÍSICA: REPRODUCIBILIDAD ESTOCÁSTICA CERO (BETA = 0)
Nodo Aladín Debian 13 (Intel Core i3-8100 4C/4T @ 3.6GHz, 8GB DDR4)
Ollama Endpoint: http://192.168.100.21:11434
Modelo: qwen2.5-coder:1.5b
Evalúa la invariancia determinista del oráculo de silicio bajo temperatura=0.0 y seed fija.
"""

import sys
import json
import hashlib
import time
import urllib.request

def run_reproducible_query(prompt, seed=42):
    url = "http://192.168.100.21:11434/api/generate"
    payload = {
        "model": "qwen2.5-coder:1.5b",
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.0,
            "seed": seed,
            "top_p": 1.0,
            "num_predict": 64
        }
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=60) as resp:
        res = json.loads(resp.read().decode("utf-8"))
    lat_ms = (time.time() - t0) * 1000.0
    text = res.get("response", "").strip()
    h = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return text, h, lat_ms

def main():
    print("=" * 70)
    print("AUDITORÍA DE REPRODUCIBILIDAD EN SILICIO NODO ALADIN (DDR4)")
    print("=" * 70)
    prompt = "State the definition of the Stiefel manifold St(k, n) in one concise mathematical sentence."
    
    print("Ejecutando Pase 1 (Seed 42, Temp 0.0)...")
    txt1, hash1, lat1 = run_reproducible_query(prompt, seed=42)
    print(f"  Pase 1 ({lat1:.1f} ms) | SHA-256: {hash1[:16]}...")
    print(f"  Respuesta: {txt1}")
    
    print("\nEjecutando Pase 2 (Seed 42, Temp 0.0)...")
    txt2, hash2, lat2 = run_reproducible_query(prompt, seed=42)
    print(f"  Pase 2 ({lat2:.1f} ms) | SHA-256: {hash2[:16]}...")
    print(f"  Respuesta: {txt2}")
    
    # Verificación determinista estricta
    assert hash1 == hash2, "ERROR: Discrepancia en ejecución determinista temperatura 0"
    assert txt1 == txt2, "ERROR: Variación textual entre pases idénticos"
    print("\n" + "=" * 70)
    print(f"VERIFICACIÓN EXIT CODE 0: HASHES COINCIDEN 100% BIT-EXACT ({hash1})")
    print(f"Latencia promedio: {(lat1 + lat2) / 2.0:.1f} ms en hardware DDR4 de Aladín")
    print("=" * 70)
    return 0

if __name__ == "__main__":
    sys.exit(main())
