# Goal4436 / V3.0 M39 - Prepared Aggregate-Frontier Numba Pipeline

## Result

M39 adds a prepared Numba continuation for the M36 aggregate-frontier
device-column primitive. This is the no-C++ partner route for the same
Barnes-Hut-style aggregate-frontier vector-sum workload that M38 covers with
CuPy.

Public API:

- `PreparedAggregateFrontierDeviceColumnsWeightedVectorSum2DNumba`
- `prepare_aggregate_frontier_device_columns_weighted_vectors_2d_numba`
- `AGGREGATE_FRONTIER_DEVICE_COLUMNS_PREPARED_WEIGHTED_VECTOR_SUM_2D_NUMBA_CONTRACT`

## Boundary

This is a prepared Numba continuation, not a new engine primitive. The RTDL
engine still emits generic aggregate/exact frontier device columns. The app
partner owns the inverse-square force law and vector accumulation.

CuPy is only the current device-column carrier because M36 exposes OptiX output
through `as_cupy_columns()`. The continuation wraps those device arrays with
Numba's CUDA-array-interface support and runs Numba CUDA JIT kernels for the
math and accumulation. That makes this a no-C++ partner route, but not a
CuPy-free backend route.

- frontier rows are not materialized on host
- contribution rows are not materialized on host
- source columns are passed to M36 by resident Numba device pointer
- output vector columns are reused across hot runs
- no raw C++ or handwritten CUDA file is required

## Claim Boundary

M39 is not a public speedup claim. It is partner-policy coverage: the same
device-column frontier can feed both the fastest practical CuPy route and a
Numba no-C++ reference route.

Conservative flags stay false:

- `rt_core_speedup_claim_authorized = False`
- `whole_app_speedup_claim_authorized = False`
- `public_speedup_claim_authorized = False`
- `true_zero_copy_claim_authorized = False`

## Validation

Local tests:

```text
py -3 -m unittest discover -s tests -p "goal443*.py"
```

Pod tests:

```text
PYTHONPATH=src python -m unittest tests.goal4436_v3_0_m39_prepared_aggregate_frontier_numba_pipeline_test -v
PYTHONPATH=src python -m unittest discover -s tests -p 'goal443*.py'
```

The 8192-point CuPy-vs-Numba timing evidence is recorded in:

- `docs/reports/goal4436_v3_0_m39_prepared_aggregate_frontier_numba_pipeline_8192_2026-06-16.json`

## Toolchain Fix

The first pod run reproduced the known Numba/PTX failure: current Numba emitted
PTX 8.7 while the driver-side linker accepted PTX 8.4. The fix was to apply the
existing partner runbook:

```text
bash scripts/goal3975_current_scale_partner_pod_setup.sh
```

That pins:

- `numba==0.60.0`
- `numpy==2.0.2`
- `nvidia-cuda-nvcc-cu12==12.4.131`
- `cupy-cuda12x==14.1.1`

The measured pod runs exported `CUDA_HOME` and `PATH` to the pip-installed CUDA
12.4 compiler package for Numba while leaving the RTDL OptiX native build as a
separate concern.

## 8192-Point Evidence

Measured configuration:

- 8192 weighted points
- bucket size 64
- theta 0.5
- softening 0.01
- 341 tree nodes
- 3,440,003 frontier rows
- no overflow

Correctness:

- Numba output compared against the CuPy prepared output from the same contract.
- max abs diff x: `3.574918139293004e-14`
- max abs diff y: `3.108624468950438e-14`
- tolerance: `1e-7`
- result: pass

Hot repeated medians:

| Partner | Frontier traversal | Partner continuation | Native + partner | Wall around both calls |
|---|---:|---:|---:|---:|
| CuPy prepared | 0.014247 s | 0.008423 s | 0.022670 s | 0.029037 s |
| Numba prepared | 0.013241 s | 0.001255 s | 0.014498 s | 0.020928 s |

Interpretation:

- Numba is 6.71x faster than CuPy for the partner continuation in this exact
  workload.
- Numba is 1.56x faster than CuPy for the measured native-plus-partner hot
  window.
- The likely reason is structural: the Numba route fuses contribution math and
  grouped accumulation into one CUDA-JIT kernel with direct atomic adds, while
  the CuPy route expresses the same work as several array operations plus
  `bincount`.
- This is an internal partner-route finding for the M36 device-column frontier
  contract, not a broad claim that Numba is always faster than CuPy.
