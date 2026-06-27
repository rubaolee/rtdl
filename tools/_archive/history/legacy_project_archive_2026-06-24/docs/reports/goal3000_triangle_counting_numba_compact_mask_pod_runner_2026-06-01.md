# Goal3000: Triangle Counting Numba Compact Mask Pod Runner

## Purpose

Goal2999 added the source-level triangle-counting app wiring for the generic v2.6 Numba `compact_mask_i64` continuation. Goal3000 prepares a pod runner that executes that app wrapper on real CUDA arrays and records CPU-oracle parity.

The runner is intentionally an app-level witness-row compaction proof. It does not claim the scalar triangle-counting fast path is faster, and it does not replace the v2.5 primitive-first fused RTDL summary.

## Runner

`scripts/goal3000_triangle_counting_numba_compact_mask_pod_runner.py`

The runner:

- generates deterministic `candidate_row_ids:int64` and `valid_triangle_mask:bool`;
- copies both columns to Numba CUDA device arrays;
- calls `run_triangle_counting_v2_6_numba_compact_mask_preview(...)`;
- cross-checks `partner_mask_indices(..., partner="numba")`;
- compares compacted candidate ids and original indices against a CPU oracle;
- writes a JSON artifact with source commit, dirty status, toolchain, GPU, and claim flags.

## Boundary

- CUDA pod runtime evidence is still required.
- The underlying generic primitive already passed L4 conformance in Goal2997.
- Goal3000 must not authorize release, public speedup wording, whole-app speedup wording, RT-core speedup wording, true-zero-copy wording, or a triangle-counting whole-app claim.
