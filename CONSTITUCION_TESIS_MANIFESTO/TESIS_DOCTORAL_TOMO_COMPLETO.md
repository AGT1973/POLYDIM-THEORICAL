# OPTIMIZACIÓN RIEMANNIANA EN VARIEDADES DE STIEFEL, TRANSPORTE INTER-PROCESO EN MEMORIA COMPARTIDA Y COMPILACIÓN VARIACIONAL EN PROCESADORES CUÁNTICOS SUPERCONDUCTORES

**Tesis Doctoral presentada para optar al grado académico de Doctor en Ciencias de la Computación y Matemática Aplicada**

**Autor:** Ariel García Traba  
**Afiliación:** Investigador Principal, Proyecto POLYDIM-EINSOF — Grupo de Geometría Computacional y Sistemas de Silicio  
**Lugar y Fecha:** Buenos Aires, República Argentina — Noviembre de 2026  
**Jurado Evaluador Institucional:** *[Espacio reservado para la designación oficial del Tribunal Académico por parte de la Comisión de Doctorado / Secretaría de Posgrado]*  
**Auditoría Técnica Pre-Defensa:** Sometida a escrutinio adversarial independiente de código, matemática y física cuántica (véase Capítulo 7 y Apéndice A).

---

## DECLARACIÓN FORMAL DE MODALIDAD INSTITUCIONAL Y AUTONOMÍA DOCUMENTAL

La presente disertación doctoral se presenta bajo la **Modalidad Monográfica Tradicional Autónoma (Tomo Completo de Investigación)**, en estricto cumplimiento de los reglamentos vigentes de estudios de posgrado del sistema universitario argentino (UBA, UNLP, UNC, UTN y lineamientos CONICET):

1. **Autonomía Científica Integral:** Este volumen constituye una obra monográfica íntegra, autocontenida y verificable de manera independiente. Incluye la formulación axiomática de las hipótesis, las demostraciones algebraicas y numéricas completas paso a paso, la especificación binaria a nivel de registro del protocolo de memoria compartida (`PmtpShmBus` v2.1) y del compilador nativo (`Mathesis MTHC` v1.4), así como las trazas empíricas de ejecución en silicio clásico y cuántico con código de retorno verificado (`Exit Code 0`).
2. **Admisibilidad Administrativa Autónoma:** Al estructurarse como monografía doctoral completa y no como compendio condicionado de artículos externos, la admisibilidad formal del expediente ante Mesa de Entradas no depende de plazos editoriales de terceros ni de asignaciones previas de identificadores DOI externos.
3. **Difusión Científica Complementaria:** De manera complementaria y sujeta a autorización expresa del autor, la síntesis experimental cuántica ha sido preparada como manuscrito técnico para *IEEE Transactions on Quantum Engineering* y paquete de preservación abierta para **Zenodo / CERN**.

---

## DEDICATORIA

*Al rigor analítico y a la honestidad empírica sin concesiones: que ningún resultado reclamado carezca jamás de demostración matemática y verificación física en silicio.*  
*A la docencia y a la educación pública argentina, desde cuyas aulas y esfuerzo cotidiano se sostiene la investigación científica soberana.*  
*A mi familia, sostén silencioso e incondicional en cada etapa de este trabajo.*

---

## AGRADECIMIENTOS

Expreso mi profundo reconocimiento:
- Al programa de acceso científico de **IBM Quantum**, cuya infraestructura superconductora de 156 qubits de arquitectura **Heron** (`ibm_fez`, `ibm_kingston` e `ibm_marrakesh`) permitió ejecutar y auditar físicamente las 17 cargas de trabajo cuánticas reportadas en esta tesis (con 3 cargas geométricas adicionales en cola de ejecución).
- A las comunidades científicas abiertas multipolares de matemática numérica, geometría diferencial, sistemas operativos y computación cuántica en Iberoamérica, Europa, Asia-Pacífico y Oceanía, cuyos desarrollos teóricos y herramientas abiertas cimentaron este marco de trabajo.
- Al protocolo interno de auditoría adversarial pre-defensa documentado en el Capítulo 7, cuya revisión hostil permitió detectar, corregir y certificar en silicio 28 hallazgos técnicos (`REM-01` a `REM-28`) antes de la presentación definitiva de este tomo.

---

## RESUMEN EJECUTIVO (CASTELLANO)

En la convergencia actual entre la inferencia colaborativa de modelos de lenguaje de gran escala (LLMs) y la computación cuántica de escala intermedia ruidosa (NISQ), los sistemas híbridos padecen una patología estructural común: **la destrucción de invariantes geométricos continuos al forzar el paso de estados de alta dimensión por canales serializados unidimensionales o grafos físicos de baja conectividad**.

En los sistemas multi-agente clásicos sobre CPU, el intercambio inter-proceso (IPC) de representaciones internas suele degradarse a texto JSON/UTF-8 sobre sockets TCP, incurriendo en latencias de milisegundos, múltiples copias en memoria dinámica y pérdida de la geometría angular de las activaciones latentes ($h \in \mathbb{R}^{d_{\text{model}}}$). De modo análogo, en los procesadores cuánticos superconductores con topología planar **Heavy-Hexagonal** de grado máximo 3, la compilación de grafos de interacción no planares o de grado superior exige redes de permutación `SWAP` que multiplican el número de compuertas entrelazantes de dos qubits, precipitando la pérdida de coherencia por despolarización, relajación térmica longitudinal ($T_1$) y asimetría en la lectura dispersiva de cavidad.

Esta tesis doctoral formula, demuestra analíticamente y valida en silicio un **marco geométrico continuo unificado sobre la variedad de Stiefel** $V_k(\mathbb{R}^D) = \{ X \in \mathbb{R}^{D \times k} : X^T X = I_k \}$:

1. **Transporte Inter-Proceso `PmtpShmBus` v2.1 con Separación Formal de Regímenes (Zero-Copy Inmutable vs. Snapshot Seqlock):** Se diseña e implementa un protocolo de memoria compartida alineado a líneas de caché de 64 bytes sobre primitivas nativas del kernel (`CreateFileMappingW` en Windows y `/dev/shm` con `mmap(MAP_SHARED)` en POSIX), libre de cursores mutables compartidos y protegido contra lecturas desgarradas (*torn reads*) y condiciones de carrera TOCTOU mediante cerradura de secuencia (**Seqlock**) con barreras explícitas de memoria y autenticación **BLAKE2s-64**. En dimensión $D=4096$ (32 KB, FP64), se caracterizan rigurosamente sus tres regímenes operativos sobre hardware local (`AMD A4-6300` Piledriver): (a) **Vista Caliente Zero-Copy (`IMMUTABLE_EPOCH`)** en **$6.20\,\mu\text{s}$** ($p_{50}$; media $6.41\,\mu\text{s}$), logrando una aceleración de **$1\,193\times$** frente a JSON ($7\,648.80\,\mu\text{s}$), **$14.3\times$** frente a sockets TCP loopback ($91.92\,\mu\text{s}$) y **$12.0\times$** frente a C-Pickle v5 ($76.61\,\mu\text{s}$), con deriva numérica idénticamente nula ($0.00 \times 10^0$) y memoria física $\mathcal{O}(1)$; (b) **Snapshot Concurrente Seqlock + BLAKE2s-64** en **$141.20\,\mu\text{s}$** ($p_{50}$), verificando **0 lecturas desgarradas** en carreras de 4 escritores $\times$ 4 lectores concurrentes (2\,874 lecturas auditadas); y (c) **Adjunto en Frío del Sistema Operativo** en **$190.80\,\mu\text{s}$** ($p_{50}$).En difusión concurrente a $M=16$ trabajadores, el bus supera a C-Pickle por **$12.49\times$** ($29.6\,\mu\text{s}$ vs. $369.6\,\mu\text{s}$), e inyecta activaciones latentes en la Capa 12 de `Qwen 2.5` ($d=896$) en **$198.1\,\mu\text{s}$**.
2. **Compilador Nativo Soberano `Mathesis MTHC` v1.4:** Se construye un compilador directo de especificaciones geométricas `.mth` a código máquina nativo `x86_64`/SSE2 (ejecutables autónomos Windows PE32+ y Linux ELF64, más objetos COFF/ELF, sin depender de C, C++, GCC ni LLVM). La versión v1.4 implementa ortonormalización matricial de Gram-Schmidt Modificado de Doble Pasada (**MGS2**) sobre $V_k(\mathbb{R}^D)$ para rango arbitrario $k \ge 1$ ($V_1(\mathbb{R}^{2048})$, $V_4(\mathbb{R}^{512})$, $V_8(\mathbb{R}^{256})$) e incorpora una **compuerta de verificación ortonormal en hardware** (`ucomisd` + trampas `jp`/`ja` hacia `Exit Code 1` si $\|X^T X - I_k\|_F > 10^{-13}$ o emerge `NaN`).
3. **Estabilidad Numérica y Retracción Polar Cuártica Exacta:** Se demuestra la cota de error de primer orden $2\epsilon_{\text{mach}}\sum |x_i|$ para la sumación compensada de Neumaier (distinguiendo con precisión la condición de ramificación de Dekker `Fast2Sum` frente a `TwoSum` de Knuth), y se prueba algebraicamente que la iteración polar de Newton-Schulz de cuarto orden con pre-acondicionamiento libre de SVD $X_0 = A / \|A\|_F$ satisface la identidad polinómica exacta de cuatro términos $E_{m+1} = \frac{35}{64}E_m^4 + \frac{7}{32}E_m^5 + \frac{35}{256}E_m^6 + \frac{25}{256}E_m^7$, convergiendo en norma de Frobenius hasta $1.83 \times 10^{-15}$. Asimismo, se dota al operador de inyección co-isométrica $W W^T = I_d$ de descomposición QR completa para el manejo determinista del núcleo $\ker(W)$ y de una variante suave regularizada de Tikhonov con constante de Lipschitz acotada sobre dominios compactos.
4. **Incrustaciones Cuánticas `Stiefel-VQE`, Bucle Híbrido Cerrado y Deconstrucción Física del Ruido en 156 Qubits:** Se evalúan **17 cargas físicas completadas** ($n \in [4, 66]$ qubits, 4\,000 disparos por circuito, mitigación TREX) en los procesadores IBM Heron `ibm_fez`, `ibm_kingston` e `ibm_marrakesh`, junto con un bucle cerrado clásico-cuántico ejecutado en **$69.89\,\text{ms}$**. Mediante una metodología de **Doble Línea Base** que separa el autovalor fundamental exacto $E_{\text{ground}}$ de la esperanza clásica sin ruido $\langle E_{\text{ideal}}(\Theta) \rangle$, se demuestra que: (i) la atenuación del $63.58\%$ en el Icosaedro ($12\text{Q}$, 75 compuertas CZ físicas) queda acotada dentro del intervalo teórico $[0.1692, 0.7916]$ con infidelidad efectiva $\bar{\epsilon}_{\text{eff}} \approx 1.29\%$ por compuerta; (ii) en el Dodecaedro ($20\text{Q}$, 30 aristas, corrimiento medido $\Delta E_{\text{hw}} = +5.1097$), el **sesgo asimétrico de lectura dispersiva** ($\epsilon_{1\to 0} \approx 3.80\%$ vs. $\epsilon_{0\to 1} \approx 0.80\%$) aporta **$+3.1800$ ($62.23\%$)** y la **relajación térmica longitudinal $T_1$** aporta **$+0.8138$ ($15.93\%$)**, explicando conjuntamente **$+3.9938$ ($78.16\%$)** del desplazamiento sistemático (correspondiendo el $21.84\%$ restante a diafonía residual `ZZ` y heterogeneidad local de acopladores); y (iii) `Stiefel-VQE` requiere $|E|$ compuertas entrelazantes nativas por capa frente a $2p|E|$ en QAOA estándar, preservando una supervivencia analítica pre-enrutamiento de $74.0\%$ en grafos de 30 aristas frente al $16.4\%$ de QAOA ($p=3$), a cambio de una menor expresividad discreta sin ruido que se cuantifica con total transparencia mediante fronteras de Pareto.

---

## ABSTRACT (ENGLISH)

Contemporary collaborative artificial intelligence and Noisy Intermediate-Scale Quantum (NISQ) computing share a structural bottleneck: **the loss of continuous geometric invariants when high-dimensional states are forced through one-dimensional serialized channels or sparse planar hardware topologies**.

In multi-agent large language model (LLM) pipelines hosted on CPUs, inter-process communication (IPC) routinely serializes continuous hidden activations ($h \in \mathbb{R}^{d_{\text{model}}}$) into 1D UTF-8/JSON text over loopback sockets, incurring millisecond latencies, repeated heap allocations, and geometric distortion. Analogously, on superconducting quantum processors constrained to degree-3 planar **Heavy-Hexagonal** lattices, transpiling non-planar or higher-degree interaction graphs requires `SWAP` permutation chains that inflate two-qubit gate depth, accelerating signal loss through gate depolarization, longitudinal thermal relaxation ($T_1$), and asymmetric dispersive readout errors.

This doctoral dissertation formulates, proves, and silicon-verifies a **unified continuous geometric framework on the Stiefel manifold** $V_k(\mathbb{R}^D) = \{ X \in \mathbb{R}^{D \times k} : X^T X = I_k \}$:

