# Goal3992 Grouped-Union Extended Telemetry

Date: 2026-06-08

## Verdict

`accept-with-boundary`

Goal3992 adds a length-aware extended telemetry path for the generic OptiX fixed-radius grouped-union all-items self route. The old 4-counter telemetry ABI remains available and unchanged. When a caller supplies an 8-counter telemetry buffer, the Python runtime selects a new explicit native symbol that receives the telemetry element count and writes counters 4-7 only when that capacity is present.

This is instrumentation for the next dense grouped-union primitive design. It is not a performance optimization and does not authorize public speedup wording.

## Native And Runtime Change

- Added `telemetry_count` to the grouped-union launch params.
- Added the generic native export:
  `rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_self_device_outputs_with_extended_telemetry_and_execution_options`
- Preserved existing 4-counter exports by passing telemetry capacity `4` on legacy telemetry calls and `0` on non-telemetry calls.
- Added Python runtime selection:
  - telemetry buffer length `4..7`: old telemetry ABI,
  - telemetry buffer length `>=8`: extended telemetry ABI.
- Added metadata:
  - `grouped_union_telemetry_counter_count`
  - `grouped_union_extended_telemetry_enabled`
  - extended `grouped_union_telemetry_contract`

## Counter Contract

| Counter | Meaning |
| --- | --- |
| `uint64[0]` | parent atomic attempts |
| `uint64[1]` | parent atomic successes |
| `uint64[2]` | fallback atomic attempts |
| `uint64[3]` | fallback atomic successes |
| `uint64[4]` | radius candidate hits after predicate/range filtering |
| `uint64[5]` | same-root culled candidate hits |
| `uint64[6]` | direct side-effect candidate hits |
| `uint64[7]` | reported intersection candidates |

The new counter names are generic fixed-radius grouped-union diagnostics. They do not encode DBSCAN, clustering policy, epsilon/min-points semantics, or application labels.

## Pod Evidence

Artifact: `docs/reports/goal3992_grouped_union_extended_telemetry_pod_smoke.json`

Pod:

- GPU: NVIDIA RTX 4000 Ada Generation, driver 550.127.05
- Checkout base: `4ea593744b4f64ef8acec52aef64daa67b7194b8`
- Applied uncommitted Goal3992 patch for native/runtime changes
- `make build-optix -j2`: passed
- Smoke profile: `clustered3d`, `4096` points, radius `0.5`

| Path | Status | Native symbol | Counter count |
| --- | --- | --- | ---: |
| old 4-counter telemetry | pass | `rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_self_device_outputs_with_telemetry` | 4 |
| extended 8-counter telemetry | pass | `rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_self_device_outputs_with_extended_telemetry_and_execution_options` | 8 |

Extended telemetry values:

| Metric | Value |
| --- | ---: |
| parent atomic attempts | 10,964 |
| parent atomic successes | 4,095 |
| fallback atomic attempts | 0 |
| fallback atomic successes | 0 |
| radius candidate hits after predicate | 3,483,897 |
| same-root culled candidate hits | 3,473,787 |
| direct side-effect candidate hits | 0 |
| reported intersection candidates | 10,110 |

Interpretation: successful parent unions are tiny compared with radius candidates and same-root-culling root reads. This strengthens the Goal3990 conclusion that the next performance primitive should reduce candidate/root-read work, not merely reduce successful union atomics.

Do not compare the old and extended elapsed times in this smoke as a speedup result. The first call paid pipeline compile/warmup in this execution order, and the extended counters intentionally add high-frequency instrumentation atomics. The artifact exists to prove the counter contract executes on hardware and yields useful bottleneck telemetry.

## Boundary

This goal does not authorize release, public speedup wording, broad RT-core speedup wording, whole-app acceleration wording, paper reproduction, true-zero-copy wording, automatic partner/backend selection, or app-specific native-engine logic. It keeps the native vocabulary generic and only improves instrumentation for the next generic dense grouped-union design step.

