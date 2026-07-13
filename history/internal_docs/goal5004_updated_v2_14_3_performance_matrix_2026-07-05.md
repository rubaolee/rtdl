# Goal5004 Result: Updated v2.14.3 Performance Matrix

Date: 2026-07-05

## Verdict

```text
completed_v2_14_3_updated_matrix__fresh_headline_corrected__replay_diagnostic_separated
```

Goal5004 updates the v2.14.3 RayJoin writer-free binary-operator performance
matrix after Goal5002 and Goal5003.

It also fixes one measurement-accounting bug in the app route: the
`writer_free_hot_sec` key list did not include the new device midpoint
query-point generation phases. The fresh top4 headline is therefore corrected
from the older undercounted `~4.8s` range to:

```text
fresh one-shot writer-free top4 = 5.003915s
```

This is the accounting-complete v2.14.3 fresh one-shot number for the current
writer-free binary route on top4 County x Zipcode.

## Scope

This goal is a matrix / accounting goal. It does not claim:

- paper text byte equality for the binary route;
- top4 author-performance ratio;
- true query-many;
- author parity;
- full zero-copy;
- Layer 4 in-traversal fusion;
- RayJoin-specific RTDL core optimization.

## Code Accounting Fix

File changed:

```text
Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py
```

The previous `writer_free_hot_keys` always listed:

```text
midpoint_points_map0_columnar_sec
midpoint_points_map1_columnar_sec
```

After Goal4999, the device-resident carrier route uses:

```text
midpoint_points_map0_device_query_points_sec
midpoint_points_map1_device_query_points_sec
```

The old `writer_free_hot_sec` therefore undercounted the new device midpoint
query-point path. Goal5004 fixes the key selection:

```text
device-resident carrier route -> device query-point keys
otherwise                     -> columnar host-pack keys
```

Regression test updated:

```text
tests/goal4999_device_query_point_location_handoff_test.py
```

Local verification:

```text
py -3 -m unittest tests.goal4999_device_query_point_location_handoff_test tests.goal4990_binary_repeat_protocol_test
Ran 6 tests: OK

py -3 -m py_compile Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py
OK
```

The local Python emits the environment warning:

```text
Could not find platform independent libraries <prefix>
```

but exits successfully.

## POD Fresh Run After Accounting Fix

POD:

```text
root@157.157.221.29 -p 25248
repo: /root/rtdl_goal4988
```

Artifact:

```text
history/internal_docs/goal5004_updated_performance_matrix_artifacts_2026-07-05/fresh_after_accounting_fix_top4.json
```

Command:

```text
python Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py
  --left Paper-reproduction-apps/rayjoin-paper/_data/top4_arcgis/top4_county.cdb
  --right Paper-reproduction-apps/rayjoin-paper/_data/top4_arcgis/top4_zipcode.cdb
  --pair-name top4_county_zipcode
  --summary /root/rtdl_goal5004_fresh_after_accounting_fix_top4.json
  --device-columnar
  --bounded-exact-lsi-device-columns
  --bounded-exact-lsi-capacity 1000000
  --point-location-device-face-columns
  --fast-scaled-point-pack
  --device-resident-carrier
```

## Updated Matrix

| Regime | Evidence | Status | Accounting-complete writer-free sec | LSI sec | Downstream sec | LSI rows | Descriptor pairs |
|---|---|---|---:|---:|---:|---:|---:|
| Fresh one-shot top4 | Goal5004 POD run | Product-relevant v2.14.3 binary route | 5.003915 | 2.628660 | 2.375255 | 428322 | 15014 |
| Generic compile-prewarmed top4 | Goal5002 diagnostic | Diagnostic only; prewarm excluded from route window | 4.584897 | 1.750720 | 2.834177 | 428322 | 15014 |
| Same prepared-query replay | Goal4999 repeat5 | Diagnostic only; same input replay, not true query-many | 0.332861 | 0.003082 | 0.329779 | 428322 | 15014 |

### Why The Fresh Number Changed

Older fresh artifacts reported:

```text
writer_free_hot_sec ~= 4.816s
```

but their downstream floor recomputation was about:

```text
LSI + downstream_floor ~= 4.95s
```

The difference came from the missing midpoint device-query-point keys. After the
fix, the fresh POD artifact reports:

```text
writer_free_hot_sec = 5.003915s
downstream_floor_breakdown.writer_free_hot_recomputed_sec = 5.003915s
```

So the headline is now internally consistent.

## LSI Floor Interpretation

Goal5002 showed that the global compile-like LSI cost can be prewarmed:

```text
exact_pipeline_ensure + split_kernel_ensure:
  ~0.99s -> ~0.000001s
```

Goal5003 then showed that the remaining LSI workspace is base/query domain
dependent:

| Workspace probe case | Meaning | Elapsed sec | scaled cache ensure | grouped range ensure |
|---|---|---:|---:|---:|
| first full run after generic compile prewarm | build current input workspace | 1.711297 | 0.706036 | 1.001106 |
| same prepared query replay | same input replay | 0.003114 | 0.000001 | 0.000000 |
| new query, same input, same base | partial same-domain reuse | 0.141655 | 0.138032 | 0.000001 |
| changed scale-domain query | incompatible workspace | 1.473499 | 0.613669 | 0.857943 |
| full query after scale changed back | rebuild full domain workspace | 1.572960 | 0.706045 | 0.862789 |

Decision:

```text
v2.14.3 keeps the fresh LSI workspace cost in the fresh headline.
```

Generic compile prewarm may be a future product feature, but it must be reported
as startup/service preparation, not silently removed from one-shot fresh timing.

## Current v2.14.3 Status

The current writer-free binary route is a real architectural improvement over
the earlier text-output reproduction route:

- no paper text writer;
- LSI pair IDs are emitted as device columns;
- Numba consumes pair columns directly for reprojection;
- directed point-location has device face-id columns;
- midpoint query points are generated on device and handed to native PIP;
- midpoint face IDs are scattered on device;
- the descriptor carrier is built and consumed as a binary descriptor route.

But the current fresh one-shot top4 cost is still:

```text
~5.00s
```

The two dominant components are:

```text
LSI producer / workspace: ~2.63s
downstream binary route: ~2.38s
```

The same prepared-query replay number:

```text
~0.33s
```

is useful as a diagnostic for a fully cached same-input replay, but it is not a
fresh result and not true query-many.

## Next Goal

Recommended next goal:

```text
Goal5005: v2.14.3 Documentation And Release Boundary Update After Corrected Matrix
```

It should update the internal/public-facing wording so that:

- fresh top4 writer-free binary route is `~5.00s`;
- compile-prewarm and prepared replay are marked diagnostic;
- no top4 author ratio is claimed without a measured top4 AuthorOfficial run;
- no true query-many claim is made;
- the binary route is presented as a writer-free app/operator route, not as
  paper text reproduction and not as author-performance parity.

## Exit Label

```text
completed_v2_14_3_updated_matrix__fresh_headline_corrected__replay_diagnostic_separated
```
