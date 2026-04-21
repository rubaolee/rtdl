# Goal666: Claude Review - Apple RT Count Performance

Date: 2026-04-20

Reviewer: Claude (claude-sonnet-4-6)

## Verdict

ACCEPT. Implementation is correct, the mixed-density correctness gap is closed, and the performance claims are real but properly bounded.

## Implementation Check

`rtdl_apple_rt_count_prepared_ray_anyhit_2d` calls the prepared Apple RT 2D any-hit traversal with `rows_out=nullptr` and `row_count_out=nullptr`. The shared native implementation still runs the MPS dispatch and result scan, but skips row allocation and row fill when `emit_rows` is false. The returned count comes from the native profile hit count, so this is not a fake shortcut that bypasses traversal.

`count_profile_packed` accepts an `AppleRtRay2DBuffer` whose ray records were packed once by `prepare_apple_rt_rays_2d`. This correctly amortizes Python-side ray packing into setup time for repeated-query apps.

## Correctness Check

The earlier mixed-density gap is closed. The updated Goal666 report includes:

- `dense_blocked:large_count`: 32768 blocked out of 32768 rays.
- `mixed_visibility:large_count`: 16384 blocked out of 32768 rays.
- `sparse_clear:large_count`: 0 blocked out of 32768 rays.

Apple RT packed-count, Embree row-count, and Shapely/GEOS count agree on all three cases. The new unit test `test_mixed_visibility_case_has_blocked_and_clear_rays` independently validates the mixed case construction with the CPU oracle, so the mixed case is not accidentally degenerate.

## Performance Claim Check

The repeated-query scalar-count result is real. On the updated report:

- Dense blocked: Apple RT packed-count / Embree row-count is `0.075x`.
- Mixed visibility: Apple RT packed-count / Embree row-count is `0.082x`.
- Sparse clear: Apple RT packed-count / Embree row-count is `0.029x`.

This supports a narrow app-level claim: for prepared scenes and prepacked repeated ray sets where the app only needs blocked-ray count, Apple RT is substantially faster than the row-materialized Embree and Shapely baselines in this harness.

## Boundary Honesty

The report keeps the required boundaries:

- Setup costs are reported separately and excluded from repeated-query timing.
- The scalar-count API has a different output contract from full emitted rows.
- Apple RT full row output remains slower than Embree and is not claimed as a win.
- The result does not generalize to Apple RT DB or graph workloads.

No remaining blocker.
