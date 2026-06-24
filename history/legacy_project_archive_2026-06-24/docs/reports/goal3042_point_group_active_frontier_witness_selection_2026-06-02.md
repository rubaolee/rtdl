# Goal3042 Point-Group Active-Frontier Witness Selection

Date: 2026-06-02

Status: source landed; A4000 pod timing collected; external review pending.

## Purpose

Goal3040 showed that writing all nearest-witness columns and then reducing them
with Numba is correct, but not fast enough for the Hausdorff benchmark. The
main cost is not the final argmax alone: it is that the current exact RT path
still makes too many query rows survive to the continuation phase.

Goal3042 adds the next generic primitive needed for the X-HD-style direction:
a device-resident active frontier over prepared point groups. The primitive is
not Hausdorff-specific. It combines:

- a point/group threshold pass over query points,
- an active mask that stays inside the native/device path,
- a nearest-witness pass that skips inactive queries,
- a generic max-distance reduction that returns only one witness row and one
  active-count scalar to Python.

## Native Contract

New OptiX export:

```text
rtdl_optix_reduce_prepared_point_group_nearest_max_distance_active_frontier_2d
```

Inputs:

- prepared point-group nearest-witness scene,
- query points,
- threshold radius,
- threshold count,
- witness radius.

Outputs:

- one `RtdlFixedRadiusNeighborRow`,
- one active-query count.

The native names stay generic: point group, threshold, active frontier, nearest
witness, max-distance reduction. The native implementation does not contain
Hausdorff, X-HD, or application-specific ABI names.

## Python Contract

`PreparedOptixPointGroupNearestWitness2D` now exposes:

```python
nearest_max_distance_active_frontier_row(
    query_points,
    threshold_radius=...,
    threshold=1,
    witness_radius=...,
)
```

The returned dictionary includes:

- `query_id`,
- `neighbor_id`,
- `distance`,
- `active_count`,
- `native_reduction = "point_group_nearest_max_distance_active_frontier"`,
- `materializes_frontier_on_host = False`.

This is not a true-zero-copy claim. Query points are still packed on the host
for this path. The bounded claim is only that the threshold-derived active
frontier is not materialized back to Python before nearest-witness reduction.

## Hausdorff App Wiring

The Hausdorff research benchmark adds:

```text
rtdl_rt_grouped_active_frontier_nearest_witness
```

The app-level strategy is:

1. Build generic uniform point groups over the target set.
2. Run a seed sample exact nearest-witness reduction to get a lower-bound
   witness distance.
3. Use `threshold_radius = seed_distance - margin`.
4. Ask the native active-frontier primitive to skip source points that already
   have a witness within that threshold radius.
5. Compare the reduced active-frontier witness with the seed witness and return
   the exact directed Hausdorff witness for that direction.

This remains app-level Python orchestration over generic native primitives.

## User-Facing Lab Changes

The multi-method language lab now lists
`rtdl_rt_grouped_active_frontier_nearest_witness` and exposes:

- `--seed-sample-count`
- `--target-points-per-group`

Those knobs are important. If the seed sample is larger than the point set, the
method intentionally falls back to the full reduced nearest-witness path.

## Claim Boundary

- `v2_6_release_authorized`: false.
- Public speedup claim: false.
- RT-core speedup claim: false.
- True-zero-copy claim: false.
- App-specific native-engine logic: false.

The OptiX pod build and same-contract timing run against the current CuPy
grouped-grid reference and current RT raw-row reference are recorded below.

## A4000 Pod Evidence

Pod:

- SSH target: `root@157.157.221.29 -p 19771`
- GPU: NVIDIA RTX A4000
- Driver: 580.159.03
- CUDA prefix: `/usr/local/cuda-12.8`
- OptiX SDK prefix: `/root/vendor/optix-sdk`
- Source commit: `f0b42a1828943de8751084a0d2438b174299fb4b`
- Python for CuPy baseline: `/root/.venvs/rtdl_goal3042/bin/python`
- CuPy: 14.1.1

Validation:

- `make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk` passed.
- Focused source tests passed on pod:
  `tests.goal3042_point_group_active_frontier_witness_selection_test`,
  `tests.goal3033_point_group_nearest_device_columns_test`, and
  `tests.goal3021_l4_optix_cuda126_hausdorff_rt_smoke_test`.
- Small runtime smoke matched OpenMP on distance, direction, source index, and
  target index after preserving original target-column witness mapping.

Timing command shape:

```bash
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so \
  /root/.venvs/rtdl_goal3042/bin/python \
  examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_v2_language_lab.py \
  --method cupy_grouped_grid_rawkernel \
  --method rtdl_rt_grouped_seeded_pruned_nearest_witness \
  --method rtdl_rt_grouped_active_frontier_nearest_witness \
  --method rtdl_rt_grouped_adaptive_raw_nearest_witness \
  --seed-sample-count 1024 \
  --target-points-per-group 512
```

All rows matched the exact reference.

| Points | CuPy grouped-grid sec | Active-frontier RT sec | Adaptive raw RT sec | Host-pruned RT sec | Active / CuPy | Active speedup vs CuPy |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 4096 | 0.004776468 | 0.006584461 | 0.068325735 | 1.339560785 | 1.379x | 0.725x |
| 8192 | 0.008929983 | 0.011395584 | 0.119935546 | 1.330690255 | 1.276x | 0.784x |
| 16384 | 0.032289381 | 0.020904737 | 0.254477752 | 1.320914034 | 0.647x | 1.545x |
| 32768 | 0.079344464 | 0.038273932 | 0.504838568 | 1.347026890 | 0.482x | 2.073x |
| 65536 | 0.300481389 | 0.078558422 | 1.069001242 | 1.364961639 | 0.261x | 3.825x |
| 131072 | 1.101468301 | 0.168522497 | 2.441497014 | 1.481538838 | 0.153x | 6.536x |

Artifact summary:

- `docs/reports/goal3042_active_frontier_perf_a4000_2026-06-02.json`
- per-size JSON rows under
  `docs/reports/goal3042_active_frontier_perf_a4000_2026-06-02/`

## Interpretation

Goal3042 is the first Hausdorff RT path in this lane that crosses the optimized
CuPy grouped-grid baseline on the tested dense synthetic rows. It is still
slower than CuPy at 4096 and 8192 points, but crosses over at 16384 and reaches
6.536x over CuPy at 131072 points on this A4000 run.

The mechanism is exactly the design lesson from the earlier negative probes:
do not materialize all nearest-witness rows and then reduce them. Use a cheap
sample witness to establish a lower-bound threshold, keep the threshold-derived
active frontier on the device, skip safe queries in the RT nearest-witness
launch, and reduce only the active rows to one witness.

This should be treated as bounded internal v2.6 performance evidence until
external review checks the contract, reproducibility, and claim language.
