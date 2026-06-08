# Goal3988 RT-DBSCAN Partner Opponent Probe

Date: 2026-06-08

## Verdict

`accept-with-boundary`

Goal3987 showed that the existing blocked grouped-stream and direct-side-effect switches do not improve RT-DBSCAN. Goal3988 checks the other major question: should the recommended RT-DBSCAN implementation switch away from RTDL/OptiX to a partner-only implementation?

The answer is no for the current 65,536-point clustered3D profile. RTDL/OptiX grouped stream remains the fastest measured same-signature route.

## Pod Setup

- Pod: NVIDIA RTX 4000 Ada Generation, driver 550.127.05
- Source checkout: `accc84daf76846d29d91fa8a145187851e941f04`
- Dataset: `clustered3d`
- Point count: `65536`
- Repeat/warmup: `--repeat 5 --warmup 1`
- Validation: `--no-validation`; output signatures compared

## Results

| Route | RT cores | Partner | Median elapsed sec | Signature |
| --- | --- | --- | ---: | --- |
| `optix_rt_core_grouped_stream_numba_column_signature_3d` | yes | Numba | 0.0861 | four clusters of 16,384; all core |
| `optix_rt_core_flags_numba_prepared_grid_column_signature_3d` | yes | Numba | 0.3003 | same |
| `partner_numba_prepared_grid_components_3d` | no | Numba | 1.7600 | same |
| `partner_cupy_prepared_grid_components_3d` | no | CuPy | 7.3648 | same |

## Interpretation

RTDL/OptiX grouped stream is about 20x faster than the Numba-only prepared-grid route and about 86x faster than the CuPy-only prepared-grid route on this current profile. The older RT-core flags plus partner grid route is slower than grouped stream because it still pays more continuation work.

This means RT-DBSCAN should remain a primitive-first RTDL/OptiX benchmark row. The remaining improvement target is not partner selection; it is a stronger generic fixed-radius grouped-union primitive with less redundant traversal and less parent-workspace atomic contention.

## Boundary

This is internal opponent evidence. It does not authorize public speedup wording, broad RT-core speedup wording, whole-app acceleration wording, paper reproduction, release action, true-zero-copy wording, automatic partner/backend selection, or app-specific native-engine logic.