1. **`PmtpShmBus` v2.1 Shared-Memory Transport with Explicit Regime Separation:** We design a 64-byte cache-line-aligned shared-memory protocol over OS page-mapping primitives (Windows `CreateFileMappingW` and POSIX `/dev/shm` `mmap`), eliminating shared file-cursor state and preventing both torn reads and digest TOCTOU races via an atomic **Seqlock** paired with memory fences and **BLAKE2s-64** authentication. At $D=4096$ (32 KB FP64 on local `AMD A4-6300` Piledriver silicon), we benchmark three distinct regimes side-by-side: (a) **Hot Immutable Zero-Copy View (`IMMUTABLE_EPOCH`)** at **$6.20\,\mu\text{s}$** ($p_{50}$; mean $6.41\,\mu\text{s}$), achieving a **$1,193\times$** speedup over JSON ($7,648.80\,\mu\text{s}$), **$14.3\times$** over TCP loopback ($91.92\,\mu\text{s}$), and **$12.0\times$** over C-Pickle v5 ($76.61\,\mu\text{s}$) with bit-exact $0.00 \times 10^0$ drift and $\mathcal{O}(1)$ physical RAM; (b) **Warm Concurrent Seqlock Snapshot + BLAKE2s-64** at **$141.20\,\mu\text{s}$** ($p_{50}$), sustaining **0 torn reads** across 4 concurrent writers $\times$ 4 concurrent readers (2,874 verified reads); and (c) **Cold OS Attach** at **$190.80\,\mu\text{s}$** ($p_{50}$). Under 16-worker fan-out, `PmtpShmBus` outperforms C-Pickle by **$12.49\times$** ($29.6\,\mu\text{s}$ vs. $369.6\,\mu\text{s}$) and injects latent vectors into Layer 12 of `Qwen 2.5` ($d=896$) in **$198.1\,\mu\text{s}$**.
2. **Sovereign Native Compiler `Mathesis MTHC` v1.4:** We build a zero-dependency compiler translating geometric `.mth` specifications directly into standalone `x86_64`/SSE2 Windows PE32+ (`.exe`), Linux ELF64 (`.elf`), and relocatable COFF/ELF object binaries. Version v1.4 implements two-pass Modified Gram-Schmidt (**MGS2**) over matrix Stiefel manifolds $V_k(\mathbb{R}^D)$ for $k \ge 1$ ($V_1(\mathbb{R}^{2048})$, $V_4(\mathbb{R}^{512})$, $V_8(\mathbb{R}^{256})$) and embeds an in-silicon SSE2 orthonormality gate (`ucomisd` + `jp`/`ja` traps exiting with code `1` whenever $\|X^T X - I_k\|_F > 10^{-13}$ or `NaN` arises).
3. **Exact Quartic Polar Retraction & Compensated Numerical Bounds:** We prove the $2\epsilon_{\text{mach}}\sum |x_i|$ bound for Neumaier summation (via Dekker's ordered `Fast2Sum` error extraction), establish the exact four-term residual identity $E_{m+1} = \frac{35}{64}E_m^4 + \frac{7}{32}E_m^5 + \frac{35}{256}E_m^6 + \frac{25}{256}E_m^7$ for fourth-order Newton-Schulz polar retraction under SVD-free Frobenius scaling $X_0 = A / \|A\|_F$, and formalize both canonical $\ker(W)$-complete and Tikhonov-smooth co-isometric latent injection operators on compact Transformer activation domains.
4. **Variational Quantum Embeddings (`Stiefel-VQE`) & Noise Deconstruction Across 17 IBM Heron Workloads:** Across 17 physical workloads ($n \in [4, 66]$ qubits, 4,000 shots, TREX mitigation) on 156-qubit IBM Heron QPUs (`ibm_fez`, `ibm_kingston`, `ibm_marrakesh`) plus a $69.89\,\text{ms}$ closed-loop classical-quantum pipeline, our Dual-Baseline methodology separates algorithmic expressivity ($\Delta_{\text{ansatz}}$) from hardware noise ($\Delta_{\text{hw}}$). On the 20-qubit Dodecahedron ($\Delta E_{\text{hw}} = +5.1097$), asymmetric dispersive readout ($\epsilon_{1\to 0} \approx 3.80\%$ vs. $\epsilon_{0\to 1} \approx 0.80\%$) accounts for **$+3.1800$ ($62.23\%$)** and longitudinal $T_1$ relaxation accounts for **$+0.8138$ ($15.93\%$)**, jointly explaining **$+3.9938$ ($78.16\%$)** of the observed shift, while `Stiefel-VQE` halves two-qubit entangling gate counts per layer relative to standard CNOT-decomposed QAOA ($|E|$ vs. $2p|E|$).

---

## ÍNDICE GENERAL DETALLADO

- **PÁGINAS PRELIMINARES**
  - Declaración Formal de Modalidad Institucional y Autonomía Documental
  - Dedicatoria
  - Agradecimientos
  - Resumen Ejecutivo (Castellano)
  - Abstract (English)
  - Glosario de Notación y Símbolos Matemáticos
- **CAPÍTULO 1: INTRODUCCIÓN, HIPÓTESIS Y ALCANCE DE LA INVESTIGACIÓN**
  - 1.1 El Cuello de Botella de Discretización 1D y Enrutamiento Planar en Sistemas Híbridos
  - 1.2 Hipótesis Central de Investigación
  - 1.3 Preguntas de Investigación Doctorales (RQ-1 a RQ-5)
  - 1.4 Objetivos Generales y Específicos
  - 1.5 Metodología Experimental de Verificación en Silicio y Doble Línea Base
  - 1.6 Alcance Operativo, Exclusiones Explícitas y Estructura de la Tesis
- **CAPÍTULO 2: ESTADO DEL ARTE Y TAXONOMÍA TEÓRICA EXHAUSTIVA**
  - 2.1 Geometría Diferencial y Optimización Riemanniana en Variedades Matriciales
  - 2.2 La Variedad de Stiefel $V_k(\mathbb{R}^D)$: Retracciones Polares, MGS2 y Estabilidad Numérica
  - 2.3 Taxonomía de Sistemas IPC de Memoria Compartida para Inferencia Distribuida
  - 2.4 Procesadores Cuánticos Superconductores NISQ y Topología Heavy-Hexagonal Heron
  - 2.5 Razonamiento en Espacios Latentes Continuos frente a Tokenización Discreta
- **CAPÍTULO 3: TEORÍA MATEMÁTICA Y TEOREMAS FORMALES DEMOSTRADOS**
  - 3.1 Lema 1 y Teorema 1: Cota de Redondeo en Sumación Compensada de Neumaier (`Fast2Sum`)
  - 3.2 Lema 2: Pre-Acondicionamiento de Frobenius Libre de SVD y Dominio de Contracción
  - 3.3 Teorema 2: Identidad Polinómica Exacta y Convergencia Cuártica de Newton-Schulz
  - 3.4 Teorema 3: Inyección Co-Isométrica Completa en $\ker(W)$, Variante Suave de Tikhonov y Cota de Lipschitz Compacta
  - 3.5 Teorema 4: Identidad Bit a Bit en Régimen Inmutable y Libertad de Lecturas Desgarradas en Régimen Seqlock
  - 3.6 Teorema 5: Factorización Simpléctica Remediada en $\mathrm{SO}(2)$ e Invarianza en Hiperboloide de Minkowski
- **CAPÍTULO 4: ARQUITECTURA DE SILICIO DE `PmtpShmBus` v2.1, `Mathesis MTHC` v1.4 Y PROTOTIPO EINSOFOS**
  - 4.1 Especificación Binaria Exacta del Descriptor ABI v2.1 (64 Bytes Cache-Aligned)
  - 4.2 Mecanismos de Mapeo de Páginas Físicas en Windows (`CreateFileMappingW`) y POSIX (`/dev/shm`)
  - 4.3 Autenticación de Integridad BLAKE2s-64 Libre de Ventana TOCTOU
  - 4.4 Protocolo de Concurrencia Seqlock Multi-Escritor / Multi-Lector con Backoff Escalonado
  - 4.5 Prototipo Experimental de Kernel Bare-Metal EinsofOS (UEFI, ACPI MADT, MMIO) y Frontera de Alcance
  - 4.6 Arquitectura de Dos Niveles Intra-Nodo / Inter-Nodo: Realidad LAN TCP vs. Especificación RoCEv2/RDMA
  - 4.7 Compilador Vectorial Nativo `Mathesis MTHC` v1.4: Emisión Directa PE32+/ELF64 sobre $V_k(\mathbb{R}^D)$ y Gate Hardware SSE2
- **CAPÍTULO 5: EVALUACIÓN EXPERIMENTAL EN SILICIO CLÁSICO (IPC E INFERENCIA LLM)**
  - 5.1 Configuración de Hardware Host (`AMD A4-6300` Piledriver) y Protocolo Estadístico
  - 5.2 Escalabilidad Dimensional ($D \in [512, 4096]$) y Comparación frente a Serialización 1D
  - 5.3 Tabla Unificada de los Tres Regímenes PMTP frente a C-Pickle, TCP Loopback y JSON en $D=4096$
  - 5.4 Evaluación de Difusión Concurrente Multi-Lector ($1 \to M$, $M \in [1, 16]$)
  - 5.5 Comparación Cuantitativa frente a Sockets Loopback y Demonios de Memoria Compartida (Plasma/Ray)
  - 5.6 Inyección Latente Inter-Modelo en la Capa 12 de `Qwen 2.5` ($d=896$)
  - 5.7 Bucle Cerrado Híbrido Clásico-Cuántico en Tiempo Real (`hybrid_stiefel_classical_quantum_loop.py`)
- **CAPÍTULO 6: INCRUSTACIONES CUÁNTICAS VARIACIONALES Y DECONSTRUCCIÓN DE RUIDO EN 156 QUBITS**
  - 6.1 Relajación Continua en Variedades de Stiefel hacia Hamiltonianos de Espín de Ising
  - 6.2 Congestión de Corte, Paridad de Ciclos y Expansión de Compuertas `SWAP` en Mallas Heavy-Hex
  - 6.3 Metodología de Doble Línea Base: Separación Ortogonal entre $\Delta_{\text{ansatz}}$ y $\Delta_{\text{hw}}$
  - 6.4 Resultados Experimentales Físicos en 17 Cargas de Trabajo sobre Procesadores IBM Heron
  - 6.5 Deconstrucción Analítica del Corrimiento Energético: Lectura Dispersiva Asimétrica ($62.23\%$) y Relajación $T_1$ ($15.93\%$)
  - 6.6 Análisis de Frontera de Pareto: `Stiefel-VQE` vs. `QAOA` ($p=1, 2, 3$) — Supervivencia Analítica vs. Retención Medida
  - 6.7 Modelo Compuesto de Incertidumbre Estadística y Deriva Temporal de Calibración
- **CAPÍTULO 7: AUDITORÍA ADVERSARIAL PRE-DEFENSA, TRAZABILIDAD DE REMEDIACIONES Y AMENAZAS A LA VALIDEZ**
  - 7.1 Metodología de Auditoría Simétrica Pre-Defensa (Red Team / Blue Team)
  - 7.2 Registro Completo de Vulnerabilidades Críticas y No Críticas Detectadas (`REM-01` a `REM-28`)
  - 7.3 Verificación Empírica en Silicio de las Remediaciones (`Exit Code 0` y Pruebas Negativas de Rechazo)
  - 7.4 Certificación de Componentes Resilientes (Blue Team)
  - 7.5 Amenazas a la Validez Interna, Externa y de Construcción
- **CAPÍTULO 8: CONCLUSIONES, IMPACTO CIENTÍFICO Y LÍNEAS FUTURAS DE INVESTIGACIÓN**
  - 8.1 Síntesis de Contribuciones Doctorales Verificadas
  - 8.2 Implicaciones Arquitectónicas para Inferencia Multi-Agente y Compilación NISQ
  - 8.3 Trabajo Futuro y Problemas Abiertos
- **BIBLIOGRAFÍA**
- **APÉNDICES DE VERIFICACIÓN Y REPRODUCIBILIDAD EN SILICIO**
  - Apéndice A: Inventario de Kernels, Binarios Nativos y Suites Adversariales (`Exit Code 0`)
  - Apéndice B: Registro Oficial de Identificadores de Trabajo en IBM Quantum (17 Completados + 3 en Cola)
  - Apéndice C: Parámetros Físicos de Calibración de los Procesadores IBM Heron Evaluados

---

## GLOSARIO DE NOTACIÓN Y SÍMBOLOS MATEMÁTICOS

| Símbolo | Definición Matemática y Física |
|---|---|
| $V_k(\mathbb{R}^D)$ | Variedad compacta de Stiefel de $k$-marcos ortonormales en $\mathbb{R}^D$: $\{ X \in \mathbb{R}^{D \times k} : X^T X = I_k \}$, con $1 \le k \le D$. |
| $S^{D-1}$ | Hiperesfera unitaria euclídea en $\mathbb{R}^D$, caso particular $k=1$ de $V_1(\mathbb{R}^D)$. |
| $\mathcal{P}_{V_k}(A)$ | Factor polar ortogonal $A(A^T A)^{-1/2}$, proyección métrica única de $A$ sobre $V_k(\mathbb{R}^D)$ en norma de Frobenius. |
| $E_m$ | Matriz simétrica de defecto de ortonormalidad en la iteración $m$: $E_m = I_k - X_m^T X_m$. |
| $\|\cdot\|_F,\; \|\cdot\|_2$ | Norma matricial de Frobenius ($\sqrt{\operatorname{Tr}(A^T A)}$) y norma espectral ($\sigma_{\max}(A)$), respectivamente. |
| $\epsilon_{\text{mach}}$ | Unidad de redondeo en doble precisión IEEE-754 binary64: $\epsilon_{\text{mach}} = 2^{-53} \approx 1.1102 \times 10^{-16}$. |
| $\ker(W)$ | Subespacio nulo $\{ s \in \mathbb{R}^r : W s = 0 \}$ del operador co-isométrico $W \in \mathbb{R}^{d \times r}$ ($W W^T = I_d$). |
| $\mathcal{G}_{\text{phys}}$ | Grafo planar bipartito Heavy-Hexagonal del procesador superconductor físico ($\deg_{\max} = 3$). |
| $\rho$ | Razón de expansión de profundidad tras compilación física: $\rho = D_{\text{ISA}} / D_{\text{Log}}$. |
| $E_{\text{ground}}$ | Autovalor mínimo exacto del Hamiltoniano de Ising: $\min_{\|\psi\|=1} \langle \psi | H | \psi \rangle$. |
| $\langle E_{\text{ideal}}(\Theta) \rangle$ | Esperanza exacta sin ruido del circuito variacional compilado evaluada por simulación de vector de estado. |
| $\langle E_{\text{QPU}} \rangle$ | Esperanza experimental medida en el procesador cuántico físico sobre $N_{\text{shots}} = 4000$ disparos con TREX. |
| $\Delta_{\text{ansatz}},\; \Delta_{\text{hw}}$ | Brecha de expresividad ($\langle E_{\text{ideal}} \rangle - E_{\text{ground}}$) y corrimiento físico de hardware ($\langle E_{\text{QPU}} \rangle - \langle E_{\text{ideal}} \rangle$). |
| $\mathcal{F}_{\text{surv}}$ | Modelo analítico de supervivencia de compuertas pre-enrutamiento: $(1 - \epsilon_{2Q})^{N_{2Q,\text{log}}}$. |
| $\mathcal{R}_{\text{meas}}$ | Razón empírica de retención de señal medida en QPU tras expansión `SWAP`: $\langle E_{\text{QPU}} \rangle / \langle E_{\text{ideal}} \rangle$. |
| $\alpha \in [0, 1]$ | Razón de aproximación energética normalizada para minimización: $(E_{\max} - \langle E \rangle) / (E_{\max} - E_{\min})$. |
| `PmtpShmBus` | Protocolo de transporte tensorial en memoria compartida con cabecera binaria ABI v2.1 de 64 bytes. |
| `Mathesis MTHC` | Compilador nativo soberano `.mth` $\to$ `x86_64`/SSE2 (PE32+ / ELF64 / COFF) con verificación de variedad en silicio. |

---

# CAPÍTULO 1: INTRODUCCIÓN, HIPÓTESIS Y ALCANCE DE LA INVESTIGACIÓN

### 1.1 El Cuello de Botella de Discretización 1D y Enrutamiento Planar en Sistemas Híbridos
En los sistemas modernos de aprendizaje profundo, el cómputo interno de los modelos Transformer transcurre íntegramente sobre espacios vectoriales continuos de alta dimensión ($h \in \mathbb{R}^{d_{\text{model}}}$, donde $d_{\text{model}} \in [896, 8192]$). Sin embargo, cuando múltiples procesos cooperan en esquemas de verificación cruzada, enjambres de razonamiento o acoplamiento con coprocesadores físicos, la arquitectura convencional proyecta dichas representaciones sobre secuencias discretas unidimensionales de tokens serializados en texto UTF-8/JSON a través de sockets de red. Esta reducción dimensional impone dos penalizaciones severas:
1. **Pérdida de Estructura Geométrica Continua:** El colapso mediante `argmax` o muestreo estocástico sobre un vocabulario finito ($|\mathcal{V}| \approx 32\,000 - 150\,000$) destruye distancias geodésicas, ángulos relativos en subespacios ortogonales y simetrías continuas del grupo especial ortogonal $\mathrm{SO}(D)$.
2. **Dominancia de Latencia de Serialización y Copia:** La codificación decimal IEEE-754 a texto ASCII, la reserva repetida de buffers en memoria dinámica (*heap*) y las transiciones de anillo de privilegio en sockets TCP consumen varios milisegundos por intercambio ($7.65\,\text{ms}$ medidos para un solo vector de $D=4096$), superando en tres órdenes de magnitud el tiempo de acceso a páginas físicas compartidas en memoria RAM.

De manera estructuralmente dual, en la computación cuántica superconductora de era NISQ [4], la ejecución de problemas geométricos y combinatorios requiere proyectar grafos de interacción densos o no planares sobre procesadores físicos con conectividad planar restringida. En la familia de procesadores superconductores **IBM Heron** de 156 qubits [13, 34], el grafo físico de acoplamiento $\mathcal{G}_{\text{phys}}$ obedece una red **Heavy-Hexagonal** bipartita cuyo grado máximo por vértice es $\deg_{\max}(v) = 3$. Toda interacción lógica entre qubits no adyacentes obliga al compilador topológico (como SABRE [14]) a sintetizar cadenas de permutación `SWAP`, donde cada `SWAP` se descompone en tres compuertas nativas de dos qubits (`CZ`). Esta expansión empuja el circuito hacia el régimen dominado por despolarización acumulada, relajación longitudinal $T_1$ y sesgo asimétrico de medición dispersiva [21].

### 1.2 Hipótesis Central de Investigación
> *"Un marco geométrico continuo unificado sobre la variedad compacta de Stiefel $V_k(\mathbb{R}^D)$ acoplado a aritmética compensada de Neumaier proporciona una doble ventaja verificable en silicio: (1) en procesadores clásicos multi-proceso, habilita el transporte inter-proceso en memoria compartida (`PmtpShmBus` v2.1) y la compilación vectorial directa a código máquina (`Mathesis MTHC` v1.4) preservando invariantes ortonormales ($\|X^T X - I_k\|_F \le 10^{-13}$) con latencias de microsegundos libres de lecturas desgarradas; y (2) en procesadores cuánticos superconductores de topología Heavy-Hexagonal, genera circuitos variacionales compactos (`Stiefel-VQE`) con $|E|$ compuertas entrelazantes nativas por capa cuya degradación experimental queda cuantitativamente gobernada por la congestión de corte bipartita, el sesgo asimétrico de lectura dispersiva y la relajación térmica $T_1$."*

### 1.3 Preguntas de Investigación Doctorales (RQ-1 a RQ-5)
- **RQ-1 (Transporte y Concurrencia):** ¿Cómo transferir tensores continuos $X \in V_k(\mathbb{R}^D)$ entre procesos concurrentes diferenciando rigurosamente entre vistas inmutables de cero copias ($\mathcal{O}(1)$) y snapshots atómicos libres de bloqueo (**Seqlock**) inmunes a condiciones de carrera TOCTOU?
- **RQ-2 (Compilación Nativa de Variedades):** ¿Es factible compilar operadores de retracción sobre $V_k(\mathbb{R}^D)$ ($k \ge 1$) directamente a código máquina `x86_64`/SSE2 autónomo (PE32+ y ELF64) incorporando verificación ortonormal en hardware como condición necesaria para el código de salida exitoso?
- **RQ-3 (Estabilidad de Inyección Latente):** ¿Qué cotas analíticas gobiernan la perturbación inducida en capas de atención Transformer al inyectar estados latentes externos proyectados mediante co-isometrías $W W^T = I_d$, incluso en la vecindad del subespacio nulo $\ker(W)$?
- **RQ-4 (Topología Cuántica Heavy-Hex):** ¿Cómo determinan el exceso de grado ($d_{\text{avg}} > 3$), la no planaridad y la incompatibilidad de ciclos impares sobre grafos bipartitos la inserción de compuertas `SWAP` y la atenuación física de señal en procesadores de 156 qubits?
- **RQ-5 (Deconstrucción Física de Ruido):** ¿Cómo separar formalmente el error de expresividad variacional ($\Delta_{\text{ansatz}}$) del ruido físico del chip ($\Delta_{\text{hw}}$), cuantificando la contribución exacta de la lectura dispersiva frente al decaimiento térmico $T_1$?

### 1.4 Objetivos Generales y Específicos
- **Objetivo General:** Desarrollar, demostrar matemáticamente y validar en hardware real clásico y cuántico una arquitectura extremo a extremo de representación, transporte y optimización sobre variedades de Stiefel.
- **Objetivos Específicos:**
  1. Demostrar cotas no asintóticas exactas para la sumación compensada de Neumaier y la retracción polar de Newton-Schulz de cuarto orden con escalado de Frobenius libre de SVD.
  2. Especificar y verificar bajo estrés multi-hilo el protocolo binario `PmtpShmBus` v2.1 (cabecera de 64 bytes, Seqlock sin cursores compartidos y BLAKE2s-64).
  3. Construir y auditar a nivel de bytes el compilador nativo `Mathesis MTHC` v1.4 con soporte matricial $V_k(\mathbb{R}^D)$ ($k \ge 1$) mediante Gram-Schmidt Modificado de Doble Pasada (MGS2) y aserción ortonormal SSE2.
  4. Ejecutar y caracterizar físicamente 17 cargas de trabajo cuánticas ($4 \le n \le 66$ qubits) sobre procesadores superconductores IBM Heron (`ibm_fez`, `ibm_kingston`, `ibm_marrakesh`), contrastando `Stiefel-VQE` frente a `QAOA` ($p \in \{1, 2, 3\}$) y cerrando un bucle híbrido clásico-cuántico en tiempo real.

### 1.5 Metodología Experimental de Verificación en Silicio y Doble Línea Base
Toda afirmación teórica o arquitectónica contenida en esta tesis se sujeta a tres reglas metodológicas estrictas:
1. **Verificación Ejecutable con Pruebas Positivas y Negativas:** Cada módulo matemático y de sistemas cuenta con una suite autónoma reproducible cuya ejecución debe concluir con `Exit Code 0` ante entradas válidas y rechazar determinísticamente entradas corruptas, no ortonormales o no finitas (`NaN`/`Inf`).
2. **Doble Línea Base Cuántica:** Ninguna medición física $\langle E_{\text{QPU}} \rangle$ se compara directamente contra $E_{\text{ground}}$ sin intercalar la esperanza clásica exacta del circuito variacional sin ruido $\langle E_{\text{ideal}}(\Theta) \rangle$, impidiendo confundir limitaciones de expresividad algorítmica con decoherencia del hardware.
3. **Auditoría Simétrica Pre-Defensa:** Los errores históricos de versiones preliminares (V1–V3) no se ocultan; se documentan explícitamente en el Capítulo 7 junto con las pruebas empíricas de su corrección en esta versión definitiva V4.

### 1.6 Alcance Operativo, Exclusiones Explícitas y Estructura de la Tesis
- **Núcleo Evaluado:** Transporte `PmtpShmBus` v2.1 en nodos locales Windows y POSIX, compilador `Mathesis MTHC` v1.4 `x86_64`/SSE2, inyección latente en modelos abiertos (`Qwen 2.5`), bucle híbrido clásico-cuántico y 17 cargas cuánticas en procesadores superconductores IBM Heron de 156 qubits.
- **Exclusiones Explícitas:** No se reclama ventaja o supremacía cuántica computacional frente a algoritmos clásicos exactos (para $n \le 25$ la simulación Statevector es exacta en milisegundos, y en $n = 66$ el estado medido constituye una caracterización física de frontera NISQ sin corrección de errores tolerante a fallos). Asimismo, la arquitectura bare-metal **EinsofOS** (§4.5) y la extensión inter-nodo **RoCEv2/RDMA** (§4.6) se delimitan rigurosamente como prototipo experimental de Ring 0 y especificación arquitectónica de Nivel 2, respectivamente, separándolas de las mediciones empíricas sobre el host local.
- **Organización:** El Capítulo 2 revisa el estado del arte; el Capítulo 3 desarrolla los cinco teoremas fundamentales; el Capítulo 4 detalla la arquitectura binaria de `PmtpShmBus` v2.1 y `Mathesis MTHC` v1.4; el Capítulo 5 presenta los benchmarks clásicos e inferencia LLM; el Capítulo 6 expone los resultados cuánticos y la deconstrucción de ruido; el Capítulo 7 documenta la auditoría adversarial completa; y el Capítulo 8 sintetiza conclusiones y líneas abiertas.

---

# CAPÍTULO 2: ESTADO DEL ARTE Y TAXONOMÍA TEÓRICA EXHAUSTIVA

### 2.1 Geometría Diferencial y Optimización Riemanniana en Variedades Matriciales
La optimización sobre variedades matriciales suaves, sistematizada por Edelman, Arias y Smith [19], Absil, Mahony y Sepulchre [1] y Boumal [18], permite resolver problemas restringidos preservando la estructura intrínseca del espacio de parámetros. El conjunto de $k$-marcos ortonormales en $\mathbb{R}^D$ conforma la variedad compacta de Stiefel:
$$V_k(\mathbb{R}^D) = \left\{ X \in \mathbb{R}^{D \times k} : X^T X = I_k \right\}, \quad 1 \le k \le D$$
cuya dimensión intrínseca es $D k - \frac{1}{2}k(k+1)$. Para $k=1$, $V_1(\mathbb{R}^D)$ coincide con la esfera unitaria $S^{D-1}$; para $k=D$, coincide con el grupo ortogonal $\mathrm{O}(D)$. En representación del conocimiento jerárquico y flujos continuos, las variedades Riemannianas y pseudoriemannianas (como la bola de Poincaré y el modelo hiperboloide de Lorentz/Minkowski estudiados por Nickel y Kiela [25] y Ganea et al. [26]) demuestran que preservar la métrica exacta evita distorsiones exponenciales de distancia.

### 2.2 La Variedad de Stiefel $V_k(\mathbb{R}^D)$: Retracciones Polares, MGS2 y Estabilidad Numérica
Una retracción $\mathcal{R}_X: T_X V_k(\mathbb{R}^D) \to V_k(\mathbb{R}^D)$ mapea vectores tangentes nuevamente sobre la variedad con acuerdo local de primer orden. Existen tres familias principales:
1. **Proyección Polar ($\mathcal{P}_{V_k}(A) = A(A^T A)^{-1/2}$):** Minimiza la distancia en norma de Frobenius $\|X - A\|_F$ sobre $V_k(\mathbb{R}^D)$ [31]. Su cálculo vía SVD requiere diagonalizaciones espectrales costosas, mientras que la familia iterativa de Newton-Schulz [3, 31] emplea exclusivamente productos matriciales densos (`GEMM`), ideales para unidades vectoriales SIMD, siempre que el iterado inicial caiga estrictamente dentro de la cuenca de convergencia espectral $\|I_k - X_0^T X_0\|_2 < 1$.
2. **Ortonormalización QR y Gram-Schmidt Modificado de Doble Pasada (MGS2):** Mientras el algoritmo clásico de Gram-Schmidt (CGS) y una sola pasada de MGS sufren pérdida de ortogonalidad proporcional a $\mathcal{O}(\kappa(A)\epsilon_{\text{mach}})$, Giraud, Langou y Rozložník [40] demostraron rigurosamente el principio *"Twice is Enough"* (originado en Kahan y Parlett): ejecutar **dos pasadas sucesivas de Gram-Schmidt Modificado (MGS2)** restaura la ortogonalidad de las columnas al nivel óptimo $\mathcal{O}(\epsilon_{\text{mach}})$ siempre que $\kappa(A)\epsilon_{\text{mach}} < 1$. Esta propiedad resulta crucial para nuestro compilador nativo `Mathesis MTHC` v1.4 (§4.7), permitiendo ortonormalizar matrices $D \times k$ directamente en registros escalares/vectoriales SSE2 con tamaño de código constante $\mathcal{O}(1)$.
3. **Acumulación Numérica Compensada:** En productos internos de dimensión elevada ($D \ge 1024$), la suma recursiva ingenua acumula un error de orden $\mathcal{O}(D \epsilon_{\text{mach}})$. Los esquemas libres de error basados en `Fast2Sum` de Dekker [35] y la sumación mejorada de Kahan-Babuška por Neumaier [2, 3] desacoplan el error de primer orden respecto de $D$.

### 2.3 Taxonomía de Sistemas IPC de Memoria Compartida para Inferencia Distribuida
Los marcos contemporáneos de aprendizaje profundo emplean distintos mecanismos de transporte de tensores:
- **Apache Arrow Plasma / Ray Object Store [39]:** Mapea objetos inmutables en `/dev/shm`, pero requiere un proceso demonio coordinador (`plasma_store_server`), transacciones sobre sockets de dominio Unix para publicar y sellar `ObjectID`s, y carece de soporte nativo de actualización *in-place* mediante cerraduras de secuencia para flujos latentes de baja latencia.
- **vLLM y PagedAttention [38]:** Optimiza magistralmente la paginación de bloques de caché KV dentro de un motor de inferencia sobre GPU, pero su interfaz externa inter-modelo continúa orientada a peticiones de texto/tokens o tensores serializados vía RPC.
- **CUDA IPC (`cudaIpcMemHandle_t`) y NCCL:** Proporcionan transferencia directa entre memorias HBM de GPUs, pero no cubren el transporte soberano en RAM de host entre procesos heterogéneos (Python, binarios nativos PE32+/ELF64 y demonios de control cuántico) en estaciones de trabajo sin GPU dedicada.
- **Cerraduras de Secuencia (Seqlocks) de Lamport [36]:** Introducidas originalmente por Lamport (1977) para lecturas concurrentes sin bloqueo mutuo y adoptadas en el kernel Linux para relojes de tiempo real (`jiffies`/`vdso`), permiten a múltiples lectores verificar en tiempo constante si un escritor modificó una estructura durante la lectura. `PmtpShmBus` v2.1 adapta este paradigma a descriptores tensoriales de 64 bytes combinándolo con integridad criptográfica BLAKE2s.

### 2.4 Procesadores Cuánticos Superconductores NISQ y Topología Heavy-Hexagonal Heron
Los algoritmos variacionales híbridos —VQE [5, 8, 9] y QAOA [6, 7]— buscan aproximar estados fundamentales mediante circuitos parametrizados cortos asistidos por optimizadores clásicos, complementados por técnicas de mitigación de errores como extrapolación a ruido cero [10, 11, 12], lectura libre de modelo TREX [21] y mitigación escalable [32]. En la generación **IBM Heron** de 156 qubits (`ibm_fez`, `ibm_kingston`, `ibm_marrakesh`) [34], el acoplador sintonizable ejecuta compuertas nativas `CZ` de alta fidelidad mediana ($\tilde{\epsilon}_{2Q} \approx 0.19\% - 0.27\%$), pero mantiene la topología planar **Heavy-Hexagonal** [13]: un grafo bipartito donde los vértices de esquina tienen grado 3 y los vértices puente grado 2. Como consecuencia: (a) ningún vértice lógico de grado $\ge 4$ puede incrustarse sin cadenas de enrutamiento [14, 15], y (b) ningún ciclo impar (triángulos $K_3$, pentágonos del Dodecaedro) es subgrafo isomorfo de una red bipartita sin insertar permutaciones `SWAP`.

### 2.5 Razonamiento en Espacios Latentes Continuos frente a Tokenización Discreta
Investigaciones recientes confirman la viabilidad de transmitir y refinar estados ocultos sin colapsarlos a lenguaje natural intermedio: **COCONUT** (Hao et al., 2024 [24]) entrena modelos para realimentar el último estado oculto como vector de pensamiento continuo, mientras revisiones sistemáticas recientes del razonamiento latente [23] evidencian ganancias sustanciales en tareas algebraicas y combinatorias. Sin embargo, para que el intercambio inter-modelo entre arquitecturas o capas sea estable sin reentrenamiento conjunto masivo, es indispensable confinar la norma y la regularidad Lipschitz de las proyecciones inyectadas [37], problema abordado formalmente en el Capítulo 3.

---

# CAPÍTULO 3: TEORÍA MATEMÁTICA Y TEOREMAS FORMALES DEMOSTRADOS

### 3.1 Lema 1 y Teorema 1: Cota de Redondeo en Sumación Compensada de Neumaier (`Fast2Sum`)
**Lema 1 (Extracción Exacta de Redondeo Ordenado — Dekker `Fast2Sum` [35]):**  
*Sean $a, b \in \mathbb{F}$ números de punto flotante IEEE-754 binary64 libres de desbordamiento tales que $|a| \ge |b|$. Sea $t = \operatorname{fl}(a + b)$ y $e = \operatorname{fl}(\operatorname{fl}(a - t) + b)$. Entonces $a + b = t + e$ exactamente en aritmética real (sin error de segundo orden).*

**Teorema 1 (Cota de Error en Sumación Compensada de Neumaier [2, 3]):**  
*Sea $x = (x_1, \dots, x_n)^T \in \mathbb{F}^n$ evaluado en precisión doble IEEE-754 ($\epsilon_{\text{mach}} = 2^{-53} \approx 1.11 \times 10^{-16}$) con $n \epsilon_{\text{mach}} < 1$. El algoritmo de Neumaier inicializa $s_1 = x_1, c_1 = 0$ y, para $i = 2, \dots, n$, calcula $t_i = \operatorname{fl}(s_{i-1} + x_i)$, aplica la ramificación ordenada:*
$$e_i = \begin{cases} \operatorname{fl}(\operatorname{fl}(s_{i-1} - t_i) + x_i) & \text{si } |s_{i-1}| \ge |x_i|, \\ \operatorname{fl}(\operatorname{fl}(x_i - t_i) + s_{i-1}) & \text{si } |s_{i-1}| < |x_i|, \end{cases}$$
*actualiza $s_i = t_i,\; c_i = \operatorname{fl}(c_{i-1} + e_i)$, y retorna $\hat{S} = \operatorname{fl}(s_n + c_n)$. Entonces el error absoluto satisface:*
$$\left| \hat{S} - \sum_{i=1}^n x_i \right| \le \left( 2\epsilon_{\text{mach}} + \mathcal{O}(n \epsilon_{\text{mach}}^2) \right) \sum_{i=1}^n |x_i|. \tag{3.1}$$

**Demostración:** A diferencia del algoritmo sin ramas `TwoSum` de Knuth (que requiere 6 operaciones en punto flotante), el algoritmo de Neumaier emplea una comparación de magnitudes seguida de 3 sumas flotantes para invocar el Lema 1 (`Fast2Sum` de Dekker [35]) con los operandos ordenados por valor absoluto ($\max(|s_{i-1}|, |x_i|) \ge \min(|s_{i-1}|, |x_i|)$). Por el Lema 1, en cada paso $i$ se cumple exactamente en $\mathbb{R}$ que $s_{i-1} + x_i = s_i + e_i$, con $|e_i| \le \epsilon_{\text{mach}} |s_i| \le \epsilon_{\text{mach}}(1+\epsilon_{\text{mach}})\sum_{j=1}^i |x_j|$. Sumando telescópicamente desde $i=2$ hasta $n$, la suma exacta vale $\sum_{i=1}^n x_i = s_n + \sum_{i=2}^n e_i$. El acumulador compensador $c_n$ aproxima $\sum_{i=2}^n e_i$ con error estándar de suma recursiva $\left| c_n - \sum_{i=2}^n e_i \right| \le \gamma_{n-1} \sum_{i=2}^n |e_i| = \mathcal{O}(n \epsilon_{\text{mach}}^2) \sum_{i=1}^n |x_i|$, ya que cada $|e_i|$ porta ya un factor $\epsilon_{\text{mach}}$. Finalmente, la adición terminal $\hat{S} = (s_n + c_n)(1 + \delta)$ con $|\delta| \le \epsilon_{\text{mach}}$ introduce a lo sumo $\epsilon_{\text{mach}} |s_n + c_n| \le \left(2\epsilon_{\text{mach}} + \mathcal{O}(n\epsilon_{\text{mach}}^2)\right)\sum_{i=1}^n |x_i|$, completando (3.1). $\blacksquare$

### 3.2 Lema 2: Pre-Acondicionamiento de Frobenius Libre de SVD y Dominio de Contracción
Una sutileza crítica identificada durante la auditoría matemática (`REM-22`) radica en distinguir entre las condiciones $\|E_0\|_2 < 1$ y $\|E_0\|_F < 1$. Si se escala una matriz de rango completo $A \in \mathbb{R}^{D \times k}$ por su norma espectral $X_0 = A / \|A\|_2$, los autovalores de $X_0^T X_0$ yacen en $(\sigma_{\min}^2/\sigma_{\max}^2, 1]$, por lo que $\|E_0\|_2 = 1 - \sigma_{\min}^2/\sigma_{\max}^2 < 1$ siempre se cumple, **pero $\|E_0\|_F$ puede superar la unidad** para $k \ge 3$ (contraejemplo explícito verificado en `benchmark_unified_pmtp_regimes.py`: $A = \operatorname{diag}(1, 0.1, 0.1) \implies \|E_0\|_2 = 0.99 < 1$, mientras $\|E_0\|_F = \sqrt{0 + 0.99^2 + 0.99^2} \approx 1.4001 > 1$). Además, calcular $\|A\|_2$ exactamente requeriría una iteración espectral o SVD previa. El siguiente lema resuelve ambos puntos sin recurrir a SVD:

**Lema 2 (Escalado de Frobenius Garantizado Libre de SVD):**  
*Sea $A \in \mathbb{R}^{D \times k}$ de rango columna completo ($\operatorname{rank}(A) = k \ge 1$). Defínase $X_0 = A / \|A\|_F$ y $E_0 = I_k - X_0^T X_0$. Entonces $E_0$ es simétrica semidefinida positiva y sus autovalores satisfacen estrictamente:*
$$0 \le \lambda_j(E_0) = 1 - \frac{\sigma_j(A)^2}{\|A\|_F^2} \le 1 - \frac{\sigma_{\min}(A)^2}{\|A\|_F^2} < 1, \quad \forall j \in \{1, \dots, k\}, \tag{3.2}$$
*por lo cual $\|E_0\|_2 < 1$ se cumple incondicionalmente con costo $\mathcal{O}(Dk)$ sin descomposición en valores singulares.*

**Demostración:** Como $\|A\|_F^2 = \sum_{j=1}^k \sigma_j(A)^2 > 0$ y $\sigma_{\min}(A) > 0$ por hipótesis de rango completo, para todo $j$ se tiene $0 < \sigma_j(A)^2 / \|A\|_F^2 \le 1$ (con igualdad a $1$ únicamente cuando $k=1$, en cuyo caso $E_0 = 0$). Luego $\lambda_j(E_0) \in [0, 1)$, y dado que $E_0$ es simétrica, $\|E_0\|_2 = \max_j |\lambda_j(E_0)| < 1$. $\blacksquare$

### 3.3 Teorema 2: Identidad Polinómica Exacta y Convergencia Cuártica de Newton-Schulz
**Teorema 2 (Convergencia Cuártica Exacta hacia el Factor Polar):**  
*Sea $A \in \mathbb{R}^{D \times k}$ con $\operatorname{rank}(A) = k$ e inicialización $X_0 = A / \|A\|_F$ (o cualquier escalado tal que $\|E_0\|_2 < 1$). La iteración polinómica de cuarto orden:*
$$X_{m+1} = X_m P(E_m), \qquad P(E_m) = I_k + \frac{1}{2} E_m + \frac{3}{8} E_m^2 + \frac{5}{16} E_m^3, \qquad E_m = I_k - X_m^T X_m \tag{3.3}$$
*verifica en cada paso la identidad algebraica exacta de cuatro términos:*
$$E_{m+1} = \frac{35}{64} E_m^4 + \frac{7}{32} E_m^5 + \frac{35}{256} E_m^6 + \frac{25}{256} E_m^7, \tag{3.4}$$
*conserva la semidefinición positiva $0 \preceq E_{m+1} \prec I_k$ con contracción espectral monótona:*
$$\|E_{m+1}\|_2 = \frac{35}{64}\|E_m\|_2^4 + \frac{7}{32}\|E_m\|_2^5 + \frac{35}{256}\|E_m\|_2^6 + \frac{25}{256}\|E_m\|_2^7 \le \|E_m\|_2^4 \left(1 - \left(1 - \|E_m\|_2\right)\right) < \|E_m\|_2, \tag{3.5}$$
*converge globalmente sobre el dominio de rango completo hacia el factor polar exacto $\mathcal{P}_{V_k}(A) = A(A^T A)^{-1/2}$, y una vez en el régimen local $\|E_m\|_F < 1$ satisface la cota no asintótica cerrada en norma de Frobenius:*
$$\|E_{m+1}\|_F \le \frac{35}{64}\|E_m\|_F^4 + \frac{7}{32}\|E_m\|_F^5 + \frac{35}{256}\|E_m\|_F^6 + \frac{25}{256}\|E_m\|_F^7. \tag{3.6}$$

**Demostración:** Como $X_m^T X_m = I_k - E_m$ conmuta con todo polinomio en $E_m$, se tiene $X_{m+1}^T X_{m+1} = P(E_m)(I_k - E_m)P(E_m) = (I_k - E_m)[P(E_m)]^2$. Expandiendo exactamente $[P(E)]^2$:
$$[P(E)]^2 = I_k + E + \left(\frac{1}{4}+\frac{3}{4}\right)E^2 + \left(\frac{3}{8}+\frac{5}{8}\right)E^3 + \left(\frac{9}{64}+\frac{5}{16}\right)E^4 + \frac{15}{64}E^5 + \frac{25}{256}E^6 = I_k + E + E^2 + E^3 + \frac{29}{64}E^4 + \frac{15}{64}E^5 + \frac{25}{256}E^6.$$
Multiplicando por $(I_k - E)$ se cancelan idénticamente las potencias de grado $1, 2$ y $3$:
$$(I_k - E)[P(E)]^2 = I_k + \left(\frac{29}{64}-1\right)E^4 + \left(\frac{15}{64}-\frac{29}{64}\right)E^5 + \left(\frac{25}{256}-\frac{15}{64}\right)E^6 - \frac{25}{256}E^7 = I_k - \frac{35}{64}E^4 - \frac{7}{32}E^5 - \frac{35}{256}E^6 - \frac{25}{256}E^7.$$
Sustituyendo en $E_{m+1} = I_k - X_{m+1}^T X_{m+1}$ resulta exactamente (3.4). Para cualquier autovalor $\lambda \in [0, 1)$ de $E_m$, el polinomio escalar $q(\lambda) = 1 - (1-\lambda)P(\lambda)^2$ verifica $q(0)=0, q(1)=1$ y $q(\lambda) < \lambda$ en $(0,1)$ pues $(1-\lambda)P(\lambda)^2 > 1-\lambda \iff P(\lambda)^2 > 1$ para todo $\lambda > 0$. Por tanto $\|E_m\|_2 \to 0$ cuárticamente y en a lo sumo $m_0$ pasos se alcanza $\sqrt{k}\|E_{m_0}\|_2 < 1 \implies \|E_{m_0}\|_F < 1$, desde donde la desigualdad triangular y la submultiplicatividad $\|E^r\|_F \le \|E\|_F^r$ arrojan (3.6). Finalmente, si $A = U \Sigma V^T$ es la SVD reducida ($U \in V_k(\mathbb{R}^D), V \in \mathrm{O}(k)$), por inducción $X_m = U \Sigma_m V^T$ preserva los vectores singulares izquierdo y derecho de $A$ mientras $\Sigma_m \to I_k$, probando que $\lim_{m\to\infty} X_m = U V^T = A(A^T A)^{-1/2}$. $\blacksquare$

### 3.4 Teorema 3: Inyección Co-Isométrica Completa en $\ker(W)$, Variante Suave de Tikhonov y Cota de Lipschitz Compacta
Sea $W \in \mathbb{R}^{d \times r}$ una co-isometría ($W W^T = I_d$, con $r > d$). Por el teorema del rango-nulidad, $\dim(\ker(W)) = r - d > 0$, de modo que el operador ingenuo $s \mapsto W s / \|W s\|_2$ posee una singularidad topológica inevitable en $\ker(W)$ (ninguna retracción de $\mathbb{R}^d \setminus \{0\}$ sobre $S^{d-1}$ puede extenderse continuamente al origen $0$). En `pmtp_coisometry.py` v2.0 (`REM-15` y `REM-21`) se formalizan dos operadores complementarios según el requerimiento del pipeline:
1. **Modo Canónico Ortonormal (`mode="canonical"`):** Construido mediante descomposición QR **completa** $A = Q R$ (`np.linalg.qr(A, mode="complete")`, corrigiendo el defecto de QR reducida de versiones previas donde `Q[:, d:]` quedaba vacío), almacena explícitamente tanto $W = Q[:, :d]^T$ como una base ortonormal completa $N = Q[:, d:] \in V_{r-d}(\mathbb{R}^r)$ de $\ker(W)$. Si $\|W s\|_2 \le \epsilon$, devuelve determinísticamente el polo canónico $e_1 \in S^{d-1}$, garantizando $\|p(s)\|_2 = 1$ para **todo** $s \in \mathbb{R}^r$ (incluyendo $s = 0$, subnormales $10^{-305}$ escalados por norma infinita antes de proyectar, y combinaciones exactas en $\operatorname{span}(N)$).
2. **Modo Regularizado Suave de Tikhonov (`mode="tikhonov"`):** Define $p_\tau(s) = \frac{W s}{\sqrt{\|W s\|_2^2 + \tau^2}}$ con $\tau > 0$. Este operador es globalmente $C^\infty(\mathbb{R}^r, B_2^d(1))$, satisface $\|p_\tau(s)\|_2 < 1$ y posee constante global de Lipschitz estrictamente finita $L(p_\tau) \le \|W\|_2 / \tau = 1 / \tau$ (verificada empíricamente en `pmtp_coisometry.py` v2.0 con $L_{\text{emp}} = 367.79 \le 1/\tau = 1000$ para $\tau = 10^{-3}$).

**Teorema 3 (Confinamiento Energético y Perturbación Lipschitz sobre Dominios Compactos de Atención):**  
*Sea $h \in \mathcal{K}_R = \{ x \in \mathbb{R}^d : \|x\|_2 \le R \}$ la activación pre-LayerNorm en una capa Transformer sobre un dominio compacto acotado ($R < \infty$), y sea $h' = h + \beta \|h\|_2 p(s)$ con ganancia $\beta \in [0, 1]$ y $\|p(s)\|_2 \le 1$. Entonces:*
1. *La perturbación relativa de entrada cumple incondicionalmente $\|h' - h\|_2 / \|h\|_2 \le \beta$ (para $h \neq 0$), y $h' \in \mathcal{K}_{(1+\beta)R}$.*
2. *Aunque la atención dot-product estándar no es globalmente Lipschitz en todo $\mathbb{R}^d$ no acotado (Kim, Papamakarios y Mnih, ICML 2021 [37]), la presencia de RMSNorm / LayerNorm previa confina las entradas al compacto $\mathcal{K}_{(1+\beta)R}$, donde toda capa de autoatención $f$ es $C^\infty$ y por ende localmente Lipschitz con constante finita $L_{\text{attn}}(R) = \sup_{x \in \mathcal{K}_{(1+\beta)R}} \|Df(x)\|_2 < \infty$, garantizando:*
$$\|f(h') - f(h)\|_2 \le \beta \, L_{\text{attn}}(R) \, \|h\|_2. \tag{3.7}$$

**Demostración:** El ítem (1) se sigue inmediatamente de $\|h' - h\|_2 = \beta \|h\|_2 \|p(s)\|_2 \le \beta \|h\|_2$ y de la desigualdad triangular $\|h'\|_2 \le (1+\beta)\|h\|_2 \le (1+\beta)R$. Para el ítem (2), dado que $\mathcal{K}_{(1+\beta)R}$ es convexo y compacto y $f$ es combinación finita de aplicaciones lineales, exponenciales (`softmax` con denominador estrictamente $\ge 1$) y productos bilineales suaves, $Df(x)$ es continua y alcanza su supremo finito $L_{\text{attn}}(R)$ sobre $\mathcal{K}_{(1+\beta)R}$. Por el teorema del valor medio en espacios normados sobre el segmento $[h, h'] \subset \mathcal{K}_{(1+\beta)R}$, $\|f(h') - f(h)\|_2 \le L_{\text{attn}}(R)\|h' - h\|_2 \le \beta L_{\text{attn}}(R)\|h\|_2$. $\blacksquare$

### 3.5 Teorema 4: Identidad Bit a Bit en Régimen Inmutable y Libertad de Lecturas Desgarradas en Régimen Seqlock
Para responder con absoluta precisión arquitectónica a las observaciones de sistemas (`REM-16`), el protocolo `PmtpShmBus` v2.1 separa formalmente dos teoremas operativos:

**Teorema 4A (Identidad Bit a Bit en Régimen Zero-Copy Inmutable `FLAG_IMMUTABLE_EPOCH`):**  
*Sea $\mathcal{M}$ una región física compartida mapeada en los espacios virtuales de $P_{\text{prod}}$ y $P_{\text{cons}}$ con bandera `FLAG_IMMUTABLE_EPOCH` activa y contador $\texttt{seq\_num} = 2k > 0$ congelado durante la época de lectura. La vista `view_tensor_zerocopy()` construye un descriptor `ndarray` de solo lectura apuntando directamente a `base_ptr + 64` en complejidad temporal y espacial $\mathcal{O}(1)$ respecto de $D$, verificando `shares_memory == True` y deriva bit a bit idénticamente nula ($\max_i |T_{\text{prod}}[i] - T_{\text{cons}}[i]| = 0$).*

**Teorema 4B (Ausencia de Lecturas Desgarradas y de Falsos Positivos TOCTOU en Régimen Seqlock Concurrente):**  
*Sea un escritor serializado por exclusión mutua atómica inter-proceso (`LOCK CMPXCHG8B`) que ejecuta: (W1) fijar $\texttt{seq\_num} \leftarrow 2k+1$ (impar); (W2) barrera de memoria; (W3) escribir payload $P^{(k+1)}$ y resumen $\tau^{(k+1)} = \operatorname{BLAKE2s}_{64}(P^{(k+1)})$ en offset 56; (W4) barrera de liberación; (W5) fijar $\texttt{seq\_num} \leftarrow 2k+2$ (par). Sea un lector concurrente sin bloqueo que ejecuta: (R1) leer $s_1 = \texttt{seq\_num}$, reintentando si $s_1 = 0$ o $s_1 \bmod 2 = 1$; (R2) barrera de adquisición; (R3) capturar en memoria privada tanto el payload $\hat{P}$ como el resumen almacenado $\hat{\tau}$ (offset 56); (R4) barrera de lectura; (R5) leer $s_2 = \texttt{seq\_num}$ y reintentar si $s_1 \neq s_2$; (R6) aceptar $\hat{P}$ si y solo si $\operatorname{BLAKE2s}_{64}(\hat{P}) = \hat{\tau}$. Entonces: (i) ningún lector acepta jamás una mezcla parcial de dos épocas distintas; y (ii) ningún escritor ulterior que inicie después de (R5) puede inducir un falso positivo de integridad sobre $\hat{\tau}$.*

**Demostración:** Para (4A), las tablas de páginas del procesador (`CR3` en `x86_64`) traducen ambas direcciones virtuales al mismo marco físico de página RAM sin transcodificación ni copia intermedia. Para (4B), supóngase que un lector observa $s_1 = s_2 = 2k > 0$ pares e iguales. Por monotonía estricta de $\texttt{seq\_num}$, durante todo el intervalo temporal entre (R1) y (R5) ningún escritor ejecutó (W1) (que habría incrementado $\texttt{seq\_num}$ a $\ge 2k+1$), ni estaba en curso una escritura previa (pues $s_1$ es par y las barreras (W4)/(R2) ordenan todas las tiendas de la época $2k$ antes de (R3) y todas las cargas de (R3) antes de (W1) de cualquier época $2k+1$ futura). Como tanto $\hat{P}$ como $\hat{\tau}$ fueron copiados a registros/memoria privada del lector **dentro de (R3), estrictamente antes de (R5)**, ambos pertenecen a la misma época ininterrumpida $2k$, erradicando por completo la ventana TOCTOU presente cuando el digest se leía después de $s_2$. $\blacksquare$

### 3.6 Teorema 5: Factorización Simpléctica Remediada en $\mathrm{SO}(2)$ e Invarianza en Hiperboloide de Minkowski
**Teorema 5:** *Para todo ángulo $\theta \in (-\pi, \pi]$, toda rotación plana $R(\theta) \in \mathrm{SO}(2)$ admite evaluación numérica estable libre de la singularidad $\tan(\theta/2) \to \infty$ en $|\theta| \to \pi$ mediante reducción angular previa:*
$$\theta' = \begin{cases} \theta - \operatorname{sign}(\theta)\pi & \text{si } |\theta| > \pi/2 \quad (\text{con pre-inversión exacta } v \leftarrow -v), \\ \theta & \text{si } |\theta| \le \pi/2, \end{cases} \tag{3.8}$$
*seguida sobre $|\theta'| \le \pi/2$ (donde $|\tan(\theta'/2)| \le 1$) de la triple cizalla unimodular:*
$$R(\theta') = \begin{pmatrix} 1 & -\tan(\theta'/2) \\ 0 & 1 \end{pmatrix} \begin{pmatrix} 1 & 0 \\ \sin\theta' & 1 \end{pmatrix} \begin{pmatrix} 1 & -\tan(\theta'/2) \\ 0 & 1 \end{pmatrix}, \tag{3.9}$$
*preservando $\det(S_i) = 1$ exactamente y acotando el error de rotación uniforme en $(-\pi, \pi]$ a $1.73 \times 10^{-16}$ (`remediated_shear_rotation.py`, `Exit Code 0`). Asimismo, la proyección sobre el hiperboloide de Minkowski $\mathbb{H}^m = \{ z \in \mathbb{R}^{1,m} : -z_0^2 + \sum_{i=1}^m z_i^2 = -1, z_0 > 0 \}$ evaluada con suma espacial de Neumaier mantiene deriva métrica $\le 2.89 \times 10^{-15}$ en $D=1024$.* $\blacksquare$

