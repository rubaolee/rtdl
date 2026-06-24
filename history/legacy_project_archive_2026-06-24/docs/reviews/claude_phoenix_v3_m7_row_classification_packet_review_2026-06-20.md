# Review: Phoenix V3 M7 Row Classification Packet

Reviewer: Claude (claude-sonnet-4-6)
Date: 2026-06-20
Verdict: **approve**

---

## Scope Reviewed

Primary files read in full:

- `docs/rebuild/v3/phoenix_v3_m7_row_classification_packet_2026-06-20.md`
- `docs/rebuild/v3/phoenix_v3_m7_row_classification_packet_2026-06-20.json`
- `scripts/v3_phoenix_m7_row_classification_packet.py`
- `tests/v3_phoenix_m7_row_classification_packet_test.py`
- `scripts/v3_release_wording_gate.py`
- `scripts/run_test_matrix.py` (header)
- `docs/rebuild/v3/v3_current_status_2026-06-20.md`
- `docs/rebuild/v3/v3_release_authorization_blockers_2026-06-20.md`
- `docs/rebuild/v3/phoenix_v3_m1_m7_compliance_table_2026-06-20.md`
- `docs/rebuild/v3/README.md`

Evidence verified against source:

- `docs/rebuild/v3/evidence/phoenix_v3_m4_grouped_continuation_20260620/phoenix_v3_m4_evidence_index_2026-06-20.json`
- `docs/rebuild/v3/evidence/phoenix_v3_m5_topology_20260620/m5_topology_intake_summary.json`
- `docs/rebuild/v3/evidence/phoenix_v3_rtnn_ranked_summary_20260620/rtnn_ranked_summary_intake_summary.json`
- `docs/rebuild/v3/evidence/phoenix_v3_triangle_prepared_graph_20260620/triangle_prepared_graph_intake_summary.json`

---

## P0 Issues

**None.**

The packet is not too permissive. No P0 fix is required before Codex writes 2-AI consensus for this bounded classification packet.

---

## Review by Question

### 1. Is the packet too permissive anywhere?

