# Source-Tree GPU Setup

Status: experimental V4.0 source-tree tutorial.

V4.0 M1 is not a package install path. It is a source-tree GPU route that
requires the checkout, CUDA-capable Python frameworks, and the OptiX native
runtime built in this repository.

## Build And Check

From the repository root on Linux:

```bash
make build-optix
PYTHONPATH=src:. python scripts/v4_0_source_tree_runtime_preflight.py --require-v4-gpu-runtime
PYTHONPATH=src:. python scripts/run_test_matrix.py --group v4_release_candidate
```

The preflight checks:

- the checkout imports `rtdsl` from `src/`;
- CuPy, Numba, PyTorch, and `build/librtdl_optix.so` are present;
- the V4 active and release-candidate gates exist;
- package, PyPI, wheel, stable SDK, and front-door claims remain blocked.

## Editable Checkout

For developer convenience, the source tree can also be made importable from a
temporary or local environment:

```bash
python -m pip install -e .
python scripts/v4_0_editable_install_runtime_probe.py --system-site-packages --run-v4-smoke
```

That command is still source-tree hygiene evidence only. It is not a V4 package,
wheel, PyPI artifact, or stable SDK claim.

## First Route

The V4.0 M1 route is `fixed_radius_count_threshold_2d`.

Inputs are caller-owned CUDA columns:

- `ids`: `uint32`;
- `x`: `float64`;
- `y`: `float64`.

Outputs are caller-owned CUDA columns:

- `query_ids`: `uint32`;
- `neighbor_counts`: `uint32`;
- `threshold_flags`: `uint32`.

The output shape is fixed: one row per query. The route does not return
variable-length neighbor rows.

## Stream Rule

Nonzero caller streams are propagated through prepare and query. The native
route synchronizes before returning, so async or nonblocking completion is not
claimed.
