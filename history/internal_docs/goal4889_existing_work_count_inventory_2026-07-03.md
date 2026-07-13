# Goal4889 Existing Work-Count Inventory

Date: 2026-07-03

Status: `measurement_inventory_complete`

## Purpose

Inventory existing evidence for the post-v2.14 RayJoin hot-path work-count gate.
This is not an optimization goal. It answers whether existing artifacts already
tell us why RTDL's hot path is far slower than AuthorPatch:

- more candidate/test work; or
- similar work count but slower work per candidate/test.

## Primary Dataset

Australia representative Section 5.7:

```text
left:  /workspace/goal4848_rep/current_osm_au/lakes_Australia_current_osm_Point.cdb
right: /workspace/goal4848_rep/current_osm_au/parks_Australia_current_osm_Point.cdb
```

## RTDL Existing Evidence

Primary artifact:

```text
history/internal_docs/goal4886_pod_numba_au_skip_v2_summary.json
```

Known RTDL data/work counts:

| Stage | Available count | Value |
| --- | --- | ---: |
| Map0 input points | loaded data | 14,788,065 |
| Map1 input points | loaded data | 992,505 |
| Map0 input edges | loaded data | 14,430,155 |
| Map1 input edges | loaded data | 941,375 |
| LSI output rows | `lsi_row_count` | 13,452 |
| LSI sorted rows map0 | `xsect_sorted_counts.map0` | 13,452 |
| LSI sorted rows map1 | `xsect_sorted_counts.map1` | 13,452 |
| Vertex PIP map0 in map1 query points | native timing `point_count` | 14,788,065 |
| Vertex PIP map0 positive faces | native timing `positive_face_count` | 193,846 |
| Vertex PIP map1 in map0 query points | native timing `point_count` | 992,505 |
| Vertex PIP map1 positive faces | native timing `positive_face_count` | 30,538 |
| Midpoint PIP map0 query points | native timing `point_count` | 1,707 |
| Midpoint PIP map0 positive faces | native timing `positive_face_count` | 920 |
| Midpoint PIP map1 query points | native timing `point_count` | 2,752 |
| Midpoint PIP map1 positive faces | native timing `positive_face_count` | 1,824 |

Known RTDL times from the same artifact:

| Stage | Time |
| --- | ---: |
| LSI public rows | 5.666642814874649 s |
| Vertex PIP map0 in map1 outer phase | 10.700430862605572 s |
| Vertex PIP map0 in map1 native traversal | 9.784154503 s |
| Vertex PIP map1 in map0 outer phase | 1.5591728761792183 s |
| Vertex PIP map1 in map0 native traversal | 1.52976916 s |
| Midpoint PIP map0 native traversal | 0.065761965 s |
| Midpoint PIP map1 native traversal | 0.059341061 s |

## New Goal4889 LSI Probe

Because the Goal4886 harness did not record LSI native timings, I ran a
measurement-only LSI probe on the same POD and copied the result to:

```text
history/internal_docs/goal4889_lsi_probe_summary_2026-07-03.json
```

Command boundary:

- no `src/rtdsl/**` edits;
- no `src/native/**` edits;
- no comparator changes;
- no prepared/fused implementation;
- LSI only, not full overlay.

Result:

| Field | Value |
| --- | ---: |
| left_edge_count | 14,430,155 |
| right_edge_count | 941,375 |
| lsi_row_count | 13,452 |
| lsi_wall_sec | 6.28831684589386 |
| native `candidate_count_pass` | 0.00289391 s |
| native `candidate_write_pass` | 0.002828656 s |
| native `exact_refine` | 2.551892339 s |
| native `emitted_count` | 13,452 |
| native `raw_candidate_count` | 0 |
| native `mode` | `none` |

Important interpretation:

`raw_candidate_count=0` here does **not** mean zero candidate events. Source
inspection shows the current grouped-range row-producing route calls the native
counter with `record_group_candidate_events=false`. Therefore the current ABI
does not expose the LSI group-candidate event denominator for this public row
route.

## AuthorPatch Existing Evidence

AuthorPatch log evidence comes from:

```text
history/internal_docs/goal4886_authorofficial_wall_attempt_invalid_summary.json
history/internal_docs/goal4886_authorofficial_wall_attempt_freshser_cwd_invalid_summary.json
```

The fresh-serialize-cwd log is the relevant phase boundary for the slow
one-shot comparison; the cached log is useful for launch dimensions.

Known AuthorPatch counts from the log:

| Stage | Evidence | Value |
| --- | --- | ---: |
| Map0 chains | log | 357,910 |
| Map0 points | log | 14,788,065 |
| Map0 edges | log | 14,430,155 |
| Map1 chains | log | 51,130 |
| Map1 points | log | 992,505 |
| Map1 edges | log | 941,375 |
| LSI compressed AABBs for map0 | `primitive.h` log | 2,640,424 |
| LSI/PIP compressed AABBs for map1 | `primitive.h` log | 194,026 |
| LSI launch query count | `lsi_rt.h` / `optixLaunch` log | 14,430,155 |
| Vertex PIP map0 launch query count | `optixLaunch` log | 14,788,065 |
| Vertex PIP map1 launch query count | `optixLaunch` log | 992,505 |
| Midpoint PIP map0 launch query count | `optixLaunch` log | 1,707 |
| Midpoint PIP map1 launch query count | `optixLaunch` log | 2,752 |
| Output chain Map0 xsect count | `output_chain.h` log | 13,452 / 11,745 |
| Output chain Map1 xsect count | `output_chain.h` log | 13,452 / 10,700 |

Known AuthorPatch times from the same log family:

| Stage | Time |
| --- | ---: |
| Intersection edges | about 4.8 ms |
| Map0 locate vertices in other map | about 20.9 ms |
| Map1 locate vertices in other map | about 7.3 ms |
| Compute output polygons | about 8.6 ms |
| Write file | about 0.8-0.9 s |

## What Existing Evidence Proves

Existing evidence proves the launch/query counts are comparable:

- LSI: both routes launch over 14,430,155 map0 segments.
- PIP map0: both routes launch over 14,788,065 map0 vertices.
- PIP map1: both routes launch over 992,505 map1 vertices.
- Midpoint PIP launches also match the small midpoint counts.

This already rules out a trivial explanation such as "RTDL launches orders of
magnitude more rays."

## What Existing Evidence Does Not Prove

Existing evidence does **not** expose the decisive denominator:

- LSI candidate/intersection-test count for the RTDL public row route;
- LSI candidate/intersection-test count for AuthorPatch;
- PIP candidate edge/range test count for RTDL;
- PIP candidate edge/range test count for AuthorPatch;
- per-query candidate distribution.

Therefore current evidence cannot yet distinguish:

1. RTDL is slower because it tests many more candidate edges per launched ray;
2. RTDL tests roughly the same candidate work but its native kernel/path is much
   slower per candidate/test.

## Inventory Label

`existing_evidence_has_query_counts_but_not_candidate_test_counts`
