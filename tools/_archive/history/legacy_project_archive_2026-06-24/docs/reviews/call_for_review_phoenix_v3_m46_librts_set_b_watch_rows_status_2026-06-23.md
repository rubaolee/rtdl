# Call For Review: Phoenix V3 M46 LibRTS Set-B Watch Rows Status

Date: 2026-06-23

Please critically review the M46 LibRTS Set-B watch-row status and next-protocol
recommendation.

Primary file:

- `docs/reports/phoenix_v3_m46_librts_set_b_watch_rows_status_and_next_protocol_2026-06-23.md`

Required supporting files:

- `docs/rebuild/v3/phoenix_v3_set_a_set_b_scorecard_gate_2026-06-22.md`
- `docs/reports/phoenix_v3_m25_librts_aabb_optix_runner_watch_row_2026-06-23.md`
- `docs/reports/phoenix_v3_m27_librts_aabb_set_b_triage_and_cold_optix_retain_fix_2026-06-23.md`
- `docs/reviews/codex_claude_phoenix_v3_m27_librts_aabb_set_b_triage_and_cold_optix_retain_fix_2ai_consensus_2026-06-23.md`
- `docs/reports/phoenix_v3_m31_librts_watch_rows_existing_evidence_analysis_2026-06-23.md`
- `examples/current/research_benchmarks/librts_spatial_index/rtdl_librts_spatial_index_benchmark_app.py`
- `tests/v3_phoenix_librts_aabb_count_runner_test.py`

Requested verdict labels:

- `accept_m46_prepare_m47_librts_stability_protocol`
- `revise_m46_watch_row_classification`
- `revise_m46_next_action_code_fix_needed_first`
- `reject_m46_librts_should_be_closed`

Review questions:

1. Does M46 correctly identify that the frozen Set-B visible row is Embree
   `0.869x`, while later focused evidence also keeps an OptiX cold watch row
   open?
2. Is M46 correct that M27's retain-output code fix should stay?
3. Is M46 correct that neither OptiX cold nor Embree stress is closed?
4. Is M46 correct to recommend a focused stability/cold-start protocol before
   more code changes or POD?
5. Are the proposed M47 protocol requirements sufficient to separate first
   sample/cold-start variance from steady behavior?
6. Does M46 correctly keep LibRTS as Set-B/control evidence, not Set-A
   runtime-trunk proof?
7. Does M46 preserve all non-authorization boundaries?

Non-authorization to preserve:

- no V3 release
- no all-app benchmark run
- no paid POD spend
- no public speedup wording
- no broad V3-over-V2 claim
- no V4 work
- no embedding
- no C ABI
- no true zero-copy claim
