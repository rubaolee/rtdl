# Goal2427 RT-DBSCAN Goal2425 Plan Smoke

Date: 2026-05-19

Status: pod smoke complete

## Purpose

Goal2425 corrected the RT-DBSCAN planner after adding a fair prepared-CuPy
baseline. Goal2427 verifies that the updated `planned_rt_dbscan` mode actually
executes the new choices on the RTX A5000 pod.

This is not a new speedup claim. It is a traceability check:

```text
plan -> explain -> execute -> preserve claim boundary
```

## Environment

```text
pod: root@69.30.85.177 -p 22055
commit: 5af2ce11a41302c569f76fcf787f2d5c4f520dba
OptiX library: /root/rtdl_goal2415/build/librtdl_optix.so
```

Artifacts:

```text
docs/reports/goal2427_rt_dbscan_goal2425_plan_smoke_pod/
```

## Smoke Rows

| Dataset | Points | Selected Mode | RT Core Phase | App sec |
| --- | ---: | --- | --- | ---: |
| tiny | 9 | `cpu_reference` | no | 0.000125 |
| clustered3d | 32768 | `partner_cupy_prepared_grid_components_3d` | no | 0.729226 |
| clustered3d | 65536 | `optix_rt_core_flags_cupy_prepared_grid_components_3d` | yes | 1.484948 |
| road3d | 262144 | `partner_cupy_prepared_grid_components_3d` | no | 2.647523 |
| road3d | 524288 | `optix_rt_core_flags_cupy_prepared_grid_components_3d` | yes | 8.101063 |
| ngsim_dense | 131072 | `partner_cupy_prepared_grid_components_3d` | no | 0.987418 |

## Interpretation

The updated plan follows the Goal2425 fairness thresholds:

- below the clustered 65k crossover, it chooses prepared CuPy;
- at the clustered 65k row, it chooses prepared RT+CuPy;
- below the road 524k crossover, it chooses prepared CuPy;
- at the road 524k row, it chooses prepared RT+CuPy;
- for compact dense rows, it chooses prepared CuPy.

The plan remains explicit. Every artifact records `execution_plan`,
`selected_mode`, and `not_hidden_dispatcher=true`.

## Remaining Runtime Problem

The correctness and planning problem is now closed for this benchmark stage.
The deeper performance problem is still open:

```text
RTDL needs a generic device-resident radius-graph continuation that can consume
RT-produced core/count or edge-stream outputs without redoing full partner-side
candidate traversal.
```

That is a v2.x primitive/runtime project, not a DBSCAN-specific engine
customization and not a v3.0 user-shader extension.
