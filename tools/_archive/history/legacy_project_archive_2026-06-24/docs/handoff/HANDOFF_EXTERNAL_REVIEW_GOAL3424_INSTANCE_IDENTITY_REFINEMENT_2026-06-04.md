# External Review Handoff: Goal3424 Instance-Aware Closed-Shape Refinement

Please review Goal3424 as an independent external AI reviewer.

## Context

RTDL v2.8 is hardening typed, device-resident RT/partner streams for closed-shape
membership / RayJoin-like workloads while keeping the native engine app-agnostic.
Goals3420-3422 found that RT candidate columns were a conservative superset on
the public RayJoin county CDB, but the CuPy simple-ring refinement helper missed
217 host-exact rows. Goal3424 discovered the immediate cause: the CDB has
duplicate public point ids and duplicate public shape ids, while the helper
collapsed public ids into a single geometry instance.

Goal3424 therefore adds generic instance identity columns to the pair-column
stream:

- public id columns: `point_id`, `shape_id`
- instance columns: `point_ordinal`, `shape_ordinal`

Public ids remain the grouping/output contract. Ordinals identify the exact
input point row and prepared shape row for partner refinement.

## Files To Inspect

- `src/native/optix/rtdl_optix_prelude.h`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/native/optix/rtdl_optix_core.cpp`
- `src/rtdsl/optix_runtime.py`
- `src/rtdsl/closed_shape_topology.py`
- `scripts/goal3424_closed_shape_instance_identity_refinement_probe.py`
- `tests/goal3424_closed_shape_instance_identity_refinement_test.py`
- `docs/reports/goal3424_closed_shape_instance_identity_refinement_2026-06-04.md`
- `docs/reports/goal3424_closed_shape_instance_identity_refinement_probe_2026-06-04.json`
- `docs/research/future_version_to_do_list.md`

## Evidence To Verify

- Commit under review: `7230bef4` or current `origin/main` if newer only by
  review artifacts.
- Pod artifact GPU: NVIDIA RTX A5000, driver 580.126.09.
- Full public `br_county.cdb`: 16,545 probe points, 15,700 closed shapes.
- Duplicate public ids: 65 duplicate point ids and 60 duplicate shape ids, max
  multiplicity 2.
- Host exact rows: 47,262.
- RT candidate rows: 47,570.
- CuPy refined rows after instance columns: 47,262.
- Dropped candidate rows: 308.
- Pair multiset match host exact: true.
- Grouped counts match host exact: true.
- All claim-boundary flags remain false.

## Review Questions

1. Is the implementation app-agnostic, or did it smuggle RayJoin/CDB policy into
   native code?
2. Is appending ordinal pointers to `RtdlNativeDevicePairColumns` a reasonable
   backward-compatible extension for current source-tree execution?
3. Does the CuPy helper preserve old public-id behavior while correctly using
   ordinals when present?
4. Does the pod artifact support the corrected diagnosis that Goal3421's miss
   was public-id collapse, not a proven unavoidable topology gap on this CDB?
5. Are claim boundaries sufficiently blocked?
6. What risks or required follow-ups remain before v2.8 closeout?

## Required Output

Write one review file:

- Claude: `docs/reviews/goal3425_claude_review_goal3424_instance_identity_refinement_2026-06-04.md`
- Gemini: `docs/reviews/goal3426_gemini_review_goal3424_instance_identity_refinement_2026-06-04.md`

Use one of the standard verdicts: `accept`, `accept-with-boundary`,
`needs-more-evidence`, or `reject`.

Do not authorize release, public speedup, RayJoin reproduction, true-zero-copy,
hidden dispatch, automatic retry, or native default-route claims.
