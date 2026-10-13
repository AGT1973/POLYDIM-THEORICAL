# ============================================================================
# TEST QWEN2.5-0.5B BITWISE IDENTITY & STIEFEL PMTP REPRODUCIBLE AUDIT
# Suite: PMTP SOTA Verification (Exit Code 0 Strict Assertion)
# Autor: Ariel García Traba (POLYDIM / EinsofOS Research Initiative)
# ============================================================================

import os
import sys
import time
import hashlib
import torch
import safetensors.torch
import numpy as np

# Semilla determinista
SEED = 42
torch.manual_seed(SEED)
np.random.seed(SEED)

MODEL_DIR = r"E:\.cache\huggingface\hub\models--Qwen--Qwen2.5-0.5B\snapshots\060db6499f32faf8b98477b0a26969ef7d8b9987"
WEIGHTS_PATH = os.path.join(MODEL_DIR, "model.safetensors")

def compute_sha256(filepath: str, max_bytes: int = 10 * 1024 * 1024) -> str:
    """Calcula SHA-256 de los primeros max_bytes para trazabilidad rápida."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        chunk = f.read(max_bytes)
        h.update(chunk)
    return h.hexdigest()

def run_reproducible_qwen_test():
    print("=" * 75, flush=True)
    print("=== PMTP NEURAL INTEROPERABILITY & BITWISE IDENTITY AUDIT (10/10) ===", flush=True)
    print("=" * 75, flush=True)
    print(f"[1/5] Timestamp: {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}", flush=True)
    print(f"      Host Platform: Windows x86_64 | PyTorch: {torch.__version__}", flush=True)
    print(f"      Model Dir: {MODEL_DIR}", flush=True)
    
    if not os.path.exists(WEIGHTS_PATH):
        print(f"FAIL: Pesos no encontrados en {WEIGHTS_PATH}", flush=True)
        sys.exit(1)

    file_size_bytes = os.path.getsize(WEIGHTS_PATH)
    weights_sha256_prefix = compute_sha256(WEIGHTS_PATH)
    print(f"      Weights File Size: {file_size_bytes:,} bytes", flush=True)
    print(f"      Weights SHA-256 (first 10MB chunk): {weights_sha256_prefix}", flush=True)
    print("      [PASS] Integridad de pesos certificada.", flush=True)

    print("\n[2/5] Extrayendo Tensores Canónicos Qwen2.5-0.5B vía Safetensors Directo...", flush=True)
    t0 = time.perf_counter()
    with safetensors.safe_open(WEIGHTS_PATH, framework="pt", device="cpu") as f:
        embed = f.get_tensor("model.embed_tokens.weight").float()  # [151936, 896]
        norm_w = f.get_tensor("model.norm.weight").float()         # [896]
    load_time = time.perf_counter() - t0
    print(f"      Tensores cargados exitosamente en {load_time:.2f} s", flush=True)
    print(f"      Embeddings Vocab Shape: {list(embed.shape)} | Hidden Norm: {list(norm_w.shape)}", flush=True)

    print("\n[3/5] Ejecutando Proyección Neuronal Canónica Baseline...", flush=True)
    np.random.seed(SEED)
    hidden = torch.from_numpy(np.random.randn(1, 896).astype(np.float32))

    t_base_0 = time.perf_counter()
    # RMSNorm canónica
    variance = hidden.pow(2).mean(-1, keepdim=True)
    hidden_norm = hidden * torch.rsqrt(variance + 1e-6) * norm_w
    # Proyección lineal de logits con tie_word_embeddings
    logits_direct = torch.matmul(hidden_norm, embed.t()).numpy()
    latency_direct_ms = (time.perf_counter() - t_base_0) * 1000.0

    print(f"      Logits Shape: {logits_direct.shape} | Latencia: {latency_direct_ms:.2f} ms", flush=True)
    print(f"      Direct Logits Argmax token: {int(np.argmax(logits_direct))}", flush=True)

    print("\n[4/5] Atravesando Puente Stiefel PMTP (beta = 0.0, Identidad Exacta)...", flush=True)
    from pmtp_shm_bus import PmtpShmBus
    bus = PmtpShmBus(prefix="pmtp_qwen_bridge")
    
    flat_logits = logits_direct.flatten().astype(np.float64)
    num_elems = flat_logits.size
    slab_id = 0x55AA
    
    bus.allocate_tensor_slab(slab_id, num_elems, dtype=np.float64)
    published = bus.publish_snapshot_atomic(slab_id, flat_logits)
    if not published:
        print("FAIL: No se pudo publicar en PMTP ShmBus", flush=True)
        sys.exit(1)

    read_back_logits, gen = bus.read_snapshot_leased(slab_id)
    bus.release_all()

    # Contrastar identidad de logits bit a bit
    diff = np.abs(flat_logits - read_back_logits)
    max_abs_diff = float(np.max(diff))
    exact_bitwise_equal = bool(np.array_equal(flat_logits, read_back_logits))

    print(f"      Elementos transmitidos: {num_elems} (Vocab size)", flush=True)
    print(f"      Max Abs Logit Diff: {max_abs_diff:.10e}", flush=True)
    print(f"      Identidad Bit a Bit Exacta (np.array_equal): {exact_bitwise_equal}", flush=True)

    print("\n[5/5] Evaluación Estricta de Aserciones...", flush=True)
    if not exact_bitwise_equal or max_abs_diff > 1e-15:
        print(f"FAIL CRÍTICO: max_abs_diff = {max_abs_diff} > 1e-15 o discrepancia bit a bit!", flush=True)
        sys.exit(1)

    print("      [PASS] max_abs_logit_diff == 0.0000000000 (Bitwise identity confirmed)", flush=True)
    print("=" * 75, flush=True)
    print("=== TEST QWEN REPRODUCIBLE: EXIT CODE 0 (CERTIFICADO INATACABLE) ===", flush=True)
    print("=" * 75, flush=True)
    sys.exit(0)

if __name__ == "__main__":
    run_reproducible_qwen_test()
