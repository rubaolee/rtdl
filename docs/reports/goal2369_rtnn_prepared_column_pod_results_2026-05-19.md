# Goal2369 - RTNN Prepared Column Pod Results

Date: 2026-05-19

## Pod

- Host: `root@69.30.85.177`
- SSH port: `22055`
- GPU: NVIDIA RTX A5000
- Driver: `570.211.01`
- Checkout: `/root/work/rtdl_goal2368`
- Commit: `03978783` (`Goal2368 add RTNN prepared pod packet`)
- OptiX SDK: `/root/vendor/optix-sdk`
- CUDA prefix: `/usr/local/cuda-12`

The packet runner was:

```bash
RTDL_ROOT=/root/work/rtdl_goal2368 \
OPTIX_PREFIX=/root/vendor/optix-sdk \
CUDA_PREFIX=/usr/local/cuda-12 \
STEP_TIMEOUT_SECONDS=900 \
REPEAT=3 \
bash scripts/goal2368_rtnn_prepared_column_pod_runner.sh
```

Artifacts are in:

`docs/reports/goal2368_rtnn_prepared_column_pod/`

## Results

All rows completed with `ok: true`. The current native path was the generic
uniform-cell bounded-neighbor traversal, not the diagnostic RT-core traversal.

| Points | Input | Execution | Pack sec | Prepare sec | Runs sec | Warm sec | Rows |
| ---: | --- | --- | ---: | ---: | --- | ---: | ---: |
| 65,536 | records | run-optix | 0.101301 | 0.000000 | 2.132270, 0.721344, 0.647949 | 0.647949 | 206,434 |
| 65,536 | packed-columns | run-optix | 0.083887 | 0.000000 | 0.693044, 0.010280, 0.010584 | 0.010584 | 206,434 |
| 65,536 | packed-columns | prepared-optix | 0.101388 | 0.274732 | 0.306814, 0.010966, 0.011261 | 0.011261 | 206,434 |
| 262,144 | records | run-optix | 0.384547 | 0.000000 | 6.354594, 2.868687, 2.838983 | 2.838983 | 2,512,822 |
| 262,144 | packed-columns | run-optix | 0.405806 | 0.000000 | 0.785405, 0.119432, 0.098917 | 0.098917 | 2,512,822 |
| 262,144 | packed-columns | prepared-optix | 0.408962 | 0.336054 | 0.442171, 0.125407, 0.101737 | 0.101737 | 2,512,822 |

## Ratios

| Points | Record warm / packed warm | Record warm / prepared warm | Packed warm / prepared warm |
| ---: | ---: | ---: | ---: |
| 65,536 | 61.22x | 57.54x | 0.94x |
| 262,144 | 28.70x | 27.91x | 0.97x |

## Interpretation

The packed-column path is the real performance fix on the current v2.2 basis.
It removes repeated tuple/dict normalization and lets the runtime reach the
generic native row stream directly.

The current `prepared-optix` path is not faster than packed `run-optix` at
steady state. That is expected after this measurement: today it reuses Python
packed inputs and prepared Python dispatch, but it does not yet build and retain
a native device-resident 3D neighbor search structure. The phase timings still
show per-run native `prepare` and `upload` work:

- 262,144 packed `run-optix`: native `prepare` 0.011274 s, `upload` 0.004064 s.
- 262,144 packed `prepared-optix`: native `prepare` 0.011685 s, `upload` 0.005964 s.

So the next v2.x primitive work is precise: `prepared_bounded_neighbor_search_3d`
must prepare and reuse the native/device search structure, not just reuse Python
packed records.

## Boundary

This evidence does not authorize RTNN paper equivalence, RT-core acceleration,
broad speedup, or release readiness. It is pod evidence for the current generic
uniform-cell bounded-neighbor path and for the packed/prepared API design.

## Next Work

1. Promote packed-column inputs as the serious-performance path in RTNN-facing
   tutorials and benchmark docs.
2. Build a true native prepared 3D bounded-neighbor handle that keeps the
   search-point structure/device buffers alive across queries.
3. Only after that, retest prepared execution against RTNN at larger scales and
   with separate query/search sets.
