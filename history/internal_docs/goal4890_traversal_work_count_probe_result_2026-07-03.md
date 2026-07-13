# Goal4890 Traversal Work-Count Probe Result

Date: 2026-07-03

## Verdict

Goal4890 completed the temporary measurement probe.

Exit label:

```text
candidate_explosion__dataflow_pushdown_or_in_traversal_pruning_next
```

The decisive result is in PIP / directed point-location, not Python output
writing and not query launch count.

## Boundary

This was a temporary measurement-only instrumentation run:

- no released product API change;
- no public docs/tutorial/release change;
- no prepared-session implementation;
- no row-buffer ABI implementation;
- no Numba partner API implementation;
- no native tuning;
- no callback API;
- no RayJoin fast path.

Temporary code was applied only in POD scratch directories:

- `/workspace/goal4890_rtdl_instr`
- `/workspace/goal4890_author_instr`

## Artifacts

Local artifacts:

- `history/internal_docs/goal4890_temporary_traversal_work_instrumentation_probe_2026-07-03.md`
- `history/internal_docs/goal4890_apply_rtdl_instrumentation.py`
- `history/internal_docs/goal4890_apply_authorpatch_instrumentation.py`
- `history/internal_docs/goal4890_rtdl_measurement_wrapper.py`
- `history/internal_docs/goal4890_rtdl_build_optix.log`
- `history/internal_docs/goal4890_author_configure.log`
- `history/internal_docs/goal4890_author_build_fresh.log`
- `history/internal_docs/goal4890_rtdl_work_count_summary_2026-07-03.json`
- `history/internal_docs/goal4890_rtdl_run_stderr_2026-07-03.log`
- `history/internal_docs/goal4890_rtdl_run_stdout_2026-07-03.json`
- `history/internal_docs/goal4890_author_run_stderr_2026-07-03.log`
- `history/internal_docs/goal4890_author_run_stdout_2026-07-03.log`
- `history/internal_docs/goal4890_rtdl_measurement_instrumentation.applied.patch`
- `history/internal_docs/goal4890_authorpatch_measurement_instrumentation.applied.patch`

## Inputs

Australia representative Section 5.7 input:

- left: `/workspace/goal4848_rep/current_osm_au/lakes_Australia_current_osm_Point.cdb`
- right: `/workspace/goal4848_rep/current_osm_au/parks_Australia_current_osm_Point.cdb`
- AuthorPatch reference output:
  `/workspace/goal4875_section57_au_representative/author_contract_full/author_contract_au_overlay.txt`

## Correctness Gate

RTDL instrumented run remained byte-equal to the AuthorPatch reference output:

```text
byte_equal_to_author: true
```

## Query Counts Still Match

The probe preserved the Goal4889 fact that query/launch counts match:

| Stage | RTDL query count | AuthorPatch query count |
| --- | ---: | ---: |
| LSI query segments | 14,430,155 | 14,430,155 |
| PIP map0 vertices | 14,788,065 | 14,788,065 |
| PIP map1 vertices | 992,505 | 992,505 |
| midpoint PIP map0 | 1,707 | 1,707 |
| midpoint PIP map1 | 2,752 | 2,752 |

So the gap is not caused by RTDL launching more rays/queries.

## Work Counts

### LSI

| Metric | RTDL | AuthorPatch |
| --- | ---: | ---: |
| emitted intersections | 13,452 | 13,452 |
| measured work count | 292,195 grouped-range candidate events | 4,886,533 segment tests |

Important caveat: the LSI work counters are not identical semantic units. RTDL
reports grouped-range candidate events; AuthorPatch reports segment tests in the
shader. This is useful diagnostic evidence, but it should not be read as a
direct apples-to-apples LSI candidate ratio.

### PIP / Directed Point-Location

| Stage | RTDL segment-loop iterations | AuthorPatch segment tests | RTDL / AuthorPatch |
| --- | ---: | ---: | ---: |
| vertex PIP map0 in map1 | 511,943,147,571 | 84,341,083 | 6,069.9x |
| vertex PIP map1 in map0 | 36,359,368,176 | 18,561,490 | 1,958.9x |
| midpoint PIP map0 | 68,493,462 | 74,815 | 915.5x |
| midpoint PIP map1 | 105,145,275 | 108,540 | 968.7x |

This is the decisive result.

## Interpretation

The RTDL hot-path gap is caused primarily by candidate explosion in the current
public directed point-location/PIP primitive.

The current RTDL public PIP route tests vastly more segments per query than the
AuthorPatch OptiX route. That means the next high-performance work cannot be
explained or solved by:

- Python output writer changes;
- host/device materialization cleanup;
- prepared sessions alone;
- row-buffer ABI alone;
- Numba continuation alone.

Those may remain useful engineering hygiene, but they do not attack the dominant
measured cause.

## Next Branch

Authorized next branch:

```text
dataflow_pushdown_or_in_traversal_pruning_next
```

The likely needed work is a generic, non-RayJoin-specific RTDL mechanism that
lets the public point-location primitive avoid testing thousands of irrelevant
segments per query. The design must remain generic:

- no RayJoin-only hidden kernel;
- no raw OptiX callback as public API;
- no public performance claim until a corrected implementation is measured.

Possible forms:

- in-traversal pruning for directed point-location as a generic primitive;
- data-flow pushdown for bounded point-location predicates;
- BVH/grouping construction change so PIP candidate ranges are not enormous.

## Not Authorized

This report does not authorize a product implementation yet. It authorizes a
design goal for a generic PIP candidate-pruning / data-flow pushdown route,
followed by a small proof before any broad performance claim.

## Goal-Level Decision Audit

1. **Am I being stupid?**

   No. Goal4890 measured the missing denominator instead of starting another
   "looks busy" optimization thread.

2. **What would make this decision stupid?**

   Treating the result as permission to write a RayJoin-specific fast path.
   The measured problem is in a generic directed point-location primitive and
   must be solved generically.

3. **Is there another path?**

   Native micro-tuning is not the first path because PIP does 900x-6000x more
   candidate work than AuthorPatch. First reduce work; then tune kernels.

4. **Can we start a different path that truly solves the problem?**

   Yes. Start a new design goal for generic in-traversal pruning / data-flow
   pushdown for directed point-location.
