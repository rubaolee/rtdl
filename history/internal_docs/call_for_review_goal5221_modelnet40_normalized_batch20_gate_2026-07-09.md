# Call For Review: Goal5221 ModelNet40 Normalized Batch20 Gate

Date: 2026-07-09

Please strictly review Goal5221.

Primary report:

```text
history/internal_docs/goal5221_modelnet40_normalized_batch20_gate_result_2026-07-09.md
```

Evidence artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5221_modelnet40_normalized_batch20_summary_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5221_modelnet40_normalized_batch20_artifacts_2026-07-09.tar.gz
```

Implementation:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_modelnet40_normalized_batch_gate.py
```

## Context

Goal5220 matched 5 / 5 ModelNet40 normalized-public-OFF cases. Goal5221 extends
the batch to 20 unique pairs, preferring distinct categories.

The script now passes paper-log `NumPointsPerCell` into the author rerun via
`-n_points_cell`, because using the author default is not the paper-branch
run configuration.

## Key Evidence

Summary:

```text
selected_count = 20
matched_case_count = 19
all_cases_matched = false
```

Nineteen cases:

```text
author normalized HDResult == paper-branch HDResult
author normalized MBRs match paper log
RTDL normalized route matches author within 1e-6
```

One failing case:

```text
range_hood_0124.off -> range_hood_0004.off
paper log HDResult              = 0.46497631072998047
author current XHD rerun        = 0.466653436422348
author-paper diff               = 0.0016771256923675537
RTDL normalized route           = 0.46497629417671404
RTDL-paper diff                 ~= 1.6553e-08
RTDL-current-author-rerun diff  ~= 0.001677142245633978
MBR match                       = true
```

The original paper-branch log for the failing case reports `Algorithm=Hybrid`
inside the repeat payload, while the current author rerun reports
`Algorithm=XHD`. A quick current-binary `-variant clover` probe aborts with CUDA
illegal memory access, so it is not usable comparator evidence.

## Requested Verdict Labels

Choose one:

```text
approve_goal5221_modelnet40_batch20_partial_with_rangehood_mismatch
approve_with_required_amendments
revise_goal5221_before_using_as_modelnet40_provenance
block_due_to_invalid_batch_or_overclaim
```

## Review Questions

1. Does the evidence support the 19 / 20 matched count?

2. Does the report correctly avoid hiding the one failing `range_hood` case?

3. Is the `range_hood` failure correctly characterized as an
   author-rerun/comparator-regime mismatch rather than a simple public-data
   failure, given that RTDL matches the paper-log scalar while current author
   XHD rerun does not?

4. Is it correct to call ModelNet40 a "strong reconstruction candidate" but
   not a complete all-pair reproduction?

5. Does passing `-n_points_cell` from the paper log fix the earlier author
   default-parameter mismatch, and is the remaining failure still real?

6. Does the report preserve the principle that OFF/normalize/paper-log
   parameter handling is app-owned and RTDL core remains generic?

7. Does the report avoid author-vs-RTDL performance ratios and full-paper /
   exact-dataset overclaims?

8. Is the recommended next step correct: investigate the `range_hood`
   Algorithm=Hybrid vs current XHD rerun mismatch before broadening the batch?

## Expected Answer Shape

```text
Verdict:
<one requested verdict label>

Blocking findings:
- ...

Required amendments:
- ...

Non-blocking notes:
- ...

Answers:
1. ...
...
8. ...
```

## Non-Authorization Boundary

This review must not authorize:

```text
ModelNet40 full reproduction complete;
all ModelNet40 pairs match;
range_hood failure resolved;
exact paper dataset identity proved;
author-vs-RTDL speedup or parity;
full X-HD paper reproduction complete.
```
