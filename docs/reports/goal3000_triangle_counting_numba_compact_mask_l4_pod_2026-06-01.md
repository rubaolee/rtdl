# Goal3000: Triangle Counting Numba Compact Mask L4 Pod Evidence

## Result

Goal3000 passed on an NVIDIA L4 pod.

The run executed the Goal2999 triangle-counting app wrapper over real Numba CUDA device arrays:

- source commit: `addde78dc109d205cc1592b06abfbc3c1d8f92b5`
- source dirty status: empty
- GPU: `NVIDIA L4, 565.57.01`
- rows: `1,000,000`
- selected rows: `150,571`
- operation: `compact_mask_i64`
- app mode: `v2_6_numba_compact_mask_preview`
- neutral handoff status: `accept`
- selected candidate ids match CPU oracle: true
- original indices match CPU oracle: true
- `partner_mask_indices(..., partner="numba")` cross-check matches CPU oracle: true

Artifact:

`docs/reports/goal3000_triangle_counting_numba_compact_mask_l4_pod_2026-06-01.json`

## Toolchain Note

The first pod attempt failed because `numba-cuda` was installed into a `--target`
directory and Python did not automatically process `_numba_cuda_redirector.pth`.
That made `from numba import cuda` resolve to the legacy in-tree Numba CUDA module,
which then failed on this driver/toolkit pair:

- without MVC: `CUDA_ERROR_UNSUPPORTED_PTX_VERSION`, PTX 8.7 vs driver PTX 8.6;
- with MVC: missing legacy `ptxcompiler` / `cubinlinker` modules.

The fix was to explicitly activate `_numba_cuda_redirector` in
`src/rtdsl/numba_partner_continuation.py` and in the pod runner before importing
`numba.cuda`. The successful artifact records:

`/root/rtdl_goal2991_v26_pod/.pydeps_v26_numba_cuda/numba_cuda/numba/cuda/__init__.py`

as the active CUDA module path.

## Boundary

This evidence proves app-level v2.6 wiring for triangle-counting-style witness-row
compaction through a user-selected Numba partner.

It does not authorize:

- v2.6 release;
- public speedup wording;
- Numba speedup wording;
- whole-app triangle-counting speedup wording;
- broad RT-core speedup wording;
- true-zero-copy wording.

The existing primitive-first fused RTDL scalar triangle-counting path remains the
recommended fast scalar path.
