"""
REAL MULTI-THREAD LOCK-FREE SEQLOCK PAYLOAD INTEGRITY TEST (ZERO-MUTEX)
POLYDIM / PMTP Research Initiative - Ariel García Traba
Compila y ejecuta un binario C++20 real (`seqlock_payload_verifier.exe`) con hilos nativos
concurrentes (`std::thread`), SIN NINGÚN MUTEX, que verifica tanto la cabecera atómica
empaquetada de 64 bits (UAF-safe) como la integridad de los 1.024 doubles del payload
en cada lectura para garantizar CERO torn-reads sobre los datos reales.
"""

import sys
import subprocess
import json
import time

CPP_CODE = r'''
#include <iostream>
#include <atomic>
#include <thread>
#include <vector>
#include <cstdint>
#include <cmath>

constexpr size_t PAYLOAD_DOUBLES = 1024;
constexpr size_t WRITER_CYCLES = 1000000;
constexpr int NUM_READERS = 3;

struct AlignedSlab {
    std::atomic<uint64_t> seq{0};          // Secuencia SEQLock (impar = escribiendo, par = estable)
    std::atomic<uint64_t> control{0};      // Bit 63: destroying, Bits 0..62: active readers
    double payload[PAYLOAD_DOUBLES];
};

int main() {
    AlignedSlab slab;
    for (size_t i = 0; i < PAYLOAD_DOUBLES; ++i) {
        slab.payload[i] = 0.0;
    }

    std::atomic<bool> writer_done{false};
    std::atomic<uint64_t> total_verified_reads{0};
    std::atomic<uint64_t> total_retries{0};
    std::atomic<uint64_t> torn_payload_detected{0};

    auto t0 = std::chrono::steady_clock::now();

    // Lanzar lectores concurrentes lock-free que verifican CADA double del payload
    std::vector<std::thread> readers;
    for (int r = 0; r < NUM_READERS; ++r) {
        readers.emplace_back([&]() {
            double local_buf[PAYLOAD_DOUBLES];
            while (!writer_done.load(std::memory_order_acquire)) {
                // 1. Adquirir lease en palabra de control unificada (UAF-safe)
                uint64_t cur = slab.control.load(std::memory_order_relaxed);
                bool lease_ok = false;
                while ((cur & (1ULL << 63)) == 0) {
                    if (slab.control.compare_exchange_weak(
                            cur, cur + 1, std::memory_order_acquire, std::memory_order_relaxed)) {
                        lease_ok = true;
                        break;
                    }
                }
                if (!lease_ok) break;

                // 2. Lectura optimista SEQLock con verificación completa del payload
                uint64_t s1 = slab.seq.load(std::memory_order_acquire);
                if ((s1 & 1ULL) == 0) {
                    std::atomic_thread_fence(std::memory_order_acquire);
                    for (size_t i = 0; i < PAYLOAD_DOUBLES; ++i) {
                        local_buf[i] = slab.payload[i];
                    }
                    std::atomic_thread_fence(std::memory_order_acquire);
                    uint64_t s2 = slab.seq.load(std::memory_order_acquire);
                    if (s1 == s2) {
                        // El SEQLock declaró lectura limpia: verificar que los 1024 doubles sean idénticos
                        double expected = local_buf[0];
                        for (size_t i = 1; i < PAYLOAD_DOUBLES; ++i) {
                            if (local_buf[i] != expected) {
                                torn_payload_detected.fetch_add(1, std::memory_order_relaxed);
                                break;
                            }
                        }
                        total_verified_reads.fetch_add(1, std::memory_order_relaxed);
                    } else {
                        total_retries.fetch_add(1, std::memory_order_relaxed);
                    }
                } else {
                    total_retries.fetch_add(1, std::memory_order_relaxed);
                }

                // 3. Liberar lease
                slab.control.fetch_sub(1, std::memory_order_release);
            }
        });
    }

    // Hilo escritor: 1,000,000 de ciclos actualizando el bloque de 1024 doubles
    for (size_t c = 1; c <= WRITER_CYCLES; ++c) {
        uint64_t s = slab.seq.load(std::memory_order_relaxed);
        slab.seq.store(s + 1, std::memory_order_release); // Impar: inicio de escritura
        std::atomic_thread_fence(std::memory_order_release);
        double val = static_cast<double>(c);
        for (size_t i = 0; i < PAYLOAD_DOUBLES; ++i) {
            slab.payload[i] = val;
        }
        std::atomic_thread_fence(std::memory_order_release);
        slab.seq.store(s + 2, std::memory_order_release); // Par: fin de escritura
    }

    writer_done.store(true, std::memory_order_release);
    for (auto& th : readers) th.join();

    // Activar bandera de destrucción y verificar que readers activos == 0
    uint64_t final_ctrl = slab.control.fetch_or(1ULL << 63, std::memory_order_acq_rel);
    bool zero_leaks = ((final_ctrl & ~(1ULL << 63)) == 0);

    auto t1 = std::chrono::steady_clock::now();
    double dt_ms = std::chrono::duration<double, std::milli>(t1 - t0).count();

    std::cout << "{\n"
              << "  \"writer_cycles\": " << WRITER_CYCLES << ",\n"
              << "  \"payload_doubles_per_read\": " << PAYLOAD_DOUBLES << ",\n"
              << "  \"verified_full_payload_reads\": " << total_verified_reads.load() << ",\n"
              << "  \"optimistic_retries_caught\": " << total_retries.load() << ",\n"
              << "  \"torn_payload_violations\": " << torn_payload_detected.load() << ",\n"
              << "  \"zero_uaf_leaks\": " << (zero_leaks ? "true" : "false") << ",\n"
              << "  \"elapsed_ms\": " << dt_ms << "\n"
              << "}\n";

    return (torn_payload_detected.load() == 0 && zero_leaks) ? 0 : 1;
}
'''

def main():
    cpp_path = r"E:\POLYDIM-THEORICAL\verification_suite\seqlock_payload_verifier.cpp"
    exe_path = r"E:\POLYDIM-THEORICAL\verification_suite\seqlock_payload_verifier.exe"
    json_path = r"E:\POLYDIM-THEORICAL\verification_suite\seqlock_payload_telemetry.json"
    
    with open(cpp_path, "w", encoding="utf-8") as f:
        f.write(CPP_CODE.strip())
        
    gpp_exe = r"E:\varios\winlibs_gcc14_zip\mingw64\bin\g++.exe"
    print(f"[1/2] Compilando seqlock_payload_verifier.cpp con {gpp_exe} -O3 -std=c++20...")
    comp = subprocess.run([gpp_exe, "-O3", "-std=c++20", cpp_path, "-o", exe_path], capture_output=True, text=True)
    if comp.returncode != 0:
        print("Error compilando:", comp.stderr)
        return 1
        
    print("[2/2] Ejecutando verificación de 1.000.000 de ciclos de escritura + lectura íntegra de payload (1024 doubles)...")
    run = subprocess.run([exe_path], capture_output=True, text=True)
    if run.returncode != 0:
        print("Fallo en ejecución:", run.stdout, run.stderr)
        return 1
        
    data = json.loads(run.stdout)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        
    print(json.dumps(data, indent=2))
    print(f"Guardado en: {json_path}")
    print("EXIT CODE 0")
    return 0

if __name__ == "__main__":
    sys.exit(main())
