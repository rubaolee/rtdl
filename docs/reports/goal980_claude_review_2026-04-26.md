# Goal980 Claude Review

Date: 2026-04-26
Reviewer: Claude (claude-sonnet-4-6)
Verdict: **ACCEPT**

---

## Scope

This review covers:

1. Whether `graph_analytics` should be blocked for **correctness repair** rather than timing repair.
2. Whether the audit evidence in Goal980 is sufficient to sustain that block.
3. Whether public speedup claims remain unauthorized across all 17 Goal978 rows.

---

## Finding 1 — Correctness block is correctly applied, not a timing block

The prior pre-Goal980 state would have classified `graph_analytics / graph_visibility_edges_gate` as `needs_timing_baseline_repair` because all four baseline artifacts lack a positive comparable phase (`phase_key: null`, `phase_sec: null`). Goal980 changes the blocking reason to `needs_graph_correctness_repair` and the Goal978 `_classify` function checks the Goal980 gate first (lines 90–105 of `goal978_rtx_speedup_claim_candidate_audit.py`), short-circuiting before any timing evaluation. This ordering is correct: timing comparison is meaningless when the outputs being timed are wrong.

The correctness failure is not marginal. At `copies=2` the Embree `visibility_edges` backend reports one more visible edge than the CPU reference (3 vs 2). At `copies=16` and `copies=256` the BFS and `triangle_count` sections show Embree `row_count` stuck at single-copy values (16 and 8 respectively) regardless of scale — at `copies=256` Embree BFS returns 16 discovered vertices while the CPU reference returns 512. This is a systematic graph-scaling bug, not floating-point noise. A speedup claim built on outputs that are not growing with the problem size would be meaningless and misleading.

The `visibility_edges` divergence also grows with scale: the excess visible-edge fraction rises from ~50% extra at `copies=2` (3 vs 2) to ~100% extra at `copies=256` (511 vs 256), consistent with an Embree backend that is applying occlusion queries to an unscaled single-copy geometry regardless of replication factor. Both failure modes (stuck row counts and growing visibility overcount) point to the same root cause: the Embree graph kernels do not correctly handle replicated graph copies.

**Correctness block verdict: correct and well-motivated.**

---

## Finding 2 — Audit evidence is sufficient for the block

Goal980 tests five scales (copies 1, 2, 8, 16, 256) and three sections (bfs, triangle_count, visibility_edges). Four of five scales fail. The single passing scale (`copies=1`) is the degenerate case where replication factor is one; it cannot be used to claim correctness at operational scale.

The comparison uses `row_count` plus section-level aggregate summaries. This is the right granularity for a gate audit: if row counts diverge, full row-level comparison is moot and the block should fire immediately. The systematic BFS row-count failure (Embree returns exactly the single-copy row count at every scale ≥ 16) is unambiguous at the summary level.

The test `test_audit_detects_current_graph_embree_mismatch` hard-codes the expected per-scale failure pattern: `copies=1` ok, `copies=2` mismatch on `visibility_edges`, `copies=16` mismatch on `bfs` and `triangle_count`. The JSON evidence matches these assertions exactly, confirming the test was written against a live run.

One limitation worth noting: summary-level comparison could in principle miss row-level errors that cancel in aggregates, but the BFS row-count discrepancy (512 vs 16) is so large that no cancellation is possible. The evidence is sufficient to block.

**Audit evidence verdict: sufficient.**

---

## Finding 3 — Public speedup claims remain unauthorized

Every row across all 17 Goal978 entries carries `"public_speedup_claim_authorized": false`. Goal980 likewise sets `"public_speedup_claim_authorized": false` and `"public_speedup_claim_authorized_count": 0` at the package level. The Goal978 script hardcodes `public_speedup_claim_authorized: False` unconditionally (line 189), independent of the classification branch taken. The boundary statement in both scripts explicitly states that no authorization is granted here.

The 7 candidate rows are correctly staged for a separate 2-AI public-claim review, not authorized by this audit. The `graph_analytics` row is correctly excluded from candidacy pending correctness repair. No evidence of any path through either script that sets an authorization field to `True` was found.

**Public claim authorization verdict: no unauthorized claims present.**

---

## Summary Table

| Question | Verdict |
| --- | --- |
| Correctness block vs timing block for graph_analytics | Correct — Embree outputs are wrong at scale, not merely slow |
| Audit evidence sufficient | Yes — 4/5 scales fail with stark systematic pattern |
| Public speedup claims unauthorized | Confirmed — 0 authorized across all 17 rows |

---

## Overall Verdict

**ACCEPT**

Goal980 provides reproducible, multi-scale evidence of Embree graph kernel correctness failures and correctly blocks `graph_analytics` for correctness repair rather than timing repair. Goal978's updated classification reflects this accurately. No public speedup claims are authorized anywhere in the system. The next required step is repair of the native graph kernels (Embree multi-copy scaling for BFS, triangle_count, and visibility_edges), followed by same-scale timing recollection before any graph speedup claim review can proceed.
