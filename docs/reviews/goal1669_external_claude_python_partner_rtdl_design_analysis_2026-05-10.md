# Claude Design Analysis: Python+Partner+RTDL

## Problem Statement and Ownership Boundary

Python excels at model definition, data wrangling, and training orchestration,
but its GIL and garbage collector make it a poor custodian of high-throughput
tensor memory. Partner runtimes (CUDA, Metal, ROCm, Vulkan) own device memory
and scheduling queues that Python cannot directly address. RTDL bridges the
two: it holds the contract that lets Python describe work while the partner
executes it, without either side reaching into the other's internals.

### Why This Architecture Exists

The core tension is lifetime mismatch. Python objects are reference-counted and
may be collected at any GC cycle. Device buffers must outlive the GPU kernels
that read them, which can be several scheduler ticks behind the CPU. A single
ownership model cannot satisfy both; RTDL exists to enforce the boundary
explicitly rather than by convention.

### Responsibility Split

| Layer | Owns | Must Not Own |
|---|---|---|
| **User Python** | Tensor shapes, dtypes, graph topology, training loop control flow | Raw device pointers, synchronization primitives, buffer lifetimes beyond the current Python frame |
| **RTDL** | Allocation descriptors, refcount tokens issued to Python, fence/event handles, the canonical lifetime registry | Execution scheduling, kernel dispatch, device-side allocators |
| **Partner runtime** | Device memory pages, kernel queues, hardware fences, DMA engines | Python object graph, RTDL's descriptor table |

### Memory Ownership and Lifetime

RTDL issues an opaque handle to Python. The handle carries a refcount managed
by RTDL, not by CPython. When Python drops the last reference, it calls back
into RTDL, which checks whether any in-flight partner work still holds the
buffer. The partner runtime is never consulted about Python lifetimes; RTDL is
the sole arbiter of when a deallocation request is safe to forward.

### Synchronization

Python must not poll hardware fences directly. It submits a completion token
request to RTDL; RTDL coordinates with the partner to return a waitable object.
The partner must not block on Python-side locks.

### Reduced-Copy vs. True Zero-Copy

Reduced-copy means the data crosses the Python/native boundary once, staged
through a RTDL-managed pinned buffer. True zero-copy means the partner maps
memory the Python side can describe by address without any staging copy. This
requires that Python never move or resize the buffer after handing the address
to RTDL, a guarantee CPython cannot make for heap-allocated objects. Claims of
zero-copy must document which allocation path provides this stability
guarantee.

## Partner Landscape

| Partner | Kernel Ownership | Python Overhead | Ecosystem Fit | Integration Complexity |
|---|---|---|---|---|
| **PyTorch** | Low — ops are black-box | Medium | Excellent | Low |
| **CuPy** | Medium — NumPy-compatible ops | Low | Good | Low |
| **Numba** | High — JIT to PTX | Very Low | Moderate | Medium |
| **RAPIDS** | Low — cuDF/cuML ops | Medium | Good for tabular | Low–Medium |
| **Custom CUDA/C++** | Full | Minimal | N/A | High |

### PyTorch

Strong autograd and operator fusion make it the default for research, but RTDL
sits outside the tensor-op abstraction; you inherit PyTorch's memory model with
limited ability to customize kernel dispatch.

### CuPy

Closest drop-in for NumPy-heavy RTDL pipelines. Exposes `RawKernel` for custom
PTX injection, giving moderate control without a full C++ build system. Best
for array-centric workloads with occasional custom ops.

### Numba

JIT-compiles Python to CUDA PTX at function level. Ideal when RTDL logic lives
in Python loops that must run on-device; kernel ownership is highest among
pure-Python options. Cold-start compilation cost is the main liability.

### RAPIDS

Optimized for structured/tabular data (`cuDF`, `cuML`, `cuGraph`). Valuable if
RTDL preprocessing is the bottleneck; less relevant for unstructured or custom
numerical kernels.

### Custom CUDA/C++

