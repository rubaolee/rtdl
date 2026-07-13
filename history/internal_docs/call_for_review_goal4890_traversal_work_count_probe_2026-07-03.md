# Call For Review: Goal4890 Traversal Work-Count Probe

Date: 2026-07-03

Requested reviewers: Claude / Antigravity

Requested verdict labels:

- `approve_goal4890_candidate_explosion_result_authorize_generic_pruning_design_goal`
- `approve_with_amendments`
- `block_goal4890_redo_measurement`

## Context

Goal4889 showed that RTDL and AuthorPatch launch the same query counts for the
Australia representative Section 5.7 workload, but did not expose candidate/test
work counts. Antigravity approved closing Goal4889 and authorized Goal4890 as a
temporary measurement-only instrumentation probe.

Goal4890 added temporary counters only in scratch copies and measured the
missing denominator.

## Files To Review

Goal definition:

```text
history/internal_docs/goal4890_temporary_traversal_work_instrumentation_probe_2026-07-03.md
```

Result report:

```text
history/internal_docs/goal4890_traversal_work_count_probe_result_2026-07-03.md
```

RTDL artifacts:

```text
history/internal_docs/goal4890_rtdl_work_count_summary_2026-07-03.json
history/internal_docs/goal4890_rtdl_run_stderr_2026-07-03.log
history/internal_docs/goal4890_rtdl_run_stdout_2026-07-03.json
history/internal_docs/goal4890_rtdl_build_optix.log
history/internal_docs/goal4890_rtdl_measurement_wrapper.py
history/internal_docs/goal4890_apply_rtdl_instrumentation.py
history/internal_docs/goal4890_rtdl_measurement_instrumentation.applied.patch
```

AuthorPatch artifacts:

```text
history/internal_docs/goal4890_author_run_stderr_2026-07-03.log
history/internal_docs/goal4890_author_run_stdout_2026-07-03.log
history/internal_docs/goal4890_author_configure.log
history/internal_docs/goal4890_author_build_fresh.log
history/internal_docs/goal4890_apply_authorpatch_instrumentation.py
history/internal_docs/goal4890_authorpatch_measurement_instrumentation.applied.patch
```

Prior approval:

```text
history/internal_docs/antigravity_goal4889_traversal_work_count_measurement_review_2026-07-03.md
```

## Main Result

RTDL output remained byte-equal to the AuthorPatch reference output.

PIP work counts:

| Stage | RTDL segment-loop iterations | AuthorPatch segment tests | RTDL / AuthorPatch |
| --- | ---: | ---: | ---: |
| vertex PIP map0 in map1 | 511,943,147,571 | 84,341,083 | 6,069.9x |
| vertex PIP map1 in map0 | 36,359,368,176 | 18,561,490 | 1,958.9x |
| midpoint PIP map0 | 68,493,462 | 74,815 | 915.5x |
| midpoint PIP map1 | 105,145,275 | 108,540 | 968.7x |

LSI:

- RTDL: 292,195 grouped-range candidate events.
- AuthorPatch: 4,886,533 segment tests.
- Caveat: these are not identical semantic units, so do not over-interpret LSI
  as a direct ratio.

## Proposed Interpretation

The next high-performance branch should be:

```text
candidate_explosion__dataflow_pushdown_or_in_traversal_pruning_next
```

The measured dominant gap is not Python, not host transfer, and not output
writing. The public RTDL PIP primitive is testing orders of magnitude more
segments than AuthorPatch.

## Review Questions

1. Did Goal4890 remain measurement-only and avoid product/public API changes?
2. Are the temporary instrumentation patches correctly scoped to scratch copies?
3. Does the RTDL run prove byte-equality was preserved while measuring?
4. Are the PIP counters comparable enough to support the candidate-explosion
   conclusion?
5. Is the LSI caveat correct: RTDL grouped-range candidate events and AuthorPatch
   segment tests are not direct apples-to-apples units?
6. Does the evidence justify choosing
   `candidate_explosion__dataflow_pushdown_or_in_traversal_pruning_next`?
7. Should native micro-tuning be postponed until candidate work is reduced?
8. Does the packet avoid authorizing RayJoin-specific shortcuts or raw callback
   APIs?
9. What amendments, if any, are required before starting the next design goal?

## Non-Authorization

This review request does not authorize:

- a public performance claim;
- a released product implementation;
- a RayJoin-specific fast path;
- a raw OptiX callback API;
- prepared sessions;
- row-buffer ABI;
- Numba partner API implementation;
- native kernel tuning before candidate reduction is designed and reviewed.
