# ============================================================================
# MASTER SILICON SUITE RUNNER — PMTP 10/10 UNIFIED VERIFICATION
# Ejecuta la suite de verificación completa de extremo a extremo en <60s
# Autor: Ariel García Traba (POLYDIM / EinsofOS Research Initiative)
# ============================================================================

import os
import sys
import time
import subprocess

TESTS = [
    ("1. C++20 / Dart ABI & CAS Silicio", [sys.executable, "-c", """
import os
from pmtp_ffi_bridge import PmtpNativeShmHandle
import numpy as np
h = PmtpNativeShmHandle('pmtp_master_check', 0x7777, 2048, create=True)
arr = np.linspace(1.0, 10.0, 2048, dtype=np.float64)
assert h.publish_atomic(arr)
out, gen = h.read_leased()
assert np.max(np.abs(out - arr)) == 0.0
h.close()
print('      [PASS] C++20 Native Engine & Anti-UAF CAS verificado.')
"""]),
    ("2. DLPack Zero-Copy Interoperability", [sys.executable, "-c", """
from pmtp_shm_bus import PmtpShmBus
import numpy as np, torch
bus = PmtpShmBus(prefix='pmtp_dlpack_master')
shm = bus.allocate_tensor_slab(0x6666, 1024, dtype=np.float32)
arr = np.ones(1024, dtype=np.float32) * 99.0
assert bus.publish_snapshot_atomic(0x6666, arr)
raw_proxy = bus.get_zero_copy_dlpack_tensor(0x6666)
t = torch.from_dlpack(raw_proxy)
assert t.shape[0] == 1024 and t[0].item() == 99.0
bus.release_all()
print('      [PASS] DLPack Zero-Copy torch interoperability certificada.')
"""]),
    ("3. Regresión Negativa (51 Casos Cátedra)", [sys.executable, r"E:\POLYDIM-THEORICAL\verification_suite\test_regression_51_cases.py"]),
    ("4. Sinceramiento de Transporte ('Peras con Peras')", [sys.executable, r"E:\POLYDIM-THEORICAL\verification_suite\benchmark_transport_matrix_honest.py"]),
    ("5. Identidad Neuronal Bit a Bit (Qwen2.5-0.5B)", [sys.executable, r"E:\POLYDIM-THEORICAL\verification_suite\test_qwen_identity_reproducible.py"])
]

def run_all():
    print("=" * 80)
    print("=== PMTP MASTER VERIFICATION SUITE — SILICON CONTRACT 10/10 ===")
    print("=" * 80)
    t_global_0 = time.perf_counter()

    for idx, (name, cmd) in enumerate(TESTS, 1):
        print(f"\n[{idx}/{len(TESTS)}] Ejecutando {name}...")
        t0 = time.perf_counter()
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        elapsed = time.perf_counter() - t0
        
        if proc.returncode != 0:
            print(f"FAIL CRÍTICO en {name} (Exit Code {proc.returncode}):")
            print(proc.stdout)
            print(proc.stderr)
            sys.exit(1)
        else:
            print(f"      Completado con éxito en {elapsed:.2f}s (Exit Code 0)")

    total_time = time.perf_counter() - t_global_0
    print("\n" + "=" * 80)
    print(f"=== PMTP SILICON PROOFS: ALL PASSED (EXIT CODE 0) EN {total_time:.2f}s ===")
    print("=" * 80)
    sys.exit(0)

if __name__ == "__main__":
    run_all()
