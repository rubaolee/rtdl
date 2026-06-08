# Choosing A Partner For Custom Logic

Status: current v2.10 source-tree guidance.
This is not a release tag, package-install promise, or broad speedup claim.

Use this page when the RTDL primitive is only part of your program and you need
custom GPU or CPU-side continuation after RTDL emits flags, counts, witnesses,
or typed columns.

## The Rule

1. Use the RTDL primitive first when it exactly expresses the work.
2. Choose the partner explicitly when the remaining work is custom logic.
3. Treat benchmark reference implementations as recommendations, not hidden
   dispatch rules.
4. Publish performance only with same-contract evidence.

RTDL is not an automatic optimizer for arbitrary partner code. If you write a
CuPy RawKernel, a Numba CUDA kernel, a C++ extension, or ordinary NumPy code,
that continuation is your application code unless RTDL ships and reviews that
exact generic contract.

RTDL does not accelerate arbitrary Numba or CuPy programs. It accelerates the
specific RTDL primitive call and any reviewed generic continuation contract you
explicitly choose.

## Quick Choice

| Need | Usually choose | Why |
| --- | --- | --- |
| Existing array algebra, scans, masks, reductions, or library operations | CuPy | CuPy is mature for CUDA arrays and has strong library coverage. |
| Custom CUDA-style element, compaction, grouped reduction, argmin, argmax, or row-stream continuation written in Python syntax | Numba | Numba lets RTDL provide generic kernels without requiring a separate CUDA C++ build. |
| A fused RTDL primitive already returns the exact scalar or summary you need | RTDL primitive | Avoid partner launches and copies when the engine can finish the generic contract directly. |
| CPU reference, debugging, or deterministic small input | NumPy / CPU reference | Easier to inspect and compare. |
| Custom C/C++ or CUDA extension owned by the app | App extension | RTDL does not forbid this, but it is not an RTDL partner speedup claim. |

## CuPy Strengths

Use CuPy when your continuation is naturally array-oriented:

- vectorized arithmetic;
- device arrays that feed common CUDA-array operations;
- RawKernel code when you want CUDA-C-like control;
- strong CUDA-core baselines for fairness against RTDL/OptiX;
- same-contract references for benchmark rows where CuPy is already measured.

CuPy is especially useful when the non-RT part is a regular GPU data-parallel
program and the app author wants direct control of the kernel.

## Numba Strengths

Use Numba when your continuation is a custom generic kernel that RTDL can expose
as a reusable partner contract:

- compact-mask continuations;
- grouped argmin or argmax;
- global argmax over score columns;
- segmented min, max, count, or sum style continuations;
- small custom kernels that should stay in Python source rather than CUDA C++.

The current v2.10 lane makes Numba first-class for selected generic continuation
contracts and records Numba/reference coverage for all promoted benchmark apps.
Numba is not automatically faster than CuPy. It wins only when the contract,
launch shape, and data residency are good for that workload.

## Benchmark Lessons

| Benchmark family | Current lesson |
| --- | --- |
| RayDB-style grouped summaries | Prefer fused RTDL primitive summaries when available; use Numba for custom grouped min/max style continuations that are not already fused. |
| Spatial RayJoin-style joins | Prefer RTDL scalar count/parity or first-hit/nearest-boundary primitives when they express the answer; Numba now covers the PIP/LSI/overlay scalar-count reference rows for users who need Python-source custom CUDA logic. On the bounded public-CDB PIP scalar-count row, CuPy is still the faster current partner baseline; RTDL/OptiX is the clear winner for the LSI/overlay scalar-count rows. |
| Triangle counting | Prefer the native scalar count path for the scalar answer; use explicit `--optix-graph-mode native` for current native timing probes; Numba compact-mask is useful for candidate-row continuation, not a replacement for the scalar primitive. |
| Hausdorff distance | The current performance winner is the RTDL/OptiX active-frontier path; CuPy grouped-grid remains a strong CUDA-core baseline; Numba paths are correctness and contract evidence, not the default performance recommendation. |
| Barnes-Hut-style force studies | CuPy remains the faster measured force-vector partner path overall; Numba now provides a no-RawKernel block-reduction reference for the exact-force continuation. |
| RTNN-style nearest-neighbor studies | RTDL fixed-radius ranked summaries and the `prepared_optix_ranked_summary` app mode are the current executable front door; use CuPy for CUDA-core baseline rows and treat partners as explicit experiments unless same-contract timing wins. |
| RT-DBSCAN-style clustering | RTDL provides fixed-radius/core-summary primitives; Numba now has measured prepared-repeat component-continuation coverage, while CuPy remains a useful baseline/opponent. |

## Claim Boundary

Allowed wording:

```text
This program uses RTDL for the RT-shaped primitive and Numba for the selected
generic continuation, with evidence from the named benchmark artifact.
```

Blocked wording:

```text
RTDL accelerates arbitrary Numba or CuPy programs.
```

When in doubt, write down the primitive, backend, partner, hardware, dataset,
script, commit, and result contract. If those details are missing, call the path
compatible or experimental rather than performance-ready.

## Programmatic Guidance

The learner docs and benchmark matrix are mirrored by advisory metadata:

```python
import rtdsl as rt

for row in rt.current_benchmark_adequacy():
    if row["app"] == "spatial_rayjoin":
        print(row["current_recommended_path"], row["current_partner_role"])
```

The metadata does not auto-select or run a partner. It returns current
recommendation context, adequacy status, evidence paths, AMD/HIPRT readiness,
and claim boundaries so apps can show a clear explanation before the user
chooses a partner.

## See Also

- [Benchmark Partner Reference Matrix](benchmark_partner_reference_matrix.md)
- [Partner Acceleration Boundaries](../partner_acceleration_boundaries.md)
- [Backend Maturity](../backend_maturity.md)
- [Research Benchmark Apps](../../examples/v2_0/research_benchmarks/README.md)
