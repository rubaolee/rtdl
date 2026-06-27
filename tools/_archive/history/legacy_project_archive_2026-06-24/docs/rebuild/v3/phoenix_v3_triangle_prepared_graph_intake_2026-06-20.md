# Phoenix V3 Triangle Prepared-Graph Candidate Intake

Status: internal candidate intake, not M7 release evidence, 2026-06-20.

This report extracts the Triangle Counting RT-Graph 2A1 rows from the current
all-app calibrated artifact and classifies them against the Phoenix V3
capability rules.

It does not authorize V3 release wording, public speedup wording, graph-database
wording, RT-Graph paper reproduction wording, or Triangle M7 qualification.

## Artifact

Source artifact:

```text
docs/rebuild/v3/evidence/v3_claim_grade_all_benchmarks_calibrated_20260620/summary.json
```

Focused intake:

```text
docs/rebuild/v3/evidence/phoenix_v3_triangle_prepared_graph_20260620/triangle_prepared_graph_intake_summary.json
```

Builder:

```text
scripts/v3_phoenix_triangle_prepared_graph_intake.py
```

## Result

The focused intake passed as internal candidate evidence:

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

## Rows

| Workload | Embree query median | OptiX query median | Hot OptiX / Embree | Embree wall | OptiX wall | Wall OptiX / Embree | Oracle |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| K4 clique ladder, 20,000 cliques | 141.561 ms | 1.220 ms | 116.060x | 4.185 s | 2.496 s | 1.677x | pass |
| K4 clique ladder, 80,000 cliques | 547.887 ms | 1.578 ms | 347.232x | 15.792 s | 2.490 s | 6.342x | pass |

The metric is `timing_ms.query_median_ms` from the same app runner, converted
to seconds in the all-app summary. It is a hot-query metric, not end-to-end
suite timing. The wall ratios are much smaller than the hot-query ratios and
must be characterized before any release-row promotion.

## What This Evidence Means

Allowed reading:

```text
On generated K4 clique-ladder rows, the generic RT-Graph 2A1
ray-triangle weighted-any-hit subpath has internal same-contract OptiX-over-
Embree hot-query wins.
```

Important supporting facts:

- both OptiX and Embree rows use
  `rt_graph_2a1_mapped_to_generic_ray_triangle_any_hit`;
- all rows match the triangle-count oracle;
- phase timing validates under the `rtdl.partner.v2.4` phase contract;
- Embree rows are not RT-core accelerated;
- OptiX rows are RT-core accelerated and use CuPy partner summary;
- claim flags remain blocked in the payload and focused intake.

## What This Evidence Does Not Mean

Forbidden reading:

```text
V3 proves public Triangle/RT-Graph paper reproduction, graph database
acceleration, or a release-authorized prepared-graph M7 row.
```

Current M7 blockers:

- the fixture is a synthetic K4 clique ladder, not a paper dataset;
- the row is not a graph database workload or full triangle-counting app;
- no author-code or paper-dataset comparison is attached;
- the route is not yet closed against the V3 prepared-graph chunk executor;
- hot-query ratios and wall-timing ratios differ materially and are not
  characterized for release;
- no fresh row-level public release review has occurred.

## Decision

This packet is useful, but it is not closure.

The correct next Triangle decision is one of:

- keep this as internal candidate evidence; or
- build a real Phoenix Triangle M7 packet that connects the row to the V3
  prepared-graph chunk executor, preserves the synthetic boundary, adds any
  needed author/paper comparison boundary, and obtains fresh external review.

It should not be promoted directly into user-facing performance claims.

## Goal-Level Decision Audit

Decision: create a Triangle focused intake from the current all-app artifact
instead of immediately rerunning the pod.

1. Was I foolish?

   No. The existing all-app artifact already contains serious Triangle rows;
   the missing work is classification and boundary enforcement.

2. If yes, what actions would have made it foolish?

   It would be foolish to cite the 347.232x ratio as a public RT-Graph or
   Triangle speedup without M7 qualification.

3. Was there another path?

   Yes. I could rerun the pod first, but that would spend time before knowing
   whether the current evidence is structurally admissible.

4. Can I now try a different path that actually solves the problem?

   Yes. The current path extracts the accepted internal facts and makes the M7
   blockers explicit before any additional pod work.
