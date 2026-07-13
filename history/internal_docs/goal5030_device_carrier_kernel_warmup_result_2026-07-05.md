# Goal5030 Device-Carrier Kernel Warmup Result

Date: 2026-07-05

## Purpose

Goal5029 made the device-carrier steady-state route faster than the CPU-carrier route, but first-batch device-carrier cost still blocked using it as a default route.

Goal5030 extends the existing Numba CUDA warmup to cover the device-carrier kernels that dominated the first batch:

- carrier side count;
- carrier side prefix sum;
- carrier side fill;
- side-to-combined copy;
- carrier sentinel fill;
- descriptor pair count consumer.

The warmup uses tiny dummy arrays. It does not run real top4 query rows and does not replay a measured query batch.

## Scope

Changed app-layer warmup code only:

- `Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py`

No RTDL core/native change, no RayJoin core primitive, no paper-text route change.

## Regime

Measured route:

- top4 County x Zipcode;
- six distinct chain-contiguous query batches;
- prepared LSI base session;
- writer-free binary descriptor route;
- device-resident carrier;
- native lexsort;
- prepared carrier arrays;
- host run tables skipped for device-carrier route;
- cold CLI and base-session setup excluded.

## Artifact

- `history/internal_docs/rtdl_goal5030_query6_device_carrier_kernel_warmup_top4.json`

## Result

Structural anchors remain stable:

- Total LSI rows across six batches: `428322`
- First-batch LSI rows: `127926`
- First-batch descriptor pair count: `6316`

### Body Time Matrix

| Route | First batch | Median | Best | Worst | Six-batch sum | Later-batch sum | Later-batch median |
|---|---:|---:|---:|---:|---:|---:|---:|
| Goal5027 CPU carrier | 0.201693s | 0.170494s | 0.143194s | 0.201693s | 1.034264s | 0.832571s | 0.168883s |
| Goal5029 device carrier, skip host run tables | 1.628664s | 0.141181s | 0.129552s | 1.628664s | 2.323421s | 0.694757s | 0.140892s |
| Goal5030 device carrier, carrier-kernel warmup | 0.643663s | 0.140243s | 0.118276s | 0.643663s | 1.318018s | 0.674355s | 0.139702s |

## Interpretation

The warmup worked.

First batch improved from `1.628664s` to `0.643663s`, a reduction of about `0.985s`.

Six-batch total improved from `2.323421s` to `1.318018s`.

Later-batch steady state remains better than CPU carrier:

- CPU carrier later-batch sum: `0.832571s`
- Device carrier after Goal5030 later-batch sum: `0.674355s`
- Relative later-batch win: about `19.0%`

But device carrier still does not beat CPU carrier over the full six-batch session:

- CPU carrier six-batch sum: `1.034264s`
- Device carrier after Goal5030 six-batch sum: `1.318018s`

So this is a real improvement, but still not enough to switch the default route.

## Remaining First-Batch Costs

After carrier-kernel warmup, the first batch is no longer dominated by carrier construction alone. Remaining first-batch costs include:

- `midpoint_points_map0_device_query_points_sec`: about `0.128800s`
- `sort_map0_device_columnar_device_run_bounds_sec`: about `0.102118s`
- `device_resident_descriptor_pair_count_consumer_sec`: about `0.145962s`
- `device_resident_carrier_construction_sec`: about `0.126269s`

The next practical target is to warm the midpoint device-query and device run-bound kernels, then remeasure the first-batch floor.

## Claim Boundary

This does not authorize:

- cold CLI one-shot speedup;
- paper-text route speedup;
- author parity;
- 10x;
- switching v2.14.3 default to device carrier;
- claiming full zero-copy.

It does authorize:

- reporting that app-layer tiny-kernel warmup substantially reduced the device-carrier first-batch penalty;
- continuing the focused first-batch warmup work, with CPU carrier retained as default until full-session evidence beats it.

## Exit Label

`completed_device_carrier_kernel_warmup__first_batch_reduced_default_still_cpu_carrier`
