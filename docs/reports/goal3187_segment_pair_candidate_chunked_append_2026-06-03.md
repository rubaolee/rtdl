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

Focused local validation:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3187_segment_pair_candidate_chunked_append_test tests.goal3185_segment_pair_candidate_device_columns_test tests.goal3181_geometry_relation_row_view_typed_producer_metadata_test tests.goal3183_shape_pair_relation_active_count_test
```

Result:

```text
Ran 20 tests in 0.068s

OK
```

Pod validation:

- Host: `root@69.30.85.131 -p 22063`
- Repo: `/root/rtdl_goal3151`
- Commit: `2822f71a`
- Python: `/root/venvs/rtdl_goal3154/bin/python`
- OptiX library: `/root/rtdl_goal3151/build/librtdl_optix.so`
- Build: `make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk`

Focused pod suite:

```bash
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=/root/rtdl_goal3151/build/librtdl_optix.so \
  /root/venvs/rtdl_goal3154/bin/python -m unittest \
  tests.goal3187_segment_pair_candidate_chunked_append_test \
  tests.goal3185_segment_pair_candidate_device_columns_test \
  tests.goal3183_shape_pair_relation_active_count_test \
  tests.goal3181_geometry_relation_row_view_typed_producer_metadata_test
```

Result:

```text
Ran 20 tests in 0.010s

OK
```

Live pod smoke artifact:

`docs/reports/goal3187_pod_segment_pair_candidate_chunked_append_2026-06-03.json`

| Dataset | Exact Rows | Candidate Column Rows | Candidate Events | Device Columns | Overflow |
| --- | ---: | ---: | ---: | ---: | --- |
| `authored_16_horizontal_by_4_vertical_crossing_segments` | 64 | 64 | 64 | 2 | `False` |

Evidence boundary:

- The chunked loop compiled in the OptiX backend.
- The same live device-column smoke still passed after the launcher refactor.
- This report does not prove a >4B-pair live pod case.