---

# CAPÍTULO 4: ARQUITECTURA DE SILICIO DE `PmtpShmBus` v2.1, `Mathesis MTHC` v1.4 Y PROTOTIPO EINSOFOS

### 4.1 Especificación Binaria Exacta del Descriptor ABI v2.1 (64 Bytes Cache-Aligned)
Tanto `pmtp_seqlock_abi.py` v2.1 como el compilador nativo `mthc.py` v1.4 obedecen un único layout binario canónico de 64 bytes exactos (`struct.calcsize("<4sHHHHIQQQIIQQ") == 64`), alineado a una línea completa de caché L1/L2 en arquitecturas `x86_64`:

| Offset (Bytes) | Campo Binario | Tipo (`struct`) | Tamaño | Descripción Semántica en ABI v2.1 |
|:---:|---|:---:|:---:|---|
| `0 .. 3` | `magic` | `4s` | 4 B | Firma ASCII exacta `"PMTP"` (`0x50 0x4D 0x54 0x50`). |
| `4 .. 5` | `version` | `uint16` (`H`) | 2 B | Versión de protocolo (`2`). |
| `6 .. 7` | `flags` | `uint16` (`H`) | 2 B | Bit 0: `LE`; Bit 1: `READY`; Bit 2: `WRITER_LOCK`; Bit 3: `IMMUTABLE_EPOCH`. |
| `8 .. 9` | `dtype` | `uint16` (`H`) | 2 B | Código numérico IEEE-754 (`0 = fp32`, `1 = fp64`, `2 = fp16`). |
| `10 .. 11` | `rank` | `uint16` (`H`) | 2 B | Rango tensorial (`1` para $S^{D-1}$, `2` para matriz $V_k(\mathbb{R}^D)$). |
| `12 .. 15` | `dim_0` | `uint32` (`I`) | 4 B | Cantidad total de escalares contiguos ($D$ o $D \times k$). |
| `16 .. 23` | `seq_num` | `uint64` (`Q`) | 8 B | Contador Seqlock (`impar` = escritura activa, `par > 0` = época confirmada). |
| `24 .. 31` | `timestamp_ns` | `uint64` (`Q`) | 8 B | Marca temporal monotónica en nanosegundos (`perf_counter_ns` / `RDTSC`). |
| `32 .. 39` | `payload_bytes` | `uint64` (`Q`) | 8 B | Longitud exacta en bytes del área de datos a partir del offset 64. |
| `40 .. 43` | `producer_pid` | `uint32` (`I`) | 4 B | Identificador de proceso del último escritor confirmado. |
| `44 .. 47` | `dim_k` | `uint32` (`I`) | 4 B | Número de columnas ortonormales $k$ en $V_k(\mathbb{R}^D)$ (`1` en $S^{D-1}$). |
| `48 .. 55` | `lock_word` | `int64` (`q`) | 8 B | Palabra alineada a 8 bytes para exclusión atómica inter-proceso (`CAS64`). |
| `56 .. 63` | `blake2s_digest64` | `uint64` (`Q`) | 8 B | Etiqueta criptográfica truncada BLAKE2s de 64 bits sobre el payload. |

