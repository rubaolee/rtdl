# Goal3143: Hausdorff `partner_exact` Numba Front Door

Date: 2026-06-03

Status: local implementation plus RTX 4000 Ada pod validation complete; not a release or public speedup authorization.

## Purpose

Goal3139/Goal3142 made Numba grouped-arg continuations fast enough to use as real benchmark-app building blocks. Goal3143 wires that path into the shared Hausdorff front door so a user can run the exact partner implementation as:

```python
hausdorff.run_app("partner_exact", copies=..., partner="numba")
```

instead of needing the older app-specific `partner_numba_block_nearest_exact` backend name.

## Implementation

- Added Numba point-column carrier support to `rt.point_rows_to_partner_columns(..., partner="numba")`.
- Added `rt.directed_hausdorff_2d_partner_columns(..., partner="numba")`.
- The Numba directed-Hausdorff route composes only generic partner primitives:
  - `pairwise_l2_sq_block_nearest_rows_2d` by default;
  - `grouped_argmin_f64`;
  - `grouped_argmax_f64`;
  - optional `sqrt_f64` when a caller wants the full nearest-distance column.
- Added a generic Numba `sqrt_f64` typed-column transform for the rich column-returning adapter default.
- Updated the Hausdorff benchmark app so `backend="partner_exact"` accepts `partner="numba"`.
- The scalar app path sets `materialize_nearest_distances=False`, because the app only needs the final witness scalar. The public adapter default still materializes the nearest-distance column.

## Boundary

This is a partner-continuation front-door improvement, not an RT-core path. The exact Numba path does not call OptiX traversal, does not add native app-specific logic, and does not authorize public speedup, whole-app, RT-core, true-zero-copy, or release wording.

## Pod Evidence

Pod: NVIDIA RTX 4000 Ada Generation, Python 3.12.3.

Validation:

```text
python -m unittest \
  tests.goal3143_hausdorff_partner_exact_numba_front_door_test \
  tests.goal3010_hausdorff_numba_witness_exact_app_wiring_test \
  tests.goal3012_numba_pairwise_score_rows_for_hausdorff_test \
  tests.goal3015_numba_block_nearest_rows_for_hausdorff_test \
  tests.goal3017_numba_grouped_witness_no_host_sync_fast_path_test \
  tests.goal3139_numba_kernel_cache_contract_test

Ran 20 tests in 0.973s
OK
```

Warmed timing artifact:
`docs/reports/goal3143_pod_artifacts/hausdorff_partner_exact_numba_pod_probe_2026-06-03.json`

| points A x B | shared `partner_exact,numba` | old `partner_numba_block_nearest_exact` | shared / old | logical pairs | emitted score rows |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1024 x 1024 | 0.012995 s | 0.012142 s | 1.070x | 1,048,576 | 4,096 |
| 4096 x 4096 | 0.024969 s | 0.022969 s | 1.087x | 16,777,216 | 65,536 |
| 8192 x 8192 | 0.044529 s | 0.085933 s | 0.518x | 67,108,864 | 262,144 |

All rows matched the oracle and all claim-boundary flags stayed false.

## Conclusion

The fast Numba grouped-arg path is now exposed through the normal benchmark-app front door. The old bespoke backend remains for compatibility, but the recommended user-facing exact partner shape can be `partner_exact` plus an explicit user-selected `partner="numba"`.

Next engineering target remains the canonical front-door compaction path for `segmented_min_f64` / `segmented_max_f64`, unless we decide to apply the same “shared front door over bespoke backend” cleanup to another benchmark app first.
