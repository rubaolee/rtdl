# Partner Columns With CuPy Or Numba

Status: current v2.10 source-tree tutorial.

Goal: learn when CuPy or Numba belongs in a Python+RTDL program.

## Partner Choice Is Explicit

RTDL does not auto-select a partner for the user. The Python app chooses:

```text
RTDL primitive only
RTDL primitive + CuPy continuation
RTDL primitive + Numba continuation
CPU or NumPy reference
```

Use a partner when the primitive returns typed columns and your app needs custom
work over those columns.

## Quick Choice

| Need | Usually choose |
| --- | --- |
| CUDA array algebra, masks, scans, or RawKernel baselines | CuPy |
| Python-source CUDA-style custom kernels without writing RawKernel code | Numba |
| exact scalar or summary already returned by RTDL | RTDL primitive only |
| simple correctness run | CPU or NumPy |

## Example Commands

These commands require a CUDA machine and the matching Python packages.

CuPy continuation:

```bash
PYTHONPATH=src:. python examples/current/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py --mode partner_cupy_grid_components_3d --dataset clustered3d --point-count 4096 --no-validation
```

Numba continuation:

```bash
PYTHONPATH=src:. python examples/current/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py --mode partner_numba_grid_components_3d --dataset clustered3d --point-count 4096 --no-validation
```

Prepared Numba continuation:

```bash
PYTHONPATH=src:. python examples/current/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py --mode partner_numba_prepared_grid_components_3d --dataset clustered3d --point-count 4096 --no-validation
```

## Claim Boundary

Allowed:

```text
This app uses RTDL for fixed-radius summaries and Numba for the selected
component-label continuation.
```

Blocked:

```text
RTDL accelerates arbitrary Numba or CuPy code.
```

For current recommendations, read
[Choosing A Partner For Custom Logic](../../learn/partner_choice_for_custom_logic.md).

## Next

Continue with [Prepared Execution And Measurement](06_prepared_execution_measurement.md).
