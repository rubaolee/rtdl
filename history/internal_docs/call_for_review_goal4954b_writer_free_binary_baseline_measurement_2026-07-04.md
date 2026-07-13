# Call For Review: Goal4954-B Writer-Free Binary Baseline Measurement

Date: 2026-07-04

Review target:

- `history/internal_docs/goal4954b_writer_free_binary_baseline_measurement_2026-07-04.md`
- `history/internal_docs/goal4954b_artifacts/writer_free_binary_summary_run1.json`
- `history/internal_docs/goal4954b_artifacts/writer_free_binary_summary_run2.json`
- `history/internal_docs/goal4954b_artifacts/writer_free_binary_summary_run3.json`
- `history/internal_docs/goal4954b_writer_free_binary_overlay_measure.py`

Requested verdict:

`approve_goal4954b_writer_free_measurement_close_open_goal4954c`

or:

`block_goal4954b_measurement_until_redone`

## Context

Goal4954-B was measurement-only:

- run the public County x Soil sample;
- exclude the paper text writer from the binary performance metric;
- preserve the paper output line only as correctness context;
- compare writer-free binary hot path against AuthorOfficial overlay compute;
- do not implement new optimization or change RTDL core/runtime.

The previous missing-OptiX blocker was resolved on the POD by using the official
NVIDIA `optix-sdk` GitHub repository at tag `v9.0.0`, then building
`build/librtdl_optix.so`.

## Review Questions

1. Did Goal4954-B remain measurement-only, with no RTDL core/runtime changes?

2. Is the OptiX v9.0.0 POD build setup acceptable evidence for running the
   measurement on this driver/GPU?

3. Does the route correctly exclude the paper text writer from the binary
   metric?

4. Does the measurement preserve the generic-system/RayJoin-app invariant?

5. Are the 3-run results enough to support the median phase table?

6. Is the interpretation correct:
   removing the writer isolates the gap but does not close it?

7. Is the reported median writer-free hot path of `5.309487s`, about `126.12x`
   slower than the `0.0421s` AuthorOfficial overlay-compute reference,
   properly bounded?

8. Does the measured bottleneck ranking justify reframing Goal4954-C from
   "reprojection/sort only" to "measured pre-fusion bottleneck prototype",
   including binary grouped row construction?

9. Does the report correctly avoid authorizing Layer 4 fusion, raw callbacks,
   public API exposure, or RayJoin-specific RTDL core work?

10. Should Goal4954-B close with:

   `writer_free_measurement_ready_for_device_columnar_work`

   and should Goal4954-C open only after a reviewed plan?

## Non-Authorization Boundary

Approval does not authorize:

- Layer 4 fusion;
- traversal-side callbacks;
- public API exposure;
- RTDL-core promotion of RayJoin app code;
- performance claims beyond this public sample and this measurement route.
