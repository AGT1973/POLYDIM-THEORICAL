# Guía de auditoría de código — POLYDIM V26150 (Documento Canónico de Cátedra)

## Instrucciones para el alumno

En cada ejercicio se indica:
- **Archivo**: dónde está el problema.
- **Líneas**: zona concreta que deben leer.
- **Contexto**: qué intenta hacer esa parte del programa.
- **Error detectado**: qué comportamiento está mal.
- **Su trabajo**: analizar la causa y proponer/codificar una solución.

No se proporciona la solución.

---

# ARCHIVO 1 — `polydim_v26150_monolito.py`

## ERROR 01 — Entrada X con dimensiones incorrectas puede romper la función
* **Archivo:** `polydim_v26150_monolito.py`
* **Línea:** 387
* **Función:** `retract_stiefel()`
* **Contexto:** Obtiene dimensiones mediante `D, K = X.shape` esperando 2D.
* **Error:** Desempaqueta `X.shape` antes de comprobar que sea 2D (1D o 3D lanzan excepción no controlada).
* **Su trabajo:** Determinar entradas que producen el fallo y localizar por qué no llega a validaciones posteriores.

## ERROR 02 — No se comprueba que X pertenezca a Stiefel
* **Archivo:** `polydim_v26150_monolito.py`
* **Líneas:** 387–397
* **Función:** `retract_stiefel()`
* **Contexto:** Manifold Stiefel exige $X^T X \approx I$.
* **Error:** Valida límites y finitud pero no comprueba $X^T X \approx I$.
* **Su trabajo:** Identificar consecuencias de aceptar X fuera de Stiefel.

## ERROR 03 — No se comprueba que Z sea tangente
* **Archivo:** `polydim_v26150_monolito.py`
* **Líneas:** 387–397
* **Contexto:** Espacio tangente exige $X^T Z + Z^T X \approx 0$.
* **Error:** Solo valida `Z.shape == X.shape`.
* **Su trabajo:** Construir Z no tangente y analizar el comportamiento.

## ERROR 04 — Dos recorridos completos de memoria antes de calcular
* **Archivo:** `polydim_v26150_monolito.py`
* **Líneas:** 395–396
* **Contexto:** Comprobación de finitud sobre X y Z.
* **Error:** Recorre X y Z completos (5.12 GB cada uno para $D=10^7, K=64$) antes del cálculo.
* **Su trabajo:** Analizar tráfico de memoria generado antes de computar.

## ERROR 05 — `np.hstack()` crea otra copia enorme
* **Archivo:** `polydim_v26150_monolito.py`
* **Línea:** 399
* **Contexto:** `XZ = np.hstack((X, Z))` para formar $[X|Z]$.
* **Error:** Duplica memoria en DRAM (~10.24 GB adicionales para $D=10^7, K=64$).
* **Su trabajo:** Calcular el pico de memoria viva acumulado.

## ERROR 06 — Se calcula un Gram más grande de lo necesario
* **Archivo:** `polydim_v26150_monolito.py`
* **Líneas:** 399–403
* **Contexto:** `Gram2K = XZ.T @ XZ` y posterior extracción de $G, S, T$.
* **Error:** Calcula matriz $2K \times 2K$ completa ignorando simetría de bloques.
* **Su trabajo:** Identificar información redundante calculada.

## ERROR 07 — Regularización silenciosa de autovalores
* **Archivo:** `polydim_v26150_monolito.py`
* **Líneas:** 405–410
* **Contexto:** `lambda = max(lambda, 1e-15)`.
* **Error:** Modificación silenciosa con umbral absoluto sin registro en métricas.
* **Su trabajo:** Analizar diferencia matemática con el autovalor original.

## ERROR 08 — Se forma explícitamente la inversa de G
* **Archivo:** `polydim_v26150_monolito.py`
* **Líneas:** 409–410
* **Contexto:** Construcción explícita de `Ginv`.
* **Error:** Inversa densa afecta estabilidad cuando $G$ está mal condicionada.
* **Su trabajo:** Estudiar impacto del condicionamiento en $1/\lambda$.

## ERROR 09 — El escalado llega demasiado tarde
* **Archivo:** `polydim_v26150_monolito.py`
* **Líneas:** 399–443
* **Contexto:** Control de paso extremo mediante `tau`.
* **Error:** $T = Z^T Z$ se evalúa antes de escalar, produciendo overflow/underflow temprano y rompiendo $(Z, \text{step}) \sim (\alpha Z, \text{step}/\alpha)$.
* **Su trabajo:** Demostrar por qué el escalado de `step` no rescata $Z^T Z$.

## ERROR 10 — `np.linalg.solve()` puede terminar en excepción
* **Archivo:** `polydim_v26150_monolito.py`
* **Línea:** 456
* **Contexto:** `np.linalg.solve(M, RHS)`.
* **Error:** Si $M$ es singular, lanza excepción cruda en vez de Status controlado.
* **Su trabajo:** Probar singularidad en $M$.

