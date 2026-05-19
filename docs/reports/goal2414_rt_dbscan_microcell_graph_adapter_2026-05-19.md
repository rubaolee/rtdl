# Goal2414 RT-DBSCAN Microcell Graph Adapter

Date: 2026-05-19

Status: local implementation complete; pod performance evidence still required

## Purpose

Goal2414 implements the corrected Goal2413 contract: a generic, partner-side
fixed-radius microcell component continuation for all-core 3-D point sets.

The implementation is deliberately not DBSCAN-native. It exposes a generic
radius-graph component adapter and lets the RT-DBSCAN benchmark compose it with
the existing OptiX RT count-threshold device-column primitive from Goal2405.

## What Changed

Added Python partner adapter:

```python
radius_graph_components_3d_cupy_microcell_graph_partner_columns(...)
```

Added RT-DBSCAN benchmark mode:

```text
optix_rt_core_flags_cupy_microcell_graph_components_3d
```

The new mode runs:

```text
OptiX RT fixed-radius count-threshold device columns
    -> CuPy clique-safe microcell component continuation
```

## Correctness Design

The unsafe radius-cell graph design was rejected because a radius-sized 3-D cell
is not internally connected. The implemented path uses:

```text
microcell_size = radius / sqrt(3)
neighbor_cell_range = ceil(radius / microcell_size)
```

This makes each occupied microcell internally clique-safe. Cross-microcell
unions are still guarded by an exact point-pair distance test:

```text
dist^2 <= radius^2
```

The fast path activates only when all supplied core flags are true. If any point
is non-core, or if core flags are not supplied, the adapter falls back to:

```python
radius_graph_components_3d_cupy_grid_partner_columns(...)
```

## Metadata

Fast-path metadata includes:

- `cell_graph_fast_path_active = True`
- `cell_graph_granularity = "clique_safe_microcell"`
- `microcell_size_policy = "radius_div_sqrt3_cube_diagonal_within_radius"`
- `neighbor_cell_range`
- conservative claim-boundary flags

Fallback metadata includes:

- `cell_graph_fast_path_active = False`
- `fallback_adapter = "radius_graph_components_3d_cupy_grid_partner_columns"`
- `fallback_reason`

## Files Changed

- `src/rtdsl/partner_adapters.py`
- `src/rtdsl/__init__.py`
- `examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py`
- `examples/v2_0/research_benchmarks/rt_dbscan/README.md`
- `scripts/goal2392_rt_dbscan_pod_runner.sh`
- `scripts/goal2403_rt_dbscan_repeat_probe.py`
- `tests/goal2414_rt_dbscan_microcell_graph_adapter_test.py`

## Local Validation

Local Windows validation:

```text
py -3 -m py_compile src/rtdsl/partner_adapters.py src/rtdsl/__init__.py examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py tests/goal2414_rt_dbscan_microcell_graph_adapter_test.py
```

```text
py -3 -m unittest tests.goal2414_rt_dbscan_microcell_graph_adapter_test
```

Result:

```text
4 tests OK, 2 skipped because CuPy/CUDA was not available in the Windows shell.
```

The non-GPU tests verify:

- generic Python-side wiring;
- no native microcell implementation was added;
- no `rtdl_optix_dbscan` native ABI appears;
- the clique-safe microcell size rejects the radius-cell assumption.

Local Linux CUDA validation used a disposable checkout:

```text
/home/lestat/work/rtdl_goal2414_check
commit 7e2b94be77d65fc454f0d2f83d40ec61e5657031
```

CuPy probe:

```text
cupy 14.0.1 devices 1
```

Focused test:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal2414_rt_dbscan_microcell_graph_adapter_test
```

Result:

```text
5 tests OK
```

This ran the GPU checks that were skipped on Windows:

- same radius-cell disconnected points remained separate under the microcell
  fast path;
- mixed-core input triggered fallback and preserved the component-column schema.

Local Linux OptiX smoke:

```text
make build-optix OPTIX_PREFIX=/home/lestat/vendor/optix-dev
RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so PYTHONPATH=src:. python3 \
  examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py \
  --mode optix_rt_core_flags_cupy_microcell_graph_components_3d \
  --dataset clustered3d --point-count 1024 --no-validation
```

Result summary:

```text
fast_path_active = false
fallback_reason = not_all_points_core
signature core_count = 1021
signature noise_count = 1
```

Additional activation smoke at 4096 and 32768 also fell back because at least
one point was not core on this local GTX smoke host:

```text
4096:  fast_path_active=false, core_count=4094, noise_count=0
32768: fast_path_active=false, core_count=32767, noise_count=0
```

This is correct behavior, not a failure. The microcell fast path is intentionally
all-core only.

## Pod Evidence Still Needed

The GPU tests now pass on local Linux, but pod-scale timing is still required
before any performance claim:

```text
tests.goal2414_rt_dbscan_microcell_graph_adapter_test
```

Then run repeat probes comparing:

```text
partner_cupy_grid_components_3d
optix_rt_core_flags_cupy_grid_components_3d
optix_rt_core_flags_cupy_microcell_graph_components_3d
```

Datasets:

```text
clustered3d, road3d
```

Sizes:

```text
32768, 65536, 131072
```

## Boundary

No native RTDL engine ABI was added. No DBSCAN-specific native continuation was
added. No release claim, paper-reproduction claim, or broad RT-core speedup
claim is authorized by this local implementation.