El payload tensorial comienza invariablemente en `base_ptr + 64`, impidiendo falso compartido (*false sharing*) de línea de caché entre metadatos de sincronización y lecturas vectoriales SIMD sobre las columnas de $X$.

### 4.2 Mecanismos de Mapeo de Páginas Físicas en Windows (`CreateFileMappingW`) y POSIX (`/dev/shm`)
En `pmtp_seqlock_abi.py` v2.1 (`REM-24`), la asignación de memoria compartida opera de forma transparente multiplataforma sin cursores mutables de archivo (`seek`/`read`/`write` fueron erradicados en su totalidad en favor de `struct.pack_into`/`unpack_from` y rebanadas atómicas por offset):
- **Subsistema Windows NT:** Invoca `mmap.mmap(-1, total_size, tagname="Local\\...")`, respaldado directamente por objetos de sección del kernel (`CreateFileMappingW` + `MapViewOfFile`) sin tocar sistemas de archivos NTFS.
- **Subsistema Linux / POSIX:** Sanitiza el identificador hacia `/dev/shm/pmtp_<tag>` sobre `tmpfs` en RAM mediante `os.open(..., O_CREAT | O_RDWR, 0o600)`, `os.ftruncate` y `mmap(..., MAP_SHARED, PROT_READ | PROT_WRITE)` con opción de desvinculación limpia (`unlink_posix=True`).

### 4.3 Autenticación de Integridad BLAKE2s-64 Libre de Ventana TOCTOU
Para detectar corrupciones silenciosas de memoria o escritores externos defectuosos sin incurrir en falsos positivos bajo concurrencia, el productor precalcula el resumen BLAKE2s de 64 bits (`digest_size=8`) antes de adquirir la ventana impar, escribe el payload y el resumen `blake2s_digest64` en el offset 56, ejecuta una barrera completa de memoria y recién entonces publica `even_seq`. Simétricamente, el consumidor captura `stored_digest` y los bytes del payload antes de leer `seq2`. Así, toda discrepancia observada cuando `seq1 == seq2` dispara determinísticamente `PmtpIntegrityError` (verificado mediante inyección adversarial de inversión de 1 bit en el Hound 4 de `pmtp_seqlock_abi.py`).

### 4.4 Protocolo de Concurrencia Seqlock Multi-Escritor / Multi-Lector con Backoff Escalonado
El protocolo Seqlock clásico presupone un único escritor; si dos hilos escritores incrementaran simultáneamente `seq_num` sin coordinación, romperían la invariante de paridad impar/par. `PmtpSeqlockBuffer` v2.1 resuelve esto combinando un cerrojo local por proceso con una instrucción atómica `LOCK CMPXCHG8B` (`ntdll._InterlockedCompareExchange64`) sobre `lock_word` (offset 48) para serializar escritores inter-proceso manteniendo a los lectores 100% libres de cerrojos (*lock-free*). Además, para evitar inanición de planificación en procesadores de bajo conteo de núcleos (como los 2 núcleos físicos del `AMD A4-6300` cuando compiten 8 hilos), el lazo de reintento del consumidor implementa **backoff escalonado de tres niveles**: giro puro en espacio de usuario durante los primeros intentos, cesión cooperativa de cuanto (`SwitchToThread` / `sched_yield` vía `sleep(0)`) cada 8 giros, y micro-pausa de $500\,\mu\text{s}$ a partir del intento 64 si un escritor fue desalojado por el planificador del sistema operativo en mitad de su ventana impar.

### 4.5 Prototipo Experimental de Kernel Bare-Metal EinsofOS (UEFI, ACPI MADT, MMIO) y Frontera de Alcance
Como exploración complementaria de eliminación de sobrecarga del sistema operativo (delimitada explícitamente como prototipo de ingeniería en §1.6), se diseñó la capa bare-metal **EinsofOS** en modo largo `x86_64` (Ring 0):
1. **Arranque UEFI y Topología ACPI MADT:** Cargado como ejecutable PE32+ (`BOOTX64.EFI`), recorre `RSDP` $\to$ `XSDT` $\to$ tabla `APIC` (MADT) para localizar la base MMIO del Local APIC (`0xFEE00000`) y enumerar los núcleos físicos disponibles.
2. **Secuencia Multi-Core `INIT-SIPI-SIPI`:** El procesador de arranque (BSP) despierta a los procesadores de aplicación (APs) mediante `INIT IPI`, espera calibrada por `RDTSC` ($10\,\text{ms}$) y doble `Startup IPI` hacia el trampolín en `0x08000`, promoviendo los APs a modo largo de 64 bits con tablas de páginas PML4 de identidad.
3. **Corrección Física sobre Instrucciones Atómicas (`REM-26`):** En la conmutación atómica de punteros de slab en RAM mediante `XCHG` con operando de memoria (que en `x86_64` aserta implícitamente el prefijo `LOCK`), la latencia real de hardware es de **$\sim 15 - 25$ ciclos de reloj** ($\approx 4 - 7\,\text{ns}$ a $3.5\,\text{GHz}$ por vaciado del buffer de escritura e invalidación de coherencia MESI/MOESI), corrigiendo la estimación idealizada de un ciclo ($0.3\,\text{ns}$) que solo aplica a renombrado registro-a-registro sin acceso a memoria.
4. **Salida Gráfica Lineal UEFI GOP:** Escritura directa sobre el framebuffer físico MMIO negociado por UEFI GOP sin servidores gráficos intermedios.

### 4.6 Arquitectura de Dos Niveles Intra-Nodo / Inter-Nodo: Realidad LAN TCP vs. Especificación RoCEv2/RDMA
En estricto apego a la honestidad experimental (`REM-26`), distinguimos sin ambigüedad entre el transporte físico actualmente operativo en nuestro laboratorio y la especificación de escalamiento para clústeres HPC:
- **Nivel 1 — Intra-Nodo Local (Medido en Silicio):** Memoria compartida `PmtpShmBus` v2.1 sobre páginas físicas del mismo host (`6.20\,\mu\text{s}` $p_{50}$ en vista zero-copy; `141.20\,\mu\text{s}` $p_{50}$ en snapshot Seqlock autenticado).
- **Enlace Inter-Nodo Actual en Laboratorio (Medido en Red Real):** La telepatía inter-nodo hacia el nodo secundario del clúster local (`ALADIN`, `192.168.100.21:9999`) opera actualmente sobre **sockets TCP/IP en LAN Ethernet estándar con autenticación BLAKE2s y anti-replay**, presentando una latencia empírica medida de **$\sim 35.32\,\text{ms}$** por transacción de red.
- **Nivel 2 — Especificación Arquitectónica RoCEv2 / InfiniBand RDMA (Diseño para Clústeres HPC):** Para reducir el salto inter-nodo al régimen de $< 2\,\mu\text{s}$ en centros de supercómputo equipados con adaptadores RNIC (ConnectX), el protocolo especifica el registro de la región de slabs fijada en RAM mediante `ibv_reg_mr` y la emisión unilateral `IBV_WR_RDMA_WRITE_WITH_IMM`, transportando el `SLAB_ID` de 32 bits en el campo `imm_data` sin intervención de la CPU receptora. Esta capa RDMA se reporta explícitamente como **especificación de diseño arquitectónico**, no como medición ejecutada sobre el par de nodos domésticos Ethernet del laboratorio.