## ERROR 11 — El resultado hereda el dtype de X
* **Archivo:** `polydim_v26150_monolito.py`
* **Línea:** 466
* **Contexto:** `out = np.empty_like(X)`.
* **Error:** Hereda `int32`, `bool`, etc., truncando cálculo continuo.
* **Su trabajo:** Probar entrada `int32` y documentar pérdida de información.

## ERROR 12 — Se puede truncar silenciosamente el resultado
* **Archivo:** `polydim_v26150_monolito.py`
* **Línea:** 468
* **Contexto:** Asignación `out[:] = X @ Ax + Z @ Az`.
* **Error:** Truncamiento implícito a entero con retorno `Status.OK`.
* **Su trabajo:** Comprobar comportamiento con enteros.

## ERROR 13 — `gram_drift` describe un resultado anterior
* **Archivo:** `polydim_v26150_monolito.py`
* **Líneas:** 471–491
* **Contexto:** Cálculo de defectos y fallback QR.
* **Error:** Tras QR se recalcula `ortho_defect` pero no `gram_drift`.
* **Su trabajo:** Identificar desfase temporal entre ambas métricas.

## ERROR 14 — El fallback puede fallar y aun así devolver OK
* **Archivo:** `polydim_v26150_monolito.py`
* **Líneas:** 479–501
* **Contexto:** Fallback QR de emergencia.
* **Error:** Si el resultado post-QR sigue degradado, retorna `Status.OK` sin re-auditar.
* **Su trabajo:** Probar fallo post-fallback.

---

# ARCHIVO 2 — Suite de pruebas (`polydim_v26150_monolito.py`)

## ERROR 15 — La suite dice “16+” pero ejecuta 14
* **Líneas:** 504–629
* **Contexto / Error:** Anuncia 16+ checks físicos pero ejecuta exactamente 14.

## ERROR 16 — Pruebas sólo generan tangentes horizontales
* **Líneas:** 563–570
* **Contexto / Error:** Fuerza $X^T Z = 0$, omitiendo tangentes generales $X^T Z + Z^T X = 0$.

## ERROR 17 — Pruebas verifican ortogonalidad, no la retracción correcta
* **Líneas:** 571–620
* **Contexto / Error:** No hay Oracle analítico. Un stub $Y=X$ obtiene 14/14 PASS.

## ERROR 18 — El test de fallback no comprueba el fallback
* **Líneas:** 616–619
* **Contexto / Error:** Verifica `Status.OK` pero no `fallback_engaged == True`.

## ERROR 19 — El test de subnormales no prueba POLYDIM
* **Líneas:** 613–614
* **Contexto / Error:** Ejecuta multiplicación NumPy en host sin invocar C++/Rust/CUDA/Triton.

## ERROR 20 — El test de alta dimensión usa 0.1% del máximo
* **Líneas:** 580–590
* **Contexto / Error:** Evalúa $D=10\,000$ frente a $D=10\,000\,000$ anunciado.

---

# ARCHIVO 3 — `kernel_cpp_v26150.cpp.txt`

## ERROR 21 — Suma compensada no evita overflow en multiplicación
* **Líneas:** 95–113 (`dot_neumaier`)
* **Error:** `a[i] * b[i]` desborda antes de que Neumaier compense la suma.

## ERROR 22 — Vector no nulo detectado como cero
* **Líneas:** 151–154 (`sphere_project`)
* **Error:** $x_i^2$ underflowea a 0 para $10^{-200}$, retornando `ZERO_VECTOR`.

## ERROR 23 — Escritura "Transactional" deja output a medias
* **Líneas:** 159–166
* **Error:** Escribe en `out` antes de detectar subnormal en posiciones posteriores.

## ERROR 24 — Subnormal confundido con no representable
* **Líneas:** 161–164
* **Error:** Trata `FP_SUBNORMAL` como `POLYDIM_UNREPRESENTABLE_OUTPUT`.

## ERROR 25 — Tangencia determinada con tolerancia absoluta
* **Líneas:** 190–193 (`sphere_transport`)
* **Error:** $|x^T v| \le 10^{-12}$ permite vectores normales pequeños.

## ERROR 26 — Entrada finita produce Inf/NaN con Status OK
* **Líneas:** 195–220
* **Error:** Denominador $1 + \cos\theta \to 0$ en antipodales genera `Inf`/`NaN` con `POLYDIM_OK`.

## ERROR 27 — Validador PMTP C++ acepta `ndim=0`
* **Líneas:** 224–234
* **Error:** Solo rechaza `ndim > 4`, aceptando `ndim=0`.

---

# ARCHIVO 4 — `kernel_rust_v26150.rs.txt`

