# Call For Review: Phoenix V3 M47 LibRTS Stability / Cold-Start Protocol

Date: 2026-06-23

Please critically review the M47 LibRTS stability/cold-start protocol. This is
a protocol draft only; do not authorize a run unless you explicitly choose the
run-authorization verdict below.

Primary file:

- `docs/rebuild/v3/phoenix_v3_m47_librts_stability_protocol_2026-06-23.md`

Required supporting files:

- `docs/reports/phoenix_v3_m46_librts_set_b_watch_rows_status_and_next_protocol_2026-06-23.md`
- `docs/reports/phoenix_v3_m31_librts_watch_rows_existing_evidence_analysis_2026-06-23.md`
- `docs/reviews/codex_claude_phoenix_v3_m27_librts_aabb_set_b_triage_and_cold_optix_retain_fix_2ai_consensus_2026-06-23.md`
- `scripts/v3_phoenix_m47_librts_stability_protocol.py`
- `tests/v3_phoenix_m47_librts_stability_protocol_test.py`
- `docs/rebuild/v3/evidence/phoenix_v3_m47_librts_stability_protocol_dry_run_20260623/summary.json`
- `examples/current/research_benchmarks/librts_spatial_index/rtdl_librts_spatial_index_benchmark_app.py`
- `tests/v3_phoenix_librts_aabb_count_runner_test.py`

Requested verdict labels:

- `accept_m47_protocol_no_run_yet`
- `accept_m47_authorize_one_focused_librts_stability_pod`
- `revise_m47_protocol_before_review`
- `reject_m47_wrong_target`

Review questions:

1. Does M47 correctly target the open LibRTS watch surfaces from M46?
2. Are the two scenarios sufficient and not overbroad?
3. Is the alternating V2.14/current order sufficient to reduce drift?
4. Are 8 samples per scenario enough for this focused stability question?
5. Are the green/yellow/red labels strict enough to avoid hiding outliers?
6. Are stop conditions and metadata requirements sufficient?
7. Does the local dry-run/intake harness correctly prevent accidental execution
   and preserve all claim boundaries?
8. Should this packet remain protocol-only, or should it authorize exactly one
   focused POD run?
9. Does it preserve all non-authorization boundaries?

Non-authorization to preserve unless the explicit run-authorization verdict is
chosen:

- no V3 release
- no all-app benchmark run
- no paid POD spend
- no public speedup wording
- no broad V3-over-V2 claim
- no V4 work
- no embedding
- no C ABI
- no true zero-copy claim
