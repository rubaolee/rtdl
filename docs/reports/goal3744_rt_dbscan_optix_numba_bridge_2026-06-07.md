# Goal3744 - RT-DBSCAN OptiX to Numba Bridge

Date: 2026-06-07

## Purpose

Goal3744 follows Goal3742 by connecting the RTDL/OptiX fixed-radius
count-threshold producer to the new Numba grid component continuation. This
gives RT-DBSCAN a real Python+RTDL/OptiX+Numba path, not only a pure Numba
partner reference and not only an OptiX+CuPy path.

No DBSCAN-specific native ABI was added.

## Implementation

The generic partner protocol now registers a narrow `cuda_array_interface`
adapter. Torch, CuPy, and NumPy still keep their framework-specific adapters;
the generic CUDA Array Interface adapter catches Numba-compatible device
columns that expose a CUDA pointer but are not Torch/CuPy objects.

The 3-D fixed-radius count-threshold output allocator now accepts
`partner="numba"`. Internally, it allocates Numba device arrays and wraps them
in a private view that exposes:

- `data_ptr` for native OptiX writes;
- `shape` and `dtype` for column validation;
- `copy_to_host()` for tests and app materialization;
- `__cuda_array_interface__` for Numba kernels.

New RT-DBSCAN app mode:

- `optix_rt_core_flags_numba_prepared_grid_components_3d`

The mode does:

1. Prepare Numba point columns and a reusable Numba grid continuation.
2. Ask OptiX to write threshold-capped neighbor counts and core flags directly
   into Numba-compatible device columns.
3. Feed those columns to the prepared Numba grid component-labeling
   continuation.

## Validation

Local:

```text
PYTHONPATH=src;. py -3 -m unittest tests.goal3742_rt_dbscan_numba_grid_reference_test

Ran 7 tests in 0.014s
OK (skipped=3)
```

A5000 pod:

```text
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=/root/rtdl_goal3737_clean/build/librtdl_optix.so \
  /root/rtdl_numba_venv/bin/python -m unittest \
  tests.goal3742_rt_dbscan_numba_grid_reference_test

Ran 7 tests in 2.404s
OK
```

The pod test verifies that the tiny RT-DBSCAN fixture matches the CPU reference
when OptiX core flags feed the Numba continuation.

## A5000 Timing Probe

These timings compare:

- `optix_rt_core_flags_cupy_prepared_grid_components_3d`
- `optix_rt_core_flags_numba_prepared_grid_components_3d`

They are same-contract bridge timings, not release claims.

| Dataset | Points | OptiX+CuPy sec | OptiX+Numba sec | Numba / CuPy |
| --- | ---: | ---: | ---: | ---: |
| `clustered3d` | 4,096 | 0.026771 | 0.027951 | 0.958x |
| `clustered3d` | 8,192 | 0.080226 | 0.051579 | 1.555x |
| `clustered3d` | 16,384 | 0.125470 | 0.124483 | 1.008x |
| `clustered3d` | 32,768 | 0.231759 | 0.217305 | 1.067x |
| `clustered3d` | 65,536 | 0.494361 | 0.492354 | 1.004x |
| `road3d` | 4,096 | 0.017473 | 0.019996 | 0.874x |
| `road3d` | 8,192 | 0.033391 | 0.037196 | 0.898x |
| `road3d` | 16,384 | 0.066775 | 0.097589 | 0.684x |
| `road3d` | 32,768 | 0.211075 | 0.193228 | 1.092x |
| `road3d` | 65,536 | 0.409885 | 0.438888 | 0.934x |

Artifact:

- `docs/reports/goal3744_rt_dbscan_optix_numba_bridge_a5000/summary.json`

## Interpretation

Goal3744 closes a design gap: users can now choose Numba for the component
continuation while still using RTDL/OptiX to produce generic core-flag device
columns.

Performance is mixed:

- On clustered rows, OptiX+Numba is mostly competitive and sometimes faster
  than OptiX+CuPy.
- On road-shaped rows, OptiX+CuPy remains faster on most sizes in this probe.
- The 8,192 clustered row shows a large OptiX+Numba win, but the two-sample
  timing is not enough to promote a universal policy from that row alone.

The right current recommendation is user choice plus evidence: expose both
partners, keep CuPy as the current known-strong route on road-shaped rows, and
keep Numba as a serious reference route that avoids user-written RawKernel code.

## Claim Boundary

Goal3744 does not authorize:

- a release action;
- public speedup wording;
- whole-app acceleration wording;
- broad RT-core wording;
- RT-DBSCAN paper reproduction wording;
- true-zero-copy wording;
- automatic partner selection;
- app-specific native-engine logic.

The new `cuda_array_interface` adapter authorizes generic pointer description
for compatible CUDA columns. It does not authorize true zero-copy marketing
claims.

## Next Work

The RT-DBSCAN Numba reference gap is materially narrower. The next larger item,
if we keep pushing RT-DBSCAN, is a Numba grouped-stream consumer for the
over-budget dense branch. That is bigger than this bridge because it must
consume the grouped stream/workspace contract rather than just threshold flags.