## ERROR 28 — `zip()` oculta diferencias de longitud
* **Líneas:** 115–129 (`dot_neumaier`)
* **Error:** Trunca silenciosamente en el slice más corto.

## ERROR 29 — Rust sufre overflow/underflow previo en $x \cdot y$
* **Línea:** 120
* **Error:** Multiplicación no protegida antes de Neumaier.

## ERROR 30 — Backend Rust anunciado incompleto
* **Archivo completo**
* **Error:** No implementa `sphere_transport` ni retracción Stiefel.

---

# ARCHIVO 5 — `kernel_cuda_v26150.cu.txt`

## ERROR 31 — Función CUDA principal no calcula nada
* **Líneas:** 212–229 (`polydim_stiefel_retract_cuda_v26150`)
* **Error:** Valida argumentos y retorna `POLYDIM_OK` sin escribir `d_out`.

## ERROR 32 — Kernels auxiliares nunca son llamados
* **Líneas:** 81–208 y 212–229
* **Error:** No hay lanzamientos `<<<...>>>` en el entry point.

## ERROR 33 — Falta matriz final $D \times K$
* **Líneas:** 184–229
* **Error:** No existe kernel que evalúe $X A_x + Z A_z$.

## ERROR 34 — Discrepancia de regularización CUDA vs Python
* **Líneas:** 81–133
* **Error:** CUDA usa 0 para $\lambda \le 10^{-15}$ mientras Python fuerza $10^{-15}$.

---

# ARCHIVO 6 — `polydim_triton_kernel_v26150.py`

## ERROR 35 — Tensor no contiguo tratado como contiguo
* **Líneas:** 39–53
* **Error:** Indexación lineal directa `x_ptr + offsets` ignora strides.

## ERROR 36 — No valida tamaño de `out`
* **Líneas:** 56–76
* **Error:** Asume `out.numel() >= x.numel()`.

## ERROR 37 — `.item()` fuerza sincronización CPU-GPU
* **Línea:** 67
* **Error:** Destruye pipeline streaming asíncrono.

## ERROR 38 — Norma torch frágil en valores extremos
* **Línea:** 67
* **Error:** Desborde en norma cuadrática torch antes de Triton.

## ERROR 39 — Operaciones prometidas ausentes
* **Líneas:** 5–13
* **Error:** Anuncia Clifford Transport y PMTP pero solo incluye proyección.

---

# ARCHIVO 7 — HardwareProbe (`polydim_v26150_monolito.py`)

## ERROR 40 — C++/Rust disponibles sin validar implementación
* **Líneas:** 253–340
* **Error:** Detección por nombre `glob` sin verificar símbolos exportados.

## ERROR 41 — Backend seleccionado no gobierna la ejecución
* **Líneas:** 350–501
* **Error:** `retract_stiefel()` ejecuta incondicionalmente NumPy.

## ERROR 42 — Telemetría reporta backend inventado
* **Líneas:** 350–499
* **Error:** Refleja la cadena de texto solicitada sin verificar ejecución real.

---

# ARCHIVO 8 — PMTP Shared Memory (`polydim_v26150_monolito.py`)

## ERROR 43 — `offset` negativo provoca crash nativo (SIGSEGV)
* **Líneas:** 215–221
* **Error:** Falta guarda `offset >= 0`.

## ERROR 44 — Falta validación de alineación 8 bytes
* **Líneas:** 215–221
* **Error:** Permite `offset=1` con float64.

## ERROR 45 — Acepta `dtype=object`
* **Líneas:** 215–221
* **Error:** Permite objetos Python no serializables en IPC binario.

## ERROR 46 — `close()` oculta `BufferError`
* **Líneas:** 223–235
* **Error:** Asigna `_mmap_obj = None` aunque el mmap siga abierto en SO.

---

# ARCHIVO 9 — PMTP Descriptor (`polydim_v26150_monolito.py`)

## ERROR 47 — Versión se lee pero no se valida
* **Líneas:** 145–175
* **Error:** `unpack()` ignora discrepancias de versión.

## ERROR 48 — Shape decimal se trunca silenciosamente
* **Líneas:** 112–140
* **Error:** `int(2.9) -> 2` rompe round-trip `pack/unpack`.

---

# ARCHIVO 10 — CLI (`polydim_v26150_monolito.py`)

## ERROR 49 — Argumentos CLI ignorados
* **Líneas:** 632–641
* **Error:** `--bench`, `--D`, `--K` no controlan la ejecución del benchmark.

---

# ARCHIVO 11 — Documentación (`readme_first.md`)

## ERROR 50 — Versiones contradictorias
* **Líneas:** 1–16
* **Error:** Paquete V26150 con código y símbolos V1350/1.3.5.

## ERROR 51 — Anuncio de CholeskyQR3 inexistente
* **Línea:** 16
* **Error:** Anuncia CholeskyQR3 pero el código implementa `np.linalg.qr`.
