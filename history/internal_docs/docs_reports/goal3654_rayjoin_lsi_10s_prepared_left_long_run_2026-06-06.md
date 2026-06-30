# Goal3654 RayJoin LSI 10s Prepared-Left Long Run

Date: 2026-06-06

Verdict: `accept-with-boundary`

## Purpose

Goal3650 measured the 4096-row public county/soil LSI visible-count contract
with a short repeated runner. Goal3654 hardens that evidence with a long
LSI-only run so the RayJoin and RTDL measurements are no longer sub-second
diagnostics.

This goal also adds two runner improvements:

- `--workloads lsi` so long LSI tests do not spend time on the unrelated PIP
  companion row;
- `--rtdl-internal-query-repeat` so RTDL can repeat the prepared-left native
  query inside one prepared session and report both median per-query time and
  measured hot-loop total time.

## Artifact

Machine artifact:

- `docs/reports/goal3654_rayjoin_lsi_10s_prepared_left_a5000/lsi_4096_10s_summary.json`

Pod state:

- source commit: `e32d0f3e`
- GPU: `NVIDIA RTX A5000, 8.6, 580.126.09`
- selected workload: `lsi`
- input left: `br_county_start256_count4096.cdb`
- input right: `br_soil_start256_count4096.cdb`

Repeat protocol:

- RayJoin: warmup `100`, repeat `30000`, process repeats `3`;
- RTDL: outer repeats `3`, internal prepared-query warmup `100`, internal
  prepared-query repeat `100000`.

## Result

| Workload | Count Contract | RayJoin Visible Count | RTDL Count | RayJoin Query Median ms | RayJoin Process Wall Median ms | RTDL Prepared Query Median ms | RTDL Hot-Loop Total Median ms | RTDL / RayJoin Query |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| LSI 4096 | matching visible segment-pair count | 4977 | 4977 | 0.353115 | 12941.675941 | 0.100411 | 10312.220677 | 0.284x |

The long-run packet therefore records:

- count parity: `4977` RayJoin visible LSI count and `4977` RTDL count;
- RayJoin process wall evidence: median `12.94 s` over three process repeats;
- RTDL hot-loop evidence: median `10.31 s` over three internal prepared-query
  repeat groups;
- per-query timing ratio: RTDL prepared-left median is about `3.52x` lower than
  RayJoin's reported query median for this narrow visible-count contract.

## Interpretation

This is the cleanest current RayJoin LSI evidence because it combines:

- public CDB inputs;
- the larger 4096-row same-slice county/soil pair;
- matching visible segment-pair count;
- prepared-left reuse inside a native generic segment-pair count primitive;
- 10-second-class hot-loop totals rather than millisecond-only timing.

The measured improvement comes from the generic prepared-left route:

- right segment-pair acceleration structure is prepared once;
- left segment set is packed and uploaded once into a prepared native handle;
- repeated dense count calls reuse both handles;
- Python keeps RayJoin interpretation and left-id remapping outside the native
  engine.

## Boundary

This goal does not authorize:

- release readiness;
- public speedup wording;
- broad RT-core speedup wording;
- whole-app benchmark claims;
- true zero-copy claims;
- full RayJoin paper reproduction claims;
- extending the LSI visible-count result to PIP, overlay, or full RayJoin
  assignment semantics.

The accepted internal claim is narrow: for the public 4096-row county/soil LSI
visible-count contract, the RTDL prepared-left generic segment-pair route
matches RayJoin's visible count and records a lower long-run prepared-query
median on the A5000 pod.
