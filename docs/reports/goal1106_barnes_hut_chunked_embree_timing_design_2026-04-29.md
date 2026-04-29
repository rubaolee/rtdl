# Goal1106 Barnes-Hut Chunked Embree Timing Design

Date: 2026-04-29

## Purpose

Goal1105 proved that the original Barnes-Hut 20M Embree timing baseline is not viable on the 16 GB Linux host: the process was killed at about 15 GB RSS before it could write the timing artifact. The failure was memory pressure from Python-side materialization, not an Embree correctness failure.

Goal1106 adds a bounded-memory timing runner for the same current-contract non-OptiX baseline row:

- app: `barnes_hut_force_app`
- path: `node_coverage_prepared_rich`
- backend: `embree`
- query count: `20,000,000`
- Barnes-Hut tree depth: `8`
- hit threshold: `4`
- validation mode: timing-only, `matches_oracle: null`
- public claim flag: `public_speedup_claim_authorized: false`

## Design

The canonical Goal1101 profiler built all generated bodies as Python objects, then derived the fixed-depth quadtree grid and queried all bodies in one prepared Embree call. For the timing-only row, the fixed-depth node grid depends on generated-body coordinate bounds, not on body masses or body membership lists.

The new script `scripts/goal1106_barnes_hut_chunked_embree_timing_baseline.py` preserves the same RT query contract while changing only host-side execution mechanics:

1. Compute generated-body bounds by streaming deterministic coordinates.
2. Build the same fixed-depth node centers as `build_fixed_depth_quadtree_cells`.
3. Prepare one Embree fixed-radius threshold structure over those node centers.
4. Stream body query points in chunks.
5. Sum per-chunk native query time into one logical iteration timing.
6. Emit a Goal1101-schema-compatible timing artifact at `docs/reports/goal1101_current_contract_non_optix_baselines/barnes_hut_depth8_20m_embree_timing_baseline.json`.

## Boundary

This is not a new Barnes-Hut algorithm claim. It is a host-memory fix for collecting the missing non-OptiX timing baseline. It does not authorize public RTX speedup claims and does not imply that Barnes-Hut force-vector reduction is native.

## Verification

Focused tests:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal1106_barnes_hut_chunked_embree_timing_baseline_test -v
```

Result:

```text
Ran 3 tests in 0.513s
OK
```

Regression tests:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal1101_current_contract_non_optix_baseline_profiler_test tests.goal1102_current_contract_baseline_intake_test -v
```

Result:

```text
Ran 10 tests in 0.676s
OK
```

The tests verify that streamed node points match the canonical fixed-depth Barnes-Hut node construction, the runner uses bounded query chunks, and the emitted artifact keeps the no-public-claim boundary.

## Next Step

Stage this script to Linux and run the 20M timing row with bounded chunks. If it completes, rerun Goal1102 intake so the baseline set can move from `waiting_for_baseline_artifacts` to `ready_for_2ai_baseline_review_not_public_claim`.
