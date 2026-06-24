# Goal3304 Current-Best RayJoin Same-Slice Packet

Date: 2026-06-04

Status: complete with RTX A5000 pod evidence; optimization gap remains.

## Purpose

Goals3300 and 3303 ruled out three tempting RayJoin PIP tuning directions:

- materialized boundary-event rows plus grouped count;
- prepared closed-shape edge layout for scalar count;
- `crossing_only` boundary mode.

Goal3304 refreshes the current recommended same-slice RayJoin comparison at
latest `main` after those negative probes. This packet is the current
best-known RTDL v2.8 basis for RayJoin-style scalar count timing, not a release
or speedup claim.

## Pod Evidence

Artifact:

- `docs/reports/goal3304_current_best_rayjoin_same_slice_pod_2026-06-04.json`

Pod:

- GPU: NVIDIA RTX A5000, driver 580.126.09
- RTDL commit: `c312903ac30ec166432288ada88b145a05cd8eab`
- Status: `pass_with_optimization_gap`
- Source state: clean tracked checkout plus untracked local data/artifact files
  on the pod

Runner route:

- LSI count route: `left_id_dense_count`
- PIP count mode: `device_filtered_validated`
- PIP query axis: `z_point`
- PIP boundary mode: `inclusive`
- PIP scalar-count pipeline: enabled
- RTDL warmup/repeat: 4 / 20
- RayJoin warmup/repeat/process repeats: 3 / 15 / 5

## Median Same-Slice Query/Count Timing

| workload | RTDL route | RayJoin query median | RTDL prepared query median | RTDL / RayJoin | count contract |
| --- | --- | ---: | ---: | ---: | --- |
| LSI | `left_id_dense_count` | 0.226 ms | 0.275 ms | 1.22x | matching visible count, 269 |
| PIP | `device_filtered_validated + inclusive + z_point + scalar count` | 0.219 ms | 0.336 ms | 1.53x | RayJoin PIP positive count not exposed; RTDL self-validates 1430 |

PIP phase notes:

- validation exact query median: 0.473 ms;
- timed native scalar count pass median: about 0.260 ms;
- point upload median inside native phase samples: about 0.020 ms;
- static shape packing median: 12.456 ms, outside the prepared-query timing
  lane.

## Interpretation

This is the current recommended RayJoin same-slice RTDL route.

It is much better than the Goal3300 boundary-event route for PIP, where
materializing first-boundary event columns took about 3.89 ms end to end and was
17.5x RayJoin query time. It is also better than the Goal3303 prepared-edge
scalar-count probe, which raised PIP prepared-query time to about 0.421 ms.

The remaining PIP gap is now narrow and precise. RTDL's timed scalar-count
native pass is about 0.260 ms, while the full prepared-query lane is about
0.336 ms. The next useful work is not another semantic shortcut. It should
target generic scalar-count launch/packing/residency overhead while preserving
inclusive boundary semantics and keeping the native engine app-agnostic.

The LSI row is also close but not a win: 0.275 ms for RTDL versus 0.226 ms for
RayJoin query time on this same slice. It remains the stronger RTDL row because
the count contract is visible and exactly matched.

## Boundary

This packet does not authorize:

- release;
- public speedup claims;
- RayJoin paper reproduction claims;
- RTDL-beats-RayJoin claims;
- broad RT-core speedup claims;
- true-zero-copy claims.

The native engine remains app-agnostic. RayJoin interpretation stays in the
benchmark app and runner.