Maximum performance and control with no abstraction tax. Appropriate when
RTDL's computational pattern does not map to any existing framework primitive.
Cost: separate build pipeline, `ctypes`/`pybind11` glue, and maintenance
burden.

### Recommendation

**CuPy** for moderate control with minimal friction; **Custom CUDA/C++** when
performance requirements exhaust framework primitives.

## Pluggable Partner Architecture and First Partner Recommendation

### Architecture

RTDL's native engine exposes exactly one memory contract: a Buffer Descriptor
struct returned after every primitive call (`run_ray_anyhit`,
`run_grouped_sum`, etc.).

```c
typedef struct RTDLBufferDesc {
    void*    device_ptr;      // raw CUDA/CPU pointer
    int64_t  shape[RTDL_MAX_DIMS];
    int64_t  strides[RTDL_MAX_DIMS];
    int      ndim;
    uint8_t  dtype;           // RTDL_DTYPE_INT32, _FLOAT32, etc.
    int      device_index;
    uint64_t stream;          // CUDA stream on which the write is complete
    uint8_t  ownership;       // RTDL_OWN_MANAGED | RTDL_OWN_BORROWED | RTDL_OWN_EXTERNAL
} RTDLBufferDesc;
```

The Python layer wraps this descriptor and implements three interop protocols
simultaneously: `__dlpack__` / `__dlpack_device__`,
`__cuda_array_interface__`, and `__array_interface__` (for CPU/Embree
results). A partner consumes whichever protocol it natively understands.

Capability negotiation happens at Python bind-time, not at allocation time.
When a user registers a partner, RTDL queries it with `rtdl.partner.probe()`.

```python
caps = rtdl.partner.probe("torch")
# -> {"dlpack": True, "cuda_array_interface": True, "in_place_write": True, "stream_ordering": "cuda_event"}
```

RTDL uses `stream_ordering` to decide whether to insert a
`cudaStreamWaitEvent` before handing off the buffer or to pass the raw stream
handle and let the partner order itself. If neither is supported, RTDL falls
back to `cudaStreamSynchronize` before export, which is slower but safe.

Memory ownership follows three modes. `RTDL_OWN_MANAGED` means RTDL allocated
the buffer and will free it when the DLPack capsule destructor fires.
`RTDL_OWN_BORROWED` means the user passed in a pre-allocated partner tensor;
RTDL writes into it and never frees it. `RTDL_OWN_EXTERNAL` is reserved for
shared IPC handles across processes. The Python `RTDLResult` object refuses to
double-free: ownership transfer is atomic and tracked with a flag cleared at
first `__dlpack__` call.

Fallback behavior: if the requested partner is absent, RTDL downgrades
gracefully. GPU results fall back to a NumPy copy via `cudaMemcpy` and a
deprecation warning is emitted. CPU/Embree results skip the partner entirely
and return plain NumPy arrays. No exception is raised; the user receives valid
data on every code path.

Failure modes: a mismatched stream raises `RTDLStreamConflictError` at
descriptor handoff, not silently at downstream kernel launch. Dtype mismatches
between a borrowed tensor and RTDL's computed output raise
`RTDLDtypeMismatchError` before any write occurs. Both errors are catchable and
documented; neither corrupts device memory.

### First Partner Recommendation: PyTorch

The first partner should be **PyTorch**, not CuPy or JAX.

Against CuPy: CuPy's `__cuda_array_interface__` is well-suited for
database-style reductions, but CuPy lacks scatter/gather primitives, autograd,
and graph neural network integrations that make RTDL commercially meaningful
for robotics and spatial ML. Validating the architecture against the easiest
interop target defers the hard work.

Against JAX: JAX's functional-purity model forbids in-place writes to
externally-owned buffers. The `RTDL_OWN_BORROWED` mode, writing RTDL output
directly into a caller-allocated tensor without a copy, is architecturally
central to zero-copy performance. JAX cannot participate in that model without
a CPU bounce or a callback workaround that reintroduces the copies RTDL is
trying to remove.

