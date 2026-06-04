# Goal3303 RayJoin Scalar-Count Negative Tuning Probes

Date: 2026-06-04

Status: complete; no new default selected.

## Purpose

After Goal3300 showed that materialized boundary-event columns are the wrong
performance route for RayJoin-style PIP counts, Goal3303 checked two tempting
generic scalar-count knobs before doing more native work:

1. enable prepared closed-shape edge layout for the scalar-count PIP path;
2. use `crossing_only` boundary mode in the timed scalar-count lane while still
   validating against inclusive exact count.

Both probes preserve the app-agnostic engine boundary. Neither should become
the current recommended RayJoin PIP route.

## Prepared Edge Layout Probe

Artifact:

- `docs/reports/goal3303_prepared_edge_scalar_count_probe_pod_2026-06-04.json`

Pod:

- GPU: NVIDIA RTX A5000, driver 580.126.09
- RTDL commit: `56a91c8955985acd2ef98964c776444797b7bce9`

Environment:

- `RTDL_OPTIX_POINT_PRIMITIVE_USE_PREPARED_EDGE_LAYOUT=1`

Runner route:

- PIP count mode: `device_filtered_validated`
- query axis: `z_point`
- boundary mode: `inclusive`
- scalar count pipeline: enabled
- repeats: 20 after 4 RTDL warmups

Median same-slice query/count timings:

| workload | RTDL route | RayJoin query median | RTDL prepared query median | RTDL / RayJoin | count contract |
| --- | --- | ---: | ---: | ---: | --- |
| LSI | `left_id_dense_count` | 0.229 ms | 0.306 ms | 1.33x | matching visible count, 269 |
| PIP | scalar count + prepared edge layout | 0.221 ms | 0.421 ms | 1.90x | RayJoin PIP positive count not exposed; RTDL self-validates 1430 |

The native PIP scalar-count launch median was about 0.325 ms. This is slower
than the prior tuned Goal3294 PIP route, which reported about 0.361 ms end-to-end
prepared query median without prepared-edge layout. The prepared-edge loop is
not the win for this slice.

## Crossing-Only Boundary Probe

Command attempted the same scalar-count route with:

`--rtdl-pip-boundary-mode crossing_only`

The runner failed closed during the first PIP warmup:

`validated device-side closed-shape count did not match exact prepared count: 129 != 1430`

No artifact was written for this probe. This confirms inclusive boundary logic
is semantically required for the bounded PIP slice.

## Conclusion

The current recommended PIP performance route remains the Goal3294 tuned
generic scalar-count lane:

`device_filtered_validated + inclusive + z_point + scalar count pipeline`

Goal3303 rules out two easy knobs:

- prepared edge layout is slower on this slice;
- crossing-only boundary mode is invalid.

The next real optimization should target launch/traversal overhead in the
generic scalar-count path, not boundary-event materialization and not boundary
relaxation.

## Boundary

This report does not authorize:

- release;
- public speedup claims;
- RayJoin paper reproduction claims;
- RTDL-beats-RayJoin claims;
- broad RT-core speedup claims;
- true-zero-copy claims.
