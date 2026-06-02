# Goal3037 - Point-Group Nearest Device Columns to Numba Argmax A4000 Pod

Date: 2026-06-02

## Purpose

Goal3037 records the first clean-source composition proof for the v2.6
device-resident continuation direction:

1. The generic OptiX producer writes prepared point-group nearest-witness rows
   into caller-owned CuPy device columns.
2. The generic Numba partner consumer reads those same device columns through
   the neutral handoff and computes a global argmax with stable tie-breaks.
3. Validation copies results to host only to compare against the existing raw
   row-view oracle.

This is not an app wrapper. The producer contract is generic point/group
nearest witness, and the consumer contract is generic `global_argmax_u32_f64`.

## Environment

- Pod: `root@157.157.221.29 -p 19771`
- GPU: NVIDIA RTX A4000, driver 580.159.03
- CUDA: `/usr/local/cuda-12.8`
- OptiX SDK: `/root/vendor/optix-sdk`
- Source commit: `5aebe6e5a80aa8b6783e98bf66a84ec8a58cd468`
- Source dirty state: `[]`
- NumPy: `2.2.6`
- CuPy: `14.1.1`
- Numba CUDA binding: `NUMBA_CUDA_USE_NVIDIA_BINDING=1`
- CUDA Python binding: `cuda-python>=12,<13`
- Minor-version compatibility: disabled

The pod rebuilt the OptiX library from the clean source checkout:

```bash
make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk CUDA_PREFIX=/usr/local/cuda-12.8
```

The focused tests also passed from clean source:

```text
Ran 9 tests in 1.118s

OK
```

## Validation Shape

- Query points: 4,096
- Search points: 6,144
- Point groups: 49
- Radius: `1.414214562373095`

The OptiX producer used:

`rtdl_optix_write_prepared_point_group_nearest_witness_2d_device_columns`

and reported:

- `native_execution_path=prepared_rt_core_point_group_nearest_witness_2d_device_columns`
- `rt_core_accelerated=true`
- `materializes_neighbor_rows=false`
- `output_columns_true_zero_copy_authorized=true`
- `true_zero_copy_authorized=false`

The Numba consumer used:

`global_argmax_u32_f64`

and reported:

- `contract=generic_global_argmax_u32_f64`
- `reduction_strategy=multi_stage_block_reduce_no_global_atomics`
- `neutral_handoff_status=accept`
- `consumer_source_protocols=["cupy", "cupy"]`
- `direct_device_handoff_authorized=true`
- `true_zero_copy_claim_authorized=false`

## Results

The device columns matched the raw row-view oracle exactly:

| Check | Result |
| --- | --- |
| Query ids match raw rows | true |
| Neighbor ids match raw rows | true |
| Distances match raw rows | true |
| Argmax query id matches raw rows | true |
| Argmax row index matches raw rows | true |
| Argmax distance matches raw rows | true |
| Argmax neighbor id matches raw rows | true |

Expected and actual argmax row:

```json
{
  "query_id": 1344,
  "neighbor_id": 5492,
  "distance": 0.02454645186662674,
  "row_index": 1344
}
```

The full artifact is:

`docs/reports/goal3037_point_group_nearest_numba_argmax_a4000_pod_2026-06-02.json`

## Claim Boundary

Goal3037 validates a clean-source primitive composition path. It does not authorize:

- v2.6 release
- public speedup wording
- broad RT-core speedup wording
- whole-app speedup wording
- true-zero-copy wording
- automatic partner selection
- app-specific native-engine behavior

The producer avoids host row materialization on the output side and the Numba
consumer reads partner device columns through the neutral handoff. The path
still uploads host query points and copies scalar/validation data back to host,
so public true-zero-copy wording remains blocked.

## Next Work

The next useful step is to turn this point/group witness plus global argmax
composition into a benchmark-app strategy, then compare it against the current
CuPy grouped-grid reference under the same contract. If the composition is still
slower, the evidence should guide a larger generic active-set/candidate-frontier
primitive rather than another app-specific native path.
