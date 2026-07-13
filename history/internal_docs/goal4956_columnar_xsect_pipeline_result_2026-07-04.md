# Goal4956 Result: Columnar Xsect Numeric Pipeline

Date: 2026-07-04

Status: measured useful win; app route added; review pending

## Objective

Goal4956 continues the v2.14.3 RayJoin+Numba generic pipeline work after
Goal4955 showed that descriptor projection alone was real but below the useful
bar.

The tested idea:

```text
Keep RTDL core generic.
Keep RayJoin as an app.
Replace Python OverlayIntersection object materialization/sort with columnar
numeric xsect arrays and NumPy sorting.
Keep the downstream descriptor route writer-free and numeric/binary.
```

This attacks the real remaining pre-fusion costs:

- `intersection_reprojection`
- `sort_map0`
- `sort_map1`
- midpoint-owner bookkeeping

It does not attack Layer 4 traversal fusion.

## Implemented Artifact

Measurement script:

```text
history/internal_docs/goal4956_columnar_xsect_pipeline_measure.py
```

Productized paper-app route:

```text
Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py
```

The productized route is the same writer-free numeric/binary columnar route,
but it is self-contained inside the RayJoin paper app and does not import
`history/internal_docs`.

The script reuses:

- public planar-map LSI pair-id route from the existing RTDL front door;
- public point-location/PIP route;
- Goal4955 projected descriptor carrier/consumer;
- Numba CPU `njit` descriptor aggregation from Goal4955.

It changes only the app-owned internal measurement route:

```text
LSI pair ids
  -> numeric xsect columns: eid0/eid1/display_x/display_y/scaled_x/scaled_y
  -> NumPy columnar sort by edge/dist/tie
  -> columnar midpoint owner bookkeeping
  -> projected descriptor carrier
  -> descriptor-pair count consumer
```

No `src/rtdsl/**` or `src/native/**` files were edited.

## Important Correctness Repair During Goal4956

The first columnar sort attempt was faster but wrong.  It used int64 distance:

```text
dist = dx * dx + dy * dy
```

Scaled coordinates can be around `1e13`, so `dx * dx` overflows int64 and
changes ordering.  The object route used Python integers and did not overflow.

The fixed route uses extended floating precision:

```text
dx = (scaled_x - start_sx).astype(np.longdouble)
dy = (scaled_y - start_sy).astype(np.longdouble)
dist = dx * dx + dy * dy
```

It also preserves the stable Python sort tie behavior with the original xsect
index as the final tie-break.

Regression coverage:

```text
tests/goal4956_columnar_xsect_pipeline_test.py
```

The regression uses overflow-scale synthetic coordinates and verifies the
columnar sort order equals the Python arbitrary-precision reference order.

POD diagnostic also confirmed:

```text
sort side 0 same True
owners side 0 same True
sort side 1 same True
owners side 1 same True
```

## POD Environment

POD:

```text
ssh -i ~/.ssh/id_ed25519_rtdl_codex_current_pod -p 10689 root@213.173.108.15
hostname: 9e6187bee599
GPU: NVIDIA RTX 4000 Ada Generation
native library: /root/rtdl_goal4955/build/librtdl_optix.so
```

Input pair:

```text
br_county_clean_25_odyssey_final.txt
br_soil_ascii_odyssey_final.txt
```

## Performance Result

Artifacts:

```text
history/internal_docs/goal4955_artifacts/goal4956_columnar_fixed_run_*.json
history/internal_docs/goal4955_artifacts/goal4956_pod_comparison_summary_v2.json
history/internal_docs/goal4955_artifacts/section57_overlay_columnar_binary_app_probe_3.json
```

Median writer-free hot path:

| Route | Median seconds | Speedup vs rerun baseline | Speedup vs original 2.921366s |
|---|---:|---:|---:|
| Goal4954-E rerun baseline | 2.947452 | 1.000000x | 0.991150x |
| Goal4955 projected descriptor minimal | 2.597365 | 1.134786x | 1.124742x |
| Goal4956 columnar xsect fixed | 2.309159 | 1.276418x | 1.265121x |