No. Every top-level flag is correctly set to the restrictive value:

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
phoenix_m7_qualified_release_rows: 0
status: "m7_classification_packet_not_release"
```

Every one of the 19 row-classification objects carries `release_authorized: false`,
`public_speedup_claim_authorized: false`, `broad_v3_faster_than_v2_claim_authorized: false`,
`m7_classification: "not_m7_qualified"`, a non-empty `m7_blockers` list, a non-empty
`accepted_internal_facts` list, and a `forbidden_public_reading` string that explicitly
names the forbidden uses. No row is missing any of these fields.

The script in `_classify_row` hardcodes `"m7_classification": "not_m7_qualified"` and
hardcodes all three claim flags to `False`. There is no code path through which the route
map can cause the packet to generate an M7-qualified row without a deliberate script
change. For this packet, that is correct and safe.

The `broad_v2_v3_denominator_rule` block correctly records that:
- the original 46-row geomean of 1.012x is the authoritative broad figure;
- removed or demoted rows must not change the broad denominator;
- any subset geomean must be labeled as a subset.

This prevents the large per-row OptiX/Embree ratios (e.g., 30,489x for
`rayjoin_overlay_seed_authored_tiled_x2048`) from being cited as broad V3 speedup evidence.

### 2. Are the hard negative facts preserved?

All required hard negative facts are present in the packet and verified by the test suite.

**M4 M10 accounting warning and system Python packaging gap:**

The focused evidence entry for `m4_grouped_continuation` records:
- `m10_clean_pass: false` (source: M4 evidence index, row gate=M10, `clean_pass: false`)
- `system_python_packaging_gap_status: "open"` (source: `open_packaging_gap.status` in M4
  evidence index)
- `all_rows_not_m7: true`

`test_focused_evidence_preserves_hard_negative_facts` checks both with
`assertFalse(focused["m4_grouped_continuation"]["m10_clean_pass"])` and
`assertEqual(focused["m4_grouped_continuation"]["system_python_packaging_gap_status"], "open")`.

The `component_union` row-level blockers include `m10_same_stream_has_accounting_warning`
and `system_python_packaging_gap_missing_cupy_numba`.

**M5 RayJoin author RT faster than RTDL OptiX:**

The focused evidence entry for `m5_topology` records:
- `rayjoin_author_rt_is_faster_than_rtdl_optix: true`
- `rayjoin_author_rt_speedup_vs_rtdl_optix_native_traversal: 3.860711740744286`

These are sourced directly from `m5_topology_intake_summary.json`
(`pip_rayjoin_rt_speedup_vs_rtdl_optix_native_traversal: 3.861`). The wall-vs-Query
comparison (5.728x) is documented in the pod evidence and current status; the packet
correctly uses the native-traversal figure as the defensible lower bound.

The test checks `> 3.0`, which is correct as a conservative floor. The `forbidden_public_reading`
on all three M5 rows prohibits RTDL-beats-RayJoin claims. The leading M7 blocker for all
three M5 rows is `rayjoin_author_rt_faster_than_rtdl_optix`.

**M6 fused Numba CUDA fastest, prepared OptiX slower:**

The focused evidence for `m6_barnes_hut` records:
- `fastest_by_scale: {"131072": "numba_cuda_fused", "32768": "numba_cuda_fused", "65536": "numba_cuda_fused"}`
- `prepared_optix_over_fastest: {"131072": 13.912, "32768": 7.328, "65536": 5.120}`
- `timing_basis_mixed: true`

The test checks that all scales show `numba_cuda_fused` as fastest and that
`prepared_optix_over_fastest["131072"] > 10.0`. The leading M7 blocker for the two
`aggregate_frontier` rows is `prepared_optix_not_fastest_route`. These rows also carry the
additional blocker `paired_v2_14_vs_v3_regression_or_route_loss` (added dynamically from
`route_map_release_evidence_status: "blocked_by_paired_regression"`), making them
`priority: "P0_blocked"`.

**RayDB hot-query-only and 213s+ cold cost for sum:**

The focused evidence for `raydb_m28_grouped_reduction` records:
- `comparison_scope: "internal_same_contract_prepared_query_refresh_not_public_speedup"`
- `sum_min_workload_build_sec: 213.265`
- `sum_embree_over_optix: 158.010`
- `count_embree_over_optix: 8.752`

The test checks `sum_min_workload_build_sec > 200.0` and the comparison scope literal.
The two `grouped_reduction` row-level M7 blockers are
`hot_query_only_not_end_to_end_application_timing` and
`sum_workload_build_and_cold_prepare_costs_exceed_213_seconds`. The 213s cost is explicitly
preserved and correctly prevents the 158x sum ratio from appearing as a whole-app speedup.

**Triangle synthetic/non-paper boundary:**

The focused evidence for `triangle_prepared_graph` records:
- `status: "internal_triangle_prepared_graph_candidate_not_m7"`
- `m7_qualified: false`
- `max_hot_optix_speedup_vs_embree: 347.232`
- `min_wall_optix_speedup_vs_embree: 1.677`
- Leading blocker: `synthetic_k4_clique_ladder_not_paper_dataset`

Source evidence confirms the `synthetic_fixture_boundary` field in both triangle rows reads
`"K4 clique ladder; not graph database or paper dataset"`. The test checks the status
string and `m7_qualified: false`. The 347x hot ratio is recorded but blocked by the
synthetic boundary.

**RTNN hot rows win, wall timing regresses:**

The focused evidence for `rtnn_ranked_summary` records:
- `all_hot_optix_faster_than_embree: true`
- `all_wall_optix_slower_than_embree: true`

Source evidence confirms for clustered: OptiX wall = 4.115s vs Embree wall = 2.572s
(wall speedup 0.625x, regression); shell: OptiX wall = 4.003s vs Embree wall = 1.264s
(wall speedup 0.316x); uniform: OptiX wall = 3.939s vs Embree wall = 1.194s
(wall speedup 0.303x). Hot elapsed shows OptiX wins on all three (3.333x, 1.182x, 1.084x).

The test checks both boolean flags. The leading M7 blocker is
`wall_timing_optix_slower_than_embree_for_all_three_distributions`.

All six hard negative facts are preserved, machine-readable, and test-verified. ✓

### 3. Are the tests and wording gate strong enough?

**Tests (5 methods):**

- `test_packet_is_not_release_authorization`: verifies all top-level claim flags and
  row/app counts match committed values.
- `test_every_row_is_blocked_or_internal_with_explicit_blockers`: loops all 19 rows and
  asserts each has correct classification, false flags, non-empty blockers, correct
  forbidden-reading text, and non-empty evidence basis.
- `test_focused_evidence_preserves_hard_negative_facts`: asserts all six hard negative
  facts with concrete values (M10 false, packaging gap open, RayJoin speedup > 3.0,
  M6 fused fastest, RayDB 213s, Triangle internal, RTNN wall regression).
- `test_capability_summaries_keep_reviewed_and_unfocused_routes_separate`: checks
  `review_status` literals for `grouped_reduction`, `point_location_topology_stream`,
  `aggregate_frontier`, `aabb_candidate_stream`, `threshold_summary`; asserts all
  capability summaries have 0 M7 rows and false flags.
- `test_script_rebuilds_packet`: runs the script and verifies `summary` and
  `row_classifications` match the committed JSON exactly; also checks the Markdown
  contains `"Phoenix M7-qualified release rows: 0"`. This is the strongest test: it
  detects script or evidence drift.

**`test_report_keeps_release_boundary_visible`** (Markdown test): asserts 8 key
phrases are present in the Markdown file, including the RTNN wall-regression phrase and
the "No row is yet a public V3 release row" phrase.

The test suite is adequate for this packet's purpose. The idempotency check in
`test_script_rebuilds_packet` is the key safety test: it ensures the committed artifact
and the script output stay in sync.

**Wording gate:**

The gate scans ~45 files for:
- 8 positive overclaim patterns (e.g., "V3 is now released", "V3 broadly beats V2",
  "V4.0.0 is the current", "V3.0.2 is the current")
- 6 post-M150 leak patterns (embedding, SDK, DLPack, etc.) with context-window negation
  exceptions
- 33 required strings that must appear in the joined file content, including all key
  packet status labels and the exact phrases that encode the hard negative facts

The gate is honestly described as a first-pass scanner, not a final release-authorization
scanner. It currently passes (per Codex verification). It is sufficient to block obvious
overclaims during the rebuild period.

**Adequacy for 2-AI consensus on this bounded packet:** Yes. The tests verify correctness
of the committed JSON, the wording gate blocks surface overclaims, and the
`test_script_rebuilds_packet` test guards against script/evidence drift.

### 4. Is the row map correctly strict with zero M7-qualified release rows?

Yes. The route-capability map produces 19 rows across 10 apps and 9 capabilities. Every
row is classified `not_m7_qualified` with at minimum one explicit M7 blocker. The script's
`_classify_row` function hard-codes this result and can only produce M7-qualified rows
after a deliberate code change. The `build_payload` count `len(m7_rows) == 0` is verified
by the test.

The `"next_m7_promotion_candidates"` section names three promotion paths
(`grouped_reduction`, `prepared_graph_chunk`, `threshold_summary_or_collision_flag_stream`)
and lists explicit must-fix requirements for each. This is appropriate: it surfaces the
next work without implying any current authorization.

---

## P1 Issues

These do not block 2-AI consensus. They should be tracked and addressed before M7
promotion of any individual capability.

**P1-1: Capability-level blockers list is truncated for `ranked_summary` and
`prepared_graph_chunk`.**

The `focused_evidence` entries carry the full blocker lists from the intake JSONs:
- `rtnn_ranked_summary`: 8 blockers in focused evidence, 4 in capability summary
  (missing: `paper_equivalent_rtnn_row_false`, `summary_rows_materialized`,
  `prepared_cuda_graph_replay_false`, `public_row_level_external_review_not_done`)
- `triangle_prepared_graph`: 6 blockers in focused evidence, 4 in capability summary
  (missing: `no_author_code_or_paper_dataset_comparison`,
  `public_row_level_external_review_not_done`)

The leading blockers in the capability summaries are correct and the rows remain blocked,
so this is not a permissiveness issue. However, the capability-level blockers should be
kept complete so the next packet author knows the full gap. `CAPABILITY_REVIEW_STATUS` in
the script should be updated to include the full blocker lists before the M7 promotion
packet for either capability.

**P1-2: `vector_accumulation` has no route-map rows.**

The script defines `CAPABILITY_REVIEW_STATUS["vector_accumulation"]` with M6 evidence
backing, and the M1-M7 compliance table lists it as a required generic capability. But no
row in the route-capability map uses `generic_capability: "vector_accumulation"`, so
it does not appear in the packet's capability summaries. The M6 Barnes-Hut evidence covers
the vector accumulation path through `aggregate_frontier` rows. Before any M6/aggregate
capability is promoted to M7, the route map should either add explicit
`vector_accumulation` rows or document why the `aggregate_frontier` rows subsume them.

**P1-3: `test_script_rebuilds_packet` compares `summary` and `row_classifications` but
not `focused_evidence` or `capability_summaries`.**

If an intake summary JSON changes (e.g., M5 topology is rerun and produces a new speedup
ratio), the `test_script_rebuilds_packet` test would pass only if the committed JSON is
also updated. The test is self-referential: it verifies consistency between the script and
the committed JSON, but not that the committed JSON accurately reflects the current intake
files. Expanding the test to also assert specific values from `focused_evidence` (e.g.,
`rayjoin_author_rt_speedup_vs_rtdl_optix_native_traversal`) directly from the rebuilt
packet would close this gap.

**P1-4: Wording gate `DEFAULT_FILES` list will require active maintenance.**

The gate scans a hard-coded list of ~45 files. As tutorials and public docs grow during
the V3 rebuild, new files will not be scanned unless explicitly added. The wording gate's
own description acknowledges this is a first-pass scanner. Before the final V3 release
gate, the `DEFAULT_FILES` list should be expanded to cover all public-facing docs, or
replaced with a directory-walk scan gated by an explicit exclude list.

**P1-5: RTNN lacks multi-run variance evidence.**

The M7 blocker `no_multi_run_variance_evidence` is correctly listed. The current evidence
is a single set of runs per distribution. Before any `ranked_summary` M7 promotion, a
multi-run rerun must provide variance data (standard deviation or IQR) for both hot and
wall timing to support the hot-row win claim.

---

## What the Packet Does Well

- The decision to classify all 19 rows before promoting any row to M7 is correct. It
  prevents the same failure mode that occurred before (internal evidence mistaken for
  release proof).
- The `forbidden_public_reading` field on every row is unusually explicit and useful. It
  names four specific forbidden uses in plain language.
- The script generates both JSON and Markdown from the same payload, and the idempotency
  test verifies they match. This is a good structural choice.
- The `broad_v2_v3_denominator_rule` block correctly anchors the 46-row geomean as the
  authoritative broad figure and prevents subset geomeans from being promoted to broad
  claims.
- The `goal_level_decision_audit` section surfaces the conscious choice not to cherry-pick
  the highest speedup row. This is appropriate for a packet that closes a known
  failure-mode.
- The Barnes-Hut rows carry both `P0_blocked` priority and `paired_v2_14_vs_v3_regression_or_route_loss`
  as an extra dynamically-added blocker. The distinction between `P0` and `P0_blocked`
  correctly signals that these rows have an additional blocker beyond normal M7
  disqualification.

---

## Summary for 2-AI Consensus

The Phoenix V3 M7 Row Classification Packet correctly classifies all 19 current candidate
rows as internal, blocked, or candidate-only. It records zero M7-qualified release rows,
preserves all required hard negative facts, and its tests verify the key facts with
concrete floor values. The wording gate passes. There are no P0 issues.

Codex may write 2-AI consensus for this bounded packet as a total row-level
classification authority with zero M7-qualified release rows.

The P1 issues listed above should be tracked as inputs to the first M7 promotion packet,
not as blockers to consensus on this classification packet.

```text
verdict: approve
p0_issues: 0
p1_issues: 5
release_authorized: false
public_speedup_claim_authorized: false
2ai_consensus_authorized: true
```