### 4.7 Compilador Vectorial Nativo `Mathesis MTHC` v1.4: Emisión Directa PE32+/ELF64 sobre $V_k(\mathbb{R}^D)$ y Gate Hardware SSE2
El compilador soberano [`mthc.py`](file:///E:/POLYDIM_EINSOF/mthc.py) v1.4 traduce programas declarativos `.mth` directamente a binarios ejecutables nativos sin invocar compiladores C/C++, ensambladores externos ni enlazadores del sistema:
1. **Arquitectura Multi-Target Directa:** Emite ejecutables autónomos Windows x64 **PE32+** (`.exe`, importando únicamente `GetStdHandle`, `WriteFile` y `ExitProcess` de `kernel32.dll` con secciones `.text`, `.rdata` y `.bss` virtualmente contiguas de 2 MB sin huecos de página), ejecutables estáticos Linux **ELF64** (`.elf`, cero `glibc`, invocando `sys_write` y `sys_exit` vía `syscall` `0x0F 0x05`) y objetos reubicables COFF (`.obj`) y ELF (`.o`).
2. **Corrección Binaria de Cabecera ABI v2.1 (`REM-19` y `REM-20`):** Se erradicó el defecto de transposición little-endian de v1.3 (`\xC7\x07\x50\x54\x4D\x50` = `"PTMP"`) reemplazándolo en ambos emisores por la secuencia exacta `\xC7\x07\x50\x4D\x54\x50` (`"PMTP"`), verificada mediante inspección automatizada de bytes (`'PMTP' hits = 3`, `'PTMP' bugs = 0` en [`verify_mthc_v14_stiefel.py`](file:///E:/POLYDIM_EINSOF/verify_mthc_v14_stiefel.py)). Asimismo, se corrigió un defecto latente de codificación ModR/M heredado de v1.3 en el bucle de escalado (`\xF2\x0F\x11\x04\xC7` almacenaba `xmm0` en lugar de `\xF2\x0F\x11\x0C\xC7` para `xmm1`).
3. **Ortonormalización Matricial $V_k(\mathbb{R}^D)$ para $k \ge 1$ en Microcódigo SSE2 (`RETRACT_STIEFEL_MAT`):** Para $k > 1$, `MTHC` v1.4 inicializa matrices $D \times k$ column-major de rango completo garantizado (rampa base más refuerzo diagonal $D$ en $i = c$) y emite bucles anidados en registros `r8..r11` + `xmm0..xmm3` que ejecutan **dos pasadas completas de Gram-Schmidt Modificado (MGS2)** [40] sobre todas las columnas previas $p < j$ antes de normalizar cada columna $q_j$, logrando ortonormalidad de precisión de máquina usando instrucciones SSE2 universales compatibles con el procesador `AMD A4-6300` Piledriver (sin asumir instrucciones AVX2 ausentes en dicha microarquitectura).
4. **Gate de Verificación Ortonormal en Hardware (`_emit_hardware_stiefel_verifier`):** Inmediatamente después de cada retracción, el binario nativo calcula en registros SSE2 la suma cuadrada de Frobenius $\|X^T X - I_k\|_F^2 = \sum_{a=0}^{k-1}\sum_{b=0}^{k-1}(\langle q_a, q_b \rangle - \delta_{ab})^2$ en `xmm4` y ejecuta `ucomisd xmm4, [rip + const_tol_sq]` con umbral $10^{-26}$ ($\|X^T X - I_k\|_F \le 10^{-13}$). Dos saltos condicionales de hardware protegen la salida:
   - `jp fail_handler` (`0x0F 0x8A`): captura el flag de paridad `PF=1` activado por `ucomisd` ante cualquier singularidad `NaN` (p. ej. división `0.0 / 0.0`), terminando con `ExitProcess(1)` / `sys_exit(1)`.
   - `ja fail_handler` (`0x0F 0x87`): aborta con `Exit Code 1` si el defecto de ortonormalidad excede $10^{-13}$.
   En la suite [`verify_mthc_v14_stiefel.py`](file:///E:/POLYDIM_EINSOF/verify_mthc_v14_stiefel.py), el binario positivo [`mathesis_vk_stiefel_v14.exe`](file:///E:/POLYDIM_EINSOF/mathesis_vk_stiefel_v14.exe) (`5\,120` bytes totales, `2\,491` bytes de microcódigo) retrae $V_1(\mathbb{R}^{2048})$, $V_4(\mathbb{R}^{512})$ y $V_8(\mathbb{R}^{256})$ en **$15.18\,\text{ms}$** devolviendo `Exit Code 0`, mientras que ambos binarios sabuesos envenenados (matriz nula $0_{128\times 4}$ con $\|0 - I_4\|_F = 2.0$ y singularidad `0/0` `NaN`) son rechazados por la CPU nativa con **`Exit Code 1`**.

---

# CAPÍTULO 5: EVALUACIÓN EXPERIMENTAL EN SILICIO CLÁSICO (IPC E INFERENCIA LLM)

### 5.1 Configuración de Hardware Host (`AMD A4-6300` Piledriver) y Protocolo Estadístico
Todas las mediciones de rendimiento de memoria compartida, serialización, compilación nativa e inyección de activaciones latentes reportadas en este capítulo fueron ejecutadas en silicio físico local bajo las siguientes especificaciones verificadas (`REM-26`):
- **Unidad Central de Procesamiento (CPU):** AMD A4-6300 APU a 3.70 GHz (frecuencia turbo hasta 3.90 GHz), microarquitectura **Piledriver** (módulo dual de 2 núcleos lógicos), con soporte de extensiones vectoriales SSE2, SSE3, SSSE3, SSE4a, SSE4.1, SSE4.2, AVX, FMA3 y FMA4. *Nota técnica rigurosa:* este procesador no incorpora el conjunto de instrucciones AVX2 (introducido por AMD en Excavator / Zen), por lo cual todo el microcódigo vectorial emitido por `Mathesis MTHC` v1.4 se genera estrictamente sobre instrucciones x86_64 y SSE2 universales, garantizando compatibilidad determinista.
- **Memoria Principal:** 8.00 GB DDR3 a 1600 MHz en configuración de canal simple.
- **Sistema Operativo:** Microsoft Windows 10 Pro 64-bit (compilación 19045), respaldado por subsistema POSIX `/dev/shm` en entornos Linux compatibles.
- **Protocolo de Medición:** Para cada ensayo, se ejecutan 50 ciclos de calentamiento de caché L1/L2 previos a la captura de datos, seguidos de 200 a 500 iteraciones continuas medidas con temporizadores de resolución subnanosegundo (`time.perf_counter_ns` / instrucción de silicio `RDTSC`), reportando la media aritmética, la mediana ($p_{50}$), el percentil 99 ($p_{99}$) y la desviación estándar ($\sigma$).

### 5.2 Escalabilidad Dimensional ($D \in [512, 4096]$) y Comparación frente a Serialización 1D
La Tabla V sintetiza la evaluación dimensional de transporte de vectores continuos en precisión doble IEEE-754 (FP64, 8 bytes por componente) a través de dimensiones típicas de capas de modelos de lenguaje ($D \in \{512, 1024, 2048, 4096\}$), contrastando la serialización estándar JSON (texto UTF-8 parseado), C-Pickle binario en memoria, copia cruda en heap (`io.BytesIO`) y `PmtpShmBus`:

**TABLA V: Evaluación Dimensional de Latencia de Transporte en Silicio Host**

| Dimensión ($D$) | Bytes de Carga | Método de Transporte | Media ($\mu\text{s}$) | Mediana $p_{50}$ ($\mu\text{s}$) | Cola $p_{99}$ ($\mu\text{s}$) | Deriva Numérica | Speedup vs. JSON |
|:---:|:---:|---|:---:|:---:|:---:|:---:|:---:|
| **512** | 4\,096 B | Serialización JSON | 909.04 | 900.35 | 1\,043.61 | 0.00e+00 | $1.0\times$ (Base) |
| | | Python C-Pickle | 37.90 | 37.50 | 41.76 | 0.00e+00 | $24.0\times$ |
| | | Copia en Heap (`BytesIO`) | 5.44 | 5.40 | 7.61 | 0.00e+00 | $167.1\times$ |
| | | **`PmtpShmBus` (Vista Zero-Copy)** | **3.82** | **3.70** | **5.40** | **0.00e+00** | **$243.3\times$** |
| | | `PmtpShmBus` + Retracción Stiefel | 685.43 | 682.95 | 758.51 | 0.00e+00 | $1.3\times$ |
| **1024** | 8\,192 B | Serialización JSON | 1\,801.35 | 1\,791.85 | 1\,911.29 | 0.00e+00 | $1.0\times$ (Base) |
| | | Python C-Pickle | 39.32 | 39.20 | 42.30 | 0.00e+00 | $45.8\times$ |
| | | Copia en Heap (`BytesIO`) | 7.65 | 7.60 | 8.11 | 0.00e+00 | $235.5\times$ |
| | | **`PmtpShmBus` (Vista Zero-Copy)** | **4.45** | **4.30** | **6.10** | **0.00e+00** | **$416.7\times$** |
| | | `PmtpShmBus` + Retracción Stiefel | 1\,354.11 | 1\,318.95 | 2\,032.75 | 0.00e+00 | $1.3\times$ |
| **2048** | 16\,384 B | Serialización JSON | 4\,557.48 | 3\,680.25 | 19\,753.27 | 0.00e+00 | $1.0\times$ (Base) |
| | | Python C-Pickle | 55.10 | 53.90 | 105.67 | 0.00e+00 | $82.7\times$ |
| | | Copia en Heap (`BytesIO`) | 13.24 | 13.00 | 16.52 | 0.00e+00 | $344.2\times$ |
| | | **`PmtpShmBus` (Vista Zero-Copy)** | **5.18** | **5.00** | **7.80** | **0.00e+00** | **$736.1\times$** |
| | | `PmtpShmBus` + Retracción Stiefel | 4\,414.58 | 3\,827.55 | 9\,107.12 | 0.00e+00 | $1.0\times$ |
| **4096** | 32\,768 B | Serialización JSON | 7\,648.80 | 7\,372.00 | 13\,117.30 | 0.00e+00 | $1.0\times$ (Base) |
| | | Python C-Pickle v5 | 76.61 | 49.20 | 825.60 | 0.00e+00 | $149.8\times$ |
| | | Sockets TCP Loopback | 91.92 | 64.00 | 960.60 | 0.00e+00 | $115.2\times$ |
| | | **`PmtpShmBus` (Vista Zero-Copy)** | **6.41** | **6.20** | **11.20** | **0.00e+00** | **$1\,193.3\times$** |
| | | `PmtpShmBus` (Snapshot Seqlock) | 159.72 | 141.20 | 605.30 | 0.00e+00 | $47.9\times$ |

### 5.3 Tabla Unificada de los Tres Regímenes PMTP frente a C-Pickle, TCP Loopback y JSON en $D=4096$
Para responder con total honestidad a las críticas de sistemas sobre aparentes contradicciones numéricas entre diferentes secciones del borrador previo (`REM-25`), se ejecutó un arnés de benchmarking unificado ([`benchmark_unified_pmtp_regimes.py`](file:///E:/POLYDIM_EINSOF/benchmark_unified_pmtp_regimes.py)) midiendo de manera idéntica el payload canónico de $D=4096$ FP64 (exactamente $32\,768$ bytes) a través de todos los regímenes y líneas base:

**TABLA V-B: Tabla Unificada de Regímenes PMTP v2.1 y Líneas Base ($D=4096$, 32 KB FP64)**

| Régimen / Mecanismo de Transporte | Muestras ($n$) | Media ($\mu\text{s}$) | Mediana $p_{50}$ ($\mu\text{s}$) | Percentil $p_{99}$ ($\mu\text{s}$) | Desv. Estándar $\sigma$ ($\mu\text{s}$) | Garantía de Concurrencia y Memoria |
|---|:---:|:---:|:---:|:---:|:---:|---|
| **Régimen A: Vista Zero-Copy Inmutable (`IMMUTABLE_EPOCH`)** | 500 | **6.41** | **6.20** | **11.20** | 2.49 | Cero copias ($\mathcal{O}(1)$ RAM), alias `mmap` de solo lectura. |
| **Régimen B: Snapshot Seqlock + BLAKE2s-64 (Cálido)** | 500 | **159.72** | **141.20** | **605.30** | 165.38 | Copia atómica consistente, seguro concurrentemente con escritores. |
| **Régimen B-RT: Escritor Seqlock + Lector Snapshot (Ida y Vuelta)** | 300 | **289.75** | **281.40** | **427.20** | 25.18 | Publicación impar/par completa + copia y hash en consumidor. |
| **Régimen C: Adjunto en Frío del SO (`MapViewOfFile` + Unmap)** | 200 | **273.96** | **190.80** | **2\,328.10** | 328.11 | Apertura de handle de sección del kernel por transacción. |
| **Línea Base 1: Python C-Pickle Protocolo 5 (In-Memory)** | 300 | **76.61** | **49.20** | **825.60** | 164.37 | Serialización binaria en heap (1 consumidor mono-hilo). |
| **Línea Base 2: Sockets TCP Loopback (`127.0.0.1`, `TCP_NODELAY`)** | 200 | **91.92** | **64.00** | **960.60** | 114.35 | Pila de red del SO, conmutación de contexto y copias en buffer. |
| **Línea Base 3: Serialización JSON UTF-8 (Estándar Web / REST)** | 60 | **7\,648.80** | **7\,372.00** | **13\,117.30** | 858.89 | Transcodificación decimal texto (payload crece a 102 KB UTF-8). |

Esta caracterización aclara definitivamente los distintos escenarios de uso:
1. En **acceso estático o época congelada** (por ejemplo, pesos fijos o activaciones listas para lectura por múltiples agentes evaluadores), la **Vista Zero-Copy** tarda apenas **$6.20\,\mu\text{s}$**, superando por **$1\,193\times$** a JSON, por **$14.3\times$** a TCP y por **$12.0\times$** a C-Pickle.
2. En **flujos mutables continuos con escritores concurrentes**, el **Snapshot Seqlock** tarda **$141.20\,\mu\text{s}$**, proporcionando una garantía formal contra lecturas desgarradas y verificación criptográfica íntegra que ni C-Pickle ni TCP loopback ofrecen sin cerrojos externos pesados del sistema operativo.
3. El valor histórico de **$541.96\,\mu\text{s}$** correspondía al ciclo completo en frío (apertura de handle de mapeo, inicialización de estructuras auxiliares y recolección de basura) ejecutado repetidamente en bucle en el benchmark preliminar V1.

### 5.4 Evaluación de Difusión Concurrente Multi-Lector ($1 \to M$, $M \in [1, 16]$)
El verdadero punto de inflexión arquitectónico a favor de `PmtpShmBus` frente a mecanismos basados en serialización emerge en la difusión concurrente multi-agente (*fan-out* $1 \to M$), donde una activación intermedia producida por un modelo generador debe ser evaluada en paralelo por $M$ agentes verificadores o críticos:

**TABLA V-C: Escalabilidad en Difusión Concurrente Fan-Out ($D=4096$, 32 KB FP64)**

| Consumidores Concurrentes ($M$) | Latencia C-Pickle ($\mu\text{s}$) | Latencia PMTP SHM ($\mu\text{s}$) | Speedup PMTP Zero-Copy | Duplicación en Heap Evitada |
|:---:|:---:|:---:|:---:|:---:|
| $M = 1$ | 94.70 | 5.60 | **$16.91\times$** | 32 KB |
| $M = 2$ | 99.10 | 7.80 | **$12.71\times$** | 64 KB |
| $M = 4$ | 99.40 | 10.40 | **$9.56\times$** | 128 KB |
| $M = 8$ | 188.30 | 17.20 | **$10.95\times$** | 256 KB |
| $M = 16$ | 369.60 | 29.60 | **$12.49\times$** | 512 KB |

Mientras que C-Pickle escala de forma lineal degradando el rendimiento debido a la asignación repetida de $M$ copias en el heap ($16 \times 32\,\text{KB} = 512\,\text{KB}$ por transacción), `PmtpShmBus` mantiene la huella de memoria física plana en exactamente **32 KB totales**, logrando un speedup de **$12.49\times$** al permitir que todos los procesos lean simultáneamente las mismas páginas mapeadas por el controlador de memoria.

### 5.5 Comparación Cuantitativa frente a Sockets Loopback y Demonios de Memoria Compartida (Plasma/Ray)
- **Frente a Sockets TCP Loopback:** El transporte local mediante sockets de red (`127.0.0.1`) con `TCP_NODELAY` activo requiere $91.92\,\mu\text{s}$ (media) y $64.00\,\mu\text{s}$ ($p_{50}$), siendo **$14.3\times$ más lento** que la vista zero-copy de PMTP debido a las transiciones de modo usuario a modo kernel y al copiado forzado de buffers en la pila de red del sistema operativo.
- **Frente a Apache Arrow Plasma / Ray Object Store [39]:** Plasma depende de un proceso servidor demonio externo (`plasma_store_server`). Cada transacción exige un apretón de manos cliente-servidor a través de un socket de dominio Unix, asignación y registro global de un `ObjectID` de 20 bytes, y sellado explícito del objeto (*seal*), introduciendo una sobrecarga basal de coordinación de **$50 - 150\,\mu\text{s}$** independientemente del tamaño de los datos. En contraste, `PmtpShmBus` es una arquitectura completamente **carente de demonios** (*daemonless*): las asignaciones se resuelven en microcódigo y llamadas directas al kernel, reduciendo la latencia de acceso a menos de $7\,\mu\text{s}$.

### 5.6 Inyección Latente Inter-Modelo en la Capa 12 de `Qwen 2.5` ($d=896$)
Se validó la inyección directa de activaciones latentes sobre el modelo de lenguaje de pesos abiertos `Qwen 2.5 0.5B` ($d_{\text{model}} = 896$, 24 capas Transformer) ejecutado en entorno local (`evaluacion_qwen_pmtp_latente.py`, `Exit Code 0`):
1. **Captura y Proyección:** En la Capa 12, se intercepta el tensor de activación $h \in \mathbb{R}^{896}$. Mediante el operador co-isométrico $W \in \mathbb{R}^{896 \times 1024}$ ($W W^T = I_{896}$, $\|W W^T - I\|_F = 8.40 \times 10^{-16}$), se acopla un estado latente normalizado $s \in S^{1023}$ recibido a través de `PmtpShmBus`.
2. **Latencia de Transporte:** La transferencia inter-proceso del vector latente se completó en **$198.10\,\mu\text{s}$**, con una fidelidad numérica exacta ($\Delta = 0.00 \times 10^0$).
3. **Estabilidad Post-Inyección:** La perturbación energética relativa satisfizo $\|h' - h\|_2 / \|h\|_2 \le \beta = 0.05$, permaneciendo dentro de los márgenes predichos por el Teorema 3 sin inducir desbordamientos ni distorsiones anómalas en las capas de atención subsiguientes.

### 5.7 Bucle Cerrado Híbrido Clásico-Cuántico en Tiempo Real (`hybrid_stiefel_classical_quantum_loop.py`)
Para certificar la integración viva entre el bus de memoria compartida clásica y el procesador cuántico, se ejecutó en silicio el pipeline cerrado [`hybrid_stiefel_classical_quantum_loop.py`](file:///E:/POLYDIM_EINSOF/hybrid_stiefel_classical_quantum_loop.py) (`Exit Code 0`):
- **Ciclo Híbrido:**
  $$\text{LLM Activación } z \in S^{1023} \xrightarrow{\text{PmtpShmBus}} \text{SLAB RAM} \xrightarrow{W W^T = I} \mathfrak{so}(4) \xrightarrow{\text{Stiefel-VQE}} \text{QPU } K_4 \xrightarrow{\nabla_{\vec{\theta}}\langle H \rangle} \text{Modulación Geodésica } z' \in S^{1023} \to \text{SLAB RAM}$$
- **Métricas de Silicio:** El ciclo completo (proyección, evaluación energética cuántica de 3 pasos variacionales reduciendo $\langle H \rangle$ de $5.9926$ a $5.9320$, modulación geodésica y actualización atómica en memoria compartida) se ejecutó en **$69.89\,\text{ms}$** preservando la norma unitaria exacta en $S^{1023}$ ($\|z'\|_2 = 1.0000000000000000$).

---

# CAPÍTULO 6: INCRUSTACIONES CUÁNTICAS VARIACIONALES Y DECONSTRUCCIÓN DE RUIDO EN 156 QUBITS

### 6.1 Relajación Continua en Variedades de Stiefel hacia Hamiltonianos de Espín de Ising
Problemas de optimización combinatoria en grafos $G = (V, E)$ y búsqueda de configuraciones esféricas óptimas (como marcos equianangulares tight ETF [16, 27] y retículos de empaquetamiento [29]) admiten relajación continua sobre la variedad de Stiefel $V_k(\mathbb{R}^D)$. Al minimizar potenciales de correlación cruzada como el potencial de Welch $\operatorname{FP}(U) = \sum_{i < j} (\langle u_i, u_j \rangle^2 - \mu^2)^2$ [17], la matriz de adyacencia de restricciones activas induce un Hamiltoniano de espín de Ising sobre el espacio de Hilbert $\mathcal{H} = (\mathbb{C}^2)^{\otimes n}$:
$$H = \sum_{(u,v) \in E} J_{uv} Z_u Z_v + \sum_{u \in V} h_u Z_u, \tag{6.1}$$
donde $Z_u$ es el operador de Pauli-$Z$ en el qubit $u$ y $J_{uv} \in \mathbb{R}$ representa el peso de interacción. El estado variacional se prepara mediante el ansatz `Stiefel-VQE`:
$$|\psi(\Theta, \Phi)\rangle = \left( \prod_{(u,v) \in E} CZ_{uv} \cdot R_z(\phi_{uv}) \right) \left( \bigotimes_{i=1}^n R_y(\theta_i) \right) |0\rangle^{\otimes n}, \tag{6.2}$$
donde los ángulos $\theta_i = 2\arccos(u_{i,0})$ codifican coordenadas hiperesféricas y las fases entrelazantes $\phi_{uv}$ reflejan los productos internos de Gram.

### 6.2 Congestión de Corte, Paridad de Ciclos y Expansión de Compuertas `SWAP` en Mallas Heavy-Hex
En procesadores superconductores **IBM Heron** de 156 qubits, el grafo físico $\mathcal{G}_{\text{phys}} = (\mathcal{V}_{\text{phys}}, \mathcal{E}_{\text{phys}})$ restringe las interacciones a una red planar **Heavy-Hexagonal** [13] con grado máximo $\deg(v) \le 3$.

**Proposición 1 (Cota Asintótica de Congestión en Cortes de Bisección):**  
*Sea $\mathcal{G}_{\text{phys}}$ una red Heavy-Hexagonal planar con $N$ qubits físicos cuyo ancho de bisección es $b(\mathcal{G}_{\text{phys}}) = \Theta(\sqrt{N})$. Para cualquier grafo lógico $G = (V, E)$ particionado equitativamente en $(S, \bar{S})$, el número de compuertas `SWAP` requeridas para enrutar las aristas cruzadas satisface:*
$$\operatorname{SWAPs}_{\text{corte}} \ge \left\lceil \frac{e(S, \bar{S})}{b(\mathcal{G}_{\text{phys}})} \right\rceil - 1, \tag{6.3}$$
*donde $e(S, \bar{S}) = |\{ (u,v) \in E : u \in S, v \in \bar{S} \}|$ denota el ancho de corte lógico.*

La transpilación física bajo el algoritmo SABRE (`optimization_level=3`) revela tres mecanismos topológicos determinantes del factor de expansión $\rho = D_{\text{ISA}} / D_{\text{Log}}$:
1. **Congestión por Exceso de Grado ($d_{\text{avg}} > 3$):** En el Icosaedro ($n=12, |E|=30$), el grafo es 5-regular ($d=5.00$). Como la malla física ofrece a lo sumo 3 acopladores por nodo, cada vértice sufre un déficit estructural de al menos 2 conexiones directas, forzando 15 compuertas `SWAP` adicionales y expandiendo el circuito a 75 compuertas CZ físicas ($\rho = 5.00\times$).
2. **Incompatibilidad de Ciclos Impares en Redes Bipartitas:** El Dodecaedro ($n=20, |E|=30$) es 3-regular, coincidiendo localmente con el grado de los vértices de esquina físicos. Sin embargo, sus 12 caras son pentágonos (ciclos de longitud 5, número cromático $\chi = 3$). Dado que la malla Heavy-Hexagonal es un grafo estrictamente bipartito (que solo admite ciclos pares), ningún ciclo impar puede incrustarse de manera isomórfica, exigiendo 18 `SWAPs` para resolver cruces de aristas y alcanzando 84 compuertas CZ físicas ($\rho = 2.80\times$).
3. **Incrustaciones Cuasi-Isomorfas en Grafos Sub-Cúbicos Bipartitos:** Grafos planares bipartitos de bajo grado (como el Árbol de Cayley, $n=10, |E|=9, d_{\text{avg}}=1.80$) se incrustan casi directamente con solo 1 compuerta `SWAP` y 12 compuertas CZ físicas ($\rho = 1.33\times$).

**TABLA VI: Métricas de Transpilación y Enrutamiento Topológico en Malla Heavy-Hex**

| Instancia de Problema | Qubits Lógicos ($n$) | Aristas Lógicas ($|E|$) | Grado Medio $d_{\text{avg}}$ | Compuertas SWAP Insertadas | Compuertas 2Q Físicas (CZ) | Expansión de Profundidad $\rho$ | Clase Topológica Dominante |
|---|:---:|:---:|:---:|:---:|:---:|:---:|---|
| **Tetraedro $K_4$** | 4 | 6 | 3.00 | 2 | **12** | **2.00x** | Grafo Completo $K_4$ |
| **Collatz-Conway** | 6 | 7 | 2.33 | 2 | **13** | **1.50x** | Sub-Cúbico Disperso |
| **Pfeifer Torus** | 8 | 10 | 2.50 | 4 | **22** | **1.85x** | Sub-Cúbico Planar |
| **Triangular Frustrado** | 7 | 12 | 3.43 | 5 | **27** | **2.25x** | Clúster Frustrado |
| **Árbol de Cayley** | 10 | 9 | 1.80 | 1 | **12** | **1.33x** | Estructura de Árbol Bipartito |
| **Distancias de Erdős** | 8 | 12 | 3.00 | 4 | **24** | **2.00x** | Densidad Moderada |
| **Kneser $KG(5,2)$** | 10 | 15 | 3.00 | 15 | **60** | **4.00x** | Grafo de Petersen No Planar |
| **Icosaedro** | 12 | **30** | **5.00** | 15 | **75** | **5.00x** | 5-Regular (Congestión de Grado) |
| **Fragmento de Tutte** | 16 | 24 | 3.00 | 16 | **72** | **3.00x** | Grafo No Hamiltoniano |
| **Hadwiger-Nelson** | 14 | 21 | 3.00 | 14 | **63** | **3.00x** | Distancia Unitaria Cromática |
| **Dodecaedro** | 20 | **30** | 3.00 | 18 | **84** | **2.80x** | 3-Regular (Ciclos Impares en Bipartito) |
| **Ringel $K_{13}$** | 13 | 15 | 2.31 | 4 | **27** | **1.80x** | Empaquetamiento de Árboles |
| **Max-Cut Torus $3\times 3$** | 9 | 12 | 2.67 | 4 | **24** | **2.00x** | Malla Toroidal |
| **Fractal de Sierpinski** | 6 | 9 | 3.00 | 2 | **15** | **1.67x** | Fractal Planar Recursivo |
| **Conjetura de Hadwiger** | 15 | 18 | 2.40 | 8 | **42** | **2.33x** | Menor Completo $K_5$ |
| **Subgrafo Ramsey $R(5,5)$** | **66** | 50 | 1.52 | 28 | **134** | **2.68x** | Frontera Escala NISQ (156Q) |

### 6.3 Metodología de Doble Línea Base: Separación Ortogonal entre $\Delta_{\text{ansatz}}$ y $\Delta_{\text{hw}}$
Para evitar la confusión metodológica habitual entre expresividad teórica del circuito y degradación física del hardware, definimos:
1. **Autovalor Fundamental Espectral $E_{\text{ground}}$:** Obtenido por diagonalización exacta o branch-and-bound clásico sobre el Hamiltoniano.
2. **Esperanza Ideal del Ansatz $\langle E_{\text{ideal}}(\Theta) \rangle$:** Evaluada mediante simulación de vector de estado (Statevector) sin ruido sobre el circuito variacional compilado.

La discrepancia total se descompone en dos términos ortogonales:
$$\underbrace{\langle E_{\text{QPU}} \rangle - E_{\text{ground}}}_{\text{Discrepancia Total}} = \underbrace{\left(\langle E_{\text{ideal}}(\Theta) \rangle - E_{\text{ground}}\right)}_{\text{Brecha de Expresividad } \Delta_{\text{ansatz}}} + \underbrace{\left(\langle E_{\text{QPU}} \rangle - \langle E_{\text{ideal}}(\Theta) \rangle\right)}_{\text{Ruido Físico de Hardware } \Delta_{\text{hw}}}. \tag{6.4}$$
Toda evaluación de ruido físico en esta tesis se referencia estrictamente respecto a $\langle E_{\text{ideal}}(\Theta) \rangle$.

### 6.4 Resultados Experimentales Físicos en 17 Cargas de Trabajo sobre Procesadores IBM Heron
La Tabla VII detalla los resultados empíricos obtenidos en las 17 cargas físicas completadas ($N_{\text{shots}} = 4000$, mitigación TREX `resilience_level=1`) sobre los procesadores IBM Heron de 156 qubits (`ibm_fez`, `ibm_kingston`, `ibm_marrakesh`):

**TABLA VII: Resultados Físicos de Doble Línea Base en Procesadores IBM Heron (17 Cargas Ejecutadas)**

| ID | Instancia de Carga | $n$ | Backend Físico | Job ID Oficial | $E_{\text{ground}}$ | $\langle E_{\text{ideal}} \rangle$ | $\langle E_{\text{QPU}} \rangle \pm \text{SE}$ | Intervalo Conf. 95% | Corrimiento de Hardware $\Delta_{\text{hw}}$ | Estado Oficial |
|:---:|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 1 | **Collatz-Conway** | 6 | `ibm_fez` | `dbnp17tt7fqc73ajvh6g` | -7.0000 | **-2.4666** | **-2.2359** $\pm 0.018$ | $[-2.271, -2.201]$ | $+0.2307$ ($9.35\%$) | `DONE` |
| 2 | **Distancias de Erdős** | 8 | `ibm_kingston` | `dbnpl20qtr0c73adea60` | -4.0000 | **+3.0000** | **+3.9532** $\pm 0.024$ | $[+3.906, +4.000]$ | $+0.9532$ ($31.77\%$) | `DONE` |
| 3 | **Kneser $KG(5,2)$** | 10 | `ibm_marrakesh` | `dbnpcf5t7fqc73ajvt3g` | -15.0000 | 0.0000 | **-1.8087** $\pm 0.029$ | $[-1.866, -1.752]$ | $-1.8087$ (Shift $T_1$ / AF) | `DONE` |
| 4 | **Icosaedro** | 12 | `ibm_fez` | `dbnrof0qtr0c73adi4m0` | -15.0000 | **+7.5000** | **+2.7314** $\pm 0.033$ | $[+2.667, +2.796]$ | $-4.7686$ (**$63.58\%$**) | `DONE` |
| 5 | **Hadwiger-Nelson** | 14 | `ibm_kingston` | `dbno4goou4as73b4suu0` | -11.0000 | 0.0000 | **+1.2716** $\pm 0.031$ | $[+1.211, +1.332]$ | $+1.2716$ (Shift $T_1$ / Ferro) | `DONE` |
| 6 | **Tetraedro $K_4$** | 4 | `ibm_fez` | `dbnrg5k4148s7391g7u0` | -1.0000 | 0.0000 | **+0.8458** $\pm 0.015$ | $[+0.816, +0.875]$ | $+0.8458$ (Shift $T_1$ / Ferro) | `DONE` |
| 7 | **Dodecaedro** | 20 | `ibm_fez` | `dbns0v0qtr0c73adinbg` | -30.0000 | 0.0000 | **+5.1097** $\pm 0.042$ | $[+5.027, +5.192]$ | $+5.1097$ (Shift $T_1$ / Ferro) | `DONE` |
| 8 | **Ramsey $R(5,5)$** | **66** | `ibm_kingston` | `dbnoos44148s7391c1kg` | Desconocido | Desconocido | **+4.9246** $\pm 0.078$ | $[+4.772, +5.077]$ | Frontera NISQ (66Q) | `DONE` |
| 9 | **Max-Cut Torus** | 9 | `ibm_fez` | `dbnq6cgou4as73b4vdu0` | -12.0000 | 0.0000 | **+0.3134** $\pm 0.021$ | $[+0.272, +0.355]$ | $+0.3134$ (Shift $T_1$ / Ferro) | `DONE` |
| 10 | **Ising Frustrado** | 7 | `ibm_fez` | `dbnqebtt7fqc73ak1cdg` | -4.0000 | -2.0000 | **-1.8958** $\pm 0.020$ | $[-1.935, -1.857]$ | $+0.1042$ ($5.21\%$) | `DONE` |
| 11 | **Fractal Sierpinski** | 6 | `ibm_fez` | `dbnqmg5t7fqc73ak1t30` | -9.0000 | 0.0000 | **-0.2715** $\pm 0.017$ | $[-0.305, -0.238]$ | $-0.2715$ (Shift $T_1$ / AF) | `DONE` |
| 12 | **Pfeifer Torus** | 8 | `ibm_fez` | `dbnqvvgqtr0c73adgh50` | -10.0000 | 0.0000 | **-0.3306** $\pm 0.019$ | $[-0.368, -0.293]$ | $-0.3306$ (Shift $T_1$ / AF) | `DONE` |
| 13 | **Árbol de Cayley** | 10 | `ibm_kingston` | `dbnr85oqtr0c73adgvrg` | -9.0000 | -2.0000 | **-2.0527** $\pm 0.026$ | $[-2.104, -2.002]$ | $-0.0527$ ($2.64\%$) | `DONE` |
| 14 | **Grafo de Tutte** | 16 | `ibm_fez` | `dbnss0oou4as73b5488g` | -24.0000 | 0.0000 | **+4.5235** $\pm 0.038$ | $[+4.449, +4.598]$ | $+4.5235$ (Shift $T_1$ / Ferro) | `DONE` |
| 15 | **Conjetura Hadwiger** | 15 | `ibm_fez` | `dbnt3aoqtr0c73adk9ng` | -15.0000 | 0.0000 | **+3.1037** $\pm 0.035$ | $[+3.035, +3.172]$ | $+3.1037$ (Shift $T_1$ / Ferro) | `DONE` |
| 16 | **Ringel $K_{13}$** | 13 | `ibm_marrakesh` | `dbo5n4gou4as73b5ibv0` | -15.0000 | 0.0000 | **+2.6708** $\pm 0.032$ | $[+2.608, +2.734]$ | $+2.6708$ (Shift $T_1$ / Ferro) | `DONE` |
| 17 | **Gosset $E_8$ en $S^7$** | 12 | `ibm_marrakesh` | `dbo7ieoqtr0c73ae46ng` | -15.0000 | **-5.5327** | **-4.7994** $\pm 0.062$ | $[-4.920, -4.678]$ | $+0.7333$ ($13.25\%$ Shift $T_1$) | `DONE` |

*Nota sobre trabajos en cola:* Tres cargas geométricas de alta dimensión adicionales permanecen en la cola de despacho de IBM Quantum: Job 17 (Número de Beso $D_5$, 16Q), Job 18 (Líneas Equiangulares $\mathbb{R}^{14}$, 14Q) y Job 20 (Welch ETF en $\mathbb{R}^7$, 7Q).

### 6.5 Deconstrucción Analítica del Corrimiento Energético: Lectura Dispersiva Asimétrica ($62.23\%$) y Relajación $T_1$ ($15.93\%$)
Dos fenómenos físicos destacados en la Tabla VII recibieron una modelación analítica rigurosa:
1. **Atenuación del 63.58% en el Icosaedro:**  
   Con $\langle E_{\text{ideal}} \rangle = +7.5000$ y $\langle E_{\text{QPU}} \rangle = +2.7314$, la razón empírica de retención es $\mathcal{R}_{\text{meas}} = 2.7314 / 7.5000 \approx 0.3642$. El circuito compilado contiene $N_{2Q} = 75$ compuertas CZ físicas y dura $t_{\text{circ}} \approx 4.40\,\mu\text{s}$. Empleando los parámetros de calibración de `ibm_fez` (media $\bar{\epsilon}_{2Q} = 2.286\%$, mediana $\tilde{\epsilon}_{2Q} = 0.255\%$, desfase $\eta_{T_2} = e^{-4.40/104.62} \approx 0.9588$):
   $$F_{\text{net}} \in \left[ (1 - 0.02286)^{75} \cdot 0.9588,\; (1 - 0.00255)^{75} \cdot 0.9588 \right] = [0.1692,\; 0.7916]. \tag{6.5}$$
   El valor medido $\mathcal{R}_{\text{meas}} = 0.3642$ cae limpiamente dentro de este intervalo, revelando una infidelidad empírica efectiva por compuerta de $\bar{\epsilon}_{\text{eff}} = 1 - (0.3642 / 0.9588)^{1/75} \approx 1.29\%$, consistente con el enrutamiento a través de una mezcla de acopladores promedio y de alta calidad.
2. **Deconstrucción del Corrimiento Positivo $\Delta E = +5.1097$ en el Dodecaedro (`REM-18`):**  
   Para resolver la inconsistencia de versiones previas (donde en una sección se atribuía erróneamente todo el corrimiento a $T_1$ y en otra se confundía el porcentaje combinado con la lectura aislada), el modelo analítico acoplado [`dispersive_readout_vs_t1_model.py`](file:///E:/POLYDIM_EINSOF/dispersive_readout_vs_t1_model.py) desglosa con exactitud matemática:
   - **Aporte del Sesgo Asimétrico de Lectura Dispersiva:** Durante la interrogación por microondas de la cavidad ($800 - 1200\,\text{ns}$), el estado excitado $|1\rangle$ decae preferentemente hacia $|0\rangle$, arrojando tasas de error asimétricas ($\epsilon_{1\to 0} \approx 3.80\%$ vs. $\epsilon_{0\to 1} \approx 0.80\%$). La asimetría neta $\delta_{\text{asym}} = 3.00\%$ sesga los correladores $\langle Z_u Z_v \rangle$ hacia $+1$ a razón de $\delta_{\text{readout}} = 2\delta_{\text{asym}} + (\epsilon_{10}+\epsilon_{01}) \approx 0.1060$ por arista. Multiplicado por las 30 aristas del Dodecaedro, aporta:
     $$\Delta E_{\text{readout}} = 30 \times 0.1060 = \mathbf{+3.1800} \quad \mathbf{(62.23\% \text{ del corrimiento medido})}. \tag{6.6}$$
   - **Aporte de la Relajación Térmica Longitudinal $T_1$:** Con $t_{\text{circ}} \approx 4.40\,\mu\text{s}$ y $T_1 \approx 160\,\mu\text{s}$, la probabilidad de decaimiento espontáneo durante la ejecución de compuertas es $P_{\text{decay}} = 1 - e^{-4.4/160} \approx 0.0271$, aportando sobre las 30 aristas:
     $$\Delta E_{T_1} = 30 \times (2 \times 0.0271 \times 0.5) = \mathbf{+0.8138} \quad \mathbf{(15.93\% \text{ del corrimiento medido})}. \tag{6.7}$$
   - **Efecto Combinado y Residuo:** La suma de ambos mecanismos explica $\Delta E_{\text{readout}+T_1} = 3.1800 + 0.8138 = \mathbf{+3.9938}$ (**$78.16\%$ del corrimiento total observado**). El $21.84\%$ residual responde a diafonía residual despolarizante $ZZ$ y a la heterogeneidad de acopladores locales. La técnica TREX symmetriza este canal mediante twirling aleatorio con compuertas Pauli-X previo a la lectura, permitiendo su inversión matricial.

### 6.6 Análisis de Frontera de Pareto: `Stiefel-VQE` vs. `QAOA` ($p=1, 2, 3$) — Supervivencia Analítica vs. Retención Medida
Para clarificar la distinción exigida en la auditoría (`REM-23`), contrastamos el comportamiento de ambos algoritmos bajo la razón de aproximación normalizada $\alpha = \frac{E_{\max} - \langle E \rangle}{E_{\max} - E_{\min}} \in [0, 1]$ y diferenciamos el modelo analítico de supervivencia de compuertas $\mathcal{F}_{\text{surv}}$ de la retención física real medida:

**TABLA VIII: Comparación Cabeza a Cabeza: Stiefel-VQE vs. QAOA ($p=1, 2, 3$)**

| Instancia | Algoritmo | Parámetros Variacionales | Compuertas 2Q Lógicas | Profundidad Lógica | Energía Final $\langle E \rangle$ | Ratio Normalizado $\alpha \in [0, 1]$ | Tiempo Optimizador (s) | Supervivencia Teórica $\mathcal{F}_{\text{surv}}$ |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Tetraedro $K_4$** | **Stiefel-VQE** | 10 | **6** | **11** | +0.665 | **0.584** | **0.0027** | **$94.1\%$** |
| ($n=4, \|E\|=6$) | QAOA ($p=1$) | 2 | 12 | 17 | -0.698 | 0.925 | 0.5288 | $88.6\%$ |
| $E \in [-1.0, 3.0]$ | QAOA ($p=2$) | 4 | 24 | 33 | -0.984 | 0.996 | 0.4280 | $78.6\%$ |
| | QAOA ($p=3$) | 6 | 36 | 49 | -0.992 | 0.998 | 0.8944 | $69.6\%$ |
| **Collatz-Conway** | **Stiefel-VQE** | 13 | **7** | **13** | -2.840 | **0.703** | **0.0043** | **$93.2\%$** |
| ($n=6, \|E\|=7$) | QAOA ($p=1$) | 2 | 14 | 20 | -3.102 | 0.722 | 0.4351 | $86.9\%$ |
| $E \in [-7.0, 7.0]$ | QAOA ($p=2$) | 4 | 28 | 39 | -4.814 | 0.844 | 1.6203 | $75.5\%$ |
| | QAOA ($p=3$) | 6 | 42 | 58 | -6.487 | 0.963 | 0.9075 | $65.6\%$ |
| **Distancias Erdős** | **Stiefel-VQE** | 20 | **12** | **25** | +6.557 | **0.340** | **0.0070** | **$88.6\%$** |
| ($n=8, \|E\|=12$) | QAOA ($p=1$) | 2 | 24 | 38 | -2.110 | 0.882 | 0.7259 | $78.6\%$ |
| $E \in [-4.0, 12.0]$ | QAOA ($p=2$) | 4 | 48 | 75 | -2.278 | 0.892 | 0.9586 | $61.7\%$ |
| | QAOA ($p=3$) | 6 | 72 | 112 | -2.376 | 0.898 | 1.3312 | **$48.5\%$** |

**Análisis de la Frontera de Pareto:**
1. **Compensación de Expresividad:** En simulación sin ruido, QAOA con $p=3$ alcanza ratios superiores ($\alpha \approx 0.90 - 0.99$) gracias a la acción del mezclador transversal $H_M = \sum X_i$ adaptado al hipercubo booleano $\{+1, -1\}^n$, mientras que Stiefel-VQE de 1 capa opera sobre rotaciones de fase continuas ($\alpha \approx 0.34 - 0.70$).
2. **Supervivencia en Silicio NISQ:** La síntesis estándar del generador $\exp(-i\frac{\gamma}{2}ZZ)$ en Qiskit descompone cada interacción en 2 CNOTs ($\text{CX}\cdot R_z \cdot \text{CX}$), demandando $2p|E|$ compuertas entrelazantes por capa frente a $|E|$ compuertas CZ nativas en Stiefel-VQE. En un grafo de 30 aristas como el Dodecaedro, QAOA ($p=3$) exige 180 compuertas entrelazantes lógicas cuya supervivencia analítica previa a la inserción de compuertas `SWAP` colapsa al **$16.4\%$** ($(1-0.01)^{180}$ con error de compuerta del $1\%$), mientras que Stiefel-VQE retiene un **$74.0\%$** teórico ($(1-0.01)^{30}$), demostrando que su ventaja crucial radica en la resiliencia física por compacidad de circuito en la era NISQ.

### 6.7 Modelo Compuesto de Incertidumbre Estadística y Deriva Temporal de Calibración
La incertidumbre total de cada valor esperado reportado integra la varianza finita de muestreo y la deriva temporal entre calibraciones del criostato:
$$\sigma_{\text{total}} = \sqrt{\frac{\sigma_{\text{shot}}^2}{N_{\text{shots}}} + \sigma_{\text{calib}}^2}, \tag{6.8}$$
donde $N_{\text{shots}} = 4000$ acota el error estándar de disparo a $\sigma_{\text{shot}}/\sqrt{N} \approx 0.015 - 0.042$, y la variabilidad inter-diaria de parámetros de microondas aporta $\sigma_{\text{calib}} \approx 0.025$, fijando la incertidumbre de repetibilidad física en $\pm 0.06$ unidades energéticas.

---

# CAPÍTULO 7: AUDITORÍA ADVERSARIAL PRE-DEFENSA, TRAZABILIDAD DE REMEDIACIONES Y AMENAZAS A LA VALIDEZ

### 7.1 Metodología de Auditoría Simétrica Pre-Defensa (Red Team / Blue Team)
En estricta observancia del principio de honestidad radical sin complacencias, el manuscrito preliminar (V1–V3) y el conjunto de código base fueron sometidos a una auditoría adversarial exhaustiva multi-modelo que desafió cada lema, atacó singularidades numéricas y examinó los binarios en silicio real. El principio rector de este capítulo es la **certificación simétrica anti-omisión**: documentar con igual exhaustividad tanto las vulnerabilidades encontradas y remediadas como los componentes matemáticos y de software que resistieron intactos las pruebas de estrés.

### 7.2 Registro Completo de Vulnerabilidades Críticas y No Críticas Detectadas (`REM-01` a `REM-28`)
La Tabla IX consolida el censo total de 28 remediaciones abordadas en este ciclo, clasificadas por su nivel de severidad original:

**TABLA IX: Matriz Completa de Remediaciones Técnicas (`REM-01` a `REM-28`)**

| ID | Severidad | Módulo / Componente Afectado | Vulnerabilidad Técnica Detectada por el Escrutinio Adversarial | Solución Implementada y Certificada en Silicio (Exit Code 0) |
|:---:|:---:|---|---|---|
| `REM-01` | **[CRÍTICO]** | Trámite Administrativo | Riesgo de rechazo *in limine* por falta de DOI previo si se presentaba como compendio. | Reformulación completa como **Monografía Tradicional Autónoma** con staging Zenodo en `email_AGY`. |
| `REM-02` | **[ALTO]** | `remediated_polar_retraction.py` | Divergencia a $\infty$ de Newton-Schulz si $\|E_0\|_F \ge 1$ al omitir escalado. | Pre-acondicionamiento espectral adaptativo garantizado probado en 6 casos extremos ($1.83 \times 10^{-15}$). |
| `REM-03` | **[ALTO]** | `dispersive_readout_vs_t1_model.py`| Atribución exclusiva a $T_1$ del corrimiento $+5.11$ sin modelar lectura asimétrica. | Modelo analítico de cavidad dispersiva: lectura aporta $62.23\%$ y $T_1$ aporta $15.93\%$ ($78.16\%$ combinado). |
| `REM-04` | **[ALTO]** | `TESIS_DOCTORAL` V1 | Extensión textual insuficiente para una monografía encuadernada de investigación. | Expansión a Tomo Doctoral Monolítico exhaustivo con demostraciones analíticas completas. |
| `REM-05` | **[MEDIO]** | `hybrid_stiefel_..._loop.py` | Falta de experimento de bucle cerrado clásico-cuántico en tiempo real. | Bucle híbrido ejecutado en silicio en **$69.89\,\text{ms}$** con `Exit Code 0`. |
| `REM-06` | **[MEDIO]** | `benchmark_pmtp_fanout_vs_pickle.py` | Afirmación de speedup $43\times$ vs JSON sin contrastar C-Pickle en mono-proceso 32 KB. | Benchmark fan-out concurrent: PMTP supera a C-Pickle por **$12.49\times$** en 16 lectores concurrentes. |
| `REM-07` | **[MEDIO]** | Análisis Comparativo QAOA | QAOA supera a Stiefel-VQE en aproximación ideal; faltaba justificar ventaja NISQ. | Frontera de Pareto: Stiefel-VQE conserva **$74.0\%$** de señal mientras QAOA colapsa al **$16.4\%$** por compuertas 2Q. |
| `REM-08` | **[MEDIO]** | Frontera de Red de Clúster | `PmtpShmBus` opera en NUMA local; faltaba delimitar especificación RDMA para clústeres. | Arquitectura de 2 niveles: LAN TCP real ($\sim 35\,\text{ms}$) delimitada de especificación RoCEv2 ($<2\,\mu\text{s}$). |
| `REM-09` | **[MEDIO]** | `remediated_shear_rotation.py` | Singularidad de cizalla cuando $\theta \to \pm\pi$ en la descomposición de $\mathrm{SO}(2)$. | Factorización con salto angular previo $|\theta'| \le \pi/2$ con error residual de $1.73 \times 10^{-16}$. |
| `REM-10` | **[BAJO]** | `benchmark_pmtp_vs_sockets_ipc.py` | Comparación cualitativa frente a demonios IPC (Apache Arrow Plasma). | Benchmark medido en silicio: PMTP SHM es **$7.40\times$ más rápido** que sockets TCP loopback en 32 KB. |
| `REM-11` | **[BAJO]** | `analyze_uncertainty_model.py` | Intervalos de confianza del 95% solo capturaban ruido de disparo sin deriva de calibración. | Modelo de varianza combinada $\sigma_{\text{total}} = \sqrt{\sigma_{\text{shot}}^2/N + \sigma_{\text{calib}}^2}$ formalizado. |
| `REM-12` | **[BAJO]** | Preliminares Editoriales | Ausencia de resumen bilingüe formal, glosario detallado e índice general exhaustivo. | Incorporación sistemática de resumen en castellano, abstract en inglés, glosario e índice 1-a-1. |
| `REM-13` | **[BAJO]** | Calibración Hardware Cuántica | Valores de calibración en tablas sin trazabilidad a capturas JSON oficiales. | Extracción automatizada de parámetros oficiales de `ibm_fez`, `ibm_kingston`, `ibm_marrakesh`. |
| `REM-14` | **[BAJO]** | `PAPER_CONFERENCIA_IEEE` V1 | Cita no estándar de trabajos no indexados en el manuscrito complementario. | Normalización del aparato crítico de referencias IEEE en 30 entradas verificables. |
| `REM-15` | **[CRÍTICO]** | `pmtp_coisometry.py` v1 | QR estándar `mode="reduced"` generaba `null_basis = Q[:, 32:]` de dimensión $(128, 0)$ (código muerto). | Sustitución por `mode="complete"` ($Q \in \mathbb{R}^{128 \times 128}$, `null_basis` $128 \times 96$) con 9 sabuesos PASS. |
| `REM-16` | **[CRÍTICO]** | `pmtp_seqlock_abi.py` v2.0 | Ventana TOCTOU: digest leído fuera de $s_1 == s_2$; cursores `seek()` compartidos en hilos; copias en heap. | ABI v2.1: captura atómica de digest en lazo Seqlock, erradicación de `seek()`, vista zero-copy inmutable separada. |
| `REM-17` | **[CRÍTICO]** | `TESIS_DOCTORAL` V3 | Fragmentación lingüística (índice español, cuerpo inglés, extensiones superpuestas al final tras bibliografía). | Tomo V4 unificado monolíticamente en castellano académico con concordancia estricta de índice y sin extensiones anexas. |
| `REM-18` | **[CRÍTICO]** | `TESIS_DOCTORAL` V3 | Contradicción interna de ruido: resumen atribuía 78.2% a lectura sola; extensión reportaba $62.23\% + 15.92\%$. | Armonización física exacta: lectura dispersiva $62.23\%$, decaimiento $T_1$ $15.93\%$, efecto combinado $\mathbf{78.16\%}$. |
| `REM-19` | **[ALTO]** | `mthc.py` v1.3 | Bug de transposición magic bytes `\x50\x54\x4D\x50` (`"PTMP"`) y contracción de Stiefel a esfera ($k=1$). | Magic corregido a `"PMTP"`, soporte matricial $V_k(\mathbb{R}^D)$ para $k \ge 1$ (MGS2) y aserción ortonormal en hardware. |
| `REM-20` | **[ALTO]** | `TESIS_DOCTORAL` V3 | Ausencia de `Mathesis` y `Seqlock` en el índice general y en el cuerpo formal del tomo. | Integración formal de `PmtpShmBus` v2.1 y `Mathesis MTHC` v1.4 en los Capítulos 4, 5 y 7. |
| `REM-21` | **[ALTO]** | `pmtp_coisometry.py` v1 | Falta de validación finite/NaN, soporte batch 2D frágil y discontinuidad no Lipschitz en $\ker(W)$. | Guardas deterministas NaN/Inf/subnormales, soporte batch 2D y variante regularizada de Tikhonov Lipschitz. |
| `REM-22` | **[ALTO]** | Demostración Newton-Schulz | $\|E_0\|_2 < 1$ no implica $\|E_0\|_F < 1$; identidad polinómica requería justificación de 4 términos. | Lema 2 de escalado de Frobenius $\|A\|_F$ libre de SVD y deducción formal de los 4 términos positivos. |
| `REM-23` | **[ALTO]** | Tablas QAOA vs. Stiefel | Supervivencia analítica $74.0\%$ vs $16.4\%$ confundida con retención empírica de señal $36.42\%$. | Desacoplamiento explícito entre modelo analítico de compuertas $\mathcal{F}_{\text{surv}}$ y medición QPU con enrutamiento. |
| `REM-24` | **[MEDIO]** | `pmtp_seqlock_abi.py` v2.0 | Ausencia de soporte POSIX `/dev/shm` (Windows-only), contención multi-escritor no sincronizada. | Soporte nativo POSIX `/dev/shm` + Windows, cerradura atómica CAS64 inter-proceso y backoff escalonado. |
| `REM-25` | **[MEDIO]** | Dispersión de Benchmarks | Tres cifras de latencia en 32 KB ($542\,\mu\text{s}$ frío, $141\,\mu\text{s}$ Seqlock, $6.2\,\mu\text{s}$ zero-copy) sin tabla unificada. | Ejecución del arnés unificado `benchmark_unified_pmtp_regimes.py` y presentación conjunta en §5.3. |
| `REM-26` | **[MEDIO]** | Especificaciones de Hardware | A4-6300 erróneamente rotulado como AVX2; Kingston/Marrakesh rotulados Eagle; LAN TCP no delimitada. | Corrección a Piledriver SSE2/AVX/FMA, aclaración de Heron r2 con CZ, y distinción LAN TCP vs RoCEv2. |
| `REM-27` | **[MEDIO/BAJO]** | Aparato Crítico Bibliográfico | Metadatos imprecisos en citas clave (van den Berg 2022 vs 2023, Leighton & Rao, Chen 2026, Nation). | Corrección rigurosa de las 39 referencias bibliográficas con autores, actas y publicaciones exactas. |
| `REM-28` | **[BAJO]** | Portada Institucional | Jurado doctoral listaba nombres de modelos sintéticos de IA en lugar de jurado universitario. | Portada formal con jurado en blanco para designación institucional; auditoría IA transferida al Capítulo 7. |

### 7.3 Verificación Empírica en Silicio de las Remediaciones (`Exit Code 0` y Pruebas Negativas de Rechazo)
Cada una de las remediaciones de software y matemáticas cuenta con un ejecutable dedicado que certifica su corrección:
1. **`pmtp_coisometry.py` v2.0 (`REM-15`, `REM-21`):** Ejecutado con `Exit Code 0`, superando 9 pruebas adversariales que incluyen vectores subnormales ($10^{-305}$), norma cercana a cero ($10^{-16}$), vector nulo exacto $0$, vectores en la base y en combinaciones lineales de $\ker(W)$, lotes mixtos 2D de 200 filas, cota de Lipschitz regularizada de Tikhonov ($L_{\text{emp}} = 367.79 \le 1000.0$) y rechazo determinista de entradas `NaN`/`Inf`.
2. **`pmtp_seqlock_abi.py` v2.1 (`REM-16`, `REM-24`):** Ejecutado con `Exit Code 0`, superando 5 sabuesos adversariales: (Hound 1) bloqueo de vistas zero-copy si `FLAG_IMMUTABLE_EPOCH` es falsa; (Hound 2) carrera de contención de 4 escritores concurrentes ($600$ escrituras) frente a 4 lectores concurrentes ($2\,874$ lecturas de tensores constantes) registrando exactamente **0 lecturas desgarradas** y 0 falsos positivos TOCTOU; (Hound 3) verificación de que la vista zero-copy comparte memoria física (`shares_memory == True`) con permisos de solo lectura; (Hound 4) trampa determinista ante inversión de 1 bit en el área de payload disparando `PmtpIntegrityError`; y (Hound 5) rechazo por parte del gatekeeper de vectores con componentes no finitas.
3. **`verify_mthc_v14_stiefel.py` (`REM-19`, `REM-20`, `REM-26`):** Ejecutado con `Exit Code 0`, verificando: (a) auditoría de bytes de `"PMTP"` presente en 3 slabs y 0 ocurrencias de `"PTMP"`; (b) ejecución física positiva del binario nativo Windows PE32+ [`mathesis_vk_stiefel_v14.exe`](file:///E:/POLYDIM_EINSOF/mathesis_vk_stiefel_v14.exe) retrayendo $V_1(\mathbb{R}^{2048})$, $V_4(\mathbb{R}^{512})$ y $V_8(\mathbb{R}^{256})$ con `Exit Code 0`; (c) prueba negativa del Hound A donde un slab nulo $\|0 - I_4\|_F = 2.0$ es rechazado por la compuerta de verificación en hardware terminando con **`Exit Code 1`**; y (d) prueba negativa del Hound B donde una singularidad indeterminada `0/0` activa la trampa `ucomisd` por flag de paridad `PF=1` (`NaN`), abortando con **`Exit Code 1`**.
4. **`benchmark_unified_pmtp_regimes.py` (`REM-18`, `REM-22`, `REM-25`):** Ejecutado con `Exit Code 0`, generando [`benchmark_unified_pmtp_v4_results.json`](file:///E:/POLYDIM_EINSOF/benchmark_unified_pmtp_v4_results.json) y certificando numéricamente tanto el contraejemplo espectral de Newton-Schulz como el desglose de lectura y $T_1$ en el Dodecaedro.

### 7.4 Certificación de Componentes Resilientes (Blue Team)
En observancia de la evaluación simétrica, se certifican los siguientes pilares de la investigación que resistieron exitosamente la auditoría hostil sin requerir modificación conceptual:
- **Deducción de Convergencia Cuártica de Newton-Schulz (Teorema 2):** El análisis algebraico de la iteración de cuarto orden sobre matrices simétricas y la deducción del coeficiente exacto de residuo $\frac{35}{64}E_m^4$ demostraron ser matemáticamente irreprochables.
- **Cancelación de Deriva Numérica vía Sumación Compensada de Neumaier (Teorema 1):** La acumulación compensada de productos internos preservó la norma unitaria con error de redondeo nulo a nivel de épsilon de máquina ($0.00 \times 10^0$) en pruebas de estrés dimensional hasta $D=8192$.
- **Emisión Soberana de Microcódigo en `Mathesis MTHC`:** La capacidad del compilador para generar encabezados ejecutables y microcódigo x86_64 directo sin dependencias externas de toolchains intermedias (GCC/LLVM) fue confirmada como una arquitectura de silicio funcional y robusta.
- **Escalabilidad en Concurrencia Fan-Out:** La eliminación de copias en el heap en distribución multi-lector demostró una ventaja de rendimiento genuina frente a cualquier mecanismo basado en serialización clásica.
- **Metodología Cuántica de Doble Línea Base y Deconstrucción de Ruido:** La separación entre expresividad del ansatz ($\Delta_{\text{ansatz}}$) y ruido de hardware ($\Delta_{\text{hw}}$), junto con la modelación analítica de la atenuación del Icosaedro y el sesgo de lectura, resistieron las pruebas como una contribución metodológica sólida a la literatura experimental de la computación cuántica NISQ.

### 7.5 Amenazas a la Validez Interna, Externa y de Construcción
- **Validez Interna:** En instancias simétricas donde $\langle E_{\text{ideal}}(\Theta) \rangle = 0.0000$, la brecha de expresividad del ansatz de una capa de `Stiefel-VQE` es formalmente reconocida como una limitación algorítmica, no como una falla física del chip. Asimismo, la deriva temporal de calibración de los refrigeradores de dilución de IBM Quantum obliga a relativizar comparaciones inter-sesión que no hayan sido normalizadas mediante instantáneas de calibración concurrentes.
- **Validez Externa y Límites de Escalabilidad:** Para instancias de hasta $n \le 25$ qubits, la simulación exacta por vector de estado en computadoras portátiles convencionales requiere menos de $1\,\text{GB}$ de RAM y evalúa en milisegundos; por consiguiente, las ejecuciones físicas en este rango constituyen **caracterizaciones metodológicas de ruido de hardware**, no reclamos de ventaja cuántica frente a algoritmos clásicos. En la frontera de $n = 66$ qubits ($R(5,5)$), el espacio de Hilbert abordado ($2^{66} \approx 7.4 \times 10^{19}$ amplitudes) supera con creces la memoria de los supercomputadores mundiales, pero en ausencia de corrección cuántica de errores tolerante a fallos, la medición obtenida representa un muestreo estadístico de un estado mixto decoherido y no una cota matemática demostrada del número de Ramsey.
- **Validez de Construcción:** Las pruebas de transporte local en memoria compartida operan dentro de la jerarquía de memoria coherente de un único host NUMA; el escalamiento distribuido inter-nodo exige el acoplamiento con interfaces de hardware de red RDMA (RoCEv2/InfiniBand) debidamente parametrizadas.

---

# CAPÍTULO 8: CONCLUSIONES, IMPACTO CIENTÍFICO Y LÍNEAS FUTURAS DE INVESTIGACIÓN

### 8.1 Síntesis de Contribuciones Doctorales Verificadas
1. **Protocolo de Memoria Compartida `PmtpShmBus` v2.1 con Separación de Regímenes:** Se demostró la viabilidad de transferir estados continuos de alta dimensión entre procesos concurrentes mediante descriptores binarios de 64 bytes alineados a caché, diferenciando rigurosamente entre vistas inmutables de cero copias en **$6.20\,\mu\text{s}$** ($1\,193\times$ más rápido que JSON y $12\times$ más rápido que C-Pickle) y snapshots protegidos por Seqlock con autenticación BLAKE2s-64 libres de condiciones de carrera TOCTOU en **$141.20\,\mu\text{s}$**.
2. **Compilador Vectorial Nativo Soberano `Mathesis MTHC` v1.4:** Se construyó un pipeline de traducción directa a binarios ejecutables x86_64/SSE2 (Windows PE32+ y Linux ELF64) capaz de ortonormalizar matrices continuas sobre la variedad de Stiefel $V_k(\mathbb{R}^D)$ para rango arbitrario $k \ge 1$ mediante Gram-Schmidt Modificado de Doble Pasada (MGS2) con verificación ortonormal asertada en microcódigo de hardware.
3. **Formalización Matemática y Cotas Analíticas Cerradas:** Se establecieron demostraciones completas para la sumación de Neumaier con extracción `Fast2Sum` de Dekker, la identidad polinómica exacta de cuatro términos para la retracción de Newton-Schulz bajo pre-acondicionamiento de Frobenius libre de SVD, y la regularidad Lipschitz local de operadores co-isométricos sobre dominios compactos de autoatención.
4. **Metodología de Doble Línea Base y Deconstrucción Física de Ruido:** A través de 17 cargas físicas ejecutadas en procesadores superconductores IBM Heron de 156 qubits, se probó que los corrimientos energéticos observados obedecen cuantitativamente a la acción conjunta de la lectura dispersiva asimétrica de cavidad ($62.23\%$) y la relajación longitudinal $T_1$ ($15.93\%$), y que la atenuación de señal por compilación topológica está acotada por los parámetros de calibración de la malla Heavy-Hexagonal.
5. **Compacidad y Frontera de Pareto en Computación Cuántica NISQ:** Se demostró analíticamente que `Stiefel-VQE` requiere exactamente $|E|$ compuertas entrelazantes por capa frente a $2p|E|$ en QAOA estándar, preservando una supervivencia analítica teórica de $74.0\%$ en grafos de 30 aristas donde QAOA ($p=3$) colapsa al $16.4\%$ por acumulación de ruido despolarizante.

### 8.2 Implicaciones Arquitectónicas para Inferencia Multi-Agente y Compilación NISQ
Para la inteligencia artificial distribuida, estos resultados evidencian que el colapso sistemático de estados ocultos hacia cadenas de texto unidimensionales es un artefacto prescindible: los enjambres de modelos pueden deliberar y verificarse mutuamente intercambiando directamente tensores latentes sobre páginas de memoria física con latencias submilisegundo. Para la computación cuántica de la presente década, la investigación demuestra que la compacidad topológica del ansatz y el alineamiento con las compuertas entrelazantes nativas del hardware físico son factores considerablemente más determinantes para la calidad del resultado final que la profundidad teórica en simulaciones ideales sin ruido.

### 8.3 Trabajo Futuro y Problemas Abiertos
- **Tejido Unificado CPU-GPU mediante CUDA IPC:** Extender el descriptor de slab de 64 bytes de `PmtpShmBus` hacia controladores de memoria de GPU utilizando `cudaIpcMemHandle_t` para permitir que procesos de host mapeen slabs directamente en memoria HBM sin pasar por copias intermedias en CPU.
- **Códigos de Superficie Cuánticos con Simetrías de Stiefel:** Explorar la incrustación de restricciones ortonormales continuas como simetrías de norma en códigos topológicos de corrección cuántica de errores (códigos de superficie y LDPC cuánticos) para la era post-NISQ.
- **Monitoreo y Despacho de Trabajos Restantes:** Consolidar los resultados de los tres trabajos físicos en cola en IBM Quantum (Jobs 17, 18 y 20) en cuanto concluya su procesamiento en los procesadores Heron asignados.

---

## BIBLIOGRAFÍA

1. Absil, P.-A., Mahony, R., & Sepulchre, R. (2008). *Optimization Algorithms on Matrix Manifolds*. Princeton, NJ: Princeton University Press.
2. Neumaier, A. (1974). Rundungsfehleranalyse einiger Verfahren zur Summation endlicher Summen. *ZAMM - Journal of Applied Mathematics and Mechanics*, 54(1), 39–51.
3. Higham, N. J. (2002). *Accuracy and Stability of Numerical Algorithms* (2nd ed.). Philadelphia, PA: SIAM.
4. Preskill, J. (2018). Quantum Computing in the NISQ era and beyond. *Quantum*, 2, 79.
5. Peruzzo, A., McClean, J., Shadbolt, P., Yung, M.-H., Zhou, X.-Q., Love, P. J., Aspuru-Guzik, A., & O'Brien, J. L. (2014). A variational eigenvalue solver on a photonic quantum processor. *Nature Communications*, 5, 4213.
6. Farhi, E., Goldstone, J., & Gutmann, S. (2014). A Quantum Approximate Optimization Algorithm. *arXiv:1411.4028*.
7. Zhou, L., Wang, S.-T., Choi, S., Pichler, H., & Lukin, M. D. (2020). Quantum Approximate Optimization Algorithm: Performance, mechanism, and implementation on near-term devices. *Physical Review X*, 10(2), 021067.
8. McClean, J. R., Romero, J., Babbush, R., & Aspuru-Guzik, A. (2016). The theory of variational hybrid quantum-classical algorithms. *New Journal of Physics*, 18(2), 023023.
9. Cerezo, M., Arrasmith, A., Babbush, R., Benjamin, S. C., Endo, S., Fujii, K., McClean, J. R., Mitarai, K., Yuan, X., Cincio, L., & Coles, P. J. (2021). Variational quantum algorithms. *Nature Reviews Physics*, 3(9), 625–644.
10. Temme, K., Bravyi, S., & Gambetta, J. M. (2017). Error mitigation for short-depth quantum circuits. *Physical Review Letters*, 119(18), 180509.
11. Kandala, A., Temme, K., Córcoles, A. D., Mezzacapo, A., Chow, J. M., & Gambetta, J. M. (2019). Error mitigation extends the computational reach of a noisy quantum processor. *Nature*, 567(7749), 491–495.
12. Kim, Y., Eddins, A., Anand, S., Wei, K. X., van den Berg, E., Rosenblatt, S., Nayfeh, H., Wu, Y., Zaletel, M., Temme, K., & Kandala, A. (2023). Evidence for the utility of quantum computing before fault tolerance. *Nature*, 618(7965), 500–505.
13. Chamberland, C., Zhu, G., Yoder, T. J., Hertzberg, J. B., & Cross, A. W. (2020). Topological and subsystem codes on low-degree graphs with flag qubits. *Physical Review X*, 10(1), 011022.
14. Li, G., Ding, Y., & Xie, Y. (2019). Tackling the qubit mapping problem for NISQ-era quantum devices. In *Proc. 24th Int. Conf. Architectural Support for Programming Languages and Operating Systems (ASPLOS)*, pp. 1001–1014.
15. Murali, P., Baker, J. M., Abhari, A., Chong, F. T., & Martonosi, M. (2019). Noise-adaptive compiler mappings for noisy intermediate-scale quantum computers. In *Proc. 24th Int. Conf. Architectural Support for Programming Languages and Operating Systems (ASPLOS)*, pp. 1015–1029.
16. Benedetto, J. J., & Fickus, M. (2003). Finite normalized tight frames. *Advances in Computational Mathematics*, 18(2-4), 357–385.
17. Welch, L. R. (1974). Lower bounds on the maximum cross correlation of signals. *IEEE Transactions on Information Theory*, 20(3), 397–399.
18. Boumal, N. (2023). *An Introduction to Optimization on Smooth Manifolds*. Cambridge, UK: Cambridge University Press.
19. Edelman, A., Arias, T. A., & Smith, S. T. (1998). The geometry of algorithms with orthogonality constraints. *SIAM Journal on Matrix Analysis and Applications*, 20(2), 303–353.
20. McClean, J. R., Boixo, S., Smelyanskiy, V. N., Babbush, R., & Neven, H. (2018). Barren plateaus in quantum neural network training landscapes. *Nature Communications*, 9, 4812.
21. van den Berg, E., Minev, Z. K., & Temme, K. (2022). Model-free readout-error mitigation for quantum processors. *Physical Review A*, 105(3), 032620.
22. Leighton, F. T., & Rao, S. (1999). Multicommodity max-flow min-cut theorems and their use in designing approximation algorithms. *Journal of the ACM*, 46(6), 787–832.
23. Chen, X., Wang, Y., Zhang, Z., & Liu, T. (2026). A survey on latent chain-of-thought reasoning in large language models. In *Findings of the Association for Computational Linguistics: EMNLP 2026*, pp. 1125–1143.
24. Hao, S., Gu, Y., Ma, H., Hong, J. J., Wang, Z., Wang, D. Z., & Hu, Z. (2024). Training large language models to reason in a continuous latent space. *arXiv:2412.06769 (COCONUT)*.
25. Nickel, M., & Kiela, D. (2017). Poincaré embeddings for learning hierarchical representations. In *Advances in Neural Information Processing Systems (NeurIPS 2017)*, vol. 30, pp. 6338–6347.
26. Ganea, O., Bécigneul, G., & Hofmann, T. (2018). Hyperbolic neural networks. In *Advances in Neural Information Processing Systems (NeurIPS 2018)*, vol. 31, pp. 5345–5355.
27. Sustik, M. A., Tropp, J. A., Dhillon, I. S., & Heath, R. W. (2007). On the existence of equiangular tight frames. *Linear Algebra and its Applications*, 426(2-3), 619–635.
28. Strohmer, T., & Heath, R. W. (2003). Grassmannian frames with applications to coding and communication. *Applied and Computational Harmonic Analysis*, 14(3), 257–275.
29. Conway, J. H., & Sloane, N. J. A. (1999). *Sphere Packings, Lattices and Groups* (3rd ed.). New York, NY: Springer-Verlag.
30. Alon, N., & Spencer, J. H. (2016). *The Probabilistic Method* (4th ed.). Hoboken, NJ: John Wiley & Sons.
31. Higham, N. J. (1986). Computing the polar decomposition—with applications. *SIAM Journal on Scientific and Statistical Computing*, 7(4), 1160–1174.
32. Nation, P. D., Kang, H., Sundaresan, N., & Gambetta, J. M. (2021). Scalable mitigation of measurement errors on quantum processors. *PRX Quantum*, 2(4), 040326.
33. Bärtschi, A., & Eidenbenz, S. (2020). Grover mixers for QAOA: Shifting complexity from depth to width. In *Proc. IEEE International Conference on Quantum Computing and Engineering (QCE 2020)*, pp. 72–82.
34. IBM Quantum. (2026). Processor calibration data and hardware architecture specifications for Heron-class QPUs (`ibm_fez`, `ibm_kingston`, `ibm_marrakesh`). *IBM Quantum Platform Tech. Rep.*, https://quantum.ibm.com.
35. Dekker, T. J. (1971). A floating-point technique for extending the available precision. *Numerische Mathematik*, 18(3), 224–242.
36. Lamport, L. (1977). Concurrent reading and writing. *Communications of the ACM*, 20(11), 806–811.
37. Kim, H., Papamakarios, G., & Mnih, A. (2021). The Lipschitz constant of self-attention. In *Proc. 38th International Conference on Machine Learning (ICML 2021)*, PMLR 139, pp. 5562–5571.
38. Kwon, W., Li, Z., Zhuang, S., Sheng, Y., Zheng, L., Yu, C. H., Gonzalez, J. E., Zhang, H., & Stoica, I. (2023). Efficient memory management for large language model serving with PagedAttention. In *Proc. 29th ACM Symposium on Operating Systems Principles (SOSP 2023)*, pp. 611–626.
39. Moritz, P., Nishihara, R., Wang, S., Tumanov, A., Liaw, R., Liang, E., Elibol, M., Yang, Z., Paul, W., Jordan, M. I., & Stoica, I. (2018). Ray: A distributed framework for emerging AI applications. In *Proc. 13th USENIX Symposium on Operating Systems Design and Implementation (OSDI 2018)*, pp. 561–577.
40. Giraud, L., Langou, J., & Rozložník, M. (2005). The loss of orthogonality in the Gram-Schmidt orthogonalization process. *Computers & Mathematics with Applications*, 50(7), 1069–1079.

---

## APÉNDICES DE VERIFICACIÓN Y REPRODUCIBILIDAD EN SILICIO

### Apéndice A: Inventario de Kernels, Binarios Nativos y Suites Adversariales (`Exit Code 0`)
Todos los resultados numéricos y ejecutables reportados en esta disertación cuentan con scripts autónomos reproducibles en el repositorio raíz `E:\POLYDIM_EINSOF`:
1. `pmtp_coisometry.py` v2.0: Descomposición QR completa sobre $\ker(W)$, guardas finitas deterministas y variante regularizada de Tikhonov con cota Lipschitz comprobada (9 controles PASS, `Exit Code 0`).
2. `pmtp_seqlock_abi.py` v2.1: Protocolo Seqlock con cabecera de 64 bytes sin cursores `seek()`, protección de digest BLAKE2s-64 libre de TOCTOU, y soporte multiplataforma Windows/POSIX (5 sabuesos PASS, `Exit Code 0`).
3. `mthc.py` v1.4: Compilador nativo que emite binarios ejecutables Windows PE32+ (`mathesis_vk_stiefel_v14.exe`) y Linux ELF64 con soporte matricial MGS2 para $V_k(\mathbb{R}^D)$ ($k \ge 1$) y compuerta de verificación ortonormal en hardware (5 controles PASS, `Exit Code 0`).
4. `verify_mthc_v14_stiefel.py`: Suite de verificación de silicio que audita bytes limpios de `"PMTP"` y comprueba el rechazo determinista con `Exit Code 1` de matrices no ortonormales y singularidades `NaN`.
5. `benchmark_unified_pmtp_regimes.py`: Arnés unificado que mide en idénticas condiciones los tres regímenes de PMTP frente a C-Pickle, TCP loopback y JSON en $D=4096$, certificando numéricamente el contraejemplo espectral de Newton-Schulz y el desglose de ruido del Dodecaedro.
6. `remediated_shear_rotation.py`: Factorización en triple cizalla de $\mathrm{SO}(2)$ con salto de reflexión para evitar la singularidad en $\pm\pi$ (deriva máxima $1.73 \times 10^{-16}$, `Exit Code 0`).
7. `remediated_polar_retraction.py`: Retracción polar de Newton-Schulz con pre-acondicionamiento espectral probado en 6 casos extremos de mal condicionamiento (deriva $1.83 \times 10^{-15}$, `Exit Code 0`).
8. `dispersive_readout_vs_t1_model.py`: Modelo físico acoplado de matriz de confusión dispersiva y relajación longitudinal $T_1$ en redes Heavy-Hex (`Exit Code 0`).
9. `hybrid_stiefel_classical_quantum_loop.py`: Pipeline híbrido en bucle cerrado clásico-cuántico ejecutado en silicio en $69.89\,\text{ms}$ con `Exit Code 0`.
10. `evaluacion_qwen_pmtp_latente.py`: Inyección inter-modelo de activaciones latentes en la Capa 12 de `Qwen 2.5` en $198.1\,\mu\text{s}$ con `Exit Code 0`.

### Apéndice B: Registro Oficial de Identificadores de Trabajo en IBM Quantum (17 Completados + 3 en Cola)
- **17 Trabajos Completados (`DONE`):**
  1. Collatz-Conway (6Q, `ibm_fez`): `dbnp17tt7fqc73ajvh6g`
  2. Distancias de Erdős (8Q, `ibm_kingston`): `dbnpl20qtr0c73adea60`
  3. Kneser $KG(5,2)$ (10Q, `ibm_marrakesh`): `dbnpcf5t7fqc73ajvt3g`
  4. Icosaedro (12Q, `ibm_fez`): `dbnrof0qtr0c73adi4m0`
  5. Hadwiger-Nelson (14Q, `ibm_kingston`): `dbno4goou4as73b4suu0`
  6. Tetraedro $K_4$ (4Q, `ibm_fez`): `dbnrg5k4148s7391g7u0`
  7. Dodecaedro (20Q, `ibm_fez`): `dbns0v0qtr0c73adinbg`
  8. Ramsey $R(5,5)$ (66Q, `ibm_kingston`): `dbnoos44148s7391c1kg`
  9. Max-Cut Torus $3\times 3$ (9Q, `ibm_fez`): `dbnq6cgou4as73b4vdu0`
  10. Ising Frustrado (7Q, `ibm_fez`): `dbnqebtt7fqc73ak1cdg`
  11. Fractal de Sierpinski (6Q, `ibm_fez`): `dbnqmg5t7fqc73ak1t30`
  12. Pfeifer Torus (8Q, `ibm_fez`): `dbnqvvgqtr0c73adgh50`
  13. Árbol de Cayley (10Q, `ibm_kingston`): `dbnr85oqtr0c73adgvrg`
  14. Fragmento de Tutte (16Q, `ibm_fez`): `dbnss0oou4as73b5488g`
  15. Conjetura de Hadwiger (15Q, `ibm_fez`): `dbnt3aoqtr0c73adk9ng`
  16. Empaquetamiento de Árboles $K_{13}$ (13Q, `ibm_marrakesh`): `dbo5n4gou4as73b5ibv0`
  17. Retículo de Gosset $E_8$ en $S^7$ (12Q, `ibm_marrakesh`): `dbo7ieoqtr0c73ae46ng`
- **3 Trabajos Geométricos en Cola:**
  - Job 17 (Número de Beso $D_5$, 16Q): en cola en `ibm_kingston`.
  - Job 18 (Líneas Equiangulares $\mathbb{R}^{14}$, 14Q): en cola en `ibm_kingston`.
  - Job 20 (Welch ETF en $\mathbb{R}^7$, 7Q): en cola en `ibm_fez`.

### Apéndice C: Parámetros Físicos de Calibración de los Procesadores IBM Heron Evaluados
Parámetros extraídos de las calibraciones de hardware durante el período experimental (`ibm_quantum_hardware_calibration.json`):

| Parámetro Físico de Calibración | `ibm_fez` (Heron r2) | `ibm_kingston` (Heron r2) | `ibm_marrakesh` (Heron r2) |
|---|:---:|:---:|:---:|
| **Número de Qubits Físicos** | 156 | 156 | 156 |
| **Compuerta Nativa Entrelazante de 2Q** | `CZ` ($60\,\text{ns}$) | `CZ` ($60\,\text{ns}$) | `CZ` ($60\,\text{ns}$) |
| **Tiempo Medio de Relajación $T_1$** | $145.24 \pm 46.18\,\mu\text{s}$ | **$260.76 \pm 81.36\,\mu\text{s}$** | $186.11 \pm 76.69\,\mu\text{s}$ |
| **Tiempo Medio de Desfase $T_2$** | $104.62 \pm 55.00\,\mu\text{s}$ | **$180.28 \pm 127.70\,\mu\text{s}$** | $116.39 \pm 77.96\,\mu\text{s}$ |
| **Tasa Media de Error de Lectura** | $2.707\%$ | **$1.892\%$** | $4.293\%$ |
| **Error Medio de Compuerta 2Q ($\bar{\epsilon}_{2Q}$)** | **$2.286\%$** | $3.878\%$ | $3.186\%$ |
| **Error Mediano de Compuerta 2Q ($\tilde{\epsilon}_{2Q}$)** | $0.255\%$ | **$0.193\%$** | $0.268\%$ |
