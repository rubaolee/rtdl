# Goal5039 - Prepared Vertex Points And Vertex PIP No-Host-Copy Result

Date: 2026-07-05

Exit label: `completed_prepared_query_batch_per_batch_hot_body_47ms__six_batch_sum_329ms__vertex_pip_no_host_copy_win`

## Purpose

Continue the v2.14.3 RayJoin prepared query-batch writer-free binary route attack after Goal5038 moved the per-query-batch hot body median from about 70ms to about 62ms.

The largest remaining split target was vertex point location / PIP:

```text
vertex_pip_map0 + vertex_pip_map1 ~= 17-18ms
```

This goal removes two avoidable hot-path costs:

1. left-side vertex query points were still prepared inside each batch hot body;
2. vertex PIP still used the host-copy face-id path even when the device-resident binary carrier consumed device face-id columns.

The implementation stays in the RayJoin paper-reproduction app layer and reuses existing public/generic RTDL point-location device-column behavior. It does not add a RayJoin overlay primitive to RTDL core.

## What Changed

### 1. Prepared left vertex point sets per query batch

Added:

```text
--prepared-query-batch-left-vertex-points
```

When used with prepared LSI base sessions and query batches, the session now prepares the left batch vertex point sets once per distinct batch and reuses them in the measured hot body.

This complements the existing prepared right vertex point set:

```text
--prepared-query-batch-right-vertex-points
```

The new route is valid only when query batches are enabled. The app fails closed if the flag is used without:

```text
--prepared-lsi-base-session
--query-chain-batches > 0
--point-location-device-face-columns
```

### 2. Vertex PIP avoids host face-id copies for device-resident carrier

The vertex PIP calls now use:

```text
copy_host=not device_resident_carrier_enabled
```

When the binary carrier is device-resident, downstream carrier construction consumes device face-id arrays directly. The app no longer forces device face-id columns through NumPy just to return to the device-side binary route.

This mirrors the midpoint PIP route, which already used the same device-resident copy policy.

## Code And Tests

Modified:

- `Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py`
- `tests/goal5036_prepared_lsi_query_workspace_test.py`

Local verification:

```text
py -3 -m unittest tests.goal5034_device_carrier_atomic_append_test tests.goal5036_prepared_lsi_query_workspace_test

Ran 10 tests
OK
```

POD verification:

```text
python -m unittest tests.goal5034_device_carrier_atomic_append_test tests.goal5036_prepared_lsi_query_workspace_test

Ran 10 tests
OK
```

POD compile check:

```text
python -m py_compile Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py
```

## Measurement Regime

This is not a cold CLI one-shot result and not a paper-text route.

Measured regime:

```text
prepared LSI base session
6 distinct chain-contiguous query batches
prepared query-batch LSI workspaces
prepared query-batch right vertex point set
prepared query-batch left vertex point sets
device-columnar reprojection/sort
native CUDA/Thrust lexsort
device-resident binary carrier
writer-free descriptor-pair consumer
```

The route excludes cold CLI startup, base-session preparation, and paper text writer cost. It is the prepared query-batch writer-free binary route, not an author-performance parity claim.

## Artifacts

Prepared left vertex points only:

- `history/internal_docs/rtdl_goal5039_left_vertex_points_1_top4.json`
- `history/internal_docs/rtdl_goal5039_left_vertex_points_2_top4.json`
- `history/internal_docs/rtdl_goal5039_left_vertex_points_3_top4.json`
- `history/internal_docs/rtdl_goal5039_left_vertex_points_4_top4.json`
- `history/internal_docs/rtdl_goal5039_left_vertex_points_5_top4.json`

Prepared left vertex points plus vertex PIP no-host-copy policy:

- `history/internal_docs/rtdl_goal5039_vertex_nohost_1_top4.json`
- `history/internal_docs/rtdl_goal5039_vertex_nohost_2_top4.json`
- `history/internal_docs/rtdl_goal5039_vertex_nohost_3_top4.json`
- `history/internal_docs/rtdl_goal5039_vertex_nohost_4_top4.json`
- `history/internal_docs/rtdl_goal5039_vertex_nohost_5_top4.json`

## Structural Anchors

All measured artifact groups preserved the same structural anchors:

