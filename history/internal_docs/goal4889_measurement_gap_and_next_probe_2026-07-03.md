# Goal4889 Measurement Gap And Next Probe

Date: 2026-07-03

Status: `instrumentation_required_before_implementation`

## Direct Answer

We do **not** yet have the work-count denominator Claude requested.

We have:

- matched query/launch counts;
- RTDL phase timings;
- AuthorPatch phase timings;
- RTDL accepted row/positive-face counts;
- AuthorPatch compressed AABB counts.

We do not have:

- RTDL LSI candidate/test count for the public row-producing route;
- RTDL PIP edge/range test count;
- AuthorPatch LSI candidate/test count;
- AuthorPatch PIP edge/range test count;
- per-query candidate distribution.

Therefore the next high-performance branch is not authorized yet.

## Why Existing Counters Are Insufficient

### LSI

RTDL has a native timing getter that can return `raw_candidate_count`, but the
actual public LSI row-producing route calls:

```text
count_segment_pair_intersection_grouped_range_direct_is_exact_one_pass_optix(..., record_group_candidate_events=false)
```

The Goal4889 LSI probe therefore reported:

```json
"raw_candidate_count": 0,
"emitted_count": 13452,
"mode": "none"
```

This is an instrumentation gap, not a zero-candidate result.

### PIP

RTDL's point-location timing getter returns:

```text
point_upload
traversal
row_download
point_count
positive_face_count
mode
```

It does not return the number of edge/range iterations inside:

```text
__intersection__rayjoin_cdb_point_location()
```

That loop is the relevant work denominator:

```cpp
for (unsigned int segment_index = range.begin; segment_index < range.end; ++segment_index) {
    ...
}
```

### AuthorPatch

AuthorPatch logs expose launch dimensions and AABB counts, but not candidate
events or segment tests.

## Smallest Safe Next Probe

Create a **measurement-only** Goal4890.

Rules:

- no public docs;
- no release claim;
- no product API;
- no prepared/session implementation;
- no row-buffer implementation;
- no Numba partner API implementation;
- no RayJoin fast path;
- no semantics/comparator change.

Allowed:

- temporary instrumented build under a scratch/POD worktree;
- source edits only in the temporary measurement copy;
- artifact output under `history/internal_docs/`;
- exact same Australia representative input.

### RTDL Temporary Counters

LSI:

- expose `group_candidate_count` for the grouped-range direct row path;
- record exact count and emitted row count in the same run.

PIP:

- count total segment-loop iterations in
  `__intersection__rayjoin_cdb_point_location`;
- record query count and positive face count;
- optionally record min/mean/p95/max range length if cheap.

### AuthorPatch Temporary Counters

LSI:

- count candidate/intersection tests in the Section 5.7 LSI RT shader/path.

PIP:

- count point-location candidate edge/range tests in the Section 5.7 vertical
  ray path.

## Decision After Goal4890

If RTDL candidate/test counts are much higher than AuthorPatch:

```text
next_branch = dataflow_pushdown_or_in_traversal_pruning
```

If candidate/test counts are similar but RTDL is far slower:

```text
next_branch = native_kernel_path_tuning
```

If mixed:

```text
next_branch = split_lsi_and_pip_work
```

## Goal-Level Decision Audit

1. **Am I being stupid?**

   The stupid path would be to start implementing fusion or prepared-session
   machinery now. The decisive work-count denominator is still missing.

2. **What would make the decision stupid?**

   Treating "same query count" as "same candidate/test work." They are not the
   same.

3. **Is there another path?**

   Yes. A small measurement-only instrumented build is the controlled path.

4. **Can we start a different path that truly solves the problem?**

   Yes. Start Goal4890 as a probe, not as product work.

## Exit Label

```text
work_count_unavailable__instrumentation_required
```