Why PyTorch wins: PyTorch's caching allocator is the most aggressive memory
manager in the Python GPU ecosystem. If RTDL can write into a PyTorch-allocated
tensor, synchronize on the correct stream, and hand ownership back without
triggering an illegal memory access or a double-free, the architecture is
proven industrial-grade. PyTorch also directly enables the highest-value
downstream workloads, including `ann_candidate_search`, robot collision
screening, and spatial GNN pipelines, on day one. CuPy should serve as the
secondary validation target in CI, confirming that
`__cuda_array_interface__` is not accidentally PyTorch-specific, but PyTorch is
the load-bearing first partner.

## Testing, Conformance, and Phased Adoption Plan

A partner-ready RTDL cannot be declared credible on design alone. Each
capability claim must be backed by a reproducible test, a passing conformance
gate, or an explicit deferral with a stated condition. The following structure
governs what ships, when, and under what evidence requirements.

### Conformance Tests (Blocking)

These tests must pass before any external partner integration is permitted. No
exceptions.

- **Schema round-trip conformance.** Every declared RTDL node type must
  serialize to its canonical form and deserialize without loss.
- **Engine-neutrality assertions.** The same RTDL document must produce
  semantically equivalent output across all supported execution backends.
- **Version compatibility matrix.** Each RTDL version must include a formal
  compatibility declaration against prior versions.
- **Null and boundary behavior.** All optional fields must have documented
  fallback semantics, and conformance tests must cover absent, null, and
  out-of-range values explicitly.

### Integration Tests (Staged)

Integration tests operate at the system boundary and gate promotion between
roadmap phases.

- **Phase 1 (Internal only):** Single-backend integration tests running against
  the primary engine. Focus on correctness, not performance.
- **Phase 2 (Controlled partner preview):** Multi-backend integration tests
  with a designated partner running their own workloads against a frozen RTDL
  version.
- **Phase 3 (Public readiness):** Full integration test suite published,
  reproducible in a partner's own environment with documented prerequisites.

### Roadmap Phases and Claim Boundaries

| Phase | What Is Internal | What Can Be Public | What Must Stay Blocked |
|---|---|---|---|
| 0 — Design | All | Problem framing only | Any performance or compatibility numbers |
| 1 — Alpha Engine | All test results | Schema specification draft | Partner-readiness language |
| 2 — Controlled Preview | Raw benchmark data | API surface and versioning policy | Broad compatibility claims |
| 3 — Public Beta | Nothing | Integration test suite | Production SLA commitments |
| 4 — GA | — | Full documentation and results | Claims not yet covered by Phase 3 evidence |

### Claims That Must Remain Blocked

The following must not appear in any partner-facing material until the named
evidence exists:

- **Production-ready** until Phase 4 gate passes with at least one external
  production deployment on record.
- **Engine-agnostic** until multi-backend conformance tests pass on two or more
  distinct engines independently.
- **Backward compatible** until the version compatibility matrix covers at
  least two consecutive RTDL versions with test coverage.
- **Any latency or throughput figure** until benchmarks are run under
  documented, reproducible conditions and reviewed for methodology.

### Final Decisions

**1. Partner choice: supported.** RTDL should not pick one partner and couple
to it permanently. The DLPack plus CUDA Array Interface bridge is the design.
Users may use PyTorch, CuPy, or any conforming consumer. PyTorch is the primary
reference; CuPy is the validation target.

**2. Stable partner ABI: required at v2.0, not before.** The `__dlpack__` and
`__cuda_array_interface__` contracts should be considered unstable through the
prototype phases. Stability should be declared only when partner-ready RTDL is
formally published.

**3. Zero-copy: a claim boundary, not a default assumption.** Zero-copy is a
verified, testable property. It should be asserted only when confirmed by exact
transfer-count evidence on the exact subpath.

**4. Public vs. internal at first:** the interop-facing Python protocols may
become public before the lower-level allocator hook, pointer export layer, and
lowering utilities. Those lower layers should remain internal until the design
is stable enough to carry semantic-versioning obligations.
