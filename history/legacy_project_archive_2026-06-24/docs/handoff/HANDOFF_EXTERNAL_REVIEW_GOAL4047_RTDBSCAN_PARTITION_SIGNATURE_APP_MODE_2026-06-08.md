# External Review Handoff: Goal4047 RT-DBSCAN Partition Signature App Mode

Please perform a read-only review of Goal4047.

## Files To Inspect

- `examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py`
- `examples/v2_0/research_benchmarks/rt_dbscan/README.md`
- `docs/reports/goal4047_rt_dbscan_partition_signature_app_mode_2026-06-08.md`
- `docs/reports/goal4047_rt_dbscan_partition_signature_app_mode_pod_smoke.json`
- `tests/goal4047_rt_dbscan_partition_signature_app_mode_test.py`
- Related primitive reports/tests:
  - `docs/reports/goal4045_partition_component_signature_preview_2026-06-08.md`
  - `docs/reports/goal4046_partition_component_signature_timing_2026-06-08.md`
  - `tests/goal4045_partition_component_signature_preview_test.py`
  - `tests/goal4046_partition_component_signature_timing_test.py`

## Review Questions

1. Does the new app mode
   `partner_cupy_partition_convergence_component_signature_3d` correctly expose
   the Goal4045/4046 component-size-signature primitive without changing the
   promoted RT-DBSCAN route?
2. Does the app correctly treat the mode as a fixed-radius graph component
   signature rather than full DBSCAN core/border/noise semantics?
3. Are claim boundaries preserved, especially:
   - no full DBSCAN claim;
   - no RT-core acceleration claim;
   - no release/public speedup claim;
   - no app-specific native-engine logic;
   - no automatic partner selection or hidden dispatch?
4. Is the pod smoke artifact at commit `f36ad087` sufficient for this narrow
   app-mode exposure, given that it is not a performance-promotion goal?
5. Are the tests focused and adequate, including the no-row rejection and the
   pod-smoke boundary checks?

## Expected Review Output

Write a review file in `docs/reviews/` with an explicit verdict:

- Claude: `docs/reviews/goal4048_claude_review_goal4047_rtdbscan_partition_signature_app_mode_2026-06-08.md`
- Gemini: `docs/reviews/goal4048_gemini_review_goal4047_rtdbscan_partition_signature_app_mode_2026-06-08.md`

Use one of the usual verdict values: `accept`, `accept-with-boundary`,
`needs-more-evidence`, or `reject`.

Please do not modify source files. If you find issues, report them with file
and line references and keep the claim-boundary discipline explicit.

