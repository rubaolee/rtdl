# Handoff: External Review for Goal4059 Direct Numba Component Signature

Please independently review Goal4059 on current `main`.

## Scope

Goal4059 adds a generic Numba component-size signature continuation for prepared
fixed-radius graph components:

- `src/rtdsl/partner_adapters.py`
  - `radius_graph_component_signature_3d_optix_numba_prepared_grouped_stream_partner_columns`
  - `PreparedOptixNumbaRadiusGraphGroupedStreamContinuation3D.run_component_signature`
  - device-side Numba root-count/signature kernel
- `src/rtdsl/v2_8_fixed_radius_graph_component_front_door.py`
  - `fixed_radius_graph_component_size_signature_3d_v2_8`
- `examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py`
  - Numba column-signature mode uses the signature front door directly
- `docs/reports/goal4059_rt_dbscan_direct_component_signature_front_door_2026-06-08.md`
- `docs/reports/goal4059_direct_numba_component_signature_front_door_pod_probe.json`
- `tests/goal4059_rt_dbscan_direct_component_signature_front_door_test.py`

## Evidence Already Recorded

- Local and pod focused test slice passed.
- Pod: RTX 4000 Ada, commit `16be56b7` for implementation and `1f33e437`
  after evidence/report commit.
- Small validation: `road3d`, 1024 points, threshold 64,
  `matches_reference: true`.
- Timing rows:
  - `road3d`, 4096 points, threshold 64: `0.001565s`;
  - `clustered3d`, 65536 points: `0.093696s`;
  - diagnostic comparison against prior Goal4056/4057 same-pod label-count route:
    `1.077x`.

## Review Questions

1. Does the new path preserve the app-agnostic engine boundary, with DBSCAN
   logic remaining outside the native engine?
2. Is the Numba-only signature front door explicit and user-selected, with no
   hidden partner dispatch?
3. Is the correctness evidence sufficient for an internal benchmark-hardening
   goal, especially the small CPU-reference validation?
4. Is the performance claim wording correctly bounded as diagnostic
   engineering evidence only?
5. Are there correctness risks in counting parent roots directly from the
   grouped-union workspace, especially for mixed core/border/noise cases?
6. What should the next engineering step be: further RT-DBSCAN scale hardening,
   a reusable generic graph-component signature primitive refinement, or a
   different benchmark bottleneck?

Please write a review to:

- Claude: `docs/reviews/goal4060_claude_review_goal4059_direct_numba_component_signature_2026-06-09.md`
- Gemini: `docs/reviews/goal4061_gemini_review_goal4059_direct_numba_component_signature_2026-06-09.md`

Use one of the allowed verdicts: `accept`, `accept-with-boundary`,
`needs-more-evidence`, or `reject`.
