# Goal3244: Repeated RTDL/RayJoin Same-Slice Count Runner

Date: 2026-06-03

## Purpose

Goal3242 used one-shot bounded public CDB slices to identify the fair current
comparison contract between upstream RayJoin `query_exec` and RTDL: RTDL
`prepared_optix` count for LSI and PIP. Goal3243's Claude review accepted that
framing but recommended a repeated same-slice median runner before spending more
engineering effort on the gap.

Goal3244 adds that runner and records the first pod execution.

## Artifacts

- Runner: `scripts/goal3244_rayjoin_same_slice_repeated_count_runner.py`
- Test: `tests/goal3244_rayjoin_same_slice_repeated_count_runner_test.py`
- Pod JSON: `docs/reports/goal3244_rayjoin_same_slice_repeated_count_pod_2026-06-03.json`
- Pod stdout: `docs/reports/goal3244_rayjoin_same_slice_repeated_count_pod_2026-06-03.stdout`
- RayJoin process logs: `docs/reports/goal3244_rayjoin_same_slice_repeated_count_pod/`

Pod evidence was collected on an NVIDIA A40 with driver `570.211.01`.
The RTDL commit under test was `43f7860c91e6747248a2442e724100b1f054a7c4`.

## Method

The runner uses upstream RayJoin `query_exec` from `/root/RayJoin/build/bin` and
the same bounded public RTDL CDB slices:

- LSI: `br_county_start256_count512.cdb + br_soil_start256_count512.cdb`
- PIP: `br_county_start0_count512.cdb`

RayJoin is run in RT mode with `-warmup=3`, `-repeat=15`, and five independent
process samples per workload. The runner records RayJoin's reported `Query:` time
directly; the calibration probe showed that this timing does not scale linearly
with `-repeat`, so Goal3244 does not divide it by repeat.

RTDL is run through `prepared_optix` count with two warmups and seven repeats.
The report compares RayJoin's reported query median to RTDL's
`phases_sec.prepared_query_sec` median.

## Results

| Workload | RayJoin RT query median | RTDL prepared count median | RTDL/RayJoin | Count status |
| --- | ---: | ---: | ---: | --- |
| LSI | 0.233793 ms | 1.449205 ms | 6.20x | visible count matches: 269 vs 269 |
| PIP | 0.193946 ms | 1.116930 ms | 5.76x | RTDL count 1430; RayJoin count not printed |

The repeated run confirms that the gap from Goal3242 is real, but slightly
smaller than the one-shot estimate (`~6.7x` became `6.20x` for LSI and `~6.8x`
became `5.76x` for PIP).

## Phase Diagnosis

For LSI, RTDL's median native phase telemetry shows:

- candidate count pass: about `0.096 ms`
- candidate write pass: about `0.052 ms`
- candidate download: about `0.010 ms`
- host exact refine: about `1.121 ms`

So the LSI gap is dominated by the host exact-refine authority path after RT-core
candidate discovery. The next serious LSI optimization should move the exact
count/refine authority onto the device, or provide a reviewed same-contract
device-side exact-count primitive that avoids downloading and refining the
candidate stream on the host.

For PIP, RTDL's median native phase telemetry shows:

- candidate/write traversal: about `0.945 ms`
- candidate download: about `0.011 ms`
- exact refine: about `0.071 ms`

So the PIP gap is mostly in the device candidate/write traversal and output
path, not in host exact refine. The next serious PIP optimization should examine
the prepared point/closed-shape count kernel and whether the count-only contract
can avoid writing/downloading candidate rows when the requested result is just
the positive assignment count.

## Boundary

Goal3244 does not authorize release, public speedup claims, broad RT-core
speedup claims, true zero-copy claims, `RTDL beats RayJoin` claims, or RayJoin
paper-reproduction claims.

The correct conclusion is narrower: RTDL's current generic prepared OptiX count
contracts are correct and repeatable on these bounded public slices, but upstream
RayJoin's specialized RT query path is still faster on the same slices. The gap
is now measured enough to guide concrete engineering work.
