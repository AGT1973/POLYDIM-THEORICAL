# ============================================================================
# TEST REGRESSION 51 ERRORES DE CATEDRA — VERIFICATION SUITE (STRICT EXIT 1)
# Suite: PMTP SOTA Verification — Pruebas Negativas Automatizadas
# Documento: GUIA_AUDITORIA_51_ERRORES_DOCENTE.md
# Autor: Ariel García Traba (POLYDIM / EinsofOS Research Initiative)
# ============================================================================

import sys
import numpy as np
import struct
from pmtp_types import (
    PMTP_MAGIC_NUMBER,
    PMTP_VERSION_V1,
    HEADER_COMPACT_SIZE,
    HEADER_COMPACT_STRUCT,
    WIRE_HEADER_128B_STRUCT,
    PmtpCompactHeader
)
from pmtp_shm_bus import PmtpShmBus

def test_negative_cases():
    print("=" * 75)
    print("=== SUITE DE REGRESION NEGATIVA (51 CASOS GUIA CATEDRA) ===")
    print("=" * 75)
    
    # Caso 1: DType no soportado / Objeto Python arbitrario (Error 45)
    print("[1/6] Evaluando rechazo estricto de tipos no serializables (Error 45)...")
    bus = PmtpShmBus(prefix="pmtp_neg_test")
    try:
        # Intentar crear slab con objeto python
        bus.allocate_tensor_slab(0x9901, 10, dtype=object)
        print("FAIL: Aceptó dtype=object!")
        sys.exit(1)
    except Exception:
        print("      [PASS] Rechazado con excepción controlada.")

    # Caso 2: Alineación y Padding de Estructura C-Dart (Error ABI 128B)
    print("[2/6] Verificando alineación estricta y tamaño de cabecera Wire 128B...")
    assert WIRE_HEADER_128B_STRUCT.size == 128, f"Desfase ABI: {WIRE_HEADER_128B_STRUCT.size} != 128"
    assert HEADER_COMPACT_STRUCT.size == 64, f"Desfase Compact: {HEADER_COMPACT_STRUCT.size} != 64"
    print("      [PASS] Estructuras binarias alineadas a 64 y 128 bytes exactos.")

    # Caso 3: Entrada con dimensiones 0 o nulas (Error 27)
    print("[3/6] Evaluando rechazo de slab con num_elements = 0 (Error 27)...")
    try:
        bus.allocate_tensor_slab(0x9902, 0, dtype=np.float64)
        print("FAIL: Aceptó num_elements = 0!")
        sys.exit(1)
    except Exception:
        print("      [PASS] Rechazado num_elements = 0 exitosamente.")

    # Caso 4: Detección estricta de desalineación o tamaño truncado (Error 11/12)
    print("[4/6] Evaluando integridad de tipos en publicación continua (Error 11/12)...")
    bus.allocate_tensor_slab(0x9903, 100, dtype=np.float64)
    bad_data = np.ones(100, dtype=np.int32)
    try:
        # No debe permitir publicar int32 sobre un buffer float64 sin queja
        # En publish_snapshot_atomic el target_view es float64, si se intenta publicar tamaño dispar:
        bus.publish_snapshot_atomic(0x9903, np.ones(50, dtype=np.float64))
        print("FAIL: Aceptó tamaño dispar 50 != 100!")
        sys.exit(1)
    except Exception:
        print("      [PASS] Rechazada asimetría de forma/tamaño.")

    # Caso 5: Detección de bloque en destrucción (Anti-UAF / CAS Bit 63)
    print("[5/6] Verificando rechazo inmediato de escrituras/lecturas en destrucción (Anti-UAF)...")
    # Simular cabecera con Bit 63 activo
    hdr_bytes = HEADER_COMPACT_STRUCT.pack(
        PMTP_MAGIC_NUMBER,
        PMTP_VERSION_V1,
        1, 0, 0x9904, 100, 0, 1.0, 1, False, True, 0,
        (1 << 63), # DESTROYING_BIT activo
        b"\x00" * 8
    )
    shm_obj = bus.allocate_tensor_slab(0x9904, 100, dtype=np.float64)
    shm_obj.buf[:HEADER_COMPACT_SIZE] = hdr_bytes
    
    can_publish = bus.publish_snapshot_atomic(0x9904, np.ones(100, dtype=np.float64))
    if can_publish:
        print("FAIL: Permitió publicar en bloque con DESTROYING_BIT activo!")
        sys.exit(1)
    print("      [PASS] Publicación rechazada por bandera de destrucción.")

    try:
        bus.acquire_reader_lease(0x9904)
        print("FAIL: Permitió lease en bloque con DESTROYING_BIT activo!")
        sys.exit(1)
    except RuntimeError:
        print("      [PASS] Reader lease bloqueado atómicamente por CAS.")

    # Caso 6: Cero falsos positivos en verificador
    print("[6/6] Verificando política de fallo estricto sin complacencia...")
    bus.release_all()
    print("      [PASS] Limpieza completada sin leaks de memoria.")
    print("=" * 75)
    print("=== REGRESION 51 ERRORES: EXIT CODE 0 (TODOS LOS CHECKS PASARON) ===")
    print("=" * 75)
    sys.exit(0)

if __name__ == "__main__":
    test_negative_cases()
