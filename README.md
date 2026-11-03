# POLYDIM-THEORICAL: Mathematical Foundations Vault & Formal Verification Suite

> **Author:** [Ariel García Traba](https://github.com/AGT1973) (Independent Research / EinsofOS)  
> **Primary Codebase:** [https://github.com/AGT1973/POLYDIM_EinSof](https://github.com/AGT1973/POLYDIM_EinSof)  
> **Canonical Papers & Slides:** [https://huggingface.co/datasets/Polydim-Einsof/POLYDIM-EINSOF-Canonical-Papers-V1550](https://huggingface.co/datasets/Polydim-Einsof/POLYDIM-EINSOF-Canonical-Papers-V1550)  
> **Model Fleet:** [https://huggingface.co/Polydim-Einsof](https://huggingface.co/Polydim-Einsof)  
> **Google AI Developers Thread:** [Breaking the 1D Token Bottleneck via Stiefel Manifold Geometry](https://discuss.ai.google.dev/t/polydim-einsofos-breaking-the-1d-token-bottleneck-via-continuous-stiefel-manifold-geometry/197762)

---

## What is this repository?

**POLYDIM-THEORICAL** is the formal mathematical and theoretical backbone of the [POLYDIM-EINSOF](https://github.com/AGT1973/POLYDIM_EinSof) research initiative.

While `POLYDIM_EinSof` contains the silicon kernels, adapters, and benchmarks, this repository holds the **formal theory**, the **1,736 certified mathematical theorems**, and the **verification tools** that underpin every claim made by the PMTP protocol.

---

## Repository Structure

| Directory | Contents |
|:---|:---|
| `PAPER/` | Full LaTeX sources and hardened PDFs of the main paper and doctoral dissertation |
| `PRESENTACIONES/` | Executive slide decks (.pptx) for academic and industry outreach |
| `CONSTITUCION_TESIS_MANIFESTO/` | Formal manifesto, thesis structure, and constitutional framework |
| `WHITEBOOK/` | EinsofOS Enterprise Whitebook (enterprise systems architecture) |
| `SOTA/` | State-of-the-art comparative analyses and Red Team audits |
| `verification_suite/` | PostgreSQL 16-backed formal theorem verification tooling |
| `tools/` | CLI utilities for theorem ingestion, audit, and certification |
| `docs/` | Academic documentation and implementation guides |

---

## Core Mathematical Framework

### The Stiefel Manifold $\mathrm{St}(k, n)$

The central invariant of POLYDIM is the compact Stiefel manifold:

$$\mathrm{St}(k, n) = \left\{ X \in \mathbb{R}^{n 	imes k} : X^T X = I_k ight\}$$

All hidden state transfers between models in the PMTP protocol are constrained to this manifold, guaranteeing:
* **Energy conservation:** $\lVert Wx Vert_2 = \lVert x Vert_2$
* **Semantic angle preservation:** No dimensional collapse or hallucination drift
* **Neumaier norm error:** $\le 10^{-15}$ (machine precision)

### 1,736 Formal Theorems Certified in PostgreSQL 16

The theorem vault (`boveda_teoremas_1607.json`, `BOVEDA_TEOREMAS_1607_COMPLETA.md`) contains all formally certified theorems spanning:
- Clifford algebra and $so(n)$ Lie algebras
- Riemannian QR polar retraction proofs
- Shannon DPI bounds and information preservation under isometry
- Multi-hop Stiefel chain convergence
- IBM Quantum QPU Intra-Chip Reduction (Section 5, `silicio_real_ibm_kingston_multiproblema.json`)

---

## Preprint & DOI Registry

| Archive | Identifier | URL |
|:---|:---|:---|
| CERN / Zenodo (Primary DOI) | `10.5281/zenodo.21136742` | https://doi.org/10.5281/zenodo.21136742 |
| CERN / Zenodo (Secondary DOI) | `10.5281/zenodo.21209973` | https://doi.org/10.5281/zenodo.21209973 |
| CNRS / HAL Open Science | `hal-05847496v1` | https://hal.science/hal-05847496v1 |
| Center for Open Science (OSF) | `osf.io/za3s7` | https://osf.io/za3s7 |
| JST / Jxiv (Japan) | `Jxiv ID 7040` | https://jxiv.jst.go.jp/index.php/jxiv/authorDashboard/submission/7040 |
| ORCID Verified Record | `0009-0001-2787-6067` | https://orcid.org/0009-0001-2787-6067 |
| Software Heritage (SWHID) | `swh:1:snp:bdea78b3...` | https://archive.softwareheritage.org/swh:1:snp:bdea78b37132a4bd6b67049805cbb6d4472ec2cd |

---

## Citation

```bibtex
@article{garcia_traba_2026_polydim_theory,
  author       = {Garc'ia Traba, Ariel},
  title        = {POLYDIM-EINSOF: Zero-Token Inter-Model Latent Transfer via Stiefel Manifolds and the PMTP Protocol},
  journal      = {EinsofOS Sovereign Research},
  year         = {2026},
  note         = {Theory Vault: \url{https://github.com/AGT1973/POLYDIM-THEORICAL} | Code: \url{https://github.com/AGT1973/POLYDIM_EinSof}},
  doi          = {10.5281/zenodo.21136742}
}
```

**License:** Apache License 2.0 | **Author:** Ariel García Traba (Independent Research / EinsofOS)
