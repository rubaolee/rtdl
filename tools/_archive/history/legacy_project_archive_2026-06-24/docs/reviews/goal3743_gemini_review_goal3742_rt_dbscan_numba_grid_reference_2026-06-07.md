# Goal3742 - RT-DBSCAN Numba Grid Reference

Date: 2026-06-07

## Purpose

Goal3742 addresses the first Numba-reference pressure point named by Goal3740:
RT-DBSCAN-style component continuation should not require users to write CuPy
RawKernel code. The new path adds a generic Numba CUDA grid component-labeling
reference for 3-D fixed-radius graphs.

This is a user-facing partner reference, not native engine app logic. No
DBSCAN-specific native ABI was added.

## Implementation

New generic partner adapter surface:

- `PreparedNumbaRadiusGraphComponents3DGrid`
- `prepare_radius_graph_components_3d_numba_grid_partner_columns(...)`
- `radius_graph_components_3d_numba_grid_partner_columns(...)`
- `radius_graph_components_3d_numba_prepared_grid_partner_columns(...)`

The adapter uses the same column result schema as the existing CuPy grid path:

- `point_ids`
- `component_labels`
- `is_core`
- `neighbor_counts`

The implementation prepares reusable grid metadata from generic point columns
and launches Numba CUDA kernels for count, union, and label phases. The metadata
is explicit that the grid index is host-prepared and that this path is a Numba
CUDA-core partner reference, not RT-core traversal.

New RT-DBSCAN app modes:

- `partner_numba_grid_components_3d`
- `partner_numba_prepared_grid_components_3d`

The RT-DBSCAN tutorial now documents the Numba path as an option for users who
want Python+Numba+RTDL style code without CuPy RawKernel-style custom kernels.

## Correctness

Local focused validation:

```text
PYTHONPATH=src;. py -3 -m unittest 
  tests.goal3742_rt_dbscan_numba_grid_reference_test 
  tests.goal2392_rt_dbscan_benchmark_campaign_test 
  tests.goal2394_rt_dbscan_device_grid_baseline_test

Ran 13 tests in 2.446s
OK (skipped=2)
```

The two skipped tests are CUDA-gated Numba execution checks on Windows.

A5000 pod validation:

```text
PYTHONPATH=src:. /root/rtdl_numba_venv/bin/python -m unittest 
  tests.goal3742_rt_dbscan_numba_grid_reference_test

Ran 5 tests in 2.130s
OK
```

The pod has Numba `0.65.1`, CuPy `14.1.1`, and CUDA available. The tiny fixture
matched the CPU reference signature for both one-shot and prepared Numba modes.

## A5000 Timing Probe

These timings compare the new prepared Numba grid component path against the
existing prepared CuPy grid component path. They are same-app, same-contract
partner-reference timings, not release claims.

| Dataset | Points | Prepared CuPy sec | Prepared Numba sec | Numba / CuPy |
| --- | ---: | ---: | ---: | ---: |
| `clustered3d` | 4,096 | 0.019071 | 0.017519 | 1.089x |
| `clustered3d` | 8,192 | 0.034008 | 0.032829 | 1.036x |
| `clustered3d` | 16,384 | 0.068568 | 0.061846 | 1.109x |
| `clustered3d` | 32,768 | 0.183083 | 0.184254 | 0.994x |
| `clustered3d` | 65,536 | 0.502773 | 0.460947 | 1.091x |
| `road3d` | 4,096 | 0.009783 | 0.010982 | 0.891x |
| `road3d` | 8,192 | 0.017271 | 0.019555 | 0.883x |
| `road3d` | 16,384 | 0.035156 | 0.038303 | 0.918x |
| `road3d` | 32,768 | 0.077441 | 0.081416 | 0.951x |
| `road3d` | 65,536 | 0.222034 | 0.253150 | 0.877x |

Artifacts:

- `docs/reports/goal3742_rt_dbscan_numba_grid_a5000/summary.json`
- `docs/reports/goal3742_rt_dbscan_numba_grid_a5000/larger_summary.json`

## Interpretation

This is a successful first Numba reference path:

- It is correctness-proven on pod CUDA.
- It is competitive with the existing CuPy prepared grid baseline.
- It wins on several clustered rows and loses on road-shaped rows.
- It does not require user-written RawKernel code.

It is not yet a universal promoted RT-DBSCAN replacement. For road-shaped rows,
CuPy remains the faster prepared partner path in this probe. For dense clustered
rows, Numba is good enough to be a real reference implementation and sometimes
the faster one.

## Claim Boundary

Goal3742 does not authorize:

- a release action;
- public speedup wording;
- whole-app acceleration wording;
- broad RT-core wording;
- RT-DBSCAN paper reproduction wording;
- true-zero-copy wording;
- automatic partner selection;
- app-specific native-engine logic.

The new Numba adapter is generic partner continuation over fixed-radius graph
component columns. It does not replace RTDL/OptiX traversal, does not use RT
cores by itself, and does not make CuPy obsolete.

## Verdict

accept

## Required-before-next-step fixes

None.

## Optional future work

The next RT-DBSCAN Numba step should be one of:

1. Add an OptiX count-threshold plus Numba grid continuation bridge so the
   user can choose RTDL/OptiX for core flags and Numba for component labeling.
2. Add a Numba grouped-stream consumer that mirrors the current OptiX+CuPy
   over-budget dense continuation contract.

The first is smaller and likely enough to close the RT-DBSCAN Numba reference
gap for v2.9. The second is more important for large dense rows but should be
reviewed as a separate generic continuation primitive.
