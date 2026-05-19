# Goal2422 RT-DBSCAN Explicit Plan Mode

Date: 2026-05-19

Status: implementation complete; pod smoke complete

## Purpose

Goal2420 showed that no single RT-DBSCAN path wins everywhere:

- prepared RT-count plus prepared CuPy-grid continuation wins on clustered
  large rows and crosses over on `road3d` at 262k points;
- pure CuPy grid continuation remains better for compact `ngsim_dense` through
  131k and for smaller sparse-road rows.

The design response is not an invisible dispatcher. Goal2422 adds an explicit
benchmark-app plan mode:

```text
planned_rt_dbscan
```

The mode records the selected execution path and reason in JSON metadata under:

```text
metadata.execution_plan
```

## Policy

The current evidence-bounded policy is:

| Shape / size | Selected mode | Reason |
| --- | --- | --- |
| `tiny` | `cpu_reference` | correctness fixture, no GPU performance claim |
| `ngsim_dense` | `partner_cupy_grid_components_3d` | Goal2420 showed compact dense rows favor pure CuPy |
| `road3d` below 262k | `partner_cupy_grid_components_3d` | Goal2418 showed pure CuPy still wins or nearly ties |
| clustered rows, and `road3d` at 262k+ | `optix_rt_core_flags_cupy_prepared_grid_components_3d` | Goal2418/Goal2420 showed the prepared RT bridge is the best current bridge |

## Boundary

This is app-level example logic over generic RTDL/partner contracts. It does not add native DBSCAN ABI, does not hide routing, and does not authorize release or
paper-reproduction claims.

The important design pattern is:

```text
plan -> explain -> execute -> preserve claim boundary
```

not:

```text
silently dispatch based on hardware and hope the user can reproduce it
```

## Pod Smoke

Smoke artifacts:

```text
docs/reports/goal2422_rt_dbscan_explicit_plan_mode_pod_smoke/
```

Validated on the RTX A5000 pod used by Goals 2418 and 2420:

| Dataset / points | Selected mode | Expected |
| --- | --- | --- |
| `clustered3d` / 32768 | `optix_rt_core_flags_cupy_prepared_grid_components_3d` | yes |
| `road3d` / 131072 | `partner_cupy_grid_components_3d` | yes |
| `road3d` / 262144 | `optix_rt_core_flags_cupy_prepared_grid_components_3d` | yes |
| `ngsim_dense` / 65536 | `partner_cupy_grid_components_3d` | yes |

Each artifact records `metadata.execution_plan.not_hidden_dispatcher = true`.
