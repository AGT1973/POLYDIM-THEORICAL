# 🌌 ARQUITECTURA POLIMÓRFICA DE MEMORIA Y CÓMPUTO MULTI-GENERACIONAL POLYDIM 2026
## Clasificación Topológica de Silicio: De Wafer-Scale SRAM a Silicio de Estrés Mínimo

---

### 1. El Principio Fundamental del Contrato de Silicio (Regla 27)

POLYDIM no asume una única arquitectura de silicio ni hardcodea supuestos sobre buses de memoria.
El hardware local mínimo (AMD A4-6300 con DDR3) actúa exclusivamente como **banco de pruebas adverso extremo (Floor of Worst-Case Stress)**. Si los algoritmos geométricos convergen en un entorno limitado (2 núcleos enteros, 1 FPU compartida, DRAM de $12.8\text{ GB/s}$), se garantiza la estabilidad matemática sin fugas ni desbordes en cualquier plataforma de producción.

El motor en tiempo de ejecución (`HardwareTopologyEngine`) interroga al anfitrión y clasifica el silicio en 5 clases de memoria y cómputo:

```
                                  ┌──────────────────────────────┐
                                  │   HardwareTopologyEngine     │
                                  └──────────────┬───────────────┘
                                                 │
      ┌────────────────────┬─────────────────────┼─────────────────────┬────────────────────┐
      ▼                    ▼                     ▼                     ▼                    ▼
[ CLASE 0: WAFER ]   [ CLASE 1: HBM ]     [ CLASE 2: GDDR ]    [ CLASE 3: DDR5/6 ]   [ CLASE 4: LEGACY ]
 Cerebras CS-2/CS-3   NVIDIA H100/H200     RTX 4090/5090 / Cloud DDR5-6400 / DDR6     AMD A4 / Core 2
 44 GB SRAM en Oblea  HBM3 / HBM3e         GDDR6X / GDDR7        8-12 Canales NUMA    DDR3 Dual Channel
 21 Petabytes/s       3.35 - 8.0 TB/s      1.0 - 1.8 TB/s        100 - 300 GB/s       12.8 GB/s
 Latencia: ~1 ns      Latencia: ~150 ns    Latencia: ~250 ns     Latencia: ~60 ns     Latencia: ~100 ns
```

---

### 2. Especificación de Clases de Hardware

```cpp
enum class HardwareClass : uint8_t {
    WAFER_SRAM_CEREBRAS = 0,  // Zero DRAM. 44 GB on-wafer SRAM. 21 PB/s 2D mesh.
    HBM_MASSIVE_ACCEL   = 1,  // HBM3/3e (3.35 - 8.0 TB/s). TMA Asynchronous Copy.
    GDDR_STREAMING      = 2,  // GDDR6/GDDR7 (1.0 - 1.8 TB/s). Coalesced GPU Warps.
    NUMA_DDR5_DDR6      = 3,  // Multi-channel High-Speed DDR5/DDR6 NUMA (100 - 300 GB/s).
    LEGACY_STRESS_HOST  = 4   // Minimal Host DDR3/DDR4 (12.8 - 25.6 GB/s) worst-case baseline.
};
```

#### 🏛️ Clase 0: Cerebras WSE (Wafer-Scale Engine CS-2 / CS-3)
* **Arquitectura de Memoria:** **Zero-DRAM**. 44 GB de memoria SRAM estática distribuida directamente sobre una oblea continua de silicio monolítico de 900,000 núcleos.
* **Ancho de Banda:** **21 Petabytes/segundo ($21{,}000{,}000\text{ GB/s}$)** sobre malla bidireccional 2D.
* **Latencia:** $\approx 1\text{ ns}$ (1 ciclo de reloj).
* **Estrategia POLYDIM:**
  * Toda la variedad Stiefel $St(D,K)$ y los operadores de Clifford residen $100\%$ en la SRAM de la oblea.
  * Los pasos de descenso geodésico y retracciones Cayley se ejecutan como flujos de datos espaciales núcleo a núcleo (*Spatial Dataflow Fabric*), sin overhead de acceso a memoria DRAM ni cuellos de botella de canal.