```text
lsi_row_counts:
[127926, 21424, 67840, 66414, 56228, 88490]

descriptor_pair_counts:
[6316, 2756, 4723, 3058, 2873, 2987]
```

The order above is the batch execution order in the artifacts. It is the same across Goal5038 and Goal5039 runs.

## Performance Result

All numbers below are per-query-batch median-of-medians across five independent process runs. Each process measures the six query batches.

| Route | hot body | downstream floor | LSI phase | vertex PIP map0 | vertex PIP map1 | carrier | descriptor consumer |
|---|---:|---:|---:|---:|---:|---:|---:|
| Goal5037 old stable native lexsort | 0.070311s | 0.068286s | 0.001870s | 0.004871s | 0.012708s | 0.024918s | 0.011388s |
| Goal5038 final direct+concurrent | 0.062045s | 0.060060s | 0.002038s | 0.004890s | 0.012757s | 0.017556s | 0.011217s |
| Goal5039 left vertex points prepared | 0.056839s | 0.054499s | 0.001831s | 0.001391s | 0.012516s | 0.017250s | 0.010997s |
| Goal5039 final no-host-copy | 0.046956s | 0.045550s | 0.001508s | 0.001095s | 0.003932s | 0.017153s | 0.010889s |

Final per-query-batch improvement over Goal5038:

```text
hot body:         0.062045s -> 0.046956s = 1.32x
downstream floor: 0.060060s -> 0.045550s = 1.32x
vertex PIP map0: 0.004890s -> 0.001095s = 4.47x
vertex PIP map1: 0.012757s -> 0.003932s = 3.24x
```

Final per-query-batch improvement over Goal5037:

```text
hot body:         0.070311s -> 0.046956s = 1.50x
downstream floor: 0.068286s -> 0.045550s = 1.50x
```

The per-query-batch median has now moved from about 70ms to about 47ms in the prepared query-batch writer-free binary regime.

Whole-top4 correction:

```text
47ms is the median single query-batch hot body.
It is not the whole top4 six-batch runtime.
```

The five Goal5039 final runs have six-batch hot-body sums:

```text
0.328842s
0.330271s
0.325430s
0.328800s
0.334660s
```

So the fair whole-top4 prepared binary number for this route is:

```text
median six-batch sum = 0.328842s
```

## Interpretation

The left-vertex prepared-points change mainly removes repeated hot-body preparation for map0 vertex PIP:

```text
vertex PIP map0:
0.004890s -> 0.001391s
```

The vertex PIP no-host-copy change then reduces the remaining vertex point-location cost, especially map1:

```text
vertex PIP map1:
0.012516s -> 0.003932s
```

This is a real prepared query-batch hot-path win. It is not a cold CLI win, not a paper-text writer win, and not a `47ms` whole-top4 claim.

## Remaining Hot-Body Floor

After this goal, the approximate prepared query-batch hot-body floor is:

```text
carrier construction:  ~17.2ms
descriptor consumer:   ~10.9ms
sort/reprojection:     ~9.9ms combined
vertex PIP combined:   ~5.0ms
LSI phase:             ~1.5ms
```

The next honest targets are now carrier construction, descriptor consumer, or sort/reprojection. Vertex PIP is no longer the largest hot-body component.

## Claim Boundary

Authorized:

- prepared query-batch writer-free binary route improved from about 62ms to about 47ms;
- whole-top4 prepared binary six-batch sum is about 0.329s;
- left vertex point sets can be prepared per distinct query batch and reused in the hot body;
- vertex PIP can avoid forced host face-id copies when the device-resident binary carrier consumes device face-id columns;
- structural anchors stayed stable;
- no RTDL core/native RayJoin-specific overlay primitive was added.

Not authorized:

- no claim that v2.14.3 paper-text Section 5.7 now runs in 47ms;
- no claim that the whole top4 prepared binary route runs in 47ms;
- no claim that cold one-shot CLI performance is 47ms;
- no claim that the route beats or matches the author program;
- no claim that all RayJoin routes are fully zero-copy;
- no claim that this optimizes the fast-pack fresh route.

## Closeout

Goal5039 should close as:

```text
completed_prepared_query_batch_per_batch_hot_body_47ms__six_batch_sum_329ms__vertex_pip_no_host_copy_win
```
