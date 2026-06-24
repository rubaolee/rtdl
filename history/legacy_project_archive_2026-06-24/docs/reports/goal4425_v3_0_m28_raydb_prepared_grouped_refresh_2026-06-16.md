# Goal4425: V3.0 M28 RayDB Prepared Grouped-Reduction Refresh

## Status

M28 refreshes the RayDB-style benchmark's primitive-first prepared grouped
reduction path under the V3 evidence rules.

This is intentionally not a partner milestone. RayDB count/sum are already
expressible as the generic `ray_triangle_grouped_i64_reduction_3d` prepared
primitive, so the correct V3 strategy is primitive-first: use the native
prepared grouped reduction directly, and reserve partner continuations for
unfused result shapes that the generic primitive cannot express.

## What Changed

- Added `scripts/v3_0_m28_raydb_prepared_grouped_refresh.py`.
- The runner measures the current app front door for:
  - `paper_rt_embree`;
  - `paper_rt_optix_prepared_grouped_reduction`.
- The runner uses a generated RayDB-style table with 262,144 rows and 1,024
  groups by default.
- Repeat counts are calibrated per backend/mode so the measured query windows
  are human-scale rather than one-off millisecond toy rows.

## Contract Boundary

| Question | M28 answer |
| --- | --- |
| Does this app need a partner for count/sum? | No. |
| Is the selected strategy primitive-first? | Yes. |
| Does this add RayDB-specific native engine logic? | No. |
| Does this compare OptiX and Embree under the same logical contract? | Yes, internally. |
| Does this authorize public speedup wording? | No. |

## Pod Evidence

The M28 runner writes compact evidence to:

- `docs/reports/goal4425_v3_0_m28_raydb_prepared_grouped_refresh_262144_2026-06-16.json`

Expected evidence fields:

- `status: ok`;
- four rows: `count` and `sum` for Embree and OptiX;
- `comparison.all_match_cpu_reference: true`;
- `comparison.no_partner_continuation_required: true`;
- `comparison.all_prepared_steady_state: true`;
- all public speedup and true-zero-copy claim flags false.

## Measured Matrix

Hardware: NVIDIA RTX 4000 Ada Generation, driver 550.127.08, 20,475 MiB.
Dataset: generated RayDB-style table, 262,144 rows, 1,024 groups.

The repeat counts are intentionally different by backend and mode so each row
has a roughly human-scale measured query window. `Median` is one prepared-query
iteration; `query window` is the measured repeated prepared-query total.

| Backend | Mode | Repeat | Triangles | Rays | Query window s | Median s | Traversal median s | Row presentation median s | Cold prepare s | Correct |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Embree | count | 400 | 262,144 | 884,736 | 5.020 | 0.012433 | 0.011568 | 0.000317 | 0.285 | true |
| Embree | sum | 10 | 262,144 | 38,043,648 | 5.702 | 0.593568 | 0.591993 | 0.000710 | 1.982 | true |
| OptiX | count | 5,000 | 262,144 | 884,736 | 4.533 | 0.000902 | 0.000211 | 0.000319 | 0.413 | true |
| OptiX | sum | 1,000 | 262,144 | 38,043,648 | 4.903 | 0.004903 | 0.004209 | 0.000312 | 3.115 | true |

Internal same-contract ratios:

| Mode | Embree median s | OptiX median s | Embree / OptiX |
| --- | ---: | ---: | ---: |
| count | 0.012433 | 0.000902 | 13.78x |
| sum | 0.593568 | 0.004903 | 121.05x |

## Interpretation

M28 is a useful counterweight to the partner-heavy V3 work: not every benchmark
app should be forced through CuPy or Numba. If a benchmark result is already a
scalar or compact grouped reduction that the generic RTDL primitive can express,
the cleaner architecture is to keep it native and app-agnostic.

The evidence is therefore about strategy selection:

- RayDB count/sum should stay on the prepared grouped-reduction primitive path.
- Partner hit-stream continuations remain available for result shapes that are
  not expressible as fused generic grouped reductions.
- The measured query windows are large enough to be meaningful, but the ratios
  are still internal same-contract engineering observations, not release claims.
- OptiX/Embree rows are same-contract internal engineering evidence only; they
  do not authorize release wording or public RT-core speedup claims.

## Verification

```bash
PYTHONPATH=src:. python -m unittest tests.goal4425_v3_0_m28_raydb_prepared_grouped_refresh_test
PYTHONPATH=src:. python scripts/v3_0_m28_raydb_prepared_grouped_refresh.py \
  --generated-rows 262144 \
  --generated-groups 1024 \
  --warmup 1 \
  --output docs/reports/goal4425_v3_0_m28_raydb_prepared_grouped_refresh_262144_2026-06-16.json
```
