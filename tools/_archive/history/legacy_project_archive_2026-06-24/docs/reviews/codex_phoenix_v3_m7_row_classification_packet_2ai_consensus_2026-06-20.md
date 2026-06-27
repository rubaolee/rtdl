# Codex 2-AI Consensus: Phoenix V3 M7 Row Classification Packet

Date: 2026-06-20

Status: accepted as current total row-level classification authority.

This is not V3 release authorization.

## Scope

Bounded goal:

```text
Classify all current Phoenix V3 candidate rows into a strict M7 packet, preserve
hard negative facts, and prevent internal evidence from being read as release
evidence.
```

Primary packet:

```text
docs/rebuild/v3/phoenix_v3_m7_row_classification_packet_2026-06-20.md
docs/rebuild/v3/phoenix_v3_m7_row_classification_packet_2026-06-20.json
```

Generator and tests:

```text
scripts/v3_phoenix_m7_row_classification_packet.py
tests/v3_phoenix_m7_row_classification_packet_test.py
```

## External Review

External reviewer:

```text
Claude (claude-sonnet-4-6)
```

Review file:

```text
docs/reviews/claude_phoenix_v3_m7_row_classification_packet_review_2026-06-20.md
```

Claude verdict:

```text
approve
P0 issues: none
P1 issues: 5
2ai_consensus_authorized: true
```

Claude's bottom line:

```text
The packet correctly classifies all 19 rows as not-M7-qualified, preserves every
required hard negative fact in machine-readable form, and is verified by an
idempotency test against the committed JSON.
```

## P1 Follow-Up Applied Before Consensus

Two low-risk P1 improvements were applied before this consensus:

1. Capability-level blockers for `prepared_graph_chunk` and `ranked_summary`
   were expanded to include the full blocker sets already present in focused
   intake evidence.
2. The idempotency test now compares `focused_evidence`,
   `capability_summaries`, and `capability_scope_notes`, not only summary and
   row classifications.
3. A `vector_accumulation` scope note now records that current M6 evidence
   exercises vector accumulation through `aggregate_frontier` rows, but no
   route-map row can promote `vector_accumulation` independently without a
   route-map update or explicit subsumption review.

Remaining P1 items are tracked as future release-gate work:

- final wording gate must expand beyond the current hard-coded first-pass file
  list before release;
- RTNN still needs multi-run variance evidence before any `ranked_summary` M7
  promotion.

## Evidence Accepted

The packet classifies 19 current candidate rows across 10 apps and 9 named
generic capabilities.

Accepted classification:

```text
status: m7_classification_packet_not_release
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
Phoenix M7-qualified release rows: 0
```

Hard negative facts preserved:

- M4 M10 is not a clean pass and system Python packaging remains open.
- M5 RayJoin author RT is faster than RTDL OptiX on the recovered PIP author
  comparison.
- M6 fused Numba CUDA is fastest on all current Barnes-Hut rerun scales;
  prepared OptiX is slower and uses mixed timing basis.
- RayDB M28 ratios are hot-query-only and the sum path has 213s+ setup/cold
  cost.
- Triangle prepared-graph rows are synthetic K4 clique ladder rows, not graph
  database or paper-reproduction rows.
- RTNN hot rows win, but OptiX wall timing is slower for all three
  distributions.

## Verification

Focused tests after Claude review and P1 fixes:

```text
py -3 -m unittest tests.v3_phoenix_m7_row_classification_packet_test tests.v3_phoenix_route_capability_map_test tests.v3_release_wording_gate_test
14 tests OK
```

Release wording gate:

```text
py -3 scripts/v3_release_wording_gate.py --pretty
status: pass
violations: []
release_authorized: false
public_speedup_claim_authorized: false
```

V3 rebuild matrix:

```text
py -3 scripts/run_test_matrix.py --group v3_rebuild
23 modules / 88 tests OK
```

Note: local Python still prints `Could not find platform independent libraries
<prefix>` before test output, but the commands exit 0 and the suites pass.

## Consensus Decision

Codex accepts Claude's review and the applied P1 hardening.

This bounded packet is closed only as:

```text
current total row-level classification authority
```

It is not closed as:

- V3 release authorization;
- public performance wording;
- broad V3-over-V2 speedup evidence;
- paper reproduction;
- whole-application speedup;
- any M7-qualified release row.

The next Phoenix V3 work is to choose exactly one reusable generic capability
and try to promote it through a focused M7 packet, or keep V3 in rebuild status.

## Goal-Level Decision Audit

Decision: close the M7 row-classification packet after Claude approval, P1
hardening, and local verification.

1. Was I foolish?

   No. The closure is bounded, externally reviewed, tested, and keeps all
   release/public claim flags false.

2. If yes, what actions made the decision foolish?

   The foolish action would have been calling this a V3 release or using the
   largest OptiX/Embree ratios as public speedup claims. This consensus does
   neither.

3. Was there another path?

   Yes. I could have skipped classification and started tuning the largest
   ratio row. That would risk repeating the earlier route-first mistake.

4. Can I now try a different path that actually solves the problem?

   Yes. The correct path is now explicit: promote one reusable generic
   capability through a focused M7 packet with row-level evidence, wording, and
   external review.