Frozen bars:

```text
useful win: >=1.15x
target win: >=1.5x
```

Decision:

```text
Goal4956 passes the useful-win bar.
Goal4956 does not pass the 1.5x target bar.
```

## Semantic Check

The fixed columnar route preserves the descriptor-result fingerprint against
the baseline route:

```text
pair_count:       28815
total_groups:     64459
total_point_rows: 673371
top_pairs:        match baseline
```

The summary file records:

```text
semantic_check_passed: true
```

The semantic check intentionally compares result fields, not incidental partner
metadata.  Goal4956 uses the Goal4955 Numba descriptor consumer, while the
baseline route has different metadata shape.

## Review Amendments Closed

An independent Lorentz review returned `approve_goal4956_useful_win_pending_productization`
with amendments.  The amendments have been applied:

- The materialization claim is now precise: no full carrier geometry payload
  columns are materialized, but transient display point tuples are still used
  for dedupe counting.
- A regression test now protects the int64-overflow sort fix.
- Claim-boundary fields now explicitly deny public high-performance,
  numeric-route paper byte-equality, and Layer-4 claims.
- The paper-app route now uses public app schemas rather than internal goal
  schemas.

## Boundary

Authorized claim:

```text
The app-owned numeric binary RayJoin route has a measured writer-free hot-path
candidate improvement from 2.947452s to 2.309159s on the current POD, preserving
descriptor-result semantics.
```

Not authorized:

- paper text byte-equality claim for this numeric route;
- public high-performance claim;
- Layer 4 traversal fusion claim;
- CUDA device-resident continuation claim;
- RTDL core primitive claim;
- broad RayJoin paper reproduction performance claim;
- broad RTDL performance claim.

## App Route Smoke

After the internal measurement passed, the route was moved into the paper app:

```text
Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py
```

POD smoke command shape:

```text
PYTHONPATH=src:. python Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py \
  --left br_county_clean_25_odyssey_final.txt \
  --right br_soil_ascii_odyssey_final.txt \
  --summary section57_overlay_columnar_binary_app_probe_1.json \
  --pair-name br_county_soil_public \
  --author-overlay-compute-sec 0.0421 \
  --cache-dir /tmp/rtdl_goal4955_cache
```

POD smoke result:

```text
schema: rtdl.paper_reproduction.rayjoin.section57_columnar_binary.v1
writer_free_hot_sec: 2.358778s
latest app smoke writer_free_hot_sec: 2.347024s
xsect_sorted_counts: side0=20860, side1=20860
pair_count: 28815
total_groups: 64459
total_point_rows: 673371
full_carrier_geometry_payload_columns_materialized: false
transient_display_point_tuples_used_for_dedupe_count: true
public_high_performance_claim_authorized: false
```

This proves the productized app route runs independently of the internal
measurement script.  The three-run performance decision still comes from the
internal fixed-run set above.

## Relationship To The Owner Principle

This route keeps the project principle intact:

```text
RTDL is a generic system.
RayJoin is an app on top of it.
```

Goal4956 does not add a RayJoin-specific RTDL core primitive.  The route is an
app-owned columnar implementation that composes generic RTDL primitives:

- public planar-map LSI pair ids;
- public point-location/PIP;
- columnar app dataflow;
- Numba descriptor aggregation.

## Remaining Gap

Even after Goal4956, the median writer-free hot path is still:

```text
2.309159s / 0.0421s = ~54.85x author overlay-compute comparator
```

So this is a useful v2.14.3 candidate win, not the final high-performance
solution.  Remaining gap is still in non-fused traversal/output-adjacent
pipeline structure.  Layer 4 fusion remains out of scope for this goal.

## Exit Label

Recommended label:

```text
v2_14_3_columnar_pipeline_useful_win_app_route_added_review_pending
```
