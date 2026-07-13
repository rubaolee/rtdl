# Goal5226 - ModelNet40 All-400 Operational Controls Result

Date: 2026-07-09

## Verdict

```text
completed_modelnet40_all400_operational_controls_ready
```

Goal5226 does **not** claim that all 400 unique ModelNet40 pairs have been
reproduced. It adds the operational controls required before running that long
job.

## Why This Goal Was Needed

Goal5224 proved a 40-category representative batch:

```text
40 / 40 matched
```

Goal5225 proved the largest public-OFF pairs are feasible:

```text
largest-1: 2.7M-point pair matched
largest-10: 10 / 10 matched
largest-10 route_wall sum: 124.0838s
largest-10 full total sum: 164.0274s
```

Those results make all-400 plausible, but they also show it is a long-running
operation. A single monolithic command would be fragile: a crash, timeout, or
one bad case could discard hours of useful case evidence.

## Implementation

Updated app-owned runner:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_modelnet40_normalized_batch_gate.py
```

New controls:

```text
--start-index / --end-index
--chunk-index / --chunk-size
--skip-completed
--continue-on-error
--aggregate-existing-cases
--goal-label
```

The runner now also writes one per-case artifact:

```text
<output-dir>/cases/<global-index>_<input-a>__<input-b>.json
```

The case index is the global index in the selected all-pair order, not a local
chunk index. This lets separately run chunks aggregate without renumbering or
silently reordering cases.

## Behavior

### Chunked execution

The all-400 selected set can be sliced either by explicit range:

```text
--start-index 0 --end-index 25
```

or by chunk index and size:

```text
--chunk-index 0 --chunk-size 25
```

The two modes are mutually exclusive and fail closed if combined.

### Resume / skip completed

With:

```text
--skip-completed
```

the runner reads the existing per-case JSON and skips only cases whose
`case_matched` is already `true`. Failed or incomplete cases are not skipped.

### Failure capture

With:

```text
--continue-on-error
```

one failing case is recorded as:

```json
{
  "case_matched": false,
  "case_error": {
    "type": "...",
    "message": "..."
  }
}
```

and the runner continues with later cases.

### Aggregation

With:

```text
--aggregate-existing-cases
```

the runner rebuilds a summary from existing per-case artifacts, including:

```text
matched_case_count
failed_case_count
all_cases_matched
selection.total_points_min/max
```

## Validation

Local validation:

```text
py -m py_compile Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_modelnet40_normalized_batch_gate.py tests/goal5223_modelnet40_algorithm_aware_comparator_test.py

py -m unittest tests.goal5223_modelnet40_algorithm_aware_comparator_test
Ran 10 tests OK

py -m unittest tests.goal5223_modelnet40_algorithm_aware_comparator_test tests.goal5219_xhd_off_normalize_input_contract_test tests.goal5203_numpy_point_matrix_input_loader_test tests.goal5205_fast_ascii_ply_matrix_loader_test
Ran 23 tests OK

py Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_modelnet40_normalized_batch_gate.py --help
```

POD validation on `213.173.108.24:13502` via `scripts/current_pod_ssh.py`:

```text
python3 -m py_compile Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_modelnet40_normalized_batch_gate.py tests/goal5223_modelnet40_algorithm_aware_comparator_test.py

python3 -m unittest tests.goal5223_modelnet40_algorithm_aware_comparator_test
Ran 10 tests OK

python3 -m unittest tests.goal5223_modelnet40_algorithm_aware_comparator_test tests.goal5219_xhd_off_normalize_input_contract_test tests.goal5203_numpy_point_matrix_input_loader_test tests.goal5205_fast_ascii_ply_matrix_loader_test
Ran 23 tests OK
```

Note: the POD copy initially lacked
`tests.goal5219_xhd_off_normalize_input_contract_test`; the test file was
uploaded and the same 23-test command then passed. This was a remote workspace
sync gap, not a test failure in the runner.

The tests cover:

```text
algorithm-aware author comparator selection
Hybrid binary requirement
largest-pair selection
chunk selection preserves global case indices
range/chunk mode conflict rejection
case artifact write/read
skip-completed behavior
aggregate-existing-cases behavior
app-owned boundary / no core promotion
```

## Claim Boundary

Allowed:

```text
The ModelNet40 runner is now operationally ready for a chunked all-400 run:
it supports chunking, resume/skip-completed, per-case artifacts, failure
capture, and aggregation.
```

Forbidden:

```text
All 400 unique ModelNet40 pairs are complete.
All 2000 ModelNet40 paper-log records are complete.
Exact paper input byte identity is proved.
ModelNet40 performance reproduction is complete.
Author-vs-RTDL performance ratio or parity is established.
Full X-HD paper reproduction is complete.
```

## Next Step

Run the all-400 unique ModelNet40 pair gate on the POD in chunks, using:

```text
--selection-strategy all_unique_pairs
--max-pairs 400
--chunk-size 25
--skip-completed
--continue-on-error
```

After all chunks finish, run:

```text
--aggregate-existing-cases
```

and write Goal5227 with the all-400 result.
