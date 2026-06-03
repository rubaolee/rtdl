# Goal3187: Segment-Pair Candidate Chunked Append

Date: 2026-06-03

## Purpose

Goal3185 proved native-owned device-resident `left_id` / `right_id` candidate
columns for prepared segment-pair traversal, but the first slice required the
full `left_count * right_count` pair space to fit one uint32 OptiX launch.

Goal3187 removes that single-launch traversal limitation by chunking the left
input and appending all chunks into the same native-owned device columns.

## Code Changes

- The candidate device-column launcher now computes `max_left_per_launch` from
  the prepared right-side primitive count.
- Each chunk launches the same generic segment-pair candidate any-hit pipeline.
- The row counter and candidate-event counter are initialized once and shared
  across launches, so chunks append into the same output columns.
- The output capacity remains uint32-bounded and fail-closed.

## Boundary

This improves the traversal launcher shape. It does not change the semantic
boundary from Goal3185.

It does:

- support chunked append over the same native-owned device columns,
- keep native terminology generic,
- preserve `left_id` / `right_id` candidate columns,
- keep overflow fail-closed.

It does not:

- produce exact intersection witness rows,
- add device-side grouped continuation over the pair columns,
- expand output capacity beyond uint32 rows,
- prove a >4B-pair live pod case,
- prove true zero-copy,
- authorize public speedup wording,
- authorize release.

Boundary flags remain:

- `release_authorized: False`
- `public_speedup_claim_authorized: False`
- `rt_core_speedup_claim_authorized: False`
- `true_zero_copy_claim_authorized: False`

## Validation

Local validation command:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3187_segment_pair_candidate_chunked_append_test tests.goal3185_segment_pair_candidate_device_columns_test
```

Initial status: local source validation is expected first. A pod rebuild should
validate that the refactored launcher still compiles and the Goal3185 live smoke
still passes, but this report does not prove a >4B-pair live pod case.
