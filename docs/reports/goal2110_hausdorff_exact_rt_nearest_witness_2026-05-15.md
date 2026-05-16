# Goal2110: Exact Hausdorff via OptiX Nearest-Witness Traversal

Date: 2026-05-15

Status: implemented locally and validated on the local Linux OptiX smoke host.

## Why this goal exists

The earlier v2.0 Hausdorff user program had two separate paths:

- `rtdl_v2_user_cuda`: exact Hausdorff distance, but the exact nearest-neighbor
  work is a CuPy/CUDA continuation and does not use RT cores.
- `rtdl_rt_threshold_search`: uses RTDL/OptiX traversal, but returns a
  tolerance-bounded interval rather than an exact nearest-witness result.

That meant the exact v2.0 Hausdorff function was useful as a Python+partner+RTDL
program, but it was not an exact RT-core Hausdorff implementation.

## What changed

This goal adds a generic OptiX prepared-scene primitive:

`rtdl_optix_run_prepared_fixed_radius_nearest_witness_2d`

The primitive takes an already prepared fixed-radius 2-D scene and, for each
query point, returns one nearest witness row:

- `query_id`
- `neighbor_id`
- `distance`

The OptiX implementation traverses the prepared point AABBs with RT traversal,
computes candidate distances in the custom intersection/any-hit program, and
returns the best witness per query. The Python Hausdorff user function then
recomputes the selected witness distance in Python double precision and reduces
the directed results into the final bidirectional Hausdorff distance.

The new public example method is:

`method="rtdl_rt_nearest_witness"`

## User-facing answer

Before this goal:

- exact v2.0 Hausdorff did not use RT cores;
- only the threshold-search decision path used RTDL/OptiX traversal.

After this goal:

- `rtdl_rt_nearest_witness` is an exact Hausdorff path using RTDL/OptiX RT
  traversal to obtain nearest witnesses;
- the exact value and witness indices match the OpenMP, CUDA C++, CuPy, and
  v2.0 user-CUDA baselines on the validation cases below.

## Validation

Host:

- Linux validation host: `192.168.1.20`
- GPU: local GTX 1070 smoke host
- OptiX SDK: `/home/lestat/vendor/optix-dev`
- Build command:
  `make build-optix OPTIX_PREFIX=/home/lestat/vendor/optix-dev`

Commands:

```bash
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so \
  python3 examples/rtdl_hausdorff_v2_function.py \
  --points-a 512 --points-b 512 \
  --method rtdl_rt_nearest_witness --rt-backend optix \
  --compare --warmup 1 \
  --json-out docs/reports/hausdorff_v2_rt_nearest_witness_local_optix_512.json
```

```bash
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so \
  python3 examples/rtdl_hausdorff_v2_function.py \
  --points-a 2048 --points-b 2048 \
  --method rtdl_rt_nearest_witness --rt-backend optix \
  --compare --warmup 1 \
  --json-out docs/reports/hausdorff_v2_rt_nearest_witness_local_optix_2048_warm.json
```

Results:

| Case | Exact RT witness HD | OpenMP match | CUDA C++ match | CuPy match | v2 user-CUDA match | RT elapsed |
| --- | ---: | --- | --- | --- | --- | ---: |
| 512 x 512 | 0.14627873169442843 | yes | yes | yes | yes | 1.073 s |
| 2048 x 2048 | 0.1389899208830002 | yes | yes | yes | yes | 1.026 s |

Artifacts:

- `docs/reports/hausdorff_v2_rt_nearest_witness_local_optix_512.json`
- `docs/reports/hausdorff_v2_rt_nearest_witness_local_optix_2048.json`
- `docs/reports/hausdorff_v2_rt_nearest_witness_local_optix_2048_warm.json`

## Boundary

This is the first exact RTDL/OptiX Hausdorff path in the v2.0 examples, but it
is not yet a claim of X-HD paper-level performance. The current implementation
uses generic prepared point AABBs and returns exact nearest witnesses, but it
does not yet implement the paper's full acceleration strategy:

- no multi-resolution grid-cell grouping;
- no HD estimator/early-break pruning loop;
- no heavy-cell CUDA offload;
- no persistent two-direction prepared-scene cache in the public Python wrapper;
- no large-pod RTX performance claim.

Therefore the correct claim is narrow: exact Hausdorff can now be expressed as a
Python+partner+RTDL program that uses RTDL/OptiX traversal for nearest-witness
discovery. Broader RT-core speedup claims remain blocked until the X-HD-style
algorithmic layer and pod-scale performance evidence exist.
