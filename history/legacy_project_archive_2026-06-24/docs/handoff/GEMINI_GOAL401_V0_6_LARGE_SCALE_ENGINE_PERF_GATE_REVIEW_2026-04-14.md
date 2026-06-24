# Gemini Review Request: Goal 401 — v0.6 Large-Scale Engine Performance Gate

Please review Goal 401 in the corrected RT `v0.6` branch.

Read first:

- `docs/goal_401_v0_6_large_scale_engine_perf_gate.md`
- `docs/reports/goal401_v0_6_large_scale_engine_perf_gate_2026-04-14.md`
- `src/rtdsl/graph_datasets.py`
- `src/rtdsl/graph_perf.py`
- `scripts/goal401_large_scale_rt_graph_perf.py`
- `tests/goal401_v0_6_large_scale_engine_perf_gate_test.py`

Important context:

- This is the corrected SIGMETRICS-2025-aligned RT graph line, not the older
  rolled-back standalone graph-runtime line.
- Goal 400 already closed bounded PostgreSQL-backed all-engine correctness.
- Goal 401 is the first bounded large real-data performance gate.
- The corrected RT graph line currently measures bounded RT-kernel steps, not
  an end-to-end whole-graph RT runtime. Review it on that honest basis.

Please evaluate:

1. Whether the new loader/perf harness code is technically coherent.
2. Whether the PostgreSQL setup/query split is measured honestly.
3. Whether the report’s claims match the actual implementation and evidence.
4. Whether Goal 401 should be accepted within its stated honesty boundary.

Write the review to:

- `docs/reports/gemini_goal401_v0_6_large_scale_engine_perf_gate_review_2026-04-14.md`

Expected output:

- short verdict
- findings first if there are problems
- otherwise a concise acceptance review
