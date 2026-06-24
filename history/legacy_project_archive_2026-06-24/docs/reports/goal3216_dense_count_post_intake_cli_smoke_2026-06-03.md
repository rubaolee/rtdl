# Goal3216: Post-Intake Dense Count CLI Smoke on Pod

Date: 2026-06-03

## Purpose

Goal3216 records a live pod execution after Goal3215 hardened the fused
segment-pair left-id count primitive.

The pod rebuilt `librtdl_optix.so` from commit `a9277a1f` and ran:

```bash
python examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py \
  --workload lsi \
  --execution-route prepared_optix_left_id_dense_count \
  --no-rows
```

Artifact:

- `docs/reports/goal3216_dense_count_post_intake_cli_smoke_2026-06-03.json`

## Result

The CLI route completed with:

- `execution_route: prepared_optix_left_id_dense_count_reuse`
- `output_contract: segment_segment_intersection_count_by_left_id_dense_device_column`
- `device_resident: true`
- `native_symbol: rtdl_optix_prepared_segment_pair_left_id_count_device_columns`
- `row_count: 1`
- `public_speedup_claim_authorized: false`

This proves the hardened native path still builds and executes on the pod after
the overflow atomic and release-alias changes.

This is a smoke test, not a timing claim; the measured phase includes cold
first-call setup and must not be used as steady-state performance evidence.

## Boundary

This run does not authorize release, public speedup claims, broad RT-core
claims, true zero-copy claims, or RayJoin paper-reproduction claims.
