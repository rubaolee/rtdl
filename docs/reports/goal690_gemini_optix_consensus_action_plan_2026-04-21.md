# Goal690: Gemini OptiX Critique Consensus And Action Plan

Date: 2026-04-21

External input:
`/Users/rl2025/antigravity-working/rtdl-4-16/docs/reports/gemini_optix_independent_critique_2026-04-21.md`

Primary internal review:
`/Users/rl2025/rtdl_python_only/docs/reports/goal689_optix_app_performance_review_2026-04-21.md`

## Consensus

Codex and Gemini agree on the main technical point: `--backend optix` must not
be treated as identical to NVIDIA RT-core acceleration.

The current public app surface contains four distinct OptiX realities:

- `optix_traversal`: true OptiX traversal/custom-primitive path eligible for
  RTX hardware acceleration on RTX-class GPUs.
- `cuda_through_optix`: CUDA-style kernels hosted by the OptiX backend library,
  useful GPU compute but not an RT-core traversal claim.
- `host_indexed_fallback`: OptiX-facing app path currently dispatches to
  CPU-side indexed logic.
- `python_interface_dominated`: real backend work exists, but app performance
  is dominated by Python packing, row materialization, reduction, or CPU
  post-processing.

Gemini specifically confirmed the highest-risk classifications:

- graph BFS/triangle OptiX paths are currently host-indexed correctness paths;
- default road-hazard and segment/polygon OptiX app paths are host-indexed
  unless native mode is separately enabled and gated;
- KNN/fixed-radius apps are CUDA-through-OptiX rather than RT-core traversal;
- `tuple[dict, ...]` row materialization and Python `rt.reduce_rows(...)`
  dilute or erase native traversal wins;
- GTX 1070 benchmark evidence is not RT-core evidence.

## Action Taken In This Goal

Added machine-readable OptiX app performance classification:

- `rtdsl.optix_app_performance_matrix()`
- `rtdsl.optix_app_performance_support(app)`
- `rtdsl.OPTIX_APP_PERFORMANCE_CLASSES`

Updated public docs:

- `docs/app_engine_support_matrix.md` now includes an "OptiX Performance
  Classification" section.

This is intentionally separate from `rtdsl.app_engine_support_matrix()`. The
app engine matrix says what CLI paths exist. The OptiX performance matrix says
what kind of performance path the OptiX app actually uses today.

## Prioritized Implementation Plan

1. API honesty and tool visibility.

   Keep the performance classification visible in docs and machine-readable
   APIs. If an app exposes OptiX but is `host_indexed_fallback`, future CLI
   help or JSON output should say so directly.

2. Native summary outputs.

   Start with robot collision / visibility / ray-triangle any-hit. This is the
   strongest OptiX flagship because it already maps to early-exit ray
   traversal. Avoid returning one Python dict row per ray when the app only
   needs pose-level collision flags, counts, or booleans.

3. DB prepared-columnar tightening.

   DB analytics has real OptiX BVH candidate discovery, but app performance is
   dominated by Python/ctypes preparation, candidate copy-back, CPU exact
   filtering/grouping, and dict-row materialization. The next useful DB work is
   prepared columnar datasets, batched predicates, and native grouped outputs.

4. Segment/polygon native OptiX promotion.

   Do not claim road-hazard or segment/polygon OptiX as a flagship until the
   native OptiX mode is default or clearly selected, correctness-gated, and
   measured.

5. Graph reclassification or native GPU work.

   Graph analytics should remain a correctness-compatible OptiX app path until
   BFS and triangle routines are moved off host-indexed CPU logic or the public
   status is downgraded.

6. RTX-class validation.

   Future OptiX performance reports must run on RTX-class hardware when making
   RT-core claims. GTX 1070 remains useful for CUDA/backend compatibility, not
   RT-core validation.

## Non-Goals

- This goal does not implement new native OptiX kernels.
- This goal does not claim new speedups.
- This goal does not downgrade existing app CLI options yet; it adds the
  classification layer needed to make that decision safely.

## Current Verdict

ACCEPT as a consensus/action-plan step. The next coding goal should target the
robot collision / visibility path with native scalar or pose-level OptiX output,
because it is the clearest path to visible NVIDIA RT-core performance.
