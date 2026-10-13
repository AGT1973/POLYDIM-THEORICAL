"""
POLYDIM Academia.edu Asset Packager
Prepares structured upload packages for https://www.academia.edu/
"""

import os
import sys
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from media_formatter import MediaFormatter
from outreach_db import queue_publication

def prepare_academia_package():
    formatter = MediaFormatter()
    
    title = "POLYDIM: High-Dimensional Native Tensor Passing ($S^{D-1}$) and Clifford Geometric Intelligence"
    
    abstract_en = """
Modern multi-agent architectures predominantly serialize high-dimensional continuous latent states (D >= 10^4) into 1D discrete text tokens (JSON/REST), introducing significant latency overhead and causing irreversible geometric entropy degradation pursuant to the Data Processing Inequality (DPI). 

In this work, we introduce POLYDIM, an open-source, mathematically unified framework for native continuous multi-agent cognition. POLYDIM eliminates the 1D text bottleneck by executing direct tensor message passing (PMTP) across shared physical memory slabs constrained to the Riemannian hyperspherical manifold S^(D-1). Rotations and state transformations are governed by Clifford algebra rotors, ensuring exact isometry and numerical stability. 

Empirical benchmarks across varied silicon classes (local AMD APU, Cloud NVIDIA GPU, and Google TPU v3) demonstrate sub-millisecond tensor exchange latencies (1.1 ms) and 350x throughput improvements over conventional JSON parsing pipelines, adhering strictly to a dynamic, hardware-agnostic Silicon Contract (CUDA C++20, Triton, and Rust Safe-SIMD).
"""

    abstract_es = """
Las arquitecturas multi-agente contemporáneas colapsan estados latentes continuos de alta dimensión (D >= 10^4) a tokens de texto 1D discretos (JSON/REST), introduciendo una sobrecarga masiva de latencia y una degradación irreversible de entropía geométrica según el Teorema de Procesamiento de Información (DPI).

Presentamos POLYDIM, un marco unificado para la cognición continua nativa entre agentes de IA. POLYDIM erradica el cuello de botella del texto 1D mediante el paso directo de tensores en memoria compartida física (PMTP) sobre la variedad riemanniana hipersférica S^(D-1). Las rotaciones y transformaciones de estado se rigen por rotores de álgebra de Clifford, garantizando isometría exacta y estabilidad numérica.

Los benchmarks empíricos en diversas clases de silicio (AMD APU local, NVIDIA GPU y TPU v3) demuestran latencias de intercambio sub-milisegundo (1.1 ms) y una aceleración de 350x frente a pipelines tradicionales de serialización JSON, cumpliendo un Contrato de Silicio dinámico y agnóstico (CUDA C++20, Triton y Rust Safe-SIMD).
"""

    keywords = [
        "Hyperdimensional Computing",
        "Vector Symbolic Architectures",
        "Geometric Deep Learning",
        "Clifford Algebra",
        "Riemannian Manifolds",
        "Multi-Agent Communication",
        "Data Processing Inequality",
        "Hardware-Software Co-Design",
        "Shared Memory PMTP",
        "Non-Tokenized AI"
    ]

    package = formatter.generate_academia_edu_package(
        title=title,
        abstract_en=abstract_en,
        abstract_es=abstract_es,
        keywords=keywords,
        pdf_file="E:\\POLYDIM-THEORICAL\\PAPER\\polydim_theory.pdf"
    )

    out_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "READY_TO_PUBLISH", "05_ACADEMIA_EDU_UPLOAD_PACKAGE.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(package, f, indent=2, ensure_ascii=False)

    queue_publication({
        "title": title,
        "topic": "PAPER_THEORY",
        "channel": "ACADEMIA_EDU",
        "content_raw": abstract_en,
        "media_paths": "E:\\POLYDIM-THEORICAL\\PAPER\\polydim_theory.pdf",
        "status": "QUEUED"
    })

    print(f"Academia.edu upload metadata package generated at: {out_file}")

if __name__ == "__main__":
    prepare_academia_package()
