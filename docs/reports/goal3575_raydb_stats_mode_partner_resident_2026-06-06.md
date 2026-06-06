# Goal3575 RayDB-Style Stats Mode for Partner-Resident Grouped i64

Date: 2026-06-06

## Purpose

Goal3575 turns the grouped-i64 `stats` path from structural support into a real
RayDB-style benchmark mode for the generic columnar aggregate contract.

The scope is intentionally narrow:

- add `stats` to the generic CPU columnar oracle;
- map `stats` to the existing generic `group_stats_i64` reduction contract;
- expose `stats` in the RayDB-style CPU and OptiX partner-resident modes;
- keep older paper-shaped RayDB RT paths unchanged until they get separate
  same-contract evidence;
- validate the partner-resident `stats` path on the A5000 pod.

This is not a release packet and does not authorize public speedup claims.

## Implementation

Files changed:

| File | Change |
| --- | --- |
| `src/rtdsl/columnar_aggregate_reference.py` | Adds `stats` to supported aggregates and the CPU oracle; updates partner-resident lowering metadata. |
| `src/rtdsl/grouped_reduction.py` | Maps `stats` to `group_stats_i64`. |
| `examples/v2_0/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py` | Adds `stats` to CPU and OptiX partner-resident modes, but not to paper-shaped RT modes. |
| `examples/v2_0/research_benchmarks/raydb_style/README.md` | Updates current user-facing mode lists. |
| `tests/goal3575_raydb_stats_mode_partner_resident_test.py` | Verifies oracle rows, mode boundaries, and lowering metadata. |

For the tiny fixture, `stats` returns one row per region with:

- `count`;
- `sum`;
- `min`;
- `max`.

## A5000 Evidence

Artifact:

`docs/reports/goal3575_raydb_stats_mode_partner_resident_a5000/stats.json`

Run:

```bash
PYTHONPATH=src:. \
RTDL_OPTIX_LIBRARY=/root/rtdl_goal3556_current/build/librtdl_optix.so \
RTDL_OPTIX_LIB=/root/rtdl_goal3556_current/build/librtdl_optix.so \
python3 examples/v2_0/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py \
  --mode stats \
  --backend optix_partner_resident_experimental \
  --copies 120000 \
  --warmup 3 \
  --repeat 5000
```

Result:

| Field | Value |
| --- | --- |
| backend | `optix_partner_resident_experimental` |
| mode | `stats` |
| row count | `960000` |
| matches CPU reference | `true` |
| native launch count | `1` |
| generic stats ABI used | `true` |
| fused native reduction | `true` |
| query median sec | `0.000477436930` |
| query min sec | `0.000466553494` |
| query max sec | `0.011575538665` |

Rows:

| `region_id` | `count` | `sum` | `min` | `max` |
| ---: | ---: | ---: | ---: | ---: |
| 0 | 240000 | 22800000 | 90 | 100 |
| 1 | 120000 | 24000000 | 200 | 200 |
| 2 | 120000 | 9600000 | 80 | 80 |

## Boundary

This goal proves that the app can now exercise the generic fused `stats`
reduction through the partner-resident OptiX dispatcher.

It does not claim:

- release or tag readiness;
- public speedup;
- whole-app acceleration;
- broad RT-core acceleration;
- true zero-copy;
- paper reproduction;
- package-install support.

The paper-shaped RayDB RT modes intentionally remain limited to
`count`, `sum`, `min`, `max`, and `avg_as_sum_count` until stats gets separate
same-contract RT-path evidence.

## Validation

Local:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3575_raydb_stats_mode_partner_resident_test tests.goal2495_raydb_style_cpu_reference_fixture_test tests.goal2499_raydb_style_lowering_plan_test tests.goal2512_raydb_style_partner_resident_experimental_backend_test tests.goal2519_partner_resident_grouped_i64_dispatch_boundary_test tests.goal2516_partner_resident_composite_avg_sum_count_test tests.goal2500_raydb_style_backend_matrix_runner_test
```

Pod artifact validation:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3575_raydb_stats_mode_partner_resident_a5000_test
```
