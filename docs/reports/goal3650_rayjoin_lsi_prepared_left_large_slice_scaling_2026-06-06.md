# Goal3650 RayJoin LSI Prepared-Left Large-Slice Scaling

Date: 2026-06-06

Verdict: `accept-with-boundary`

## Purpose

Goal3647 proved that the RayJoin LSI helper can use the generic prepared-left
segment-set route on a 512-row public CDB slice. Goal3650 checks the same
visible-count contract on the larger public 4096-row county/soil slice.

This goal is still a narrow contract check:

- RayJoin and RTDL are compared on the visible LSI segment-pair count reported
  by the unmodified RayJoin `query_exec` binary;
- RTDL uses the generic prepared right segment-pair index plus generic prepared
  left segment set plus dense count by left id;
- RayJoin interpretation, CDB loading, and benchmark orchestration remain at
  the app layer.

## Artifact

Machine artifact:

- `docs/reports/goal3650_rayjoin_lsi_prepared_left_large_slice_a5000/same_slice_4096_summary.json`

Pod state:

- source commit: `13e40398`
- GPU: `NVIDIA RTX A5000, 8.6, 580.126.09`
- OptiX library: `build/librtdl_optix.so`

Inputs:

- LSI left: `br_county_start256_count4096.cdb`
- LSI right: `br_soil_start256_count4096.cdb`
- PIP control: 512-row county slice, retained only because the shared runner
  reports PIP as a companion row.

Runner settings:

- RayJoin warmup/repeat: `3` / `10`
- RTDL warmup/repeat: `3` / `10`
- RayJoin process repeats: `1`
- RTDL LSI route: `left_id_dense_count`, which now selects the prepared-left
  route in the app helper.

## Result

| Slice | Workload | Count Contract | RayJoin Visible Count | RTDL Count | RayJoin Query Median ms | RTDL Prepared Query Median ms | RTDL / RayJoin |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 512 | LSI | matching visible segment-pair count | 269 | 269 | 0.229534 | 0.182799 | 0.796x |
| 4096 | LSI | matching visible segment-pair count | 4977 | 4977 | 0.393796 | 0.223968 | 0.569x |

The 4096-row result is the stronger current evidence for this narrow LSI count
contract: RTDL matches RayJoin's visible count and the prepared-left query
median is about `1.76x` faster than RayJoin's reported query median
(`0.393796 / 0.223968`).

## Interpretation

The prepared-left route is doing the work we wanted from Goal3645:

- the left segment set is uploaded once into a native prepared handle;
- repeated query calls reuse that handle;
- the app no longer pays host-left upload cost inside each counted query;
- the engine ABI remains generic segment-pair counting, not RayJoin-specific.

The 512-to-4096 progression is useful because the old one-row comparison could
have been dismissed as launch-noise sensitive. At 4096 rows the visible LSI
count rises from `269` to `4977`, while the RTDL/RayJoin query ratio improves
from `0.796x` to `0.569x`.

## Boundary

This goal does not authorize:

- release readiness;
- public speedup wording;
- broad RT-core speedup wording;
- whole-app benchmark claims;
- true zero-copy claims;
- full RayJoin paper reproduction claims;
- extending the LSI count-contract result to PIP, overlay, or full RayJoin
  assignment semantics.

The accepted claim is only that, for the public 4096-row county/soil LSI visible
count contract, the RTDL prepared-left generic segment-pair route matches
RayJoin's visible count and has a lower prepared-query median on the A5000 pod.
