# Codex 2-AI Consensus: Phoenix V3 Triangle Prepared-Graph Candidate Intake

Date: 2026-06-20

Status: bounded Triangle intake packet closed as reviewed internal candidate
evidence only.

This is not V3 release authorization, not Triangle M7 row qualification, and
not public RT-Graph, graph-database, or paper-reproduction wording.

## Inputs

External review:

```text
docs/reviews/claude_phoenix_v3_triangle_prepared_graph_intake_review_2026-06-20.md
verdict: approve-with-required-fixes
P0 findings: none
P1 findings: four clarity/guard fixes
```

Review request:

```text
docs/reviews/call_for_review_phoenix_v3_triangle_prepared_graph_intake_2026-06-20.md
```

Primary evidence:

```text
docs/rebuild/v3/phoenix_v3_triangle_prepared_graph_intake_2026-06-20.md
docs/rebuild/v3/evidence/phoenix_v3_triangle_prepared_graph_20260620/triangle_prepared_graph_intake_summary.json
docs/rebuild/v3/evidence/v3_claim_grade_all_benchmarks_calibrated_20260620/summary.json
```

## Claude Review Result

Claude approved the intake after P1 fixes and found no P0 blockers.

Required P1 fixes:

1. Add wall-timing ratios to the `pairs[]` JSON and markdown table.
2. Add `hot_query_vs_wall_timing_ratio_not_characterized_for_release` to the
   M7 blocker list.
3. Add tests guarding M7 blocker completeness.
4. Add a capability-status qualifier so `prepared_graph_chunk` is read as a
   candidate taxonomy label, not a closed M113/M120 executor linkage.

All four P1 items were fixed before this consensus was written.

## Verified Facts

The focused Triangle intake extracts four rows from the all-app calibrated
artifact:

- Embree and OptiX for `triangle_count_rt_graph_2a1_cliques_20000`;
- Embree and OptiX for `triangle_count_rt_graph_2a1_cliques_80000`.

Accepted internal facts:

```text
status: internal_triangle_prepared_graph_candidate_not_m7
generic_capability: prepared_graph_chunk
generic_capability_status: candidate_executor_linkage_not_closed
row_count: 4
group_count: 2
all_rows_ok: true
all_match_oracle: true
all_phase_timing_accept: true
same_contract: true
same_metric_source: true
optix_rt_core_and_embree_non_rt_core: true
release_authorized: false
public_speedup_claim_authorized: false
m7_qualified: false
```

Rows:

| Workload | Hot OptiX / Embree | Wall OptiX / Embree | Boundary |
| --- | ---: | ---: | --- |
| K4 clique ladder, 20,000 cliques | 116.060x | 1.677x | internal candidate only |
| K4 clique ladder, 80,000 cliques | 347.232x | 6.342x | internal candidate only |

The wall ratios are intentionally recorded because the hot-query wins are much
larger than end-to-end wall timing. Any release-row promotion must handle that
gap explicitly.

## Verification

Focused Triangle test:

```text
py -3 -m unittest tests.v3_phoenix_triangle_prepared_graph_intake_test
Ran 5 tests
OK
```

Release wording gate:

```text
py -3 scripts/v3_release_wording_gate.py --pretty
status: pass
violations: []
release_authorized: false
public_speedup_claim_authorized: false
```

Full V3 rebuild matrix:

```text
py -3 scripts/run_test_matrix.py --group v3_rebuild
module_count: 21
Ran 76 tests
OK
```

The local Python installation prints `Could not find platform independent
libraries <prefix>` before these runs, but the commands return success and the
test bodies pass.

## Codex Consensus

Codex agrees with Claude's post-fix verdict.

The Triangle packet may be accepted only as reviewed internal candidate
evidence because:

- it extracts real non-toy all-app calibrated Triangle rows;
- both scales use the same generic RT-Graph 2A1 ray-triangle weighted-any-hit
  contract;
- both scales match the triangle-count oracle;
- Embree and OptiX use the same primary metric source;
- phase timing validates under the saved V2.4 phase contract;
- Embree is correctly non-RT-core and OptiX is RT-core accelerated;
- all public/release claim flags remain false;
- the synthetic K4 clique-ladder boundary is explicit;
- wall-time ratios are now visible beside hot-query ratios.

## Closure Boundary

This bounded Triangle intake closes only at this level:

```text
reviewed internal candidate evidence: accepted
prepared_graph_chunk executor linkage: not closed
M7-qualified release row: no
V3 release authorization: no
public speedup wording: no
graph-database claim: no
RT-Graph paper reproduction claim: no
Phoenix M7-qualified release rows: 0
```

Future Triangle work should either keep this packet internal or build a real M7
row packet that resolves the blockers:

- synthetic fixture versus paper dataset;
- graph-database/full-app scope;
- author/paper comparison boundary;
- M113/M120 prepared-graph executor linkage;
- hot-query versus wall-time characterization;
- fresh row-level public review.

## Goal-Level Decision Audit

Decision: close the Triangle focused intake as reviewed internal candidate
evidence after Claude review and P1 fixes.

1. Was I foolish?

   The corrected closure decision is not foolish. It keeps strong Triangle
   numbers visible but prevents them from becoming release claims.

2. If yes, what actions made the decision foolish?

   The foolish risk was initially omitting wall-time ratios from the pair table,
   which made 116x/347x easier to misread as end-to-end performance.

3. Was there another path?

   Yes. I could have rerun the pod immediately or promoted the all-app rows
   directly. Both would skip the classification gap.

4. Can I now try a different path that actually solves the problem?

   Yes. The current path classifies the existing serious Triangle rows, exposes
   the M7 blockers, and keeps the next work focused on real promotion criteria
   instead of headline ratios.
