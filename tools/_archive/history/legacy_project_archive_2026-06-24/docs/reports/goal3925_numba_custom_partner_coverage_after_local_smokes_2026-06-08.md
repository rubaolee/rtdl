# Goal3925 Numba Custom-Partner Coverage After Local Smokes

Date: 2026-06-08

## Purpose

Goal3925 records the current custom-partner coverage picture for the ten
benchmark apps after the Goal3918-3924 Numba work. The project rule is:

- RTDL primitives are the default when a fused generic primitive exactly answers
  the app contract.
- When a benchmark app needs custom continuation logic, provide a Numba
  reference path so users are not forced to write CuPy RawKernel code.
- CuPy can remain a baseline, conformance opponent, or fastest measured partner
  for a specific row, but it must not be the only path for user-written custom
  logic in benchmark guidance.

## Current Ten-App Partner Coverage

| Benchmark app | Current primary path | Needs custom partner for reference path? | Numba coverage status |
| --- | --- | --- | --- |
| `hausdorff_xhd` | RTDL/OptiX active-frontier primitive | No for primary exact contract | Numba has contract evidence for score/global reductions; CuPy remains same-contract CUDA-core baseline. |
| `spatial_rayjoin` | Primitive-first scalar paths; Numba row-stream compaction when rows are needed | Yes for row-stream compaction | Numba compact-mask reference exists for PIP, LSI, and overlay-seed row streams. |
| `rt_dbscan` | RTDL fixed-radius/core summaries plus Numba component/signature continuation | Yes for component/signature continuation | Numba grouped-stream reference exists; blocked Numba modes landed in Goal3918 and await Goal3920 A5000 timing. |
| `robot_collision` | Generic any-hit/collision-flag primitives | No promoted partner path | No partner is currently required; future Numba flag reduction is optional, not a current requirement. |
| `contact_manifold` | Bounded collect / fail-closed witness primitives | No promoted partner path | No partner is currently required; future Numba witness filtering is optional, not a current requirement. |
| `raydb_style` | Fused RTDL grouped reductions when exact; Numba for unfused grouped scalar continuations | Yes for unfused grouped continuation shapes | Numba grouped count/sum/min/max/avg lane exists and is the recommended custom continuation. |
| `barnes_hut` | RTDL frontier collection plus custom force-vector continuation | Yes for exact force-vector continuation | CuPy remains fastest measured, but Numba no-RawKernel exact-force reference exists for users who prefer Python JIT custom logic. |
| `librts_spatial_index` | Generic point/range query rows where supported | No promoted partner path | No partner is currently required; custom mutable-index continuation remains a future study. |
| `rtnn` | Prepared fixed-radius ranked-summary primitive | No for primary ranked-summary contract | CuPy remains all-pairs baseline; Numba custom ranking is future optional work, not a current blocker. |
| `triangle_counting` | Native scalar triangle-count primitive for scalar answer; Numba compaction for witness rows | Yes for candidate-row compaction | Numba compact-mask continuation exists and is the recommended custom continuation. |

## Local Smoke Evidence

Local Linux host `192.168.1.20` was used for functional readiness only. It has a
GTX 1070, so these runs are not release performance evidence.

| App | Route | Local result | Notes |
| --- | --- | --- | --- |
| `rt_dbscan` | `optix_rt_core_grouped_stream_numba_column_signature_3d` | pass | Rebuilt `librtdl_optix.so`; smoke produced stable signature. |
| `rt_dbscan` | `optix_rt_core_grouped_stream_blocked_numba_column_signature_3d` | pass | Rebuilt `librtdl_optix.so`; exercised four query blocks at 1024 points. |
| `triangle_counting` | `run_triangle_counting_v2_6_numba_compact_mask_preview` | pass | 32,768 candidate rows; CPU parity true for selected ids and original indices. |

## Remaining Timing Work

The main A5000 timing queue is still Goal3923:

- Goal3913 RayJoin shared loaded-case subprobe timing.
- Goal3920 RTDBSCAN unblocked versus blocked Numba timing.

Triangle counting already has prior pod evidence from Goal3000/Goal3052. The
local smoke above only confirms the current local CUDA/Numba path still runs.

## Boundary

Goal3925 is a coverage and readiness audit. It does not add native engine
behavior, auto-select partners, promote CuPy or Numba globally, authorize public
speedup claims, authorize broad RT-core claims, authorize true-zero-copy claims,
or authorize release wording.

## Validation

Run:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3925_numba_custom_partner_coverage_after_local_smokes_test tests.goal3921_partner_choice_guidance_after_numba_reference_refresh_test
```

Expected: all tests pass.
