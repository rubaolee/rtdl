# Goal3647 RayJoin LSI Prepared-Left Route Adoption

Date: 2026-06-06

Verdict: `accept-with-boundary`

## Purpose

Goals 3645 and 3646 added and measured a generic prepared-left segment-set
route. Goal3647 wires that route into the RayJoin LSI benchmark helper so the
app-level repeated dense count path no longer calls the older host-left route.

This is still a generic primitive composition:

- prepared right segment-pair index;
- prepared left segment set;
- dense grouped count by left id;
- RayJoin interpretation and left-id remapping remain in Python.

## Artifacts

Machine artifacts:

- `docs/reports/goal3647_rayjoin_prepared_left_app_a5000/app_smoke_summary.json`
- `docs/reports/goal3647_rayjoin_prepared_left_app_a5000/same_slice_summary.json`

Pod source state:

- source commit: `fd7abe1d`
- GPU: `NVIDIA RTX A5000, 8.6, 580.126.09`
- tracked source status: clean

## Route Smoke

The app-level smoke confirms that
`run_rayjoin_prepared_optix_left_id_dense_count_workload(...)` now selects:

`prepared_optix_left_id_dense_count_prepared_left_reuse`

and the native counted route is:

`rtdl_optix_prepared_segment_pair_left_id_count_prepared_left_device_columns`

The app payload records:

- `native_prepared_left_set_enabled: true`;
- `native_prepared_left_set_paid_once: true`;
- `query_pack_paid_in_call: false`.

## Same-Slice Count Comparison

The bounded same-slice runner used the public CDB 512-row slice:

- LSI left: `br_county_start256_count512.cdb`
- LSI right: `br_soil_start256_count512.cdb`
- RayJoin process repeats: `1`
- RayJoin internal warmup/repeat: `3` / `15`
- RTDL warmup/repeat: `5` / `20`

| Workload | Count Contract | RayJoin Visible Count | RTDL Count | RayJoin Query Median ms | RTDL Prepared Query Median ms | RTDL / RayJoin |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| LSI | matching visible segment-pair count | 269 | 269 | 0.229534 | 0.182799 | 0.796x |

For this narrow count contract, RTDL's prepared-left route is about `1.26x`
faster than the RayJoin query timing reported by `query_exec` on this 512-row
slice (`0.229534 / 0.182799`).

The same runner also reports PIP, but PIP is not part of this Goal3647 claim.
The PIP row remains slower and RayJoin does not expose a comparable positive
assignment count in this unpatched upstream binary.

## Boundary

This goal does not authorize:

- release readiness;
- public speedup wording;
- broad RT-core speedup wording;
- whole-app benchmark claims;
- true zero-copy claims;
- full RayJoin paper reproduction claims;
- extending the LSI count-contract result to PIP or overlay.

The accepted claim is narrow: the RayJoin LSI helper now uses the generic
prepared-left segment-set route, and A5000 evidence shows a matching-count
same-slice LSI result where the RTDL prepared query median is lower than
RayJoin's reported query median.
