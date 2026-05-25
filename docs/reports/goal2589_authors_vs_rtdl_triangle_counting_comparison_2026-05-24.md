# Goal2589 Authors-Code vs RTDL Triangle-Counting Comparison

Date: 2026-05-24

Status: internal same-pod comparison. This document does not authorize public
speedup wording.

## Environment

| Field | Value |
| --- | --- |
| Pod | `ssh root@203.57.40.104 -p 10001 -i ~/.ssh/id_ed25519` |
| Working key actually present on this Mac | `~/.ssh/id_ed25519_rtdl_codex` |
| Hostname | `fc75fca4648a` |
| GPU | NVIDIA RTX A5000 |
| Authors code | `/root/rtdl_python_only/scratch/external/RT-Graph/tc` |
| Workloads | deterministic K4-clique binary edge lists under `/root/rtdl_python_only/build/goal2589_more_probes` |

The authors code was rebuilt twice by changing
`rt_tc/include/config.h::RTTC_METHOD`:

- `RTTC_METHOD=0`: list-intersection / 1A2.
- `RTTC_METHOD=1`: hashmap / 2A1.

Both `bs_tc` and `rt_tc` consume this shared compile-time selector.

## Timing Contract

The timing contracts are different:

- Authors `rt_tc` reports graph preprocessing, CSR conversion, graph-to-RT
  conversion, ray computation, BVH build, and OptiX trace. It does not report
  Python-style app orchestration or RTDL primitive construction costs.
- Authors `bs_tc` reports graph preprocessing, CSR conversion, optional 2A1
  preprocessing, and CUDA counting.
- RTDL reports Python edge loading, Python RT-Graph contract construction,
  benchmark-owned geometry lowering, generic OptiX backend run time, and native
  phase timing inside the summary primitive.

Therefore, the most meaningful comparisons are separated below.

## Pure RT Trace

This compares only authors `rt_tc` trace time against RTDL native traversal
time inside the app-agnostic summary primitive.

| Workload | Method | Count | Authors `rt_tc` trace ms | RTDL native traversal ms | RTDL / authors |
| --- | --- | ---: | ---: | ---: | ---: |
| K4 x 10,000 | 1A2 | 40,000 | 0.061 | 0.090 | 1.48x |
| K4 x 10,000 | 2A1 | 40,000 | 0.056 | 0.083 | 1.49x |
| K4 x 50,000 | 1A2 | 200,000 | 0.148 | 0.270 | 1.83x |
| K4 x 50,000 | 2A1 | 200,000 | 0.117 | 0.191 | 1.64x |
| K4 x 100,000 | 1A2 | 400,000 | 0.284 | 0.441 | 1.55x |
| K4 x 100,000 | 2A1 | 400,000 | 0.146 | 0.284 | 1.95x |

Conclusion: RTDL traversal is close in order of magnitude, but authors
specialized RT traversal remains about `1.5-2.0x` faster on these K4 probes.

## RT Lowering Plus Backend

This compares authors `rt_tc` graph-to-RT conversion + ray computation + BVH +
trace against RTDL benchmark-owned geometry lowering + generic OptiX
`run_backend`.

| Workload | Method | Authors RT-lowering+backend ms | RTDL geometry+backend ms | RTDL / authors |
| --- | --- | ---: | ---: | ---: |
| K4 x 10,000 | 1A2 | 2.329 | 22.628 | 9.72x |
| K4 x 10,000 | 2A1 | 11.111 | 27.569 | 2.48x |
| K4 x 50,000 | 1A2 | 8.368 | 156.959 | 18.76x |
| K4 x 50,000 | 2A1 | 71.496 | 161.746 | 2.26x |
| K4 x 100,000 | 1A2 | 26.124 | 303.333 | 11.61x |
| K4 x 100,000 | 2A1 | 58.354 | 331.093 | 5.67x |

Conclusion: after the follow-up optimizations, RTDL still loses most clearly in
Python/NumPy lowering, especially for 1A2. The 2A1 gap is smaller but still
significant at large scale.

## Broader Reported Phase Sum

For authors `rt_tc`, this sums reported phases:
`TC Preprocessing + CSR + graph-to-RT conversion + ray computation + BVH + trace`.
For RTDL, this uses benchmark-reported `total`.

| Workload | Method | Authors `rt_tc` phase sum ms | RTDL total ms | RTDL / authors |
| --- | --- | ---: | ---: | ---: |
| K4 x 10,000 | 1A2 | 302.410 | 259.736 | 0.86x |
| K4 x 10,000 | 2A1 | 314.132 | 276.231 | 0.88x |
| K4 x 50,000 | 1A2 | 407.437 | 1569.971 | 3.85x |
| K4 x 50,000 | 2A1 | 381.812 | 1539.519 | 4.03x |
| K4 x 100,000 | 1A2 | 342.187 | 3185.847 | 9.31x |
| K4 x 100,000 | 2A1 | 387.067 | 3244.977 | 8.38x |

