# SOTA Technical Specification: PMTP WAN Phase 10/11 Architecture (Serie 900)
**Document ID:** `SOTA_PMTP_PHASE10_WAN_RAPTORQ_SPEC_2026`  
**Classification:** Master Architecture & Hardware Blueprint  
**Status:** Approved for Serie 900 Prototype  
**Date:** September 2026  

---

## 1. The Information-Theoretic Rectification: RaptorQ (RFC 6330)

### 1.1 The Arithmetic Proof & The Burst Invariant
In a rateless fountain block of $K$ source symbols with $R$ repair symbols, the receiver captures $M$ symbols out of the $N = K + R$ transmitted packets:
$$M = (K + R) - L$$
where $L$ is the number of erased (dropped) packets in that block.
A successful RaptorQ decoding requires:
$$M \ge K + \Delta \implies L \le R - \Delta$$

If a continuous burst erasure of $L_{\text{burst}} = 500$ packets hits a single transmission stream:
1. **Case A (No Interleaving / Single Block Hit):**
   If $K = 4,000$ and $R = 200$ ($5\%$ overhead), then $L_{\max} \approx 200$. A burst of $500$ packets drops $M$ to $3,700 < 4,000$, making decoding mathematically impossible.
   **Rule:** For single-block 500-packet immunity, $R$ must satisfy $R \ge 500 + \Delta$ (minimum $12.5\%$ overhead).
2. **Case B (Cross-Block Matrix Interleaving):**
   If the tensor ($20\text{ MB}$) is divided into $B = 4$ blocks ($K = 4,000$ each), and transmission packets are interleaved in round-robin fashion:
   $$\text{Packet } t \mapsto \text{Block } (t \bmod 4)$$
   A burst of $500$ contiguous lost packets is evenly distributed across the $4$ blocks:
   $$L_b = \frac{500}{4} = 125 \text{ packets per block}$$
   Since $125 \le R - \Delta = 200 - 2 = 198$, **all 4 blocks decode perfectly** with $R=200$ ($5\%$ overhead).

---

## 2. Dual Operational Profiles for PMTP WAN

| Parameter | Profile A: Low-Latency High-Efficiency | Profile B: Extreme Loss Hardened |
|---|---|---|
| **Target Channel** | Private Leased Line / Tier-1 Transit ($P_{\text{loss}} \le 2\%$) | Lossy Commodity Internet ($P_{\text{loss}} \ge 5\%$, severe congestion) |
| **Tensor Size** | $20\text{ MB}$ ($D=10^7$ FP16) | $20\text{ MB}$ ($D=10^7$ FP16) |
| **Blocks ($B$)** | 4 blocks ($5\text{ MB}$ each) | 4 blocks ($5\text{ MB}$ each) |
| **Symbol Size ($T$)** | $1,280\text{ bytes}$ (UDP Payload) | $1,280\text{ bytes}$ (UDP Payload) |
| **Total MTU on Wire** | $1,280\text{ B} + 8\text{ B (UDP)} + 20\text{ B (IP)} + 14\text{ B (Eth)} = 1,322\text{ B} < 1,500\text{ B}$ | $1,322\text{ B} < 1,500\text{ B}$ |
| **Source Symbols ($K$)** | $4,000$ symbols/block | $4,000$ symbols/block |
| **Repair Symbols ($R$)** | $200$ symbols/block ($5\%$ overhead) | $550$ symbols/block ($13.75\%$ overhead) |
| **Burst Resilience** | Up to $190$ pkts/block (or $760$ pkts with 4-way interleaving) | Up to $540$ pkts/block direct (no interleaving required) |
| **Failure Probability ($P_f$)** | $\le 10^{-6}$ with $\Delta = 3$ | $\le 10^{-8}$ with $\Delta = 4$ |

---

## 3. Hardware Transport Topology: PCIe vs. NVLink-C2C

```
[Traditional PCIe Gen5 Topology]
  GPU VRAM (H100 / RTX 4090 / MI300X)
        │
        ▼ (PCIe P2P DMA via BAR1)
  ConnectX-7 NIC / BlueField-3 DPU
        │
        ▼ (RaptorQ Encapsulation over UDP)
  WAN Transit (MTU 1500, Rate Paced)

[NVIDIA Grace-Hopper / Blackwell Architecture (GH200 / GB200)]
  GPU VRAM (HBM3e)
        │
        ▲▼ (NVLink-C2C: 900 GB/s bidirectional coherency)
  Grace CPU LPDDR5X (Unified Memory Space)
        │
        ▲▼ (PCIe Gen5 DMA)
  ConnectX-7 / BlueField-3 NIC
        │
        ▼ (RaptorQ Encapsulation over UDP)
  WAN Transit (MTU 1500, Rate Paced)
```

### Architectural Contract:
1. **PCIe Fabrics:** Enforce GPUDirect RDMA via `nvidia-peermem` (or ROCm `PeerDirect`). Validate that GPU and NIC are located on the same PCIe Root Complex Switch (`nvidia-smi topo -m` matrix shows `NODE` or `PIX`).
2. **NVLink-C2C Fabrics (GH200/GB200):** Hardware does not expose HBM3 directly to PCIe DMA. Memory buffers must be allocated in the unified coherent LPDDR5X space. DMA flows between NIC and LPDDR5X, while the Grace-to-Hopper transfer occurs across the $900\text{ GB/s}$ NVLink-C2C bus with sub-microsecond latency and zero CPU copy overhead.

---

## 4. DPU Hardware Offload: BlueField-3 Integration

To prevent host CPU starvation during 400 Gb/s streaming:
1. **Control Plane:** Handled by UCX / TCP control stream (connection negotiation, symbol parameter $T$, $K$, $R$ distribution).
2. **Data Plane Offload:** BlueField-3 ARM cores (or embedded crypto/compression acceleration units) perform:
   - On-the-fly RaptorQ symbol generation and packetization.
   - Hardware Leaky-Bucket rate pacing matching WAN bottleneck capacity.
   - Ingress symbol reception, Galois Field inactivation solving, and direct memory push into GPU memory.

---

## 5. Summary Verification Criterion for Serie 900

No WAN bridge shall be declared production-ready without executing a continuous 24-hour physical test transferring $10^7$-dimensional FP16 tensors over an emulated WAN channel subject to:
- Continuous background packet loss $q = 3.5\%$.
- Periodic burst drops of $500$ packets every $10\text{ seconds}$.
- Jitter buffer oscillation between $15\text{ ms}$ and $120\text{ ms}$.
- **Acceptance Threshold:** $100\%$ bit-exact tensor reconstruction with 0.0 algebraic drift, verified by Betti-1 simplicial topological check $\beta_1 = 1$.
