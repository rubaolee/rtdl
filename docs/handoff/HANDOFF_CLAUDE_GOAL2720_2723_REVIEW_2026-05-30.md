# Handoff: Claude Review for Goals2720-2723 v2.5 Prepared Hit-Stream and Tiered Manifest

Please perform an independent review of the recent v2.5 work.

## Scope

Review these goals:

- Goal2720: prepared RayDB-style native OptiX device hit-stream steady-state path.
- Goal2722: larger RTX A5000 pod evidence for the prepared path.
- Goal2723: tiered 10-benchmark v2.5 manifest that separates Tier A same-contract parity, Tier B per-app/fallback bets, and Tier C RT-core no-regression baselines.

## Files

- `examples/v2_0/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py`
- `scripts/goal2685_raydb_device_hit_stream_handoff_pod_runner.py`
- `src/rtdsl/v2_5_triton_app_migration.py`
- `src/rtdsl/__init__.py`
- `docs/reports/goal2720_raydb_prepared_device_hit_stream_steady_state_2026-05-30.md`
- `docs/reports/goal2720_pod_artifacts/goal2720_raydb_prepared_device_hit_stream_smoke_pod_69_30_85_171_2026-05-30.json`
- `docs/reports/goal2722_raydb_prepared_device_hit_stream_large_scale_pod_evidence_2026-05-30.md`
- `docs/reports/goal2722_pod_artifacts/goal2722_raydb_prepared_device_hit_stream_large_pod_69_30_85_171_2026-05-30.json`
- `docs/reports/goal2723_v2_5_tiered_benchmark_manifest_after_raydb_prepared_evidence_2026-05-30.md`
- `tests/goal2720_raydb_prepared_device_hit_stream_steady_state_test.py`
- `tests/goal2720_raydb_prepared_device_hit_stream_pod_evidence_test.py`
- `tests/goal2722_raydb_prepared_device_hit_stream_large_scale_pod_evidence_test.py`
- `tests/goal2723_v2_5_tiered_benchmark_manifest_test.py`

## Questions

1. Does the prepared path reuse app-owned setup without adding app-specific native engine logic?
2. Do the pod artifacts support the smoke and large-scale prepared-vs-unprepared speedups?
3. Are the claim boundaries still conservative: no true-zero-copy claim, no broad speedup claim, no RayDB reproduction claim, no v2.5 release claim?
4. Does the tiered manifest correctly prevent category errors across the 10 benchmark apps?
5. What are the highest-priority next risks before the next v2.5 implementation goal?

## Required Output

Write the review to:

`docs/reviews/goal2724_claude_review_goal2720_2723_v2_5_prepared_and_tiered_manifest_2026-05-30.md`

Use one of these verdicts:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

State explicitly that this is an independent Claude review distinct from Codex.
