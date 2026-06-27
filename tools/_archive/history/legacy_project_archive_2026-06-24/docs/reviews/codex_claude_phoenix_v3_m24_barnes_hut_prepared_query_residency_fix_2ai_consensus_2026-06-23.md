# Codex + Claude Consensus: Phoenix V3 M24 Barnes-Hut Prepared Query Residency Fix

Status: accepted with boundary; focused M24 Barnes-Hut blocker closed.

## Inputs

Codex report:

- `docs/reports/phoenix_v3_m24_barnes_hut_prepared_query_residency_fix_2026-06-23.md`

Claude reviews:

- `docs/reviews/claude_phoenix_v3_m24_barnes_hut_prepared_query_residency_fix_review_2026-06-23.raw.md`
- `docs/reviews/claude_phoenix_v3_m24_barnes_hut_prepared_query_residency_fix_followup_2026-06-23.raw.md`

Evidence:

- `docs/rebuild/v3/evidence/phoenix_v3_m24_barnes_hut_current_repro_20260623`
- `docs/rebuild/v3/evidence/phoenix_v3_m24_barnes_hut_v2_14_repro_20260623`
- `docs/rebuild/v3/evidence/phoenix_v3_m24_barnes_hut_current_prepacked_fix_20260623`
- `docs/rebuild/v3/evidence/phoenix_v3_m24_barnes_hut_repeat50_20260623`
- `docs/reports/phoenix_v3_m24_release_wording_gate_after_barnes_fix_2026-06-23.json`

## Consensus

Codex and Claude agree that M24 is accepted with boundary:

- The Barnes-Hut M22/M21 severe-regression blocker is closed for the focused
  Barnes-Hut blocker-row set.
- The accepted technical fix is the generic prepared-query payload API on
  `GenericPreparedFixedRadiusCountThreshold2D`, plus compatible `PackedPoints`
  support for the Embree prepared fixed-radius count-threshold handle.
- Barnes-Hut node coverage is an allowed first user of that generic V3 prepared
  query surface.
- The fix is not an app-specific native engine and not a benchmark-only number
  patch.

Post-fix Barnes-Hut blocker-row geomean:

- fixed current vs V2.14 four-row geomean: `15.811x`
- required floor: `0.900x`
- status: pass

Repeat-50 evidence:

- 32768 bodies: V2.14 query total `2.161036s`; fixed current query total
  `0.008010s`; including one current query prepare, `17.818x`
- 131072 bodies: V2.14 query total `12.044135s`; fixed current query total
  `0.038259s`; including one current query prepare, `22.812x`

Release wording gate:

- `v3_release_wording_gate.py`: pass
- violations: `[]`

## Hard Boundary

This consensus does not authorize:

- V3 release
- broad V3-over-V2 speedup wording
- public speedup wording
- whole-app Barnes-Hut force-solver speedup claims
- all-app rerun claims
- external zero-copy, embedding, C ABI, or multi-language host claims

The accepted claim is narrower:

- generic V3 prepared fixed-radius query payload reuse improves Barnes-Hut
  node-coverage prepared/repeated-query work
- single-query use is slower than V2.14 at the tested sizes because the current
  route pays a visible query-prepare cost
- the prepared payload amortizes after roughly four repeated queries per
  prepared query payload

The single-query boundary must be carried into any later release-adjacent
documentation that cites this M24 result:

- 32768 bodies: current query prepare plus one hot query is about `0.113719s`,
  slower than V2.14's single-query `0.041552s`
- 131072 bodies: current query prepare plus one hot query is about `0.491206s`,
  slower than V2.14's single-query `0.296358s`

## Decision Audit

1. Was I foolish?

   No. The closure follows POD evidence, a generic implementation, local/POD
   tests, release wording gate, Claude review, and Claude follow-up acceptance.

2. If yes, what actions made the decision foolish?

   The foolish action would have been to count the hot-query number as whole-app
   speedup, hide the single-query penalty, skip the wording gate, or close M24
   without the Claude follow-up.

3. Was there another path that avoided being stuck on that idea?

   Yes. Instead of chasing native OptiX traversal, the work measured packing vs
   native time and moved to the prepared-query API path after evidence showed
   native traversal was already fast.

4. Can I now try a different path that truly solves the problem?

   Yes. M24 closes this blocker with boundary. The next path is to move to the
   next M22 blocker rather than running all-app prematurely.

## Next Work

Do not run all-app solely because M24 closed. Continue the blocker queue:

1. LibRTS AABB OptiX watch row at `0.802964x`
2. remaining row-level correctness failures from M22
3. only after focused blockers close, rerun the protocol-level all-app gate
