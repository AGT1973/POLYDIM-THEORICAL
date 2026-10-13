"""
REAL EMPIRICAL BENCHMARK: CLIFFORD-WHT RECONSTRUCTION UNDER PACKET LOSS
POLYDIM / PMTP Research Initiative - Ariel García Traba
Ejecuta la Transformada Rápida de Walsh-Hadamard (FWHT) real sobre tensores en S^{D-1}
con pérdida estocástica de paquetes UDP (Monte Carlo con semillas múltiples) y registra
telemetría genuina con varianza real, tiempos de reloj físico y hashes de ejecución.
"""

import sys
import time
import csv
import json
import hashlib
import numpy as np

def fwht_inplace(a: np.ndarray) -> np.ndarray:
    """Fast Walsh-Hadamard Transform vectorizada O(D log D) en numpy."""
    x = a.copy()
    n = x.shape[0]
    h = 1
    while h < n:
        x = x.reshape(-1, 2, h)
        u = x[:, 0, :].copy()
        v = x[:, 1, :].copy()
        x[:, 0, :] = u + v
        x[:, 1, :] = u - v
        h *= 2
    return x.reshape(-1) / np.sqrt(n)

def run_benchmark():
    D = 65536  # 2^16 para ejecución rápida y exacta de múltiples semillas en CPU
    drop_rates = [0.05, 0.10, 0.15, 0.20]
    seeds = [101, 202, 303, 404, 505]
    
    csv_path = r"E:\POLYDIM-THEORICAL\verification_suite\wan_wht_empirical_telemetry.csv"
    md_path = r"E:\POLYDIM-THEORICAL\SOTA\WAN_EMPIRICAL_BENCHMARK.md"
    
    rows = []
    print("=" * 75)
    print(f"EJECUTANDO BENCHMARK EMPÍRICO FWHT (D={D}, {len(seeds)} seeds por tasa)")
    print("=" * 75)
    
    for p in drop_rates:
        mse_raw_list = []
        mse_wht_list = []
        cos_sim_raw_list = []
        cos_sim_wht_list = []
        lat_list = []
        
        for seed in seeds:
            rng = np.random.default_rng(seed)
            t0 = time.perf_counter()
            
            # Estado original en S^{D-1} con estructura localizada (sparse spikes + suave)
            x = np.zeros(D, dtype=np.float64)
            spike_idx = rng.choice(D, size=64, replace=False)
            x[spike_idx] = rng.standard_normal(64) * 10.0
            x += rng.standard_normal(D) * 0.05
            x /= np.linalg.norm(x)
            
            # Máscara de pérdida de paquetes en ráfaga (bloques de 256 floats = 2KB packet)
            pkt_size = 256
            num_pkts = D // pkt_size
            pkt_keep = rng.random(num_pkts) >= p
            mask = np.repeat(pkt_keep, pkt_size).astype(np.float64)
            
            # 1. Transmisión Directa (Sin dispersión WHT)
            x_raw_rx = x * mask
            norm_raw = np.linalg.norm(x_raw_rx)
            x_raw_retracted = x_raw_rx / norm_raw if norm_raw > 1e-12 else x_raw_rx
            mse_raw = float(np.mean((x - x_raw_retracted) ** 2))
            cos_raw = float(np.dot(x, x_raw_retracted))
            
            # 2. Transmisión con Dispersión Unitaria FWHT + Retracción Esférica Compensada
            y_tx = fwht_inplace(x)
            y_rx = y_tx * mask
            # Reescalado de energía por tasa de recepción conocida y retorno FWHT (involución)
            keep_ratio = max(np.mean(mask), 1e-6)
            x_wht_rec = fwht_inplace(y_rx / keep_ratio)
            x_wht_retracted = x_wht_rec / np.linalg.norm(x_wht_rec)
            
            mse_wht = float(np.mean((x - x_wht_retracted) ** 2))
            cos_wht = float(np.dot(x, x_wht_retracted))
            lat_ms = (time.perf_counter() - t0) * 1000.0
            
            mse_raw_list.append(mse_raw)
            mse_wht_list.append(mse_wht)
            cos_sim_raw_list.append(cos_raw)
            cos_sim_wht_list.append(cos_wht)
            lat_list.append(lat_ms)
            
            rows.append({
                "timestamp_ns": time.time_ns(),
                "seed": seed,
                "dimension": D,
                "packet_loss_pct": p * 100.0,
                "actual_loss_pct": round((1.0 - float(np.mean(mask))) * 100.0, 3),
                "mse_direct_drop": f"{mse_raw:.8e}",
                "mse_wht_retracted": f"{mse_wht:.8e}",
                "cosine_direct": f"{cos_raw:.6f}",
                "cosine_wht": f"{cos_wht:.6f}",
                "latency_ms": f"{lat_ms:.3f}"
            })
            
        print(f"Loss {p*100:4.1f}% | Direct Cos: {np.mean(cos_sim_raw_list):.4f} ± {np.std(cos_sim_raw_list):.4f} "
              f"| WHT Cos: {np.mean(cos_sim_wht_list):.4f} ± {np.std(cos_sim_wht_list):.4f} "
              f"| Lat: {np.mean(lat_list):.2f} ms")

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    with open(csv_path, "rb") as f:
        csv_hash = hashlib.sha256(f.read()).hexdigest()

    md_content = f"""# Telemetría Empírica Real: Reconstrucción FWHT bajo Pérdida de Paquetes en Ráfaga
**Autor:** Ariel García Traba (POLYDIM-EINSOF Independent Research)  
**Script Generador:** `E:\\POLYDIM-THEORICAL\\verification_suite\\bench_wan_wht_real.py`  
**CSV Crudo:** `E:\\POLYDIM-THEORICAL\\verification_suite\\wan_wht_empirical_telemetry.csv`  
**SHA-256 del CSV:** `{csv_hash}`  
**Nota Metodológica:** Reemplaza la tabla sintética previa. Simulación Monte Carlo en silicio real ($D={D}$, bloques de paquete de 256 floats, 5 semillas estocásticas por nivel de pérdida) midiendo la preservación de picos localizados bajo pérdida en ráfaga (burst loss) con y sin pre-dispersión de Walsh-Hadamard (`fwht_inplace`).

| Pérdida Nominal (%) | Pérdida Efectiva (%) | Seed | MSE Directo | MSE con FWHT | Coseno Directo | Coseno FWHT | Latencia (ms) |
|---|---|---|---|---|---|---|---|
"""
    for r in rows:
        md_content += f"| {r['packet_loss_pct']:.1f} | {r['actual_loss_pct']:.2f} | {r['seed']} | `{r['mse_direct_drop']}` | `{r['mse_wht_retracted']}` | {r['cosine_direct']} | {r['cosine_wht']} | {r['latency_ms']} |\n"

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    print("=" * 75)
    print(f"CSV escrito en: {csv_path} (SHA256: {csv_hash[:16]}...)")
    print("EXIT CODE 0")
    return 0

if __name__ == "__main__":
    sys.exit(run_benchmark())
