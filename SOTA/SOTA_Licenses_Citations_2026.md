### 1. DLPack (Zero-Copy)
*   **Official License**: Apache License 2.0
*   **Academic Citation**: There is no specific peer-reviewed academic paper for DLPack. It is standard to cite the official repository or documentation.
    ```bibtex
    @misc{dlpack,
      author = {DLPack Contributors},
      title = {DLPack: Open In-Memory Tensor Structure},
      url = {https://dmlc.github.io/dlpack/latest/},
      year = {2026}
    }
    ```
*   **Credit Requirements**: Under Apache 2.0, you must include the original copyright notice and a copy of the license in any redistributed code. Academic credit relies on citing the project website.

### 2. OpenMP (C++ Multithreading)
*   **Official License**: OpenMP is an API specification, not a software product, so it does not have a software license. The implementations are licensed individually (e.g., LLVM/Clang OpenMP under MIT/NCSA, GCC `libgomp` under GPLv3 with GCC Runtime Library Exception).
*   **Academic Citation**: Cite the API specification from the OpenMP Architecture Review Board corresponding to the version used.
    ```bibtex
    @manual{openmp,
      title        = {OpenMP Application Programming Interface Specification},
      author       = {{OpenMP Architecture Review Board}},
      year         = {2024},
      url          = {https://www.openmp.org/specifications/}
    }
    ```
*   **Credit Requirements**: No licensing requirement for simply using the API. In the thesis, explicitly mention the compiler and runtime version (e.g., GCC, LLVM) used for the OpenMP implementation.

### 3. OpenBLAS & Intel oneMKL (Numpy's underlying BLAS/LAPACK)
#### OpenBLAS
*   **Official License**: BSD 3-Clause License
*   **Academic Citation**:
    ```bibtex
    @misc{openblas,
      author = {Zhang, Xianyi and Kroeker, Martin and others},
      title = {OpenBLAS: An optimized {BLAS} library},
      howpublished = {\url{https://www.openblas.net/}},
    }
    ```
*   **Credit Requirements**: BSD 3-Clause requires retaining the copyright notice, this list of conditions, and the disclaimer in the source code or documentation.

#### Intel oneMKL
*   **Official License**: Intel Simplified Software License (ISSL) - Free for academic and commercial use.
*   **Academic Citation**: Cited as software, no specific paper.
    ```bibtex
    @manual{onemkl,
      title        = {Intel® oneAPI Math Kernel Library (oneMKL)},
      author       = {{Intel Corporation}},
      url          = {https://www.intel.com/content/www/us/en/developer/tools/oneapi/onemkl.html}
    }
    ```
*   **Credit Requirements**: Ensure that if oneMKL includes third-party software, their respective licenses are respected as per `third-party-software.txt`. No royalty fees.

### 4. PyTorch & Triton
#### PyTorch
*   **Official License**: BSD 3-Clause License
*   **Academic Citation**: Cite the NeurIPS 2019 paper.
    ```bibtex
    @inproceedings{paszke2019pytorch,
      title={PyTorch: An Imperative Style, High-Performance Deep Learning Library},
      author={Paszke, Adam and others},
      booktitle={Advances in Neural Information Processing Systems 32},
      year={2019}
    }
    ```
*   **Credit Requirements**: Standard BSD 3-clause requirements (retain copyright notice and disclaimer).

#### OpenAI Triton
*   **Official License**: MIT License
*   **Academic Citation**: Cite the MAPL 2019 paper.
    ```bibtex
    @inproceedings{tillet2019triton,
      title={Triton: an intermediate language and compiler for tiled neural network computations},
      author={Tillet, Philippe and Kung, Hai-Tao and Cox, David},
      booktitle={Proceedings of the 3rd ACM SIGPLAN International Workshop on Machine Learning and Programming Languages},
      pages={10--19},
      year={2019}
    }
    ```
*   **Credit Requirements**: Include the original MIT copyright notice and permission notice in any copies or substantial portions of the software.

### 5. Rust Standard Library
*   **Official License**: Dual-licensed under the MIT License and Apache License 2.0.
*   **Academic Citation**: Cite "The Rust Programming Language" book or the official language website.
    ```bibtex
    @book{klabnik2023rust,
      title={The Rust Programming Language},
      author={Klabnik, Steve and Nichols, Carol},
      year={2023},
      publisher={No Starch Press}
    }
    ```
*   **Credit Requirements**: Comply with either MIT or Apache 2.0 notice requirements depending on which license path you choose for your usage. Generally requires preserving the `COPYRIGHT` notice.
