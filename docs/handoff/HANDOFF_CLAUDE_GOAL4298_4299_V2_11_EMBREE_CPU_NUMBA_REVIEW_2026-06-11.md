# Handoff: Review Goal4298/Goal4299 v2.11 Embree CPU + Numba Reference Path

Please perform a read-only independent review of the Goal4298/Goal4299 work.

## Context

The project is starting v2.11. The user asked to finish the Embree CPU plus
Numba/current-partner reference path using local Linux (`192.168.1.20`).

## Files To Review

- `src/rtdsl/current_embree_cpu_partner_reference.py`
- `scripts/rtdl_v2_11_embree_cpu_partner_reference_runner.py`
- `src/rtdsl/partner_adapters.py`
- `examples/current/apps/ml/rtdl_ann_candidate_app.py`
- `docs/reports/goal4298_v2_11_embree_cpu_partner_reference_packet_2026-06-11.md`
- `docs/reports/goal4298_v2_11_embree_cpu_partner_reference_local_linux.json`
- `docs/reports/goal4299_numba_topk_partner_reference_for_v2_11_embree_cpu_packet_2026-06-11.md`
- `tests/goal4298_v2_11_embree_cpu_partner_reference_packet_test.py`
- `tests/goal4299_numba_topk_partner_reference_test.py`

## Facts To Verify

- The registry covers all ten current benchmark apps exactly once.
- Nine rows exercise Embree CPU, and RTNN is honestly recorded as the one
  Numba CPU partner reference row because the current RTNN app has no Embree
  front door.
- The runner sets all-thread CPU env vars, prints per-row progress, supports
  `--only` for resumability, and fails closed on claim-boundary flags.
- Local Linux artifact records `all_pass: true` for all ten rows.
- Goal4299 is generic: it adds `partner="numba"` support to
  `top_k_nearest_points_2d_partner_columns` through Numba pairwise score rows
  plus host-ranked reference top-k, not through an RTNN-specific shortcut.
- The ANN app change is only output conversion for Numba device columns.
- The reports do not authorize release, public speedup, broad RT-core, Intel GPU,
  true-zero-copy, automatic partner selection, or app-specific engine logic.

## Questions

1. Is the Embree CPU + Numba reference path correctly scoped for v2.11?
2. Is the RTNN Numba path honest enough as a reference path, given that top-k
   ranking is still host-materialized after device score rows?
3. Do any names, docs, metadata, or tests overclaim performance, release readiness,
   zero-copy, or RT-core acceleration?
4. Are there any correctness risks in the Numba top-k deterministic ordering
   or ANN output conversion?

## Expected Output

Write the review to:

`docs/reviews/goal4300_claude_review_goal4298_4299_v2_11_embree_cpu_numba_2026-06-11.md`

Use verdict `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.
