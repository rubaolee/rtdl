# Goal5223 - ModelNet40 Algorithm-Aware Batch20 Gate Result

Date: 2026-07-09

## Verdict

```text
completed_modelnet40_algorithm_aware_batch20_gate__20_of_20_selected_cases_matched
```

Goal5223 turns the Goal5222 finding into the actual batch gate: author
comparator selection now follows the paper-log algorithm payload instead of
using current `main/rt` for every ModelNet40 record.

## Implementation

The app-owned batch runner now optionally reads the original paper-branch log
blob from the author repository:

```text
record["blob"] -> git cat-file -p <blob> -> Running.Repeats[*].Algorithm
```

Comparator selection:

```text
Algorithm=XHD    -> current main author binary, variant=rt
Algorithm=Hybrid -> paper branch author binary, variant=hybrid
```

This remains entirely in the X-HD paper app runner. No RTDL core, native symbol,
or generic API was changed for ModelNet40 or X-HD semantics.

## Evidence Artifacts

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5223_modelnet40_algorithm_aware_batch20_summary_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5223_modelnet40_algorithm_aware_batch20_artifacts_2026-07-09.tar.gz
tests/goal5223_modelnet40_algorithm_aware_comparator_test.py
```

Local/remote validation:

```text
py -m py_compile Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_modelnet40_normalized_batch_gate.py tests/goal5223_modelnet40_algorithm_aware_comparator_test.py
py -m unittest tests.goal5223_modelnet40_algorithm_aware_comparator_test tests.goal5219_xhd_off_normalize_input_contract_test
Ran 10 tests OK

POD:
python3 -m unittest tests.goal5223_modelnet40_algorithm_aware_comparator_test
Ran 6 tests OK
```

## Batch Result

```text
schema = rtdl.paper_reproduction.xhd.modelnet40_normalized_batch_gate.v2
selected_count = 20
matched_case_count = 20
all_cases_matched = true
algorithm_aware_author_comparator_selection = true
```

All 20 selected paper-log records report:

```text
Algorithm = Hybrid
```

Therefore all 20 selected records used:

```text
author binary = /tmp/xhd-goal5222_build_paper/bin/hd_exec
variant       = hybrid
branch        = origin/paper
```

The maximum observed differences are:

```text
max author-vs-paper HDResult diff = 0.0
max RTDL-vs-author HDResult diff  = 1.1170203562116399e-07
MBR matched cases                 = 20 / 20
```

The previously failing case now passes under the correct comparator:

```text
case = 06_range_hood_0124__range_hood_0004
paper log HDResult              = 0.46497631072998047
paper branch Hybrid HDResult    = 0.46497631072998047
RTDL normalized route           = 0.46497629417671404
author-vs-paper diff            = 0.0
RTDL-vs-author diff             = 1.655326642424626e-08
```

## Interpretation

Goal5223 upgrades the ModelNet40 status from:

```text
19 / 20 cases matched with current main/rt, with one comparator mismatch
```

to:

```text
20 / 20 selected ModelNet40 normalized-public-OFF cases match when the author
comparator follows the paper-log algorithm payload.
```

This is strong evidence that official public ModelNet40 OFF files plus the
author `-normalize=true` transform reproduce the selected paper-log scalar
results for these 20 records.

## Claim Boundary

Allowed:

```text
For 20 selected ModelNet40 paper-log records, official public OFF files plus
author-compatible normalization reproduce the paper-log HDResult with an
algorithm-aware author comparator, and RTDL's normalized route matches that
author comparator within 1e-6.
```

Forbidden:

```text
All ModelNet40 paper records are complete.
Exact paper input byte identity is proved.
The whole X-HD paper is reproduced.
Author-vs-RTDL performance ratio or parity is established.
ModelNet40 performance is reproduced.
```

## Next Step

The next goal should decide whether to expand ModelNet40 coverage beyond 20
selected records or stop ModelNet40 as a representative Level-B batch:

```text
Option A: expand to a larger ModelNet40 batch with algorithm-aware comparator;
Option B: freeze ModelNet40 at 20 selected records and move to another paper
          workload family / figure target.
```

Do not report performance ratios until the denominator and runtime regime are
aligned.
