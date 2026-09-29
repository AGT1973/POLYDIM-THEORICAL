# POLYDIM WHITEBOOK: LA INGENIERÍA DEL CONSENSO NATIVO
**Guía Pedagógica para Arquitectos de Swarms IA**

## 1. El Problema del Colapso 1D
Tradicionalmente, los clústeres multi-agente usan REST/JSON. Al serializar un tensor de 10,000 dimensiones a texto, el sistema choca de frente con la Data Processing Inequality (DPI). El 60% del tiempo de cómputo se pierde en el Embedding y Decoding autorregresivo.

## 2. La Falacia de la Sincronización Pura
Muchos intentos de "Zero-Copy" en memoria compartida (Shared Memory / RDMA) fracasan porque confunden **Consistencia de Búfer** con **Vida del Objeto**.

### El Error del Puntero Suicida (Use-After-Free)
Imagina que el Agente A tiene un puntero al tensor en memoria compartida.
El Agente A intenta bloquear la memoria: `active_ops.fetch_add(1)`.
Sin embargo, milisegundos antes, el Agente B destruyó la memoria compartida (Garbage Collection). El incremento de `active_ops` ocurre sobre un objeto *que ya no existe*. 
**Lección:** Un puntero crudo no puede proteger su propio ciclo de vida. 

## 3. La Solución POLYDIM: Jerarquía de 4 Capas
Para construir un enjambre robusto, la arquitectura requiere:
1. **Stable Handle Registry (Ownership):** Python y Rust se comunican no por punteros de memoria, sino por un ID entero (Handle). Rust verifica el ID en un registro seguro (`HashMap<Handle, Arc>`).
2. **Live Reference (Lifetime):** Al existir el `Arc` (Reference Count atómico externo), la memoria física jamás será destruida mientras la operación ocurra.
3. **Máquina de Estados 2-Slot SPSC (Consistency):** Una vez asegurada la existencia de la memoria, se usan atómicos (`Acquire/Release`) sobre dos ranuras para garantizar que nunca se lea algo mientras se escribe.
4. **Control de Épocas (Freshness):** El lector guarda un `last_seq` y descarta activamente la basura lógica (`seq <= last_seq`), asegurando monotonicidad absoluta.