Conclusion: at 10k K4, RTDL looks competitive in broad phase-sum terms because
authors graph preprocessing has a large fixed cost on this synthetic workload.
At 50k and 100k, RTDL is clearly slower overall because Python contract
construction dominates.

## CuPy Partner Follow-Up

After the initial authors comparison, the benchmark gained an optional CuPy
partner for the app-owned RT-Graph contract construction. This is not a native
RTDL engine specialization: the partner handles graph preprocessing and emits
generic RTDL inputs.

Rows below are medians of three warm RTDL+CuPy app runs on the same pod. The
authors rows remain the previously recorded phase sums from the same K4 inputs.
The comparison is still internal because the timing contracts differ and the
workloads are synthetic K4 probes, not the paper SNAP datasets.

| Workload | Method | Authors `rt_tc` phase sum ms | RTDL+CuPy total ms | RTDL+CuPy / authors |
| --- | --- | ---: | ---: | ---: |
| K4 x 10,000 | 1A2 | 302.410 | 19.421 | 0.06x |
| K4 x 10,000 | 2A1 | 314.132 | 13.661 | 0.04x |
| K4 x 50,000 | 1A2 | 407.437 | 91.623 | 0.22x |
| K4 x 50,000 | 2A1 | 381.812 | 83.132 | 0.22x |
| K4 x 100,000 | 1A2 | 342.187 | 171.575 | 0.50x |
| K4 x 100,000 | 2A1 | 387.067 | 162.544 | 0.42x |

The important conclusion is architectural, not a public speed claim. Once the
slow graph contract is moved to a GPU partner, the RTDL path becomes dominated
by generic geometry packing, OptiX scene preparation, and host/device transfer
boundaries. That is exactly the Python+partner+RTDL design pressure this
benchmark is supposed to expose.

Against the pre-partner RTDL path on K4 x 100,000, the same code family changed
from multi-second totals to sub-200 ms totals:

| Method | No-partner RTDL total ms | RTDL+CuPy total ms | Improvement |
| --- | ---: | ---: | ---: |
| 1A2 | 3553.406 | 171.575 | 20.7x |
| 2A1 | 3466.177 | 162.544 | 21.3x |

These rows support the internal statement that CuPy is the right partner for
this benchmark's slow app-owned preprocessing. They still do not authorize
public wording that RTDL beats RT-Graph.

## Authors `bs_tc` Reference Rows

These are CUDA binary-search/hashmap baselines from the authors code. The
reported phase sum is `TC Preprocessing + CSR + optional BSTC preprocessing +
BSTC counting`.

| Workload | Method | Authors `bs_tc` phase sum ms | Authors count kernel ms | Count |
| --- | --- | ---: | ---: | ---: |
| K4 x 10,000 | 1A2 | 558.032 | 0.322 | 40,000 |
| K4 x 10,000 | 2A1 | 498.510 | 0.037 | 40,000 |
| K4 x 50,000 | 1A2 | 475.315 | 0.175 | 200,000 |
| K4 x 50,000 | 2A1 | 503.800 | 0.019 | 200,000 |
| K4 x 100,000 | 1A2 | 457.737 | 0.035 | 400,000 |
| K4 x 100,000 | 2A1 | 497.053 | 0.027 | 400,000 |

The kernel-only rows are extremely small and noisy on these synthetic K4
workloads, so they should not be used as standalone public claims.

## Main Conclusion

RTDL now has a faithful Python+RTDL expression of both RT-Graph triangle-counting
decompositions, with app-agnostic native summary primitives and correct
same-input results. With pure Python preprocessing it is not
performance-competitive with the authors specialized C++/CUDA/OptiX
implementation at large scale. With the CuPy partner, the app-owned
preprocessing gap is largely removed on the synthetic K4 probes, but the result
still requires review before any public performance wording.

The remaining gap is not the RT core traversal itself. The gap is the
Python-owned graph contract construction and Python/NumPy lowering path in the
no-partner configuration; after the CuPy partner path, the next gap is
partner-to-RTDL lowering and scene/query buffer transfer. A future serious
performance push should move geometry packing toward partner-resident columns or
lower-copy/zero-copy buffer handoff while preserving the rule that native RTDL
engine APIs remain graph-agnostic.

## Claim Boundary

Authorized internally:

- Same-input counts match for authors `bs_tc`, authors `rt_tc`, and RTDL 1A2/2A1
  mappings on the K4 workloads listed here.
- RTDL traversal is within the same order of magnitude as authors RT trace on
  these synthetic K4 probes.
- RTDL whole-app performance is still slower at larger K4 scales because
  Python preprocessing/lowering dominates.
- RTDL+CuPy removes most of the app-owned preprocessing bottleneck on the
  synthetic K4 probes and is the correct internal next direction for this
  benchmark.

Not authorized:

- Public speedup wording.
- Claiming RTDL beats the RT-Graph authors implementation.
- Claiming SNAP/paper dataset reproduction from these synthetic K4 rows.
- Treating the compatibility-patched authors build as an unmodified artifact.