#### ⚡ Clase 1: Aceleradores HBM3 / HBM3e (NVIDIA H100/H200/B200, AMD MI300X, Google TPU v4/v5e)
* **Arquitectura de Memoria:** Memoria apilada 3D (*Through-Silicon Vias* - TSV) sobre interposer de silicio.
* **Ancho de Banda:** $3{,}350\text{--}8{,}000\text{ GB/s}$.
* **Latencia:** $\approx 120\text{--}150\text{ ns}$.
* **Estrategia POLYDIM:**
  * Despliegue de kernels Triton / CUDA optimizados con **TMA (Tensor Memory Accelerator)** asíncrono.
  * Copia asíncrona de bloques de Gramian DSYRK directamente a memoria compartida (`smem`) sin tocar los registros de los hilos de cómputo (*Asynchronous Barrier Copy*).

#### 🚀 Clase 2: Aceleradores Dedicados GDDR6 / GDDR6X / GDDR7 (GPUs Cloud & Locales)
* **Arquitectura de Memoria:** Bus paralelo de 256 a 384 bits con modulación PAM4/NRZ.
* **Ancho de Banda:** $1{,}000\text{--}1{,}800\text{ GB/s}$.
* **Latencia:** $\approx 200\text{--}250\text{ ns}$.
* **Estrategia POLYDIM:**
  * Vectorización coalescente de 128 bytes por warp.
  * Retracciones polares, rotaciones Clifford y transformadas ortogonales en GPU; transferencia exclusiva de estados de consenso BFT hacia el Host vía PCIe Gen 4/5.

#### 💻 Clase 3: Servidores Modernos con DDR5 / DDR6 / LPDDR5X (EPYC Genoa/Turin, Xeon Granite Rapids)
* **Arquitectura de Memoria:** 8 a 12 canales NUMA por socket, sub-canales independientes de 32 bits, memorias DDR5-6400 / DDR6.
* **Ancho de Banda:** $100\text{--}300\text{ GB/s}$.
* **Latencia:** $\approx 50\text{--}70\text{ ns}$.
* **Estrategia POLYDIM:**
  * Asignación estricta por nodo NUMA (`libnuma` / `SetThreadGroupAffinity`).
  * Vectorización AVX-512 (F, BW, CD) o AMX con bloques de memoria contiguos, eliminando la contención en enlaces inter-socket (Infinity Fabric / UPI).

#### 🛡️ Clase 4: Banco de Estrés Local Mínimo (DDR3 Dual Channel / AMD Family 15h Piledriver)
* **Arquitectura de Memoria:** Bus DDR3 compartido de 64/128 bits ($12.8\text{ GB/s}$).
* **Latencia:** $\approx 80\text{--}110\text{ ns}$.
* **Estrategia POLYDIM:**
  * Modo de resistencia: Tiling agresivo en caché L1D (16 KB), desenrollado con 4 acumuladores independientes para ocultar latencias y ejecución con 1 solo hilo AVX-256 (o 2 hilos AVX-128) para prevenir la contención de la FPU compartida FlexFP.

---

### 3. Tabla de Resumen Comparativo de Transferencia para $D = 10^6, K = 16$ ($128\text{ MB}$)

| Clase de Silicio | Ancho de Banda Teórico | Tiempo de Transferencia de Tensor ($128\text{ MB}$) | Régimen Operativo |
| :--- | :--- | :--- | :--- |
| **Clase 0 (Cerebras CS-3)** | $21{,}000{,}000\text{ GB/s}$ | **$\approx 0.000006\text{ ms}$ ($6\text{ ns}$)** | Residente en SRAM / Compute-Bound Puro |
| **Clase 1 (H100 HBM3)** | $3{,}350\text{ GB/s}$ | **$\approx 0.038\text{ ms}$ ($38\ \mu\text{s}$)** | Ultra Compute-Bound |
| **Clase 2 (RTX 5090 GDDR7)** | $1{,}792\text{ GB/s}$ | **$\approx 0.071\text{ ms}$ ($71\ \mu\text{s}$)** | Compute-Bound |
| **Clase 3 (DDR5-6400 8-ch)** | $204.8\text{ GB/s}$ | **$\approx 0.625\text{ ms}$** | Equilibrado / Cache-Friendly |
| **Clase 4 (A4-6300 DDR3)** | $12.8\text{ GB/s}$ | **$\approx 10.000\text{ ms}$** | $100\%$ Memory-Bound (Stress Floor) |

---
*Documento integrado en la base teórica de POLYDIM Serie 800.*
