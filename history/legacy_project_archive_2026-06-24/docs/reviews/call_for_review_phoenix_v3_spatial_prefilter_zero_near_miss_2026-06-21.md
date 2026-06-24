# Call For Review: Phoenix V3 Spatial Prefilter-Zero Near-Miss

Date: 2026-06-21.

Please critically review the Phoenix V3 Spatial relation-status prefilter-zero
near-miss packet. Do not edit files. Return a concise but rigorous review with
a verdict.

## Scope

- V3 only.
- V4, C ABI, embedding, and external zero-copy interop are out of scope.
- The current V3 release remains blocked.
- This review must not authorize release.
- Promote only reusable, evidence-backed V3 engine capabilities; reject
  app-specific or unsupported public claims.

## Files To Inspect

- `docs/rebuild/v3/phoenix_v3_spatial_relation_status_prefilter_zero_experiment_2026-06-21.md`
- `docs/rebuild/v3/phoenix_v3_spatial_relation_status_prefilter_zero_experiment_2026-06-21.json`
- `docs/rebuild/v3/phoenix_v3_next_generic_engine_work_queue_2026-06-21.md`
- `docs/rebuild/v3/phoenix_v3_next_generic_engine_work_queue_2026-06-21.json`
- `scripts/v3_phoenix_spatial_relation_status_prefilter_zero_experiment.py`
- `tests/v3_phoenix_spatial_relation_status_prefilter_zero_experiment_test.py`
- `tests/v3_phoenix_next_engine_work_queue_test.py`
- `scripts/v3_phoenix_release_readiness_gate.py`
- `src/native/optix/rtdl_optix_workloads.cpp`

## Facts To Verify

- Dataset: `br_county.cdb` public county data, not toy.
- Old best legal RTDL route: `5.406518 ms` prepared query, exact count
  `47,262`.
- New default-off native switch:
  `RTDL_OPTIX_RELATION_STATUS_CORRECTED_PREFILTER_ZERO`.
- New stable `y_then_x` sample7 result: `1.903492957353592 ms` prepared query,
  exact count `47,262`.
- Internal speedup versus old legal RTDL route: `2.8403141598782855x`.
- RayJoin author Query bar: `1.865660 ms`.
- RayJoin author is still faster by `1.0202785916799373x`; remaining gap is
  `0.03783295735359182 ms`.
- Boundary-helper fast path failed correctness: `47,259 != 47,262`; it was
  rejected.
- Status should remain
  `spatial_relation_status_prefilter_zero_near_miss_not_m7`.
- M7 rows added should remain `0`.
- `release_authorized`, `public_speedup_claim_authorized`, and
  `broad_v3_faster_than_v2_claim_authorized` should remain `false`.
- Queue/release gates should keep missing `point_location_topology_stream` as a
  blocker.

## Questions

1. Verdict: `approve-near-miss-not-m7`, `reject-promote`, or
   `needs-more-evidence`.
2. Are the no-release/no-M7 boundaries correct?
3. Are correctness and author-bar reasons adequate?
4. Are there P0/P1 fixes before this can be used as a V3 status/queue artifact?
5. What concrete next technical path is still V3-scoped and not app-specific?
